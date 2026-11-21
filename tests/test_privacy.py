# SPDX-License-Identifier: AGPL-3.0-or-later
import json
from collections.abc import Iterator
from copy import deepcopy
from dataclasses import replace
from importlib.resources import files
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from befund import cli
from befund.catalogue import load_catalogue
from befund.i18n import load_locale
from befund.model import ServicePlan, load_scan, load_scan_text, scan_to_json
from befund.rules import load_service_plans

PLANTED_SCAN = Path(__file__).parent / "fixtures" / "planted_scan.json"
PRIVATE_TEXT = ("Mustermann", "eyJhbGci", "planted-secret")
IGNORED_KEYS = ("operator", "granted_by", "owner", "access_token", "admin_contact", "display_name")
NAME = "Erika Mustermann"
ADDRESS = "erika.mustermann@example.invalid"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJleGFtcGxlIn0.test-signature"
SINGLE_TOKENS = ("ReviewMarker", "Erika_Mustermann")

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
    copied = scan_to_json(scan, plans=load_service_plans(catalogue))
    assert all(text not in copied for text in ignored)
    assert copied == json.dumps(json.loads(copied), sort_keys=True, indent=2) + "\n"
    assert scan.licences is not None
    (product,) = scan.licences.products
    anonymous = replace(
        product, sku_part_number=None, sku_guid=None, service_plans=(ServicePlan(None, None),)
    )
    assert load_scan_text(copied, PLANTED_SCAN.name, catalogue) == replace(
        scan, licences=replace(scan.licences, products=(anonymous,)), dropped_count=0
    )

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


def test_unregistered_licence_identifiers_are_private_in_both_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = files("befund").joinpath("demo", "town", "scan.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    suite, phone, reporting = data["licences"]["products"]
    suite["sku_part_number"] = suite["sku_part_number"].lower()
    suite["service_plans"].append(
        {"name": SINGLE_TOKENS[0], "guid": phone["service_plans"][0]["guid"]}
    )
    private_guid = "f8c16d36-b9e3-460e-8ac2-54b6d950986f"
    phone["sku_part_number"] = SINGLE_TOKENS[0]
    reporting["sku_part_number"] = SINGLE_TOKENS[1]
    reporting["sku_guid"] = private_guid
    sample = _sample_directory(tmp_path, monkeypatch)
    scan = sample / "scan.json"
    scan.write_text(json.dumps(data), encoding="utf-8")
    (sample / "inputs.yaml").write_text("{}\n", encoding="utf-8")

    for command in (["report", str(scan)], ["demo"]):
        out = tmp_path / f"{command[0]}-out"
        result = runner.invoke(cli.app, [*command, "--out", str(out)])
        assert result.exit_code == 0 and not result.stderr, result.output
        _assert_no_private_text(result, out, *SINGLE_TOKENS, private_guid)
        html = Path(result.stdout.splitlines()[-1]).read_text(encoding="utf-8")
        assert 'data-product="SPE_E3"' in html
        assert "Unregistered product 1" in html and "Unregistered product 2" in html
        assert "Unclassified service plans in this product: 1." in html

    (copied_scan,) = (tmp_path / "demo-out").glob("*.json")
    copied_suite, copied_phone, copied_reporting = json.loads(copied_scan.read_bytes())["licences"][
        "products"
    ]
    assert copied_suite["sku_part_number"] == "SPE_E3"
    assert copied_suite["service_plans"][-1] == {
        "name": None,
        "guid": phone["service_plans"][0]["guid"],
    }
    for product in (copied_phone, copied_reporting):
        assert product["sku_part_number"] is None and product["sku_guid"] is None
    rebuilt = runner.invoke(
        cli.app, ["report", str(copied_scan), "--out", str(tmp_path / "rebuild")]
    )
    assert rebuilt.exit_code == 0, rebuilt.output
    copy_html = Path(rebuilt.stdout.strip()).read_text(encoding="utf-8")
    assert "Unregistered product 2" in copy_html
    assert "Unclassified service plans in this product: 1." in copy_html
    original_html = (tmp_path / "report-out" / "report-2026-11-02-en.html").read_text(
        encoding="utf-8"
    )
    assert copy_html == original_html


@pytest.mark.parametrize("planted", SINGLE_TOKENS)
def test_unknown_input_key_reports_position(tmp_path: Path, planted: str) -> None:
    answers = tmp_path / "answers.yaml"
    answers.write_text(f"currency: EUR\ncurrent_costs:\n  {planted}: null\n", encoding="utf-8")
    out = tmp_path / "out"
    result = runner.invoke(
        cli.app, ["report", str(PLANTED_SCAN), "--inputs", str(answers), "--out", str(out)]
    )
    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert len(result.stderr.splitlines()) == 1
    assert answers.name in result.stderr and "current_costs[0]" in result.stderr
    _assert_no_private_text(result, out, planted)


def test_cli_escapes_control_characters_in_file_paths(tmp_path: Path) -> None:
    out = tmp_path / "out\n\x1b\u202e"
    result = runner.invoke(cli.app, ["demo", "--out", str(out)])
    assert result.exit_code == 0 and not result.stderr, result.output
    assert len(result.stdout.splitlines()) == 3
    assert all(r"out\n\x1b\u202e" in line for line in result.stdout.splitlines())
    assert (out / "report-2026-11-02-en.html").is_file()

    source = tmp_path / "missing\r\t\x1b\u202e.json"
    failure = runner.invoke(cli.app, ["report", str(source), "--out", str(out)])
    assert failure.exit_code == 2 and not failure.stdout
    assert len(failure.stderr.splitlines()) == 1
    assert r"missing\r\t\x1b\u202e.json" in failure.stderr


@pytest.mark.parametrize("character", ["\0", "\u202e"], ids=["nul", "bidi"])
@pytest.mark.parametrize("field", ["organisation_name", "windows_only_software[0].name"])
def test_report_rejects_nonprintable_names(tmp_path: Path, character: str, field: str) -> None:
    answers = tmp_path / "answers.yaml"
    name = json.dumps(f"Example{character}Name")
    prefix = (
        "organisation_name: "
        if field == "organisation_name"
        else "windows_only_software:\n  - name: "
    )
    answers.write_text(f"{prefix}{name}\n", encoding="utf-8")
    out = tmp_path / "out"
    result = runner.invoke(
        cli.app, ["report", str(PLANTED_SCAN), "--inputs", str(answers), "--out", str(out)]
    )
    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert len(result.stderr.splitlines()) == 1
    assert field in result.stderr and answers.name in result.stderr
    _assert_no_private_text(result, out, character)


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


@pytest.mark.slow
@pytest.mark.parametrize(
    "planted",
    [NAME, ADDRESS, TOKEN, *SINGLE_TOKENS],
    ids=["name", "address", "token", "single-token", "underscore-name"],
)
@pytest.mark.parametrize("placement", ["key", "value"])
def test_privacy_in_every_scan_field_and_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, planted: str, placement: str
) -> None:
    catalogue = load_catalogue()
    plans = load_service_plans(catalogue)
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
            copied = scan_to_json(load_scan(scan_file, catalogue), plans=plans)
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
    source = files("befund").joinpath("demo", "town", "scan.json")
    sample = _sample_directory(tmp_path, monkeypatch)
    (sample / "scan.json").write_bytes(source.read_bytes())
    (sample / "inputs.yaml").write_text(inputs, encoding="utf-8")
    out = tmp_path / "out"

    result = runner.invoke(cli.app, ["demo", "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout and not out.exists()
    assert "inputs.yaml" in result.stderr and "at sign" in result.stderr
    _assert_no_private_text(result, out, ADDRESS)
