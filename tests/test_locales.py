# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from importlib.resources import files
from string import Formatter as FormatParser

import pytest

from befund.catalogue import load_catalogue
from befund.i18n import SUPPORTED_LANGUAGES, Formatter, code_label, load_locale, reason_text
from befund.parsing import read_text


def flatten_keys(
    tree: dict, parent: tuple[str, ...] = ()
) -> dict[tuple[str, ...], str | list[str]]:
    leaves = {}
    for key, value in tree.items():
        path = (*parent, key)
        if isinstance(value, dict):
            leaves.update(flatten_keys(value, path))
        elif isinstance(value, list):
            assert value and all(isinstance(text, str) and text.strip() for text in value), path
            leaves[path] = value
        else:
            assert isinstance(value, str) and value.strip(), path
            leaves[path] = value
    return leaves


def _fields(text: str) -> set[str]:
    return {name for _, name, _, _ in FormatParser().parse(text) if name is not None}


def test_locale_key_parity() -> None:
    english = flatten_keys(load_locale("en"))
    german = flatten_keys(load_locale("de"))

    difference = sorted(".".join(path) for path in english.keys() ^ german.keys())
    assert not difference, f"Different locale keys: {', '.join(difference)}"
    for path, value in english.items():
        translation = german[path]
        assert type(translation) is type(value), path
        if isinstance(value, str):
            assert _fields(value) == _fields(translation), path
        else:
            assert len(value) == len(translation), path
            for left, right in zip(value, translation, strict=True):
                assert _fields(left) == _fields(right), path


@pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
def test_catalogue_labels_and_reason_codes_have_translations(lang: str) -> None:
    catalogue = load_catalogue()
    strings = load_locale(lang)
    leaves = flatten_keys(strings)
    for entry in (*catalogue.workloads, *catalogue.findings):
        assert tuple(entry.label.split(".", 1)) in leaves, entry.label
    for entry in catalogue.findings:
        if entry.unit is not None:
            assert ("units", entry.unit) in leaves, entry.unit
    assert catalogue.collector_ids <= strings["collector"].keys()
    assert catalogue.source_codes <= strings["source"].keys()
    assert {
        "not_in_export",
        "permission_denied",
        "not_licensed",
        "not_collected_in_this_version",
        "answer_not_provided",
        "source_not_supplied",
        "needs_recipient_export",
        "collector_skipped",
        "not_in_scan",
        "licensed_use_not_measured",
        "coverage_partial",
        "not_established",
        "not_recognised",
    } <= catalogue.reason_codes
    assert all(
        {"label", "fix"} == strings["reason"][code].keys() for code in catalogue.reason_codes
    )
    assert reason_text(strings, "unrecognised") == reason_text(strings, "not_recognised")
    assert code_label(strings, "collector", "unrecognised") == "unrecognised"


def test_template_uses_locale_for_visible_text() -> None:
    source = files("befund").joinpath("templates", "report.html.j2")
    template = read_text(source)
    for attribute in re.findall(r'\s(?:aria-label|title|alt)="([^"]*)"', template):
        assert re.fullmatch(r"\s*{{[^{}]+}}\s*", attribute), attribute

    content = re.sub(r"{{.*?}}|{%.*?%}|{#.*?#}|<style\b.*?</style>", "", template, flags=re.S)
    visible = re.sub(r"<[^>]*>", "", content)
    assert not re.search(r"[^\W\d_]{2,}", visible), visible


@pytest.mark.parametrize(
    ("lang", "integer", "storage", "date", "period"),
    [
        ("en", "1,234,567", "312.4 GB", "2 November 2026", "6 May 2026 to 1 November 2026"),
        ("de", "1.234.567", "312,4 GB", "2. November 2026", "6. Mai 2026 bis 1. November 2026"),
    ],
)
def test_formatter(lang: str, integer: str, storage: str, date: str, period: str) -> None:
    formatter = Formatter(lang)
    assert formatter.integer(1234567) == integer
    assert formatter.storage(312400000000) == storage
    assert formatter.date("2026-11-02") == date
    assert formatter.period("2026-05-06/2026-11-01") == period


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0.0 B"),
        (750, "750.0 B"),
        (1250, "1.3 kB"),
        (1000000, "1.0 MB"),
        (1500000000000, "1.5 TB"),
    ],
)
def test_storage_units(value: int, expected: str) -> None:
    assert Formatter("en").storage(value) == expected
