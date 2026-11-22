# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections import Counter
from dataclasses import asdict, replace
from datetime import date
from html import unescape
from importlib.resources import files
from pathlib import Path
from shutil import copytree

import pytest
import yaml
from helpers import (
    assert_readiness_order,
    readiness_row,
    report_section,
    runner,
    sample_inputs_path,
)
from report_expectations import SECTION_ORDER

from fazit import i18n, rules
from fazit import report as report_module
from fazit.catalogue import Catalogue, load_catalogue
from fazit.cli import app
from fazit.errors import InputError
from fazit.i18n import load_locale
from fazit.inputs import Inputs, WindowsSoftware, load_inputs
from fazit.licences import classify_product, licence_findings, load_service_plans
from fazit.mappings import COVERAGE_LADDER, GAP_COVERAGE, PROFILES, load_mapping
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
from fazit.status import (
    STEP_KINDS,
    Condition,
    MissingEvidence,
    StatusRuleSet,
    WorkloadStatus,
    evaluate,
    load_status_rules,
)

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
    assert mapping.reviewed_on is None
    assert tuple(key for key in rows if key in FUNCTION_IDS) == FUNCTION_IDS
    assert len(mapping.functions) == len(rows)
    assert mapping.no_function == ("licences",)
    assert set(mapping.no_function) | {row.workload for row in rows.values()} == set(
        catalogue.workload_ids
    )
    assert all(row.coverage in COVERAGE_LADDER for row in rows.values())
    assert {row.function for row in rows.values() if row.coverage == "transfer_undocumented"} == {
        "teams_chat_history",
        "vba_macros",
        "sharepoint_workflows",
    }
    assert all(row.need_finding for row in rows.values() if row.coverage in GAP_COVERAGE)
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
        assert tuple(rows) == (
            *FUNCTION_IDS[:5],
            "intranet_pages",
            *FUNCTION_IDS[5:10],
            "notes",
            "diagrams",
            *FUNCTION_IDS[10:],
        )
        assert all(row.checked_on == date(2026, 11, 22) for row in rows.values())
        assert all(
            row.reference_url != "https://docs.opendesk.eu/operations/architecture/"
            for row in rows.values()
        )
        for function, replacement in (
            ("intranet_pages", "XWiki"),
            ("notes", "Notes"),
            ("diagrams", "CryptPad with diagrams.net"),
        ):
            assert rows[function].coverage == "in_suite_with_limits"
            assert rows[function].replacement["en"] == replacement
    else:
        assert tuple(rows) == FUNCTION_IDS


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
        "XWiki",
        "Notes",
        "CryptPad",
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
        ("unassessed_workload", "no_function"),
        ("bad_product_flag", "product_profile"),
        ("unknown_need", "functions[0].need_finding"),
        ("count_as_need", "functions[0].need_finding"),
        ("other_workload_need", "functions[0].need_finding"),
        ("inferred_need", "functions[0]"),
        ("missing_review", "operator_review"),
        ("bad_review", "operator_review"),
        ("gap_without_need", "functions[0].need_finding"),
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
        case "unassessed_workload":
            data["no_function"] = [first["workload"]]
            first["workload"] = "licences"
        case "bad_product_flag":
            data["product_profile"] = "true"
        case "unknown_need":
            first["need_finding"] = "directory.unrecognised"
        case "count_as_need":
            first["need_finding"] = "directory.user_count"
        case "other_workload_need":
            first["need_finding"] = "telephony.in_use"
        case "inferred_need":
            first["need_finding"] = "directory.account_list_reviewed"
            first["need_if_positive"] = "directory.user_count"
        case "missing_review":
            data.pop("operator_review", None)
        case "bad_review":
            data["operator_review"] = "2026-02-30"
        case "gap_without_need":
            first["coverage"] = "not_available"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(InputError) as caught:
        load_mapping("opendesk", catalogue, tmp_path)

    assert (caught.value.file, caught.value.field) == (path.name, field)


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("lang", i18n.SUPPORTED_LANGUAGES)
def test_shipped_mappings_show_the_unreviewed_notice(
    catalogue: Catalogue, profile: str, lang: str
) -> None:
    html = render_report(sample_scan("town", catalogue), lang=lang, profile=profile)
    sentence = {
        "en": "This mapping has not yet been reviewed by someone who operates the target system.",
        "de": (
            "Diese Zuordnung wurde noch nicht von einer Person geprüft, "
            "die das Zielsystem betreibt."
        ),
    }[lang]
    marker = f'<p data-mapping-review="unreviewed">{sentence}</p>'

    assert report_section(html, "moves").count(marker) == 1
    assert report_section(html, "appendix").count(marker) == 1


@pytest.mark.parametrize("lang", i18n.SUPPORTED_LANGUAGES)
def test_reviewed_mapping_shows_the_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue: Catalogue, lang: str
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules_dir())), copied)
    path = copied / "mappings" / "opendesk.yaml"
    source = read_text(path)
    path.write_text(
        source.replace("operator_review: unreviewed", 'operator_review: "2026-12-01"'),
        encoding="utf-8",
    )
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)

    assert load_mapping("opendesk", catalogue).reviewed_on == date(2026, 12, 1)
    html = render_report(sample_scan("town", catalogue), lang=lang)
    sentence = {
        "en": (
            "This mapping was reviewed on 1 December 2026 by someone who operates "
            "the target system."
        ),
        "de": (
            "Diese Zuordnung wurde am 1. Dezember 2026 von einer Person geprüft, "
            "die das Zielsystem betreibt."
        ),
    }[lang]
    marker = f'<p data-mapping-review="2026-12-01">{sentence}</p>'
    assert report_section(html, "moves").count(marker) == 1
    assert report_section(html, "appendix").count(marker) == 1


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
    mapping = load_mapping("opendesk", catalogue)
    return next(
        row
        for row in evaluate(findings, status_rules, catalogue, mapping)
        if row.workload == workload
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
    ("workload", "finding_id", "rule_id", "other_finding"),
    [
        (
            "sharepoint",
            "sharepoint.workflows_in_use",
            "sharepoint-workflows",
            "sharepoint.custom_solutions_in_use",
        ),
        (
            "teams",
            "teams.apps_in_use",
            "teams-apps",
            "teams.chat_history_must_be_kept",
        ),
    ],
)
def test_sharepoint_and_teams_require_the_new_answers_for_ready(
    catalogue: Catalogue,
    status_rules: StatusRuleSet,
    complete_evidence: dict[str, Finding],
    workload: str,
    finding_id: str,
    rule_id: str,
    other_finding: str,
) -> None:
    ready = _status(workload, complete_evidence, status_rules, catalogue)
    assert ready.status == "ready" and not ready.incomplete

    answer = complete_evidence.pop(finding_id, None)
    missing = (MissingEvidence(finding_id, "answer_not_provided", None),)
    unknown = _status(workload, complete_evidence, status_rules, catalogue)
    assert unknown.status == "unknown" and unknown.incomplete and unknown.missing == missing

    assert answer is not None and answer.value is False
    complete_evidence[finding_id] = replace(answer, value=True)
    problem = _status(workload, complete_evidence, status_rules, catalogue)
    assert problem.status == "needs_work" and not problem.incomplete
    assert problem.deciding is not None and problem.deciding.id == rule_id
    step = problem.deciding.next_step
    assert step.kind == "clarify" and set(step.text) == {"en", "de"} and all(step.text.values())

    del complete_evidence[finding_id]
    _set_value(complete_evidence, other_finding, True)
    incomplete = _status(workload, complete_evidence, status_rules, catalogue)
    assert incomplete.status == "needs_work" and incomplete.incomplete
    assert incomplete.missing == missing


@pytest.mark.parametrize(
    ("assigned", "replacement", "in_use", "status", "incomplete"),
    [
        (True, False, True, "blocker", False),
        (True, True, True, "needs_work", False),
        (True, False, False, "needs_work", False),
        (True, True, False, "needs_work", False),
        (True, None, False, "needs_work", False),
        (True, None, True, "needs_work", True),
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
        if in_use is True:
            assert row.deciding is not None and row.deciding.id == "target-not-available-telephony"
        else:
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


@pytest.mark.parametrize("profile", PROFILES)
def test_evaluation_applies_profile_gaps_after_workload_rules(
    complete_evidence: dict[str, Finding],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    profile: str,
) -> None:
    _set_value(complete_evidence, "telephony.in_use", True)
    _set_value(complete_evidence, "teams.chat_history_must_be_kept", True)
    del complete_evidence["telephony.replacement_available"]
    del complete_evidence["device_management.windows_desktops_required"]
    mapping = load_mapping(profile, catalogue)
    rows = {
        row.workload: row for row in evaluate(complete_evidence, status_rules, catalogue, mapping)
    }

    phone = rows["telephony"]
    assert phone.missing == (
        MissingEvidence("telephony.replacement_available", "answer_not_provided", None),
    )
    if profile == "opendesk":
        (gap,) = phone.transfer_gaps
        assert gap.mapping.coverage == "not_available" and gap.mapping.function == "telephony"
        assert (gap.finding, gap.need, gap.reasons) == (
            complete_evidence["telephony.in_use"],
            "yes",
            (),
        )
        assert phone.status == "needs_work" and phone.reason_code is None
        assert phone.deciding is not None and phone.deciding.id == "target-not-available-telephony"
        assert phone.deciding.when == (Condition("telephony.in_use", "==", True),)
    else:
        assert phone.status == "unknown" and phone.deciding is None and not phone.transfer_gaps

    devices = rows["device_management"]
    if profile == "generic":
        assert devices.status == "ready" and not devices.incomplete and not devices.transfer_gaps
    else:
        assert [(gap.mapping.function, gap.need) for gap in devices.transfer_gaps] == [
            ("device_management", "no"),
            ("desktop_operating_system", "unknown"),
        ]
        assert devices.status == "unknown" and devices.reason_code == "answer_not_provided"
        assert devices.missing == (
            MissingEvidence(
                "device_management.windows_desktops_required", "answer_not_provided", None
            ),
        )

    teams = rows["teams"]
    assert teams.status == "needs_work" and not teams.incomplete
    assert teams.deciding is not None and teams.deciding.id == "teams-chat-history"
    (note,) = teams.notes
    assert note.id == "target-transfer-undocumented-teams-chat-history"
    assert note.when == (Condition("teams.chat_history_must_be_kept", "==", True),)
    assert note.next_step == status_rules.target_gaps["transfer_undocumented"].next_step


@pytest.mark.parametrize("lang", i18n.SUPPORTED_LANGUAGES)
@pytest.mark.parametrize("profile", PROFILES)
def test_target_gaps_reach_readiness_and_appendix(
    catalogue: Catalogue, status_rules: StatusRuleSet, lang: str, profile: str
) -> None:
    scan = sample_scan("town", catalogue)
    unanswered = {"device_management.windows_desktops_required", "telephony.replacement_available"}
    scan = replace(
        scan, findings=tuple(item for item in scan.findings if item.id not in unanswered)
    )
    inputs = Inputs(
        provided_counts={"device_management.windows_device_count": 0},
        confirmations={
            "device_management.in_use": False,
            "teams.chat_history_must_be_kept": True,
            "teams.apps_in_use": False,
            "telephony.in_use": True,
        },
    )
    html = render_report(scan, lang=lang, profile=profile, inputs=inputs)
    telephony = unescape(readiness_row(html, "telephony"))
    appendix = unescape(report_section(html, "appendix"))
    phone_rule = re.search(
        r'<div data-rule="target-not-available-telephony">.*?</div>', appendix, re.S
    )
    strings = load_locale(lang)

    phone_status = "needs_work" if profile == "opendesk" else "unknown"
    assert f'data-status="{phone_status}" data-incomplete' in telephony
    assert 'data-missing="telephony.replacement_available"' in telephony
    if profile == "opendesk":
        label = {
            "en": "Teams Phone and public telephone calling",
            "de": "Teams Phone und Anrufe ins öffentliche Telefonnetz",
        }[lang]
        template = status_rules.target_gaps["not_available"]
        reason = template.reason[lang].format(profile="openDesk", function=label)
        assert reason in telephony and template.next_step.text[lang] in telephony
        assert phone_rule is not None and reason in phone_rule[0]
        assert strings["status"]["needs_work"] in phone_rule[0]
        condition = strings["finding"]["telephony.in_use"]
        assert re.search(rf"{re.escape(condition)}\s+== {strings['common']['yes']}", phone_rule[0])
    else:
        assert phone_rule is None

    devices = readiness_row(html, "device_management")
    device_status = "ready" if profile == "generic" else "unknown"
    assert ("data-incomplete" in devices) is (profile != "generic")
    assert f'data-status="{device_status}"' in devices
    assert ('data-missing="device_management.windows_desktops_required"' in devices) is (
        profile != "generic"
    )

    teams = unescape(readiness_row(html, "teams"))
    assert 'data-status="needs_work"' in teams and "data-incomplete" not in teams
    assert 'data-rule="target-transfer-undocumented-teams-chat-history"' in appendix
    deciding = next(
        rule for rule in status_rules.workloads["teams"].rules if rule.id == "teams-chat-history"
    )
    mapping = load_mapping(profile, catalogue)
    gap = next(row for row in mapping.functions if row.function == "teams_chat_history")
    note = (
        status_rules.target_gaps[gap.coverage]
        .reason[lang]
        .format(profile=mapping.label[lang], function=gap.microsoft[lang])
    )
    assert deciding.next_step.text[lang] in teams
    assert teams.index(deciding.reason[lang]) < teams.index(note)
    assert appendix.index('data-rule="teams-chat-history"') < appendix.index(
        'data-rule="target-transfer-undocumented-teams-chat-history"'
    )


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
    assert [rule.id for rule in windows.notes] == [
        "software-present",
        "target-not-available-windows-applications",
    ]
    assert windows.notes[-1].when == (Condition("windows_software.application_count", ">", 0),)


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
        assert 'href="#readiness-integrations" data-unexamined-workload=' in report_section(
            html, "path"
        )
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
                "next_step": data["workloads"]["integrations"]["rules"][0]["next_step"].copy(),
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
    open_points = report_section(html, "path")
    for workload in ("small_apps", "integrations"):
        row = readiness_row(html, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert 'data-reason="confirmation_conflict"' in row
        assert "0 applications" in row and "3 applications" in row
        assert f'href="#readiness-{workload}" data-unexamined-workload=' in open_points


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
        load_mapping("opendesk", catalogue),
        collectors={collector.id: collector for collector in scan.collectors},
    )
    row = next(item for item in rows if item.workload == "mail")

    assert row.status == "unknown" and row.incomplete
    assert row.missing == (MissingEvidence(shared.id, "collector_skipped", "exchange_recipients"),)


@pytest.mark.parametrize("profile", PROFILES)
def test_removing_a_workloads_evidence_never_gives_ready(
    complete_evidence: dict[str, Finding],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    profile: str,
) -> None:
    mapping = load_mapping(profile, catalogue)
    rows = evaluate(complete_evidence, status_rules, catalogue, mapping)
    assert tuple(row.workload for row in rows) == catalogue.assessed_workload_ids
    assert all(row.status == "ready" and not row.incomplete for row in rows)
    assert all(gap.need == "no" for row in rows for gap in row.transfer_gaps)
    for workload in catalogue.assessed_workload_ids:
        without = {
            key: item for key, item in complete_evidence.items() if item.workload != workload
        }
        row = next(
            row
            for row in evaluate(without, status_rules, catalogue, mapping)
            if row.workload == workload
        )
        assert row.status == "unknown" and row.missing


def test_shipped_status_rules_define_each_assessed_workload(
    status_rules: StatusRuleSet, catalogue: Catalogue
) -> None:
    path = rules_dir().joinpath("status.yaml")
    data = parse_yaml(read_text(path), path.name)
    assert set(data) == {"workloads", "target_gaps"}
    assert tuple(status_rules.workloads) == catalogue.assessed_workload_ids
    assert set(status_rules.target_gaps) == set(GAP_COVERAGE)
    assert sum(len(block.rules) for block in status_rules.workloads.values()) == 32
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
        ("unassessed_workload", "workloads"),
        ("empty_evidence", "workloads.directory.ready.evidence"),
        ("missing_next_step", "workloads.directory.rules[0].next_step"),
        ("missing_next_step_en", "workloads.directory.rules[0].next_step.en"),
        ("missing_next_step_de", "workloads.directory.rules[0].next_step.de"),
        ("missing_step_kind", "workloads.directory.rules[0].next_step.kind"),
        ("invalid_step_kind", "workloads.directory.rules[0].next_step.kind"),
        ("blank_step_text", "workloads.directory.rules[0].next_step.de"),
        ("extra_step_field", "workloads.directory.rules[0].next_step"),
        ("ready_next_step", "workloads.directory.ready"),
        ("missing_target_gaps", "target_gaps"),
        ("missing_target_gap", "target_gaps.not_available"),
        ("extra_target_gap", "target_gaps"),
        ("target_blocker", "target_gaps.not_available.status"),
        ("target_without_function", "target_gaps.transfer_undocumented.reason.de"),
        ("target_extra_placeholder", "target_gaps.not_available.reason.en"),
        ("target_malformed_placeholder", "target_gaps.not_available.reason.en"),
        ("target_duplicate_id", "target_gaps.not_available.id"),
        ("target_duplicate_template_id", "target_gaps.not_available.id"),
        ("target_invalid_id", "target_gaps.not_available.id"),
        ("target_missing_step_kind", "target_gaps.not_available.next_step.kind"),
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
        case "unassessed_workload":
            data["workloads"]["licences"] = {"ready": block["ready"], "rules": []}
        case "empty_evidence":
            block["ready"]["evidence"] = []
        case "missing_next_step":
            rule.pop("next_step", None)
        case "missing_next_step_en":
            del rule["next_step"]["en"]
        case "missing_next_step_de":
            del rule["next_step"]["de"]
        case "missing_step_kind":
            del rule["next_step"]["kind"]
        case "invalid_step_kind":
            rule["next_step"]["kind"] = "fix"
        case "blank_step_text":
            rule["next_step"]["de"] = " "
        case "extra_step_field":
            rule["next_step"]["extra"] = True
        case "ready_next_step":
            block["ready"]["next_step"] = rule["next_step"].copy()
        case "missing_target_gaps":
            del data["target_gaps"]
        case "missing_target_gap":
            del data["target_gaps"]["not_available"]
        case "extra_target_gap":
            data["target_gaps"]["in_suite"] = data["target_gaps"]["not_available"].copy()
        case "target_blocker":
            data["target_gaps"]["not_available"]["status"] = "blocker"
        case "target_without_function":
            data["target_gaps"]["transfer_undocumented"]["reason"]["de"] = "{profile}."
        case "target_extra_placeholder":
            data["target_gaps"]["not_available"]["reason"]["en"] += " {other}."
        case "target_malformed_placeholder":
            data["target_gaps"]["not_available"]["reason"]["en"] += " {"
        case "target_duplicate_id":
            data["target_gaps"]["not_available"]["id"] = rule["id"]
        case "target_duplicate_template_id":
            data["target_gaps"]["not_available"]["id"] = data["target_gaps"][
                "transfer_undocumented"
            ]["id"]
        case "target_invalid_id":
            data["target_gaps"]["not_available"]["id"] = "invalid id"
        case "target_missing_step_kind":
            del data["target_gaps"]["not_available"]["next_step"]["kind"]
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(InputError) as caught:
        load_status_rules(catalogue, path)

    assert (caught.value.file, caught.value.field) == (path.name, field)


def test_all_problem_rules_have_bilingual_product_neutral_next_steps(
    status_rules: StatusRuleSet,
) -> None:
    banned = (
        "opendesk",
        "nextcloud",
        "collabora",
        "keycloak",
        "nubus",
        "element",
        "jitsi",
        "open-xchange",
        "openproject",
        "libreoffice",
        "univention",
        "xwiki",
        "cryptpad",
        "import",
        "export",
    )
    workload_rules = [rule for block in status_rules.workloads.values() for rule in block.rules]
    for rule in (*workload_rules, *status_rules.target_gaps.values()):
        assert rule.next_step.kind in STEP_KINDS, rule.id
        step = rule.next_step.text
        assert set(step) == set(i18n.SUPPORTED_LANGUAGES), rule.id
        for lang, text in step.items():
            assert text.endswith(".") and not re.search(r"[.?!]\s", text), (rule.id, lang)
            assert text != rule.reason[lang], (rule.id, lang)
            assert not any(word in text.casefold() for word in banned), (rule.id, lang)
    assert {rule.next_step.kind for rule in status_rules.target_gaps.values()} == {"replace"}


@pytest.mark.parametrize(
    ("lang", "banned"), [("en", ("block",)), ("de", ("hindernis", "verhinder", "blockier"))]
)
def test_only_blocker_rules_can_describe_a_blocker(
    status_rules: StatusRuleSet, lang: str, banned: tuple[str, ...]
) -> None:
    for workload, block in status_rules.workloads.items():
        assert not any(word in block.ready_reason[lang].casefold() for word in banned), workload
        for rule in block.rules:
            if rule.status != "blocker":
                for text in (rule.reason[lang], rule.next_step.text[lang]):
                    assert not any(word in text.casefold() for word in banned), (rule.id, text)
    for rule in status_rules.target_gaps.values():
        for text in (rule.reason[lang], rule.next_step.text[lang]):
            assert not any(word in text.casefold() for word in banned), (rule.id, text)


def test_next_step_kind_reaches_the_town_report_context(
    catalogue: Catalogue, status_rules: StatusRuleSet
) -> None:
    kinds = {
        rule.next_step.kind for block in status_rules.workloads.values() for rule in block.rules
    }
    assert kinds <= {"clarify", "decide", "replace"}

    scan = sample_scan("town", catalogue)
    inputs = load_inputs(sample_inputs_path("town"), catalogue)
    context, _ = report_module._prepare_report(scan, "en", "opendesk", catalogue, inputs)
    row = next(row for row in context["statuses"] if row.workload == "telephony")

    assert row.deciding is not None and row.deciding.id == "telephony-no-replacement"
    assert row.deciding.next_step.kind == "replace"


@pytest.mark.parametrize(("lang", "label"), [("en", "Next step"), ("de", "Nächster Schritt")])
def test_town_telephony_shows_deciding_next_step(
    catalogue: Catalogue, status_rules: StatusRuleSet, lang: str, label: str
) -> None:
    scan = sample_scan("town", catalogue)
    inputs = load_inputs(sample_inputs_path("town"), catalogue)
    html = render_report(scan, lang=lang, catalogue=catalogue, inputs=inputs)
    row = unescape(readiness_row(html, "telephony"))

    assert f'<p class="finding-next"><strong>{label}</strong>' in row
    rule = next(
        rule
        for rule in status_rules.workloads["telephony"].rules
        if rule.id == "telephony-no-replacement"
    )
    step = f'<p class="finding-next"><strong>{label}</strong> {rule.next_step.text[lang]}</p>'
    assert row.index(rule.reason[lang]) < row.index(step)
    assert 'class="finding-next"' not in readiness_row(html, "onedrive")
    security = unescape(readiness_row(html, "security_compliance"))
    fix = load_locale(lang)["reason"]["licensed_use_not_measured"]["fix"]
    assert f'<p class="finding-next"><strong>{label}</strong> {fix}</p>' in security


def test_next_step_text_is_autoescaped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue: Catalogue
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules_dir())), copied)
    path = copied / "status.yaml"
    data = yaml.safe_load(read_text(path))
    rule = next(
        rule
        for rule in data["workloads"]["telephony"]["rules"]
        if rule["id"] == "telephony-no-replacement"
    )
    rule["next_step"]["en"] = "The IT team tests the <b>replacement</b>."
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)
    scan = sample_scan("town", catalogue)
    inputs = load_inputs(sample_inputs_path("town"), catalogue)
    html = render_report(scan, lang="en", catalogue=catalogue, inputs=inputs)

    row = readiness_row(html, "telephony")
    assert "&lt;b&gt;replacement&lt;/b&gt;" in row
    assert "<b>replacement</b>" not in row


@pytest.mark.parametrize(
    ("field", "before", "after", "lang"),
    [
        ("workloads[0].label", "label: workload.licences", "label: workload.licensse", "de"),
        (
            "categories[0].label",
            "label: category.communication",
            "label: category.communicaton",
            "de",
        ),
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
        ("en", "  communication:", "findings.yaml", "categories[0].label"),
        ("de", "  communication:", "findings.yaml", "categories[0].label"),
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


@pytest.mark.parametrize("sample", ["town", "nonprofit"])
@pytest.mark.parametrize("lang", i18n.SUPPORTED_LANGUAGES)
@pytest.mark.parametrize("profile", PROFILES)
def test_demo_rows_show_the_categories_of_assessed_workloads(
    tmp_path: Path, catalogue: Catalogue, sample: str, lang: str, profile: str
) -> None:
    members = {
        "communication": ("mail", "teams", "telephony"),
        "files": ("onedrive", "sharepoint", "office_files"),
        "identity_devices": (
            "directory",
            "device_management",
            "windows_software",
            "identity_access",
        ),
        "automation_ai": ("power_platform", "small_apps", "integrations"),
        "security": ("security_compliance",),
    }
    assert [(entry.id, entry.label) for entry in catalogue.categories] == [
        (category, f"category.{category}") for category in members
    ]
    expected = {workload: category for category, group in members.items() for workload in group}
    assert {entry.id: entry.category for entry in catalogue.workloads if entry.assessed} == expected
    assert [(entry.id, entry.category) for entry in catalogue.workloads if not entry.assessed] == [
        ("licences", None)
    ]

    command = ["demo", "--sample", sample, "--lang", lang, "--profile", profile]
    result = runner.invoke(app, [*command, "--out", str(tmp_path)])
    assert result.exit_code == 0 and not result.stderr, result.output
    path = Path(result.stdout.splitlines()[-1])
    assert path.is_file()
    html = path.read_text(encoding="utf-8")
    table = report_section(html, "readiness")
    assert_readiness_order(table, catalogue.assessed_workload_ids)
    assert 'data-workload="licences" data-status=' not in html
    labels = load_locale(lang)["category"]
    for workload, category in expected.items():
        row = readiness_row(table, workload)
        assert f'data-category="{category}"' in row
        assert f'<span class="finding-category">{labels[category]}</span>' in unescape(row)


def test_changing_the_catalogue_category_changes_the_rendered_row(tmp_path: Path) -> None:
    source = rules_dir().joinpath("findings.yaml")
    path = tmp_path / source.name
    text = read_text(source).replace(
        "label: workload.mail\n    category: communication",
        "label: workload.mail\n    category: files",
    )
    path.write_text(text, encoding="utf-8")
    catalogue = load_catalogue(path)

    html = render_report(sample_scan("town", catalogue), lang="en", catalogue=catalogue)

    row = readiness_row(html, "mail")
    assert 'data-category="files"' in row
    assert '<span class="finding-category">Files and documents</span>' in row


@pytest.mark.parametrize("lang", i18n.SUPPORTED_LANGUAGES)
@pytest.mark.parametrize(
    ("coverage", "reason"),
    [(None, "not_in_scan"), ("partial", "coverage_partial"), ("unknown", "coverage_unknown")],
)
def test_licence_inventory_shows_its_coverage_gap(
    catalogue: Catalogue, lang: str, coverage: str | None, reason: str
) -> None:
    scan = sample_scan("town", catalogue)
    assert scan.licences is not None
    inventory = None if coverage is None else replace(scan.licences, coverage=Coverage(coverage))
    html = render_report(replace(scan, licences=inventory), lang=lang, catalogue=catalogue)

    found = report_section(html, "found")
    summary = re.search(
        r'<summary id="licences-title">.*?</summary>\s*(<p[^>]*>.*?</p>)', found, re.S
    )
    assert summary is not None
    evidence = summary[1]
    provenance = "unknown" if inventory is None else "measured"
    strings = load_locale(lang)
    assert f'data-provenance="{provenance}"' in evidence
    assert strings["provenance"][provenance] in evidence
    assert f'data-reason="{reason}"' in evidence
    assert all(text in unescape(evidence) for text in strings["reason"][reason].values())
    assert found.count("data-product=") == (0 if inventory is None else len(inventory.products))


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
            "xls",
            "xlt",
            "xla",
            "doc",
            "dot",
            "ppt",
            "pot",
            "pps",
            "ppa",
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
        "xls",
        "xlt",
        "xla",
        "doc",
        "dot",
        "ppt",
        "pot",
        "pps",
        "ppa",
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
    applications = re.search(
        r'<li data-gap="windows_applications" data-need="yes">.*?</li>', gaps, re.S
    )
    assert applications is not None and 'data-provenance="provided"' in applications[0]
    desktop = re.search(
        r'<li data-gap="desktop_operating_system" data-need="unknown">.*?</li>', gaps, re.S
    )
    assert desktop is not None and 'data-provenance="unknown"' in desktop[0]
    assert 'data-reason="answer_not_provided"' in desktop[0]


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
def test_attention_lists_each_transfer_gap_from_the_profile(
    catalogue: Catalogue, profile: str
) -> None:
    mapping = load_mapping(profile, catalogue)
    gaps = [row for row in mapping.functions if row.coverage in GAP_COVERAGE]
    html = render_report(sample_scan("town", catalogue), lang="en", profile=profile)
    section = report_section(html, "attention")
    details = dict(re.findall(r'<li data-gap="([^"]+)"([^>]*)>.*?</li>', section, re.S))

    assert 'data-subsection="cannot-be-moved"' in section
    assert list(details) == [row.function for row in gaps]
    for row in gaps:
        entry = re.search(rf'<li data-gap="{row.function}".*?</li>', section, re.S)
        assert entry is not None and "data-status=" not in entry[0]
        assert (
            f'<strong id="transfer-gap-{row.function}">{row.microsoft["en"]}</strong>'
            in unescape(entry[0])
        )
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
    gap = next(
        row
        for row in profile.functions
        if row.coverage in GAP_COVERAGE and row.need_finding == finding.id
    )
    assert gap.coverage == "transfer_undocumented"
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
    assert all(row.need_finding for row in profile.functions if row.coverage in GAP_COVERAGE)


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize(
    ("workflow_answer", "macro_answer", "workflow_need", "macro_need"),
    [(True, False, "yes", "no"), (False, None, "no", "unknown"), (None, True, "unknown", "yes")],
)
def test_workflow_and_vba_gaps_follow_their_own_answers(
    catalogue: Catalogue,
    profile: str,
    workflow_answer: bool | None,
    macro_answer: bool | None,
    workflow_need: str,
    macro_need: str,
) -> None:
    inputs = Inputs(
        confirmations={
            "sharepoint.workflows_in_use": workflow_answer,
            "office_files.vba_macros_in_use": macro_answer,
        }
    )
    html = render_report(sample_scan("town", catalogue), lang="en", profile=profile, inputs=inputs)
    attention = report_section(html, "attention")

    assert f'data-gap="sharepoint_workflows" data-need="{workflow_need}"' in attention
    assert f'data-gap="vba_macros" data-need="{macro_need}"' in attention


def test_town_transfer_gap_counts_and_incomplete_sharepoint(catalogue: Catalogue) -> None:
    scan = sample_scan("town", catalogue)
    inputs = load_inputs(sample_inputs_path("town"), catalogue)
    html = render_report(scan, lang="en", profile="opendesk", inputs=inputs)

    assert Counter(re.findall(r'<li data-gap="[^"]+" data-need="([^"]+)"', html)) == {
        "yes": 4,
        "no": 1,
        "unknown": 3,
    }
    sharepoint = readiness_row(html, "sharepoint")
    assert 'data-status="needs_work" data-incomplete' in sharepoint
    assert 'data-missing="sharepoint.workflows_in_use"' in sharepoint


def _rendered_coverage_counts(html: str, lang: str) -> Counter[str]:
    section = report_section(html, "moves")
    column = re.escape(load_locale(lang)["moves"]["replacement"])
    cells = re.findall(
        rf'<td role="cell" data-label="{column}" data-coverage-label="[^"]+">'
        r'\s*<span class="cov-cell">\s*'
        r'<span class="cov(?: cov-none)?">.*?</span>\s*<strong>([^<]+)</strong>',
        section,
        re.S,
    )
    assert len(cells) == section.count("<tr data-function=")
    return Counter(unescape(cell.strip()) for cell in cells)


@pytest.mark.parametrize("sample", ["town", "nonprofit"])
@pytest.mark.parametrize("lang", i18n.SUPPORTED_LANGUAGES)
@pytest.mark.parametrize("profile", ["opendesk", "nextcloud"])
def test_scope_statement_matches_the_replacements_and_gap_lists(
    catalogue: Catalogue, sample: str, lang: str, profile: str
) -> None:
    scan = sample_scan(sample, catalogue)
    inputs = load_inputs(sample_inputs_path(sample), catalogue)
    context, _ = report_module._prepare_report(scan, lang, profile, catalogue, inputs)
    scope = context.get("scope_statement")

    assert scope is not None
    mapping = context["mapping"]
    assert scope == report_module.scope_statement(mapping, context["statuses"], lang)
    assert scope.profile == mapping.label[lang] and scope.reviewed_on is None
    html = report_module._render_html(context)
    labels = load_locale(lang)["mapping_coverage"]
    assert _rendered_coverage_counts(html, lang) == {
        labels[coverage]: count for coverage, count in scope.by_coverage
    }
    assert sum(count for _, count in scope.by_coverage) == scope.total == len(mapping.functions)
    assert tuple(coverage for coverage, _ in scope.by_coverage) == tuple(
        key for key in COVERAGE_LADDER if key in dict(scope.by_coverage)
    )

    attention = report_section(html, "attention")
    gaps = re.findall(
        r'<li data-gap="([^"]+)" data-need="([^"]+)">\s*<strong id="([^"]+)">([^<]+)</strong>',
        attention,
    )
    assert len(gaps) == attention.count("<li data-gap=")
    assert scope.needed == tuple(
        (unescape(text), anchor) for _, need, anchor, text in gaps if need == "yes"
    )
    assert scope.unknown_need == sum(need == "unknown" for _, need, _, _ in gaps)
    assert all(html.count(f'id="{anchor}"') == 1 for _, anchor in scope.needed)

    if profile == "opendesk":
        assert scope.total == 22
        assert scope.by_coverage == (
            ("in_suite", 6),
            ("in_suite_with_limits", 8),
            ("transfer_undocumented", 3),
            ("not_available", 5),
        )
        if sample == "town":
            assert [anchor for _, anchor in scope.needed] == [
                "transfer-gap-device_management",
                "transfer-gap-windows_applications",
                "transfer-gap-automation_and_low_code",
                "transfer-gap-telephony",
            ]
            assert scope.unknown_need == 3
            assert [function for function, need, _, _ in gaps if need == "unknown"] == [
                "sharepoint_workflows",
                "vba_macros",
                "desktop_operating_system",
            ]
        else:
            assert scope.needed == ()
    else:
        assert ("open_source_community", 1) in scope.by_coverage


def test_generic_profile_has_no_scope_statement(catalogue: Catalogue) -> None:
    scan = sample_scan("town", catalogue)
    context, _ = report_module._prepare_report(scan, "en", "generic", catalogue, None)

    assert "scope_statement" in context and context["scope_statement"] is None
    assert report_module.scope_statement(context["mapping"], context["statuses"], "en") is None


@pytest.mark.parametrize("coverage", GAP_COVERAGE)
def test_marking_a_mapping_as_a_transfer_gap_adds_it_to_the_gap_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue: Catalogue, coverage: str
) -> None:
    need_finding = "directory.account_list_reviewed"
    scan = sample_scan("town", catalogue)
    scan = replace(scan, findings=tuple(item for item in scan.findings if item.id != need_finding))
    before, _ = report_module._prepare_report(scan, "en", "opendesk", catalogue, None)
    before_html = report_module._render_html(before)

    copied = tmp_path / "rules"
    copytree(Path(str(rules_dir())), copied)
    path = copied / "mappings" / "opendesk.yaml"
    data = parse_yaml(read_text(path), path.name)
    changed = next(row for row in data["functions"] if row["coverage"] == "in_suite")
    changed["coverage"] = coverage
    changed["need_finding"] = need_finding
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)

    context, _ = report_module._prepare_report(scan, "en", "opendesk", catalogue, None)
    html = report_module._render_html(context)
    section = report_section(html, "attention")
    entry = re.search(
        rf'<li data-gap="{changed["function"]}" data-need="unknown">.*?</li>', section, re.S
    )

    labels = load_locale("en")["mapping_coverage"]
    assert entry is not None
    assert f"<p>{labels[coverage]}</p>" in entry[0]
    assert 'data-reason="answer_not_provided"' in entry[0]

    original = before["scope_statement"]
    scope = context["scope_statement"]
    counts = dict(original.by_coverage)
    counts["in_suite"] -= 1
    counts[coverage] += 1
    assert dict(scope.by_coverage) == counts
    assert (scope.total, scope.needed, scope.unknown_need) == (
        original.total,
        original.needed,
        original.unknown_need + 1,
    )
    rendered_counts = _rendered_coverage_counts(before_html, "en")
    rendered_counts[labels["in_suite"]] -= 1
    rendered_counts[labels[coverage]] += 1
    assert (
        _rendered_coverage_counts(html, "en")
        == rendered_counts
        == {labels[code]: count for code, count in scope.by_coverage}
    )


def test_next_steps_and_open_evidence_follow_the_findings(
    catalogue: Catalogue, complete_evidence: dict[str, Finding], status_rules: StatusRuleSet
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
    path = unescape(report_section(html, "path"))
    rule = next(
        rule for rule in status_rules.workloads["telephony"].rules if rule.status == "blocker"
    )
    assert re.search(
        r'<dt><a href="#readiness-telephony" class="more">.*?</a></dt>\s*'
        r'<dd>\s*<ul class="path-actions">\s*'
        rf'<li data-step-kind="{rule.next_step.kind}">{re.escape(rule.next_step.text["en"])}</li>',
        path,
        re.S,
    )
    staying, moving = path.split('id="not-examined"')
    assert set(re.findall(r'data-step-kind="([^"]+)"', staying)) == {"clarify", "decide"}
    assert set(re.findall(r'data-step-kind="([^"]+)"', moving)) == {"replace"}
    assert re.search(
        rf'<li [^>]*data-unexamined-gap="{re.escape(mail_gap.id)}"[^>]*>'
        r'[^<]*<a href="#readiness-mail"[^>]*>',
        moving,
    )
    assert load_locale("en")["reason"]["needs_recipient_export"]["fix"] in moving
    for workload in re.findall(r'href="#readiness-([^"]+)"', path):
        assert 'data-status="ready"' not in readiness_row(html, workload)
    assert "%" not in path and "<ol" not in path and "pilot" not in path.casefold()


def test_next_steps_explain_the_empty_state(
    catalogue: Catalogue, complete_evidence: dict[str, Finding]
) -> None:
    sample = sample_scan("town", catalogue)
    scan = replace(
        sample,
        collectors=tuple(replace(item, status="ok", reason=None) for item in sample.collectors),
        findings=tuple(complete_evidence.values()),
        licences=None,
    )
    html = render_report(scan, lang="en")
    path = report_section(html, "path")
    strings = load_locale("en")["path"]["empty"]
    assert all(
        'data-status="ready"' in readiness_row(html, workload)
        for workload in catalogue.assessed_workload_ids
    )
    assert strings["unknown"] in path and strings["blocker"] in path
    assert "data-open-point" not in path and "data-step-kind" not in path


def test_summary_explains_empty_lists_with_complete_evidence(
    catalogue: Catalogue, complete_evidence: dict[str, Finding]
) -> None:
    sample = sample_scan("town", catalogue)
    scan = replace(
        sample,
        collectors=tuple(replace(item, status="ok", reason=None) for item in sample.collectors),
        findings=tuple(complete_evidence.values()),
        licences=None,
    )
    summary = unescape(report_section(render_report(scan, lang="en"), "summary"))
    blockers, open_part = summary.split('data-summary="unknown"', 1)
    strings = load_locale("en")

    assert strings["path"]["empty"]["blocker"] in blockers
    assert "a Blocker cannot be ruled out" not in blockers
    assert 'href="#status-blocker"' not in blockers
    assert strings["path"]["empty"]["unknown"] in open_part
    assert f'href="#not-examined">{strings["summary"]["not_examined"]}' in open_part
