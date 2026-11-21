# SPDX-License-Identifier: AGPL-3.0-or-later
import re
import socket
from dataclasses import replace
from importlib.resources import files
from pathlib import Path

import pytest
from typer.testing import CliRunner

from m365_exit_scan import __version__
from m365_exit_scan.catalogue import load_catalogue
from m365_exit_scan.cli import app
from m365_exit_scan.errors import InputError
from m365_exit_scan.i18n import load_locale
from m365_exit_scan.model import Coverage, Scan, load_scan_text
from m365_exit_scan.parsing import read_text
from m365_exit_scan.report import render_report, report_file_name

runner = CliRunner()


def test_demo_writes_one_local_report(tmp_path: Path) -> None:
    result = runner.invoke(app, ["demo", "--out", str(tmp_path)])

    assert result.exit_code == 0, result.output
    report = tmp_path / "report-2026-11-02-en.html"
    assert result.stdout.splitlines() == [str(report)]
    assert report.is_file()
    html = report.read_text(encoding="utf-8")
    assert re.findall(r'data-section="([^"]+)"', html) == ["header", "found", "appendix", "footer"]
    header = load_locale("en")["header"]
    assert all(header[key] in html for key in ("local", "offline", "sample"))
    assert 'data-finding="directory.user_count"' in html


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


def test_demo_refuses_a_symlink_destination(tmp_path: Path) -> None:
    outside = tmp_path / "outside.html"
    outside.write_bytes(b"Preserve this file")
    out = tmp_path / "report"
    out.mkdir()
    destination = out / "report-2026-11-02-en.html"
    destination.symlink_to(outside)

    result = runner.invoke(app, ["demo", "--out", str(out)])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "symbolic link" in result.stderr
    assert destination.is_symlink()
    assert outside.read_bytes() == b"Preserve this file"


def _sample_scan(name: str) -> Scan:
    source = files("m365_exit_scan").joinpath("demo", name, "scan.json")
    return load_scan_text(read_text(source), source.name, load_catalogue())


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize(("sample", "date"), [("town", "2026-11-02"), ("nonprofit", "2026-11-05")])
def test_cli_renders_both_samples_in_both_languages(
    tmp_path: Path, lang: str, sample: str, date: str
) -> None:
    result = runner.invoke(
        app, ["demo", "--lang", lang, "--sample", sample, "--out", str(tmp_path)]
    )

    assert result.exit_code == 0, result.output
    report = tmp_path / f"report-{date}-{lang}.html"
    assert result.stdout.splitlines() == [str(report)]
    assert not result.stderr and report.is_file()
    html = report.read_text(encoding="utf-8")
    assert f'<html lang="{lang}">' in html
    assert load_locale(lang)["header"]["sample"] in html


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
    assert strings["source"]["inputs_yaml"] in html
    assert strings["source"]["sample.interview"] not in html


def test_nonprofit_partial_coverage_has_all_counts_and_localised_dates() -> None:
    html = render_report(_sample_scan("nonprofit"), lang="de")
    row = re.search(r'<tr data-finding="onedrive.storage_bytes"[^>]*>(.*?)</tr>', html, re.S)
    assert row is not None
    assert "Teilweise, 18 von 20 geprüft, 2 fehlgeschlagen" in row[1]
    assert "52,5 GB" in row[1]
    assert "5. November 2026" in row[1]
    assert "9. Mai 2026 bis 4. November 2026" in row[1]


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
