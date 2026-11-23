# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path

import pytest
from helpers import readiness_row, report_section, runner
from typer.testing import Result

from fazit.catalogue import load_catalogue
from fazit.cli import app
from fazit.i18n import load_locale
from fazit.licences import load_service_plans
from fazit.model import Coverage

NO_TELEPHONY = "confirmations: {telephony.in_use: false, telephony.replacement_available: false}"
LICENCE_PILOTS = ("power_platform", "telephony", "identity_access", "security_compliance")


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


def _stamp_directory(scan: dict, stamp: str) -> None:
    for finding in scan["findings"]:
        if finding["source"] == "sample.directory":
            finding["collected_at"] = stamp
    scan["directory_population"]["collected_at"] = stamp


def _report(
    tmp_path: Path, scan: dict, answers: str | None = None, *, lang: str | None = None
) -> Result:
    tmp_path.mkdir()
    source = tmp_path / "inventory.json"
    source.write_text(json.dumps(scan), encoding="utf-8")
    options = []
    if answers is not None:
        inputs = tmp_path / "answers.yaml"
        inputs.write_text(answers, encoding="utf-8")
        options = ["--inputs", str(inputs)]
    if lang is not None:
        options.extend(("--lang", lang))
    command = ["report", str(source), "--out", str(tmp_path / "out"), *options]
    return runner.invoke(app, command)


def _html(result: Result) -> str:
    assert result.exit_code == 0 and not result.stderr, result.output
    return Path(result.stdout.strip()).read_text(encoding="utf-8")


def _reject_scan(
    tmp_path: Path, scan: dict, field: str, answers: str | None = None, *, lang: str | None = None
) -> str:
    result = _report(tmp_path, scan, answers, lang=lang)
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

    for workload in LICENCE_PILOTS:
        assert 'data-status="unknown"' in readiness_row(before, workload)
        row = readiness_row(after, workload)
        assert 'data-status="unknown"' in row, workload
        assert f'data-reason="{reason}"' in row
    for html, code in (
        (before, "licence_assignments_conflict"),
        (after, "licence_directory_unverified"),
    ):
        assert f'data-reason="{code}"' in report_section(html, "found")
    product["assigned"] = assigned
    positive = _html(_report(tmp_path / "directory-skipped-with-assignments", scan, answers))
    assert 'data-reason="licence_directory_unverified"' in report_section(positive, "found")
    for workload in LICENCE_PILOTS:
        row = readiness_row(positive, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert f'data-reason="{reason}"' in row
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
        ("collected_at", "2026-11-04"),
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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("period", "2026-11-02/2026-11-04"),
        ("collected_at", "2026-11-04"),
        ("collected_at", "2026-11-02T08:30:00-01:00"),
    ],
)
def test_report_rejects_future_interview_evidence(
    tmp_path: Path, town_scan: dict, field: str, value: str
) -> None:
    interview = _finding(town_scan, "telephony.in_use")
    interview.update(
        value=True,
        provenance="provided",
        source="interview",
        period="2026-10-20/2026-11-02",
        missing_reason=None,
    )
    _html(_report(tmp_path / "on-scan-date", town_scan))

    interview[field] = value
    index = town_scan["findings"].index(interview)
    _reject_scan(tmp_path / "future-interview", town_scan, f"findings[{index}].{field}")


@pytest.mark.parametrize(
    ("scan_stamp", "stamp"),
    [
        ("2026-11-02T09:00:00Z", "2026-11-02"),
        ("2026-11-02T10:00:00Z", "2026-11-03"),
        ("2026-11-02T09:00:00Z", "2026-11-02T10:00:00+01:00"),
    ],
)
def test_report_accepts_days_that_have_started_and_equal_instants(
    tmp_path: Path, town_scan: dict, scan_stamp: str, stamp: str
) -> None:
    town_scan["generated_at"] = scan_stamp
    if len(stamp) == 10:
        for finding in town_scan["findings"]:
            if finding["source"] == "sample.teams_usage":
                finding["collected_at"] = stamp
    _finding(town_scan, "teams.teams_with_guests_count")["collected_at"] = stamp

    _html(_report(tmp_path / "possible-date", town_scan))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("collected_at", "2026-11-02T08:59:59Z"),
        ("collected_at", "2026-11-02"),
        ("period", "2026-05-07/2026-11-01"),
        ("period", None),
    ],
)
def test_report_rejects_mixed_stamps_from_one_source(
    tmp_path: Path, town_scan: dict, field: str, value: str | None
) -> None:
    guests = _finding(town_scan, "teams.teams_with_guests_count")
    guests[field] = value
    index = town_scan["findings"].index(guests)

    _reject_scan(tmp_path / "mixed-stamps", town_scan, f"findings[{index}].{field}")


@pytest.mark.parametrize("stamp", ["2026-11-01", "2026-11-01T08:00:00Z"])
def test_report_compares_interview_counts_from_the_same_source_and_day(
    tmp_path: Path, town_scan: dict, stamp: str
) -> None:
    population = _finding(town_scan, "device_management.device_count")
    windows = _finding(town_scan, "device_management.windows_device_count")
    for row, value, date in ((population, 10, "2026-11-01"), (windows, 20, stamp)):
        row.update(
            value=value,
            provenance="provided",
            source="interview",
            collected_at=date,
            missing_reason=None,
        )

    index = town_scan["findings"].index(windows)
    _reject_scan(tmp_path / "inconsistent-counts", town_scan, f"findings[{index}].value")

    windows.update(collected_at="2026-10-31")
    _html(_report(tmp_path / "different-day", town_scan))
    windows.update(source="sample.interview", collected_at=stamp)
    _html(_report(tmp_path / "different-source", town_scan))


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
    assert 'href="#readiness-integrations" data-unexamined-workload=' in report_section(
        skipped, "path"
    )


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
    open_points = report_section(html, "path").split('id="not-examined"', 1)[1]
    assert 'href="#readiness-integrations"' in open_points.split("</dl>", 1)[0]


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

    found = report_section(html, "found")
    evidence = re.search(
        r'<summary id="licences-title"[^>]*>.*?</summary>\s*(<p[^>]*>.*?</p>)', found, re.S
    )
    assert evidence is not None
    provenance = "measured" if coverage == "complete" else "unknown"
    assert f'data-provenance="{provenance}"' in evidence[1]
    assert ("Licence products found: 0" in evidence[1]) is (coverage == "complete")
    if reason:
        assert f'data-reason="{reason}"' in evidence[1]
    else:
        assert "data-reason=" not in evidence[1] and "0 of 0 scanned" in evidence[1]
    telephony = readiness_row(html, "telephony")
    assert f'data-status="{status}"' in telephony
    if coverage != "complete":
        assert 'data-reason="licence_products_missing"' in telephony
        assert "No licence products were recorded." in evidence[1]
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


@pytest.mark.parametrize("lang", ["en", "de"])
def test_report_shows_excess_assignments_as_assigned_use(
    tmp_path: Path, town_scan: dict, lang: str
) -> None:
    phone = next(p for p in town_scan["licences"]["products"] if p["sku_part_number"] == "MCOEV")
    phone.update(purchased=0, assigned=12)

    html = _html(_report(tmp_path / "excess-assignments", town_scan, NO_TELEPHONY, lang=lang))
    strings = load_locale(lang)
    note = strings["licences"]["assigned_exceeds_purchased"].format(count=12)
    assert f'data-reason="assigned_exceeds_purchased">{note}' in html
    row = readiness_row(html, "telephony")
    assert 'data-status="needs_work"' in row
    assert re.search(
        r'<li data-evidence="telephony\.licence_add_on_assigned">\s*<strong>[^<]+</strong>\s*'
        rf'<div data-provenance="measured">\s*{strings["common"]["yes"]}',
        row,
    )


@pytest.mark.parametrize(
    ("lang", "note"),
    [
        ("de", "Es ist 1 Lizenzplatz mehr zugewiesen als erworben."),
        ("en", "The assigned count exceeds the purchased count by 1."),
    ],
)
def test_report_describes_one_excess_licence_seat(
    tmp_path: Path, town_scan: dict, lang: str, note: str
) -> None:
    phone = next(p for p in town_scan["licences"]["products"] if p["sku_part_number"] == "MCOEV")
    phone.update(purchased=11, assigned=12)

    html = _html(_report(tmp_path / "one-excess-assignment", town_scan, lang=lang))
    assert f'data-reason="assigned_exceeds_purchased">{note}' in html


def test_report_distinguishes_registered_skus_with_the_same_part_number(
    tmp_path: Path, town_scan: dict
) -> None:
    products = [
        {
            "sku_part_number": "MCOPSTN5",
            "sku_guid": "54a152dc-90de-4996-93d2-bc47e670fc06",
            "purchased": 3,
            "assigned": 1,
            "service_plans": [{"name": "MCOPSTN5", "guid": "54a152dc-90de-4996-93d2-bc47e670fc06"}],
        },
        {
            "sku_part_number": "MCOPSTN5",
            "sku_guid": "d43177b5-475b-4880-92d4-d54c27b5efbd",
            "purchased": 3,
            "assigned": 2,
            "service_plans": [
                {
                    "name": "Skype for Business PSTN Calling Domestic Small",
                    "guid": "9a0125a5-c8f8-4526-b231-49e2abe0ebce",
                }
            ],
        },
    ]
    town_scan["licences"].update(
        products=products, coverage={"kind": "complete", "scanned": 2, "failed": 0, "total": 2}
    )
    _finding(town_scan, "directory.licensed_user_count")["value"] = 3

    html = _html(_report(tmp_path / "same-part-number", town_scan, NO_TELEPHONY))
    assert 'data-status="needs_work"' in readiness_row(html, "telephony")
    assert html.count('data-product="MCOPSTN5"') == 2
    assert "Unclassified service plans" not in html
    for product in products:
        assert f"<code>{product['sku_guid']}</code>" in html
        assert f"<code>{product['service_plans'][0]['name']}</code>" in html

    products[1]["service_plans"][0]["guid"] = products[0]["sku_guid"]
    _reject_scan(
        tmp_path / "unregistered-plan-pair", town_scan, "licences.products[1].service_plans[0].name"
    )


@pytest.mark.parametrize("missing", ["sku_part_number", "sku_guid"])
def test_partial_inventory_accepts_a_shared_sku_with_one_identifier(
    tmp_path: Path, town_scan: dict, missing: str
) -> None:
    products = [
        {
            "sku_part_number": roster.part_number,
            "sku_guid": roster.sku_guid,
            "purchased": 1,
            "assigned": 1,
            "service_plans": [
                {"name": plan.name, "guid": plan.guid} for plan in roster.plans.values()
            ],
        }
        for roster in load_service_plans(load_catalogue()).rosters.values()
        if roster.part_number == "MCOPSTN5"
    ]
    del products[0][missing]
    town_scan["licences"].update(
        products=products, coverage={"kind": "partial", "scanned": 2, "failed": 1, "total": 3}
    )

    html = _html(_report(tmp_path / "partial-inventory", town_scan, NO_TELEPHONY))
    assert html.count('data-product="MCOPSTN5"') == 1
    assert 'data-status="needs_work" data-incomplete' in readiness_row(html, "telephony")
    assert 'data-status="unknown" data-incomplete' in readiness_row(html, "power_platform")

    products[0][missing] = (
        "MCOEV" if missing == "sku_part_number" else ("00000000-0000-4000-8000-000000000001")
    )
    _reject_scan(tmp_path / "conflicting-identifiers", town_scan, f"licences.products[0].{missing}")


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
def test_unidentified_products_leave_licence_absence_unknown(
    tmp_path: Path, town_scan: dict, identity: dict[str, str | None]
) -> None:
    products = town_scan["licences"]["products"]
    assert products[1]["sku_part_number"] == "MCOEV"
    products[1] = {**identity, "purchased": 0, "assigned": 0, "service_plans": []}
    html = _html(_report(tmp_path / "unassigned", town_scan, NO_TELEPHONY))
    row = readiness_row(html, "telephony")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-reason="licence_product_unidentified"' in row
    assert 'data-reason="licence_product_unidentified"' in report_section(html, "found")
    assert 'data-status="needs_work"' in readiness_row(html, "power_platform")

    products[1].update(purchased=12, assigned=12)
    html = _html(_report(tmp_path / "assigned", town_scan, NO_TELEPHONY))
    row = readiness_row(html, "telephony")
    assert 'data-status="unknown" data-incomplete' in row
    assert 'data-provenance="unknown"' in row
    assert 'data-reason="licence_plan_list_missing"' in row
    assert 'data-status="needs_work"' in readiness_row(html, "power_platform")


@pytest.mark.parametrize("first", ["service_plans", "identifiers"])
def test_losing_unassigned_product_evidence_does_not_restore_ready(
    tmp_path: Path, first: str
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit")
    scan = json.loads(sample.joinpath("scan.json").read_text(encoding="utf-8"))
    roster = next(
        roster
        for roster in load_service_plans(load_catalogue()).rosters.values()
        if roster.part_number == "STANDARDPACK"
    )
    product = {
        "sku_part_number": roster.part_number,
        "sku_guid": roster.sku_guid,
        "purchased": 1,
        "assigned": 0,
        "service_plans": [{"name": plan.name, "guid": plan.guid} for plan in roster.plans.values()],
    }
    scan["licences"]["products"].append(product)
    scan["licences"]["coverage"].update(scanned=2, total=2)
    answers = sample.joinpath("inputs.yaml").read_text(encoding="utf-8")
    baseline = _html(_report(tmp_path / "complete", scan, answers))
    for workload in ("directory", *LICENCE_PILOTS):
        assert 'data-status="ready"' in readiness_row(baseline, workload)

    omissions = {
        "service_plans": ("service_plans",),
        "identifiers": ("sku_part_number", "sku_guid"),
    }
    for step in (first, next(name for name in omissions if name != first)):
        for field in omissions[step]:
            del product[field]
        report = _html(_report(tmp_path / step, scan, answers))
        for workload in LICENCE_PILOTS:
            assert 'data-status="unknown" data-incomplete' in readiness_row(report, workload)
        if "sku_guid" not in product:
            row = readiness_row(report, "directory")
            assert 'data-status="unknown" data-incomplete' in row
            assert 'data-reason="licence_product_unidentified"' in row


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
    found = report_section(html, "found")
    assert f"Licence products found: {len(licences['products'])}" in found
    assert 'data-reason="licence_assignments_conflict"' in found
    assert 'data-workload="licences"' not in report_section(html, "readiness")
    assert 'href="#readiness-telephony" data-unexamined-workload=' in report_section(html, "path")


@pytest.mark.parametrize(
    ("assigned", "account_update", "reason"),
    [
        (1, {}, "licence_assignments_conflict"),
        (20, {"value": 0}, "licence_assignments_conflict"),
        (1, {"collected_at": "2026-11-05T09:59:59Z"}, "licence_directory_unverified"),
        (20, {"coverage": {"kind": "partial"}}, "coverage_partial"),
        (20, {"coverage": {"kind": "unknown"}}, "coverage_unknown"),
        (20, None, "not_in_scan"),
        (
            20,
            {
                "value": None,
                "provenance": "unknown",
                "coverage": None,
                "missing_reason": "permission_denied",
            },
            "permission_denied",
        ),
    ],
    ids=[
        "too-few-seats",
        "too-many-seats",
        "different-instant",
        "partial",
        "unknown",
        "missing",
        "denied",
    ],
)
def test_licence_pilots_require_reconciled_directory_headcount(
    tmp_path: Path, assigned: int, account_update: dict | None, reason: str
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit")
    scan = json.loads(sample.joinpath("scan.json").read_text(encoding="utf-8"))
    answers = sample.joinpath("inputs.yaml").read_text(encoding="utf-8")
    answers = answers.replace(
        "licences.contract_terms_known: false", "licences.contract_terms_known: true"
    )
    (product,) = scan["licences"]["products"]
    accounts = _finding(scan, "directory.licensed_user_count")
    accounts["collected_at"] = "2026-11-05T11:00:00+01:00"
    baseline = _html(_report(tmp_path / "reconciled", scan, answers))
    assert 'data-workload="licences"' not in report_section(baseline, "readiness")

    product["assigned"] = assigned
    if account_update is None:
        scan["findings"].remove(accounts)
    else:
        if stamp := account_update.get("collected_at"):
            _stamp_directory(scan, stamp)
        accounts.update(account_update)
    html = _html(_report(tmp_path / "unreconciled", scan, answers))
    if reason != "licence_assignments_conflict":
        assert 'data-reason="licence_assignments_conflict"' not in html
    inventory_reason = (
        reason if reason == "licence_assignments_conflict" else "licence_directory_unverified"
    )
    assert f'data-reason="{inventory_reason}"' in report_section(html, "found")
    open_points = report_section(html, "path")
    for workload in ("directory", *LICENCE_PILOTS):
        assert 'data-status="ready"' in readiness_row(baseline, workload)
        row = readiness_row(html, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert f'data-reason="{reason}"' in row
        assert f'href="#readiness-{workload}" data-unexamined-workload=' in open_points
    assert re.search(
        r'<li data-evidence="small_apps\.licence_bundled_assigned">\s*<strong>[^<]+</strong>\s*'
        r'<div data-provenance="measured">\s*Yes',
        readiness_row(html, "small_apps"),
    )


@pytest.mark.parametrize("violation", ["directory-population", "empty-coverage"])
def test_report_rejects_impossible_licensed_headcounts(tmp_path: Path, violation: str) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit", "scan.json")
    scan = json.loads(sample.read_text(encoding="utf-8"))
    accounts = _finding(scan, "directory.licensed_user_count")
    if violation == "directory-population":
        _finding(scan, "directory.user_count")["value"] = 0
        assert _finding(scan, "directory.guest_count")["value"] == 0
    else:
        accounts["coverage"].update(scanned=0, failed=0, total=0)

    index = scan["findings"].index(accounts)
    _reject_scan(tmp_path / violation, scan, f"findings[{index}].value")


def test_report_bounds_unchecked_internal_accounts(tmp_path: Path) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit", "scan.json")
    scan = json.loads(sample.read_text(encoding="utf-8"))
    scan["directory_population"] = {
        "collector": "directory",
        "collected_at": scan["generated_at"],
        "coverage": asdict(Coverage("complete", 20, 0, 20)),
    }
    _finding(scan, "directory.user_count").update(
        value=0, coverage={"kind": "partial", "scanned": 19, "failed": 1, "total": 20}
    )
    _finding(scan, "directory.guest_count")["value"] = 19
    _html(_report(tmp_path / "twenty-accounts", scan))

    accounts = _finding(scan, "directory.licensed_user_count")
    accounts["value"] = 21
    scan["licences"]["products"][0]["assigned"] = 21
    index = scan["findings"].index(accounts)
    _reject_scan(tmp_path / "too-many-accounts", scan, f"findings[{index}].value")


@pytest.mark.parametrize(
    ("member", "guest", "licensed", "declared_error"),
    [
        ((0, Coverage("partial", 19, 1, 20)), (19, Coverage("complete")), 21, "licensed_user"),
        ((0, Coverage("partial", 19, 1, 20)), (19, Coverage("partial", 19, 0, 21)), 22, None),
        ((11, Coverage("complete", 20, 0, 20)), (10, Coverage("complete", 20, 0, 20)), 20, "guest"),
        (
            (20, Coverage("complete", 20, 0, 20)),
            (20, Coverage("complete", 20, 0, 20)),
            25,
            "licensed_user",
        ),
        ((10, Coverage("complete", 10, 0, 10)), (10, Coverage("complete", 10, 0, 10)), 11, None),
    ],
    ids=[
        "missing-guest-total",
        "different-totals",
        "twenty-one-in-twenty",
        "double-twenty",
        "filtered",
    ],
)
def test_directory_counts_without_a_declared_population_keep_licence_pilots_unknown(
    tmp_path: Path,
    member: tuple[int, Coverage],
    guest: tuple[int, Coverage],
    licensed: int,
    declared_error: str | None,
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit")
    scan = json.loads(sample.joinpath("scan.json").read_text(encoding="utf-8"))
    answers = sample.joinpath("inputs.yaml").read_text(encoding="utf-8")
    scan.pop("directory_population", None)
    for kind, (value, coverage) in (
        ("user", member),
        ("guest", guest),
        ("licensed_user", (licensed, Coverage("complete"))),
    ):
        _finding(scan, f"directory.{kind}_count").update(value=value, coverage=asdict(coverage))
    scan["licences"]["products"][0]["assigned"] = licensed

    html = _html(_report(tmp_path / "undeclared", scan, answers))
    for workload in LICENCE_PILOTS:
        row = readiness_row(html, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert 'data-reason="licence_directory_unverified"' in row
    if declared_error is not None:
        scan["directory_population"] = {
            "collector": "directory",
            "collected_at": scan["generated_at"],
            "coverage": asdict(Coverage("complete", 20, 0, 20)),
        }
        index = scan["findings"].index(_finding(scan, f"directory.{declared_error}_count"))
        _reject_scan(tmp_path / "declared", scan, f"findings[{index}].value", answers)


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize(
    ("case", "status"),
    [
        ("filtered", "unknown"),
        ("undeclared", "unknown"),
        ("older-members", "rejected"),
        ("older-guests", "rejected"),
        ("unknown-population", "unknown"),
        ("no-inventory", "unknown"),
        ("confirmed-guest", "needs_work"),
    ],
)
def test_directory_ready_requires_counts_in_a_complete_declared_population(
    tmp_path: Path, town_scan: dict, lang: str, case: str, status: str
) -> None:
    town_scan["licences"] = None
    population = town_scan["directory_population"]
    population.update(
        collected_at="2026-11-02T10:00:00+01:00",
        coverage=asdict(Coverage("complete", 2, 0, 2)),
    )
    members = _finding(town_scan, "directory.user_count")
    guests = _finding(town_scan, "directory.guest_count")
    licensed = _finding(town_scan, "directory.licensed_user_count")
    members["value"], guests["value"], licensed["value"] = 2, 0, 2
    if case in ("filtered", "undeclared", "confirmed-guest"):
        del town_scan["directory_population"]
    if case == "filtered":
        members["value"] = 1
        members["coverage"] = guests["coverage"] = asdict(Coverage("complete", 1, 0, 1))
    elif case == "undeclared":
        members["value"], licensed["value"] = 0, 20
    elif status == "rejected":
        stale = members if case == "older-members" else guests
        stale["collected_at"] = "2026-11-02T08:59:59Z"
        town_scan["findings"].remove(stale)
        index = len(town_scan["findings"])
        town_scan["findings"].append(stale)
        _reject_scan(tmp_path / case, town_scan, f"findings[{index}].collected_at", lang=lang)
        return
    elif case == "unknown-population":
        population["coverage"] = {"kind": "unknown", "total": 2}
    elif case == "confirmed-guest":
        guests["value"] = 1
    answers = "confirmations: {directory.account_list_reviewed: true}"

    row = readiness_row(_html(_report(tmp_path / case, town_scan, answers, lang=lang)), "directory")

    assert f'data-status="{status}"' in row
    absence = {"en": "there are no guest accounts", "de": "es gibt keine Gastkonten"}
    assert (absence[lang] in row) == (status == "ready")
    if case == "no-inventory":
        assert 'data-reason="not_in_scan"' in row
    elif status == "unknown":
        assert 'data-reason="directory_population_unverified"' in row


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize(
    ("assigned", "guests", "licence_status", "status", "reason"),
    [
        (1, 0, "ok", "ready", None),
        (2, 0, "ok", "unknown", "licence_assignments_conflict"),
        (2, 1, "ok", "needs_work", "licence_assignments_conflict"),
        (2, 0, "skipped", "unknown", "permission_denied"),
        (2, 0, "partial", "unknown", "coverage_partial"),
        (1, 0, "absent", "unknown", "not_in_scan"),
        (1, 0, "inventory-partial", "unknown", "coverage_partial"),
        (1, 0, "inventory-unknown", "unknown", "coverage_unknown"),
    ],
    ids=[
        "reconciled",
        "conflict",
        "conflict-with-guest",
        "licences-skipped",
        "licences-partial",
        "licences-absent",
        "inventory-partial",
        "inventory-unknown",
    ],
)
def test_directory_accounts_are_checked_against_licences(
    tmp_path: Path,
    town_scan: dict,
    lang: str,
    assigned: int,
    guests: int,
    licence_status: str,
    status: str,
    reason: str | None,
) -> None:
    coverage = asdict(Coverage("complete", 1, 0, 1))
    town_scan["directory_population"]["coverage"] = coverage
    _finding(town_scan, "directory.user_count")["value"] = 1 - guests
    _finding(town_scan, "directory.guest_count")["value"] = guests
    _finding(town_scan, "directory.licensed_user_count")["value"] = 1
    collector = next(row for row in town_scan["collectors"] if row["id"] == "licences")
    if licence_status == "absent":
        town_scan["collectors"].remove(collector)
    elif licence_status in {"skipped", "partial"}:
        collector.update(status=licence_status, reason=reason)
    if licence_status in {"skipped", "absent"}:
        town_scan["licences"] = None
    else:
        inventory = town_scan["licences"]
        product = inventory["products"][0]
        product["assigned"] = assigned
        kind = (
            licence_status.removeprefix("inventory-")
            if licence_status.startswith("inventory-")
            else "complete"
        )
        inventory.update(products=[product], coverage=coverage | {"kind": kind})
    answers = "confirmations: {directory.account_list_reviewed: true}"

    html = _html(_report(tmp_path / "licence-check", town_scan, answers, lang=lang))
    row = readiness_row(html, "directory")
    if reason == "licence_assignments_conflict":
        assert f'data-reason="{reason}"' in report_section(html, "found")
    assert f'data-status="{status}"' in row
    absence = {"en": "there are no guest accounts", "de": "es gibt keine Gastkonten"}
    assert (absence[lang] in html) == (status == "ready")
    if reason is not None:
        assert f'data-reason="{reason}"' in row and "data-incomplete" in row
        assert load_locale(lang)["reason"][reason]["label"] in row


@pytest.mark.parametrize("state", ["partial", "unknown", "different-instant"])
def test_licence_pilots_require_a_complete_directory_population_at_the_same_instant(
    tmp_path: Path, state: str
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit")
    scan = json.loads(sample.joinpath("scan.json").read_text(encoding="utf-8"))
    answers = sample.joinpath("inputs.yaml").read_text(encoding="utf-8")
    scan["directory_population"] = {
        "collector": "directory",
        "collected_at": scan["generated_at"],
        "coverage": asdict(Coverage("complete", 21, 0, 21)),
    }
    baseline = _html(_report(tmp_path / "complete", scan, answers))
    for workload in LICENCE_PILOTS:
        assert 'data-status="ready"' in readiness_row(baseline, workload)

    population = scan["directory_population"]
    reason = "licence_directory_unverified"
    if state == "different-instant":
        population["collected_at"] = "2026-11-05T10:59:59+01:00"
    else:
        population["coverage"] = asdict(Coverage(state, 20, 1, 21))
        members = _finding(scan, "directory.user_count")
        field = f"findings[{scan['findings'].index(members)}].coverage"
        _reject_scan(tmp_path / "contradictory", scan, field, answers)
        members["value"] = 20
        for finding_id in ("user_count", "guest_count", "licensed_user_count"):
            _finding(scan, f"directory.{finding_id}")["coverage"] = population["coverage"]
        reason = f"coverage_{state}"
    html = _html(_report(tmp_path / state, scan, answers))
    for workload in LICENCE_PILOTS:
        row = readiness_row(html, workload)
        assert 'data-status="unknown" data-incomplete' in row
        assert f'data-reason="{reason}"' in row


@pytest.mark.parametrize("date_only", ["both", "directory", "licences"])
def test_report_rejects_date_only_snapshots_that_could_restore_licence_pilots(
    tmp_path: Path, date_only: str
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit", "scan.json")
    scan = json.loads(sample.read_text(encoding="utf-8"))
    accounts = _finding(scan, "directory.licensed_user_count")
    _stamp_directory(scan, "2026-11-05T09:59:59Z")
    licences = scan["licences"]
    baseline = _html(_report(tmp_path / "different-instants", scan))
    assert 'data-reason="licence_directory_unverified"' in report_section(baseline, "found")

    if date_only in {"both", "licences"}:
        licences["collected_at"] = licences["collected_at"][:10]
    if date_only in {"both", "directory"}:
        accounts["collected_at"] = accounts["collected_at"][:10]
        field = f"findings[{scan['findings'].index(accounts)}].collected_at"
    else:
        field = "licences.collected_at"
    _reject_scan(tmp_path / date_only, scan, field)


@pytest.mark.parametrize("offsetless", ["directory", "licences"])
def test_report_requires_snapshot_offsets_during_the_repeated_hour(
    tmp_path: Path, town_scan: dict, offsetless: str
) -> None:
    accounts = _finding(town_scan, "directory.licensed_user_count")
    licences = town_scan["licences"]
    _stamp_directory(town_scan, "2026-10-25T02:30:00+02:00")
    licences["collected_at"] = "2026-10-25T02:30:00+01:00"
    html = _html(_report(tmp_path / "different-offsets", town_scan))
    assert 'data-reason="licence_directory_unverified"' in report_section(html, "found")

    if offsetless == "licences":
        licences["collected_at"] = "2026-10-25T02:30:00"
        field = "licences.collected_at"
    else:
        accounts["collected_at"] = "2026-10-25T02:30:00"
        field = f"findings[{town_scan['findings'].index(accounts)}].collected_at"
    _reject_scan(tmp_path / offsetless, town_scan, field)


def test_report_rejects_positive_storage_for_a_known_empty_export(
    tmp_path: Path, town_scan: dict
) -> None:
    accounts = _measure(town_scan, "onedrive.account_count", 0, "onedrive_usage")
    storage = _finding(town_scan, "onedrive.storage_bytes")
    accounts["period"] = storage["period"]
    assert storage["value"] > 0

    index = town_scan["findings"].index(storage)
    _reject_scan(tmp_path / "empty-export", town_scan, f"findings[{index}].value")

    accounts["coverage"].update(kind="partial", scanned=19, total=20)
    _html(_report(tmp_path / "incomplete-export", town_scan))

    accounts["coverage"] = {"kind": "complete"}
    accounts["period"] = "2026-10-01/2026-10-15"
    _reject_scan(tmp_path / "different-export-period", town_scan, f"findings[{index}].period")


@pytest.mark.parametrize(
    ("accounts", "coverage"),
    [
        (0, Coverage("complete", scanned=1, failed=0, total=1)),
        (2, Coverage("complete", scanned=3, failed=0, total=3)),
        (2, Coverage("partial", scanned=2, failed=1)),
        (2, Coverage("partial", scanned=1, total=3)),
    ],
)
def test_one_drive_storage_checks_fit_the_account_population(
    tmp_path: Path, town_scan: dict, accounts: int, coverage: Coverage
) -> None:
    storage = _finding(town_scan, "onedrive.storage_bytes")
    account_count = _finding(town_scan, "onedrive.account_count")
    account_count["value"] = accounts
    storage.update(value=0, coverage=asdict(coverage))
    index = town_scan["findings"].index(storage)
    answers = "confirmations: {onedrive.external_sharing_in_use: false}"

    _reject_scan(tmp_path / "excess-checks", town_scan, f"findings[{index}].coverage", answers)

    storage["coverage"] = asdict(Coverage("complete", accounts, 0, accounts))
    report = _html(_report(tmp_path / "consistent-checks", town_scan, answers))
    assert 'data-status="ready"' in readiness_row(report, "onedrive")


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

    period = guests["period"]
    guests["period"] = "2026-10-01/2026-10-15"
    _reject_scan(tmp_path / "different-period", town_scan, f"findings[{index}].period")
    town_scan["findings"].remove(_finding(town_scan, "teams.team_count"))
    index = town_scan["findings"].index(guests)
    guests.update(period=period, coverage={"kind": "partial", "scanned": 31, "total": 50})
    _reject_scan(tmp_path / "outside-own-scope", town_scan, f"findings[{index}].value")


@pytest.mark.parametrize(
    ("parent_stamp", "subset_stamp"),
    [
        ("2026-11-02T09:00Z", "2026-11-02T10:00+01:00"),
        ("2026-11-02T08:59:59.999999Z", "2026-11-02T09:59:59.999999+01:00"),
    ],
)
def test_report_rejects_a_subset_above_its_population_at_the_same_instant(
    tmp_path: Path, town_scan: dict, parent_stamp: str, subset_stamp: str
) -> None:
    for finding in town_scan["findings"]:
        if finding["source"] == "sample.teams_usage":
            finding.update(period=None, collected_at=parent_stamp)
    guests = _finding(town_scan, "teams.teams_with_guests_count")
    guests.update(value=40, period=None, collected_at=subset_stamp)
    index = town_scan["findings"].index(guests)

    _reject_scan(tmp_path / "same-instant", town_scan, f"findings[{index}].value")

    guests["collected_at"] = "2026-11-02T08:59:59.999998Z"
    _reject_scan(tmp_path / "different-instant", town_scan, f"findings[{index}].collected_at")


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
    assert 'data-reason="licence_plan_list_incomplete"' in report_section(html, "found")
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
    assert 'data-reason="licence_plan_list_missing"' in report_section(html, "found")


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
    assert 'data-reason="licence_not_classified"' in report_section(html, "found")
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
  teams.apps_in_use: false
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
        html.replace("<wbr>", ""),
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


@pytest.mark.parametrize(("replacement", "status"), [("false", "blocker"), ("true", "needs_work")])
@pytest.mark.parametrize("confirmed_in_interview", [False, True])
def test_partial_telephony_collection_keeps_confirmed_use(
    tmp_path: Path, town_scan: dict, replacement: str, status: str, confirmed_in_interview: bool
) -> None:
    town_scan["collectors"].append(
        {
            "id": "telephony",
            "status": "partial",
            "reason": "coverage_partial",
            "permissions_used": [],
        }
    )
    finding = _measure(town_scan, "telephony.in_use", True, "telephony", kind="partial")
    finding["coverage"].update(scanned=1, failed=0, total=85)
    answers = f"confirmations:\n  telephony.replacement_available: {replacement}\n"
    if confirmed_in_interview:
        answers += "  telephony.in_use: true\n"

    html = _html(_report(tmp_path / "partial-phone-use", town_scan, answers))
    row = readiness_row(html, "telephony")
    assert f'data-status="{status}" data-incomplete' in row
    assert 'data-reason="coverage_partial"' in row and "1 of 85 scanned" in row
    assert 'data-gap="telephony" data-need="yes"' in html


def test_report_rejects_telephony_use_when_all_checks_failed(
    tmp_path: Path, town_scan: dict
) -> None:
    licences = town_scan["licences"]
    licences["products"] = [p for p in licences["products"] if p["sku_part_number"] != "MCOEV"]
    licences["coverage"].update(scanned=2, total=2)
    town_scan["collectors"].append(
        {
            "id": "telephony",
            "status": "partial",
            "reason": "coverage_partial",
            "permissions_used": [],
        }
    )
    finding = _measure(town_scan, "telephony.in_use", True, "telephony", kind="partial")
    finding["coverage"].update(scanned=0, failed=85, total=85)
    index = town_scan["findings"].index(finding)

    _reject_scan(
        tmp_path / "failed-telephony",
        town_scan,
        f"findings[{index}].value",
        "confirmations: {telephony.replacement_available: false}",
    )


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
    evidence = re.search(rf'<li data-evidence="{re.escape(finding_id)}">.*?</li>', row, re.S)
    assert evidence is not None and conflict in evidence[0]
    bounds = "" if kind == "complete" else "At least "
    assert re.findall(
        r'data-provenance="(?:measured|provided)">\s*([^\n]+ applications)', evidence[0]
    ) == [
        f"{bounds}3 applications",
        "0 applications",
    ]
    open_points = report_section(html, "path").split('id="not-examined"', 1)[1]
    assert 'href="#readiness-integrations"' in open_points.split("</dl>", 1)[0]

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
        r'<li data-provenance="measured">\s*'
        rf'<strong class="tile-label">{re.escape(label)}</strong>\s*'
        rf'<span class="figure-num">{re.escape(figure)}</span>',
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
    evidence = re.search(r'<li data-evidence="small_apps\.in_use">.*?</li>', row, re.S)
    assert evidence is not None
    assert sorted(re.findall(r'data-provenance="provided">\s*(Yes|No)', evidence[0])) == [
        "No",
        "Yes",
    ]
    assert strings["source"]["interview"] in evidence[0]
    assert strings["source"]["inputs_yaml"] in evidence[0]
    assert "2\u00a0November\u00a02026" in evidence[0]
    supplied_date = (
        f"{int(inputs_date[-2:])}\u00a0November\u00a02026"
        if inputs_date
        else strings["common"]["date_not_supplied"]
    )
    assert supplied_date in evidence[0]
    assert 'href="#readiness-small_apps" data-unexamined-workload=' in report_section(html, "path")


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
    ("software", "status", "applications_need"),
    [
        ("null", "unknown", "unknown"),
        ("[]", "ready", "no"),
        ("[{name: Records, vendor_has_web_version: true}]", "needs_work", "yes"),
        ("[{name: Records}]", "needs_work", "yes"),
        (
            "[{name: Records, vendor_has_web_version: false}, {name: Permits}]",
            "needs_work",
            "yes",
        ),
    ],
)
def test_windows_dependency_is_scoped_to_the_desktop_move(
    tmp_path: Path,
    town_scan: dict,
    software: str,
    status: str,
    applications_need: str,
) -> None:
    town_scan["findings"].remove(_finding(town_scan, "device_management.windows_desktops_required"))
    html = _html(_report(tmp_path / "desktop", town_scan, f"windows_only_software: {software}"))
    row = readiness_row(html, "windows_software")

    assert f'data-status="{status}"' in row
    desktop = re.search(
        r'<li data-gap="desktop_operating_system" data-need="unknown">.*?</li>', html, re.S
    )
    assert desktop is not None and 'data-reason="answer_not_provided"' in desktop[0]
    assert f'data-gap="windows_applications" data-need="{applications_need}"' in html
    if "vendor_has_web_version: false" in software:
        assert (
            "needs Windows to run, either on staff workstations or on a separate Windows system"
            in row
        )
        assert "move away from Microsoft 365" in row
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
def test_desktop_gap_keeps_its_answer_when_software_counts_disagree(
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
    gap = re.search(r'<li data-gap="desktop_operating_system" data-need="no">.*?</li>', html, re.S)
    assert gap is not None and 'data-provenance="provided"' in gap[0]
    assert 'data-reason="provided_answers_conflict"' not in gap[0]


@pytest.mark.parametrize("profile", ["opendesk", "nextcloud"])
def test_desktop_gap_keeps_a_no_answer_with_windows_only_software(
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
    html = _html(_report(tmp_path / "separate-windows-system", town_scan, answers))

    gap = re.search(r'<li data-gap="desktop_operating_system" data-need="no">.*?</li>', html, re.S)
    assert gap is not None and 'data-provenance="provided"' in gap[0]
    assert "data-reason=" not in gap[0]
    assert "Windows desktops required for applications, devices or peripherals" in gap[0]
    assert "Windows desktops are unnecessary" not in html
    assert 'data-gap="windows_applications" data-need="yes"' in html
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
