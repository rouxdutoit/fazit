# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from importlib.resources import files
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from befund.catalogue import load_catalogue
from befund.cli import app
from befund.i18n import load_locale
from befund.rules import load_service_plans

NO_TELEPHONY = "confirmations: {telephony.in_use: false, telephony.replacement_available: false}"


@pytest.fixture
def town_scan() -> dict:
    source = files("befund").joinpath("demo", "town", "scan.json")
    return json.loads(source.read_text(encoding="utf-8"))


def _finding(scan: dict, finding_id: str) -> dict:
    return next(item for item in scan["findings"] if item["id"] == finding_id)


def _measure(
    scan: dict, finding_id: str, value: int | bool, collector: str, *, kind: str = "complete"
) -> dict:
    finding = _finding(scan, finding_id)
    finding.update(
        value=value,
        provenance="measured",
        collector=collector,
        source=f"sample.{collector}",
        collected_at=scan["generated_at"],
        coverage={"kind": kind},
        missing_reason=None,
    )
    return finding


def _report(tmp_path: Path, scan: dict, answers: str | None = None) -> Result:
    tmp_path.mkdir()
    source = tmp_path / "inventory.json"
    source.write_text(json.dumps(scan), encoding="utf-8")
    options = []
    if answers is not None:
        inputs = tmp_path / "answers.yaml"
        inputs.write_text(answers, encoding="utf-8")
        options = ["--inputs", str(inputs)]
    command = ["report", str(source), "--out", str(tmp_path / "out"), *options]
    return CliRunner().invoke(app, command)


def _html(result: Result) -> str:
    assert result.exit_code == 0 and not result.stderr, result.output
    return Path(result.stdout.strip()).read_text(encoding="utf-8")


def _readiness(html: str, workload: str) -> str:
    row = re.search(rf'<tr data-workload="{workload}".*?</tr>', html, re.S)
    assert row is not None
    return row[0]


def test_supplied_zero_preserves_a_skipped_observation(tmp_path: Path, town_scan: dict) -> None:
    finding_id = "integrations.application_count"
    _measure(town_scan, finding_id, 3, "directory")
    answers = f"provided_counts: {{{finding_id}: 0}}"

    checked = _html(_report(tmp_path / "checked", town_scan, answers))
    row = _readiness(checked, "integrations")
    assert 'data-status="needs_work"' in row
    assert "3 applications" in row and "0 applications" in row

    directory = next(item for item in town_scan["collectors"] if item["id"] == "directory")
    directory.update(status="skipped", reason="permission_denied")
    for finding in town_scan["findings"]:
        if finding["collector"] == "directory":
            finding.update(
                value=None, provenance="unknown", coverage=None, missing_reason="permission_denied"
            )
    skipped = _html(_report(tmp_path / "skipped", town_scan, answers))
    row = _readiness(skipped, "integrations")
    assert 'data-status="unknown" data-incomplete' in row
    assert f'data-missing="{finding_id}"' in row
    assert 'data-reason="permission_denied"' in row
    assert load_locale("en")["collector"]["directory"] in row
    assert "0 applications" in row
    assert 'data-path-status="ready" data-path-workload="integrations"' not in skipped


@pytest.mark.parametrize(
    ("collector_status", "reason_code"),
    [("skipped", "permission_denied"), ("partial", "not_in_export")],
)
@pytest.mark.parametrize(("answer", "status"), [(0, "unknown"), (3, "needs_work")])
def test_incomplete_bound_collector_is_reported_without_a_scan_finding(
    tmp_path: Path,
    town_scan: dict,
    collector_status: str,
    reason_code: str,
    answer: int,
    status: str,
) -> None:
    finding_id = "integrations.application_count"
    town_scan["findings"] = [
        finding
        for finding in town_scan["findings"]
        if finding["id"] != finding_id and finding["collector"] != "directory"
    ]
    directory = next(item for item in town_scan["collectors"] if item["id"] == "directory")
    directory.update(status=collector_status, reason=reason_code)

    html = _html(
        _report(
            tmp_path / "omitted-finding", town_scan, f"provided_counts: {{{finding_id}: {answer}}}"
        )
    )
    row = _readiness(html, "integrations")
    strings = load_locale("en")

    assert f'data-status="{status}" data-incomplete' in row
    assert f'data-missing="{finding_id}"' in row
    assert f'data-reason="{reason_code}"' in row
    assert strings["reason"][reason_code]["fix"] in row
    assert strings["collector"]["directory"] in row
    assert f"{answer} applications" in row
    assert 'data-path-status="ready" data-path-workload="integrations"' not in html


def test_shared_mailboxes_require_the_exchange_recipient_export(
    tmp_path: Path, town_scan: dict
) -> None:
    answers = "confirmations: {mail.other_systems_send_mail: false}"
    original = _html(_report(tmp_path / "missing", town_scan, answers))
    row = _readiness(original, "mail")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="needs_recipient_export"' in row

    finding_id = "mail.shared_mailbox_count"
    finding = _measure(town_scan, finding_id, 0, "mailbox_usage")
    wrong = _report(tmp_path / "usage", town_scan, answers)
    assert wrong.exit_code == 2 and not wrong.stdout
    assert len(wrong.stderr.splitlines()) == 1
    assert "inventory.json" in wrong.stderr and finding_id in wrong.stderr
    assert not (tmp_path / "usage" / "out").exists()

    recipients = next(
        item for item in town_scan["collectors"] if item["id"] == "exchange_recipients"
    )
    recipients.update(status="ok", reason=None)
    finding.update(collector="exchange_recipients")
    mismatched = _report(tmp_path / "mismatched", town_scan, answers)
    assert mismatched.exit_code == 2 and not mismatched.stdout
    assert "inventory.json" in mismatched.stderr and finding_id in mismatched.stderr

    finding.update(source="sample.exchange_recipients")
    verified = _html(_report(tmp_path / "recipient-export", town_scan, answers))
    assert 'data-status="ready"' in _readiness(verified, "mail")


@pytest.mark.parametrize("source", ["sample.mailbox_usage", "inputs_yaml"])
def test_licence_inventory_requires_a_source_bound_to_its_collector(
    tmp_path: Path, town_scan: dict, source: str
) -> None:
    town_scan["licences"].update(source=source, products=[])

    result = _report(tmp_path / "wrong-licence-source", town_scan, NO_TELEPHONY)

    assert result.exit_code == 2 and not result.stdout
    assert len(result.stderr.splitlines()) == 1
    assert "inventory.json" in result.stderr and "licences.source" in result.stderr
    assert not (tmp_path / "wrong-licence-source" / "out").exists()


def test_empty_licence_inventory_leaves_absence_unknown(tmp_path: Path, town_scan: dict) -> None:
    town_scan["licences"]["products"] = []
    answers = """
confirmations:
  licences.contract_terms_known: true
  telephony.in_use: false
  telephony.replacement_available: false
"""

    html = _html(_report(tmp_path / "empty-inventory", town_scan, answers))

    for workload, finding_id in (
        ("telephony", "telephony.licence_add_on_assigned"),
        ("licences", "licences.product_count"),
    ):
        row = _readiness(html, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert 'data-reason="licence_products_missing"' in row
        assert "No licence products were recorded." in row
        evidence = re.search(rf'<li data-evidence="{re.escape(finding_id)}">.*?</li>', row, re.S)
        assert evidence is not None
        assert 'data-provenance="unknown"' in evidence[0]
        assert 'data-provenance="measured"' not in evidence[0]
    assert "Licence products found: 0" not in html


@pytest.mark.parametrize("plan_list", ["empty", "omitted", "null"])
def test_assigned_product_without_plans_leaves_licence_evidence_unknown(
    tmp_path: Path, town_scan: dict, plan_list: str
) -> None:
    checked = _html(_report(tmp_path / "with-plans", town_scan, NO_TELEPHONY))
    assert 'data-status="blocker"' in _readiness(checked, "telephony")

    phone = next(
        item for item in town_scan["licences"]["products"] if item["sku_part_number"] == "MCOEV"
    )
    if plan_list == "omitted":
        del phone["service_plans"]
    else:
        phone["service_plans"] = [] if plan_list == "empty" else None
    html = _html(_report(tmp_path / "no-plans", town_scan, NO_TELEPHONY))
    row = _readiness(html, "telephony")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_plan_list_missing"' in row


def test_unclassified_phone_plan_leaves_add_on_assignment_unknown(
    tmp_path: Path, town_scan: dict
) -> None:
    phone = next(
        item for item in town_scan["licences"]["products"] if item["sku_part_number"] == "MCOEV"
    )
    assert phone["assigned"] == 12
    town_scan["licences"].update(
        products=[phone], coverage={"kind": "complete", "scanned": 1, "failed": 0, "total": 1}
    )
    baseline = _html(_report(tmp_path / "classified-phone", town_scan, NO_TELEPHONY))
    assert 'data-status="blocker"' in _readiness(baseline, "telephony")

    phone["service_plans"] = [
        {"name": "REVIEW_PLAN", "guid": "00000000-0000-4000-8000-000000000001"}
    ]
    html = _html(_report(tmp_path / "unclassified-phone", town_scan, NO_TELEPHONY))
    row = _readiness(html, "telephony")

    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_not_classified"' in row
    evidence = re.search(
        r'<li data-evidence="telephony\.licence_add_on_assigned">.*?</li>', row, re.S
    )
    assert evidence is not None
    assert 'data-provenance="unknown"' in evidence[0]
    assert not re.search(r"\b(?:No|Measured)\b", evidence[0])
    assert "Unclassified service plans in this product: 1." in html
    assert "update the service plan catalogue" in html
    assert "REVIEW_PLAN" not in html


def test_unlisted_plan_prevents_an_absence_conclusion_but_preserves_known_assignments(
    tmp_path: Path, town_scan: dict
) -> None:
    answers = """
confirmations:
  teams.chat_history_must_be_kept: false
  telephony.in_use: false
  telephony.replacement_available: false
"""
    baseline = _html(_report(tmp_path / "known-plans", town_scan, answers))
    assert 'data-status="ready"' in _readiness(baseline, "teams")

    suite = next(
        item for item in town_scan["licences"]["products"] if item["sku_part_number"] == "SPE_E3"
    )
    suite["service_plans"].append(
        {"name": "UNLISTED_PLAN", "guid": "0bcaffc1-5211-41e4-b81e-79a9d25b77e4"}
    )
    html = _html(_report(tmp_path / "unlisted-plan", town_scan, answers))
    assert "Unclassified service plans in this product: 1." in html
    row = _readiness(html, "teams")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_not_classified"' in row
    assert 'data-status="blocker"' in _readiness(html, "telephony")

    suite["assigned"] = 0
    html = _html(_report(tmp_path / "unassigned-plan", town_scan, answers))
    assert "Unclassified service plans in this product: 1." in html
    assert 'data-status="ready"' in _readiness(html, "teams")


@pytest.mark.parametrize("partial_by", ["coverage", "collector"])
def test_partial_licence_inventory_confirms_assignments_only(
    tmp_path: Path, town_scan: dict, partial_by: str
) -> None:
    answers = """
confirmations:
  telephony.replacement_available: false
  telephony.in_use: false
  power_platform.in_use: false
"""
    licences = town_scan["licences"]
    licences["products"] = [
        item for item in licences["products"] if item["sku_part_number"] != "PBI_PREMIUM_PER_USER"
    ]
    checked = _html(_report(tmp_path / "complete-licences", town_scan, answers))
    assert 'data-status="blocker"' in _readiness(checked, "telephony")
    assert 'data-status="ready"' in _readiness(checked, "power_platform")

    if partial_by == "coverage":
        licences["coverage"] = {"kind": "partial", "scanned": 2, "failed": 1, "total": 3}
        reason = "coverage_partial"
    else:
        collector = next(item for item in town_scan["collectors"] if item["id"] == "licences")
        collector.update(status="partial", reason="not_in_export")
        reason = "not_in_export"
    html = _html(_report(tmp_path / "partial-licences", town_scan, answers))
    row = _readiness(html, "telephony")
    assert 'data-status="blocker" data-incomplete' in row
    assert 'data-reason="coverage_partial"' in row
    if partial_by == "coverage":
        assert "2 of 3 scanned" in row
    row = _readiness(html, "power_platform")
    assert 'data-status="unknown" data-incomplete' in row
    assert f'data-reason="{reason}"' in row
    assert 'data-provenance="unknown"' in row


def test_eea_suite_with_published_punctuation_is_classified(
    tmp_path: Path, town_scan: dict
) -> None:
    guid = "c2fe850d-fbbb-4858-b67d-bd0c6e746da3"
    plans = [plan for plan in load_service_plans(load_catalogue()) if plan.sku_guid == guid]
    assert any(plan.name == "EXCHANGE_S_ENTERPRISE" and plan.signal == "bundled" for plan in plans)
    assert any(plan.signal == "no_workload" for plan in plans)
    product = town_scan["licences"]["products"][0]
    product.update(
        sku_part_number="O365_w/o\u00a0Teams\u00a0Bundle_M3",
        sku_guid=guid,
        service_plans=[{"name": plan.name, "guid": plan.guid} for plan in plans],
    )
    html = _html(_report(tmp_path / "eea-suite", town_scan))
    assert "Unclassified service plans" not in html
    assert re.search(
        r"Mail · Included in the product\s*<small>[^\n]*<code>EXCHANGE_S_ENTERPRISE</code>",
        html,
    )

    product["sku_guid"] = "0bcaffc1-5211-41e4-b81e-79a9d25b77e4"
    invalid = _report(tmp_path / "wrong-sku-guid", town_scan)
    assert invalid.exit_code == 2 and not invalid.stdout
    assert "licences.products[0].sku_part_number" in invalid.stderr


@pytest.mark.parametrize(
    ("measured", "provided", "coverage", "status"),
    [
        (True, True, "complete", "blocker"),
        (False, False, "complete", "ready"),
        (False, True, "complete", "blocker"),
        (True, False, "complete", "unknown"),
        (True, False, "partial", "unknown"),
    ],
)
def test_telephony_rule_reads_the_provided_confirmation(
    tmp_path: Path, town_scan: dict, measured: bool, provided: bool, coverage: str, status: str
) -> None:
    town_scan["licences"]["products"] = [
        item for item in town_scan["licences"]["products"] if item["sku_part_number"] != "MCOEV"
    ]
    answers = f"""
confirmations:
  telephony.in_use: {str(provided).lower()}
  telephony.replacement_available: false
"""
    baseline = _html(_report(tmp_path / "confirmation-only", town_scan, answers))
    expected = "blocker" if provided else "ready"
    assert f'data-status="{expected}"' in _readiness(baseline, "telephony")

    town_scan["collectors"].append(
        {"id": "telephony", "status": "ok", "reason": None, "permissions_used": []}
    )
    _measure(town_scan, "telephony.in_use", measured, "telephony", kind=coverage)
    html = _html(_report(tmp_path / "both-observations", town_scan, answers))
    row = _readiness(html, "telephony")
    assert f'data-status="{status}"' in row
    evidence = re.search(r'<li data-evidence="telephony.in_use">.*?</li>', row, re.S)
    assert evidence is not None
    observations = [
        ("measured", "Yes" if measured else "No"),
        ("provided", "Yes" if provided else "No"),
    ]
    if coverage == "partial":
        observations.reverse()
    assert (
        re.findall(r'data-provenance="(measured|provided)">\s*(Yes|No)', evidence[0])
        == observations
    )
    assert ('data-reason="confirmation_conflict"' in row) is (measured != provided)
    assert ("data-incomplete" in row) is (measured != provided)


@pytest.mark.parametrize(
    ("workload", "finding_id", "collector", "measured", "provided", "lower_bound", "answer"),
    [
        (
            "integrations",
            "integrations.application_count",
            "directory",
            4,
            1,
            "At least 4 applications",
            "1 application",
        ),
        (
            "office_files",
            "office_files.kind.macro",
            "office_files",
            500,
            271,
            "At least 500 files",
            "271 files",
        ),
    ],
)
def test_measured_lower_bound_takes_precedence_over_a_smaller_provided_total(
    tmp_path: Path,
    town_scan: dict,
    workload: str,
    finding_id: str,
    collector: str,
    measured: int,
    provided: int,
    lower_bound: str,
    answer: str,
) -> None:
    if collector == "office_files":
        town_scan["collectors"].append(
            {"id": collector, "status": "ok", "reason": None, "permissions_used": []}
        )
    _measure(town_scan, finding_id, measured, collector, kind="partial")
    html = _html(
        _report(tmp_path / "bounds", town_scan, f"provided_counts: {{{finding_id}: {provided}}}")
    )

    row = _readiness(html, workload)
    assert 'data-status="needs_work" data-incomplete' in row
    evidence = re.search(rf'<li data-evidence="{re.escape(finding_id)}">.*?</li>', row, re.S)
    assert evidence is not None
    assert evidence[0].index(lower_bound) < evidence[0].index(answer)
    assert load_locale("en")["readiness"]["conflict"] in evidence[0]


def test_measured_storage_lower_bound_rounds_down(tmp_path: Path, town_scan: dict) -> None:
    _measure(town_scan, "mail.storage_bytes", 1250, "mailbox_usage", kind="partial")
    html = _html(_report(tmp_path / "storage", town_scan))

    assert "At least 1.2 kB" in html
    assert "At least 1.3 kB" not in html


@pytest.mark.parametrize(
    ("software", "status", "desktop_need", "applications_need"),
    [
        ("null", "unknown", "unknown", "unknown"),
        ("[]", "ready", "no", "no"),
        ("[{name: Records, vendor_has_web_version: true}]", "needs_work", "no", "yes"),
        ("[{name: Records}]", "needs_work", "unknown", "yes"),
        (
            "[{name: Records, vendor_has_web_version: false}, {name: Permits}]",
            "needs_work",
            "yes",
            "yes",
        ),
    ],
)
def test_windows_dependency_is_scoped_to_the_desktop_move(
    tmp_path: Path,
    town_scan: dict,
    software: str,
    status: str,
    desktop_need: str,
    applications_need: str,
) -> None:
    html = _html(_report(tmp_path / "desktop", town_scan, f"windows_only_software: {software}"))
    row = _readiness(html, "windows_software")

    assert f'data-status="{status}"' in row
    assert f'data-gap="desktop_operating_system" data-need="{desktop_need}"' in html
    assert f'data-gap="windows_applications" data-need="{applications_need}"' in html
    if desktop_need == "yes":
        assert "blocks a move away from Windows desktops" in row
        assert "Microsoft 365 exit" in row
        assert 'data-status="needs_work" data-incomplete' in row
        assert "At least 1 application" in row and 'data-reason="answer_not_provided"' in row


@pytest.mark.parametrize(
    ("lang", "title"),
    [("en", "Direct transfer unverified"), ("de", "Nicht direkt übertragbar")],
)
def test_transfer_gap_heading_describes_the_scope_of_evidence(
    tmp_path: Path, town_scan: dict, lang: str, title: str
) -> None:
    html = _html(_report(tmp_path / "transfer", town_scan, f"language: {lang}"))
    section = re.search(r'<div data-subsection="cannot-be-moved">.*?</div>', html, re.S)
    assert section is not None
    assert f"<h3>{title}</h3>" in section[0]
    assert load_locale(lang)["attention"]["gap_scope"] in section[0]
