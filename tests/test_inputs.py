# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import fields, replace
from decimal import Decimal
from html import unescape
from importlib.resources import files
from pathlib import Path

import pytest

from befund.catalogue import Catalogue, load_catalogue
from befund.errors import InputError
from befund.i18n import error_sentence, load_locale
from befund.inputs import (
    CurrentCosts,
    ScenarioInputs,
    WindowsSoftware,
    combine,
    empty_inputs,
    load_inputs,
    load_inputs_text,
    provided_findings,
)
from befund.model import Coverage, load_scan_text
from befund.parsing import parse_yaml, read_text
from befund.report import render_report
from befund.rules import load_risky_file_types, load_status_rules

COUNT_ID = "office_files.kind.macro"
BOOLEAN_ID = "onedrive.external_sharing_in_use"
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def catalogue() -> Catalogue:
    return load_catalogue()


def test_empty_inputs(catalogue: Catalogue) -> None:
    inputs = load_inputs_text("", "inputs.yaml", catalogue)

    assert inputs == empty_inputs()
    assert inputs.organisation_name is None
    assert inputs.currency is inputs.language is inputs.target_profile is inputs.as_of is None
    assert inputs.amounts_are_invented is False
    assert inputs.current_costs.microsoft_licences_per_year is None
    assert inputs.partial_exit.users is inputs.full_exit.users is None
    assert inputs.windows_only_software is None
    assert provided_findings(inputs, catalogue) == ()


@pytest.mark.parametrize(
    ("text", "code", "field"),
    [
        ("[]", "invalid_field", "$"),
        ("curency: EUR", "unknown_field", "curency"),
        ("current_costs: {annual: null}", "unknown_field", "current_costs.annual"),
        (
            "target_costs: {full_exit: {user_count: null}}",
            "unknown_field",
            "target_costs.full_exit.user_count",
        ),
        (
            "target_costs: {hosting_per_user_per_month: null}",
            "unknown_field",
            "target_costs.hosting_per_user_per_month",
        ),
        ("currency: EUR\ncurrency: CHF", "duplicate_key", "$[1]"),
        ("current_costs: {other_it_per_year: .inf}", "non_finite_number", "$[0][0]"),
        ("organisation_name: private@example.test", "contains_at", "$[0]"),
        ("private@example.test: null", "contains_at", "$[0]"),
        ("currency: eur", "invalid_field", "currency"),
        ("language: fr", "unsupported_language", "language"),
        ("target_profile: other", "unsupported_profile", "target_profile"),
        ("as_of: yesterday", "invalid_field", "as_of"),
        ('as_of: "2026-02-30"', "invalid_field", "as_of"),
        ('as_of: "20261121"', "invalid_field", "as_of"),
        ('current_costs: {other_it_per_year: "0"}', "missing_field", "currency"),
        (
            'current_costs: {other_it_per_year: "-1"}',
            "invalid_field",
            "current_costs.other_it_per_year",
        ),
        (
            'current_costs: {other_it_per_year: "many"}',
            "invalid_field",
            "current_costs.other_it_per_year",
        ),
        (
            'current_costs: {other_it_per_year: "NaN"}',
            "invalid_field",
            "current_costs.other_it_per_year",
        ),
        (
            "target_costs: {partial_exit: {hosting_per_user_per_month: 8.5}}",
            "money_not_quoted",
            "target_costs.partial_exit.hosting_per_user_per_month",
        ),
        (
            "current_costs: {other_it_per_year: 08}",
            "money_not_quoted",
            "current_costs.other_it_per_year",
        ),
        (
            "current_costs: {other_it_per_year: !!str 8.5}",
            "money_not_quoted",
            "current_costs.other_it_per_year",
        ),
        (
            "current_costs:\n  other_it_per_year: |-\n    8.5",
            "money_not_quoted",
            "current_costs.other_it_per_year",
        ),
        (
            "current_costs: {other_it_per_year: private@example.test}",
            "contains_at",
            "current_costs.other_it_per_year",
        ),
        (
            "target_costs: {partial_exit: {parallel_running_months: 61}}",
            "invalid_field",
            "target_costs.partial_exit.parallel_running_months",
        ),
        (
            "target_costs: {full_exit: {users: 1.5}}",
            "invalid_field",
            "target_costs.full_exit.users",
        ),
        (
            "target_costs: {full_exit: {training_days_per_person: 1.5}}",
            "money_not_quoted",
            "target_costs.full_exit.training_days_per_person",
        ),
        (f"provided_counts: {{{BOOLEAN_ID}: 1}}", "unknown_field", f"provided_counts.{BOOLEAN_ID}"),
        (f"confirmations: {{{COUNT_ID}: false}}", "unknown_field", f"confirmations.{COUNT_ID}"),
        (f"provided_counts: {{{COUNT_ID}: true}}", "invalid_field", f"provided_counts.{COUNT_ID}"),
        (f"provided_counts: {{{COUNT_ID}: -1}}", "invalid_field", f"provided_counts.{COUNT_ID}"),
        (f"confirmations: {{{BOOLEAN_ID}: 1}}", "invalid_field", f"confirmations.{BOOLEAN_ID}"),
        (
            "windows_only_software: [{name: Editor, users: false}]",
            "invalid_field",
            "windows_only_software[0].users",
        ),
        ("windows_only_software: [{}]", "missing_field", "windows_only_software[0].name"),
    ],
)
def test_invalid_inputs(catalogue: Catalogue, text: str, code: str, field: str) -> None:
    with pytest.raises(InputError) as caught:
        load_inputs_text(text, "manual.yaml", catalogue)

    error = caught.value
    assert (error.code, error.file, error.field) == (code, "manual.yaml", field)
    sentence = error_sentence(load_locale("en"), error)
    assert "manual.yaml" in sentence and field in sentence
    assert "private@example.test" not in sentence


@pytest.mark.parametrize("name", ['""', '"   "', f'"{"x" * 81}"', '"Two\\nLines"'])
def test_software_name_is_short_and_on_one_line(catalogue: Catalogue, name: str) -> None:
    with pytest.raises(InputError) as caught:
        load_inputs_text(f"windows_only_software: [{{name: {name}}}]", "inputs.yaml", catalogue)
    assert caught.value.field == "windows_only_software[0].name"


def test_exact_cost_values(catalogue: Catalogue, tmp_path: Path) -> None:
    path = tmp_path / "manual.yaml"
    path.write_text(
        """currency: EUR
as_of: 2026-11-20
current_costs: {microsoft_licences_per_year: '1.00499999999999999', other_it_per_year: '0'}
target_costs:
  partial_exit: {users: 10, parallel_running_months: 60, training_days_per_person: "1.25"}
  full_exit: {users: 20, parallel_running_months: 0, training_days_per_person: 2}
""",
        encoding="utf-8",
    )

    inputs = load_inputs(path, catalogue)

    assert inputs.as_of == "2026-11-20"
    assert inputs.current_costs.microsoft_licences_per_year == Decimal("1.00499999999999999")
    assert inputs.current_costs.other_it_per_year == Decimal("0")
    assert inputs.partial_exit.parallel_running_months == 60
    assert inputs.full_exit.parallel_running_months == 0
    assert inputs.partial_exit.training_days_per_person == Decimal("1.25")
    assert inputs.full_exit.training_days_per_person == Decimal("2")


def test_input_file_must_be_utf8(catalogue: Catalogue, tmp_path: Path) -> None:
    path = tmp_path / "manual.yaml"
    path.write_bytes(b"\xff")
    with pytest.raises(InputError) as caught:
        load_inputs(path, catalogue)
    assert caught.value.code == "not_utf8"


@pytest.mark.parametrize("as_of", [None, "2026-11-20"])
def test_supplied_answers_have_their_own_source_and_date(
    catalogue: Catalogue, as_of: str | None
) -> None:
    text = f"""as_of: {as_of or "null"}
provided_counts:
  {COUNT_ID}: 0
  office_files.kind.access: null
confirmations:
  {BOOLEAN_ID}: false
"""
    inputs = load_inputs_text(text, "field-notes.yaml", catalogue)

    findings = {finding.id: finding for finding in provided_findings(inputs, catalogue)}

    assert findings.keys() == {COUNT_ID, BOOLEAN_ID}
    assert type(findings[COUNT_ID].value) is int and findings[COUNT_ID].value == 0
    assert findings[BOOLEAN_ID].value is False
    for finding in findings.values():
        assert finding.provenance == "provided"
        assert finding.source == "inputs_yaml"
        assert finding.collector is finding.period is finding.coverage is None
        assert finding.collected_at == as_of


@pytest.mark.parametrize(
    ("answers", "number_without_web", "provenance", "coverage"),
    [
        ([], 0, "provided", None),
        (["false", "true"], 1, "provided", None),
        (["true", "null"], None, "unknown", Coverage("partial", scanned=1, total=2)),
        (["false", "null"], 1, "provided", Coverage("partial", scanned=1, total=2)),
    ],
)
def test_software_answers_derive_counts(
    catalogue: Catalogue,
    answers: list[str],
    number_without_web: int | None,
    provenance: str,
    coverage: Coverage | None,
) -> None:
    entries = [
        f"{{name: Fictional App {i}, vendor_has_web_version: {answer}}}"
        for i, answer in enumerate(answers)
    ]
    inputs = load_inputs_text(
        f"windows_only_software: [{', '.join(entries)}]", "inputs.yaml", catalogue
    )
    findings = {catalogue.finding(f.id).provided: f for f in provided_findings(inputs, catalogue)}

    assert findings["software_list"].value == len(answers)
    without = findings["software_list_without_web_version"]
    assert (without.value, without.provenance, without.coverage) == (
        number_without_web,
        provenance,
        coverage,
    )
    assert without.missing_reason == ("answer_not_provided" if provenance == "unknown" else None)


@pytest.mark.parametrize(
    ("recorded_coverage", "recorded_value", "supplied_value", "primary_value", "alternative_value"),
    [
        ("complete", 4, 12, 4, 12),
        ("partial", 4, 0, 4, 0),
        ("partial", 0, 12, 12, 0),
        ("partial", 4, 12, 12, 4),
        ("unknown", 4, 12, 12, 4),
    ],
)
def test_combine_keeps_both_observations(
    catalogue: Catalogue,
    recorded_coverage: str,
    recorded_value: int,
    supplied_value: int,
    primary_value: int,
    alternative_value: int,
) -> None:
    sample = files("befund").joinpath("demo", "town", "scan.json")
    scan = load_scan_text(read_text(sample), sample.name, catalogue)
    inputs = load_inputs_text(
        f"provided_counts: {{{COUNT_ID}: {supplied_value}}}", "inputs.yaml", catalogue
    )
    (supplied,) = provided_findings(inputs, catalogue)
    measured = replace(
        supplied,
        value=recorded_value,
        provenance="measured",
        collector="directory",
        source="sample.directory",
        coverage=Coverage(recorded_coverage),
        collected_at=scan.generated_at,
    )
    scan = replace(scan, findings=(measured,))

    combined, (alternative,) = combine(scan, (supplied,))

    assert scan.findings == (measured,)
    assert combined.findings[0].value == primary_value
    assert alternative.value == alternative_value
    assert {combined.findings[0], alternative} == {measured, supplied}


@pytest.mark.parametrize("previous", [None, "unknown", "provided"])
def test_combine_uses_new_answer(catalogue: Catalogue, previous: str | None) -> None:
    sample = files("befund").joinpath("demo", "town", "scan.json")
    scan = load_scan_text(read_text(sample), sample.name, catalogue)
    inputs = load_inputs_text(f"provided_counts: {{{COUNT_ID}: 17}}", "inputs.yaml", catalogue)
    (supplied,) = provided_findings(inputs, catalogue)
    earlier = {
        "unknown": replace(
            supplied, value=None, provenance="unknown", missing_reason="answer_not_provided"
        ),
        "provided": replace(supplied, value=2),
    }
    scan = replace(scan, findings=() if previous is None else (earlier[previous],))

    combined, alternatives = combine(scan, (supplied,))

    assert combined.findings == (supplied,)
    assert alternatives == ()


def test_inputs_module_has_no_catalogue_ids(catalogue: Catalogue) -> None:
    source = read_text(files("befund").joinpath("inputs.py"))
    assert not {entry.id for entry in catalogue.findings if entry.id in source}


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        (
            "town",
            {
                "ready": {"licences", "onedrive", "teams", "small_apps"},
                "needs_work": {
                    "directory",
                    "mail",
                    "sharepoint",
                    "office_files",
                    "device_management",
                    "power_platform",
                    "identity_access",
                    "integrations",
                },
                "blocker": {"windows_software", "telephony"},
                "unknown": {"security_compliance"},
            },
        ),
        (
            "nonprofit",
            {
                "ready": {
                    "directory",
                    "mail",
                    "windows_software",
                    "power_platform",
                    "telephony",
                    "identity_access",
                    "security_compliance",
                },
                "needs_work": {
                    "licences",
                    "onedrive",
                    "teams",
                    "office_files",
                    "device_management",
                    "small_apps",
                },
                "unknown": {"sharepoint", "integrations"},
            },
        ),
    ],
)
def test_sample_inputs_and_rendered_statuses(
    catalogue: Catalogue, sample: str, expected: dict[str, set[str]]
) -> None:
    directory = files("befund").joinpath("demo", sample)
    scan = load_scan_text(read_text(directory.joinpath("scan.json")), "scan.json", catalogue)
    text = read_text(directory.joinpath("inputs.yaml"))
    inputs = load_inputs_text(text, "inputs.yaml", catalogue)
    comments = [line for line in text.splitlines() if line.startswith("#")]
    assert any("invented" in line for line in comments)
    assert any("erfunden" in line for line in comments)
    assert inputs.amounts_are_invented and inputs.currency == "EUR" and inputs.as_of
    assert inputs.language is inputs.target_profile is None
    assert inputs.partial_exit.users < inputs.full_exit.users

    html = render_report(scan, lang="en", catalogue=catalogue, inputs=inputs)
    statuses = dict(re.findall(r'<tr data-workload="([^"]+)" data-status="([^"]+)"', html))
    assert statuses == {
        workload: status for status, workloads in expected.items() for workload in workloads
    }
    if sample == "town":
        mail = re.search(r'<tr data-workload="mail".*?</tr>', html, re.S)[0]
        security = re.search(r'<tr data-workload="security_compliance".*?</tr>', html, re.S)[0]
        assert 'data-status="needs_work" data-incomplete' in mail
        assert 'data-reason="needs_recipient_export"' in mail
        assert 'data-rule="mail-other-systems"' in html
        assert 'data-reason="licensed_use_not_measured"' in security
    else:
        assert inputs.full_exit.productivity_loss is None
        assert inputs.confirmations["telephony.replacement_available"] is None
        assert inputs.provided_counts["integrations.application_count"] is None


@pytest.mark.parametrize(
    ("as_of", "label"), [("2026-11-20", "20 November 2026"), (None, "Date not supplied")]
)
def test_report_dates_provided_values_and_keeps_measured_values_separate(
    catalogue: Catalogue, as_of: str | None, label: str
) -> None:
    path = files("befund").joinpath("demo", "town", "scan.json")
    scan = load_scan_text(read_text(path), path.name, catalogue)
    inputs = load_inputs_text(
        f"as_of: {as_of or 'null'}\nprovided_counts: {{{COUNT_ID}: 12}}",
        "typed-answers.yaml",
        catalogue,
    )
    (answer,) = provided_findings(inputs, catalogue)
    measurement = replace(
        answer,
        value=4,
        provenance="measured",
        collector="directory",
        source="sample.directory",
        collected_at="2026-11-02",
        coverage=Coverage("complete"),
    )
    findings = tuple(measurement if item.id == COUNT_ID else item for item in scan.findings)

    html = render_report(replace(scan, findings=findings), lang="en", inputs=inputs)

    row = re.search(rf'<tr data-finding="{COUNT_ID}".*?</tr>', html, re.S)[0]
    assert row.startswith(f'<tr data-finding="{COUNT_ID}" data-provenance="measured"')
    assert 'data-provenance="provided"' in row
    assert row.index("4 files") < row.index("12 files")
    assert "Provided" in row and "For comparison only" in row
    assert "Answer in the inputs file" in row and label in row
    assert "typed-answers.yaml" not in html


def test_software_list_escapes_names_and_shows_confirmed_and_missing_answers(
    catalogue: Catalogue,
) -> None:
    path = files("befund").joinpath("demo", "town", "scan.json")
    scan = load_scan_text(read_text(path), path.name, catalogue)
    markup = '<img src="https://example.invalid/plant">'
    inputs = load_inputs_text(
        f"""organisation_name: '<strong>Example Authority</strong>'
windows_only_software:
  - {{name: '{markup}', users: 7, vendor_has_web_version: false}}
  - {{name: Second example, users: null, vendor_has_web_version: null}}
""",
        "typed-answers.yaml",
        catalogue,
    )

    html = render_report(scan, lang="en", inputs=inputs)

    assert markup not in html and "<img" not in html
    assert "&lt;strong&gt;Example Authority&lt;/strong&gt;" in html
    row = re.search(r'<tr data-workload="windows_software".*?</tr>', html, re.S)[0]
    assert 'data-status="blocker" data-incomplete' in row
    assert "At least 1 application" in row and "1 of 2 answers supplied" in row
    assert 'data-reason="answer_not_provided"' in row
    entries = re.findall(r"<tr data-software-entry.*?</tr>", html, re.S)
    assert len(entries) == 2
    assert markup in unescape(entries[0]) and ">7<" in entries[0] and ">No<" in entries[0]
    assert "Second example" in entries[1] and "Not stated" in entries[1]
    for entry in entries:
        assert 'data-provenance="provided"' in entry
        assert "Answer in the inputs file" in entry and "Date not supplied" in entry


def test_inputs_example_covers_the_contract(catalogue: Catalogue) -> None:
    path = ROOT / "inputs.example.yaml"
    text = read_text(path)
    lines = text.splitlines()
    assert lines[0] == "# SPDX-License-Identifier: AGPL-3.0-or-later"
    scenario = dict.fromkeys(field.name for field in fields(ScenarioInputs))
    assert len(scenario) == 13
    answers = {
        field: {
            entry.id: None
            for entry in catalogue.findings
            if entry.provided == "answer" and entry.type == kind
        }
        for field, kind in (("provided_counts", "count"), ("confirmations", "boolean"))
    }
    expected = {
        "organisation_name": None,
        "currency": None,
        "language": None,
        "target_profile": None,
        "as_of": None,
        "amounts_are_invented": False,
        "current_costs": dict.fromkeys(field.name for field in fields(CurrentCosts)),
        "target_costs": {"partial_exit": scenario, "full_exit": scenario},
        "windows_only_software": None,
        **answers,
    }

    parsed = parse_yaml(text, path.name)
    assert parsed == expected and list(parsed) == list(expected)
    assert load_inputs(path, catalogue) == replace(empty_inputs(), **answers)
    key_lines = r"^\s*(?:#\s+(?:-\s+)?)?[a-z][a-z0-9_.]*:"
    for index, line in enumerate(lines):
        if re.match(key_lines, line):
            assert lines[index - 2].lstrip().startswith("# EN:"), line
            assert lines[index - 1].lstrip().startswith("# DE:"), line
    currency_amount = r"\b[A-Z]{3}\s*\d|\d\s*[A-Z]{3}\b"
    assert not re.search(currency_amount, text)


@pytest.mark.parametrize("suffix", ["", ".de"])
def test_checklist_matches_inputs_and_catalogue(catalogue: Catalogue, suffix: str) -> None:
    text = read_text(ROOT / "docs" / f"interview-checklist{suffix}.md")
    mentions = set(re.findall(r"`([^`\n]+)`", text))
    questions = re.findall(r"^- [^\n]*\(`([^`\n]+)`\)\?$", text, re.M)
    answer_ids = {entry.id for entry in catalogue.findings if entry.provided == "answer"}
    assert mentions & {entry.id for entry in catalogue.findings} == answer_ids
    example = ROOT / "inputs.example.yaml"
    data = parse_yaml(read_text(example), example.name)
    groups = {key for key, value in data.items() if isinstance(value, dict)}
    blocks = {f"target_costs.{name}" for name in data["target_costs"]}
    leaves = {
        *(data.keys() - groups),
        *(f"current_costs.{name}" for name in data["current_costs"]),
        *(
            f"target_costs.{block}.{key}"
            for block, values in data["target_costs"].items()
            for key in values
        ),
        *(f"windows_only_software.{field.name}" for field in fields(WindowsSoftware)),
    }
    assert groups | blocks <= mentions
    assert sorted(questions) == sorted(leaves | answer_ids)
    for kind in load_risky_file_types(catalogue):
        line = next(line for line in text.splitlines() if f"`{kind.finding_id}`" in line)
        assert set(re.findall(r"`\.([a-z0-9]+)`", line)) == set(kind.extensions)
    if suffix == ".de":
        assert "Sie" in text


def test_every_provided_finding_is_used_by_rules_or_headlines(catalogue: Catalogue) -> None:
    rule_set = load_status_rules(catalogue)
    rule_ids = {
        condition.finding
        for block in rule_set.workloads.values()
        for condition in (
            *block.ready,
            *(condition for rule in block.rules for condition in rule.when),
        )
    }

    assert not {
        entry.id
        for entry in catalogue.findings
        if entry.provided != "no" and not entry.headline and entry.id not in rule_ids
    }
