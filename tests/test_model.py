# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections.abc import ItemsView
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path
from typing import Never

import pytest

from befund.catalogue import Catalogue, load_catalogue
from befund.errors import InputError
from befund.i18n import error_sentence, load_locale
from befund.model import Coverage, Scan, load_scan, load_scan_text
from befund.parsing import MAX_FILE_BYTES, parse_json, parse_yaml, read_text, reject_at_signs
from befund.report import render_report


@pytest.fixture
def catalogue() -> Catalogue:
    return load_catalogue()


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
        "tool": {"name": "befund", "version": "0.1.0"},
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
            "collected_at": "2026-11-02",
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
    town = files("befund").joinpath("demo", "town", "scan.json")
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
    source = files("befund").joinpath("rules", "findings.yaml")
    bad = tmp_path / "findings.yaml"
    bad.write_text(
        read_text(source).replace("workload: licences", "workload: absent", 1), encoding="utf-8"
    )

    with pytest.raises(InputError) as caught:
        load_catalogue(bad)

    assert (caught.value.file, caught.value.field) == (bad.name, "findings[0].workload")


@pytest.mark.parametrize(
    "target", ["teams.absent", "teams.chat_history_must_be_kept", "teams.teams_with_guests_count"]
)
def test_catalogue_requires_a_distinct_count_as_the_coverage_reference(
    tmp_path: Path, target: str
) -> None:
    source = files("befund").joinpath("rules", "findings.yaml")
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
    assert error.file == "scan.json" and error.field and error.field.startswith("$")
    assert not error.details and address not in error.field
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
    scan_data["findings"][0]["coverage"] = asdict(coverage)
    finding = _load(scan_data, catalogue).finding("directory.user_count")
    assert finding is not None and finding.coverage == coverage


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
@pytest.mark.parametrize("group", ["collectors", "findings", "sku_part_number", "sku_guid"])
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
        if group == "sku_part_number":
            duplicate = {
                **original,
                "sku_part_number": original["sku_part_number"].upper(),
                "sku_guid": "00000000-0000-4000-8000-000000000003",
            }
        else:
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


@pytest.mark.parametrize(
    ("document", "code"),
    [
        ('{"items":[{"first":0,"first":1}]}', "duplicate_key"),
        ('{"items":[NaN]}', "non_finite_number"),
        ('{"items":[Infinity]}', "non_finite_number"),
        ('{"items":[-Infinity]}', "non_finite_number"),
        ('{"items":[1e999]}', "non_finite_number"),
        ('{"items":[}', "invalid_json"),
    ],
)
def test_strict_json_errors_have_structural_paths(document: str, code: str) -> None:
    with pytest.raises(InputError, match=code) as caught:
        parse_json(document, "scan.json")

    assert caught.value.file == "scan.json"
    assert caught.value.field and caught.value.field.startswith("$")
    assert "first" not in caught.value.field and not caught.value.details


@pytest.mark.parametrize(
    ("document", "code"),
    [
        ("items:\n  - {value: 1, value: 2}", "duplicate_key"),
        ("items:\n  - .NaN", "non_finite_number"),
        ("items: .inf", "non_finite_number"),
        ("items: -1.0e+999", "non_finite_number"),
        ("items: [", "invalid_yaml"),
        ("items: &items [*items]", "invalid_yaml"),
        ("defaults: &defaults {value: 1}\nitems: {<<: *defaults}", "invalid_yaml"),
    ],
)
def test_strict_yaml_errors_have_structural_paths(document: str, code: str) -> None:
    with pytest.raises(InputError, match=code) as caught:
        parse_yaml(document, "inputs.yaml")

    assert caught.value.file == "inputs.yaml"
    assert caught.value.field and caught.value.field.startswith("$")
    assert not caught.value.details


def test_strict_yaml_preserves_quoted_text_and_finite_numbers() -> None:
    assert parse_yaml('quoted: "1.00499999999999999"\nfinite: 1.5', "inputs.yaml") == {
        "quoted": "1.00499999999999999",
        "finite": 1.5,
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
    assert all(error.value.field == "$" for error in (missing, directory, encoding))


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
    assert (caught.value.file, caught.value.field) == (path.name, "$")


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
    assert (caught.value.file, caught.value.field) == (path.name, "$")


def test_privacy_walk_checks_each_shared_container_once() -> None:
    class CountedMapping(dict[str, object]):
        visits = 0

        def items(self) -> ItemsView[str, object]:
            self.visits += 1
            return super().items()

    mapping = CountedMapping({"name": "Example"})
    shared = [mapping, mapping]
    reject_at_signs([shared, shared], "manual.yaml")

    assert mapping.visits == 1


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
