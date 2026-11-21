# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections import Counter
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
from importlib.resources import files
from itertools import combinations, pairwise
from pathlib import Path
from shutil import copytree

import pytest
from typer.testing import CliRunner

from befund import __version__, catalogue, rules
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


def _rebuild(
    scan: Path, out: Path, lang: str, *, profile: str = "opendesk", inputs: Path | None = None
) -> str:
    command = ["report", str(scan), "--lang", lang, "--profile", profile, "--out", str(out)]
    if inputs is not None:
        command.extend(["--inputs", str(inputs)])
    result = runner.invoke(app, command)
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file() and path.parent == out
    assert not result.stderr
    return path.read_text(encoding="utf-8")


def _sample_scan(sample: str) -> Path:
    return Path(str(files("befund").joinpath("demo", sample, "scan.json")))


def _sample_inputs(sample: str) -> Path:
    return _sample_scan(sample).with_name("inputs.yaml")


def _sample_report(sample: str, out: Path, lang: str, profile: str) -> str:
    return _rebuild(_sample_scan(sample), out, lang, profile=profile, inputs=_sample_inputs(sample))


@pytest.mark.parametrize(("sample", "lang"), [*SAMPLES, ("planted", "en")])
@pytest.mark.parametrize("profile", PROFILES)
def test_report_cannot_fetch_resources(
    tmp_path: Path, sample: str, lang: str, profile: str
) -> None:
    html = (
        _rebuild(PLANTED_SCAN, tmp_path, lang, profile=profile)
        if sample == "planted"
        else _sample_report(sample, tmp_path, lang, profile)
    )
    document = ReportDocument(html)

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


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
@pytest.mark.parametrize("profile", PROFILES)
def test_rendered_text_is_autoescaped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, sample: str, lang: str, profile: str
) -> None:
    text = '<img src="https://example.invalid/repository">'
    monkeypatch.setattr(report_module, "REPOSITORY_URL", text)
    markup = '<img src="https://example.invalid/organisation">'
    original = _sample_inputs(sample).read_text(encoding="utf-8")
    inputs = tmp_path / "inputs.yaml"
    edited = re.sub(
        r"^organisation_name:.*$", f"organisation_name: '{markup}'", original, flags=re.M
    )
    inputs.write_text(edited, encoding="utf-8")
    html = _rebuild(_sample_scan(sample), tmp_path / "out", lang, profile=profile, inputs=inputs)

    assert "&lt;img src=" in html and "example.invalid/repository" in html
    header = html.split("</header>", 1)[0]
    assert "&lt;img src=" in header and markup in unescape(header)
    assert all(tag != "img" for tag, _ in ReportDocument(html).tags)


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
@pytest.mark.parametrize("profile", PROFILES)
def test_report_document_structure(tmp_path: Path, sample: str, lang: str, profile: str) -> None:
    document = ReportDocument(_sample_report(sample, tmp_path, lang, profile))

    assert [attrs.get("lang") for tag, attrs in document.tags if tag == "html"] == [lang]
    headings = [int(tag[1]) for tag, _ in document.tags if re.fullmatch(r"h[1-6]", tag)]
    assert headings and headings[0] == 1 and headings.count(1) == 1
    assert all(next_level <= level + 1 for level, next_level in pairwise(headings))
    sections = [attrs["data-section"] for _, attrs in document.tags if "data-section" in attrs]
    assert tuple(sections) == SECTION_ORDER
    assert [
        attrs["data-subsection"] for _, attrs in document.tags if "data-subsection" in attrs
    ] == ["not-examined", "cannot-be-moved", "run-details"]

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
@pytest.mark.parametrize("profile", PROFILES)
def test_report_styles_work_in_light_dark_narrow_and_print(
    tmp_path: Path, sample: str, lang: str, profile: str
) -> None:
    document = ReportDocument(_sample_report(sample, tmp_path, lang, profile))
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
    print_css = css.split("@media print", 1)[1]
    assert re.search(r"::details-content\s*\{[^}]*content-visibility:\s*visible", print_css)


def _checksums(html: str) -> dict[str, str]:
    details = html.split('data-subsection="run-details"', 1)[1]
    pairs = re.findall(r'<code data-checksum="([^"]+)">([a-f0-9]{64})</code>', details)
    assert len(pairs) == 5
    return dict(pairs)


@pytest.mark.parametrize("profile", PROFILES)
def test_run_details_checksums_match_packaged_files(tmp_path: Path, profile: str) -> None:
    rendered = _checksums(_sample_report("town", tmp_path, "en", profile))
    directory = rules.rules_dir()
    rule_paths = (
        "findings.yaml",
        "status.yaml",
        "service_plans.yaml",
        "risky_file_types.yaml",
        f"mappings/{profile}.yaml",
    )
    expected = {
        Path(path).name: sha256(directory.joinpath(path).read_bytes()).hexdigest()
        for path in rule_paths
    }
    assert rendered == dict(rules.rule_file_checksums(profile)) == expected


def test_checksums_use_the_five_rule_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = _checksums(_sample_report("town", tmp_path / "original", "en", "opendesk"))
    copied = tmp_path / "rules"
    copytree(Path(str(rules.rules_dir())), copied)
    path = copied / "status.yaml"
    raw = path.read_bytes().replace(b"\n", b"\r\n") + b"\r\n# Edited for this test.\r\n"
    path.write_bytes(raw)
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)
    real_read = rules.read_text
    reads: Counter[str] = Counter()

    def record_read(path: Path) -> str:
        reads[path.name] += 1
        return real_read(path)

    monkeypatch.setattr(rules, "read_text", record_read)
    monkeypatch.setattr(catalogue, "read_text", record_read)

    after = _checksums(_sample_report("town", tmp_path / "edited", "en", "opendesk"))

    assert after == (original | {"status.yaml": sha256(raw).hexdigest()})
    assert after["status.yaml"] != original["status.yaml"]
    assert reads == Counter(dict.fromkeys(original, 1))


@pytest.mark.parametrize("with_date", [True, False])
def test_run_details_use_dates_and_roles_without_filenames(tmp_path: Path, with_date: bool) -> None:
    scan = tmp_path / "private-scan-name.json"
    scan.write_bytes(_sample_scan("town").read_bytes())
    inputs = tmp_path / "private-inputs-name.yaml"
    text = _sample_inputs("town").read_text(encoding="utf-8")
    inputs.write_text(
        text if with_date else text.replace('as_of: "2026-11-10"', "as_of: null"), encoding="utf-8"
    )

    html = _rebuild(scan, tmp_path / "out", "en", inputs=inputs)

    details = html.split('data-subsection="run-details"', 1)[1]
    strings = load_locale("en")
    assert scan.name not in html and inputs.name not in html
    assert __version__ in details
    assert strings["appendix"]["scan_role"] in details
    assert strings["appendix"]["inputs_role"] in details
    data = json.loads(scan.read_text(encoding="utf-8"))
    assert f'<time datetime="{data["generated_at"]}">' in details
    periods = sorted({row["period"] for row in data["findings"] if row["period"]})
    assert re.findall(r'data-reporting-period="([^"]+)"', details) == periods
    if with_date:
        assert '<time datetime="2026-11-10">10 November 2026</time>' in details
    else:
        assert strings["common"]["date_not_supplied"] in details
    appendix = html.split('data-section="appendix"', 1)[1]
    for formula in strings["costs"]["formulas"]:
        assert formula in unescape(appendix)


def test_workload_evidence_stays_in_the_document_with_localised_reasons(tmp_path: Path) -> None:
    html = _sample_report("town", tmp_path, "en", "opendesk")
    document = ReportDocument(html)
    details = [
        attrs
        for tag, attrs in document.tags
        if tag == "details" and "data-evidence-workload" in attrs
    ]
    assert details and all("open" not in attrs for attrs in details)
    data = json.loads(_sample_scan("town").read_text(encoding="utf-8"))
    assert {row["workload"] for row in data["findings"]} == {
        attrs["data-evidence-workload"] for attrs in details
    }
    assert {row["id"] for row in data["findings"]} <= {
        attrs.get("data-finding") for tag, attrs in document.tags if tag == "tr"
    }
    readiness = html.split('data-section="readiness"', 1)[1].split('data-section="moves"', 1)[0]
    visible = unescape(re.sub(r"<[^>]*>", "", readiness))
    reason_codes = set(re.findall(r'data-reason="([^"]+)"', readiness))
    assert "needs_recipient_export" in reason_codes
    assert all(code not in visible for code in reason_codes)
    assert "Source · —" not in visible
