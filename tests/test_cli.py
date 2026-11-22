# SPDX-License-Identifier: AGPL-3.0-or-later
import ast
import datetime
import json
import os
import re
import shlex
import socket
import subprocess
import sys
from dataclasses import replace
from datetime import date, tzinfo
from hashlib import sha256
from html import unescape
from importlib.resources import files
from pathlib import Path
from shutil import copyfile, copytree

import pytest
import yaml
from helpers import (
    ROOT,
    readiness_row,
    readme_code_blocks,
    report_section,
    runner,
    sample_inputs_path,
    sample_scan_path,
)
from report_expectations import SECTION_ORDER

from fazit import __version__, i18n, model, rules, validation
from fazit import report as report_module
from fazit.catalogue import load_catalogue
from fazit.cli import app
from fazit.errors import InputError
from fazit.i18n import load_locale
from fazit.mappings import PROFILES, load_mapping
from fazit.model import Coverage, Scan, load_scan
from fazit.parsing import parse_yaml, read_text
from fazit.report import render_report, report_file_name
from fazit.status import STATUSES

ANSI_STYLE = re.compile(r"\x1b\[[0-9;]*m")


def test_demo_prints_output_paths_and_renders_inventory(tmp_path: Path) -> None:
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
    assert html.startswith("<!doctype html>\n")
    assert re.findall(r'data-section="([^"]+)"', html) == list(SECTION_ORDER)
    header = load_locale("en")["header"]
    assert all(header[key] in html for key in ("local", "offline", "sample"))
    assert 'data-finding="directory.user_count"' in html
    assert "Stadtverwaltung Musterstadt" in html
    assert "data-software-entry" in report_section(html, "attention")
    moves = report_section(html, "moves")
    assert "Nubus" in moves and "Keycloak" in moves


@pytest.mark.slow
def test_readme_examples_produce_local_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prefix = "uv run fazit "
    examples = {
        tuple(
            line.strip()
            for block in readme_code_blocks((ROOT / readme).read_text(encoding="utf-8"))
            for line in block.splitlines()
            if line.lstrip().startswith(prefix)
        )
        for readme in ("README.md", "README.de.md")
    }
    assert all(examples)
    for index, commands in enumerate(sorted(examples)):
        working = tmp_path / str(index) / "Pat Analyst@example.invalid"
        working.mkdir(parents=True)
        copyfile(ROOT / "inputs.example.yaml", working / "inputs.yaml")
        monkeypatch.chdir(working)

        for command in commands:
            result = runner.invoke(app, shlex.split(command.removeprefix(prefix)))
            assert result.exit_code == 0 and not result.stderr, f"{command}\n{result.output}"
            assert working.name not in result.stdout
            path = Path(result.stdout.splitlines()[-1])
            assert not path.is_absolute() and path.is_file()
            assert path.resolve().is_relative_to(working.resolve())
            html = path.read_text(encoding="utf-8")
            assert tuple(re.findall(r'data-section="([^"]+)"', html)) == SECTION_ORDER


def test_cli_prints_usable_paths_without_revealing_link_targets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cwd = tmp_path / "Pat Analyst@example.invalid"
    inside = cwd / "Alex Local@example.invalid"
    outside = tmp_path / "Sam Outside@example.invalid"
    inside.mkdir(parents=True)
    outside.mkdir()
    (cwd / "local").symlink_to(inside, target_is_directory=True)
    (tmp_path / "other").symlink_to(outside, target_is_directory=True)
    monkeypatch.chdir(cwd)

    demo = runner.invoke(app, ["demo", "--out", str(cwd / "local")])

    assert demo.exit_code == 0 and not demo.stderr, demo.output
    strings = load_locale("en")["cli"]
    scan, inputs, report = (
        Path("local") / name
        for name in (
            "scan-2026-11-02-en.json",
            "inputs-2026-11-02-en.yaml",
            "report-2026-11-02-en.html",
        )
    )
    assert demo.stdout.splitlines() == [
        strings["sample_scan"].format(path=scan),
        strings["sample_inputs"].format(path=inputs),
        str(report),
    ]
    assert all(path.is_file() for path in (scan, inputs, report))

    source = Path("Jo Reader@example.invalid.json")
    copyfile(scan, source)
    out = os.sep.join(("..", ".", "other"))
    rebuilt = runner.invoke(app, ["report", str(source), "--out", out])

    assert rebuilt.exit_code == 0 and not rebuilt.stderr, rebuilt.output
    assert rebuilt.stdout.splitlines() == [os.path.join(out, report.name)]
    assert (outside / report.name).is_file()


def test_cli_errors_only_name_the_supplied_input_or_generated_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cwd = tmp_path / "Pat Analyst@example.invalid"
    private = cwd / "Alex Local@example.invalid"
    private.mkdir(parents=True)
    (cwd / "local").symlink_to(private, target_is_directory=True)
    monkeypatch.chdir(cwd)

    scan = Path("Jo Reader@example.invalid.json")
    missing = runner.invoke(app, ["report", str(Path("local") / scan)])
    assert missing.exit_code == 2 and not missing.stdout
    assert missing.stderr.splitlines() == ["Error: Could not find the scan file."]

    report = "report-2026-11-02-en.html"
    (private / report).mkdir()
    blocked = runner.invoke(app, ["demo", "--out", "local"])
    assert blocked.exit_code == 2 and not blocked.stdout
    label = Path("local") / report
    assert blocked.stderr.splitlines() == [
        f"Error: The output location {label} for --out is not a regular file."
    ]


@pytest.mark.parametrize(
    ("lang", "role"), [("en", "the inputs file"), ("de", "Datei mit den Eingaben")]
)
@pytest.mark.parametrize("contents", [None, "currency: [}\n"])
def test_input_error_uses_the_role_for_an_identifying_filename(
    tmp_path: Path, lang: str, role: str, contents: str | None
) -> None:
    scan = sample_scan_path("town")
    inputs = tmp_path / "Pat Analyst@example.invalid.yaml"
    if contents is not None:
        inputs.write_text(contents, encoding="utf-8")
    out = tmp_path / "out"

    result = runner.invoke(
        app, ["report", str(scan), "--inputs", str(inputs), "--lang", lang, "--out", str(out)]
    )

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert len(result.stderr.splitlines()) == 1
    assert role in result.stderr and "@" not in result.stderr
    if contents is not None:
        assert ("line 1" if lang == "en" else "Zeile 1") in result.stderr
        assert "currency" not in result.stderr


@pytest.mark.parametrize("profile", PROFILES)
def test_report_shows_function_mapping_and_workload_evidence(tmp_path: Path, profile: str) -> None:
    source = files("fazit").joinpath("demo", "town", "scan.json")
    result = runner.invoke(
        app, ["report", str(source), "--profile", profile, "--out", str(tmp_path)]
    )

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.strip())
    assert report.is_file() and report.parent == tmp_path
    html = report.read_text(encoding="utf-8")
    mapping = load_mapping(profile, load_catalogue())
    strings = load_locale("en")
    moves = report_section(html, "moves")
    assert mapping.label["en"] in html.split("</header>", 1)[0]
    assert "<caption data-sample>" in moves
    assert re.findall(r'<tr data-function="([^"]+)"', moves) == [
        row.function for row in mapping.functions
    ]
    readiness_html = report_section(html, "readiness")
    readiness = dict(
        re.findall(r'<tr data-workload="([^"]+)" data-status="([^"]+)"', readiness_html)
    )
    appendix = report_section(html, "appendix")
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
        assert re.findall(r'href="([^"]+)"', move[0]) == [f"#readiness-{row.workload}"]
        assert readiness_html.count(f'id="readiness-{row.workload}"') == 1
        if row.checked_on is None:
            assert strings["moves"]["no_project_check"] in move[0]
            assert strings["moves"]["no_project_check"] in detail[0]
        else:
            assert row.checked_on.isoformat() in move[0] and row.checked_on.isoformat() in detail[0]
            assert row.reference_url and row.reference_url in unescape(detail[0])
        if row.note:
            assert row.note["en"] in unescape(detail[0])
    assert "data-move-evidence=" not in moves and "href=" not in appendix
    assert strings["moves"]["no_function"] in moves
    assert "Other systems send mail" in readiness_html
    assert strings["provenance"]["provided"] in readiness_html
    assert strings["source"]["sample.interview"] in readiness_html
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
    assert markup in unescape(report_section(html, "moves")) and markup not in html
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


def _sample_scan(sample: str) -> Scan:
    return load_scan(sample_scan_path(sample), load_catalogue())


@pytest.mark.parametrize(
    ("sample", "lang", "profile"),
    [
        ("town", "en", "opendesk"),
        ("nonprofit", "de", "opendesk"),
        ("town", "en", "nextcloud"),
        ("nonprofit", "de", "nextcloud"),
        ("town", "de", "generic"),
        ("nonprofit", "en", "generic"),
    ],
)
def test_demo_writes_the_selected_sample_language_and_profile(
    tmp_path: Path, sample: str, lang: str, profile: str
) -> None:
    scan = _sample_scan(sample)
    stamp = f"{scan.generated_at[:10]}-{lang}"
    report = tmp_path / f"report-{stamp}.html"
    scan_path = tmp_path / f"scan-{stamp}.json"
    inputs_path = tmp_path / f"inputs-{stamp}.yaml"

    result = runner.invoke(
        app,
        ["demo", "--lang", lang, "--sample", sample, "--profile", profile, "--out", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    strings = load_locale(lang)["cli"]
    assert result.stdout.splitlines() == [
        strings["sample_scan"].format(path=scan_path),
        strings["sample_inputs"].format(path=inputs_path),
        str(report),
    ]
    assert not result.stderr and report.is_file()
    assert load_scan(scan_path, load_catalogue()) == scan
    assert inputs_path.read_bytes() == sample_inputs_path(sample).read_bytes()
    html = report.read_text(encoding="utf-8")
    assert f'<html lang="{lang}">' in html
    assert load_locale(lang)["header"]["sample"] in html
    mapping = load_mapping(profile, load_catalogue())
    assert mapping.label[lang] in html.split("</header>", 1)[0]
    moves = report_section(html, "moves")
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

    relabeled = render_report(replace(scan, source_kind="import"), lang="en")
    assert strings["header"]["sample"] in relabeled
    assert "data-sample" in relabeled


def test_provided_answer_source_is_independent_of_scan_source() -> None:
    scan = _sample_scan("town")
    strings = load_locale("en")
    provided = scan.finding("device_management.device_count")
    assert provided is not None and provided.source == "sample.interview"
    assert strings["source"]["sample.interview"] in render_report(scan, lang="en")

    findings = tuple(
        replace(finding, source="interview") if finding.id == provided.id else finding
        for finding in scan.findings
    )
    html = render_report(replace(scan, findings=findings), lang="en")
    device_row = re.search(r'<tr data-finding="device_management.device_count".*?</tr>', html, re.S)
    assert device_row is not None
    assert strings["source"]["interview"] in device_row[0]
    assert strings["source"]["sample.interview"] not in device_row[0]
    mail_row = re.search(r'<tr data-finding="mail.other_systems_send_mail".*?</tr>', html, re.S)
    assert mail_row is not None
    assert strings["source"]["sample.interview"] in mail_row[0]
    assert strings["source"]["interview"] not in mail_row[0]


@pytest.mark.parametrize(("sample", "lang"), [("town", "en"), ("nonprofit", "de")])
def test_scan_only_report_explains_readiness_and_missing_evidence(
    tmp_path: Path, sample: str, lang: str
) -> None:
    scan_path = files("fazit").joinpath("demo", sample, "scan.json")
    result = runner.invoke(app, ["report", str(scan_path), "--lang", lang, "--out", str(tmp_path)])
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file() and not result.stderr
    html = path.read_text(encoding="utf-8")
    strings = load_locale(lang)
    table = report_section(html, "readiness")
    assert "%" not in table
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
        assert strings["status"][status] in readiness_row(table, workload)
    segments = re.findall(r'data-segment="([^"]+)" data-count="(\d+)"', table)
    assert segments == [
        (status, str(total))
        for status in STATUSES
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
        mail = readiness_row(table, "mail")
        assert 'data-status="needs_work" data-incomplete' in mail
        assert strings["collector"]["exchange_recipients"] in mail
        for text in strings["reason"]["needs_recipient_export"].values():
            assert text in mail
        assert 'data-reason="needs_recipient_export"' in mail
        assert 'data-rule="mail-other-systems"' in html
    else:
        onedrive = readiness_row(table, "onedrive")
        for text in (
            "52,5 GB",
            strings["provenance"]["measured"],
            strings["source"]["sample.onedrive_usage"],
            "5. November 2026",
            "9. Mai bis 4. Nov. 2026",
            "Teilweise, 18 von 20 geprüft, 2 fehlgeschlagen",
        ):
            assert text in onedrive

    appendix = html.split('data-section="appendix"', 1)[1]
    assert appendix.count(strings["appendix"]["ready_evidence"]) == len(catalogue.workloads)
    assert "status.yaml" in appendix


def test_changed_rule_changes_demo_status_and_escapes_the_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scan = files("fazit").joinpath("demo", "town", "scan.json")
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
    file.write_bytes(b"Keep this")
    result = runner.invoke(app, ["demo", "--lang", "de", "--out", str(file)])

    expected = load_locale("de")["errors"]["out_dir"].format(file=file, field="--out")
    assert result.exit_code == 2
    assert result.stderr.splitlines() == [f"Fehler: {expected}"]
    assert not result.stdout
    assert file.read_bytes() == b"Keep this"


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
    assert "planted" not in result.stderr and "fazit" not in result.stderr


def test_version_works_without_a_command() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


@pytest.mark.parametrize("arguments", [[], ["--debug"]])
def test_missing_command_shows_help(arguments: list[str]) -> None:
    result = runner.invoke(app, arguments)
    output = ANSI_STYLE.sub("", result.output)
    assert result.exit_code == 2
    assert "Usage:" in output and "COMMAND [ARGS]..." in output
    assert all(option in output for option in ("--debug", "demo", "report"))


def test_module_entry_point() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "fazit", "--version"], capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 0 and not result.stderr, result.stderr
    assert result.stdout.strip() == __version__


def test_report_usage_uses_the_documented_argument_name_in_english() -> None:
    failure = runner.invoke(app, ["report", "--lang", "de"])
    help_result = runner.invoke(app, ["report", "--help"])

    assert failure.exit_code == 2 and "Missing argument" in failure.stderr
    assert help_result.exit_code == 0
    for output in (ANSI_STYLE.sub("", failure.stderr), ANSI_STYLE.sub("", help_result.stdout)):
        usage = next(line for line in output.splitlines() if "Usage:" in line)
        assert usage.rstrip().endswith("[OPTIONS] SCAN_JSON")


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
    scan = files("fazit").joinpath("demo", "town", "scan.json")
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
    assert load_mapping(profile, load_catalogue()).label[lang] in header
    assert answers.name not in html


@pytest.mark.parametrize(
    ("lang", "message"),
    [
        (None, "Error: Remove the unrecognised field on line 4 of {file}."),
        ("de", "Fehler: Entfernen Sie das unbekannte Feld in Zeile 4 der Datei {file}."),
    ],
)
def test_report_input_errors_use_the_flag_language(
    tmp_path: Path, lang: str | None, message: str
) -> None:
    scan = files("fazit").joinpath("demo", "town", "scan.json")
    answers = tmp_path / "office-interview.yaml"
    answers.write_text("# Interview\nlanguage: de\n\ncurency: EUR\n", encoding="utf-8")
    out = tmp_path / "out"
    options = [] if lang is None else ["--lang", lang]

    result = runner.invoke(
        app, ["report", str(scan), "--inputs", str(answers), "--out", str(out), *options]
    )

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert result.stderr.splitlines() == [message.format(file=answers.name)]


@pytest.mark.parametrize("kind", ["missing", "directory"])
def test_report_rejects_missing_or_directory_inputs(tmp_path: Path, kind: str) -> None:
    scan = files("fazit").joinpath("demo", "town", "scan.json")
    answers = tmp_path / "office-interview.yaml"
    if kind == "directory":
        answers.mkdir()
    out = tmp_path / "out"

    result = runner.invoke(app, ["report", str(scan), "--inputs", str(answers), "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert len(result.stderr.splitlines()) == 1 and answers.name in result.stderr


@pytest.mark.parametrize(("lang", "line_label"), [("en", "line"), ("de", "Zeile")])
@pytest.mark.parametrize(
    ("name", "content", "code", "line", "field"),
    [
        ("inputs.yaml", "currency: EUR\ncurrency: CHF\n", "duplicate_key_field", 2, "currency"),
        (
            "inputs.yaml",
            "current_costs:\n  'Pat Analyst@example.invalid': 1\n"
            "  'Pat Analyst@example.invalid': 2\n",
            "duplicate_key",
            3,
            None,
        ),
        (
            "inputs.yaml",
            "'target_costs.partial_exit.users': 1\n'target_costs.partial_exit.users': 2\n",
            "duplicate_key",
            2,
            None,
        ),
        (
            "inputs.yaml",
            "current_costs:\n  other_it_per_year: .nan\n",
            "non_finite_number_field",
            2,
            "current_costs.other_it_per_year",
        ),
        (
            "inputs.yaml",
            "target_costs:\n  partial_exit:\n    users: [1, }\n",
            "invalid_yaml",
            3,
            None,
        ),
        *[
            (
                "inputs.yaml",
                f"# Interview date\ncurrency: EUR\n\nas_of: {date}\n",
                "invalid_scalar_field",
                4,
                "as_of",
            )
            for date in ("2026-02-30", '"2026-02-30"')
        ],
        (
            "scan.json",
            '{\n "tool": {"name": "fazit",\n "n\\u0061me": "fazit"}\n}',
            "duplicate_key_document",
            None,
            None,
        ),
        (
            "scan.json",
            '{\n "Pat Analyst@example.invalid": {"name": "other",\n "name": "copy"}\n}',
            "duplicate_key_document",
            None,
            None,
        ),
        (
            "scan.json",
            '{"findings": [{\n "value": 1e999\n}]}',
            "non_finite_number_document",
            None,
            None,
        ),
        ("scan.json", '{"findings": [{\n "value": }]}', "invalid_json", 2, None),
        ("scan.json", '{\n "Pat Analyst@example.invalid": }', "invalid_json", 2, None),
    ],
)
def test_parse_errors_report_available_positions_without_leaking_fields(
    tmp_path: Path,
    name: str,
    content: str,
    code: str,
    line: int | None,
    field: str | None,
    lang: str,
    line_label: str,
) -> None:
    source = tmp_path / name
    source.write_text(content, encoding="utf-8")
    out = tmp_path / "out"
    command = ["report", "--lang", lang, "--out", str(out)]
    if name == "inputs.yaml":
        command += [str(sample_scan_path("town")), "--inputs", str(source)]
    else:
        command.append(str(source))

    result = runner.invoke(app, command)

    assert result.exit_code == 2 and not result.stdout and not out.exists(), result.output
    strings = load_locale(lang)
    message = strings["errors"][code].format(file=name, line=line, field=field)
    assert result.stderr.splitlines() == [strings["cli"]["error_prefix"].format(message=message)]
    assert name in message and "$" not in message and "Pat Analyst" not in message
    if line is not None:
        assert f"{line_label} {line}" in message
    if field is not None:
        assert field in message
    if code in ("invalid_json", "invalid_yaml"):
        assert "value" not in message and "users" not in message


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
    assert html == demo_report.read_text(encoding="utf-8")
    macro = re.compile(r'<tr data-finding="office_files.kind.macro".*?</tr>', re.S)
    assert "Sample input" in macro.search(html)[0]
    assert 'data-cost-origin="sample_input">Sample input' in report_section(html, "costs")
    assert "answers_are_sample: true" in answers.read_text(encoding="utf-8")

    own = tmp_path / "own-inputs.yaml"
    text = answers.read_text(encoding="utf-8")
    own.write_text(
        text.replace("answers_are_sample: true", "answers_are_sample: false").replace(
            "office_files.kind.macro: 271", "office_files.kind.macro: 6"
        ),
        encoding="utf-8",
    )
    rebuilt = runner.invoke(
        app, ["report", str(source), "--inputs", str(own), "--out", str(tmp_path / "own")]
    )
    assert rebuilt.exit_code == 0, rebuilt.output
    own_html = Path(rebuilt.stdout.strip()).read_text(encoding="utf-8")
    assert "6 files" in macro.search(own_html)[0] and "Provided" in macro.search(own_html)[0]
    assert "Sample input" not in macro.search(own_html)[0]
    own_costs = report_section(own_html, "costs")
    assert 'data-cost-origin="provided">Provided' in own_costs
    assert 'data-cost-origin="sample_input"' not in own_costs
    assert 'data-cost-origin="invented"' in own_costs

    out = tmp_path / "scan-only"
    scan_only = runner.invoke(app, ["report", str(source), "--lang", "de", "--out", str(out)])
    assert scan_only.exit_code == 0, scan_only.output
    report = out / "report-2026-11-02-de.html"
    assert scan_only.stdout.splitlines() == [str(report)] and not scan_only.stderr
    assert list(out.iterdir()) == [report]
    scan_html = report.read_text(encoding="utf-8")
    assert 'lang="de"' in scan_html and "2. November 2026" in scan_html
    assert 'data-workload="telephony" data-status="unknown"' in report_section(
        scan_html, "readiness"
    )
    assert "Diese Organisation" in scan_html.split("</header>", 1)[0]


@pytest.mark.parametrize(
    ("kind", "code"),
    [
        ("missing", "file_not_found"),
        ("directory", "is_directory"),
        pytest.param(
            "unreadable",
            "not_readable",
            marks=pytest.mark.skipif(
                os.name != "posix" or os.geteuid() == 0, reason="Requires POSIX permissions"
            ),
        ),
        ("not_utf8", "not_utf8"),
        ("schema", "schema_version"),
    ],
)
@pytest.mark.parametrize("lang", ["en", "de"])
def test_report_errors_name_the_file_and_field(
    tmp_path: Path, kind: str, code: str, lang: str
) -> None:
    scan = tmp_path / "inventory.json"
    if kind == "directory":
        scan.mkdir()
    elif kind == "unreadable":
        scan.touch(mode=0)
    elif kind == "not_utf8":
        scan.write_bytes(b"\xff")
    elif kind == "schema":
        scan.write_text('{"schema_version": "2.0"}', encoding="utf-8")
    out = tmp_path / "out"
    result = runner.invoke(app, ["report", str(scan), "--out", str(out), "--lang", lang])

    strings = load_locale(lang)
    message = strings["errors"][code].format(
        file=scan.name, field="schema_version", found="2.0", supported="1.x"
    )
    assert result.exit_code == 2
    assert result.stderr.splitlines() == [strings["cli"]["error_prefix"].format(message=message)]
    assert not result.stdout and not out.exists()


def test_debug_reraises_the_underlying_input_error(tmp_path: Path) -> None:
    scan = tmp_path / "missing.json"
    with pytest.raises(InputError, match="file_not_found"):
        runner.invoke(app, ["--debug", "report", str(scan)], catch_exceptions=False)


@pytest.mark.parametrize("case", ["alias-expansion", "oversized-yaml", "oversized-json"])
def test_report_bounds_untrusted_inputs(tmp_path: Path, case: str) -> None:
    sample = files("fazit").joinpath("demo", "town", "scan.json")
    scan = tmp_path / "inventory.json"
    answers = tmp_path / "answers.yaml"
    scan.write_bytes(sample.read_bytes())
    if case == "alias-expansion":
        lines = ["a0: &a0 [0]"]
        for level in range(1, 11):
            repeated = ",".join([f"*a{level - 1}"] * 10)
            lines.append(f"a{level}: &a{level} [{repeated}]")
        text = "\n".join(lines).ljust(700)
        assert len(text.encode()) == 700
        answers.write_text(text, encoding="utf-8")
    else:
        path = scan if case == "oversized-json" else answers
        with path.open("ab") as stream:
            stream.truncate(2 * 1024 * 1024 + 1)
    out = tmp_path / "out"
    options = [] if case == "oversized-json" else ["--inputs", str(answers)]

    result = subprocess.run(
        ["uv", "run", "--no-sync", "fazit", "report", str(scan), *options, "--out", str(out)],
        capture_output=True,
        text=True,
        timeout=1,
    )

    strings = load_locale("en")
    code = "yaml_anchors" if case == "alias-expansion" else "file_too_large"
    file_name = scan.name if case == "oversized-json" else answers.name
    expected = strings["errors"][code].format(file=file_name, line=1)
    assert result.returncode == 2
    assert result.stderr.splitlines() == [strings["cli"]["error_prefix"].format(message=expected)]
    assert not result.stdout and not out.exists()


@pytest.mark.parametrize(
    ("field", "maximum", "oversized"),
    [
        pytest.param("users", "999999999999", "1000000000000", id="count-boundary"),
        pytest.param("users", "999999999999", "9" * 4300, id="huge-count"),
        pytest.param("training_days_per_person", "999999999999", "9" * 4400, id="huge-days"),
        pytest.param(
            "training_days_per_person", '"999999999999.0"', '"999999999999.1"', id="decimal-days"
        ),
        pytest.param(
            "training_days_per_person",
            '"999999999999.0"',
            f'"{"9" * 4400}"',
            id="huge-decimal-days",
        ),
        pytest.param("training_days_per_person", '"0.123456"', '"0.1234567"', id="decimal-places"),
    ],
)
def test_report_bounds_cost_quantities(
    tmp_path: Path, field: str, maximum: str, oversized: str
) -> None:
    scan = sample_scan_path("town")
    inputs = sample_inputs_path("town").read_text(encoding="utf-8")
    answers = tmp_path / "answers.yaml"
    for literal, accepted in ((maximum, True), (oversized, False)):
        text = re.sub(rf"^    {field}: .+$", f"    {field}: {literal}", inputs, count=1, flags=re.M)
        answers.write_text(text, encoding="utf-8")
        out = tmp_path / ("accepted" if accepted else "rejected")
        args = ["report", str(scan), "--inputs", str(answers), "--out", str(out)]
        result = runner.invoke(app, args)
        if accepted:
            assert result.exit_code == 0 and not result.stderr, result.output
            assert Path(result.stdout.strip()).is_file()
        else:
            assert result.exit_code == 2 and not result.stdout and not out.exists(), result.output
            assert len(result.stderr.splitlines()) == 1
            assert answers.name in result.stderr
            assert f"target_costs.partial_exit.{field}" in result.stderr


@pytest.mark.parametrize(
    ("finding_id", "maximum", "oversized"),
    [
        pytest.param("directory.user_count", 10**12 - 1, str(10**12), id="count-boundary"),
        pytest.param("directory.user_count", 10**12 - 1, "9" * 4400, id="huge-count"),
        pytest.param("mail.storage_bytes", 2**63 - 1, str(2**63), id="byte-boundary"),
    ],
)
def test_report_bounds_scan_integers(
    tmp_path: Path, finding_id: str, maximum: int, oversized: str
) -> None:
    sample = json.loads(sample_scan_path("town").read_bytes())
    index, row = next(
        (i, row) for i, row in enumerate(sample["findings"]) if row["id"] == finding_id
    )
    row["value"] = "replace-with-integer"
    text = json.dumps(sample)
    scan = tmp_path / "inventory.json"
    for literal, accepted in ((str(maximum), True), (oversized, False)):
        scan.write_text(text.replace('"replace-with-integer"', literal), encoding="utf-8")
        out = tmp_path / ("accepted" if accepted else "rejected")
        result = runner.invoke(app, ["report", str(scan), "--out", str(out), "--lang", "de"])
        if accepted:
            assert result.exit_code == 0 and not result.stderr, result.output
            assert Path(result.stdout.strip()).is_file()
        else:
            assert result.exit_code == 2 and not result.stdout and not out.exists(), result.output
            assert len(result.stderr.splitlines()) == 1
            assert scan.name in result.stderr and f"findings[{index}].value" in result.stderr


@pytest.mark.parametrize(
    "amount", ["1000000000000000", "0.001", "9" * 200_000], ids=["integer", "fraction", "long"]
)
def test_report_rejects_amounts_outside_the_supported_precision(
    tmp_path: Path, amount: str
) -> None:
    scan = files("fazit").joinpath("demo", "town", "scan.json")
    answers = tmp_path / "answers.yaml"
    answers.write_text(
        f'currency: EUR\ncurrent_costs: {{other_it_per_year: "{amount}"}}\n', encoding="utf-8"
    )
    out = tmp_path / "out"
    result = runner.invoke(app, ["report", str(scan), "--inputs", str(answers), "--out", str(out)])
    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert len(result.stderr.splitlines()) == 1
    assert "current_costs.other_it_per_year" in result.stderr and answers.name in result.stderr


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="Requires POSIX permissions")
def test_report_refuses_an_unwritable_output_directory(tmp_path: Path) -> None:
    scan = files("fazit").joinpath("demo", "town", "scan.json")
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

    for module in (datetime, i18n, report_module, validation):
        patch.setattr(module, "date", SystemDate)
    for module in (datetime, model):
        patch.setattr(module, "datetime", SystemDateTime)


def test_demo_and_report_use_the_scan_date_independently_of_the_clock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    demo = tmp_path / "demo"
    original = demo / "report-2026-11-02-en.html"
    with monkeypatch.context() as patch:
        _set_system_day(patch, date(2027, 1, 1))
        result = runner.invoke(app, ["demo", "--out", str(demo)])
    assert result.exit_code == 0 and not result.stderr, result.output
    assert Path(result.stdout.splitlines()[-1]) == original
    assert "2 November 2026" in original.read_text(encoding="utf-8").split("</header>", 1)[0]

    scan = demo / "scan-2026-11-02-en.json"
    inputs = demo / "inputs-2026-11-02-en.yaml"
    out = tmp_path / "rebuilt"
    with monkeypatch.context() as patch:
        _set_system_day(patch, date(2031, 12, 31))
        result = runner.invoke(
            app, ["report", str(scan), "--inputs", str(inputs), "--out", str(out)]
        )
    assert result.exit_code == 0 and not result.stderr, result.output
    rebuilt = out / original.name
    assert Path(result.stdout.strip()) == rebuilt
    assert rebuilt.read_bytes() == original.read_bytes()


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
