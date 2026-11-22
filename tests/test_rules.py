# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from dataclasses import asdict, replace
from datetime import date
from html import unescape
from importlib.resources import files
from pathlib import Path
from shutil import copytree

import pytest
import yaml
from helpers import readiness_row, report_section, runner
from report_expectations import SECTION_ORDER

from fazit import i18n, rules
from fazit.catalogue import Catalogue, load_catalogue
from fazit.cli import app
from fazit.errors import InputError
from fazit.i18n import load_locale
from fazit.inputs import Inputs, WindowsSoftware
from fazit.licences import classify_product, licence_findings, load_service_plans
from fazit.mappings import COVERAGE_LADDER, PROFILES, load_mapping
from fazit.model import (
    Coverage,
    Finding,
    FindingValue,
    Product,
    Scan,
    ServicePlan,
    load_scan_text,
)
from fazit.parsing import parse_yaml, read_text
from fazit.report import render_report
from fazit.risky_files import load_risky_file_types
from fazit.rules import rules_dir
from fazit.status import MissingEvidence, StatusRuleSet, WorkloadStatus, evaluate, load_status_rules

LICENSING_REFERENCE = (
    "https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference"
)
FUNCTION_IDS = (
    "identity_management",
    "mail_and_calendar",
    "personal_files",
    "team_files",
    "sharepoint_workflows",
    "chat",
    "video_meetings",
    "teams_chat_history",
    "office_editing",
    "vba_macros",
    "device_management",
    "desktop_operating_system",
    "windows_applications",
    "automation_and_low_code",
    "telephony",
    "single_sign_on",
    "security_and_compliance",
    "forms_tasks_bookings",
    "application_integrations",
)


@pytest.fixture
def catalogue() -> Catalogue:
    return load_catalogue()


def sample_scan(sample: str, catalogue: Catalogue) -> Scan:
    source = files("fazit").joinpath("demo", sample, "scan.json")
    return load_scan_text(read_text(source), source.name, catalogue)


@pytest.mark.parametrize("profile", PROFILES)
def test_shipped_mapping_covers_every_workload(catalogue: Catalogue, profile: str) -> None:
    mapping = load_mapping(profile, catalogue)
    rows = {row.function: row for row in mapping.functions}
    source = rules_dir().joinpath("mappings", mapping.file_name)

    assert read_text(source).startswith("# SPDX-License-Identifier: AGPL-3.0-or-later\n")
    assert mapping.profile == profile and mapping.file_name == f"{profile}.yaml"
    assert mapping.product_profile is (profile != "generic")
    assert tuple(rows) == FUNCTION_IDS and len(mapping.functions) == len(rows)
    assert mapping.no_function == ("licences",)
    assert set(mapping.no_function) | {row.workload for row in rows.values()} == set(
        catalogue.workload_ids
    )
    assert all(row.coverage in COVERAGE_LADDER for row in rows.values())
    for key in ("teams_chat_history", "vba_macros", "sharepoint_workflows"):
        assert rows[key].coverage == "not_available"
    if mapping.product_profile:
        assert all(
            row.reference_url and row.reference_url.startswith("https://") for row in rows.values()
        )
        assert all(isinstance(row.checked_on, date) for row in rows.values())
    else:
        assert all(row.reference_url is None and row.checked_on is None for row in rows.values())
        assert {row.coverage for row in rows.values()} <= set(COVERAGE_LADDER[4:])
    if profile == "opendesk":
        assert "Nubus" in rows["identity_management"].replacement["en"]
        assert "Keycloak" in rows["single_sign_on"].replacement["en"]


def test_generic_mapping_names_no_target_products() -> None:
    generic = read_text(rules_dir().joinpath("mappings", "generic.yaml"))
    target_products = (
        "openDesk",
        "Nubus",
        "Keycloak",
        "Open-Xchange",
        "OX App Suite",
        "Nextcloud",
        "Element",
        "Jitsi",
        "Collabora Online",
        "OpenProject",
        "Euro-Office",
        "Windmill",
        "Team Folders",
        "OIDC Identity Provider",
    )
    for product in target_products:
        assert not re.search(rf"\b{re.escape(product)}\b", generic, re.IGNORECASE), product


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ("missing_de", "functions[0].replacement.de"),
        ("unknown_workload", "functions[0].workload"),
        ("repeated_function", "functions[1].function"),
        ("wrong_profile", "profile"),
        ("bad_coverage", "functions[0].coverage"),
        ("omit_reference", "functions[0].reference_url"),
        ("omit_date", "functions[0].checked_on"),
        ("bad_reference", "functions[0].reference_url"),
        ("bad_date", "functions[0].checked_on"),
        ("unmapped_workload", "no_function"),
        ("overlap", "no_function"),
        ("bad_product_flag", "product_profile"),
        ("unknown_need", "functions[0].need_finding"),
        ("count_as_need", "functions[0].need_finding"),
        ("other_workload_need", "functions[0].need_finding"),
    ],
)
def test_bad_mapping_names_the_file_and_field(
    tmp_path: Path, catalogue: Catalogue, change: str, field: str
) -> None:
    directory = tmp_path / "mappings"
    directory.mkdir()
    path = directory / "opendesk.yaml"
    data = parse_yaml(read_text(rules_dir().joinpath("mappings", path.name)), path.name)
    first, second, *_ = data["functions"]
    match change:
        case "missing_de":
            del first["replacement"]["de"]
        case "unknown_workload":
            first["workload"] = "unrecognised"
        case "repeated_function":
            second["function"] = first["function"]
        case "wrong_profile":
            data["profile"] = "nextcloud"
        case "bad_coverage":
            first["coverage"] = "fully_equivalent"
        case "omit_reference":
            del first["reference_url"]
        case "omit_date":
            del first["checked_on"]
        case "bad_reference":
            first["reference_url"] = "http://example.invalid/"
        case "bad_date":
            first["checked_on"] = "2026-02-30"
        case "unmapped_workload":
            data["no_function"] = []
        case "overlap":
            data["no_function"].append(first["workload"])
        case "bad_product_flag":
            data["product_profile"] = "true"
        case "unknown_need":
            first["need_finding"] = "directory.unrecognised"
        case "count_as_need":
            first["need_finding"] = "directory.user_count"
        case "other_workload_need":
            first["need_finding"] = "telephony.in_use"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(InputError) as caught:
        load_mapping("opendesk", catalogue, tmp_path)

    assert (caught.value.file, caught.value.field) == (path.name, field)


def test_shipped_service_plans_cite_the_reference(catalogue: Catalogue) -> None:
    plans = load_service_plans(catalogue)

    assert plans
    assert all(
        catalogue.accepts_plan_name(plan.name, plan.guid)
        and catalogue.accepts_sku_part_number(plan.sku_part_number, plan.sku_guid)
        for plan in plans
    )
    assert {
        (plan.name, plan.guid)
        for plan in plans
        if not re.fullmatch(r"[A-Za-z0-9_]{1,64}", plan.name)
    } == {
        ("Skype for Business PSTN Calling Domestic Small", "9a0125a5-c8f8-4526-b231-49e2abe0ebce")
    }
    assert {plan.workload for plan in plans} <= {None, *catalogue.workload_ids}
    assert {plan.signal for plan in plans} == {"add_on", "bundled", "no_workload"}
    assert all((plan.workload is None) == (plan.signal == "no_workload") for plan in plans)
    assert {plan.reference_url for plan in plans} == {LICENSING_REFERENCE}
    assert all(isinstance(plan.checked_on, date) for plan in plans)
    phone = {(plan.sku_part_number, plan.signal) for plan in plans if plan.name == "MCOEV"}
    assert {("SPE_E5", "bundled"), ("MCOEV", "add_on")} <= phone


@pytest.mark.parametrize(
    ("section", "field", "value", "error_field"),
    [
        ("plan", "workload", "unrecognised", "plans[0].workload"),
        ("product", "measured", ["MCOEV"], "products[0]"),
        ("product", "add_on", ["UNKNOWN_PLAN"], "products[0].add_on[0]"),
        ("product", "add_on", ["MCOEV", "MCOEV"], "products[0].add_on[1]"),
        ("product", "no_workload", ["MCOEV"], "products[0].no_workload[0]"),
        ("root", "reference_url", None, "reference_url"),
        ("root", "reference_url", "https://learn.microsoft.com.example.invalid/", "reference_url"),
        ("root", "checked_on", None, "checked_on"),
        ("root", "checked_on", "2026-02-30", "checked_on"),
        ("product", "sku_guid", "not_a_guid", "products[0].sku_guid"),
        ("plan", "guid", "not_a_guid", "plans[0].guid"),
        ("product", "sku_part_number", "invalid product", "products[0].sku_part_number"),
        ("plan", "name", "invalid plan", "plans[0].name"),
        ("plan", "name", "repeat", "plans[1].name"),
        ("plan", "note", {"en": "Explanation only in English."}, "plans[0].note.de"),
    ],
)
def test_invalid_service_plan_names_the_field(
    tmp_path: Path, catalogue: Catalogue, section: str, field: str, value: object, error_field: str
) -> None:
    path = tmp_path / "service_plans.yaml"
    plan = {
        "name": "MCOEV",
        "guid": "4828c8ec-dc2e-4779-b502-87ac9ce28ab7",
        "workload": "telephony",
    }
    product = {
        "sku_part_number": "MCOEV",
        "sku_guid": "e43b5b99-8dfb-405f-9987-dc307f34bcbd",
        "add_on": ["MCOEV"],
    }
    data = {
        "reference_url": LICENSING_REFERENCE,
        "checked_on": "2026-11-21",
        "plans": [plan],
        "products": [product],
    }
    row = {"root": data, "product": product, "plan": plan}[section]
    if value is None:
        del row[field]
    elif value == "repeat":
        data["plans"].append({**plan, "name": "mcoev"})
    else:
        row[field] = value
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(InputError) as caught:
        load_service_plans(catalogue, path)

    assert (caught.value.file, caught.value.field) == (path.name, error_field)


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
    for product in scan.licences.products:
        expected = {(plan.name, plan.guid) for plan in plans if plan.sku_guid == product.sku_guid}
        assert expected and {(plan.name, plan.guid) for plan in product.service_plans} == expected
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
    coverage = Coverage("complete", len(products), 0, len(products))
    licensed = max((product.assigned for product in products), default=0)
    scan = replace(
        scan,
        licences=replace(scan.licences, products=products, coverage=coverage),
        findings=tuple(
            replace(finding, value=licensed)
            if finding.id == "directory.licensed_user_count"
            else finding
            for finding in scan.findings
        ),
    )
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
    empty = _product_findings(catalogue)
    assert len(empty) == 1 + 2 * len(catalogue.workloads)
    count = empty.pop("licences.product_count")
    assert (count.value, count.provenance, count.missing_reason) == (0, "measured", None)
    assert all(
        (finding.value, finding.provenance, finding.missing_reason) == (False, "measured", None)
        for finding in empty.values()
    )
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
    wrong_product = replace(
        phone, sku_part_number="OTHER_PRODUCT", sku_guid="00000000-0000-4000-8000-000000000001"
    )
    bad_plan_guid = replace(
        phone, service_plans=(replace(phone.service_plans[0], guid=phone.sku_guid),)
    )
    for product, reason in (
        (wrong_product, "licence_not_classified"),
        (bad_plan_guid, "licence_plan_list_incomplete"),
    ):
        findings = _product_findings(catalogue, product)
        del findings["licences.product_count"]
        assert all(
            (signal.value, signal.provenance, signal.missing_reason) == (None, "unknown", reason)
            for signal in findings.values()
        )
        assert classify_product(product, load_service_plans(catalogue)) == (None,)
    partly_classified_phone = replace(
        phone, service_plans=phone.service_plans + bad_plan_guid.service_plans
    )
    for products in ((phone, wrong_product), (partly_classified_phone,)):
        findings = _product_findings(catalogue, *products)
        assert findings["telephony.licence_add_on_assigned"].value is True
        assert findings["teams.licence_add_on_assigned"].value is None


def test_incomplete_roster_preserves_confirmed_assignments(catalogue: Catalogue) -> None:
    scan = sample_scan("town", catalogue)
    assert scan.licences is not None
    suite, phone, reporting = scan.licences.products
    baseline = _product_findings(catalogue, suite, phone, reporting)
    remaining = tuple(plan for plan in suite.service_plans if plan.name != "EXCHANGE_S_ENTERPRISE")
    partial = replace(suite, service_plans=(*remaining, remaining[0]))
    assert len(partial.service_plans) == len(suite.service_plans)
    findings = _product_findings(catalogue, partial, phone, reporting)

    for finding_id, complete in baseline.items():
        observed = findings[finding_id]
        if finding_id == "mail.licence_bundled_assigned" or complete.value is False:
            assert (observed.value, observed.provenance, observed.missing_reason) == (
                None,
                "unknown",
                "licence_plan_list_incomplete",
            )
        else:
            assert observed == complete


def test_render_report_checks_in_memory_licence_coverage(catalogue: Catalogue) -> None:
    scan = sample_scan("town", catalogue)
    assert scan.licences is not None
    suite, _, reporting = scan.licences.products
    scan = replace(scan, licences=replace(scan.licences, products=(suite, reporting)))

    with pytest.raises(InputError, match="invalid_licence_coverage") as caught:
        render_report(scan, lang="en", catalogue=catalogue)
    assert (caught.value.file, caught.value.field) == ("scan.json", "licences.coverage")


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
    source.write_text(json.dumps(asdict(scan)), encoding="utf-8")
    result = runner.invoke(app, ["report", str(source), "--out", str(tmp_path / "out")])

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
    findings = _product_findings(
        catalogue, *(replace(product, assigned=0) for product in scan.licences.products)
    )
    for entry in catalogue.findings:
        manual = entry.provided != "no"
        value: FindingValue = False if entry.type == "boolean" else 0
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
        (True, False, False, "needs_work", False),
        (True, True, False, "needs_work", False),
        (True, None, False, "needs_work", False),
        (True, None, True, "unknown", True),
        (True, None, None, "unknown", True),
        (True, False, None, "unknown", True),
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
    if assigned and replacement is None and in_use is not False:
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
            "windows_software": replace(
                block, rules=(block.rules[1], replace(block.rules[0], status="blocker"))
            ),
        },
    )
    windows = _status("windows_software", findings, edited, catalogue)
    assert windows.status == "blocker"
    assert windows.deciding is not None and windows.deciding.id == "software-no-web-version"
    assert [rule.id for rule in windows.notes] == ["software-present"]


def test_windows_software_shows_confirmed_dependency_and_unanswered_item(
    catalogue: Catalogue,
) -> None:
    inputs = Inputs(
        windows_only_software=(
            WindowsSoftware("Example application", vendor_has_web_version=False),
            WindowsSoftware("Unanswered application"),
        )
    )
    html = render_report(sample_scan("town", catalogue), lang="en", inputs=inputs)
    row = readiness_row(html, "windows_software")

    assert 'data-status="needs_work" data-incomplete' in row
    assert "At least one Windows-only application has no web version" in row
    assert "At least 1 application" in row and "1 of 2 answers supplied" in row
    assert "answer_not_provided" in row and "The answer is missing." in row


@pytest.mark.parametrize(
    ("coverage", "count", "status", "reason"),
    [
        ("complete", 0, "ready", None),
        ("partial", 3, "needs_work", None),
        ("partial", 0, "unknown", "coverage_partial"),
        ("unknown", 3, "needs_work", None),
        ("unknown", 0, "unknown", "coverage_unknown"),
    ],
)
def test_incomplete_counts_can_confirm_only_positive_lower_bounds(
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
    html = render_report(scan, lang="en", inputs=Inputs(provided_counts={answer.id: 0}))
    row = readiness_row(html, "integrations")

    assert 'data-status="needs_work" data-incomplete' in row
    assert "At least 4 applications" in row and 'data-provenance="measured"' in row
    assert "0 applications" in row and 'data-provenance="provided"' in row
    assert "6 of 8 scanned" in row
    assert load_locale("en")["readiness"]["conflict"] in row
    move = re.search(r'<tr data-function="application_integrations".*?</tr>', html, re.S)
    assert move is not None and 'href="#readiness-integrations"' in move[0]
    assert "At least 4 applications" not in move[0] and "0 applications" not in move[0]


@pytest.mark.parametrize(
    ("coverage", "count", "status", "first", "second"),
    [
        ("complete", 0, "unknown", "0 applications", "7 applications"),
        ("complete", 8, "unknown", "8 applications", "7 applications"),
        ("partial", 0, "needs_work", "7 applications", "0 applications in the items checked"),
        ("partial", 4, "needs_work", "7 applications", "At least 4 applications"),
    ],
)
def test_complete_counts_must_agree_but_a_partial_count_can_be_consistent(
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
    html = render_report(scan, lang="en", inputs=Inputs(provided_counts={answer.id: 7}))
    row = readiness_row(html, "integrations")

    assert f'data-status="{status}"' in row
    assert ("data-incomplete" in row) is (coverage == "complete")
    assert row.index(first) < row.index(second)
    strings = load_locale("en")
    assert strings["readiness"]["conflict"] not in row
    assert (strings["reason"]["confirmation_conflict"]["label"] in row) is (coverage == "complete")
    if coverage == "complete":
        for source in ("sample.directory", "inputs_yaml"):
            assert strings["source"][source] in row
        ready = re.search(r'<ul data-path-status="ready".*?</ul>', html, re.S)
        assert ready is None or 'data-path-workload="integrations"' not in ready[0]
        assert "need their integrations reviewed" not in row
        assert "shows no applications integrated" not in row


@pytest.mark.parametrize("check_ready", [True, False], ids=["ready", "problem"])
def test_disputed_count_blocks_every_workload_that_uses_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue: Catalogue, check_ready: bool
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules_dir())), copied)
    path = copied / "status.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    finding_id = "integrations.application_count"
    block = data["workloads"]["small_apps"]
    if check_ready:
        block["ready"]["evidence"].append({"finding": finding_id, "op": "==", "value": 0})
    else:
        block["rules"].append(
            {
                "id": "small-apps-integrations",
                "when": [{"finding": finding_id, "op": ">", "value": 0, "provenance": "provided"}],
                "status": "needs_work",
                "reason": {"en": "Review integrations.", "de": "Prüfen Sie die Schnittstellen."},
            }
        )
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)
    scan = sample_scan("town", catalogue)
    recorded = replace(
        scan.finding(finding_id),
        value=0,
        provenance="measured",
        collector="directory",
        source="sample.directory",
        collected_at=scan.generated_at,
        coverage=Coverage("complete"),
        missing_reason=None,
    )
    scan = replace(
        scan, findings=tuple(recorded if item.id == finding_id else item for item in scan.findings)
    )
    answers = Inputs(
        provided_counts={finding_id: 3},
        confirmations={"small_apps.in_use": False},
    )

    html = render_report(scan, lang="en", inputs=answers)
    pilots = re.search(r'<ul data-path-status="ready".*?</ul>', html, re.S)
    for workload in ("small_apps", "integrations"):
        row = readiness_row(html, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert 'data-reason="confirmation_conflict"' in row
        assert "0 applications" in row and "3 applications" in row
        assert pilots is None or f'data-path-workload="{workload}"' not in pilots[0]


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


@pytest.mark.parametrize(
    ("field", "before", "after", "lang"),
    [
        ("workloads[0].label", "label: workload.licences", "label: workload.licensse", "de"),
        (
            "findings[0].label",
            "label: finding.licences.contract_terms_known",
            "label: finding.licences.contract_terms",
            "en",
        ),
        ("findings[1].unit", "unit: users", "unit: usres", "de"),
    ],
)
def test_bad_catalogue_label_exits_with_a_localised_sentence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    before: str,
    after: str,
    lang: str,
) -> None:
    path = tmp_path / "rules" / "findings.yaml"
    path.parent.mkdir()
    data = read_text(rules_dir().joinpath(path.name))
    path.write_text(data.replace(before, after, 1), encoding="utf-8")
    monkeypatch.setattr("fazit.catalogue.files", lambda _: tmp_path)
    out = tmp_path / "out"
    strings = load_locale(lang)

    result = runner.invoke(app, ["demo", "--lang", lang, "--out", str(out)])

    message = strings["errors"]["invalid_label"].format(file=path.name, field=field)
    assert result.stderr.splitlines() == [strings["cli"]["error_prefix"].format(message=message)]
    assert result.exit_code == 2 and not result.stdout and not out.exists()


@pytest.mark.parametrize(
    ("lang", "prefix", "file", "field"),
    [
        ("de", "  licences: Lizenzen", "findings.yaml", "workloads[0].label"),
        ("en", "  sample.directory:", "en.yaml", "source.sample.directory"),
        ("de", "  sample.licences:", "de.yaml", "source.sample.licences"),
        ("en", "  sample.interview:", "en.yaml", "source.sample.interview"),
    ],
)
def test_catalogue_rejects_a_label_missing_only_in_the_other_locale(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    lang: str,
    prefix: str,
    file: str,
    field: str,
) -> None:
    locales = tmp_path / "locales"
    copytree(Path(str(files("fazit").joinpath("locales"))), locales)
    path = locales / f"{lang}.yaml"
    source = path.read_text(encoding="utf-8")
    line = next(line for line in source.splitlines(keepends=True) if line.startswith(prefix))
    path.write_text(source.replace(line, "", 1), encoding="utf-8")
    monkeypatch.setattr("fazit.i18n.files", lambda _: tmp_path)
    i18n._read_locale.cache_clear()
    request.addfinalizer(i18n._read_locale.cache_clear)
    other = "en" if lang == "de" else "de"
    out = tmp_path / "out"

    result = runner.invoke(app, ["demo", "--lang", other, "--out", str(out)])

    strings = load_locale(other)
    message = strings["errors"]["invalid_label"].format(file=file, field=field)
    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert result.stderr.splitlines() == [strings["cli"]["error_prefix"].format(message=message)]


def test_shipped_risky_extensions(catalogue: Catalogue) -> None:
    kinds = load_risky_file_types(catalogue)
    assert {kind.id: kind.extensions for kind in kinds} == {
        "macro": (
            "xlsm",
            "xltm",
            "xlam",
            "xlsb",
            "docm",
            "dotm",
            "pptm",
            "potm",
            "ppam",
            "ppsm",
            "sldm",
        ),
        "access": ("accdb", "mdb"),
        "publisher": ("pub",),
        "visio": ("vsdx",),
        "onenote": ("one",),
    }
    assert {extension for kind in kinds for extension in kind.extensions} == {
        "xlsm",
        "xltm",
        "xlam",
        "xlsb",
        "docm",
        "dotm",
        "pptm",
        "potm",
        "ppam",
        "ppsm",
        "sldm",
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


@pytest.mark.parametrize("lang", ["en", "de"])
def test_attention_shows_risky_types_and_windows_software(
    tmp_path: Path, catalogue: Catalogue, lang: str
) -> None:
    source = files("fazit").joinpath("demo", "town", "scan.json")
    result = runner.invoke(app, ["report", str(source), "--lang", lang, "--out", str(tmp_path)])
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file()
    html = path.read_text(encoding="utf-8")
    section = report_section(html, "attention")
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


def test_attention_shows_provided_counts_and_zero_explicitly(catalogue: Catalogue) -> None:
    software = tuple(
        WindowsSoftware(f"Example application {number}", vendor_has_web_version=number != 1)
        for number in range(1, 5)
    )
    inputs = Inputs(
        provided_counts={"office_files.kind.macro": 40, "office_files.kind.access": 0},
        windows_only_software=software,
    )
    section = report_section(
        render_report(sample_scan("town", catalogue), lang="en", inputs=inputs), "attention"
    )

    assert "40 files" in section and "0 files" in section and "None were reported." in section
    assert "4 applications" in section and "1 application" in section
    evidence, gaps = section.split('<div data-subsection="cannot-be-moved">', 1)
    figures = evidence.split('aria-labelledby="software-title"', 1)[0]
    assert figures.count('data-provenance="provided"') == 4
    assert evidence.count("data-software-entry") == len(software)
    for function in ("desktop_operating_system", "windows_applications"):
        gap = re.search(rf'<li data-gap="{function}" data-need="yes">.*?</li>', gaps, re.S)
        assert gap is not None and 'data-provenance="provided"' in gap[0]


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

    result = runner.invoke(app, ["demo", "--out", str(tmp_path / "out")])

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.splitlines()[-1])
    assert report.is_file()
    section = report_section(report.read_text(encoding="utf-8"), "attention")
    assert "<code>.pptm</code>" in section and "<code>.potm</code>" not in section


@pytest.mark.parametrize("profile", PROFILES)
def test_attention_lists_each_unavailable_function_from_the_profile(
    catalogue: Catalogue, profile: str
) -> None:
    mapping = load_mapping(profile, catalogue)
    gaps = [row for row in mapping.functions if row.coverage == "not_available"]
    html = render_report(sample_scan("town", catalogue), lang="en", profile=profile)
    section = report_section(html, "attention")
    details = dict(re.findall(r'<li data-gap="([^"]+)"([^>]*)>.*?</li>', section, re.S))

    assert 'data-subsection="cannot-be-moved"' in section
    assert list(details) == [row.function for row in gaps]
    for row in gaps:
        entry = re.search(rf'<li data-gap="{row.function}".*?</li>', section, re.S)
        assert entry is not None and "data-status=" not in entry[0]
        assert row.microsoft["en"] in unescape(entry[0])
        assert row.note and row.note["en"] in unescape(entry[0])
        if row.reference_url and row.checked_on:
            assert row.reference_url in unescape(entry[0])
            assert row.checked_on.isoformat() in entry[0]
        else:
            assert load_locale("en")["moves"]["no_project_check"] in entry[0]


@pytest.mark.parametrize(
    ("answer", "coverage", "expected"),
    [
        (True, None, "yes"),
        (False, None, "no"),
        (None, None, "unknown"),
        (True, "partial", "unknown"),
    ],
)
def test_gap_need_uses_only_its_declared_complete_answer(
    catalogue: Catalogue,
    complete_evidence: dict[str, Finding],
    answer: bool | None,
    coverage: str | None,
    expected: str,
) -> None:
    profile = load_mapping("opendesk", catalogue)
    finding = complete_evidence["teams.chat_history_must_be_kept"]
    gap = next(row for row in profile.functions if row.need_finding == finding.id)
    assert gap.coverage == "not_available"
    scan = sample_scan("town", catalogue)
    scan = replace(scan, findings=tuple(item for item in scan.findings if item.id != finding.id))
    inputs = Inputs(confirmations={finding.id: answer})
    if coverage is not None:
        partial = replace(finding, value=answer, coverage=Coverage(coverage))
        scan = replace(scan, findings=(*scan.findings, partial))
        inputs = Inputs()
    section = report_section(render_report(scan, lang="en", inputs=inputs), "attention")
    entry = re.search(rf'<li data-gap="{gap.function}".*?</li>', section, re.S)

    assert entry is not None and f'data-need="{expected}"' in entry[0]
    strings = load_locale("en")
    assert strings["attention"]["needed_here"] in entry[0]
    if expected == "unknown":
        assert 'data-provenance="unknown"' in entry[0]
        assert "data-reason=" in entry[0]
    else:
        assert 'data-provenance="provided"' in entry[0]
    for row in profile.functions:
        if row.coverage == "not_available" and row.need_finding is None:
            assert f'data-gap="{row.function}" data-need="unknown"' in section


def test_marking_a_mapping_unavailable_adds_it_to_the_gap_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules_dir())), copied)
    path = copied / "mappings" / "opendesk.yaml"
    data = parse_yaml(read_text(path), path.name)
    changed = next(row for row in data["functions"] if row["coverage"] == "in_suite")
    changed["coverage"] = "not_available"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)

    result = runner.invoke(app, ["demo", "--out", str(tmp_path / "out")])

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.splitlines()[-1])
    assert report.is_file()
    section = report_section(report.read_text(encoding="utf-8"), "attention")
    assert f'data-gap="{changed["function"]}" data-need="unknown"' in section


def test_suggested_path_lists_only_the_designated_workload_statuses(
    catalogue: Catalogue, complete_evidence: dict[str, Finding]
) -> None:
    scan = sample_scan("town", catalogue)
    mail_gap = scan.finding("mail.shared_mailbox_count")
    assert mail_gap is not None and mail_gap.provenance == "unknown"
    complete_evidence[mail_gap.id] = mail_gap
    problem_values = {
        "licences.contract_terms_known": False,
        "directory.guest_count": 1,
        "sharepoint.custom_solutions_in_use": True,
        "teams.teams_with_guests_count": 1,
        "office_files.kind.macro": 1,
        "device_management.in_use": True,
        "windows_software.application_count": 1,
        "power_platform.in_use": True,
        "telephony.in_use": True,
        "security_compliance.protection_or_retention_in_use": True,
        "identity_access.sso_application_count": 1,
        "small_apps.in_use": True,
        "integrations.application_count": 1,
    }
    for finding_id, value in problem_values.items():
        _set_value(complete_evidence, finding_id, value)
    scan = replace(
        scan, findings=tuple(complete_evidence[entry.id] for entry in catalogue.findings)
    )
    html = render_report(scan, lang="en")
    path = re.search(r'<section data-section="path">.*?</section>', html, re.S)

    assert path is not None and "%" not in path[0]
    matches = re.findall(r'<ul data-path-status="([^"]+)"[^>]*>(.*?)</ul>', path[0], re.S)
    assert [
        (status, re.findall(r'data-path-workload="([^"]+)"', items)) for status, items in matches
    ] == [("blocker", ["telephony"]), ("unknown", ["mail"]), ("ready", ["onedrive"])]
    assert "no replacement" in matches[0][1]
    assert load_locale("en")["reason"]["needs_recipient_export"]["fix"] in matches[1][1]
    strings = load_locale("en")["path"]
    for key in ("blocker", "unknown", "ready", "pilot_evidence", "pilot_choice"):
        assert strings[key] in unescape(path[0])
    assert re.findall(r"<li>(.*?)</li>", unescape(path[0]), re.S) == strings["steps"]


def test_suggested_path_explains_empty_lists(catalogue: Catalogue) -> None:
    html = render_report(sample_scan("town", catalogue), lang="en")
    path = re.search(r'<section data-section="path">.*?</section>', html, re.S)
    strings = load_locale("en")["path"]["empty"]

    assert path is not None
    for status in ("blocker", "ready"):
        assert strings[status] in path[0]
        assert f'data-path-status="{status}"' not in path[0]
