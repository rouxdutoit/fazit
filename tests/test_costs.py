# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction
from html import unescape
from pathlib import Path

import pytest
from helpers import (
    ROOT,
    rebuild_report,
    report_section,
    runner,
    sample_inputs_path,
    sample_scan_path,
)

from fazit import report as report_module
from fazit.catalogue import load_catalogue
from fazit.cli import app
from fazit.costs import BLOCKS, SCENARIOS, CostGroup, ScenarioResult, compute_scenarios
from fazit.i18n import Formatter, load_locale
from fazit.inputs import CurrentCosts, Inputs, ScenarioInputs, load_inputs
from fazit.model import load_scan


@pytest.fixture
def worked_example() -> Inputs:
    return Inputs(
        currency="EUR",
        current_costs=CurrentCosts(Decimal("100000"), Decimal("20000")),
        partial_exit=ScenarioInputs(
            users=30,
            retained_microsoft_licences_per_year=Decimal("60000"),
            hosting_per_user_per_month=Decimal("8.50"),
            operations_per_year=Decimal("6000"),
            other_recurring_per_year=Decimal("1500"),
            one_time_migration=Decimal("15000"),
            application_adaptation=Decimal("4000"),
            external_advice=Decimal("3000"),
            training_days_per_person=Decimal("2"),
            training_day_rate=Decimal("400"),
            training_staff=30,
            productivity_loss=Decimal("9000"),
            parallel_running_months=6,
        ),
        full_exit=ScenarioInputs(
            users=85,
            retained_microsoft_licences_per_year=Decimal("0"),
            hosting_per_user_per_month=Decimal("8.50"),
            operations_per_year=Decimal("12000"),
            other_recurring_per_year=Decimal("2000"),
            one_time_migration=Decimal("40000"),
            application_adaptation=Decimal("10000"),
            external_advice=Decimal("8000"),
            training_days_per_person=Decimal("2"),
            training_day_rate=Decimal("400"),
            training_staff=85,
            productivity_loss=Decimal("25000"),
            parallel_running_months=12,
        ),
    )


def _amounts(group: CostGroup) -> dict[str, Fraction | None]:
    return {line.id: line.amount for line in group.lines}


def _groups(result: ScenarioResult) -> tuple[CostGroup, ...]:
    return (result.running, *result.blocks)


def test_worked_example(worked_example: Inputs) -> None:
    stay, partial, full = compute_scenarios(worked_example)

    assert (stay.id, partial.id, full.id) == SCENARIOS
    assert [result.total for result in (stay, partial, full)] == [600000, 527800, 464350]
    assert [result.difference_to_stay for result in (stay, partial, full)] == [0, -72200, -135650]
    assert all(result.missing_inputs == () for result in (stay, partial, full))
    assert tuple(group.id for group in stay.blocks) == BLOCKS
    assert _amounts(stay.running) == {"microsoft_licences": 500000, "other_it": 100000}
    assert [group.total for group in _groups(stay)] == [600000, 0, 0, 0]
    assert _amounts(partial.running) == {
        "retained_licences": 270000,
        "hosting": 15300,
        "operations": 30000,
        "other_recurring": 7500,
        "other_it": 100000,
    }
    assert _amounts(full.running) == {
        "retained_licences": 0,
        "hosting": 43350,
        "operations": 60000,
        "other_recurring": 10000,
        "other_it": 100000,
    }
    for result, totals, direct_lines in (
        (partial, [422800, 46000, 9000, 50000], [15000, 4000, 3000, 24000]),
        (full, [213350, 126000, 25000, 100000], [40000, 10000, 8000, 68000]),
    ):
        direct, loss, overlap = result.blocks
        assert tuple(group.id for group in result.blocks) == BLOCKS
        assert [group.total for group in _groups(result)] == totals
        assert _amounts(direct) == dict(
            zip(
                ("one_time_migration", "application_adaptation", "external_advice", "training"),
                direct_lines,
                strict=True,
            )
        )
        assert _amounts(loss) == {"productivity_loss": totals[2]}
        assert _amounts(overlap) == {"parallel_running": totals[3]}


def test_zero_overlap_without_current_licence_cost(worked_example: Inputs) -> None:
    inputs = replace(
        worked_example,
        current_costs=replace(worked_example.current_costs, microsoft_licences_per_year=None),
        partial_exit=replace(worked_example.partial_exit, parallel_running_months=0),
    )

    stay, partial, _ = compute_scenarios(inputs)

    assert partial.blocks[2].total == 0
    assert partial.total == 507800
    assert stay.total is partial.difference_to_stay is None
    assert stay.missing_inputs == ("current_costs.microsoft_licences_per_year",)
    assert partial.missing_inputs == ()


def test_full_overlap_without_retained_licence_cost(worked_example: Inputs) -> None:
    inputs = replace(
        worked_example,
        partial_exit=replace(
            worked_example.partial_exit,
            parallel_running_months=60,
            retained_microsoft_licences_per_year=None,
        ),
    )

    _, partial, _ = compute_scenarios(inputs)

    assert _amounts(partial.running)["retained_licences"] == 0
    assert partial.blocks[2].total == 500000
    assert partial.total == 707800
    assert partial.missing_inputs == ()


@pytest.mark.parametrize(
    ("target", "group", "line"),
    [
        (ScenarioInputs(hosting_per_user_per_month=Decimal(0)), 0, "hosting"),
        (ScenarioInputs(users=0), 0, "hosting"),
        (ScenarioInputs(training_days_per_person=Decimal(0)), 1, "training"),
        (ScenarioInputs(retained_microsoft_licences_per_year=Decimal(0)), 0, "retained_licences"),
    ],
)
def test_zero_factor_makes_unknown_factors_immaterial(
    target: ScenarioInputs, group: int, line: str
) -> None:
    _, result, _ = compute_scenarios(Inputs(partial_exit=target))

    cost_line = next(item for item in _groups(result)[group].lines if item.id == line)
    assert cost_line.amount == 0
    assert cost_line.missing == ()


def test_unknown_productivity_loss_only_affects_its_scenario(worked_example: Inputs) -> None:
    complete = compute_scenarios(worked_example)
    inputs = replace(
        worked_example, full_exit=replace(worked_example.full_exit, productivity_loss=None)
    )

    results = compute_scenarios(inputs)

    assert results[:2] == complete[:2]
    full = results[2]
    assert full.blocks[1].total is full.total is full.difference_to_stay is None
    assert full.missing_inputs == ("target_costs.full_exit.productivity_loss",)


def test_unknown_other_it_affects_all_scenarios(worked_example: Inputs) -> None:
    inputs = replace(
        worked_example, current_costs=replace(worked_example.current_costs, other_it_per_year=None)
    )
    for result in compute_scenarios(inputs):
        assert result.running.total is result.total is result.difference_to_stay is None
        assert result.missing_inputs == ("current_costs.other_it_per_year",)


def test_empty_costs_have_no_defaults() -> None:
    stay, *exits = compute_scenarios(Inputs())

    assert stay.missing_inputs == (
        "current_costs.microsoft_licences_per_year",
        "current_costs.other_it_per_year",
    )
    assert all(group.total == 0 and group.missing == () for group in stay.blocks)
    for result in exits:
        prefix = f"target_costs.{result.id}."
        assert result.missing_inputs == (
            prefix + "retained_microsoft_licences_per_year",
            prefix + "parallel_running_months",
            prefix + "hosting_per_user_per_month",
            prefix + "users",
            prefix + "operations_per_year",
            prefix + "other_recurring_per_year",
            "current_costs.other_it_per_year",
            prefix + "one_time_migration",
            prefix + "application_adaptation",
            prefix + "external_advice",
            prefix + "training_days_per_person",
            prefix + "training_day_rate",
            prefix + "training_staff",
            prefix + "productivity_loss",
            "current_costs.microsoft_licences_per_year",
        )
        assert all(group.total is None and group.missing for group in _groups(result))
    for result in (stay, *exits):
        assert result.total is result.difference_to_stay is None
        assert all(
            line.amount is None and line.missing
            for group in _groups(result)
            for line in group.lines
        )


def test_hosting_changes_with_the_input(worked_example: Inputs) -> None:
    before = compute_scenarios(worked_example)
    inputs = replace(
        worked_example,
        partial_exit=replace(worked_example.partial_exit, hosting_per_user_per_month=Decimal("17")),
    )

    stay, partial, full = compute_scenarios(inputs)

    assert (stay, full) == (before[0], before[2])
    old_lines = _amounts(before[1].running)
    new_lines = _amounts(partial.running)
    assert new_lines.pop("hosting") == 2 * old_lines.pop("hosting")
    assert new_lines == old_lines
    assert partial.blocks == before[1].blocks
    assert partial.total == 543100


def test_fractional_hosting_is_exact() -> None:
    inputs = Inputs(partial_exit=ScenarioInputs(hosting_per_user_per_month=Decimal("0.1"), users=3))
    _, partial, _ = compute_scenarios(inputs)
    assert _amounts(partial.running)["hosting"] == Decimal("18")


def test_retained_and_parallel_licences_reconcile_before_division(worked_example: Inputs) -> None:
    annual = Decimal("0.01300000000000000000000000001")
    inputs = replace(
        worked_example,
        current_costs=CurrentCosts(annual, Decimal(0)),
        partial_exit=ScenarioInputs(
            retained_microsoft_licences_per_year=annual,
            parallel_running_months=1,
            users=0,
            operations_per_year=Decimal(0),
            other_recurring_per_year=Decimal(0),
            one_time_migration=Decimal(0),
            application_adaptation=Decimal(0),
            external_advice=Decimal(0),
            training_days_per_person=Decimal(0),
            productivity_loss=Decimal(0),
        ),
    )

    with localcontext(prec=3):
        stay, partial, _ = compute_scenarios(inputs)

    assert stay.total == partial.total == Decimal("0.06500000000000000000000000005")
    assert partial.difference_to_stay == 0


def test_cost_groups_sum_unrounded_lines() -> None:
    inputs = Inputs(
        partial_exit=ScenarioInputs(
            one_time_migration=Decimal("0.005"),
            application_adaptation=Decimal("0.005"),
            external_advice=Decimal(0),
            training_days_per_person=Decimal(0),
        )
    )
    direct = compute_scenarios(inputs)[1].blocks[0]

    assert direct.total == Decimal("0.01")
    assert [line.amount for line in direct.lines[:2]] == [Decimal("0.005")] * 2
    formatter = Formatter("en")
    for amount in (direct.total, *(line.amount for line in direct.lines[:2])):
        assert amount is not None and formatter.money(amount, "EUR") == "EUR 0.01"


@pytest.mark.parametrize(
    ("lang", "whole", "negative_half", "carry"),
    [
        ("en", "EUR 527,800.00", "EUR -0.01", "EUR 1,000.00"),
        ("de", "527.800,00 EUR", "-0,01 EUR", "1.000,00 EUR"),
    ],
)
def test_money_format(lang: str, whole: str, negative_half: str, carry: str) -> None:
    formatter = Formatter(lang)
    assert formatter.money(Decimal("527800"), "EUR") == whole
    assert formatter.money(Decimal("-0.005"), "EUR") == negative_half
    assert formatter.money(Decimal("999.995"), "EUR") == carry
    expected = {
        "en": ("EUR 1,235", "EUR -1", "EUR 0"),
        "de": ("1.235 EUR", "-1 EUR", "0 EUR"),
    }[lang]
    assert (
        tuple(
            formatter.money(Decimal(amount), "EUR", whole=True)
            for amount in ("1234.50", "-0.50", "-0.49")
        )
        == expected
    )


@pytest.mark.parametrize(
    ("difference", "direction", "amount"),
    [
        (Fraction(-120, 7), "less", Fraction(120, 7)),
        (Fraction(17, 13), "more", Fraction(17, 13)),
        (Fraction(0), "same", Fraction(0)),
        (Fraction(-1, 240), "sub_cent", Fraction(1, 240)),
        (Fraction(1, 200), "more", Fraction(1, 200)),
        (None, "unknown", None),
    ],
)
def test_cost_comparison_preserves_the_exact_difference(
    difference: Fraction | None, direction: str, amount: Fraction | None
) -> None:
    comparison = report_module._cost_comparison(difference)

    assert (comparison.direction, comparison.amount) == (direction, amount)
    assert comparison.amount is None or isinstance(comparison.amount, Fraction)


def test_break_even_matches_the_cost_model(worked_example: Inputs) -> None:
    _, partial, full = compute_scenarios(worked_example)

    for result, scenario, amount, entered in (
        (partial, worked_example.partial_exit, 20440, 6000),
        (full, worked_example.full_exit, 39130, 12000),
    ):
        threshold = report_module._break_even(result, scenario.operations_per_year)
        assert threshold is not None and not threshold.none
        assert threshold.amount == Fraction(amount) and isinstance(threshold.amount, Fraction)
        assert threshold.entered == Fraction(entered)

    at_break_even = replace(
        worked_example,
        full_exit=replace(worked_example.full_exit, operations_per_year=Decimal("39130")),
    )
    assert compute_scenarios(at_break_even)[2].difference_to_stay == 0


def test_break_even_can_be_below_zero(worked_example: Inputs) -> None:
    target = replace(worked_example.partial_exit, one_time_migration=Decimal("150000"))
    result = compute_scenarios(replace(worked_example, partial_exit=target))[1]
    threshold = report_module._break_even(result, target.operations_per_year)

    assert threshold is not None and threshold.none
    assert threshold.amount == -6560


def test_break_even_is_absent_without_operations_or_a_known_comparison(
    worked_example: Inputs,
) -> None:
    move = compute_scenarios(worked_example)[1]
    assert report_module._break_even(move, None) is None

    inputs = replace(
        worked_example,
        current_costs=replace(worked_example.current_costs, microsoft_licences_per_year=None),
        partial_exit=replace(worked_example.partial_exit, parallel_running_months=0),
    )
    stay, partial, _ = compute_scenarios(inputs)
    assert stay.total is None and partial.total == 507800
    assert report_module._break_even(partial, inputs.partial_exit.operations_per_year) is None


def test_no_prices_in_application_sources() -> None:
    source = ROOT / "src" / "fazit"
    currency = r"(?:[$€£¥]|\b(?:EUR|CHF|USD|GBP|CAD|AUD|JPY|CNY|SEK|NOK|DKK|PLN)\b)"
    price = re.compile(rf"{currency}\s*\d|\d\s*{currency}")
    for path in source.rglob("*"):
        if path.suffix in {".py", ".yaml", ".j2"} and path.relative_to(source).parts[0] != "demo":
            assert not price.search(path.read_text(encoding="utf-8")), path


def _cost_section(out: Path, *command: str) -> str:
    result = runner.invoke(app, [*command, "--out", str(out)])
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.splitlines()[-1])
    assert path.is_file() and path.parent == out
    return report_section(path.read_text(encoding="utf-8"), "costs")


def _rendered_totals(section: str) -> dict[str, str]:
    return dict(re.findall(r'data-scenario="([^"]+)" data-total="([^"]+)"', section))


def _visible_text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", "", html)).split())


def _cost_tile(summary: str, scenario: str) -> str:
    tile = re.search(rf'<li data-cost-tile="{scenario}">.*?</li>', summary, re.S)
    assert tile is not None, scenario
    return tile[0]


def _town_with_cost_edits(tmp_path: Path, *edits: tuple[str, str], lang: str = "en") -> str:
    text = sample_inputs_path("town").read_text(encoding="utf-8")
    for before, after in edits:
        assert before in text
        text = text.replace(before, after, 1)
    path = tmp_path / "costs.yaml"
    path.write_text(text, encoding="utf-8")
    return rebuild_report(sample_scan_path("town"), tmp_path / "out", lang, inputs=path)


@pytest.mark.parametrize("lang", ["en", "de"])
def test_town_cost_tiles_use_whole_units_and_show_the_break_even(tmp_path: Path, lang: str) -> None:
    html = rebuild_report(
        sample_scan_path("town"), tmp_path, lang, inputs=sample_inputs_path("town")
    )
    summary = report_section(html, "summary")
    formatter = Formatter(lang)
    strings = formatter.strings["costs"]
    assert re.findall(r'data-cost-tile="([^"]+)"', summary) == list(SCENARIOS)
    assert f"<h3>{strings['total']}</h3>" in summary

    def money(amount: int) -> str:
        return formatter.money(Fraction(amount), "EUR", whole=True)

    figures = re.findall(r'class="figure-num">([^<]+)</', summary)
    assert figures == [money(amount) for amount in (600000, 527800, 464350)]
    assert all(formatter.strings["format"]["decimal_separator"] not in text for text in figures)
    for scenario in SCENARIOS:
        tile = _cost_tile(summary, scenario)
        assert f'<p class="tile-label">{strings[scenario]}</p>' in tile
        origin = strings["origins"]["calculated_with_examples"]
        assert f'<p data-cost-origin="calculated_with_examples">{origin}</p>' in tile

    assert strings["stay_basis"] in _visible_text(_cost_tile(summary, "stay"))
    assert strings["stay_assumption"] in summary
    for scenario, difference, threshold, entered in (
        ("partial_exit", 72200, 20440, 6000),
        ("full_exit", 135650, 39130, 12000),
    ):
        tile = _cost_tile(summary, scenario)
        assert 'data-comparison="less"' in tile
        assert f"{money(difference)} {strings['less']}" in _visible_text(tile)
        expected = strings["break_even"].format(
            scenario=strings[scenario], amount=money(threshold), entered=money(entered)
        )
        assert f'data-break-even="{scenario}">{expected}</p>' in unescape(summary)


def test_nonprofit_full_cost_tile_is_unknown_and_shows_known_blocks(tmp_path: Path) -> None:
    html = rebuild_report(
        sample_scan_path("nonprofit"), tmp_path, "en", inputs=sample_inputs_path("nonprofit")
    )
    summary = report_section(html, "summary")
    full = _cost_tile(summary, "full_exit")

    assert re.search(r'<span class="status unknown">.*?</svg> Unknown</span>', full, re.S)
    assert "Total of known blocks EUR 40,600" in _visible_text(full)
    assert 'href="#costs-missing">1 input is missing<' in full
    assert 'data-break-even="full_exit"' not in summary
    partial = re.search(r'data-break-even="partial_exit">([^<]+)</p>', summary)
    assert partial and "EUR 26" in partial[1] and "entered: EUR 1,600" in partial[1]


def test_known_move_total_with_unknown_cost_comparison(tmp_path: Path) -> None:
    html = _town_with_cost_edits(
        tmp_path,
        ('microsoft_licences_per_year: "100000"', "microsoft_licences_per_year: null"),
        ("parallel_running_months: 6", "parallel_running_months: 0"),
    )
    summary = report_section(html, "summary")
    stay = _cost_tile(summary, "stay")
    partial = _cost_tile(summary, "partial_exit")
    full = _cost_tile(summary, "full_exit")

    assert 'class="status unknown"' in stay
    assert "Today's yearly costs for five years" in unescape(stay)
    assert "Total of known blocks" not in stay
    assert '<span class="figure-num">EUR 507,800</span>' in partial
    assert 'data-comparison="unknown"' in partial and "Comparison unknown" in partial
    assert 'href="#costs-missing">1 input is missing<' in partial
    assert 'class="status unknown"' in full and "Total of known blocks EUR 364,350" in full
    assert "data-break-even=" not in summary
    assert 'id="costs-missing"' in report_section(html, "costs")


@pytest.mark.parametrize("lang", ["en", "de"])
def test_seven_digit_cost_tile_has_one_unbroken_figure(tmp_path: Path, lang: str) -> None:
    html = _town_with_cost_edits(
        tmp_path, ('one_time_migration: "15000"', 'one_time_migration: "1115000"'), lang=lang
    )
    tile = _cost_tile(report_section(html, "summary"), "partial_exit")
    amount = Formatter(lang).money(Fraction(1627800), "EUR", whole=True)

    assert re.findall(r'class="figure-num">([^<]+)</', tile) == [amount]
    assert re.search(r"\.figure-num\s*\{[^}]*white-space:\s*nowrap", html)


def test_cost_tile_keeps_cents_for_a_small_nonzero_difference(tmp_path: Path) -> None:
    html = _town_with_cost_edits(
        tmp_path, ('operations_per_year: "12000"', 'operations_per_year: "39130.01"')
    )
    tile = _cost_tile(report_section(html, "summary"), "full_exit")

    assert '<span class="figure-num">EUR 600,000</span>' in tile
    assert 'data-comparison="more"' in tile
    assert "EUR 0.05 more than staying" in _visible_text(tile)


def _chart_rows(section: str) -> dict[str, str]:
    chart = section.split('<div class="cost-notes">', 1)[0]
    parts = re.split(r'<div class="cost-chart-row" data-chart-scenario="([^"]+)">', chart)
    return dict(zip(parts[1::2], parts[2::2], strict=True))


@pytest.mark.parametrize(
    ("sample", "shares"),
    [("town", ["1.0000", "0.8797", "0.7739"]), ("nonprofit", ["0.7365", "1.0000"])],
)
def test_cost_chart_uses_one_scale(tmp_path: Path, sample: str, shares: list[str]) -> None:
    section = _cost_section(tmp_path, "demo", "--sample", sample, "--lang", "en")
    rows = _chart_rows(section)
    results = compute_scenarios(load_inputs(sample_inputs_path(sample), load_catalogue()))
    largest = max(result.total for result in results if result.total is not None)

    assert list(rows) == list(SCENARIOS)
    assert re.findall(r"--share: ([0-9.]+)", section) == shares
    assert max(shares) == "1.0000"
    for result in results:
        row = rows[result.id]
        if result.total is None:
            assert "--share:" not in row
        else:
            share = f"{result.total / largest:.4f}"
            assert f'<div class="cost-bar" aria-hidden="true" style="--share: {share}">' in row
            assert 'data-cost-origin="calculated_with_examples"' in row
    assert re.findall(r'data-chart-block="([^"]+)"', rows["stay"]) == ["running"]


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize("sample", ["town", "nonprofit"])
def test_cost_chart_text_equals_the_table_subtotals(tmp_path: Path, lang: str, sample: str) -> None:
    section = _cost_section(tmp_path, "demo", "--sample", sample, "--lang", lang)
    rows = _chart_rows(section)
    subtotals = {}
    for key, body in re.findall(r'<tbody data-block="([^"]+)"[^>]*>(.*?)</tbody>', section, re.S):
        row = re.search(r'<tr class="subtotals"[^>]*>(.*?)</tr>', body, re.S)
        assert row is not None
        subtotals[key] = re.findall(r'data-amount="[^"]+">([^<]+)</td>', row[1])
        assert len(subtotals[key]) == len(SCENARIOS)

    formatter = Formatter(lang)
    for index, scenario in enumerate(SCENARIOS):
        values = {
            block: _visible_text(value)
            for block, value in re.findall(
                r'data-chart-value="([^"]+)">(.*?)</li>', rows[scenario], re.S
            )
        }
        shown = (
            ("productivity_loss",)
            if sample == "nonprofit" and scenario == "full_exit"
            else ("running", *BLOCKS)
        )
        assert list(values) == list(shown)
        assert values == {key: subtotals[key][index] for key in shown}

    zero = formatter.money(Fraction(0), "EUR")
    assert all(zero == subtotals[key][0] for key in BLOCKS)
    assert re.findall(r'data-chart-block="([^"]+)"', rows["stay"]) == ["running"]


def test_nonprofit_chart_shows_unknown_without_a_bar(tmp_path: Path) -> None:
    section = _cost_section(tmp_path, "demo", "--sample", "nonprofit", "--lang", "en")
    full = _chart_rows(section)["full_exit"]

    assert 'class="cost-segment is-unknown"' in full and "Total unknown" in full
    assert 'class="cost-bar"' not in full and "--share:" not in full
    assert "data-chart-block" not in full
    text = _visible_text(full)
    assert "Total of known blocks EUR 40,600.00" in text
    assert "Lost working time (internal estimate, not a payment) · Unknown" in text
    assert '<span class="status unknown">' in full
    for comparison in ("Difference from staying", "less than staying", "more than staying"):
        assert comparison not in full


def test_chart_keeps_a_known_total_when_staying_is_unknown(tmp_path: Path) -> None:
    html = _town_with_cost_edits(
        tmp_path,
        ('microsoft_licences_per_year: "100000"', "microsoft_licences_per_year: null"),
        ("parallel_running_months: 6", "parallel_running_months: 0"),
    )
    row = _chart_rows(report_section(html, "costs"))["partial_exit"]

    assert "--share: 1.0000" in row
    assert "EUR 507,800.00 · Difference from staying · Unknown" in _visible_text(row)


@pytest.mark.parametrize("with_example", [False, True])
def test_cost_chart_is_omitted_without_cost_inputs(tmp_path: Path, with_example: bool) -> None:
    options = ("--inputs", str(ROOT / "inputs.example.yaml")) if with_example else ()
    section = _cost_section(tmp_path, "report", str(sample_scan_path("town")), *options)
    note = load_locale("en")["costs"]["provide_inputs"]

    assert 'class="cost-bars"' not in section
    assert f'<p class="note">{note}</p>' in unescape(section)
    assert len(_rendered_totals(section)) == len(SCENARIOS)


def test_explicit_zero_costs_show_a_chart_without_any_fill(tmp_path: Path) -> None:
    inputs = tmp_path / "zero.yaml"
    inputs.write_text(
        "currency: EUR\ncurrent_costs:\n"
        '  microsoft_licences_per_year: "0"\n  other_it_per_year: "0"\n',
        encoding="utf-8",
    )
    section = _cost_section(
        tmp_path / "out", "report", str(sample_scan_path("town")), "--inputs", str(inputs)
    )

    assert list(_chart_rows(section)) == list(SCENARIOS)
    assert re.findall(r"--share: ([0-9.]+)", section) == ["0.0000"]
    assert "data-chart-block=" not in section


def test_cost_chart_uses_only_markers_when_no_block_is_known(tmp_path: Path) -> None:
    inputs = tmp_path / "users.yaml"
    inputs.write_text("target_costs:\n  partial_exit:\n    users: 0\n", encoding="utf-8")
    section = _cost_section(
        tmp_path / "out", "report", str(sample_scan_path("town")), "--inputs", str(inputs)
    )

    assert list(_chart_rows(section)) == list(SCENARIOS)
    assert section.count('class="cost-segment is-unknown"') == 3
    assert section.count("Total unknown") == 3
    assert "--share:" not in section and "data-chart-value=" not in section
    assert "Total of known blocks" not in section


@pytest.mark.parametrize("lang", ["en", "de"])
def test_cost_section_order_intro_and_shared_notes(tmp_path: Path, lang: str) -> None:
    sample = "nonprofit"
    entries = load_catalogue()
    inputs = load_inputs(sample_inputs_path(sample), entries)
    scan = load_scan(sample_scan_path(sample), entries)
    html = rebuild_report(
        sample_scan_path(sample), tmp_path, lang, inputs=sample_inputs_path(sample)
    )
    section = unescape(report_section(html, "costs"))
    summary = unescape(report_section(html, "summary"))
    formatter = Formatter(lang)
    strings = formatter.strings["costs"]
    markers = (
        "<h2 ",
        '<p class="sec-intro">',
        strings["profile_note"],
        '<div class="cost-bars">',
        strings["stay_assumption"],
        'data-break-even="partial_exit"',
        'id="cost-results-title"',
        'data-block="running"',
        strings["rounding"],
        strings["vat_note"],
        'id="costs-missing"',
        '<details class="cost-inputs">',
    )
    positions = [section.find(marker) for marker in markers]
    assert positions == sorted(set(positions)) and min(positions) >= 0
    intro = re.search(r'<p class="sec-intro">(.*?)</p>', section, re.S)
    assert intro is not None and inputs.as_of
    assert _visible_text(intro[1]) == " · ".join(
        (
            inputs.organisation_name,
            f"{formatter.strings['header']['scan_date']} {formatter.date(scan.generated_at)}",
            f"{formatter.strings['header']['inputs_date']} {formatter.date(inputs.as_of)}",
            strings["origins"]["invented"],
        )
    )
    assert section.count(strings["profile_note"]) == section.count(strings["vat_note"]) == 1
    notes = r'<div class="cost-notes">(.*?)</div>'
    assert re.search(notes, section, re.S)[1] == re.search(notes, summary, re.S)[1]


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize(
    ("sample", "totals"),
    [
        ("town", ("600000.00", "527800.00", "464350.00")),
        ("nonprofit", ("22000.00", "29870.00", "unknown")),
    ],
)
def test_demo_cost_comparison(
    tmp_path: Path, lang: str, sample: str, totals: tuple[str, ...]
) -> None:
    section = _cost_section(tmp_path, "demo", "--sample", sample, "--lang", lang)
    strings = load_locale(lang)["costs"]

    assert _rendered_totals(section) == dict(zip(SCENARIOS, totals, strict=True))
    assert re.findall(r'data-block="([^"]+)"', section) == ["running", *BLOCKS]
    assert section.count("<caption data-invented-amounts>") == 2
    assert strings["rounding"] in section
    assert 'data-cost-origin="invented"' in section
    assert 'data-cost-origin="sample_input"' in section
    if sample == "nonprofit":
        row = re.search(r'<tr data-cost-input="productivity_loss".*?</tr>', section, re.S)
        block = re.search(r'<tbody data-block="productivity_loss".*?</tbody>', section, re.S)
        assert row is not None and strings["not_provided"] in row[0]
        assert block is not None and 'data-amount="unknown"' in block[0]
        missing = re.findall(r'<li data-missing-cost="([^"]+)">([^<]+)</li>', section)
        assert missing == [
            (
                "target_costs.full_exit.productivity_loss",
                strings["input_fields"]["productivity_loss"],
            )
        ]
    else:
        assert 'data-amount="unknown"' not in section
        assert "data-missing-cost" not in section


@pytest.mark.parametrize("with_example", [False, True])
def test_empty_inputs_render_unknown_costs(tmp_path: Path, with_example: bool) -> None:
    scan = sample_scan_path("town")
    options = ("--inputs", str(ROOT / "inputs.example.yaml")) if with_example else ()
    section = _cost_section(tmp_path, "report", str(scan), *options)
    strings = load_locale("en")["costs"]

    assert _rendered_totals(section) == dict.fromkeys(SCENARIOS, "unknown")
    assert "data-invented-amounts" not in section
    fields = re.findall(r'<tr data-cost-input="([^"]+)"[^>]*>(.*?)</tr>', section, re.S)
    assert set(dict(fields)) == strings["input_fields"].keys()
    for field, row in fields:
        count = 3 if field in ("microsoft_licences_per_year", "other_it_per_year") else 2
        assert row.count(strings["not_provided"]) == count
        assert "data-cost-origin=" not in row
    if not with_example:
        assert strings["provide_inputs"] in unescape(section)


def test_sample_measurements_do_not_label_real_prices_invented(tmp_path: Path) -> None:
    answers = tmp_path / "costs.yaml"
    data = sample_inputs_path("town").read_text(encoding="utf-8")
    answers.write_text(
        data.replace("amounts_are_invented: true", "amounts_are_invented: false").replace(
            'retained_microsoft_licences_per_year: "60000"',
            'retained_microsoft_licences_per_year: "60000.01"',
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"

    section = _cost_section(out, "report", str(sample_scan_path("town")), "--inputs", str(answers))

    assert _rendered_totals(section) == {
        "stay": "600000.00",
        "partial_exit": "527800.05",
        "full_exit": "464350.00",
    }
    assert re.search(r'data-amount="270000\.05">\s*EUR 270,000\.05', section)
    assert "data-invented-amounts" not in section and 'data-cost-origin="invented"' not in section
    assert 'data-cost-origin="provided"' in section
    assert 'data-cost-origin="sample_input"' in section
    assert 'data-cost-origin="calculated"' in section
    (path,) = out.glob("*.html")
    html = path.read_text(encoding="utf-8")
    assert "<caption data-sample>" in html
    assert load_locale("en")["header"]["sample"] in html


@pytest.mark.parametrize("lang", ["en", "de"])
def test_report_rejects_padded_headcounts(tmp_path: Path, lang: str) -> None:
    inputs = tmp_path / "inputs.yaml"
    original = sample_inputs_path("town").read_text(encoding="utf-8")
    inputs.write_text(original.replace("users: 30", "users: 030", 1), encoding="utf-8")
    out = tmp_path / "rejected"
    result = runner.invoke(
        app,
        [
            "report",
            str(sample_scan_path("town")),
            "--inputs",
            str(inputs),
            "--lang",
            lang,
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 2 and not result.stdout and not out.exists(), result.output
    assert len(result.stderr.splitlines()) == 1
    assert "inputs.yaml" in result.stderr and "target_costs.partial_exit.users" in result.stderr
    line = next(i for i, text in enumerate(original.splitlines(), 1) if "users: 30" in text)
    location = f"line {line}" if lang == "en" else f"Zeile {line}"
    guidance = (
        "whole number without leading zeros" if lang == "en" else "ganze Zahl ohne führende Nullen"
    )
    assert location in result.stderr and guidance in result.stderr
