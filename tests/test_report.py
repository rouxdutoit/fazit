# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections import Counter
from dataclasses import replace
from hashlib import sha256
from html import unescape
from itertools import pairwise
from pathlib import Path
from shutil import copytree

import pytest
from helpers import (
    CSS_RESOURCE,
    PLANTED_SCAN,
    RESOURCE_ATTRIBUTES,
    RESOURCE_ELEMENTS,
    ReportDocument,
    assert_readiness_order,
    readiness_row,
    rebuild_report,
    report_section,
    runner,
    sample_inputs_path,
    sample_scan_path,
)
from report_expectations import DISPLAY_ORDER, SECTION_ORDER

from fazit import __version__, catalogue, rules
from fazit import report as report_module
from fazit.cli import app
from fazit.i18n import Formatter, load_locale
from fazit.inputs import load_inputs
from fazit.mappings import PROFILES, load_mapping
from fazit.model import load_scan

# The report embeds its two fonts; nothing else in its CSS may point anywhere.
EMBEDDED_FONT = re.compile(r"url\(data:font/woff2;base64,[A-Za-z0-9+/=]+\)")
SAMPLES = [("town", "en"), ("town", "de"), ("nonprofit", "en"), ("nonprofit", "de")]


def _sample_report(sample: str, out: Path, lang: str, profile: str) -> str:
    return rebuild_report(
        sample_scan_path(sample), out, lang, profile=profile, inputs=sample_inputs_path(sample)
    )


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_readiness_cards_keep_status_order_and_show_the_area_and_action(
    tmp_path: Path, sample: str, lang: str
) -> None:
    html = _sample_report(sample, tmp_path, lang, "opendesk")
    readiness = report_section(html, "readiness")
    entries = catalogue.load_catalogue()
    strings = load_locale(lang)

    assert_readiness_order(readiness, entries.assessed_workload_ids)
    assert 'data-workload="licences"' not in readiness
    assert "readiness-bar" not in html and "data-segment" not in html
    for workload in (entry for entry in entries.workloads if entry.assessed):
        card = readiness_row(readiness, workload.id)
        assert f'class="finding" id="readiness-{workload.id}"' in card
        assert f'aria-labelledby="area-{workload.id}"' in card
        assert f'<h4 class="finding-area" id="area-{workload.id}">' in card
        assert f'data-category="{workload.category}"' in card
        category = strings["category"][workload.category]
        assert f'<span class="finding-category">{category}</span>' in unescape(card)
        status = re.search(r'data-status="([^"]+)"', card)[1]
        label = strings["status"][status]
        assert re.search(rf'<p class="finding-status">.*?</svg> {label}</span>', card, re.S)
        reason = re.search(r'<div class="finding-reason">(.*?)</div>', card, re.S)
        assert reason and re.sub(r"<[^>]+>", "", reason[1]).strip()
        if status != "ready":
            action = re.search(r'<p class="finding-next"><strong>[^<]+</strong>(.*?)</p>', card)
            assert action and action[1].strip()


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_card_disclosures_count_each_observation_once(
    tmp_path: Path, sample: str, lang: str
) -> None:
    html = _sample_report(sample, tmp_path, lang, "opendesk")
    entries = catalogue.load_catalogue()
    readiness = report_section(html, "readiness")
    found = report_section(html, "found")
    assert re.findall(r'data-evidence-workload="([^"]+)"', found) == ["licences"]
    assert load_locale(lang)["found"]["notes"]["directory"] in readiness
    for workload in entries.assessed_workload_ids:
        card = readiness_row(readiness, workload)
        if 'data-status="ready"' in card:
            assert 'class="finding-next"' not in card and 'class="finding-missing"' not in card
        records = re.findall(
            r'<(li|tr) data-(?:evidence|finding)="([^"]+)"[^>]*>(.*?)</\1>', card, re.S
        )
        disclosures = re.findall(r'<details class="workload-evidence"[^>]*>', card)
        if not records:
            assert not disclosures
            continue
        assert disclosures == [
            f'<details class="workload-evidence" data-evidence-workload="{workload}">'
        ]
        detail = card.split(disclosures[0], 1)[1].split("</details>", 1)[0]
        observations = {}
        for _, finding, record in records:
            assert record in detail
            provenances = tuple(re.findall(r'<div data-provenance="([^"]+)"', record))
            assert provenances and observations.setdefault(finding, provenances) == provenances
        counts = Counter(
            provenance for evidence in observations.values() for provenance in evidence
        )
        expected = load_locale(lang)["readiness"]["evidence_summary"].format(
            **{kind: counts[kind] for kind in ("measured", "provided", "unknown")}
        )
        assert re.search(
            rf'<summary id="evidence-{workload}">.*?</svg>{expected}</summary>', detail
        )
        if '<table class="coverage"' in detail and '<ul class="rule-evidence"' in detail:
            assert detail.index('<ul class="rule-evidence"') < detail.index(
                '<table class="coverage"'
            )


@pytest.mark.parametrize("with_inventory", [True, False])
def test_card_disclosure_can_contain_derived_licence_evidence_alone(with_inventory: bool) -> None:
    entries = catalogue.load_catalogue()
    scan = load_scan(sample_scan_path("town"), entries)
    scan = replace(
        scan,
        findings=tuple(finding for finding in scan.findings if finding.workload != "telephony"),
        licences=scan.licences if with_inventory else None,
    )
    card = readiness_row(report_module.render_report(scan, lang="en"), "telephony")
    assert ('data-evidence-workload="telephony"' in card) is with_inventory
    assert ('data-evidence="telephony.licence_add_on_assigned"' in card) is with_inventory
    assert '<table class="coverage"' not in card


def test_card_disclosure_counts_two_disagreeing_observations_with_the_same_provenance() -> None:
    entries = catalogue.load_catalogue()
    scan = load_scan(sample_scan_path("town"), entries)
    finding = scan.finding("small_apps.in_use")
    assert finding is not None
    supplied = replace(
        finding, value=True, provenance="provided", source="interview", missing_reason=None
    )
    scan = replace(
        scan,
        findings=tuple(supplied if item.id == supplied.id else item for item in scan.findings),
        licences=None,
    )
    inputs = load_inputs(sample_inputs_path("town"), entries)
    card = readiness_row(report_module.render_report(scan, lang="en", inputs=inputs), "small_apps")
    assert "Evidence · 0 measured, 2 provided, 0 unknown" in card
    assert card.count('class="evidence-meta"><span class="prov">Provided</span>') == 4


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
@pytest.mark.parametrize("profile", PROFILES)
def test_card_target_lines_keep_needed_gaps_and_mapping_details(
    tmp_path: Path, sample: str, lang: str, profile: str
) -> None:
    html = _sample_report(sample, tmp_path, lang, profile)
    entries = catalogue.load_catalogue()
    mapping = load_mapping(profile, entries)
    formatter = Formatter(lang)
    strings = formatter.strings
    gaps = set(re.findall(r'<li data-gap="([^"]+)" data-need="yes"', html))

    for workload in entries.assessed_workload_ids:
        card = readiness_row(html, workload)
        target = re.search(r'<p class="finding-target">(.*?)</p>', card, re.S)
        assert target and re.findall(r'href="([^"]+)"', target[1]) == ["#moves-title"]
        functions = [item for item in mapping.functions if item.workload == workload]
        needed = [item for item in functions if item.function in gaps]
        expected = (needed + [item for item in functions if item not in needed])[:2]
        shown = re.findall(r'<span data-target-function="([^"]+)">(.*?)</span>', target[1], re.S)
        assert {item.function for item in needed} <= {function for function, _ in shown}
        assert [function for function, _ in shown] == [item.function for item in expected]
        for (_, text), item in zip(shown, expected, strict=True):
            assert item.replacement[lang] in unescape(text)
            assert strings["mapping_coverage"][item.coverage] in unescape(text)
            date_text = (
                formatter.date(item.checked_on.isoformat())
                if item.checked_on
                else strings["moves"]["no_project_check"]
            )
            assert date_text in text


def test_needed_teams_chat_history_comes_first_on_the_card(tmp_path: Path) -> None:
    inputs = tmp_path / "inputs.yaml"
    original = sample_inputs_path("town").read_text(encoding="utf-8")
    inputs.write_text(
        original.replace(
            "teams.chat_history_must_be_kept: false", "teams.chat_history_must_be_kept: true"
        ),
        encoding="utf-8",
    )
    html = rebuild_report(sample_scan_path("town"), tmp_path / "out", "en", inputs=inputs)
    card = readiness_row(html, "teams")
    assert re.findall(r'data-target-function="([^"]+)"', card) == ["teams_chat_history", "chat"]


def _screen_media_spans(css: str) -> list[range]:
    spans = []
    for media in re.finditer(r"@media\s+screen\b[^{}]*\{", css):
        depth = 1
        for brace in re.finditer(r"[{}]", css[media.end() :]):
            depth += 1 if brace[0] == "{" else -1
            if depth == 0:
                spans.append(range(media.end(), media.end() + brace.start()))
                break
        assert depth == 0
    return spans


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_readiness_filters_use_the_card_counts_and_catalogue(
    tmp_path: Path, sample: str, lang: str
) -> None:
    html = _sample_report(sample, tmp_path, lang, "opendesk")
    readiness = report_section(html, "readiness")
    entries = catalogue.load_catalogue()
    formatter = Formatter(lang)
    strings = formatter.strings
    groups = re.findall(
        r'<fieldset class="segmented" data-filter="([^"]+)">(.*?)</fieldset>', readiness, re.S
    )
    assert [group for group, _ in groups] == ["status", "category"]
    cards = [attrs for tag, attrs in ReportDocument(readiness).tags if tag == "article"]
    counts = Counter(card["data-status"] for card in cards)
    category_ids = [category.id for category in entries.categories]
    assert {card["data-category"] for card in cards} == set(category_ids)

    for kind, group in groups:
        ids = DISPLAY_ORDER if kind == "status" else category_ids
        assert f'<legend class="sr-only">{strings["filter"][f"{kind}_legend"]}</legend>' in group
        labels = re.findall(r"<label>(.*?)</label>", group, re.S)
        radios = [attrs for tag, attrs in ReportDocument(group).tags if tag == "input"]
        assert len(labels) == len(radios) == len(ids) + 1
        for option, label, radio in zip(("all", *ids), labels, radios, strict=True):
            assert radio["type"] == "radio" and radio["name"] == f"f-{kind}"
            assert radio["id"] == f"f-{kind}-{option}"
            assert "<input " in label
            assert ("checked" in radio) is (option == "all")
            assert ("disabled" in radio) is (
                kind == "status" and option != "all" and not counts[option]
            )
            text = unescape(" ".join(re.sub(r"<[^>]*>", "", label).split()))
            if kind == "status":
                count = len(entries.assessed_workload_ids) if option == "all" else counts[option]
                name = strings["filter"]["all"] if option == "all" else strings["status"][option]
                assert text == f"{name} · {formatter.integer(count)}"
                assert ("<svg" in label) is (option != "all")
            else:
                name = (
                    strings["filter"]["all_categories"]
                    if option == "all"
                    else strings["category"][option]
                )
                assert text == name and "<svg" not in label

    assert strings["filter"]["search_hint"] in unescape(readiness)
    assert f'<p class="areas-empty note">{strings["filter"]["empty"]}</p>' in unescape(readiness)
    document = ReportDocument(html)
    assert not any(tag == "form" for tag, _ in document.tags)
    (css,) = document.styles
    screen_spans = _screen_media_spans(css)
    checked = [match.start() for match in re.finditer(r":checked\b", css)]
    assert checked and all(any(position in span for span in screen_spans) for position in checked)
    assert re.search(
        r"@supports not selector\(:has\(\*\)\)\s*\{\s*\.filters\s*\{\s*display:\s*none", css
    )


@pytest.mark.parametrize(("sample", "lang"), [*SAMPLES, ("planted", "en")])
@pytest.mark.parametrize("profile", PROFILES)
def test_report_cannot_fetch_resources(
    tmp_path: Path, sample: str, lang: str, profile: str
) -> None:
    html = (
        rebuild_report(PLANTED_SCAN, tmp_path, lang, profile=profile)
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
    assert len(document.styles) == 1
    assert len(EMBEDDED_FONT.findall(document.styles[0])) == 2
    assert not CSS_RESOURCE.search(EMBEDDED_FONT.sub("", document.styles[0]))
    assert "font-src data:;" in policies[0] and "img-src" not in policies[0]


def test_demo_writes_exactly_one_html_report(tmp_path: Path) -> None:
    result = runner.invoke(app, ["demo", "--out", str(tmp_path)])

    assert result.exit_code == 0, result.output
    report = Path(result.stdout.splitlines()[-1])
    assert list(tmp_path.glob("*.html")) == [report]
    footer = report.read_text(encoding="utf-8").split('<footer data-section="footer">')[1]
    assert "<p>fazit · https://github.com/rouxdutoit/fazit</p>" in footer
    assert "href=" not in footer


def test_scan_organisation_markup_is_ignored(tmp_path: Path) -> None:
    data = json.loads(PLANTED_SCAN.read_text(encoding="utf-8"))
    data["organisation"]["display_name"] = '<img src="https://example.invalid/organisation">'
    scan = tmp_path / "scan.json"
    scan.write_text(json.dumps(data), encoding="utf-8")

    html = rebuild_report(scan, tmp_path / "out", "en")

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
    original = sample_inputs_path(sample).read_text(encoding="utf-8")
    inputs = tmp_path / "inputs.yaml"
    edited = re.sub(
        r"^organisation_name:.*$", f"organisation_name: '{markup}'", original, flags=re.M
    )
    inputs.write_text(edited, encoding="utf-8")
    html = rebuild_report(
        sample_scan_path(sample), tmp_path / "out", lang, profile=profile, inputs=inputs
    )

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
    html = _sample_report(sample, tmp_path, lang, profile)
    document = ReportDocument(html)
    metas = {
        attrs.get("name"): attrs.get("content") for tag, attrs in document.tags if tag == "meta"
    }
    assert "width=device-width" in (metas.get("viewport") or "")
    assert metas.get("color-scheme") == "light dark"
    (css,) = document.styles
    assert "apple.com" not in css and "iOS system colours" not in css
    assert re.search(r"a:hover\s*\{\s*color:\s*var\(--accent-hover\);\s*\}", css)
    light = re.search(r":root\s*\{([^}]+)\}", css)
    dark = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]+)\}", css)
    assert light and dark
    for scheme, block in (("light", light[1]), ("dark", dark[1])):
        colors = dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", block))
        for background in ("--bg", "--surface"):
            for foreground in ("--text", "--muted", "--accent", "--accent-hover"):
                low, high = sorted((_luminance(colors[foreground]), _luminance(colors[background])))
                contrast = (high + 0.05) / (low + 0.05)
                assert contrast >= 4.5, (scheme, foreground, background, contrast)
        assert _luminance(colors["--accent-hover"]) > _luminance(colors["--accent"])
        status_colors = [
            colors[f"--status-{status}"] for status in ("ready", "needs-work", "blocker", "unknown")
        ]
        assert len(set(status_colors)) == 4, (scheme, status_colors)
    assert re.search(r"@media[^{}]+\(max-width:\s*40rem\)", css)
    assert re.search(r"content:\s*attr\(data-label\)", css)
    assert re.search(r"@page\s*\{\s*margin:", css)
    assert re.search(r"@media\s+print\s*\{", css)
    assert re.search(r"break-inside:\s*avoid", css)
    assert re.search(r"print-color-adjust:\s*exact", css)
    print_css = css.split("@media print", 1)[1]
    assert re.search(r"::details-content\s*\{[^}]*content-visibility:\s*visible", print_css)
    # Colour is never the only cue: every status label carries its own symbol and its text.
    icons = {
        status: re.findall(rf'<span class="status {status}"><svg[^>]*><path d="([^"]+)"', html)
        for status in ("ready", "needs_work", "blocker", "unknown")
    }
    paths = {next(iter(set(found))) for found in icons.values() if found}
    assert len(paths) == sum(1 for found in icons.values() if found)


def test_report_and_website_share_colour_tokens(tmp_path: Path) -> None:
    css = ReportDocument(_sample_report("town", tmp_path, "en", "opendesk")).styles[0]
    site = (Path(__file__).resolve().parents[1] / "site" / "style.css").read_text("utf-8")
    pairs = {
        "--bg": "--bg",
        "--surface": "--fill",
        "--fill-2": "--fill-2",
        "--text": "--fg",
        "--muted": "--fg-2",
        "--line": "--rule",
        "--accent": "--link",
        "--accent-hover": "--link-hover",
    }
    light = dict(
        re.findall(r"(--[\w-]+):\s*(#[0-9a-f]{6});", re.search(r":root\s*\{([^}]+)\}", css)[1])
    )
    dark_block = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]+)\}", css)[1]
    dark = dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-f]{6});", dark_block))
    tokens = {
        name: (light_value, dark_value)
        for name, light_value, dark_value in re.findall(
            r"(--[\w-]+):\s*light-dark\((#[0-9a-f]{6}),\s*(#[0-9a-f]{6})\);", site
        )
    }
    for report_name, site_name in pairs.items():
        assert tokens[site_name] == (light[report_name], dark[report_name]), report_name
    assert re.search(r"a:hover\s*\{\s*color:\s*var\(--link-hover\);", site)
    for hover, text in zip(tokens["--solid-hover"], tokens["--solid-fg"], strict=True):
        low, high = sorted((_luminance(hover), _luminance(text)))
        assert (high + 0.05) / (low + 0.05) >= 4.5
    for status in ("ready", "needs-work", "blocker"):
        assert tokens[f"--status-{status}"] == (
            light[f"--status-{status}"],
            dark[f"--status-{status}"],
        )


def _checksums(html: str) -> dict[str, str]:
    details = html.split('data-subsection="run-details"', 1)[1]
    pairs = re.findall(r'<code data-checksum="([^"]+)">([a-f0-9]{64})</code>', details)
    assert len(pairs) == 5
    return dict(pairs)


@pytest.mark.parametrize("lang", ["en", "de"])
def test_report_records_scan_origin_and_versions(tmp_path: Path, lang: str) -> None:
    data = json.loads(sample_scan_path("town").read_bytes())
    data["findings"] = [row for row in data["findings"] if row["source"] is None]
    data["licences"] = None
    scan = tmp_path / "PrivateScanMarker.json"
    run_details = []
    for index, (source, version) in enumerate(
        [("import", "0.0.9"), ("live", "0.0.9"), ("live", "0.1.1")]
    ):
        data["source_kind"] = source
        data["tool"]["version"] = version
        scan.write_text(json.dumps(data), encoding="utf-8")
        html = rebuild_report(scan, tmp_path / f"out-{index}", lang)
        assert "PrivateScanMarker" not in html
        assert "scan.json" in html.split("</header>", 1)[0]
        assert "data-sample" not in html
        run_details.append(html.split('data-subsection="run-details"', 1)[1])

    assert len(set(run_details)) == 3
    for details, origin in zip(run_details, ("import", "live", "live"), strict=True):
        assert f'data-source-kind="{origin}"' in details
        assert "<dd data-scan-producer>fazit</dd>" in details
        assert f"<dd data-renderer-version>{__version__}</dd>" in details
    assert "<dd data-producer-version>0.0.9</dd>" in run_details[0]
    assert "<dd data-producer-version>0.1.1</dd>" in run_details[-1]


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
    assert rendered == expected


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
    scan.write_bytes(sample_scan_path("town").read_bytes())
    inputs = tmp_path / "private-inputs-name.yaml"
    text = sample_inputs_path("town").read_text(encoding="utf-8")
    inputs.write_text(
        text if with_date else text.replace('as_of: "2026-11-10"', "as_of: null"), encoding="utf-8"
    )

    html = rebuild_report(scan, tmp_path / "out", "en", inputs=inputs)

    header = html.split("</header>", 1)[0]
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
        assert '<time datetime="2026-11-10">10 November 2026</time>' in header
    else:
        assert strings["common"]["date_not_supplied"] in details
        assert strings["common"]["date_not_supplied"] in header
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
    data = json.loads(sample_scan_path("town").read_text(encoding="utf-8"))
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
