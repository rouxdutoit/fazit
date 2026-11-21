# SPDX-License-Identifier: AGPL-3.0-or-later
import ast
import datetime
import os
import re
import socket
from dataclasses import replace
from datetime import date, tzinfo
from hashlib import sha256
from html import unescape
from importlib.resources import files
from pathlib import Path
from shutil import copytree

import pytest
import yaml
from typer.testing import CliRunner

from befund import __version__, i18n, inputs, model, rules
from befund import report as report_module
from befund.catalogue import load_catalogue
from befund.cli import app
from befund.errors import InputError
from befund.i18n import SUPPORTED_LANGUAGES, load_locale
from befund.model import Coverage, Scan, load_scan, load_scan_text
from befund.parsing import parse_yaml, read_text
from befund.report import render_report, report_file_name

runner = CliRunner()


def test_demo_writes_one_local_report(tmp_path: Path) -> None:
    result = runner.invoke(app, ["demo", "--out", str(tmp_path)])

    assert result.exit_code == 0, result.output
    report = tmp_path / "report-2026-11-02-en.html"
    strings = load_locale("en")["cli"]
    assert result.stdout.splitlines() == [
        strings["sample_scan"].format(path=tmp_path / "scan-2026-11-02-en.json"),
        strings["sample_inputs"].format(path=tmp_path / "inputs-2026-11-02-en.yaml"),
        str(report),
    ]
    assert report.is_file()
    html = report.read_text(encoding="utf-8")
    assert re.findall(r'data-section="([^"]+)"', html) == [
        "header",
        "found",
        "costs",
        "readiness",
        "moves",
        "attention",
        "path",
        "appendix",
        "footer",
    ]
    header = load_locale("en")["header"]
    assert all(header[key] in html for key in ("local", "offline", "sample"))
    assert 'data-finding="directory.user_count"' in html
    assert "Stadtverwaltung Musterstadt" in html
    assert "data-software-entry" in _section(html, "attention")
    moves = _section(html, "moves")
    assert "Nubus" in moves and "Keycloak" in moves


def _section(html: str, name: str) -> str:
    section = re.search(rf'<section data-section="{name}">.*?</section>', html, re.S)
    assert section is not None, name
    return section[0]


@pytest.mark.parametrize("profile", rules.PROFILES)
def test_report_shows_function_mapping_and_workload_evidence(tmp_path: Path, profile: str) -> None:
    source = files("befund").joinpath("demo", "town", "scan.json")
    result = runner.invoke(
        app, ["report", str(source), "--profile", profile, "--out", str(tmp_path)]
    )

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.strip())
    assert report.is_file() and report.parent == tmp_path
    html = report.read_text(encoding="utf-8")
    mapping = rules.load_mapping(profile, load_catalogue())
    strings = load_locale("en")
    moves = _section(html, "moves")
    assert mapping.label["en"] in html.split("</header>", 1)[0]
    assert "<caption data-sample>" in moves
    assert re.findall(r'<tr data-function="([^"]+)"', moves) == [
        row.function for row in mapping.functions
    ]
    readiness = dict(
        re.findall(
            r'<tr data-workload="([^"]+)" data-status="([^"]+)"', _section(html, "readiness")
        )
    )
    appendix = _section(html, "appendix")
    assert mapping.file_name in appendix and mapping.description["en"] in appendix
    for row in mapping.functions:
        move = re.search(rf'<tr data-function="{row.function}".*?</tr>', moves, re.S)
        detail = re.search(rf'<dd data-mapping-details="{row.function}".*?</dd>', appendix, re.S)
        assert move is not None and detail is not None
        status = readiness[row.workload]
        assert f'data-status="{status}"' in move[0] and strings["status"][status] in move[0]
        for text in (
            row.microsoft["en"],
            row.replacement["en"],
            strings["mapping_coverage"][row.coverage],
        ):
            assert text in unescape(move[0])
        assert move[0].count("data-move-evidence=") <= 3
        if row.checked_on is None:
            assert strings["moves"]["no_project_check"] in move[0]
            assert strings["moves"]["no_project_check"] in detail[0]
        else:
            assert row.checked_on.isoformat() in move[0] and row.checked_on.isoformat() in detail[0]
            assert row.reference_url and row.reference_url in unescape(detail[0])
        if row.note:
            assert row.note["en"] in unescape(detail[0])
    assert "href=" not in moves and "href=" not in appendix
    assert strings["moves"]["no_function"] in moves
    assert "Other systems send mail" in moves and strings["provenance"]["provided"] in moves
    assert strings["source"]["sample.interview"] in moves
    assert strings["readiness"]["incomplete"] in moves


def test_changed_mapping_is_read_once_and_rendered_as_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules.rules_dir())), copied)
    path = copied / "mappings" / "opendesk.yaml"
    data = parse_yaml(read_text(path), path.name)
    mail = next(row for row in data["functions"] if row["function"] == "mail_and_calendar")
    markup = '<img src="https://example.invalid/mapping">'
    mail["replacement"]["en"] = markup
    raw = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).replace("\n", "\r\n").encode()
    path.write_bytes(raw)
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)
    real_read = rules.read_text
    reads = []

    def record_read(path: Path) -> str:
        reads.append(path.name)
        return real_read(path)

    monkeypatch.setattr(rules, "read_text", record_read)
    result = runner.invoke(app, ["demo", "--out", str(tmp_path / "out")])

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.splitlines()[-1])
    assert report.is_file()
    html = report.read_text(encoding="utf-8")
    assert markup in unescape(_section(html, "moves")) and markup not in html
    assert not re.search(r"<img\b", html)
    assert f'data-checksum="{path.name}">{sha256(raw).hexdigest()}</code>' in html
    assert reads.count(path.name) == 1


def test_cli_names_a_broken_mapping_file_and_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules.rules_dir())), copied)
    path = copied / "mappings" / "opendesk.yaml"
    data = parse_yaml(read_text(path), path.name)
    del data["functions"][0]["replacement"]["de"]
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)
    out = tmp_path / "out"
    result = runner.invoke(app, ["demo", "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert result.stderr.splitlines() == [
        "Error: Supply a value for functions[0].replacement.de in opendesk.yaml."
    ]


def test_demo_rejects_an_output_path_that_is_a_file(tmp_path: Path) -> None:
    file = tmp_path / "regular-file"
    file.write_text("Keep this", encoding="utf-8")

    result = runner.invoke(app, ["demo", "--out", str(file)])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert len(result.stderr.splitlines()) == 1
    assert result.stderr.startswith("Error:")
    assert "--out" in result.stderr and file.name in result.stderr
    assert "Traceback" not in result.stderr
    assert file.read_text(encoding="utf-8") == "Keep this"


def test_report_filename_uses_only_the_scan_day_and_selected_language() -> None:
    assert report_file_name("2026-11-02T23:30:00-05:00", lang="en") == "report-2026-11-02-en.html"
    with pytest.raises(InputError, match="unsupported_language"):
        report_file_name("2026-11-02", lang="../../outside")


def test_audit_hook_records_caught_socket_attempts(offline: list[str]) -> None:
    with pytest.raises(AssertionError, match=r"socket\.__new__"):
        socket.socket()
    with pytest.raises(AssertionError, match=r"socket\.getaddrinfo"):
        socket.getaddrinfo("localhost", 0)

    assert offline.pop(0) == "socket.__new__"
    assert offline.pop(0) == "socket.getaddrinfo"


@pytest.mark.parametrize(
    "name",
    ["report-2026-11-02-en.html", "scan-2026-11-02-en.json", "inputs-2026-11-02-en.yaml"],
)
def test_demo_refuses_a_symlink_destination(tmp_path: Path, name: str) -> None:
    outside = tmp_path / "outside.html"
    outside.write_bytes(b"Preserve this file")
    out = tmp_path / "report"
    out.mkdir()
    destination = out / name
    os.symlink(outside, destination)

    result = runner.invoke(app, ["demo", "--out", str(out)])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "symbolic link" in result.stderr
    assert destination.is_symlink()
    assert outside.read_bytes() == b"Preserve this file"


def _sample_scan(name: str) -> Scan:
    source = files("befund").joinpath("demo", name, "scan.json")
    return load_scan_text(read_text(source), source.name, load_catalogue())


@pytest.mark.parametrize("profile", rules.PROFILES)
@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize(("sample", "date"), [("town", "2026-11-02"), ("nonprofit", "2026-11-05")])
def test_cli_renders_every_profile_in_both_languages_for_both_samples(
    tmp_path: Path, lang: str, sample: str, date: str, profile: str
) -> None:
    result = runner.invoke(
        app,
        ["demo", "--lang", lang, "--sample", sample, "--profile", profile, "--out", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    report = tmp_path / f"report-{date}-{lang}.html"
    scan_path = tmp_path / f"scan-{date}-{lang}.json"
    inputs_path = tmp_path / f"inputs-{date}-{lang}.yaml"
    strings = load_locale(lang)["cli"]
    assert result.stdout.splitlines() == [
        strings["sample_scan"].format(path=scan_path),
        strings["sample_inputs"].format(path=inputs_path),
        str(report),
    ]
    assert not result.stderr and report.is_file()
    assert load_scan(scan_path, load_catalogue()) == _sample_scan(sample)
    inputs = files("befund").joinpath("demo", sample, "inputs.yaml")
    assert inputs_path.read_bytes() == inputs.read_bytes()
    html = report.read_text(encoding="utf-8")
    assert f'<html lang="{lang}">' in html
    assert load_locale(lang)["header"]["sample"] in html
    mapping = rules.load_mapping(profile, load_catalogue())
    assert mapping.label[lang] in html.split("</header>", 1)[0]
    moves = _section(html, "moves")
    assert moves.count("data-function=") == len(mapping.functions)
    if not mapping.product_profile:
        assert load_locale(lang)["moves"]["no_project_check"] in moves


@pytest.mark.parametrize("sample", ["town", "nonprofit"])
def test_sample_has_all_findings_and_explicit_gaps(sample: str) -> None:
    scan = _sample_scan(sample)
    assert sorted(item.id for item in scan.findings) == sorted(
        entry.id for entry in load_catalogue().findings
    )
    assert scan.dropped_count == 0
    assert any(collector.status == "skipped" for collector in scan.collectors)
    assert {finding.provenance for finding in scan.findings} == {"measured", "provided", "unknown"}
    assert scan.licences is not None and scan.licences.products


def test_german_visible_text_uses_only_german_provenance_words() -> None:
    html = render_report(_sample_scan("town"), lang="de")
    content = re.sub(r"<style\b.*?</style>", "", html, flags=re.S)
    visible = re.sub(r"<[^>]*>", " ", content)
    assert all(word in visible for word in load_locale("de")["provenance"].values())
    assert all(word not in visible for word in load_locale("en")["provenance"].values())


def test_sample_measurement_labels_and_directory_note() -> None:
    scan = _sample_scan("town")
    strings = load_locale("en")
    html = render_report(scan, lang="en")
    tables = re.findall(r"<table\b.*?</table>", html, re.S)
    measured_tables = [table for table in tables if 'data-provenance="measured"' in table]
    assert measured_tables
    assert all("<caption data-sample>" in table for table in measured_tables)
    assert all(strings["found"]["sample"] in table for table in measured_tables)
    found = html.split('data-section="found"')[1].split('data-section="appendix"')[0]
    assert strings["found"]["notes"]["directory"] in found

    imported = render_report(replace(scan, source_kind="import"), lang="en")
    assert strings["header"]["sample"] not in imported
    assert "data-sample" not in imported


def test_provided_answer_source_is_independent_of_scan_source() -> None:
    scan = _sample_scan("town")
    strings = load_locale("en")
    provided = scan.finding("device_management.device_count")
    assert provided is not None and provided.source == "sample.interview"
    assert strings["source"]["sample.interview"] in render_report(scan, lang="en")

    findings = tuple(
        replace(finding, source="inputs_yaml") if finding.id == provided.id else finding
        for finding in scan.findings
    )
    html = render_report(replace(scan, findings=findings), lang="en")
    device_row = re.search(r'<tr data-finding="device_management.device_count".*?</tr>', html, re.S)
    assert device_row is not None
    assert strings["source"]["inputs_yaml"] in device_row[0]
    assert strings["source"]["sample.interview"] not in device_row[0]
    mail_row = re.search(r'<tr data-finding="mail.other_systems_send_mail".*?</tr>', html, re.S)
    assert mail_row is not None
    assert strings["source"]["sample.interview"] in mail_row[0]
    assert strings["source"]["inputs_yaml"] not in mail_row[0]


@pytest.mark.parametrize(("sample", "lang"), [("town", "en"), ("nonprofit", "de")])
def test_scan_only_report_readiness(tmp_path: Path, sample: str, lang: str) -> None:
    scan_path = files("befund").joinpath("demo", sample, "scan.json")
    result = runner.invoke(app, ["report", str(scan_path), "--lang", lang, "--out", str(tmp_path)])
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file() and not result.stderr
    html = path.read_text(encoding="utf-8")
    strings = load_locale(lang)
    section = re.search(r'<section data-section="readiness">.*?</section>', html, re.S)
    assert section is not None and "%" not in section[0]
    table = section[0]
    rows = re.findall(
        r'<tr data-workload="([^"]+)" data-status="([^"]+)"[^>]*>.*?</tr>', table, re.S
    )
    catalogue = load_catalogue()
    assert [workload for workload, _ in rows] == list(catalogue.workload_ids)
    assert "<caption data-sample>" in table
    assert [workload for workload, status in rows if status == "ready"] == (
        ["telephony"] if sample == "nonprofit" else []
    )
    for workload, status in rows:
        row = re.search(rf'<tr data-workload="{workload}".*?</tr>', table, re.S)
        assert row is not None and strings["status"][status] in row[0]
    segments = re.findall(r'data-segment="([^"]+)" data-count="(\d+)"', table)
    assert segments == [
        (status, str(total))
        for status in rules.STATUSES
        if (total := sum(result == status for _, result in rows))
    ]
    assert sum(int(total) for _, total in segments) == len(catalogue.workloads)
    assert 'data-subsection="not-examined"' in table
    assert {key for key, _ in rows if f'data-unexamined-workload="{key}"' in table} == {
        key for key, status in rows if status == "unknown"
    }
    scan = _sample_scan(sample)
    for finding in scan.findings:
        if finding.provenance == "unknown":
            assert f'data-unexamined-finding="{finding.id}"' in table
    for collector in scan.collectors:
        if collector.status == "skipped":
            assert f'data-unexamined-collector="{collector.id}"' in table
    if sample == "town":
        mail = re.search(r'<tr data-workload="mail".*?</tr>', table, re.S)
        assert mail is not None and 'data-status="needs_work" data-incomplete' in mail[0]
        assert strings["collector"]["exchange_recipients"] in mail[0]
        for text in strings["reason"]["needs_recipient_export"].values():
            assert text in mail[0]
        assert 'data-reason="needs_recipient_export"' in mail[0]
        assert 'data-rule="mail-other-systems"' in html
    else:
        onedrive = re.search(r'<tr data-workload="onedrive".*?</tr>', table, re.S)
        assert onedrive is not None
        for text in (
            "52,5 GB",
            strings["provenance"]["measured"],
            strings["source"]["sample.onedrive_usage"],
            "5. November 2026",
            "9. Mai bis 4. Nov. 2026",
            "Teilweise, 18 von 20 geprüft, 2 fehlgeschlagen",
        ):
            assert text in onedrive[0]

    appendix = html.split('data-section="appendix"', 1)[1]
    assert appendix.count(strings["appendix"]["ready_evidence"]) == len(catalogue.workloads)
    assert "status.yaml" in appendix


def test_changed_rule_changes_demo_status_and_escapes_the_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scan = files("befund").joinpath("demo", "town", "scan.json")
    original = runner.invoke(app, ["report", str(scan), "--out", str(tmp_path / "original")])
    assert original.exit_code == 0, original.output
    html = Path(original.stdout.strip()).read_text(encoding="utf-8")
    assert 'data-workload="directory" data-status="needs_work"' in html
    copied = tmp_path / "rules"
    copytree(Path(str(rules.rules_dir())), copied)
    rule_path = copied / "status.yaml"
    markup = '<img src="https://example.invalid/rule">'
    data = parse_yaml(read_text(rule_path), rule_path.name)
    guest_rule = next(
        rule for rule in data["workloads"]["directory"]["rules"] if rule["id"] == "directory-guests"
    )
    guest_rule["status"] = "blocker"
    guest_rule["reason"]["en"] = markup
    source = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    raw = source.replace("\n", "\r\n").encode("utf-8")
    rule_path.write_bytes(raw)
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)
    real_read = rules.read_text
    reads = []

    def record_read(path: Path) -> str:
        reads.append(path.name)
        return real_read(path)

    monkeypatch.setattr(rules, "read_text", record_read)
    result = runner.invoke(app, ["demo", "--out", str(tmp_path / "changed")])

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.splitlines()[-1])
    assert report.is_file()
    html = report.read_text(encoding="utf-8")
    assert 'data-workload="directory" data-status="blocker"' in html
    assert "directory-guests" in html and "&lt;img src=" in html and markup not in html
    assert not re.search(r"<img\b", html)
    assert f'data-checksum="status.yaml">{sha256(raw).hexdigest()}</code>' in html
    assert reads.count("status.yaml") == 1


def test_nonprofit_partial_coverage_has_all_counts_and_localised_dates() -> None:
    html = render_report(_sample_scan("nonprofit"), lang="de")
    row = re.search(r'<tr data-finding="onedrive.storage_bytes"[^>]*>(.*?)</tr>', html, re.S)
    assert row is not None
    assert "Teilweise, 18 von 20 geprüft, 2 fehlgeschlagen" in row[1]
    assert "52,5 GB" in row[1]
    assert "5. November 2026" in row[1]
    assert "9. Mai bis 4. Nov. 2026" in row[1]


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (7, "At least 7 accounts"),
        (0, "0 accounts in the items checked"),
    ],
)
def test_partial_counts_describe_the_observed_scope(value: int, message: str) -> None:
    scan = _sample_scan("town")
    findings = tuple(
        replace(finding, value=value, coverage=Coverage("partial"))
        if finding.id == "directory.user_count"
        else finding
        for finding in scan.findings
    )
    assert message in render_report(replace(scan, findings=findings), lang="en")


def test_cli_localises_bad_output_directory(tmp_path: Path) -> None:
    file = tmp_path / "file"
    file.touch()
    result = runner.invoke(app, ["demo", "--lang", "de", "--out", str(file)])

    expected = load_locale("de")["errors"]["out_dir"].format(file=file, field="--out")
    assert result.exit_code == 2
    assert result.stderr.splitlines() == [f"Fehler: {expected}"]
    assert not result.stdout


@pytest.mark.parametrize(
    ("arguments", "prefix", "field"),
    [
        (["--lang", "planted"], "Error:", "--lang"),
        (["--lang", "de", "--sample", "planted"], "Fehler:", "--sample"),
        (["--profile", "planted"], "Error:", "--profile"),
        (["--lang", "de", "--profile", "planted"], "Fehler:", "--profile"),
    ],
)
def test_cli_rejects_unsupported_options_without_echoing_the_value(
    arguments: list[str], prefix: str, field: str
) -> None:
    result = runner.invoke(app, ["demo", *arguments])
    assert result.exit_code == 2
    assert result.stderr.startswith(prefix) and field in result.stderr
    assert "planted" not in result.stderr


def test_debug_preserves_the_underlying_input_error(tmp_path: Path) -> None:
    file = tmp_path / "file"
    file.touch()
    result = runner.invoke(app, ["--debug", "demo", "--out", str(file)])
    assert isinstance(result.exception, InputError) and result.exception.code == "out_dir"


def test_version_works_without_a_command() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_report_rebuilds_a_demo_copy(tmp_path: Path) -> None:
    demo_out = tmp_path / "demo"
    demo_result = runner.invoke(app, ["demo", "--out", str(demo_out)])
    assert demo_result.exit_code == 0, demo_result.output
    scan = demo_out / "scan-2026-11-02-en.json"
    assert scan.is_file()

    out = tmp_path / "rebuilt"
    result = runner.invoke(app, ["report", str(scan), "--lang", "de", "--out", str(out)])

    assert result.exit_code == 0, result.output
    report = out / "report-2026-11-02-de.html"
    assert result.stdout.splitlines() == [str(report.resolve())]
    assert not result.stderr
    assert list(out.iterdir()) == [report]
    html = report.read_text(encoding="utf-8")
    assert 'lang="de"' in html
    assert "2. November 2026" in html


def test_report_refuses_a_symlink_destination(tmp_path: Path) -> None:
    outside = tmp_path / "outside.html"
    outside.write_bytes(b"Preserve this file")
    out = tmp_path / "out"
    out.mkdir()
    destination = out / "report-2026-11-02-en.html"
    os.symlink(outside, destination)
    scan = files("befund").joinpath("demo", "town", "scan.json")

    result = runner.invoke(app, ["report", str(scan), "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout
    assert "symbolic link" in result.stderr
    assert destination.is_symlink()
    assert outside.read_bytes() == b"Preserve this file"


@pytest.mark.parametrize(
    ("text", "options", "lang", "profile"),
    [
        ("", [], "en", "opendesk"),
        ("language: de\ntarget_profile: generic\n", [], "de", "generic"),
        ("language: de\ntarget_profile: generic\n", ["--lang", "en"], "en", "generic"),
        ("language: de\ntarget_profile: generic\n", ["--profile", "nextcloud"], "de", "nextcloud"),
    ],
)
def test_report_resolves_options_and_displays_organisation_from_inputs(
    tmp_path: Path, text: str, options: list[str], lang: str, profile: str
) -> None:
    scan = files("befund").joinpath("demo", "town", "scan.json")
    answers = tmp_path / "office-interview.yaml"
    answers.write_text(text + "organisation_name: West Weir Council\n", encoding="utf-8")
    out = tmp_path / "out"

    result = runner.invoke(
        app, ["report", str(scan), "--inputs", str(answers), "--out", str(out), *options]
    )

    assert result.exit_code == 0 and not result.stderr, result.output
    report_path = out / f"report-2026-11-02-{lang}.html"
    assert result.stdout.splitlines() == [str(report_path)]
    assert list(out.iterdir()) == [report_path]
    html = report_path.read_text(encoding="utf-8")
    header = html.split("</header>", 1)[0]
    assert f'<html lang="{lang}">' in html
    assert "West Weir Council" in header and "West Weir Council" not in result.stdout
    assert rules.load_mapping(profile, load_catalogue()).label[lang] in header
    assert answers.name not in html


@pytest.mark.parametrize(("lang", "prefix"), [(None, "Error:"), ("de", "Fehler:")])
def test_report_input_errors_use_the_flag_language(
    tmp_path: Path, lang: str | None, prefix: str
) -> None:
    scan = files("befund").joinpath("demo", "town", "scan.json")
    answers = tmp_path / "office-interview.yaml"
    answers.write_text("language: de\ncurency: EUR\n", encoding="utf-8")
    out = tmp_path / "out"
    options = [] if lang is None else ["--lang", lang]

    result = runner.invoke(
        app, ["report", str(scan), "--inputs", str(answers), "--out", str(out), *options]
    )

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert len(result.stderr.splitlines()) == 1 and result.stderr.startswith(prefix)
    assert answers.name in result.stderr and "curency" in result.stderr


@pytest.mark.parametrize("kind", ["missing", "directory"])
def test_report_rejects_missing_or_directory_inputs(tmp_path: Path, kind: str) -> None:
    scan = files("befund").joinpath("demo", "town", "scan.json")
    answers = tmp_path / "office-interview.yaml"
    if kind == "directory":
        answers.mkdir()
    out = tmp_path / "out"

    result = runner.invoke(app, ["report", str(scan), "--inputs", str(answers), "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert len(result.stderr.splitlines()) == 1 and answers.name in result.stderr


def test_report_rebuilds_from_the_demo_copies(tmp_path: Path) -> None:
    demo = tmp_path / "demo"
    result = runner.invoke(app, ["demo", "--out", str(demo)])
    assert result.exit_code == 0, result.output
    demo_report = Path(result.stdout.splitlines()[-1])
    assert demo_report.is_file()
    source, answers = demo / "scan-2026-11-02-en.json", demo / "inputs-2026-11-02-en.yaml"
    assert source.is_file() and answers.is_file()
    out = tmp_path / "rebuilt"

    result = runner.invoke(
        app, ["report", str(source), "--inputs", str(answers), "--out", str(out)]
    )

    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file() and path.parent == out
    html = path.read_text(encoding="utf-8")
    readiness = _section(html, "readiness")
    assert 'data-workload="telephony" data-status="blocker"' in readiness
    assert 'data-workload="windows_software" data-status="blocker"' in readiness
    assert 'data-workload="mail" data-status="needs_work" data-incomplete' in readiness
    assert 'data-reason="needs_recipient_export"' in readiness
    assert 'data-workload="mail" data-status="ready"' not in readiness
    macro = re.compile(r'<tr data-finding="office_files.kind.macro".*?</tr>', re.S)
    assert "Sample interview answer" in macro.search(demo_report.read_text(encoding="utf-8"))[0]
    assert "Answer in the inputs file" in macro.search(html)[0]

    scan_only = runner.invoke(app, ["report", str(source), "--out", str(tmp_path / "scan-only")])
    assert scan_only.exit_code == 0, scan_only.output
    scan_html = Path(scan_only.stdout.strip()).read_text(encoding="utf-8")
    assert 'data-workload="telephony" data-status="unknown"' in _section(scan_html, "readiness")
    assert "This organisation" in scan_html.split("</header>", 1)[0]


@pytest.mark.parametrize(
    ("kind", "code", "field", "details"),
    [
        ("missing", "file_not_found", "$", {}),
        ("directory", "is_directory", "$", {}),
        ("not_utf8", "not_utf8", "$", {}),
        ("schema", "schema_version", "schema_version", {"found": "2.0", "supported": "1.x"}),
    ],
)
@pytest.mark.parametrize("lang", ["en", "de"])
def test_report_errors_name_the_file_and_field(
    tmp_path: Path, kind: str, code: str, field: str, details: dict[str, str], lang: str
) -> None:
    scan = tmp_path / "inventory.json"
    if kind == "directory":
        scan.mkdir()
    elif kind == "not_utf8":
        scan.write_bytes(b"\xff")
    elif kind == "schema":
        scan.write_text('{"schema_version": "2.0"}', encoding="utf-8")
    out = tmp_path / "out"
    arguments = ["report", str(scan), "--out", str(out)]
    if lang == "de":
        arguments.extend(["--lang", "de"])

    result = runner.invoke(app, arguments)

    strings = load_locale(lang)
    message = strings["errors"][code].format(file=scan.name, field=field, **details)
    assert result.exit_code == 2
    assert result.stderr.splitlines() == [strings["cli"]["error_prefix"].format(message=message)]
    assert not result.stdout and not out.exists()


def test_report_debug_exposes_the_input_error(tmp_path: Path) -> None:
    scan = tmp_path / "missing.json"
    with pytest.raises(InputError, match="file_not_found"):
        runner.invoke(app, ["--debug", "report", str(scan)], catch_exceptions=False)


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="Requires POSIX permissions")
def test_report_refuses_an_unwritable_output_directory(tmp_path: Path) -> None:
    scan = files("befund").joinpath("demo", "town", "scan.json")
    out = tmp_path / "unwritable"
    out.mkdir(mode=0o500)
    try:
        result = runner.invoke(app, ["report", str(scan), "--out", str(out)])

        assert result.exit_code == 2
        assert not result.stdout
        assert len(result.stderr.splitlines()) == 1
        assert result.stderr.startswith("Error:")
        assert "--out" in result.stderr and out.name in result.stderr
        assert not list(out.iterdir())
    finally:
        out.chmod(0o700)


def _set_system_day(patch: pytest.MonkeyPatch, day: date) -> None:
    class SystemDate(date):
        @classmethod
        def today(cls) -> date:
            return day

    class SystemDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> datetime.datetime:
            return cls(day.year, day.month, day.day, tzinfo=tz)

        @classmethod
        def utcnow(cls) -> datetime.datetime:
            return cls.now()

    for module in (datetime, model, i18n, inputs, report_module):
        patch.setattr(module, "date", SystemDate)
    for module in (datetime, model):
        patch.setattr(module, "datetime", SystemDateTime)


@pytest.mark.parametrize(
    ("sample", "lang", "profile", "with_inputs"),
    [
        ("town", "en", "opendesk", False),
        *(
            (sample, lang, profile, True)
            for sample in ("town", "nonprofit")
            for lang in SUPPORTED_LANGUAGES
            for profile in rules.PROFILES
        ),
    ],
)
def test_report_bytes_and_name_ignore_the_system_day(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sample: str,
    lang: str,
    profile: str,
    with_inputs: bool,
) -> None:
    sample_dir = files("befund").joinpath("demo", sample)
    scan = sample_dir.joinpath("scan.json")
    options = ["--lang", lang, "--profile", profile]
    if with_inputs:
        options.extend(["--inputs", str(sample_dir.joinpath("inputs.yaml"))])
    reports = []
    for day in (date(2027, 1, 1), date(2031, 12, 31)):
        out = tmp_path / day.isoformat()
        with monkeypatch.context() as patch:
            _set_system_day(patch, day)
            result = runner.invoke(app, ["report", str(scan), "--out", str(out), *options])
        assert result.exit_code == 0, result.output
        path = Path(result.stdout.strip())
        assert path.is_file() and path.parent == out
        reports.append((path.name, path.read_bytes()))

    assert reports[0] == reports[1]


def test_source_does_not_read_the_clock() -> None:
    source = Path(__file__).resolve().parents[1] / "src"
    wall_clock = {"today", "now", "utcnow"}
    time_functions = {"time", "localtime", "gmtime"}
    for path in sorted(source.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        time_modules = {"time"}
        forbidden = set(wall_clock)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                time_modules.update(
                    alias.asname or alias.name for alias in node.names if alias.name == "time"
                )
            elif isinstance(node, ast.ImportFrom) and node.module == "time":
                forbidden.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name in time_functions
                )
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = ast.unparse(node.func)
            module, _, attribute = name.rpartition(".")
            reads_clock = attribute in wall_clock or name in forbidden
            reads_clock |= module in time_modules and attribute in time_functions
            assert not reads_clock, f"{path}:{node.lineno} calls {name}"
