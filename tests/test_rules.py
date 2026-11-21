# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import replace
from datetime import date
from importlib.resources import files
from pathlib import Path
from shutil import copytree

import pytest
import yaml
from typer.testing import CliRunner

from m365_exit_scan import rules
from m365_exit_scan.catalogue import Catalogue, load_catalogue
from m365_exit_scan.cli import app
from m365_exit_scan.errors import InputError
from m365_exit_scan.i18n import load_locale
from m365_exit_scan.model import (
    Coverage,
    Finding,
    FindingValue,
    Product,
    Scan,
    ServicePlan,
    load_scan_text,
    scan_to_json,
)
from m365_exit_scan.parsing import parse_yaml, read_text
from m365_exit_scan.report import SECTION_ORDER, render_report
from m365_exit_scan.rules import (
    MissingEvidence,
    StatusRuleSet,
    WorkloadStatus,
    classify_product,
    evaluate,
    licence_findings,
    load_risky_file_types,
    load_service_plans,
    load_status_rules,
    rules_dir,
)

LICENSING_REFERENCE = (
    "https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference"
)


@pytest.fixture
def catalogue() -> Catalogue:
    return load_catalogue()


def sample_scan(sample: str, catalogue: Catalogue) -> Scan:
    source = files("m365_exit_scan").joinpath("demo", sample, "scan.json")
    return load_scan_text(read_text(source), source.name, catalogue)


def test_shipped_service_plans_cite_the_reference(catalogue: Catalogue) -> None:
    plans = load_service_plans(catalogue)

    assert plans
    assert all(
        plan.name == plan.name.upper() and plan.sku_part_number == plan.sku_part_number.upper()
        for plan in plans
    )
    assert {plan.workload for plan in plans} <= set(catalogue.workload_ids)
    assert {plan.signal for plan in plans} == {"add_on", "bundled"}
    assert {plan.reference_url for plan in plans} == {LICENSING_REFERENCE}
    assert all(isinstance(plan.checked_on, date) for plan in plans)
    phone = {(plan.sku_part_number, plan.signal) for plan in plans if plan.name == "MCOEV"}
    assert {("SPE_E5", "bundled"), ("MCOEV", "add_on")} <= phone


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("workload", "unrecognised"),
        ("signal", "measured"),
        ("reference_url", None),
        ("reference_url", "https://learn.microsoft.com.example.invalid/"),
        ("checked_on", None),
        ("checked_on", "2026-02-30"),
        ("sku_guid", "not_a_guid"),
        ("guid", "not_a_guid"),
        ("sku_part_number", "invalid product"),
        ("name", "invalid plan"),
        ("name", "repeat"),
        ("note", {"en": "Explanation only in English."}),
    ],
)
def test_invalid_service_plan_names_the_field(
    tmp_path: Path, catalogue: Catalogue, field: str, value: object
) -> None:
    path = tmp_path / "service_plans.yaml"
    row = {
        "sku_part_number": "MCOEV",
        "sku_guid": "e43b5b99-8dfb-405f-9987-dc307f34bcbd",
        "name": "MCOEV",
        "guid": "4828c8ec-dc2e-4779-b502-87ac9ce28ab7",
        "workload": "telephony",
        "signal": "add_on",
        "reference_url": LICENSING_REFERENCE,
        "checked_on": "2026-11-21",
    }
    if value is None:
        rows = [{key: item for key, item in row.items() if key != field}]
    elif value == "repeat":
        rows = [row, {**row, "name": "mcoev"}]
    else:
        rows = [{**row, field: value}]
    path.write_text(yaml.safe_dump({"plans": rows}), encoding="utf-8")

    with pytest.raises(InputError) as caught:
        load_service_plans(catalogue, path)

    error = caught.value
    assert error.file == path.name
    assert error.field == {
        "repeat": "plans[1].name",
        "note": "plans[0].note.de",
    }.get("repeat" if value == "repeat" else field, f"plans[0].{field}")


@pytest.mark.parametrize(("sample", "count"), [("town", 3), ("nonprofit", 1)])
def test_sample_licence_findings_match_assigned_products(
    catalogue: Catalogue, sample: str, count: int
) -> None:
    scan = sample_scan(sample, catalogue)
    plans = load_service_plans(catalogue)
    findings = licence_findings(scan, plans, catalogue)
    by_id = {finding.id: finding.value for finding in findings}

    assert scan.dropped_count == 0
    assert scan.licences is not None
    assert by_id["licences.product_count"] == count
    assert len(by_id) == 1 + 2 * len(catalogue.workloads)
    for finding in findings:
        assert finding.provenance == "measured"
        assert finding.collector == scan.licences.collector
        assert finding.source == scan.licences.source
        assert finding.collected_at == scan.licences.collected_at
        assert finding.coverage == scan.licences.coverage
    if sample == "town":
        assert by_id["telephony.licence_add_on_assigned"] is True
        assert by_id["power_platform.licence_add_on_assigned"] is True
        assert by_id["power_platform.licence_bundled_assigned"] is True
        assert by_id["security_compliance.licence_bundled_assigned"] is True
        assert by_id["telephony.licence_bundled_assigned"] is False
    else:
        assert not any(
            value for key, value in by_id.items() if key.endswith(".licence_add_on_assigned")
        )
        assert by_id["small_apps.licence_bundled_assigned"] is True


def _product_findings(catalogue: Catalogue, *products: Product) -> dict[str, Finding]:
    scan = sample_scan("town", catalogue)
    assert scan.licences is not None
    scan = replace(scan, licences=replace(scan.licences, products=products))
    return {
        item.id: item for item in licence_findings(scan, load_service_plans(catalogue), catalogue)
    }


def test_no_licence_block_and_no_assigned_licences(catalogue: Catalogue) -> None:
    scan = sample_scan("town", catalogue)
    assert (
        licence_findings(replace(scan, licences=None), load_service_plans(catalogue), catalogue)
        == ()
    )
    assert scan.licences is not None
    unassigned = [replace(product, assigned=0) for product in scan.licences.products]
    findings = _product_findings(catalogue, *unassigned)

    assert findings.pop("licences.product_count").value == len(unassigned)
    assert all(finding.value is False for finding in findings.values())


def test_unmapped_pairs_are_unknown_without_erasing_classified_assignments(
    catalogue: Catalogue,
) -> None:
    scan = sample_scan("town", catalogue)
    assert scan.licences is not None
    _, phone, _ = scan.licences.products
    wrong_product = replace(phone, sku_part_number="OTHER_PRODUCT")
    bad_plan_guid = replace(
        phone, service_plans=(replace(phone.service_plans[0], guid=phone.sku_guid),)
    )
    for product in (wrong_product, bad_plan_guid):
        findings = _product_findings(catalogue, product)
        signal = findings["telephony.licence_add_on_assigned"]
        assert (signal.value, signal.provenance, signal.missing_reason) == (
            None,
            "unknown",
            "licence_not_classified",
        )
        assert findings["teams.licence_add_on_assigned"].value is False
        assert classify_product(product, load_service_plans(catalogue)) == (None,)
    mixed = _product_findings(catalogue, phone, wrong_product)
    assert mixed["telephony.licence_add_on_assigned"].value is True


def test_audio_conferencing_is_a_meetings_signal(catalogue: Catalogue) -> None:
    plan = next(
        plan for plan in load_service_plans(catalogue) if plan.sku_part_number == "MCOMEETADV"
    )
    product = Product(
        plan.sku_part_number, plan.sku_guid, 1, 1, (ServicePlan(plan.name, plan.guid),)
    )
    findings = _product_findings(catalogue, product)

    assert findings["teams.licence_add_on_assigned"].value is True
    assert findings["telephony.licence_add_on_assigned"].value is False


def test_report_counts_unclassified_plans_without_showing_their_names(
    tmp_path: Path, catalogue: Catalogue
) -> None:
    scan = sample_scan("town", catalogue)
    assert scan.licences is not None
    suite, phone, reporting = scan.licences.products
    unknown = ServicePlan("UNRECOGNISED_PLAN", phone.sku_guid)
    suite = replace(suite, service_plans=(*suite.service_plans, unknown))
    scan = replace(scan, licences=replace(scan.licences, products=(suite, phone, reporting)))
    source = tmp_path / "scan.json"
    source.write_text(scan_to_json(scan), encoding="utf-8")
    result = CliRunner().invoke(app, ["report", str(source), "--out", str(tmp_path / "out")])

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.strip())
    assert report.is_file()
    html = report.read_text(encoding="utf-8")
    assert html.count("data-product=") == len(scan.licences.products)
    assert "<caption data-sample>Scan measurements are simulated.</caption>" in html
    assert "Telephony · Separately licensed" in html
    assert "Power Platform · Included in the product" in html
    assert "Unclassified service plans in this product: 1." in html
    assert "UNRECOGNISED_PLAN" not in html


@pytest.fixture
def status_rules(catalogue: Catalogue) -> StatusRuleSet:
    return load_status_rules(catalogue)


@pytest.fixture
def complete_evidence(catalogue: Catalogue) -> dict[str, Finding]:
    scan = sample_scan("town", catalogue)
    assert scan.licences is not None
    scan = replace(scan, licences=replace(scan.licences, products=()))
    findings = {
        item.id: item for item in licence_findings(scan, load_service_plans(catalogue), catalogue)
    }
    for entry in catalogue.findings:
        manual = entry.provided != "no"
        value: FindingValue = {"boolean": False, "count": 0, "bytes": 0, "code": "example"}[
            entry.type
        ]
        if entry.id in {"licences.contract_terms_known", "directory.account_list_reviewed"}:
            value = True
        findings[entry.id] = Finding(
            entry.id,
            entry.workload,
            value,
            entry.unit,
            "provided" if manual else "measured",
            None if manual else "directory",
            "inputs_yaml" if manual else "sample.directory",
            "2026-11-02",
            None,
            None if manual else Coverage("complete"),
            None,
        )
    return findings


def _status(
    workload: str,
    findings: dict[str, Finding],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
) -> WorkloadStatus:
    return next(
        row for row in evaluate(findings, status_rules, catalogue) if row.workload == workload
    )


def _set_value(findings: dict[str, Finding], finding_id: str, value: FindingValue) -> None:
    findings[finding_id] = replace(findings[finding_id], value=value)


def _readiness_row(html: str, workload: str) -> str:
    row = re.search(rf'<tr data-workload="{workload}"[^>]*>.*?</tr>', html, re.S)
    assert row is not None, workload
    return row[0]


def test_mail_is_unknown_until_a_problem_is_confirmed(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    findings = complete_evidence
    shared = findings["mail.shared_mailbox_count"]
    findings[shared.id] = replace(
        shared,
        value=None,
        provenance="unknown",
        collector="exchange_recipients",
        missing_reason="needs_recipient_export",
    )
    row = _status("mail", findings, status_rules, catalogue)
    assert row.status == "unknown" and row.reason_code == "needs_recipient_export"
    assert row.missing == (
        MissingEvidence(shared.id, "needs_recipient_export", "exchange_recipients"),
    )

    _set_value(findings, "mail.other_systems_send_mail", True)
    row = _status("mail", findings, status_rules, catalogue)
    assert row.deciding is not None and row.deciding.id == "mail-other-systems"
    assert row.status == "needs_work" and row.incomplete
    assert row.missing == (
        MissingEvidence(shared.id, "needs_recipient_export", "exchange_recipients"),
    )


def test_onedrive_requires_external_sharing_answer(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    findings = complete_evidence
    assert _status("onedrive", findings, status_rules, catalogue).status == "ready"

    answer = findings.pop("onedrive.external_sharing_in_use")
    row = _status("onedrive", findings, status_rules, catalogue)

    assert row.status == "unknown" and row.incomplete
    assert row.missing == (MissingEvidence(answer.id, "answer_not_provided", None),)


@pytest.mark.parametrize(
    ("assigned", "replacement", "in_use", "status", "incomplete"),
    [
        (True, False, True, "blocker", False),
        (True, True, True, "needs_work", False),
        (True, None, True, "unknown", True),
        (True, None, None, "unknown", True),
        (False, False, False, "ready", False),
        (False, None, False, "ready", False),
        (False, None, None, "unknown", True),
        (False, False, True, "blocker", False),
    ],
)
def test_telephony_needs_replacement_or_explicit_non_use(
    complete_evidence: dict[str, Finding],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    assigned: bool,
    replacement: bool | None,
    in_use: bool | None,
    status: str,
    incomplete: bool,
) -> None:
    findings = complete_evidence
    _set_value(findings, "telephony.licence_add_on_assigned", assigned)
    for key, value in (("replacement_available", replacement), ("in_use", in_use)):
        if value is None:
            del findings[f"telephony.{key}"]
        else:
            _set_value(findings, f"telephony.{key}", value)

    row = _status("telephony", findings, status_rules, catalogue)

    assert row.status == status and row.incomplete == incomplete
    if assigned and replacement is None:
        assert row.deciding is None
        assert findings["telephony.licence_add_on_assigned"] in row.evidence
        assert (
            MissingEvidence("telephony.replacement_available", "answer_not_provided", None)
            in row.missing
        )


def test_measured_non_use_cannot_replace_the_telephony_confirmation(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    confirmation = complete_evidence["telephony.in_use"]
    complete_evidence[confirmation.id] = replace(
        confirmation, provenance="measured", source="sample.licences", coverage=Coverage("complete")
    )

    row = _status("telephony", complete_evidence, status_rules, catalogue)

    assert row.status == "unknown"
    assert row.missing == (MissingEvidence(confirmation.id, "answer_not_provided", None),)


@pytest.mark.parametrize("answered", [False, True])
def test_premium_power_platform_add_on_is_a_problem_with_or_without_usage_answer(
    complete_evidence: dict[str, Finding],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    answered: bool,
) -> None:
    findings = complete_evidence
    _set_value(findings, "power_platform.licence_add_on_assigned", True)
    if not answered:
        del findings["power_platform.in_use"]

    row = _status("power_platform", findings, status_rules, catalogue)

    assert row.deciding is not None and row.deciding.id == "power-premium-licences"
    assert row.status == "needs_work" and row.incomplete == (not answered)
    if not answered:
        assert row.missing == (
            MissingEvidence("power_platform.in_use", "answer_not_provided", None),
        )


def test_bundled_licence_does_not_establish_use(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    _set_value(complete_evidence, "small_apps.licence_bundled_assigned", True)
    del complete_evidence["small_apps.in_use"]

    row = _status("small_apps", complete_evidence, status_rules, catalogue)

    assert row.status == "unknown" and row.reason_code == "licensed_use_not_measured"
    assert row.incomplete


@pytest.mark.parametrize(
    ("value", "reason", "status"),
    [
        (None, None, "unknown"),
        (None, "source_not_supplied", "unknown"),
        (0, None, "ready"),
        (3, None, "needs_work"),
    ],
)
def test_integrations_requires_a_known_count(
    complete_evidence: dict[str, Finding],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    value: int | None,
    reason: str | None,
    status: str,
) -> None:
    count = complete_evidence.pop("integrations.application_count")
    if reason:
        complete_evidence[count.id] = replace(
            count, provenance="unknown", value=None, missing_reason=reason
        )
    elif value is not None:
        complete_evidence[count.id] = replace(count, value=value)

    row = _status("integrations", complete_evidence, status_rules, catalogue)

    assert row.status == status
    if status == "unknown":
        assert row.reason_code == (reason or "answer_not_provided")


def test_risk_from_macros_is_cautious(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    _set_value(complete_evidence, "office_files.kind.macro", 40)
    row = _status("office_files", complete_evidence, status_rules, catalogue)

    assert row.status == "needs_work" and not row.incomplete
    assert row.deciding is not None and row.deciding.id == "office-macro"
    assert "may contain macros" in row.deciding.reason["en"]
    assert "separate content scan that this tool does not perform" in row.deciding.reason["en"]


def test_worst_rule_wins_and_ties_keep_file_order(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    findings = complete_evidence
    _set_value(findings, "directory.guest_count", 4)
    _set_value(findings, "directory.account_list_reviewed", False)
    directory = _status("directory", findings, status_rules, catalogue)
    assert directory.deciding is not None and directory.deciding.id == "directory-guests"
    assert [rule.id for rule in directory.notes] == ["directory-accounts-not-reviewed"]

    _set_value(findings, "windows_software.application_count", 1)
    _set_value(findings, "windows_software.without_web_version_count", 1)
    block = status_rules.workloads["windows_software"]
    edited = replace(
        status_rules,
        workloads={
            **status_rules.workloads,
            "windows_software": replace(block, rules=block.rules[::-1]),
        },
    )
    windows = _status("windows_software", findings, edited, catalogue)
    assert windows.status == "blocker"
    assert windows.deciding is not None and windows.deciding.id == "software-no-web-version"
    assert [rule.id for rule in windows.notes] == ["software-present"]


def test_windows_software_shows_confirmed_blocker_and_unanswered_item(
    complete_evidence: dict[str, Finding], catalogue: Catalogue
) -> None:
    count = replace(complete_evidence["windows_software.application_count"], value=2)
    no_web = replace(
        complete_evidence["windows_software.without_web_version_count"],
        value=1,
        coverage=Coverage("partial", scanned=1, total=2),
    )
    html = render_report(sample_scan("town", catalogue), lang="en", provided=(count, no_web))
    row = _readiness_row(html, "windows_software")

    assert 'data-status="blocker" data-incomplete' in row
    assert "At least one Windows-only application has no web version" in row
    assert "At least 1 application" in row and "1 of 2 answers supplied" in row
    assert "answer_not_provided" in row and "The answer is missing." in row


@pytest.mark.parametrize(
    ("coverage", "count", "status", "reason"),
    [
        ("complete", 0, "ready", None),
        ("partial", 3, "needs_work", None),
        ("partial", 0, "unknown", "coverage_partial"),
        ("unknown", 3, "unknown", "coverage_unknown"),
    ],
)
def test_partial_counts_can_confirm_only_positive_lower_bounds(
    complete_evidence: dict[str, Finding],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    coverage: str,
    count: int,
    status: str,
    reason: str | None,
) -> None:
    finding = complete_evidence["directory.guest_count"]
    complete_evidence[finding.id] = replace(finding, coverage=Coverage(coverage), value=count)

    row = _status("directory", complete_evidence, status_rules, catalogue)

    assert (row.status, row.reason_code) == (status, reason)
    assert row.incomplete == (coverage != "complete")


def test_partial_positive_overrides_a_provided_zero_and_displays_both(
    complete_evidence: dict[str, Finding], catalogue: Catalogue
) -> None:
    answer = complete_evidence["integrations.application_count"]
    measurement = replace(
        answer,
        value=4,
        provenance="measured",
        collector="directory",
        source="sample.directory",
        coverage=Coverage("partial", scanned=6, failed=2, total=8),
    )
    scan = sample_scan("town", catalogue)
    scan = replace(
        scan,
        findings=tuple(
            measurement if finding.id == answer.id else finding for finding in scan.findings
        ),
    )
    html = render_report(scan, lang="en", provided=(answer,))
    row = _readiness_row(html, "integrations")

    assert 'data-status="needs_work" data-incomplete' in row
    assert "At least 4 applications" in row and 'data-provenance="measured"' in row
    assert "0 applications" in row and 'data-provenance="provided"' in row
    assert load_locale("en")["readiness"]["conflict"] in row


@pytest.mark.parametrize(
    ("coverage", "count", "status", "first", "second"),
    [
        ("complete", 0, "ready", "0 applications", "7 applications"),
        ("partial", 0, "needs_work", "7 applications", "0 applications in the items checked"),
        ("partial", 4, "needs_work", "7 applications", "At least 4 applications"),
    ],
)
def test_complete_evidence_decides_when_values_do_not_conflict_with_a_lower_bound(
    complete_evidence: dict[str, Finding],
    catalogue: Catalogue,
    coverage: str,
    count: int,
    status: str,
    first: str,
    second: str,
) -> None:
    answer = replace(complete_evidence["integrations.application_count"], value=7)
    recorded = replace(
        answer,
        value=count,
        provenance="measured",
        collector="directory",
        source="sample.directory",
        coverage=Coverage(coverage),
    )
    scan = sample_scan("town", catalogue)
    scan = replace(
        scan, findings=tuple(recorded if item.id == answer.id else item for item in scan.findings)
    )
    row = _readiness_row(render_report(scan, lang="en", provided=(answer,)), "integrations")

    assert f'data-status="{status}"' in row and "data-incomplete" not in row
    assert row.index(first) < row.index(second)
    assert load_locale("en")["readiness"]["conflict"] not in row


def test_when_ready_evidence_is_false_and_no_problem_fires(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    block = replace(status_rules.workloads["small_apps"], rules=())
    rules = replace(status_rules, workloads={**status_rules.workloads, "small_apps": block})
    _set_value(complete_evidence, "small_apps.in_use", True)

    row = _status("small_apps", complete_evidence, rules, catalogue)

    assert row.status == "unknown" and row.reason_code == "not_established"
    assert not row.incomplete


def test_skipped_collector_cannot_make_a_workload_ready(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    scan = sample_scan("town", catalogue)
    shared = complete_evidence["mail.shared_mailbox_count"]
    complete_evidence[shared.id] = replace(shared, collector="exchange_recipients")

    rows = evaluate(
        complete_evidence,
        status_rules,
        catalogue,
        collectors={collector.id: collector for collector in scan.collectors},
    )
    row = next(item for item in rows if item.workload == "mail")

    assert row.status == "unknown" and row.incomplete
    assert row.missing == (MissingEvidence(shared.id, "collector_skipped", "exchange_recipients"),)


def test_removing_a_workloads_evidence_never_gives_ready(
    complete_evidence: dict[str, Finding], status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    rows = evaluate(complete_evidence, status_rules, catalogue)
    assert tuple(row.workload for row in rows) == catalogue.workload_ids
    assert all(row.status == "ready" and not row.incomplete for row in rows)
    for workload in catalogue.workload_ids:
        without = {
            key: item for key, item in complete_evidence.items() if item.workload != workload
        }
        row = _status(workload, without, status_rules, catalogue)
        assert row.status == "unknown" and row.missing


def test_shipped_status_rules_define_each_workload(
    status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    path = rules_dir().joinpath("status.yaml")
    data = parse_yaml(read_text(path), path.name)
    assert set(data) == {"workloads"}
    assert tuple(status_rules.workloads) == catalogue.workload_ids
    assert {
        "telephony-no-replacement",
        "power-premium-licences",
        "integrations-present",
        "office-macro",
    } <= {rule.id for block in status_rules.workloads.values() for rule in block.rules}


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ("missing_de", "workloads.directory.rules[0].reason.de"),
        ("missing_operator", "workloads.directory.rules[0].when[0].op"),
        ("bad_operator", "workloads.directory.rules[0].when[0].op"),
        ("ready_status", "workloads.directory.rules[0].status"),
        ("unknown_finding", "workloads.directory.rules[0].when[0].finding"),
        ("literal", "workloads.directory.rules[0].when[0].value"),
        ("duplicate_id", "workloads.directory.rules[2].id"),
        ("missing_workload", "workloads.directory"),
        ("unknown_workload", "workloads"),
        ("empty_evidence", "workloads.directory.ready.evidence"),
    ],
)
def test_bad_status_rule_names_the_file_and_field(
    tmp_path: Path, catalogue: Catalogue, change: str, field: str
) -> None:
    path = tmp_path / "status.yaml"
    data = yaml.safe_load(read_text(rules_dir().joinpath(path.name)))
    block = data["workloads"]["directory"]
    rule = block["rules"][0]
    condition = rule["when"][0]
    match change:
        case "missing_de":
            del rule["reason"]["de"]
        case "missing_operator":
            condition["op"] = "missing"
        case "bad_operator":
            condition["op"] = "!="
        case "ready_status":
            rule["status"] = "ready"
        case "unknown_finding":
            condition["finding"] = "directory.some_other_count"
        case "literal":
            condition["value"] = True
        case "duplicate_id":
            block["rules"].append({**rule})
        case "missing_workload":
            del data["workloads"]["directory"]
        case "unknown_workload":
            data["workloads"]["unlisted"] = block
        case "empty_evidence":
            block["ready"]["evidence"] = []
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(InputError) as caught:
        load_status_rules(catalogue, path)

    assert (caught.value.file, caught.value.field) == (path.name, field)


def test_shipped_risky_extensions(catalogue: Catalogue) -> None:
    kinds = load_risky_file_types(catalogue)
    assert {kind.id: kind.extensions for kind in kinds} == {
        "macro": ("xlsm", "xltm", "xlam", "docm", "dotm", "pptm", "potm"),
        "access": ("accdb", "mdb"),
        "publisher": ("pub",),
        "visio": ("vsdx",),
        "onenote": ("one",),
    }
    assert {extension for kind in kinds for extension in kind.extensions} == {
        "xlsm",
        "xltm",
        "xlam",
        "docm",
        "dotm",
        "pptm",
        "potm",
        "accdb",
        "mdb",
        "pub",
        "vsdx",
        "one",
    }


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ("duplicate_extension", "kinds[1].extensions[0]"),
        ("missing_de", "kinds[0].label.de"),
        ("empty_extensions", "kinds[0].extensions"),
        ("repeated_kind", "kinds[1].id"),
        ("unknown_kind", "kinds[0].id"),
        ("uppercase", "kinds[0].extensions[0]"),
        ("leading_dot", "kinds[0].extensions[0]"),
    ],
)
def test_bad_risky_file_list_names_the_file_and_field(
    tmp_path: Path, catalogue: Catalogue, change: str, field: str
) -> None:
    path = tmp_path / "risky_file_types.yaml"
    data = parse_yaml(read_text(rules_dir().joinpath(path.name)), path.name)
    first, second, *_ = data["kinds"]
    match change:
        case "duplicate_extension":
            second["extensions"][0] = first["extensions"][0]
        case "missing_de":
            del first["label"]["de"]
        case "empty_extensions":
            first["extensions"] = []
        case "repeated_kind":
            second["id"] = first["id"]
        case "unknown_kind":
            first["id"] = "project"
        case "uppercase":
            first["extensions"][0] = "XLSM"
        case "leading_dot":
            first["extensions"][0] = ".xlsm"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(InputError) as caught:
        load_risky_file_types(catalogue, path)

    assert (caught.value.file, caught.value.field) == (path.name, field)


def _attention(html: str) -> str:
    section = re.search(r'<section data-section="attention">.*?</section>', html, re.S)
    assert section is not None
    return section[0]


@pytest.mark.parametrize("lang", ["en", "de"])
def test_attention_shows_risky_types_and_windows_software(
    tmp_path: Path, catalogue: Catalogue, lang: str
) -> None:
    source = files("m365_exit_scan").joinpath("demo", "town", "scan.json")
    result = CliRunner().invoke(
        app, ["report", str(source), "--lang", lang, "--out", str(tmp_path)]
    )
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file()
    html = path.read_text(encoding="utf-8")
    section = _attention(html)
    strings = load_locale(lang)
    assert "<caption data-sample>" in section
    for kind in load_risky_file_types(catalogue):
        row = re.search(rf'<tr data-kind="{kind.id}".*?</tr>', section, re.S)
        assert row is not None
        assert kind.label[lang] in row[0] and kind.note[lang] in row[0]
        assert all(f"<code>.{extension}</code>" in row[0] for extension in kind.extensions)
        assert strings["provenance"]["unknown"] in row[0]
        assert all(
            phrase in row[0]
            for phrase in strings["reason"]["not_collected_in_this_version"].values()
        )
    macro_label = "may contain macros" if lang == "en" else "kann makros enthalten"
    assert macro_label in section.lower() and ".dotx" not in section
    software_ids = (
        "windows_software.application_count",
        "windows_software.without_web_version_count",
    )
    assert re.findall(r'data-software-count="([^"]+)"', section) == list(software_ids)
    for finding_id in software_ids:
        detail = re.search(rf'<dd data-software-count="{finding_id}".*?</dd>', section, re.S)
        assert detail is not None and strings["provenance"]["unknown"] in detail[0]
        assert strings["reason"]["not_collected_in_this_version"]["fix"] in detail[0]
    sections = re.findall(r'data-section="([^"]+)"', html)
    assert sections == [section for section in SECTION_ORDER if section in sections]


def test_attention_shows_provided_counts_and_zero_explicitly(
    complete_evidence: dict[str, Finding], catalogue: Catalogue
) -> None:
    answers = (
        replace(complete_evidence["office_files.kind.macro"], value=40),
        complete_evidence["office_files.kind.access"],
        replace(complete_evidence["windows_software.application_count"], value=4),
        replace(complete_evidence["windows_software.without_web_version_count"], value=1),
    )
    section = _attention(render_report(sample_scan("town", catalogue), lang="en", provided=answers))

    assert "40 files" in section and "0 files" in section and "None were reported." in section
    assert "4 applications" in section and "1 application" in section
    assert section.count('data-provenance="provided"') == len(answers)


def test_removing_an_extension_changes_the_next_demo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules.rules_dir())), copied)
    path = copied / "risky_file_types.yaml"
    source = read_text(path)
    assert "potm" in source
    path.write_text(source.replace(", potm", ""), encoding="utf-8")
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)

    result = CliRunner().invoke(app, ["demo", "--out", str(tmp_path / "out")])

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.splitlines()[-1])
    assert report.is_file()
    section = _attention(report.read_text(encoding="utf-8"))
    assert "<code>.pptm</code>" in section and "<code>.potm</code>" not in section
