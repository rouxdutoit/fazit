# SPDX-License-Identifier: AGPL-3.0-or-later
import json
from collections.abc import Iterator
from copy import deepcopy
from dataclasses import replace
from importlib.resources import files
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from fazit import cli
from fazit.catalogue import load_catalogue
from fazit.i18n import load_locale
from fazit.model import load_scan, load_scan_text, scan_to_json

PLANTED_SCAN = Path(__file__).parent / "fixtures" / "planted_scan.json"
PRIVATE_TEXT = ("Mustermann", "eyJhbGci", "planted-secret")
IGNORED_KEYS = ("operator", "granted_by", "owner", "access_token", "admin_contact", "display_name")
NAME = "Erika Mustermann"
ADDRESS = "erika.mustermann@example.invalid"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJleGFtcGxlIn0.test-signature"

runner = CliRunner()

type Position = tuple[str | int, ...]


def _assert_no_private_text(result: Result, out: Path, *planted: str) -> None:
    files_written = list(out.iterdir()) if out.exists() else []
    output = [result.stdout, result.stderr]
    for file in files_written:
        output.extend((file.name, file.read_text(encoding="utf-8")))
    for text in planted:
        assert all(text not in part for part in output), text


def _sample_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    sample = tmp_path / "demo" / "town"
    sample.mkdir(parents=True)
    monkeypatch.setattr(cli, "files", lambda package: tmp_path)
    return sample


def test_ignored_scan_data_leaves_only_a_count_in_the_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalogue = load_catalogue()
    scan = load_scan(PLANTED_SCAN, catalogue)
    assert scan.dropped_count == 8
    ignored = (*IGNORED_KEYS, "mail.largest_mailboxes", *PRIVATE_TEXT)
    copied = scan_to_json(scan)
    assert all(text not in copied for text in ignored)
    assert copied == json.dumps(json.loads(copied), sort_keys=True, indent=2) + "\n"
    assert load_scan_text(copied, PLANTED_SCAN.name, catalogue) == replace(scan, dropped_count=0)

    out = tmp_path / "out"
    result = runner.invoke(cli.app, ["report", str(PLANTED_SCAN), "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [str(out / "report-2026-11-02-en.html")]
    assert not result.stderr
    html = Path(result.stdout.strip()).read_text(encoding="utf-8")
    assert 'data-ignored-count="8"' in html
    assert load_locale("en")["appendix"]["ignored"].format(count=8) in html
    _assert_no_private_text(result, out, *ignored)

    sample = _sample_directory(tmp_path, monkeypatch)
    (sample / "scan.json").write_bytes(PLANTED_SCAN.read_bytes())
    (sample / "inputs.yaml").write_text("{}\n", encoding="utf-8")
    demo_out = tmp_path / "demo-out"
    result = runner.invoke(cli.app, ["demo", "--out", str(demo_out)])
    assert result.exit_code == 0, result.output
    assert (demo_out / "scan-2026-11-02-en.json").read_text(encoding="utf-8") == copied
    _assert_no_private_text(result, demo_out, *ignored)


def _positions(value: object, path: Position = ()) -> Iterator[Position]:
    if isinstance(value, dict):
        children = value.items()
    elif isinstance(value, list):
        children = enumerate(value)
    else:
        return
    for key, item in children:
        position = (*path, key)
        yield position
        yield from _positions(item, position)


@pytest.mark.parametrize("planted", [NAME, ADDRESS, TOKEN], ids=["name", "address", "token"])
@pytest.mark.parametrize("placement", ["key", "value"])
def test_privacy_in_every_scan_field_and_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, planted: str, placement: str
) -> None:
    catalogue = load_catalogue()
    strings = load_locale("en")
    monkeypatch.setattr(cli, "load_catalogue", lambda: catalogue)
    monkeypatch.setattr(cli, "load_locale", lambda lang: strings)
    original = json.loads(PLANTED_SCAN.read_text(encoding="utf-8"))
    scan_file = tmp_path / "scan.json"

    for index, position in enumerate(_positions(original)):
        key = position[-1]
        if placement == "key" and isinstance(key, int):
            continue
        data = deepcopy(original)
        parent = data
        for part in position[:-1]:
            parent = parent[part]
        if placement == "key":
            parent[planted] = parent.pop(key)
        else:
            parent[key] = planted

        scan_file.write_text(json.dumps(data), encoding="utf-8")
        out = tmp_path / str(index)
        result = runner.invoke(cli.app, ["report", str(scan_file), "--out", str(out)])
        assert result.exit_code in (0, 2), (position, result.exception)
        _assert_no_private_text(result, out, *PRIVATE_TEXT, planted)
        if planted == ADDRESS:
            assert result.exit_code == 2, position
            assert strings["errors"]["contains_at"].split("{")[0] in result.stderr
        if result.exit_code == 0:
            copied = scan_to_json(load_scan(scan_file, catalogue))
            assert all(text not in copied for text in (*PRIVATE_TEXT, planted)), position
            assert len(list(out.glob("*.html"))) == 1 and not result.stderr
        else:
            assert not out.exists() and not result.stdout, position
            assert len(result.stderr.splitlines()) == 1, position


@pytest.mark.parametrize(
    ("group", "index", "field", "value", "planted"),
    [
        (
            "findings",
            0,
            "source",
            "https://example.invalid/?token=planted-secret",
            "planted-secret",
        ),
        ("collectors", 1, "reason", "Access denied to Erika Mustermann", "Mustermann"),
        ("findings", 1, "missing_reason", "erika_mustermann", "erika_mustermann"),
    ],
)
def test_report_rejects_unregistered_evidence_codes(
    tmp_path: Path, group: str, index: int, field: str, value: str, planted: str
) -> None:
    data = json.loads(PLANTED_SCAN.read_text(encoding="utf-8"))
    data[group][index][field] = value
    source = tmp_path / "scan.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    out = tmp_path / "out"

    result = runner.invoke(cli.app, ["report", str(source), "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert f"{group}[{index}].{field}" in result.stderr
    _assert_no_private_text(result, out, planted)


@pytest.mark.parametrize(
    "inputs",
    [
        f'organisation_name: "{ADDRESS}"\n',
        f'windows_only_software:\n  - name: "{ADDRESS}"\n',
    ],
    ids=["organisation", "software"],
)
def test_demo_rejects_addresses_in_inputs_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, inputs: str
) -> None:
    source = files("fazit").joinpath("demo", "town", "scan.json")
    sample = _sample_directory(tmp_path, monkeypatch)
    (sample / "scan.json").write_bytes(source.read_bytes())
    (sample / "inputs.yaml").write_text(inputs, encoding="utf-8")
    out = tmp_path / "out"

    result = runner.invoke(cli.app, ["demo", "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert "inputs.yaml" in result.stderr and "at sign" in result.stderr
    _assert_no_private_text(result, out, ADDRESS)
