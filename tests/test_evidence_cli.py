# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from importlib.resources import files
from pathlib import Path

import pytest
from helpers import readiness_row, runner
from typer.testing import Result

from fazit.catalogue import load_catalogue
from fazit.cli import app
from fazit.i18n import load_locale
from fazit.licences import load_service_plans

NO_TELEPHONY = "confirmations: {telephony.in_use: false, telephony.replacement_available: false}"


@pytest.fixture
def town_scan() -> dict:
    source = files("fazit").joinpath("demo", "town", "scan.json")
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
    return runner.invoke(app, command)


def _html(result: Result) -> str:
    assert result.exit_code == 0 and not result.stderr, result.output
    return Path(result.stdout.strip()).read_text(encoding="utf-8")


def _reject_scan(tmp_path: Path, scan: dict, field: str, answers: str | None = None) -> str:
    result = _report(tmp_path, scan, answers)
    assert result.exit_code == 2 and not result.stdout, result.output
    assert len(result.stderr.splitlines()) == 1
    assert "inventory.json" in result.stderr and field in result.stderr
    assert not (tmp_path / "out").exists()
    return result.stderr


@pytest.mark.parametrize("reason", ["collector_skipped", "permission_denied"])
@pytest.mark.parametrize("initial_assignments", [0, 1])
def test_skipping_directory_keeps_unreconciled_licence_absence_unknown(
    tmp_path: Path, reason: str, initial_assignments: int
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit")
    scan = json.loads(sample.joinpath("scan.json").read_text(encoding="utf-8"))
    answers = sample.joinpath("inputs.yaml").read_text(encoding="utf-8")
    answers = answers.replace(
        "licences.contract_terms_known: false", "licences.contract_terms_known: true"
    )
    (product,) = scan["licences"]["products"]
    assigned = product["assigned"]
    product["assigned"] = initial_assignments
    before = _html(_report(tmp_path / "directory-present", scan, answers))

    directory = next(row for row in scan["collectors"] if row["id"] == "directory")
    directory.update(status="skipped", reason=reason)
    for finding in scan["findings"]:
        if finding["collector"] == "directory":
            finding.update(value=None, provenance="unknown", coverage=None, missing_reason=reason)
    after = _html(_report(tmp_path / "directory-skipped", scan, answers))

    for workload in ("power_platform", "telephony", "identity_access", "security_compliance"):
        assert 'data-status="unknown"' in readiness_row(before, workload)
        row = readiness_row(after, workload)
        assert 'data-status="unknown"' in row, workload
        assert f'data-reason="{reason}"' in row
    for html, code in (
        (before, "licence_assignments_conflict"),
        (after, "licence_directory_unverified"),
    ):
        row = readiness_row(html, "licences")
        assert 'data-status="unknown"' in row and f'data-reason="{code}"' in row
    product["assigned"] = assigned
    positive = _html(_report(tmp_path / "directory-skipped-with-assignments", scan, answers))
    assert re.search(
        r'<li data-evidence="small_apps\.licence_bundled_assigned">\s*<strong>[^<]+</strong>\s*'
        r'<div data-provenance="measured">\s*Yes',
        readiness_row(positive, "small_apps"),
    )


@pytest.mark.parametrize("source_kind", ["live", "import"])
@pytest.mark.parametrize("sample_evidence", ["findings", "licences"])
def test_report_rejects_simulated_evidence_in_a_non_sample_scan(
    tmp_path: Path, town_scan: dict, source_kind: str, sample_evidence: str
) -> None:
    town_scan["source_kind"] = source_kind
    if sample_evidence == "licences":
        town_scan["findings"] = []
    else:
        town_scan["licences"] = None

    _reject_scan(tmp_path / "mislabeled", town_scan, "source_kind")


@pytest.mark.parametrize(
    ("status", "reason"), [("ok", "permission_denied"), ("partial", None), ("skipped", None)]
)
def test_report_rejects_a_collector_reason_that_disagrees_with_status(
    tmp_path: Path, town_scan: dict, status: str, reason: str | None
) -> None:
    index = next(i for i, row in enumerate(town_scan["collectors"]) if row["id"] == "teams_usage")
    town_scan["collectors"][index].update(status=status, reason=reason)

    _reject_scan(tmp_path / "collector-reason", town_scan, f"collectors[{index}].reason")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("period", "2030-12-01/2030-12-31"),
        ("collected_at", "2026-11-03"),
        ("collected_at", "2026-11-02T08:30:00-01:00"),
        ("collected_at", "2026-11-02T09:00:00.0000001Z"),
    ],
)
def test_report_rejects_impossible_finding_dates(
    tmp_path: Path, town_scan: dict, field: str, value: str
) -> None:
    finding = _finding(town_scan, "teams.teams_with_guests_count")
    finding[field] = value
    index = town_scan["findings"].index(finding)

    _reject_scan(tmp_path / "impossible-date", town_scan, f"findings[{index}].{field}")


@pytest.mark.parametrize("stamp", ["2026-11-02", "2026-11-02T10:00:00+01:00"])
def test_report_accepts_same_day_and_equal_offset_timestamps(
    tmp_path: Path, town_scan: dict, stamp: str
) -> None:
    _finding(town_scan, "teams.teams_with_guests_count")["collected_at"] = stamp

    _html(_report(tmp_path / "possible-date", town_scan))


def test_report_rejects_a_licence_collection_later_than_the_scan(
    tmp_path: Path, town_scan: dict
) -> None:
    town_scan["licences"]["collected_at"] = "2030-12-31"

    _reject_scan(tmp_path / "impossible-licence-date", town_scan, "licences.collected_at")


def test_supplied_zero_preserves_a_skipped_observation(tmp_path: Path, town_scan: dict) -> None:
    finding_id = "integrations.application_count"
    _measure(town_scan, finding_id, 3, "directory", kind="partial")
    answers = f"provided_counts: {{{finding_id}: 0}}"

    checked = _html(_report(tmp_path / "checked", town_scan, answers))
    row = readiness_row(checked, "integrations")
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
    row = readiness_row(skipped, "integrations")
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
    row = readiness_row(html, "integrations")
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
    _finding(town_scan, "mail.other_systems_send_mail")["value"] = False
    answers = "confirmations: {mail.other_systems_send_mail: false}"
    original = _html(_report(tmp_path / "missing", town_scan, answers))
    row = readiness_row(original, "mail")
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
    assert 'data-status="ready"' in readiness_row(verified, "mail")


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


@pytest.mark.parametrize(
    ("coverage", "directory_value", "status", "reason"),
    [
        ("complete", 0, "ready", None),
        ("complete", None, "unknown", "licence_directory_unverified"),
        ("partial", 0, "unknown", "licence_products_missing"),
        ("partial", 85, "unknown", "licence_products_missing"),
        ("unknown", 0, "unknown", "licence_products_missing"),
    ],
)
def test_empty_licence_inventory_requires_completed_coverage(
    tmp_path: Path,
    town_scan: dict,
    coverage: str,
    directory_value: int | None,
    status: str,
    reason: str | None,
) -> None:
    accounts = _finding(town_scan, "directory.licensed_user_count")
    if directory_value is None:
        town_scan["findings"].remove(accounts)
    else:
        accounts["value"] = directory_value
    town_scan["licences"].update(
        products=[], coverage={"kind": coverage, "scanned": 0, "failed": 0, "total": 0}
    )
    answers = """
confirmations:
  licences.contract_terms_known: true
  telephony.in_use: false
  telephony.replacement_available: false
"""

    html = _html(_report(tmp_path / "empty-inventory", town_scan, answers))

    row = readiness_row(html, "licences")
    assert f'data-status="{status}"' in row
    evidence = re.search(r'<li data-evidence="licences\.product_count">.*?</li>', row, re.S)
    assert evidence is not None
    provenance = "measured" if coverage == "complete" else "unknown"
    assert f'data-provenance="{provenance}"' in evidence[0]
    assert ("Licence products found: 0" in html) is (coverage == "complete")
    if reason:
        assert "data-incomplete" in row and f'data-reason="{reason}"' in row
    else:
        assert "data-incomplete" not in row and "0 of 0 scanned" in evidence[0]
    telephony = readiness_row(html, "telephony")
    assert f'data-status="{status}"' in telephony
    if coverage != "complete":
        assert 'data-reason="licence_products_missing"' in telephony
        assert "No licence products were recorded." in row
        assert re.search(
            r'<li data-evidence="telephony\.licence_add_on_assigned">\s*<strong>[^<]+</strong>\s*'
            r'<div data-provenance="unknown">',
            telephony,
        )


def test_complete_licence_inventory_rejects_a_missing_product(
    tmp_path: Path, town_scan: dict
) -> None:
    licences = town_scan["licences"]
    licences["coverage"] = {"kind": "complete", "scanned": 3, "failed": 0, "total": 3}
    baseline = _html(_report(tmp_path / "all-products", town_scan, NO_TELEPHONY))
    assert 'data-status="needs_work"' in readiness_row(baseline, "telephony")

    licences["products"] = [
        item for item in licences["products"] if item["sku_part_number"] != "MCOEV"
    ]
    assert len(licences["products"]) == 2
    incomplete = tmp_path / "missing-product"
    result = _report(incomplete, town_scan, NO_TELEPHONY)

    assert result.exit_code == 2 and not result.stdout, result.output
    assert len(result.stderr.splitlines()) == 1
    assert "inventory.json" in result.stderr and "licences.coverage" in result.stderr
    assert not (incomplete / "out").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sku_part_number", "MCOEV"),
        ("sku_part_number", "UNREGISTERED_PART"),
        ("sku_part_number", None),
        ("sku_guid", "00000000-0000-4000-8000-000000000001"),
        ("sku_guid", None),
    ],
)
def test_report_rejects_conflicting_registered_sku_identifiers(
    tmp_path: Path, town_scan: dict, field: str, value: str | None
) -> None:
    suite = town_scan["licences"]["products"][0]
    assert suite["sku_part_number"] == "SPE_E3"
    suite["assigned"] = 0
    suite["service_plans"] = [
        plan for plan in suite["service_plans"] if plan["name"] != "EXCHANGE_S_ENTERPRISE"
    ]
    suite[field] = value
    town_scan["licences"].update(
        products=[suite], coverage={"kind": "complete", "scanned": 1, "failed": 0, "total": 1}
    )

    error = _reject_scan(tmp_path / "sku-mismatch", town_scan, f"licences.products[0].{field}")
    if value is not None:
        assert value not in error


@pytest.mark.parametrize(
    "identity",
    [
        {"sku_part_number": None, "sku_guid": None},
        {"sku_part_number": "UNREGISTERED_PART"},
        {"sku_guid": "00000000-0000-4000-8000-000000000001"},
        {},
    ],
)
def test_only_assigned_unidentified_products_leave_licence_signals_unknown(
    tmp_path: Path, town_scan: dict, identity: dict[str, str | None]
) -> None:
    products = town_scan["licences"]["products"]
    assert products[1]["sku_part_number"] == "MCOEV"
    products[1] = {**identity, "purchased": 0, "assigned": 0, "service_plans": []}
    html = _html(_report(tmp_path / "unassigned", town_scan, NO_TELEPHONY))
    row = readiness_row(html, "telephony")
    assert 'data-status="ready"' in row and 'data-provenance="measured"' in row

    products[1].update(purchased=12, assigned=12)
    html = _html(_report(tmp_path / "assigned", town_scan, NO_TELEPHONY))
    row = readiness_row(html, "telephony")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-provenance="unknown"' in row
    assert 'data-reason="licence_plan_list_missing"' in row
    assert 'data-status="needs_work"' in readiness_row(html, "power_platform")


@pytest.mark.parametrize("empty_inventory", [False, True])
def test_licensed_accounts_make_zero_assignments_inconclusive(
    tmp_path: Path, town_scan: dict, empty_inventory: bool
) -> None:
    licences = town_scan["licences"]
    assert _finding(town_scan, "directory.licensed_user_count")["value"] == 85
    for product in licences["products"]:
        product["assigned"] = 0
    if empty_inventory:
        licences.update(
            products=[], coverage={"kind": "complete", "scanned": 0, "failed": 0, "total": 0}
        )

    answers = """
confirmations:
  licences.contract_terms_known: true
  telephony.in_use: false
"""
    html = _html(_report(tmp_path / "contradictory-assignments", town_scan, answers))
    row = readiness_row(html, "telephony")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_assignments_conflict"' in row
    assert "Licence assignments contradict licensed accounts." in row
    for workload in load_catalogue().workload_ids:
        assert f'data-unexamined-finding="{workload}.licence_add_on_assigned"' in html
    assert f"Licence products found: {len(licences['products'])}" in html
    row = readiness_row(html, "licences")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_assignments_conflict"' in row
    pilots = re.search(r'<ul data-path-status="ready".*?</ul>', html, re.S)
    assert pilots is None or 'data-path-workload="licences"' not in pilots[0]


def test_fewer_assigned_seats_than_licensed_people_withholds_dependent_pilots(
    tmp_path: Path,
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit")
    scan = json.loads(sample.joinpath("scan.json").read_text(encoding="utf-8"))
    answers = sample.joinpath("inputs.yaml").read_text(encoding="utf-8")
    (product,) = scan["licences"]["products"]
    accounts = _finding(scan, "directory.licensed_user_count")
    assert accounts["value"] == 20
    accounts["collected_at"] = "2026-11-05T11:00:00+01:00"
    product["assigned"] = 1

    html = _html(_report(tmp_path / "underassigned", scan, answers))
    pilots = re.search(r'<ul data-path-status="ready".*?</ul>', html, re.S)
    for workload in ("power_platform", "telephony", "identity_access", "security_compliance"):
        row = readiness_row(html, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert 'data-reason="licence_assignments_conflict"' in row
        assert pilots is None or f'data-path-workload="{workload}"' not in pilots[0]
    assert 'data-reason="licence_assignments_conflict"' in readiness_row(html, "licences")
    assert re.search(
        r'<li data-evidence="small_apps\.licence_bundled_assigned">\s*<strong>[^<]+</strong>\s*'
        r'<div data-provenance="measured">\s*Yes',
        readiness_row(html, "small_apps"),
    )
    accounts["collected_at"] = "2026-11-05T09:59:59Z"
    different_time = _html(_report(tmp_path / "different-directory-date", scan, answers))
    assert 'data-reason="licence_assignments_conflict"' not in different_time


@pytest.mark.parametrize("parent_kind", ["complete", "partial", "unknown"])
def test_report_rejects_coverage_total_contradicting_team_count(
    tmp_path: Path, town_scan: dict, parent_kind: str
) -> None:
    parent = _finding(town_scan, "teams.team_count")
    assert parent["value"] == 31
    parent["coverage"] = {"kind": parent_kind}
    guest_count = _finding(town_scan, "teams.teams_with_guests_count")
    guest_count["coverage"] = {"kind": "complete", "scanned": 0, "failed": 0, "total": 0}
    town_scan["findings"].reverse()
    index = town_scan["findings"].index(guest_count)

    _reject_scan(tmp_path / "coverage-total", town_scan, f"findings[{index}].coverage.total")

    total = 31 if parent_kind == "complete" else 32
    guest_count["coverage"].update(scanned=total, total=total)
    _html(_report(tmp_path / "consistent-total", town_scan))


def test_report_rejects_a_subset_above_its_population_for_the_same_period(
    tmp_path: Path, town_scan: dict
) -> None:
    guests = _finding(town_scan, "teams.teams_with_guests_count")
    guests["value"] = 40
    index = town_scan["findings"].index(guests)

    _reject_scan(tmp_path / "impossible-subset", town_scan, f"findings[{index}].value")

    guests["period"] = "2026-10-01/2026-10-15"
    _html(_report(tmp_path / "different-period", town_scan))
    guests["coverage"] = {"kind": "partial", "scanned": 31, "total": 50}
    _reject_scan(tmp_path / "outside-own-scope", town_scan, f"findings[{index}].value")


@pytest.mark.parametrize(
    ("parent_stamp", "subset_stamp"),
    [
        ("2026-11-02T09:00Z", "2026-11-02T10:00+01:00"),
        ("2026-11-02T08:59:59.9999999Z", "2026-11-02T09:59:59.99999990+01:00"),
    ],
)
def test_report_rejects_a_subset_above_its_population_at_the_same_instant(
    tmp_path: Path, town_scan: dict, parent_stamp: str, subset_stamp: str
) -> None:
    _finding(town_scan, "teams.team_count").update(period=None, collected_at=parent_stamp)
    guests = _finding(town_scan, "teams.teams_with_guests_count")
    guests.update(value=40, period=None, collected_at=subset_stamp)
    index = town_scan["findings"].index(guests)

    _reject_scan(tmp_path / "same-instant", town_scan, f"findings[{index}].value")

    guests["collected_at"] = "2026-11-02T08:59:59.9999998Z"
    _html(_report(tmp_path / "different-instant", town_scan))


@pytest.mark.parametrize(
    ("coverage", "field"),
    [
        ({"kind": "complete", "scanned": 1, "failed": 0, "total": 1}, "coverage"),
        ({"kind": "partial", "scanned": 1, "failed": 0, "total": 4}, "coverage.scanned"),
        ({"kind": "unknown", "total": 1}, "coverage.total"),
    ],
)
def test_report_rejects_products_above_licence_coverage(
    tmp_path: Path, town_scan: dict, coverage: dict, field: str
) -> None:
    town_scan["licences"]["coverage"] = coverage

    _reject_scan(tmp_path / "too-many-products", town_scan, f"licences.{field}")


@pytest.mark.parametrize(
    ("sku", "removed", "assigned", "baseline_status"),
    [
        ("BUSINESS_VOICE_DIRECTROUTING", "MCOEV", 12, "needs_work"),
        ("SPE_E3", "EXCHANGE_S_ENTERPRISE", 85, "ready"),
        ("SPE_E3", "EXCHANGE_S_ENTERPRISE", 0, "ready"),
    ],
)
def test_missing_roster_plan_leaves_add_on_absence_unknown(
    tmp_path: Path, town_scan: dict, sku: str, removed: str, assigned: int, baseline_status: str
) -> None:
    roster = [plan for plan in load_service_plans(load_catalogue()) if plan.sku_part_number == sku]
    product = {
        "sku_part_number": sku,
        "sku_guid": roster[0].sku_guid,
        "purchased": assigned,
        "assigned": assigned,
        "service_plans": [{"name": plan.name, "guid": plan.guid} for plan in roster],
    }
    town_scan["licences"].update(
        products=[product], coverage={"kind": "complete", "scanned": 1, "failed": 0, "total": 1}
    )
    _finding(town_scan, "directory.licensed_user_count")["value"] = assigned
    baseline = _html(_report(tmp_path / "complete-roster", town_scan, NO_TELEPHONY))
    assert f'data-status="{baseline_status}"' in readiness_row(baseline, "telephony")

    service_plans = product["service_plans"]
    (missing,) = [plan for plan in service_plans if plan["name"] == removed]
    service_plans.remove(missing)
    html = _html(_report(tmp_path / "incomplete-roster", town_scan, NO_TELEPHONY))
    row = readiness_row(html, "telephony")

    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_plan_list_incomplete"' in row
    assert "Plan list incomplete for a known product." in row
    evidence = re.search(
        r'<li data-evidence="telephony\.licence_add_on_assigned">.*?</li>', row, re.S
    )
    assert evidence is not None
    assert 'data-provenance="unknown"' in evidence[0]
    assert not re.search(r"\b(?:No|Measured)\b", evidence[0])


@pytest.mark.parametrize("plan_list", ["empty", "omitted", "null"])
def test_assigned_product_without_plans_leaves_licence_evidence_unknown(
    tmp_path: Path, town_scan: dict, plan_list: str
) -> None:
    checked = _html(_report(tmp_path / "with-plans", town_scan, NO_TELEPHONY))
    assert 'data-status="needs_work"' in readiness_row(checked, "telephony")

    phone = next(
        item for item in town_scan["licences"]["products"] if item["sku_part_number"] == "MCOEV"
    )
    if plan_list == "omitted":
        del phone["service_plans"]
    else:
        phone["service_plans"] = [] if plan_list == "empty" else None
    html = _html(_report(tmp_path / "no-plans", town_scan, NO_TELEPHONY))
    row = readiness_row(html, "telephony")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_plan_list_incomplete"' in row
    assert 'data-reason="licence_plan_list_missing"' in html


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
    _finding(town_scan, "directory.licensed_user_count")["value"] = 12
    baseline = _html(_report(tmp_path / "classified-phone", town_scan, NO_TELEPHONY))
    assert 'data-status="needs_work"' in readiness_row(baseline, "telephony")

    phone["service_plans"] = [
        {"name": "REVIEW_PLAN", "guid": "00000000-0000-4000-8000-000000000001"}
    ]
    html = _html(_report(tmp_path / "unclassified-phone", town_scan, NO_TELEPHONY))
    row = readiness_row(html, "telephony")

    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_plan_list_incomplete"' in row
    assert 'data-reason="licence_not_classified"' in html
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
    assert 'data-status="ready"' in readiness_row(baseline, "teams")

    suite = next(
        item for item in town_scan["licences"]["products"] if item["sku_part_number"] == "SPE_E3"
    )
    suite["service_plans"].append(
        {"name": "UNLISTED_PLAN", "guid": "0bcaffc1-5211-41e4-b81e-79a9d25b77e4"}
    )
    html = _html(_report(tmp_path / "unlisted-plan", town_scan, answers))
    assert "Unclassified service plans in this product: 1." in html
    row = readiness_row(html, "teams")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_not_classified"' in row
    assert 'data-status="needs_work"' in readiness_row(html, "telephony")

    suite["assigned"] = 0
    _finding(town_scan, "directory.licensed_user_count")["value"] = 12
    html = _html(_report(tmp_path / "unassigned-plan", town_scan, answers))
    assert "Unclassified service plans in this product: 1." in html
    assert 'data-status="ready"' in readiness_row(html, "teams")


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
    licences["coverage"] = {"kind": "complete", "scanned": 2, "failed": 0, "total": 2}
    checked = _html(_report(tmp_path / "complete-licences", town_scan, answers))
    assert 'data-status="needs_work"' in readiness_row(checked, "telephony")
    assert 'data-status="ready"' in readiness_row(checked, "power_platform")

    if partial_by == "coverage":
        licences["coverage"] = {"kind": "partial", "scanned": 2, "failed": 1, "total": 3}
        reason = "coverage_partial"
    else:
        collector = next(item for item in town_scan["collectors"] if item["id"] == "licences")
        collector.update(status="partial", reason="not_in_export")
        reason = "not_in_export"
    html = _html(_report(tmp_path / "partial-licences", town_scan, answers))
    row = readiness_row(html, "telephony")
    assert 'data-status="needs_work" data-incomplete' in row
    assert "Review whether the assigned Teams Phone licences are still needed" in row
    assert 'data-reason="coverage_partial"' in row
    if partial_by == "coverage":
        assert "2 of 3 scanned" in row
    row = readiness_row(html, "power_platform")
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
        (False, True, "complete", "unknown"),
        (True, False, "complete", "unknown"),
        (False, True, "partial", "blocker"),
        (True, False, "partial", "unknown"),
    ],
)
def test_telephony_distinguishes_partial_absence_from_conflicting_evidence(
    tmp_path: Path, town_scan: dict, measured: bool, provided: bool, coverage: str, status: str
) -> None:
    town_scan["licences"]["products"] = [
        item for item in town_scan["licences"]["products"] if item["sku_part_number"] != "MCOEV"
    ]
    town_scan["licences"]["coverage"] = {"kind": "complete", "scanned": 2, "failed": 0, "total": 2}
    answers = f"""
confirmations:
  telephony.in_use: {str(provided).lower()}
  telephony.replacement_available: false
"""
    baseline = _html(_report(tmp_path / "confirmation-only", town_scan, answers))
    expected = "blocker" if provided else "ready"
    assert f'data-status="{expected}"' in readiness_row(baseline, "telephony")

    town_scan["collectors"].append(
        {"id": "telephony", "status": "ok", "reason": None, "permissions_used": []}
    )
    finding = _measure(town_scan, "telephony.in_use", measured, "telephony", kind=coverage)
    if coverage == "partial":
        finding["coverage"].update(scanned=1, failed=0, total=85)
    html = _html(_report(tmp_path / "both-observations", town_scan, answers))
    row = readiness_row(html, "telephony")
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
    disputed = measured != provided and (coverage == "complete" or measured)
    assert ('data-reason="confirmation_conflict"' in row) is disputed
    assert ("data-incomplete" in row) is disputed
    if coverage == "partial":
        assert "1 of 85 scanned" in row
        need = "unknown" if disputed else "yes"
        assert f'data-gap="telephony" data-need="{need}"' in html


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

    row = readiness_row(html, workload)
    assert 'data-status="needs_work" data-incomplete' in row
    evidence = re.search(rf'<li data-evidence="{re.escape(finding_id)}">.*?</li>', row, re.S)
    assert evidence is not None
    assert evidence[0].index(lower_bound) < evidence[0].index(answer)
    assert load_locale("en")["readiness"]["conflict"] in evidence[0]


@pytest.mark.parametrize("kind", ["complete", "partial", "unknown"])
def test_measured_positive_count_cannot_be_overridden_by_zero(
    tmp_path: Path, town_scan: dict, kind: str
) -> None:
    finding_id = "integrations.application_count"
    finding = _measure(town_scan, finding_id, 3, "directory", kind=kind)
    finding["coverage"].update(scanned=6 if kind == "complete" else 3, failed=0, total=6)
    answers = f'as_of: "2026-11-02"\nprovided_counts: {{{finding_id}: 0}}'

    html = _html(_report(tmp_path / "conflicting-counts", town_scan, answers))
    row = readiness_row(html, "integrations")
    status = "unknown" if kind == "complete" else "needs_work"
    assert f'data-status="{status}" data-incomplete' in row
    strings = load_locale("en")
    conflict = (
        strings["reason"]["confirmation_conflict"]["label"]
        if kind == "complete"
        else strings["readiness"]["conflict"]
    )
    assert conflict in row
    bounds = "" if kind == "complete" else "At least "
    assert re.findall(r'data-provenance="(?:measured|provided)">\s*([^\n]+ applications)', row) == [
        f"{bounds}3 applications",
        "0 applications",
    ]
    assert 'data-path-status="ready" data-path-workload="integrations"' not in html

    scan_only = readiness_row(_html(_report(tmp_path / "scan-only", town_scan)), "integrations")
    assert 'data-status="needs_work"' in scan_only
    assert ("data-incomplete" in scan_only) is (kind != "complete")


def test_measured_storage_lower_bound_rounds_down(tmp_path: Path, town_scan: dict) -> None:
    _measure(town_scan, "mail.storage_bytes", 1250, "mailbox_usage", kind="partial")
    html = _html(_report(tmp_path / "storage", town_scan))

    assert "At least 1.2 kB" in html
    assert "At least 1.3 kB" not in html


@pytest.mark.parametrize("coverage", ["complete", "partial", "unknown"])
@pytest.mark.parametrize(("lang", "zero"), [("en", "0.0 B"), ("de", "0,0 B")])
def test_headline_qualifies_zero_without_complete_coverage(
    tmp_path: Path, town_scan: dict, coverage: str, lang: str, zero: str
) -> None:
    _measure(town_scan, "mail.storage_bytes", 0, "mailbox_usage", kind=coverage)
    html = _html(_report(tmp_path / "headline", town_scan, f"language: {lang}"))
    strings = load_locale(lang)
    label = strings["finding"]["mail.storage_bytes"]
    figure = zero if coverage == "complete" else strings["found"]["partial_zero"].format(value=zero)
    assert re.search(
        rf'<li data-provenance="measured">\s*<strong>{re.escape(label)}</strong>\s*'
        rf'<span class="figure">{re.escape(figure)}</span>',
        html,
    )


@pytest.mark.parametrize(
    ("recorded", "inputs_date"), [(True, "2026-11-01"), (False, "2026-11-03"), (True, None)]
)
def test_disagreeing_provided_answers_remain_visible_and_undecided(
    tmp_path: Path, town_scan: dict, recorded: bool, inputs_date: str | None
) -> None:
    finding = _finding(town_scan, "small_apps.in_use")
    finding.update(
        value=recorded,
        provenance="provided",
        source="interview",
        collected_at="2026-11-02",
        missing_reason=None,
    )
    date_input = f'as_of: "{inputs_date}"\n' if inputs_date else ""
    answers = f"{date_input}confirmations: {{small_apps.in_use: {str(not recorded).lower()}}}"

    html = _html(_report(tmp_path / "disagreeing-answers", town_scan, answers))
    row = readiness_row(html, "small_apps")
    strings = load_locale("en")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="provided_answers_conflict"' in row
    assert sorted(re.findall(r'data-provenance="provided">\s*(Yes|No)', row)) == ["No", "Yes"]
    assert strings["source"]["interview"] in row and strings["source"]["inputs_yaml"] in row
    assert "2 November 2026" in row
    supplied_date = (
        f"{int(inputs_date[-2:])} November 2026"
        if inputs_date
        else strings["common"]["date_not_supplied"]
    )
    assert supplied_date in row
    assert 'data-path-status="ready" data-path-workload="small_apps"' not in html


@pytest.mark.parametrize("source", ["inputs_yaml", "sample.inputs_yaml"])
def test_scan_cannot_supply_software_answers_under_an_inputs_source(
    tmp_path: Path, town_scan: dict, source: str
) -> None:
    finding = _finding(town_scan, "windows_software.application_count")
    index = town_scan["findings"].index(finding)
    for row in town_scan["findings"]:
        if row["workload"] == "windows_software":
            row.update(value=0, provenance="provided", source=source, missing_reason=None)

    _reject_scan(
        tmp_path / "missing-list",
        town_scan,
        f"findings[{index}].source",
        "organisation_name: Example organisation",
    )


@pytest.mark.parametrize(
    ("collector_status", "in_use", "status", "reason"),
    [
        ("partial", True, "unknown", "permission_denied"),
        ("partial", False, "needs_work", "permission_denied"),
        ("skipped", False, "needs_work", "permission_denied"),
        ("ok", True, "unknown", "confirmation_conflict"),
        ("ok", False, "needs_work", None),
    ],
)
def test_transfer_need_agrees_with_the_readiness_evidence(
    tmp_path: Path,
    town_scan: dict,
    collector_status: str,
    in_use: bool,
    status: str,
    reason: str | None,
) -> None:
    failure = None if collector_status == "ok" else "permission_denied"
    town_scan["collectors"].append(
        {"id": "telephony", "status": collector_status, "reason": failure, "permissions_used": []}
    )
    if collector_status == "skipped":
        _finding(town_scan, "telephony.in_use").update(
            collector="telephony", missing_reason=failure
        )
    else:
        _measure(town_scan, "telephony.in_use", False, "telephony")
    inputs = f"""
confirmations:
  telephony.in_use: {str(in_use).lower()}
  telephony.replacement_available: false
"""

    html = _html(_report(tmp_path / "transfer-evidence", town_scan, inputs))
    row = readiness_row(html, "telephony")
    assert f'data-status="{status}"' in row
    if status == "needs_work":
        assert "Review whether the assigned Teams Phone licences are still needed" in row
    gap = re.search(r'<li data-gap="telephony".*?</li>', html, re.S)
    assert gap is not None
    if reason is None:
        assert 'data-need="no"' in gap[0] and 'data-provenance="measured"' in gap[0]
    else:
        assert "data-incomplete" in row
        assert f'data-reason="{reason}"' in row and f'data-reason="{reason}"' in gap[0]
        assert 'data-need="unknown"' in gap[0] and 'data-provenance="unknown"' in gap[0]
        assert 'data-provenance="measured"' not in gap[0]


@pytest.mark.parametrize(
    ("source", "in_use", "status", "need"),
    [
        ("provided", True, "blocker", "yes"),
        ("measured", True, "blocker", "yes"),
        ("provided", False, "needs_work", "no"),
        ("measured", False, "needs_work", "no"),
        ("unknown", None, "unknown", "unknown"),
    ],
)
def test_assigned_phone_licences_do_not_establish_operational_use(
    tmp_path: Path, town_scan: dict, source: str, in_use: bool | None, status: str, need: str
) -> None:
    answers = "confirmations:\n  telephony.replacement_available: false\n"
    if source == "provided":
        answers += f"  telephony.in_use: {str(in_use).lower()}\n"
    elif source == "measured":
        town_scan["collectors"].append(
            {"id": "telephony", "status": "ok", "reason": None, "permissions_used": []}
        )
        _measure(town_scan, "telephony.in_use", in_use, "telephony")

    html = _html(_report(tmp_path / "phone-use", town_scan, answers))
    row = readiness_row(html, "telephony")
    assert f'data-status="{status}"' in row
    assert f'data-gap="telephony" data-need="{need}"' in html
    if in_use is False:
        assert "Review whether the assigned Teams Phone licences are still needed" in row


def test_header_shows_both_file_dates_when_samples_are_mixed(
    tmp_path: Path, town_scan: dict
) -> None:
    source = files("fazit").joinpath("demo", "nonprofit", "inputs.yaml")
    html = _html(_report(tmp_path / "mixed-samples", town_scan, source.read_text(encoding="utf-8")))
    header = html.split("</header>", 1)[0]
    scan = re.search(r'<div data-input-role="scan">.*?</div>', header, re.S)
    inputs = re.search(r'<div data-input-role="inputs">.*?</div>', header, re.S)

    assert scan is not None and inputs is not None and scan.end() <= inputs.start()
    assert "scan.json" in scan[0] and f'datetime="{town_scan["generated_at"]}"' in scan[0]
    assert "inputs.yaml" in inputs[0] and 'datetime="2026-11-12"' in inputs[0]
    assert "Linden Bridge Association" in header and "inventory.json" not in header
    assert "answers.yaml" not in header
    assert 'data-status="ready"' in readiness_row(html, "sharepoint")


@pytest.mark.parametrize(
    ("software", "status", "desktop_need", "applications_need"),
    [
        ("null", "unknown", "unknown", "unknown"),
        ("[]", "ready", "unknown", "no"),
        ("[{name: Records, vendor_has_web_version: true}]", "needs_work", "unknown", "yes"),
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
    row = readiness_row(html, "windows_software")

    assert f'data-status="{status}"' in row
    assert f'data-gap="desktop_operating_system" data-need="{desktop_need}"' in html
    assert f'data-gap="windows_applications" data-need="{applications_need}"' in html
    if "vendor_has_web_version: false" in software:
        assert "blocks a move away from Windows desktops" in row
        assert "Microsoft 365 exit" in row
        assert 'data-status="needs_work" data-incomplete' in row
        assert "At least 1 application" in row and 'data-reason="answer_not_provided"' in row


@pytest.mark.parametrize("profile", ["opendesk", "nextcloud"])
@pytest.mark.parametrize(("answer", "expected"), [("false", "no"), ("true", "yes")])
def test_desktop_gap_accepts_a_specific_confirmed_requirement(
    tmp_path: Path, town_scan: dict, profile: str, answer: str, expected: str
) -> None:
    answers = f"""
target_profile: {profile}
windows_only_software: []
confirmations:
  device_management.windows_desktops_required: {answer}
"""
    html = _html(_report(tmp_path / "desktop-confirmed", town_scan, answers))
    gap = re.search(
        rf'<li data-gap="desktop_operating_system" data-need="{expected}">.*?</li>', html, re.S
    )
    assert gap is not None and 'data-provenance="provided"' in gap[0]
    assert "Windows desktops required for applications, devices or peripherals" in gap[0]


@pytest.mark.parametrize("profile", ["opendesk", "nextcloud"])
def test_desktop_gap_shows_disputed_software_count_from_another_workload(
    tmp_path: Path, town_scan: dict, profile: str
) -> None:
    finding = _finding(town_scan, "windows_software.without_web_version_count")
    finding.update(
        value=2,
        provenance="provided",
        source="sample.interview",
        collected_at="2026-11-02",
        missing_reason=None,
    )
    answers = f"""
target_profile: {profile}
as_of: "2026-11-02"
windows_only_software: []
confirmations:
  device_management.windows_desktops_required: false
"""

    html = _html(_report(tmp_path / "disputed-desktop", town_scan, answers))

    row = readiness_row(html, "windows_software")
    assert 'data-reason="provided_answers_conflict"' in row
    gap = re.search(
        r'<li data-gap="desktop_operating_system" data-need="unknown">.*?</li>', html, re.S
    )
    assert gap is not None and 'data-reason="provided_answers_conflict"' in gap[0]


@pytest.mark.parametrize("profile", ["opendesk", "nextcloud"])
def test_desktop_gap_shows_disagreement_between_confirmation_and_software_list(
    tmp_path: Path, town_scan: dict, profile: str
) -> None:
    answers = f"""
target_profile: {profile}
as_of: 2026-11-02
windows_only_software:
  - {{name: Records, vendor_has_web_version: false}}
  - {{name: Permits, vendor_has_web_version: false}}
confirmations:
  device_management.windows_desktops_required: false
"""
    html = _html(_report(tmp_path / "desktop-disagreement", town_scan, answers))

    gap = re.search(
        r'<li data-gap="desktop_operating_system" data-need="unknown">.*?</li>', html, re.S
    )
    assert gap is not None and 'data-reason="desktop_requirements_conflict"' in gap[0]
    assert "Windows desktops are unnecessary" in gap[0]
    assert "Windows-only applications without a web version" in gap[0]
    assert "2 applications" in readiness_row(html, "windows_software")
    desktop_evidence = re.search(
        r'<tr data-finding="device_management\.windows_desktops_required"'
        r' data-provenance="provided".*?</tr>',
        html,
        re.S,
    )
    assert desktop_evidence is not None and re.search(r"\bNo\b", desktop_evidence[0])


@pytest.mark.parametrize(
    ("lang", "title"),
    [("en", "Direct transfer unverified"), ("de", "Direkte Übernahme nicht belegt")],
)
def test_transfer_gap_heading_describes_the_scope_of_evidence(
    tmp_path: Path, town_scan: dict, lang: str, title: str
) -> None:
    html = _html(_report(tmp_path / "transfer", town_scan, f"language: {lang}"))
    section = re.search(r'<div data-subsection="cannot-be-moved">.*?</div>', html, re.S)
    assert section is not None
    assert f"<h3>{title}</h3>" in section[0]
    assert load_locale(lang)["attention"]["gap_scope"] in section[0]
