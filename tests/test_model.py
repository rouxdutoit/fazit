# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
import sys
from dataclasses import asdict, replace
from importlib.resources import files
from itertools import product
from pathlib import Path
from typing import Never

import pytest
from helpers import ROOT, rebuild_report

from fazit import model
from fazit.catalogue import Catalogue, load_catalogue
from fazit.errors import InputError
from fazit.i18n import error_sentence, load_locale
from fazit.licences import classify_product, licence_findings, load_service_plans
from fazit.model import Coverage, Scan, load_scan, load_scan_text
from fazit.parsing import MAX_FILE_BYTES, parse_json, parse_yaml, read_text
from fazit.report import render_report


def _finding(finding_id: str, **overrides: object) -> dict[str, object]:
    return {
        "id": finding_id,
        "workload": finding_id.split(".", 1)[0],
        "value": 91,
        "unit": "users",
        "provenance": "measured",
        "collector": "directory",
        "source": "sample.directory",
        "collected_at": "2026-11-02T09:00:00Z",
        "period": "2026-05-06/2026-11-01",
        "coverage": {"kind": "complete"},
        "missing_reason": None,
        **overrides,
    }


@pytest.fixture
def scan_data() -> dict:
    return {
        "schema_version": "1.0",
        "tool": {"name": "fazit", "version": "0.1.0"},
        "generated_at": "2026-11-02T09:00:00Z",
        "source_kind": "sample",
        "collectors": [
            {
                "id": "directory",
                "status": "ok",
                "reason": None,
                "permissions_used": ["User.Read.All"],
            },
            {"id": "licences", "status": "ok", "reason": None, "permissions_used": []},
            {"id": "mailbox_usage", "status": "ok", "reason": None, "permissions_used": []},
            {
                "id": "exchange_recipients",
                "status": "skipped",
                "reason": "source_not_supplied",
                "permissions_used": [],
            },
        ],
        "findings": [
            _finding("directory.user_count"),
            _finding(
                "mail.mailbox_count",
                unit="mailboxes",
                collector="mailbox_usage",
                source="sample.mailbox_usage",
            ),
            _finding(
                "mail.shared_mailbox_count",
                value=None,
                unit="mailboxes",
                provenance="unknown",
                collector="exchange_recipients",
                source=None,
                collected_at=None,
                period=None,
                coverage=None,
                missing_reason="needs_recipient_export",
            ),
            _finding(
                "mail.other_systems_send_mail",
                value=False,
                unit=None,
                provenance="provided",
                collector=None,
                source="interview",
                collected_at=None,
                period=None,
                coverage=None,
            ),
        ],
        "licences": {
            "collector": "licences",
            "source": "sample.licences",
            "collected_at": "2026-11-02T09:00:00Z",
            "coverage": {"kind": "complete", "scanned": 1, "failed": 0, "total": 1},
            "products": [
                {
                    "sku_part_number": "sample_SKU",
                    "sku_guid": "00000000-0000-4000-8000-00000000000F",
                    "purchased": 3,
                    "assigned": 2,
                    "service_plans": [
                        {"name": "sample_PLAN", "guid": "00000000-0000-4000-8000-000000000002"}
                    ],
                }
            ],
        },
    }


def _load(data: dict, catalogue: Catalogue) -> Scan:
    return load_scan_text(json.dumps(data), "scan.json", catalogue)


@pytest.mark.parametrize("total", range(1, 4))
@pytest.mark.parametrize("declared", [False, True])
def test_licensed_accounts_fit_exhaustive_directory_observations(
    scan_data: dict, catalogue: Catalogue, total: int, declared: bool
) -> None:
    ceilings: dict[tuple[tuple[int, Coverage], tuple[int, Coverage]], int] = {}
    observations: set[tuple[int, Coverage]] = set()
    for rows in product(("internal", "guest", "other"), repeat=total):
        internal = {(rows.count("internal"), Coverage("complete"))}
        guests = {(rows.count("guest"), Coverage("complete"))}
        for checks in product(("checked", "failed", "pending"), repeat=total):
            observed = [row for row, check in zip(rows, checks, strict=True) if check == "checked"]
            if not observed:
                continue
            for scanned in (len(observed), None):
                for failed in (checks.count("failed"), None):
                    coverage = Coverage("partial", scanned, failed, total)
                    internal.add((observed.count("internal"), coverage))
                    guests.add((observed.count("guest"), coverage))
        observations.update(internal, guests)
        for member, guest in product(internal, guests):
            possible = rows.count("internal") + rows.count("guest")
            ceilings[member, guest] = max(ceilings.get((member, guest), 0), possible)

    if declared:
        scan_data["directory_population"] = {
            "collector": "directory",
            "collected_at": scan_data["generated_at"],
            "coverage": asdict(Coverage("complete", total, 0, total)),
        }
    licensed = _finding("directory.licensed_user_count", period=None)
    for member, guest in product(observations, repeat=2):
        scan_data["findings"] = [
            _finding(
                "directory.user_count", value=member[0], coverage=asdict(member[1]), period=None
            ),
            _finding(
                "directory.guest_count", value=guest[0], coverage=asdict(guest[1]), period=None
            ),
            licensed,
        ]
        if not declared:
            licensed["value"] = 2 * total + 1
            assert _load(scan_data, catalogue).findings[-1].value == licensed["value"]
            continue
        ceiling = ceilings.get((member, guest))
        if ceiling is not None:
            licensed["value"] = ceiling
            assert _load(scan_data, catalogue).findings[-1].value == ceiling
        licensed["value"] = 0 if ceiling is None else ceiling + 1
        with pytest.raises(InputError, match="subset_count_exceeds_population") as caught:
            _load(scan_data, catalogue)
        assert caught.value.field == (
            "findings[1].value" if ceiling is None else "findings[2].value"
        )


def test_complete_filtered_directory_lists_load(scan_data: dict, catalogue: Catalogue) -> None:
    for internal, guests, licensed in product(range(9, 18), repeat=3):
        scan_data["findings"] = [
            _finding(f"directory.{name}_count", value=count, coverage=asdict(coverage), period=None)
            for name, count, coverage in (
                ("user", internal, Coverage("complete", internal, 0, internal)),
                ("guest", guests, Coverage("complete", guests, 0, guests)),
                ("licensed_user", licensed, Coverage("complete")),
            )
        ]
        assert _load(scan_data, catalogue).findings[-1].value == licensed


def test_population_total_applies_only_to_matching_directory_snapshots(
    scan_data: dict, catalogue: Catalogue
) -> None:
    scan_data["directory_population"] = {
        "collector": "directory",
        "collected_at": "2026-11-02T10:00:00+01:00",
        "coverage": asdict(Coverage("complete", 20, 0, 20)),
    }
    finding = scan_data["findings"][0]
    finding.update(value=10, coverage=asdict(Coverage("complete", 10, 0, 10)), period=None)
    with pytest.raises(InputError, match="coverage_total_conflict") as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == "findings[0].coverage.total"

    finding["collected_at"] = "2026-11-02T08:59:59Z"
    scan = _load(scan_data, catalogue)
    assert scan.directory_population.coverage.total == 20
    assert scan.findings[0].coverage.total == 10
    assert scan.dropped_count == 0


@pytest.mark.parametrize(
    ("declared", "observed", "count", "field"),
    [
        (Coverage("partial", 0, 21, 21), Coverage("complete"), 21, "coverage"),
        (Coverage("partial", 1, 20, 21), Coverage("partial"), 2, "value"),
        (Coverage("partial", 1, 20, 21), Coverage("partial", scanned=2), 1, "coverage"),
        (Coverage("partial", failed=20, total=21), Coverage("partial"), 2, "value"),
        (Coverage("unknown", failed=20, total=21), Coverage("complete"), 1, "coverage"),
    ],
)
def test_directory_counts_cannot_exceed_declared_checks(
    scan_data: dict,
    catalogue: Catalogue,
    declared: Coverage,
    observed: Coverage,
    count: int,
    field: str,
) -> None:
    scan_data["directory_population"] = {
        "collector": "directory",
        "collected_at": scan_data["generated_at"],
        "coverage": asdict(declared),
    }
    scan_data["findings"][0].update(value=count, period=None, coverage=asdict(observed))

    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)

    assert caught.value.field == f"findings[0].{field}"


@pytest.mark.parametrize("total", range(1, 5))
def test_joint_directory_counts_fit_declared_checks(
    scan_data: dict, catalogue: Catalogue, total: int
) -> None:
    coverage = asdict(Coverage("partial", total=total))
    scan_data["directory_population"] = {
        "collector": "directory",
        "collected_at": scan_data["generated_at"],
        "coverage": coverage,
    }
    members, guests = (
        _finding(f"directory.{kind}_count", period=None, coverage={"kind": "partial"})
        for kind in ("user", "guest")
    )
    scan_data["findings"] = [members, guests]
    for scanned, failed in product((None, *range(1, total + 1)), (None, *range(total))):
        if (scanned or 0) + (failed or 0) > total:
            continue
        coverage.update(scanned=scanned, failed=failed)
        possible = {
            (roster.count("internal"), roster.count("guest"))
            for roster in product(("internal", "guest", "other", "failed", "pending"), repeat=total)
            if roster.count("failed") == (failed or 0)
            and (scanned is None or roster.count("pending") == total - scanned - (failed or 0))
        }
        limit = max(member for member, _ in possible)
        for counts in product(range(limit + 1), repeat=2):
            members["value"], guests["value"] = counts
            if counts in possible:
                assert tuple(item.value for item in _load(scan_data, catalogue).findings) == counts
            else:
                with pytest.raises(InputError, match="subset_count_exceeds_population") as caught:
                    _load(scan_data, catalogue)
                assert caught.value.field == "findings[1].value"


@pytest.mark.parametrize("scanned", [1, 2])
def test_licensed_accounts_fit_within_successfully_checked_directory_rows(
    scan_data: dict, catalogue: Catalogue, scanned: int
) -> None:
    scan_data["directory_population"] = {
        "collector": "directory",
        "collected_at": scan_data["generated_at"],
        "coverage": asdict(Coverage("partial", scanned, 0, 3)),
    }
    scan_data["findings"] = [
        _finding(
            f"directory.{kind}_count",
            value=value,
            period=None,
            coverage={"kind": "partial", "scanned": 1},
        )
        for kind, value in (("user", 0), ("guest", 0), ("licensed_user", 1))
    ]
    if scanned == 2:
        assert _load(scan_data, catalogue).findings[-1].value == 1
    else:
        with pytest.raises(InputError, match="subset_count_exceeds_population") as caught:
            _load(scan_data, catalogue)
        assert caught.value.field == "findings[2].value"


def test_complete_directory_count_inherits_the_declared_total(
    scan_data: dict, catalogue: Catalogue
) -> None:
    scan_data["directory_population"] = {
        "collector": "directory",
        "collected_at": scan_data["generated_at"],
        "coverage": asdict(Coverage("complete", 2, 0, 2)),
    }
    accounts = _finding(
        "directory.licensed_user_count",
        value=2,
        period=None,
        collected_at="2026-11-02T10:00:00+01:00",
        coverage={"kind": "complete", "scanned": 2, "failed": 0},
    )
    scan_data["findings"][0] = accounts
    assert _load(scan_data, catalogue).findings[0].value == 2

    accounts.update(value=1)
    accounts["coverage"]["scanned"] = 1
    with pytest.raises(InputError, match="invalid_coverage") as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == "findings[0].coverage"

    accounts["coverage"]["scanned"] = 2
    accounts["collected_at"] = "2026-11-02T08:59:59Z"
    with pytest.raises(InputError, match="invalid_coverage") as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == "findings[0].coverage"


@pytest.mark.parametrize(
    ("generated_at", "valid"),
    [
        ("2026-11-06T00:30:00+01:00", True),
        ("2026-11-05T23:30:00Z", True),
        ("2026-11-05T19:30:00-05:00", True),
        ("2026-11-06T00:30:00Z", True),
        ("2026-11-05T10:00:00Z", True),
        ("2026-11-05T09:59:59Z", False),
        ("2026-11-05", True),
        ("2026-11-05T00:30:00+01:00", False),
        ("2026-11-04T23:30:00Z", False),
        ("2026-11-04", True),
        ("2026-11-03", False),
    ],
)
def test_undated_interview_period_is_bounded_by_the_scan(
    scan_data: dict, catalogue: Catalogue, generated_at: str, valid: bool
) -> None:
    scan_data["generated_at"] = generated_at
    period = "2026-11-01/2026-11-06"
    scan_data["findings"][3]["period"] = period
    if valid:
        assert _load(scan_data, catalogue).findings[3].period == period
    else:
        with pytest.raises(InputError, match="period_after_scan") as caught:
            _load(scan_data, catalogue)
        assert caught.value.field == "findings[3].period"


@pytest.mark.parametrize(
    ("collected_at", "valid"),
    [
        ("2026-11-02T00:30:00+01:00", True),
        ("2026-11-01T23:30:00Z", True),
        ("2026-11-01T19:30:00-05:00", True),
        ("2026-11-02T00:30:00Z", True),
        ("2026-11-01T10:00:00Z", True),
        ("2026-11-01T09:59:59Z", False),
        ("2026-11-01", True),
        ("2026-11-01T00:30:00+01:00", False),
        ("2026-10-31T23:30:00Z", False),
        ("2026-10-31", True),
        ("2026-10-30", False),
    ],
)
def test_dated_period_is_bounded_by_collection(
    scan_data: dict, catalogue: Catalogue, collected_at: str, valid: bool
) -> None:
    period = "2026-10-01/2026-11-02"
    scan_data["findings"][1].update(period=period, collected_at=collected_at)
    if valid:
        assert _load(scan_data, catalogue).findings[1].period == period
    else:
        with pytest.raises(InputError, match="period_after_collection") as caught:
            _load(scan_data, catalogue)
        assert caught.value.field == "findings[1].period"


@pytest.mark.parametrize(
    ("generated_at", "valid"),
    [
        ("2026-11-05T00:00:00Z", False),
        ("2026-11-04T19:00:00-05:00", False),
        ("2026-11-05T09:59:59.999999Z", False),
        ("2026-11-05T10:00:00Z", True),
        ("2026-11-06T00:00:00+14:00", True),
        ("2026-11-06T00:30:00+01:00", True),
        ("2026-11-05T23:30:00Z", True),
        ("2026-11-05T18:30:00-05:00", True),
        ("2026-11-06T20:05:00-05:00", True),
        ("2026-11-07T01:05:00Z", True),
        ("2026-11-03", False),
        ("2026-11-04", True),
        ("2026-11-05", True),
    ],
)
def test_date_only_interview_requires_the_day_to_have_started(
    scan_data: dict, catalogue: Catalogue, generated_at: str, valid: bool
) -> None:
    scan_data.update(generated_at=generated_at, findings=[scan_data["findings"][3]], licences=None)
    scan_data["findings"][0]["collected_at"] = "2026-11-06"
    if valid:
        assert _load(scan_data, catalogue).findings[0].collected_at == "2026-11-06"
    else:
        with pytest.raises(InputError, match="collection_after_scan") as caught:
            _load(scan_data, catalogue)
        assert caught.value.field == "findings[0].collected_at"


@pytest.mark.parametrize(
    ("collected_at", "valid"),
    [
        ("2026-11-04T20:00:00-05:00", True),
        ("2026-11-05T12:00:00Z", True),
        ("2026-11-05T12:00:00.000001Z", False),
    ],
)
def test_date_only_scan_ends_at_midnight_utc_minus_twelve(
    scan_data: dict, catalogue: Catalogue, collected_at: str, valid: bool
) -> None:
    interview = scan_data["findings"][3]
    interview["collected_at"] = collected_at
    scan_data.update(generated_at="2026-11-04", findings=[interview], licences=None)
    if valid:
        assert _load(scan_data, catalogue).findings[0].collected_at == collected_at
    else:
        with pytest.raises(InputError, match="collection_after_scan") as caught:
            _load(scan_data, catalogue)
        assert caught.value.field == "findings[0].collected_at"


def test_period_end_must_fit_both_collection_and_scan(
    scan_data: dict, catalogue: Catalogue
) -> None:
    scan_data["generated_at"] = "2026-11-02T10:00:00Z"
    observation = scan_data["findings"][1]
    observation.update(collected_at="2026-11-03", period="2026-10-01/2026-11-03")
    assert _load(scan_data, catalogue).findings[1].collected_at == "2026-11-03"

    observation["period"] = "2026-10-01/2026-11-04"
    with pytest.raises(InputError, match="period_after_scan") as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == "findings[1].period"


@pytest.mark.parametrize(
    ("field", "value"),
    [("collected_at", "2026-11-01"), ("period", "2026-05-07/2026-11-01")],
)
def test_unknown_findings_may_omit_source_dates_but_cannot_contradict_them(
    scan_data: dict, catalogue: Catalogue, field: str, value: str
) -> None:
    missing = _finding(
        "directory.group_count",
        unit="groups",
        provenance="unknown",
        value=None,
        missing_reason="not_in_export",
        collected_at=None,
        period=None,
        coverage=None,
    )
    scan_data["findings"] = [scan_data["findings"][0], missing]
    assert _load(scan_data, catalogue).findings[1].provenance == "unknown"

    missing[field] = value
    with pytest.raises(InputError, match=f"{field}_conflict") as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == f"findings[1].{field}"


def test_dated_active_users_headcount_is_independent_of_the_directory_snapshot(
    catalogue: Catalogue,
) -> None:
    sample = files("fazit").joinpath("demo", "nonprofit", "scan.json")
    data = json.loads(read_text(sample))
    source = "import.active_users"
    key = "directory.licensed_user_count"
    catalogue = replace(
        catalogue,
        source_codes=catalogue.source_codes | {source},
        findings=tuple(
            replace(entry, measured_by=entry.measured_by | {("directory", source)})
            if entry.id == key
            else entry
            for entry in catalogue.findings
        ),
    )
    accounts = next(row for row in data["findings"] if row["id"] == key)
    accounts.update(
        source=source,
        collected_at="2026-11-04",
        period="2026-11-04/2026-11-04",
        coverage=asdict(Coverage("unknown", scanned=21, failed=0)),
    )
    scan = _load(data, catalogue)
    assert scan.finding(key).value == 20
    assert not scan.directory_population.includes(scan.finding(key))
    derived = {
        row.id: row for row in licence_findings(scan, load_service_plans(catalogue), catalogue)
    }
    assert derived["licences.product_count"].missing_reason == "licence_directory_unverified"
    assert derived["telephony.licence_add_on_assigned"].value is None
    assert derived["small_apps.licence_bundled_assigned"].value is True


@pytest.mark.parametrize("content", ["sharepoint.file_count", "sharepoint.storage_bytes"])
def test_empty_sharepoint_export_cannot_have_content(catalogue: Catalogue, content: str) -> None:
    town = files("fazit").joinpath("demo", "town", "scan.json")
    data = json.loads(read_text(town))
    findings = {row["id"]: (index, row) for index, row in enumerate(data["findings"])}
    for finding_id in (
        "sharepoint.site_count",
        "sharepoint.file_count",
        "sharepoint.storage_bytes",
    ):
        findings[finding_id][1]["value"] = 0
    assert _load(data, catalogue).finding(content).value == 0

    index, row = findings[content]
    row["value"] = 1
    with pytest.raises(InputError, match="content_without_population") as caught:
        _load(data, catalogue)
    assert caught.value.field == f"findings[{index}].value"

    row["period"] = "2026-05-01/2026-11-01"
    data["findings"].append(data["findings"].pop(index))
    with pytest.raises(InputError, match="period_conflict") as caught:
        _load(data, catalogue)
    assert caught.value.field == f"findings[{len(data['findings']) - 1}].period"


def test_catalogue_and_town_sample_agree(catalogue: Catalogue) -> None:
    assert catalogue.workload_ids == (
        "licences",
        "directory",
        "mail",
        "onedrive",
        "sharepoint",
        "teams",
        "office_files",
        "device_management",
        "windows_software",
        "power_platform",
        "telephony",
        "identity_access",
        "security_compliance",
        "small_apps",
        "integrations",
    )
    town = files("fazit").joinpath("demo", "town", "scan.json")
    scan = load_scan_text(read_text(town), town.name, catalogue)

    assert tuple(finding.id for finding in scan.findings) == tuple(
        entry.id for entry in catalogue.findings
    )
    assert scan.dropped_count == 0
    assert scan.licences is not None and len(scan.licences.products) == 3
    for finding_id, expected in (
        ("directory.user_count", 91),
        ("directory.licensed_user_count", 85),
        ("directory.guest_count", 12),
        ("teams.teams_with_guests_count", 0),
        ("device_management.device_count", 92),
    ):
        finding = scan.finding(finding_id)
        assert finding is not None and finding.value == expected


def test_catalogue_refuses_an_unlisted_workload(tmp_path: Path) -> None:
    source = files("fazit").joinpath("rules", "findings.yaml")
    bad = tmp_path / "findings.yaml"
    bad.write_text(
        read_text(source).replace("workload: licences", "workload: absent", 1), encoding="utf-8"
    )

    with pytest.raises(InputError) as caught:
        load_catalogue(bad)

    assert (caught.value.file, caught.value.field) == (bad.name, "findings[0].workload")


@pytest.mark.parametrize(
    ("before", "after", "field", "code"),
    [
        ("    category: communication\n", "", "workloads[2].category", "missing_field"),
        ("category: communication", "category: absent", "workloads[2].category", "invalid_code"),
        (
            "assessed: false",
            "assessed: false\n    category: communication",
            "workloads[0].category",
            "invalid_field",
        ),
        ("assessed: false", 'assessed: "false"', "workloads[0].assessed", "invalid_field"),
        (
            "    label: category.security",
            "    label: category.security\n  - id: unused\n    label: category.unused",
            "categories[5].id",
            "invalid_field",
        ),
        ("  - id: security\n", "  - id: files\n", "categories[4].id", "duplicate_id"),
    ],
)
def test_catalogue_rejects_invalid_workload_categories(
    tmp_path: Path, before: str, after: str, field: str, code: str
) -> None:
    source = files("fazit").joinpath("rules", "findings.yaml")
    path = tmp_path / source.name
    path.write_text(read_text(source).replace(before, after, 1), encoding="utf-8")

    with pytest.raises(InputError, match=code) as caught:
        load_catalogue(path)

    assert (caught.value.file, caught.value.field) == (path.name, field)


@pytest.mark.parametrize(
    "owner", [None, "unregistered"], ids=["missing-owner", "unregistered-owner"]
)
def test_catalogue_requires_a_registered_finding_owner(tmp_path: Path, owner: str | None) -> None:
    source = files("fazit").joinpath("rules", "findings.yaml")
    path = tmp_path / source.name
    update = "" if owner is None else f"    owner: {owner}\n"
    path.write_text(
        read_text(source).replace("    owner: procurement\n", update, 1), encoding="utf-8"
    )

    with pytest.raises(InputError) as caught:
        load_catalogue(path)

    assert (caught.value.file, caught.value.field) == (
        path.name,
        "findings.licences.contract_terms_known.owner",
    )


@pytest.mark.parametrize(
    "target", ["teams.absent", "teams.chat_history_must_be_kept", "teams.teams_with_guests_count"]
)
def test_catalogue_requires_a_distinct_count_as_the_coverage_reference(
    tmp_path: Path, target: str
) -> None:
    source = files("fazit").joinpath("rules", "findings.yaml")
    bad = tmp_path / "findings.yaml"
    bad.write_text(
        read_text(source).replace(
            "coverage_total_from: teams.team_count", f"coverage_total_from: {target}"
        ),
        encoding="utf-8",
    )

    with pytest.raises(InputError) as caught:
        load_catalogue(bad)

    assert caught.value.file == bad.name
    assert caught.value.field and caught.value.field.endswith(".coverage_total_from")


def test_scan_counts_ignored_fields_and_findings_without_keeping_names(
    scan_data: dict, catalogue: Catalogue
) -> None:
    scan_data["operator"] = "Example Person"
    scan_data["organisation"] = {"display_name": "Example Organisation"}
    scan_data["tool"]["token"] = "planted-token"
    scan_data["collectors"][0]["owner"] = "Example Person"
    scan_data["findings"][0]["one_person"] = "Example Person"
    scan_data["findings"][0]["coverage"]["one_row"] = "Example Person"
    scan_data["findings"].append({"id": "directory.future_finding", "value": "Example Person"})
    scan_data["licences"]["extra_licence_field"] = "Example Person"
    scan_data["licences"]["products"][0]["credential"] = "planted-token"
    scan_data["licences"]["products"][0]["service_plans"][0]["person"] = "Example Person"

    scan = _load(scan_data, catalogue)
    html = render_report(scan, lang="en", catalogue=catalogue)
    model = json.dumps(asdict(scan))

    assert scan.dropped_count == 10
    assert scan.finding("directory.future_finding") is None
    assert 'data-ignored-count="10"' in html
    for text in (
        "operator",
        "Example Person",
        "Example Organisation",
        "planted-token",
        "future_finding",
    ):
        assert text not in html and text not in model


@pytest.mark.parametrize("location", ["key", "value"])
def test_scan_refuses_contact_text_before_dropping_unknown_data(
    scan_data: dict, catalogue: Catalogue, location: str
) -> None:
    address = "erika.mustermann@musterstadt.example"
    scan_data["ignored"] = [{address: 1} if location == "key" else {"contact": address}]

    with pytest.raises(InputError, match="contains_at") as caught:
        _load(scan_data, catalogue)

    error = caught.value
    assert error.file == "scan.json" and error.field is None and not error.details
    assert address not in error_sentence(load_locale("en"), error)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", "https://example.invalid/token"),
        ("source", "sample custom"),
        ("source", "sample.unsupported"),
        ("unit", "unknown_unit"),
        ("workload", "mail"),
        ("coverage", {"kind": "unused"}),
        ("collected_at", "2026-02-30"),
        ("period", "2026-11-01/2026-05-01"),
        ("provenance", "planted_text"),
        ("value", True),
        ("value", "91"),
        ("value", 1.5),
        ("value", -1),
        ("value", None),
        ("coverage", None),
        ("source", None),
        ("collected_at", None),
    ],
)
def test_finding_checks_catalogue_codes_and_required_evidence(
    scan_data: dict, catalogue: Catalogue, field: str, value: object
) -> None:
    scan_data["findings"][0][field] = value

    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)

    assert caught.value.field in {f"findings[0].{field}", f"findings[0].{field}.kind"}
    assert not caught.value.details


@pytest.mark.parametrize("reason", ["unsupported_reason", "Example Person had a problem", None])
def test_unknown_finding_requires_registered_reason(
    scan_data: dict, catalogue: Catalogue, reason: str | None
) -> None:
    scan_data["findings"][2]["missing_reason"] = reason

    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)

    assert caught.value.field == "findings[2].missing_reason"
    assert not caught.value.details


@pytest.mark.parametrize(
    ("field", "value", "expected_field"),
    [
        ("id", "DIRECTORY", "collectors[3].id"),
        ("reason", "A sentence about someone", "collectors[3].reason"),
        ("reason", "unsupported_reason", "collectors[3].reason"),
        ("reason", None, "collectors[3].reason"),
        ("permissions_used", ["Example.Person"], "collectors[3].permissions_used[0]"),
    ],
)
def test_collector_requires_known_codes(
    scan_data: dict, catalogue: Catalogue, field: str, value: object, expected_field: str
) -> None:
    scan_data["collectors"][3][field] = value

    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)

    assert caught.value.field == expected_field


@pytest.mark.parametrize("collector", [None, "absent", "exchange_recipients"])
def test_measured_finding_requires_a_collector_that_ran(
    scan_data: dict, catalogue: Catalogue, collector: str | None
) -> None:
    scan_data["findings"][0]["collector"] = collector
    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == "findings[0].collector"


def test_missing_finding_field_names_that_field(scan_data: dict, catalogue: Catalogue) -> None:
    del scan_data["findings"][0]["collector"]
    with pytest.raises(InputError, match="missing_field") as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == "findings[0].collector"


def test_separate_mail_collectors_preserve_their_states(
    scan_data: dict, catalogue: Catalogue
) -> None:
    scan = _load(scan_data, catalogue)
    measured = scan.finding("mail.mailbox_count")
    unknown = scan.finding("mail.shared_mailbox_count")

    assert measured is not None and measured.collector == "mailbox_usage"
    assert unknown is not None and unknown.collector == "exchange_recipients"
    mailbox_usage = scan.collector(measured.collector)
    recipients = scan.collector(unknown.collector)
    assert mailbox_usage is not None and mailbox_usage.status == "ok"
    assert recipients is not None and recipients.status == "skipped"


@pytest.mark.parametrize("value", [True, False])
def test_provided_boolean_allows_a_missing_date(
    scan_data: dict, catalogue: Catalogue, value: bool
) -> None:
    scan_data["findings"][3]["value"] = value
    supplied = _load(scan_data, catalogue).finding("mail.other_systems_send_mail")

    assert supplied is not None and supplied.value is value and supplied.collected_at is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("value", "true"),
        ("value", 1),
        ("collector", "mailbox_usage"),
        ("source", "sample.mailbox_usage"),
        ("coverage", {"kind": "complete"}),
    ],
)
def test_provided_finding_refuses_wrong_type_or_collector_evidence(
    scan_data: dict, catalogue: Catalogue, field: str, value: object
) -> None:
    scan_data["findings"][3][field] = value
    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == f"findings[3].{field}"


@pytest.mark.parametrize(
    "coverage",
    [
        {"kind": "partial", "scanned": -1},
        {"kind": "partial", "scanned": True},
        {"kind": "partial", "scanned": 18, "failed": 3, "total": 20},
        {"kind": "unknown", "failed": 21, "total": 20},
        {"kind": "complete", "scanned": 18, "failed": 0, "total": 20},
        {"kind": "complete", "scanned": 18, "failed": 2, "total": 20},
        {"kind": "complete", "total": 20},
    ],
)
def test_coverage_rejects_inconsistent_counts(
    scan_data: dict, catalogue: Catalogue, coverage: dict
) -> None:
    scan_data["findings"][0]["coverage"] = coverage
    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)
    assert caught.value.field and caught.value.field.startswith("findings[0].coverage")


@pytest.mark.parametrize(
    "coverage",
    [
        Coverage("complete"),
        Coverage("complete", 20, 0, 20),
        Coverage("partial", 18, 2, 20),
        Coverage("partial", scanned=18),
        Coverage("unknown"),
    ],
)
def test_coverage_preserves_supplied_counts(
    scan_data: dict, catalogue: Catalogue, coverage: Coverage
) -> None:
    scan_data["findings"][0].update(value=18, coverage=asdict(coverage))
    finding = _load(scan_data, catalogue).finding("directory.user_count")
    assert finding is not None and finding.coverage == coverage and finding.value == 18


def test_licences_preserve_identifiers_counts_and_service_plans(
    scan_data: dict, catalogue: Catalogue
) -> None:
    licences = _load(scan_data, catalogue).licences
    assert licences is not None and licences.collector == "licences"
    assert licences.coverage == Coverage("complete", 1, 0, 1)
    (product,) = licences.products
    (plan,) = product.service_plans
    assert (product.sku_part_number, product.sku_guid[-1]) == ("sample_SKU", "f")
    assert (product.purchased, product.assigned) == (3, 2)
    assert (plan.name, plan.guid) == ("sample_PLAN", "00000000-0000-4000-8000-000000000002")
    scan_data["licences"] = None
    assert _load(scan_data, catalogue).licences is None


@pytest.mark.parametrize("missing_guid", [None, "sku", "plan-omitted", "plan-null"])
def test_microsoft_licence_reference_loads(
    scan_data: dict, catalogue: Catalogue, missing_guid: str | None
) -> None:
    path = Path(__file__).with_name("fixtures") / "microsoft_licence_reference.json"
    reference = json.loads(path.read_text(encoding="utf-8"))
    assert len({guid.strip().lower() for _, guid, _ in reference["products"]}) == 620
    plans = load_service_plans(catalogue)
    if missing_guid is not None:
        scan_data["licences"]["coverage"].update(kind="partial", total=2)
    (product_row,) = scan_data["licences"]["products"]
    for part_number, guid, indices in reference["products"]:
        service_plans = [tuple(reference["plans"][index]) for index in indices]
        product_row.update(
            sku_part_number=part_number,
            sku_guid=guid,
            service_plans=[{"name": name, "guid": plan_guid} for name, plan_guid in service_plans],
        )
        if missing_guid == "sku":
            del product_row["sku_guid"]
        elif missing_guid is not None:
            for plan in product_row["service_plans"]:
                if missing_guid == "plan-omitted":
                    del plan["guid"]
                else:
                    plan["guid"] = None
        scan = _load(scan_data, catalogue)
        (loaded,) = scan.licences.products
        assert loaded.sku_part_number == part_number
        assert loaded.sku_guid == (None if missing_guid == "sku" else guid.strip().lower())
        assert [(plan.name, plan.guid) for plan in loaded.service_plans] == [
            (name, None if missing_guid in {"plan-omitted", "plan-null"} else plan_guid.lower())
            for name, plan_guid in service_plans
        ]
        assert (loaded.purchased, loaded.assigned) == (3, 2)
        if missing_guid is not None:
            assert all(match is None for match in classify_product(loaded, plans))
        assert licence_findings(scan, plans, catalogue)[0].value == 1


@pytest.mark.parametrize("coverage", [Coverage("complete"), Coverage("complete", 0, 0, 0)])
def test_complete_licences_require_coverage_for_all_listed_products(
    scan_data: dict, catalogue: Catalogue, coverage: Coverage
) -> None:
    scan_data["licences"]["coverage"] = asdict(coverage)
    with pytest.raises(InputError, match="invalid_licence_coverage") as caught:
        _load(scan_data, catalogue)
    assert (caught.value.file, caught.value.field) == ("scan.json", "licences.coverage")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sku_part_number", "product name"),
        ("sku_guid", "not-a-guid"),
        ("assigned", -1),
        ("purchased", True),
    ],
)
def test_licences_check_product_fields(
    scan_data: dict, catalogue: Catalogue, field: str, value: object
) -> None:
    scan_data["licences"]["products"][0][field] = value
    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == f"licences.products[0].{field}"


@pytest.mark.parametrize(("field", "value"), [("name", "plan name"), ("guid", "not-a-guid")])
def test_licences_check_service_plan_fields(
    scan_data: dict, catalogue: Catalogue, field: str, value: str
) -> None:
    scan_data["licences"]["products"][0]["service_plans"][0][field] = value
    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == f"licences.products[0].service_plans[0].{field}"


@pytest.mark.parametrize("failure", ["wrong_collector", "absent", "skipped"])
def test_licences_require_the_licences_collector_to_have_run(
    scan_data: dict, catalogue: Catalogue, failure: str
) -> None:
    if failure == "wrong_collector":
        scan_data["licences"]["collector"] = "directory"
    elif failure == "absent":
        del scan_data["collectors"][1]
    else:
        scan_data["collectors"][1].update(status="skipped", reason="permission_denied")

    with pytest.raises(InputError) as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == "licences.collector"


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("group", ["collectors", "findings", "sku_guid"])
def test_duplicate_ids_fail_regardless_of_order(
    scan_data: dict, catalogue: Catalogue, reverse: bool, group: str
) -> None:
    if group == "collectors":
        original = scan_data[group][0]
        duplicate = {**original, "status": "partial", "reason": "not_in_export"}
        scope = "collectors[1].id"
        rows = scan_data[group]
    elif group == "findings":
        original = scan_data[group][0]
        duplicate = {**original, "value": 42}
        scope = "findings[1].id"
        rows = scan_data[group]
    else:
        rows = scan_data["licences"]["products"]
        original = rows[0]
        duplicate = {
            **original,
            "sku_part_number": "OTHER",
            "sku_guid": original["sku_guid"].lower(),
        }
        scope = f"licences.products[1].{group}"
    rows[:1] = [duplicate, original] if reverse else [original, duplicate]

    with pytest.raises(InputError, match="duplicate_id") as caught:
        _load(scan_data, catalogue)
    assert caught.value.field == scope


def test_schema_version_support_and_additive_compatibility(
    scan_data: dict, catalogue: Catalogue
) -> None:
    scan_data.update(schema_version="1.7", future_field="unknown")
    compatible = _load(scan_data, catalogue)
    assert compatible.schema_version == "1.7" and compatible.dropped_count == 1

    scan_data["schema_version"] = "2.0"
    with pytest.raises(InputError, match="schema_version") as caught:
        _load(scan_data, catalogue)
    sentence = error_sentence(load_locale("en"), caught.value)
    assert all(text in sentence for text in ("scan.json", "schema_version", "2.0", "1.x"))
    assert caught.value.field == "schema_version"


def test_scan_format_document_matches_the_loader(tmp_path: Path, catalogue: Catalogue) -> None:
    document = ROOT / "docs" / "scan-format.md"
    assert document.is_file()
    text = read_text(document)
    (example,) = re.findall(r"^```json\n(.*?)^```$", text, re.M | re.S)
    scan = load_scan_text(example, "scan.json", catalogue)
    assert not scan.is_sample

    names = set(re.findall(r"`([^`\n]+)`", text))
    required = {
        *model._SCAN_FIELDS,
        *model._SCAN_OPTIONAL,
        *model._TOOL_FIELDS,
        *model._FINDING_FIELDS,
        *model._COLLECTOR_REQUIRED,
        *model._COLLECTOR_OPTIONAL,
        "kind",
        *model._COVERAGE_COUNTS,
        *model._DIRECTORY_POPULATION_FIELDS,
        *model._LICENCE_FIELDS,
        *model._PRODUCT_REQUIRED,
        *model._PRODUCT_OPTIONAL,
        *model._SERVICE_PLAN_FIELDS,
        *model.SOURCE_KINDS,
        *model.COLLECTOR_STATUSES,
        *model.PROVENANCES,
        *model.COVERAGE_KINDS,
    }
    assert required <= names, sorted(required - names)
    assert "D31" in text and "findings.yaml" in text

    source = tmp_path / "scan.json"
    source.write_text(example, encoding="utf-8")
    html = rebuild_report(source, tmp_path / "out", "en")
    assert 'data-finding="telephony.in_use" data-provenance="provided"' in html


@pytest.mark.parametrize(
    ("document", "code", "line"),
    [
        ('{"items":[{"first":0,\n"first":1}]}', "duplicate_key_document", None),
        ('{"items":[\nNaN]}', "non_finite_number_document", None),
        ('{"items":[Infinity]}', "non_finite_number_document", None),
        ('{"items":[-Infinity]}', "non_finite_number_document", None),
        ('{"items":[1e999]}', "non_finite_number_document", None),
        ('{"items":[\n}', "invalid_json", 2),
    ],
)
def test_strict_json_errors_report_only_available_positions(
    document: str, code: str, line: int | None
) -> None:
    with pytest.raises(InputError, match=code) as caught:
        parse_json(document, "scan.json")

    assert caught.value.file == "scan.json"
    assert caught.value.line == line
    assert caught.value.field is None and not caught.value.details


def test_deeply_nested_scan_input_errors_remain_localised(catalogue: Catalogue) -> None:
    limit = sys.getrecursionlimit()
    for depth in range(limit - 100, limit + 1):
        with pytest.raises(InputError, match="invalid_json|invalid_field"):
            load_scan_text("[" * depth + "0" + "]" * depth, "scan.json", catalogue)


@pytest.mark.parametrize(
    ("document", "code", "line"),
    [
        ("items:\n  - {value: 1, value: 2}", "duplicate_key", 2),
        ("items:\n  - .NaN", "non_finite_number", 2),
        ("items: .inf", "non_finite_number", 1),
        ("items: -1.0e+999", "non_finite_number", 1),
        ("items: [", "invalid_yaml", 1),
        ("items: &items [*items]", "invalid_yaml", 1),
        ("defaults: &defaults {value: 1}\nitems: {<<: *defaults}", "invalid_yaml", 2),
    ],
)
def test_strict_yaml_errors_locate_unknown_fields_by_line(
    document: str, code: str, line: int
) -> None:
    with pytest.raises(InputError, match=code) as caught:
        parse_yaml(document, "inputs.yaml")

    assert caught.value.file == "inputs.yaml"
    assert caught.value.line == line
    assert caught.value.field is None and not caught.value.details


def test_strict_yaml_preserves_quoted_text_and_finite_numbers() -> None:
    assert parse_yaml('quoted: "1.00499999999999999"\nfinite: 1:02.5', "inputs.yaml") == {
        "quoted": "1.00499999999999999",
        "finite": 62.5,
    }


def test_load_scan_reads_utf8_without_normalising_newlines(
    tmp_path: Path, scan_data: dict, catalogue: Catalogue
) -> None:
    path = tmp_path / "scan.json"
    text = json.dumps(scan_data) + "\r\n"
    path.write_bytes(text.encode("utf-8"))

    assert read_text(path) == text
    assert load_scan(path, catalogue) == _load(scan_data, catalogue)


def test_read_text_maps_absent_directory_and_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "scan.json"
    with pytest.raises(InputError, match="file_not_found") as missing:
        read_text(path)
    with pytest.raises(InputError, match="is_directory") as directory:
        read_text(tmp_path)
    path.write_bytes(b"\xff")
    with pytest.raises(InputError, match="not_utf8") as encoding:
        read_text(path)

    assert missing.value.file == encoding.value.file == path.name
    assert directory.value.file == tmp_path.name
    assert all(error.value.field is None for error in (missing, directory, encoding))


def test_read_text_maps_unreadable_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "scan.json"
    path.touch()

    def refuse_read(self: Path, mode: str) -> Never:
        assert self == path
        assert mode == "rb"
        raise PermissionError

    monkeypatch.setattr(Path, "open", refuse_read)
    with pytest.raises(InputError, match="not_readable") as caught:
        read_text(path)
    assert (caught.value.file, caught.value.field) == (path.name, None)


def test_read_text_checks_size_before_opening(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "scan.json"
    path.write_bytes(b" " * MAX_FILE_BYTES)
    assert len(read_text(path)) == MAX_FILE_BYTES
    with path.open("ab") as stream:
        stream.write(b" ")

    def unexpected_open(self: Path, mode: str) -> Never:
        raise AssertionError(f"Opened oversized file {self} in {mode}")

    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", unexpected_open)
        with pytest.raises(InputError, match="file_too_large") as caught:
            read_text(path)
    assert (caught.value.file, caught.value.field) == (path.name, None)


def test_report_shows_finding_evidence_and_collector_details(
    scan_data: dict, catalogue: Catalogue
) -> None:
    scan = _load(scan_data, catalogue)
    html = render_report(scan, lang="en", catalogue=catalogue)
    rows = dict(re.findall(r'<tr data-finding="([^"]+)"[^>]*>(.*?)</tr>', html, re.S))
    strings = load_locale("en")

    assert rows.keys() == {finding.id for finding in scan.findings}
    assert all(
        text in rows["directory.user_count"]
        for text in (
            "91",
            strings["units"]["users"],
            strings["provenance"]["measured"],
            strings["collector"]["directory"],
            strings["source"]["sample.directory"],
            strings["coverage"]["complete"],
        )
    )
    assert all(
        text in rows["mail.shared_mailbox_count"]
        for text in (
            strings["provenance"]["unknown"],
            strings["collector"]["exchange_recipients"],
            *strings["reason"]["needs_recipient_export"].values(),
        )
    )
    assert strings["common"]["date_not_supplied"] in rows["mail.other_systems_send_mail"]
    appendix = html.split('data-section="appendix"')[1]
    assert all(f'data-collector="{collector.id}"' in appendix for collector in scan.collectors)
    assert all(
        text in appendix
        for text in (
            strings["collector_status"]["skipped"],
            strings["reason"]["source_not_supplied"]["label"],
            "User.Read.All",
            scan.schema_version,
            scan.tool.version,
        )
    )
