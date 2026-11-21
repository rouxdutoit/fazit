# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from html.parser import HTMLParser
from importlib.resources import files
from itertools import combinations, pairwise
from pathlib import Path

import pytest
from typer.testing import CliRunner

from befund import report as report_module
from befund.cli import app
from befund.i18n import load_locale
from befund.report import SECTION_ORDER
from befund.rules import PROFILES

PLANTED_SCAN = Path(__file__).parent / "fixtures" / "planted_scan.json"
RESOURCE_ELEMENTS = {
    "audio",
    "base",
    "embed",
    "form",
    "frame",
    "iframe",
    "img",
    "link",
    "object",
    "script",
    "source",
    "svg",
    "track",
    "video",
}
RESOURCE_ATTRIBUTES = {"action", "background", "formaction", "ping", "poster", "src", "srcset"}
CSS_RESOURCE = re.compile(r"@import\b|\b(?:url|src|image-set)\s*\(", re.IGNORECASE)
SAMPLES = [("town", "en"), ("town", "de"), ("nonprofit", "en"), ("nonprofit", "de")]

runner = CliRunner()


class ReportDocument(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.styles: list[str] = []
        self._in_style = False
        self.feed(html)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        if tag == "style":
            self._in_style = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.styles.append(data)


def _rebuild(scan: Path, out: Path, lang: str, *, profile: str = "opendesk") -> str:
    result = runner.invoke(
        app, ["report", str(scan), "--lang", lang, "--profile", profile, "--out", str(out)]
    )
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file() and path.parent == out
    assert not result.stderr
    return path.read_text(encoding="utf-8")


def _sample_scan(sample: str) -> Path:
    return Path(str(files("befund").joinpath("demo", sample, "scan.json")))


@pytest.mark.parametrize(("sample", "lang"), [*SAMPLES, ("planted", "en")])
@pytest.mark.parametrize("profile", PROFILES)
def test_report_cannot_fetch_resources(
    tmp_path: Path, sample: str, lang: str, profile: str
) -> None:
    scan = PLANTED_SCAN if sample == "planted" else _sample_scan(sample)
    document = ReportDocument(_rebuild(scan, tmp_path, lang, profile=profile))

    policies = []
    for tag, attrs in document.tags:
        assert tag not in RESOURCE_ELEMENTS, tag
        assert not (RESOURCE_ATTRIBUTES & attrs.keys()), attrs
        for name, value in attrs.items():
            if name in {"href", "xlink:href"}:
                assert (value or "").startswith("#"), value
            assert not name.startswith("on"), name
            if name == "style":
                assert not CSS_RESOURCE.search(value or ""), value
        if tag == "meta":
            directive = (attrs.get("http-equiv") or "").strip().lower()
            assert directive != "refresh"
            if directive == "content-security-policy":
                policies.append(attrs.get("content") or "")
    assert len(policies) == 1 and "default-src 'none'" in policies[0]
    assert len(document.styles) == 1 and not CSS_RESOURCE.search(document.styles[0])


def test_demo_writes_exactly_one_html_report(tmp_path: Path) -> None:
    result = runner.invoke(app, ["demo", "--out", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert list(tmp_path.glob("*.html")) == [Path(result.stdout.splitlines()[-1])]


def test_scan_organisation_markup_is_ignored(tmp_path: Path) -> None:
    data = json.loads(PLANTED_SCAN.read_text(encoding="utf-8"))
    data["organisation"]["display_name"] = '<img src="https://example.invalid/organisation">'
    scan = tmp_path / "scan.json"
    scan.write_text(json.dumps(data), encoding="utf-8")

    html = _rebuild(scan, tmp_path / "out", "en")

    assert "example.invalid" not in html
    assert all(tag != "img" for tag, _ in ReportDocument(html).tags)


def test_rendered_text_is_autoescaped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    text = '<img src="https://example.invalid/repository">'
    monkeypatch.setattr(report_module, "REPOSITORY_URL", text)

    html = _rebuild(PLANTED_SCAN, tmp_path, "en")

    assert "&lt;img src=" in html and "example.invalid/repository" in html
    assert all(tag != "img" for tag, _ in ReportDocument(html).tags)


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_report_document_structure(tmp_path: Path, sample: str, lang: str) -> None:
    document = ReportDocument(_rebuild(_sample_scan(sample), tmp_path, lang))

    assert [attrs.get("lang") for tag, attrs in document.tags if tag == "html"] == [lang]
    headings = [int(tag[1]) for tag, _ in document.tags if re.fullmatch(r"h[1-6]", tag)]
    assert headings and headings[0] == 1 and headings.count(1) == 1
    assert all(next_level <= level + 1 for level, next_level in pairwise(headings))
    sections = [attrs["data-section"] for _, attrs in document.tags if "data-section" in attrs]
    assert {"header", "found", "appendix", "footer"} <= set(sections)
    assert sections == [section for section in SECTION_ORDER if section in sections]

    headers = [attrs for tag, attrs in document.tags if tag == "th"]
    scopes = {"col", "colgroup", "row", "rowgroup"}
    assert headers and all(attrs.get("scope") in scopes for attrs in headers)
    cells = [attrs for tag, attrs in document.tags if tag in {"td", "th"}]
    labels = {
        value
        for group in load_locale(lang).values()
        if isinstance(group, dict)
        for value in group.values()
        if isinstance(value, str)
    }
    assert cells and all(attrs.get("data-label") in labels for attrs in cells)


def _luminance(color: str) -> float:
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return sum(
        value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True)
    )


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_report_styles_work_in_light_dark_narrow_and_print(
    tmp_path: Path, sample: str, lang: str
) -> None:
    document = ReportDocument(_rebuild(_sample_scan(sample), tmp_path, lang))
    metas = {
        attrs.get("name"): attrs.get("content") for tag, attrs in document.tags if tag == "meta"
    }
    assert "width=device-width" in (metas.get("viewport") or "")
    assert metas.get("color-scheme") == "light dark"
    (css,) = document.styles
    light = re.search(r":root\s*\{([^}]+)\}", css)
    dark = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]+)\}", css)
    assert light and dark
    for scheme, block in (("light", light[1]), ("dark", dark[1])):
        colors = dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", block))
        for background in ("--bg", "--surface"):
            for foreground in ("--text", "--muted", "--accent"):
                low, high = sorted((_luminance(colors[foreground]), _luminance(colors[background])))
                contrast = (high + 0.05) / (low + 0.05)
                assert contrast >= 4.5, (scheme, foreground, background, contrast)
        assert "--status-unknown" in colors
        status_colors = [
            colors[f"--status-{status}"] for status in ("ready", "needs-work", "blocker")
        ]
        for left, right in combinations(status_colors, 2):
            low, high = sorted((_luminance(left), _luminance(right)))
            assert (high + 0.05) / (low + 0.05) >= 1.5, (scheme, left, right)
    assert re.search(r"@media[^{}]+\(max-width:\s*40rem\)", css)
    assert re.search(r"content:\s*attr\(data-label\)", css)
    assert re.search(r"@page\s*\{\s*margin:", css)
    assert re.search(r"@media\s+print\s*\{", css)
    assert re.search(r"break-inside:\s*avoid", css)
    assert re.search(r"print-color-adjust:\s*exact", css)
