# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections import Counter
from dataclasses import replace
from datetime import date
from hashlib import sha256
from html import unescape
from importlib.resources import files
from itertools import pairwise
from pathlib import Path
from shutil import copytree

import pytest
from helpers import (
    ALL_UNKNOWN_SCAN,
    CSS_RESOURCE,
    PLANTED_SCAN,
    ROOT,
    ReportDocument,
    assert_readiness_order,
    offline_policies,
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
from fazit.fonts.css import CSS_DECLARATION, check_font_families
from fazit.i18n import Formatter, load_locale
from fazit.inputs import load_inputs
from fazit.licences import licence_findings
from fazit.mappings import PROFILES, load_mapping
from fazit.model import load_scan
from fazit.parsing import read_text

# The report embeds its two fonts; nothing else in its CSS may point anywhere.
EMBEDDED_FONT = re.compile(r"url\(data:font/woff2;base64,[A-Za-z0-9+/=]+\)")
SAMPLES = [("town", "en"), ("town", "de"), ("nonprofit", "en"), ("nonprofit", "de")]
CSS_ROOT = re.compile(r"(?:^|(?<=[{}]))\s*:root\s*\{[^{}]*\}")
CSS_COLOUR = re.compile(r"#[0-9a-f]{3,8}\b|\b(?:rgba?|hsla?)\([^)]*\)", re.I)
STATUS_PATHS = re.compile(r'<(?:span|dt) class="status ([a-z_]+)[^"]*"><svg[^>]*><path d="([^"]+)"')
REPORT_ICONS = files("fazit").joinpath("icons")


def _sample_report(sample: str, out: Path, lang: str, profile: str) -> str:
    return rebuild_report(
        sample_scan_path(sample), out, lang, profile=profile, inputs=sample_inputs_path(sample)
    )


@pytest.fixture(scope="session")
def style_references(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    return {
        lang: _sample_report(
            "town", tmp_path_factory.mktemp(f"report-style-{lang}"), lang, "opendesk"
        )
        for lang in ("en", "de")
    }


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_report_navigation_resolves_and_appendix_explains_scope(
    tmp_path: Path, sample: str, lang: str
) -> None:
    html = _sample_report(sample, tmp_path, lang, "opendesk")
    tags = ReportDocument(html).tags
    strings = load_locale(lang)
    ids = Counter(attrs["id"] for _, attrs in tags if "id" in attrs)
    for _, attrs in tags:
        if "href" in attrs:
            href = attrs["href"]
            assert href.startswith("#") and ids[href[1:]] == 1

    assert tags[tags.index(("body", {})) + 1] == ("a", {"class": "skip", "href": "#main"})
    assert [attrs["id"] for tag, attrs in tags if tag == "main"] == ["main"]
    assert [attrs["aria-label"] for tag, attrs in tags if tag == "nav"] == [
        strings["nav"]["label"],
        strings["nav"]["label"],
    ]
    menu = re.search(r'<details class="bar-menu">\s*<summary[^>]*>(.*?)</summary>', html)
    assert menu and f'<span class="sr-only">{strings["nav"]["on_this_page"]}</span>' in menu[1]
    indexes = re.findall(r'<div class="bar-links-in">(.*?)</div>', html, re.S)
    expected_links = [
        (f"{section}-title", strings["nav"][key])
        for section, key in (
            ("summary", "summary"),
            ("path", "next_steps"),
            ("readiness", "areas"),
            ("costs", "costs"),
            ("moves", "replacements"),
            ("attention", "closer_look"),
            ("appendix", "appendix"),
        )
    ]
    assert len(indexes) == 2
    for index in indexes:
        assert (
            re.findall(
                r'<a href="#([^"]+)"[^>]*><span class="symbol-text">([^<]+)</span></a>', index
            )
            == expected_links
        )
    appendix = unescape(report_section(html, "appendix"))
    for key in ("not_looked", "not_looked_text"):
        assert strings["appendix"][key] in appendix
    before, run_details = unescape(html).split('data-subsection="run-details"', 1)
    for key in ("local", "offline"):
        assert strings["header"][key] in run_details and strings["header"][key] not in before


def test_coverage_symbols_match_the_site() -> None:
    icons = sorted((ROOT / "src" / "fazit" / "icons").glob("*.svg"))
    assert {"circle", "contrast", "code", "cancel"} <= {icon.stem for icon in icons}
    for icon in icons:
        shared = ROOT / "site" / "icons" / icon.name
        assert shared.is_file() and shared.read_bytes() == icon.read_bytes(), icon.name


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
@pytest.mark.parametrize("profile", PROFILES)
def test_replacements_use_coverage_symbols_distinct_from_status(
    tmp_path: Path, sample: str, lang: str, profile: str
) -> None:
    html = _sample_report(sample, tmp_path, lang, profile)
    strings = load_locale(lang)
    mapping = load_mapping(profile, catalogue.load_catalogue())
    moves = report_section(html, "moves")
    shared = {item.checked_on for item in mapping.functions}
    shared_check = len(shared) == 1 and None not in shared
    date_label = strings["appendix"]["mapping_date"]
    if shared_check:
        day = next(iter(shared))
        assert day is not None
        assert (
            re.search(r"<caption[^>]*>.*?</caption>", moves, re.S)[0].count(
                f'<time datetime="{day.isoformat()}">'
            )
            == 1
        )
        assert f'data-label="{date_label}"' not in moves
    rows = dict(re.findall(r'<tr data-function="([^"]+)"(.*?)</tr>', moves, re.S))
    assert list(rows) == [item.function for item in mapping.functions]
    needs = dict(re.findall(r'<li data-gap="([^"]+)" data-need="([^"]+)"', html))
    symbols = {
        coverage: icon
        for icon, codes in (
            ("circle", ("in_suite",)),
            ("contrast", ("in_suite_with_limits",)),
            ("code", ("open_source_community", "open_source_third_party")),
            (
                "cancel",
                (
                    "announced",
                    "component_vendor_solution",
                    "proprietary_third_party",
                    "not_available",
                    "transfer_undocumented",
                ),
            ),
        )
        for coverage in codes
    }
    status_paths = dict(STATUS_PATHS.findall(html))
    chevron_icon = REPORT_ICONS.joinpath("chevron-right.svg")
    chevron = re.search(r'<path d="([^"]+)"', chevron_icon.read_text(encoding="utf-8"))[1]
    for item in mapping.functions:
        row = rows[item.function]
        status = re.search(r'data-status="([^"]+)"', row)[1]
        assert row.count("<td ") == (3 if shared_check else 4)
        if not shared_check:
            assert f'data-label="{date_label}"' in row
        need = re.search(
            rf'<td role="cell" data-label="{strings["moves"]["need"]}">\s*([^<]+)',
            row,
        )
        assert need
        expected_need = needs.get(item.function)
        assert need[1].strip() == (
            strings["status"]["unknown"]
            if expected_need == "unknown"
            else strings["common"][expected_need]
            if expected_need
            else strings["moves"]["need_not_assessed"]
        )
        coverage = re.search(r'<span class="cov-cell\b[^"]*">.*?</td>', row, re.S)
        assert coverage is not None
        source = REPORT_ICONS.joinpath(f"{symbols[item.coverage]}.svg")
        path = re.search(r'<path d="([^"]+)"', source.read_text(encoding="utf-8"))[1]
        assert re.findall(r'<path d="([^"]+)"', coverage[0]) == [path]
        assert path not in status_paths.values()
        assert strings["mapping_coverage"][item.coverage] in unescape(coverage[0])
        link = re.search(
            r'<a href="#readiness-([^"]+)" aria-label="([^"]+)" '
            r'class="[^"]*\breplacement-status\b[^"]*">(.*?)</a>',
            row,
            re.S,
        )
        assert link and link[1] == item.workload
        assert unescape(link[2]) == strings["moves"]["status_link"].format(
            area=strings["workload"][item.workload], status=strings["status"][status]
        )
        assert f"status {status} badge" in link[0]
        label = re.search(
            r'<span class="symbol-text"><span class="link-text">([^<]+)</span>'
            r'<span class="chevron-tail[^"]*" aria-hidden="true"><svg class="chevron"',
            link[3],
        )
        assert label and unescape(label[1]) == strings["status"][status]
        assert re.findall(r'<path d="([^"]+)"', link[3]) == [status_paths[status], chevron]
        for _, attrs in ReportDocument(row.replace(link[0], "")).tags:
            assert not ({"status", *DISPLAY_ORDER} & set(attrs.get("class", "").split()))


@pytest.mark.parametrize("lang", ["en", "de"])
def test_replacements_keep_per_row_dates_when_checks_differ(lang: str) -> None:
    entries = catalogue.load_catalogue()
    scan = load_scan(sample_scan_path("town"), entries)
    context, _ = report_module._prepare_report(scan, lang, "opendesk", entries, None)
    mapping = context["mapping"]
    first, *rest = mapping.functions
    first = replace(first, checked_on=date(2026, 11, 20))
    context["mapping"] = replace(mapping, functions=(first, *rest))

    moves = report_section(report_module._render_html(context), "moves")
    assert 'class="checked-on"' not in moves
    formatter = Formatter(lang)
    date_label = formatter.strings["appendix"]["mapping_date"]
    cells = re.findall(rf'data-label="{date_label}">\s*(<time [^<]+</time>)', moves)
    assert cells == [
        f'<time datetime="{item.checked_on.isoformat()}">'
        f"{formatter.date(item.checked_on.isoformat())}</time>"
        for item in context["mapping"].functions
    ]


def _assert_status_summary(summary: str, counts: Counter[str], formatter: Formatter) -> None:
    strings = formatter.strings
    status_list = re.search(r'<dl class="status-summary">(.*?)</dl>', summary, re.S)
    assert status_list is not None
    rows = re.findall(
        r'<dt class="status ([a-z_]+)[^"]*"><svg[^>]*>.*?</svg>'
        r'<span class="symbol-text">([^<]+)</span>'
        r' <span class="row-count[^"]*">([^<]+)</span></dt>'
        r"\s*<dd>([^<]+)</dd>",
        unescape(status_list[1]),
    )
    assert rows == [
        (
            status,
            strings["status"][status],
            formatter.integer(counts[status]),
            strings["summary"]["define"][status],
        )
        for status in DISPLAY_ORDER
    ]
    total = len(catalogue.load_catalogue().assessed_workload_ids)
    assert sum(counts.values()) == total
    assert strings["summary"]["of_areas"].format(n=formatter.integer(total)) in summary


def _summary_area_rows(part: str) -> list[tuple[str, str, str]]:
    return re.findall(
        r'<dt class="finding-head">(\s*<div>\s*<a href="#readiness-([^"]+)".*?</dt>)'
        r"\s*<dd>\s*(.*?)\s*</dd>",
        part,
        re.S,
    )


def test_summary_caps_blockers_and_open_areas_in_catalogue_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = tmp_path / "rules"
    copytree(Path(str(rules.rules_dir())), copied)
    path = copied / "status.yaml"
    amended = re.sub(
        r"^(        status: )needs_work$", r"\g<1>blocker", read_text(path), flags=re.M
    )
    path.write_text(amended, encoding="utf-8")
    monkeypatch.setattr(rules, "rules_dir", lambda: copied)

    html = _sample_report("town", tmp_path / "out", "en", "opendesk")
    summary = unescape(report_section(html, "summary"))
    blockers, open_part = summary.split('data-summary="unknown"', 1)
    readiness = report_section(html, "readiness")
    assessed = catalogue.load_catalogue().assessed_workload_ids
    blocker_ids = [
        workload
        for workload in assessed
        if 'data-status="blocker"' in readiness_row(readiness, workload)
    ]
    assert len(blocker_ids) > 3
    rows = _summary_area_rows(blockers)
    assert [workload for _, workload, _ in rows] == blocker_ids[:3]
    strings = load_locale("en")
    assert strings["summary"]["confirmed"].format(shown=3, total=len(blocker_ids)) in blockers
    all_blockers = strings["summary"]["all_blockers"]
    assert (
        f'href="#status-blocker"><span class="symbol-text">'
        f'<span class="link-text">{all_blockers}</span>' in blockers
    )

    for term, workload, detail in rows:
        card = readiness_row(readiness, workload)
        reason = re.search(r'<div class="finding-reason">\s*([^<]+)', unescape(card))[1].strip()
        assert detail == reason
        assert (strings["readiness"]["incomplete"] in term) == (" data-incomplete" in card)

    open_ids = [
        workload
        for workload in assessed
        if re.search(
            r'<article [^>]*(data-status="unknown"|data-incomplete)',
            readiness_row(readiness, workload),
        )
    ]
    assert len(open_ids) > 4
    open_rows = _summary_area_rows(open_part)
    assert [workload for _, workload, _ in open_rows] == open_ids[:4]
    for _, workload, fix in open_rows:
        card = readiness_row(readiness, workload)
        if 'data-status="unknown"' in card:
            reason_part = card.split('<div class="finding-reason">', 1)[1].split("</div>", 1)[0]
        else:
            reason_part = re.search(r'<li data-missing="[^"]+">.*?</li>', card, re.S)[0]
        reason_code = re.search(r'data-reason="([^"]+)"', reason_part)[1]
        gaps = re.findall(r'<li data-missing="([^"]+)">.*?data-reason="([^"]+)"', card, re.S)
        finding_id = next((id for id, code in gaps if code == reason_code), gaps[0][0])
        question = strings["path"]["questions"][finding_id]
        if reason_code == "answer_not_provided":
            assert " ".join(fix.split()) == question
        else:
            assert " ".join(fix.split()) == f"{question} {strings['reason'][reason_code]['fix']}"


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_summary_counts_and_links_match_the_report(tmp_path: Path, sample: str, lang: str) -> None:
    html = _sample_report(sample, tmp_path, lang, "opendesk")
    summary = report_section(html, "summary")
    document = ReportDocument(html)
    formatter = Formatter(lang)
    strings = formatter.strings
    counts = Counter(attrs["data-status"] for tag, attrs in document.tags if tag == "article")
    _assert_status_summary(summary, counts, formatter)

    assert counts["blocker"] <= 3
    assert strings["summary"]["confirmed"].split("{shown}")[0] not in summary
    all_blockers = strings["summary"]["all_blockers"]
    blocker_link = (
        f'href="#status-blocker"><span class="symbol-text">'
        f'<span class="link-text">{all_blockers}</span>'
    )
    assert (blocker_link in summary) == (counts["blocker"] > 0)
    assert not any(text in summary for text in ("data-segment", "readiness-bar", "%"))
    ids = {attrs.get("id") for _, attrs in document.tags}
    links = re.findall(r'href="#([^"]+)"', summary)
    assert "not-examined" in links and set(links) <= ids
    missing = set(re.findall(r'data-missing-cost="([^"]+)"', report_section(html, "costs")))
    assert ("costs-missing" in links) == bool(missing)
    if missing:
        assert strings["costs"]["inputs_missing_one"].format(n=len(missing)) in summary
        assert strings["costs"]["missing_fix"] in summary


@pytest.mark.parametrize("lang", ["en", "de"])
def test_summary_keeps_all_unknown_areas_unknown(tmp_path: Path, lang: str) -> None:
    html = rebuild_report(ALL_UNKNOWN_SCAN, tmp_path, lang)
    summary = report_section(html, "summary")
    readiness = report_section(html, "readiness")
    formatter = Formatter(lang)
    strings = formatter.strings
    unknown_areas = re.findall(r'<article data-workload="([^"]+)" data-status="unknown"', readiness)
    assert len(unknown_areas) == readiness.count("<article ")
    _assert_status_summary(summary, Counter(unknown=len(unknown_areas)), formatter)
    assert strings["path"]["empty"]["blocker"] in unescape(summary)
    assert strings["summary"]["caveat"].format(n=formatter.integer(len(unknown_areas))) in summary
    assert [workload for _, workload, _ in _summary_area_rows(summary)] == unknown_areas[:4]
    open_points = strings["summary"]["not_examined"]
    assert (
        'href="#not-examined"><span class="symbol-text">'
        f'<span class="link-text">{open_points}</span>' in summary
    )
    costs = report_section(html, "costs")
    missing = re.findall(r'data-missing-cost="([^"]+)"', costs)
    assert 0 < len(set(missing)) < len(missing)
    missing_label = strings["costs"]["inputs_missing"].format(
        n=formatter.integer(len(set(missing)))
    )
    assert (
        'href="#costs-missing"><span class="symbol-text">'
        f'<span class="link-text">{missing_label}</span>' in summary
    )
    assert 'id="costs-missing">' in costs and strings["costs"]["missing_fix"] in costs
    assert "#status-blocker" not in summary


def _open_point_rows(path: str) -> list[tuple[str, str]]:
    return re.findall(r'<dt data-open-point="([^"]+)">(.*?)</dd>', path, re.S)


@pytest.mark.parametrize(
    ("sample", "lang"), [*SAMPLES, ("all-unknown", "en"), ("all-unknown", "de")]
)
def test_open_points_include_every_gap_unknown_finding_and_skipped_collector(
    sample: str, lang: str
) -> None:
    entries = catalogue.load_catalogue()
    if sample == "all-unknown":
        scan, inputs = load_scan(ALL_UNKNOWN_SCAN, entries), None
    else:
        scan = load_scan(sample_scan_path(sample), entries)
        inputs = load_inputs(sample_inputs_path(sample), entries)
    context, plans = report_module._prepare_report(scan, lang, "opendesk", entries, inputs)
    html = report_module._render_html(context)
    path = report_section(html, "path")
    points = _open_point_rows(path)
    statuses = context["statuses"]
    unknown_areas = {row.workload for row in statuses if row.status == "unknown"}
    strings = load_locale(lang)
    roles = set(strings["role"].values())

    assert points and len(dict(points)) == len(points)
    assert html.count('id="not-examined"') == 1 and '<h4 id="not-examined">' in path
    assert "not-examined" not in report_section(html, "readiness")
    assert "<ol" not in path and not re.search(r"\bdata-path-(?:status|workload)\b", path)
    assert Counter(re.findall(r'data-unexamined-collector="([^"]+)"', path)) == {
        collector.id: 1 for collector in scan.collectors if collector.status == "skipped"
    }
    merged = context["scan"]
    findings = (*merged.findings, *licence_findings(merged, plans, entries))
    assert Counter(re.findall(r'data-unexamined-finding="([^"]+)"', path)) == {
        finding.id: 1 for finding in findings if finding.provenance == "unknown"
    }
    assert set(re.findall(r'data-unexamined-workload="([^"]+)"', path)) == unknown_areas
    gaps = set()
    for key, body in points:
        assert not key.startswith(("confirmations.", "provided_counts.")) or (
            f"<code>{key}</code>" in body.replace("<wbr>", "")
        )
        owner = re.search(r'<p><span class="open-label">[^<]+</span>\s*([^<]+)', unescape(body))
        assert owner and set(owner[1].strip().split(" · ")) <= roles
        tags = ReportDocument(body).tags
        links = {}
        for tag, attrs in tags:
            if tag == "a":
                workload = attrs["href"].removeprefix("#readiness-")
                assert workload not in links
                links[workload] = attrs
                assert attrs.get("data-unexamined-workload") == (
                    workload if workload in unknown_areas else None
                )
        for tag, attrs in tags:
            if tag == "span" and (gap := attrs.get("data-unexamined-gap")):
                assert attrs.get("data-unexamined-finding", gap) == gap
                areas = attrs["data-areas"].split()
                assert areas and set(areas) <= links.keys()
                gaps.update((area, gap) for area in areas)
    assert gaps == {(row.workload, gap.finding_id) for row in statuses for gap in row.missing}
    if sample == "town":
        recipients = dict(points)["collector.exchange_recipients"]
        assert 'data-unexamined-collector="exchange_recipients"' in recipients
        assert 'data-unexamined-finding="mail.shared_mailbox_count"' in recipients
        assert 'href="#readiness-mail"' in recipients
        assert recipients.count(strings["path"]["questions"]["mail.shared_mailbox_count"]) == 1
        assert recipients.count(strings["collector"]["exchange_recipients"]) == 1
        assert re.search(
            rf"{strings['path']['who_answers']}</span>\s*{strings['role']['it_team']}", recipients
        )
    if sample == "nonprofit":
        sharepoint = unescape(dict(points)["collector.sharepoint_site_usage"])
        fix = strings["reason"]["collector_skipped"]["fix"]
        assert sharepoint.count(fix) == 1
        assert strings["path"]["guidance"]["source_not_supplied"] not in sharepoint


def test_open_points_group_both_software_counts_by_the_input_list(tmp_path: Path) -> None:
    html = rebuild_report(sample_scan_path("town"), tmp_path, "en")
    points = dict(_open_point_rows(report_section(html, "path")))
    software = points["windows_only_software"]
    assert re.findall(r'data-unexamined-gap="([^"]+)"', software) == [
        "windows_software.application_count",
        "windows_software.without_web_version_count",
    ]
    assert software.count('href="#readiness-windows_software"') == 1
    assert "<code>windows_only_software</code>" in software


@pytest.mark.parametrize("lang", ["en", "de"])
def test_manual_open_points_name_the_actual_question_and_input(tmp_path: Path, lang: str) -> None:
    html = _sample_report("town", tmp_path, lang, "opendesk")
    summary = unescape(report_section(html, "summary"))
    path = unescape(report_section(html, "path"))
    strings = load_locale(lang)
    points = dict(_open_point_rows(path))
    for finding_id in (
        "sharepoint.workflows_in_use",
        "office_files.vba_macros_in_use",
        "device_management.windows_desktops_required",
    ):
        key = f"confirmations.{finding_id}"
        question = strings["path"]["questions"][finding_id]
        assert question in points[key].split("</dt>")[0]
        assert question in summary
        wrapped_key = key.replace(".", ".<wbr>")
        assert f"{strings['path']['input_field']}</span> <code>{wrapped_key}</code>" in points[key]
        assert strings["reason"]["answer_not_provided"]["fix"] not in points[key]
        workload = finding_id.split(".")[0]
        card = unescape(readiness_row(html, workload))
        missing = re.search(rf'<li data-missing="{re.escape(finding_id)}">(.*?)</li>', card, re.S)[
            1
        ]
        assert question in missing and f"<code>{wrapped_key}</code>" in missing
        assert strings["path"]["who_answers"] in missing
        entry = catalogue.load_catalogue().finding(finding_id)
        assert entry and strings["role"][entry.owner] in missing
        assert strings["reason"]["answer_not_provided"]["fix"] not in missing


def _path_action_rows(part: str) -> list[tuple[str, list[tuple[str, str]]]]:
    groups = re.findall(
        r'<dt><a href="#readiness-([^"]+)" class="area-link more\b[^"]*">.*?</a></dt>\s*'
        r'<dd>\s*<ul class="path-actions">(.*?)</ul>',
        part,
        re.S,
    )
    return [
        (workload, re.findall(r'<li data-step-kind="([^"]+)">([^<]+)</li>', items))
        for workload, items in groups
    ]


@pytest.mark.parametrize(("sample", "lang"), SAMPLES)
def test_next_steps_group_actions_by_area_in_display_order(sample: str, lang: str) -> None:
    entries = catalogue.load_catalogue()
    scan = load_scan(sample_scan_path(sample), entries)
    inputs = load_inputs(sample_inputs_path(sample), entries)
    context, _ = report_module._prepare_report(scan, lang, "opendesk", entries, inputs)
    path = unescape(report_section(report_module._render_html(context), "path"))
    before, after = path.split('id="not-examined"')
    templates = context["status_rules"].target_gaps
    transfer_copy = load_locale(lang)["path"]["transfer_actions"]
    expected_stay: dict[str, list[tuple[str, str]]] = {}
    expected_move: dict[str, list[tuple[str, str]]] = {}
    for status in ("blocker", "needs_work"):
        for row in (row for row in context["statuses"] if row.status == status):
            grouped: set[str] = set()
            for rule in (row.deciding, *row.notes):
                target = next(
                    (
                        code
                        for code, template in templates.items()
                        if rule.id.startswith(template.id + "-")
                    ),
                    None,
                )
                kind, text = rule.next_step.kind, rule.next_step.text[lang]
                if target in grouped:
                    continue
                if target is not None:
                    grouped.add(target)
                    affected = [
                        gap.mapping
                        for gap in row.transfer_gaps
                        if gap.need == "yes" and gap.mapping.coverage == target
                    ]
                    assert affected
                    function_key = f"{target}.{affected[0].function}"
                    copy = transfer_copy.get(function_key) if len(affected) == 1 else None
                    text = (copy or transfer_copy[target]).format(
                        functions=", ".join(item.microsoft[lang] for item in affected)
                    )
                group = expected_move if kind == "replace" else expected_stay
                group.setdefault(row.workload, []).append((kind, text))
    assert _path_action_rows(before) == list(expected_stay.items())
    assert _path_action_rows(after) == list(expected_move.items())
    assert path.count("data-step-kind=") == sum(
        len(actions) for actions in (*expected_stay.values(), *expected_move.values())
    )


@pytest.mark.parametrize("lang", ["en", "de"])
def test_next_steps_name_both_functions_in_one_transfer_action(lang: str) -> None:
    entries = catalogue.load_catalogue()
    scan = load_scan(sample_scan_path("town"), entries)
    inputs = load_inputs(sample_inputs_path("town"), entries)
    inputs = replace(
        inputs,
        confirmations=inputs.confirmations | {"device_management.windows_desktops_required": True},
    )
    context, _ = report_module._prepare_report(scan, lang, "opendesk", entries, inputs)
    path = unescape(report_section(report_module._render_html(context), "path"))
    rows = _path_action_rows(path.split('id="not-examined"')[1])
    device_rows = [actions for workload, actions in rows if workload == "device_management"]
    assert len(device_rows) == 1
    functions = ", ".join(
        item.microsoft[lang]
        for item in context["mapping"].functions
        if item.function in ("device_management", "desktop_operating_system")
    )
    action = load_locale(lang)["path"]["transfer_actions"]["not_available"]
    assert device_rows[0].count(("replace", action.format(functions=functions))) == 1


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize("profile", PROFILES)
def test_summary_scope_matches_the_replacements_and_gaps(lang: str, profile: str) -> None:
    entries = catalogue.load_catalogue()
    scan = load_scan(sample_scan_path("town"), entries)
    inputs = load_inputs(sample_inputs_path("town"), entries)
    context, _ = report_module._prepare_report(scan, lang, profile, entries, inputs)
    scope = context["scope_statement"]
    html = report_module._render_html(context)
    summary = unescape(report_section(html, "summary"))
    if profile == "generic":
        assert scope is None and 'data-summary="scope"' not in summary
        return
    assert isinstance(scope, report_module.ScopeStatement)
    summary = summary.split('data-summary="scope"', 1)[1]
    formatter = Formatter(lang)
    strings = formatter.strings
    blocks = re.search(r"<h3>([^<]+)</h3>\s*<p>([^<]+)</p>", summary)
    assert blocks is not None
    assert blocks[1] == strings["summary"]["scope_title"].format(profile=scope.profile)
    intro = strings["summary"]["scope_of"].format(n=scope.total, profile=scope.profile)
    assert blocks[2] == intro
    coverage = re.search(r'<dl class="coverage-summary">(.*?)</dl>', summary, re.S)
    assert coverage
    assert re.findall(r'<dt>([^<]+)</dt>\s*<dd class="row-count">([^<]+)</dd>', coverage[1]) == [
        (strings["mapping_coverage"][code], formatter.integer(count))
        for code, count in scope.by_coverage
    ]
    needed = re.search(r'<ul class="scope-links" role="list">(.*?)</ul>', summary, re.S)
    assert needed and scope.needed
    chevron = REPORT_ICONS.joinpath("chevron-right.svg").read_text(encoding="utf-8")
    path = re.search(r'<path d="([^"]+)"', chevron)[1]
    links = re.findall(
        r'<li><a href="#(replacement-[^"]+)" class="area-link more\b[^"]*">'
        r'<span class="symbol-text"><span class="link-text">([^<]+)</span>'
        r'<span class="chevron-tail[^"]*" aria-hidden="true">'
        r'<svg class="chevron"[^>]*><path d="([^"]+)"/></svg></span></span></a></li>',
        needed[1],
    )
    assert links == [
        (f"replacement-{anchor.removeprefix('transfer-gap-')}", name, path)
        for name, anchor in scope.needed
    ]
    moves = unescape(report_section(html, "moves"))
    replacements = dict(
        re.findall(r'<tr[^>]* id="(replacement-[^"]+)">\s*<th[^>]*>([^<]+)</th>', moves)
    )
    assert all(replacements[target] == name for target, name, _ in links)
    assert (
        strings["summary"]["scope_unknown"].format(n=scope.unknown_need, profile=scope.profile)
        in summary
    )
    assert summary.count(strings["moves"]["unreviewed"]) == 1

    reviewed_context = context | {"scope_statement": replace(scope, reviewed_on=date(2026, 11, 22))}
    reviewed = report_section(report_module._render_html(reviewed_context), "summary")
    assert strings["moves"]["unreviewed"] not in reviewed


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
        assert re.search(
            rf'<p class="finding-status">.*?</svg><span class="symbol-text">{label}</span>',
            card,
            re.S,
        )
        incomplete = strings["readiness"]["incomplete"]
        assert bool(
            re.search(
                rf'<span class="badge\b[^"]*"><span class="symbol-text">{incomplete}</span>', card
            )
        ) == (" data-incomplete" in card)
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
        copy = load_locale(lang)["readiness"]
        expected = copy["evidence_summary"].format(
            **{kind: counts[kind] for kind in ("measured", "provided", "unknown")}
        )
        assert re.search(
            rf'<summary id="evidence-{workload}"[^>]*>.*?</svg>\s*'
            rf'<span class="symbol-text">{copy["evidence"]}\s*'
            rf'<small class="evidence-counts">{expected}</small>',
            detail,
            re.S,
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
    assert '<small class="evidence-counts">0 measured, 2 provided, 0 unknown</small>' in card
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
    (status_group,) = re.findall(
        r'<fieldset class="segmented" data-filter="status">(.*?)</fieldset>', readiness, re.S
    )
    cards = [attrs for tag, attrs in ReportDocument(readiness).tags if tag == "article"]
    counts = Counter(card["data-status"] for card in cards)
    category_ids = [category.id for category in entries.categories]
    assert {card["data-category"] for card in cards} == set(category_ids)

    assert f'<legend class="sr-only">{strings["filter"]["status_legend"]}</legend>' in status_group
    labels = re.findall(r"(<label\b[^>]*>)(.*?)</label>", status_group, re.S)
    radios = [attrs for tag, attrs in ReportDocument(status_group).tags if tag == "input"]
    assert len(labels) == len(radios) == len(DISPLAY_ORDER) + 1
    for option, (tag, label), radio in zip(("all", *DISPLAY_ORDER), labels, radios, strict=True):
        assert radio["type"] == "radio" and radio["name"] == "f-status"
        assert radio["id"] == f"f-status-{option}"
        assert "<input " in label
        assert ("checked" in radio) is (option == "all")
        assert ("disabled" in radio) is (option != "all" and not counts[option])
        text = unescape(" ".join(re.sub(r"<[^>]*>", "", label).split()))
        count = len(entries.assessed_workload_ids) if option == "all" else counts[option]
        name = strings["filter"]["all"] if option == "all" else strings["status"][option]
        assert text == f"{name} {formatter.integer(count)}"
        assert ("<svg" in label) is (option != "all")
        assert "aria-label" not in radio
        if option != "all":
            assert f'title="{name}"' in unescape(tag)
            assert f'<span class="symbol-text segment-name">{name}</span>' in unescape(label)

    ((legend, category_menu),) = re.findall(
        r'<select id="f-category" name="f-category" aria-label="([^"]+)"[^>]*>(.*?)</select>',
        readiness,
        re.S,
    )
    assert unescape(legend) == strings["filter"]["category_legend"]
    options = re.findall(
        r'<option id="f-category-([^"]+)" value="([^"]+)" class="symbol-label"( selected)?>'
        r'<svg[^>]*>.*?</svg><span class="symbol-text">([^<]+)</span></option>',
        category_menu,
    )
    assert options == [
        ("all", "all", " selected", strings["filter"]["all_categories"]),
        *((id, id, "", strings["category"][id]) for id in category_ids),
    ]
    assert re.findall(
        r'<span class="category-label" data-category-label="([^"]+)" aria-hidden="true">'
        r"([^<]+)</span>",
        readiness,
    ) == [(id, text) for id, _, _, text in options]

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

    policies = offline_policies(document)
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


@pytest.mark.parametrize(
    ("lang", "demo_home"), [("en", "https://fazit.dev/"), ("de", "https://fazit.dev/de/")]
)
def test_only_the_demo_wordmark_links_to_the_website(
    tmp_path: Path, lang: str, demo_home: str
) -> None:
    result = runner.invoke(app, ["demo", "--lang", lang, "--out", str(tmp_path / "demo")])
    assert result.exit_code == 0, result.output
    demo = ReportDocument(Path(result.stdout.splitlines()[-1]).read_text(encoding="utf-8"))
    inputs = tmp_path / "inputs.yaml"
    inputs.write_text("organisation_name: West Weir Council\n", encoding="utf-8")
    report = ReportDocument(
        rebuild_report(ALL_UNKNOWN_SCAN, tmp_path / "report", lang, inputs=inputs)
    )

    for document, href in ((demo, demo_home), (report, "#main")):
        wordmarks = [
            attrs for tag, attrs in document.tags if tag == "a" and attrs.get("class") == "wordmark"
        ]
        assert wordmarks == [{"class": "wordmark", "href": href}]
        policies = offline_policies(document, demo_home=demo_home if document is demo else None)
        assert len(policies) == 1 and "default-src 'none'" in policies[0]


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
def test_report_document_structure(
    tmp_path: Path, style_references: dict[str, str], sample: str, lang: str, profile: str
) -> None:
    html = _sample_report(sample, tmp_path, lang, profile)
    document = ReportDocument(html)
    (reference_css,) = ReportDocument(style_references[lang]).styles
    assert document.styles == [reference_css]

    metas = {
        attrs.get("name"): attrs.get("content") for tag, attrs in document.tags if tag == "meta"
    }
    assert "width=device-width" in (metas.get("viewport") or "")
    assert metas.get("color-scheme") == "light dark"

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

    # Colour is never the only cue: every status label carries its own symbol and its text.
    icons = set(STATUS_PATHS.findall(html))
    assert {status for status, _ in icons} == set(DISPLAY_ORDER)
    assert len({path for _, path in icons}) == len(icons) == len(DISPLAY_ORDER)


def _srgb(color: str) -> tuple[float, ...]:
    return tuple(int(color[i : i + 2], 16) / 255 for i in (1, 3, 5))


def _luminance(color: str | tuple[float, ...]) -> float:
    channels = _srgb(color) if isinstance(color, str) else color
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return sum(
        value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True)
    )


@pytest.mark.parametrize("lang", ("en", "de"))
def test_report_styles_work_in_light_dark_narrow_and_print(
    style_references: dict[str, str], lang: str
) -> None:
    (css,) = ReportDocument(style_references[lang]).styles
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
    assert re.search(r"@media[^{}]+\(max-width:\s*40rem\)", css)
    assert re.search(r"content:\s*attr\(data-label\)", css)
    assert re.search(r"@page\s*\{\s*margin:", css)
    assert re.search(r"@media\s+print\s*\{", css)
    assert re.search(r"break-inside:\s*avoid", css)
    assert re.search(r"print-color-adjust:\s*exact", css)
    screen_css, print_css = css.split("@media print", 1)
    assert re.search(r"\.scope-links\s*\{[^}]*list-style:\s*none", screen_css)
    assert not re.search(r"\.scope-links a\s*\{[^}]*text-decoration:\s*underline", screen_css)
    assert re.search(r"::details-content\s*\{[^}]*content-visibility:\s*visible", print_css)


@pytest.mark.parametrize("lang", ("en", "de"))
def test_report_styles_follow_the_design_rules(style_references: dict[str, str], lang: str) -> None:
    html = style_references[lang]
    (css,) = ReportDocument(html).styles
    css = re.sub(r"/\*.*?\*/", "", EMBEDDED_FONT.sub("", css), flags=re.S)
    for prop, value in CSS_DECLARATION.findall(CSS_ROOT.sub("", css)):
        for colour in CSS_COLOUR.findall(value):
            assert prop.lower() == "box-shadow" and colour == "rgb(0 0 0 / 12%)", (prop, value)
    assert not (font_errors := list(check_font_families(css))), font_errors

    moves = report_section(html, "moves")
    coverage_cells = re.findall(r'<span class="cov-cell\b[^"]*">.*?</td>', moves, re.S)
    coverage_paths = set(re.findall(r'<path d="([^"]+)"', "".join(coverage_cells)))
    status_paths = {path for _, path in STATUS_PATHS.findall(html)}
    assert coverage_paths and status_paths, "Coverage cells and status labels both need symbols"
    assert coverage_paths.isdisjoint(status_paths), (
        "Coverage cells reuse a status symbol",
        coverage_paths & status_paths,
    )


def test_print_hides_controls_opens_disclosures_and_starts_working_sections_on_new_pages(
    tmp_path: Path,
) -> None:
    html = _sample_report("town", tmp_path, "en", "opendesk")
    (css,) = ReportDocument(html).styles
    print_css = css.split("@media print", 1)[1]
    rules = re.findall(r"([^{}]+)\{([^{}]+)\}", print_css)
    hidden = set()
    page_starts = set()
    for selectors, declarations in rules:
        names = {selector.strip() for selector in selectors.split(",")}
        if re.search(r"display:\s*none", declarations):
            hidden.update(names)
        if re.search(r"break-before:\s*page", declarations):
            page_starts.update(names)
    assert {".bar", ".skip", ".filters", ".areas-empty"} <= hidden
    assert page_starts == {"[data-section=path]", "[data-section=costs]", "[data-section=appendix]"}
    disclosure = re.search(r"details::details-content\s*\{([^}]+)\}", print_css)
    assert disclosure
    for declaration in ("content-visibility: visible", "display: block", "block-size: auto"):
        assert declaration in disclosure[1]


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


def test_status_palette_is_shared_by_the_site_and_report(style_references: dict[str, str]) -> None:
    (report,) = ReportDocument(style_references["en"]).styles
    template = (ROOT / "src" / "fazit" / "templates" / "report.html.j2").read_text("utf-8")
    sources = [template, report]
    site = ROOT / "site" / "style.css"
    if site.is_file() or not (ROOT / "PKG-INFO").is_file():
        sources.append(site.read_text("utf-8"))
    palettes = {
        "": {
            "blocker": "light-dark(#ff8d28,#ff9230)",
            "needs-work": "light-dark(#ffcc00,#ffd600)",
            "ready": "light-dark(#34c759,#30d158)",
            "unknown": "#8e8e93",
        },
        "@media screen and (prefers-contrast: more)": {
            "blocker": "light-dark(#c55300,#ffa056)",
            "needs-work": "light-dark(#a16a00,#fedf43)",
            "ready": "light-dark(#008932,#4ad968)",
            "unknown": "light-dark(#6c6c70,#aeaeb2)",
        },
    }
    for css in sources:
        for media, expected in palettes.items():
            start = re.escape(media) + r"\s*\{\s*" if media else ""
            root = re.search(start + r":root\s*\{([^}]+)\}", css)
            assert root, media
            values = re.findall(r"--status-([\w-]+):\s*([^;]+);", root[1])
            assert {key: re.sub(r"\s+", "", value.lower()) for key, value in values} == expected
        for status in palettes[""]:
            assert len(re.findall(rf"--status-{status}\s*:", css)) == len(palettes)
            selector = status.replace("-", "_")
            assert f".{selector} {{ --status-fill: var(--status-{status}); }}" in css
        assert re.search(r"@media print\s*\{\s*:root\s*\{\s*color-scheme:\s*light;", css)
        assert re.search(r"\.status > \.icon\s*\{\s*color:\s*var\(--status-fill\);\s*\}", css)
        assert re.search(
            r"\.badge\.status\s*\{\s*color:\s*light-dark\(var\(--fg\),\s*var\(--status-fill\)\);"
            r"\s*background:\s*color-mix\(in srgb,\s*"
            r"var\(--status-fill\)\s*12%,\s*var\(--fill\)\);",
            css,
        )
        base_badge = re.search(r"^\s*\.badge\s*\{([^}]+)\}", css, re.M)
        assert base_badge and "background: var(--fill-2);" in base_badge[1]
        assert "color:" not in base_badge[1]


@pytest.mark.parametrize("theme", ("light", "dark"))
@pytest.mark.parametrize("more_contrast", (False, True))
def test_badge_labels_clear_small_text_contrast(
    style_references: dict[str, str], theme: str, more_contrast: bool
) -> None:
    (css,) = ReportDocument(style_references["en"]).styles
    default = re.search(r":root\s*\{([^}]+)\}", css)
    dark = re.search(r"prefers-color-scheme: dark\)\s*\{\s*:root\s*\{([^}]+)\}", css)
    increased = re.search(r"prefers-contrast: more\)\s*\{\s*:root\s*\{([^}]+)\}", css)
    assert default and dark and increased
    surfaces = dict(CSS_DECLARATION.findall(dark[1] if theme == "dark" else default[1]))
    palette = dict(CSS_DECLARATION.findall(increased[1] if more_contrast else default[1]))
    surface = _srgb(surfaces["--surface"].strip())
    for status in DISPLAY_ORDER:
        values = re.findall(r"#[0-9a-f]{6}", palette[f"--status-{status.replace('_', '-')}"])
        color = values[-1] if theme == "dark" else values[0]
        label = color if theme == "dark" else surfaces["--text"].strip()
        tint = tuple(0.12 * a + 0.88 * b for a, b in zip(_srgb(color), surface, strict=True))
        low, high = sorted((_luminance(label), _luminance(tint)))
        assert (high + 0.05) / (low + 0.05) >= 4.5, (theme, more_contrast, status)


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
        assert '<time datetime="2026-11-10">10\u00a0November\u00a02026</time>' in details
        assert '<time datetime="2026-11-10">10\u00a0November\u00a02026</time>' in header
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
