# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import replace
from decimal import Decimal, localcontext
from html import unescape
from importlib.resources import files
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fazit.cli import app
from fazit.costs import BLOCKS, SCENARIOS, CostGroup, ScenarioResult, compute_scenarios
from fazit.i18n import Formatter, load_locale
from fazit.inputs import CurrentCosts, Inputs, ScenarioInputs

ROOT = Path(__file__).resolve().parents[1]


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


def _amounts(group: CostGroup) -> dict[str, Decimal | None]:
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


def test_no_prices_in_application_sources() -> None:
    source = ROOT / "src" / "fazit"
    currency = r"(?:[$€£¥]|\b(?:EUR|CHF|USD|GBP|CAD|AUD|JPY|CNY|SEK|NOK|DKK|PLN)\b)"
    price = re.compile(rf"{currency}\s*\d|\d\s*{currency}")
    for path in source.rglob("*"):
        if path.suffix in {".py", ".yaml", ".j2"} and path.relative_to(source).parts[0] != "demo":
            assert not price.search(path.read_text(encoding="utf-8")), path


def _cost_section(out: Path, *command: str) -> str:
    result = CliRunner().invoke(app, [*command, "--out", str(out)])
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.splitlines()[-1])
    assert path.is_file() and path.parent == out
    html = path.read_text(encoding="utf-8")
    section = re.search(r'<section data-section="costs">.*?</section>', html, re.S)
    assert section is not None
    return section[0]


def _rendered_totals(section: str) -> dict[str, str]:
    return dict(re.findall(r'data-scenario="([^"]+)" data-total="([^"]+)"', section))


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize(
    ("sample", "totals"),
    [("town", ("600000", "527800", "464350")), ("nonprofit", ("22000", "29870", "unknown"))],
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
    scan = files("fazit").joinpath("demo", "town", "scan.json")
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
    source = files("fazit").joinpath("demo", "town")
    answers = tmp_path / "costs.yaml"
    data = source.joinpath("inputs.yaml").read_text(encoding="utf-8")
    answers.write_text(
        data.replace("amounts_are_invented: true", "amounts_are_invented: false"), encoding="utf-8"
    )
    out = tmp_path / "out"

    section = _cost_section(
        out, "report", str(source.joinpath("scan.json")), "--inputs", str(answers)
    )

    assert _rendered_totals(section) == {
        "stay": "600000",
        "partial_exit": "527800",
        "full_exit": "464350",
    }
    assert "data-invented-amounts" not in section and 'data-cost-origin="invented"' not in section
    assert 'data-cost-origin="provided"' in section
    assert 'data-cost-origin="sample_input"' in section
    assert 'data-cost-origin="calculated"' in section
    (path,) = out.glob("*.html")
    html = path.read_text(encoding="utf-8")
    assert "<caption data-sample>" in html
    assert load_locale("en")["header"]["sample"] in html


@pytest.mark.parametrize("lang", ["en", "de"])
def test_padded_headcount_is_rejected_instead_of_changing_the_total(
    tmp_path: Path, lang: str
) -> None:
    source = files("fazit").joinpath("demo", "town")
    inputs = tmp_path / "inputs.yaml"
    original = source.joinpath("inputs.yaml").read_text(encoding="utf-8")
    inputs.write_text(original, encoding="utf-8")
    command = ("report", str(source.joinpath("scan.json")), "--inputs", str(inputs), "--lang", lang)
    section = _cost_section(tmp_path / "valid", *command)
    assert _rendered_totals(section)["partial_exit"] == "527800"

    inputs.write_text(original.replace("users: 30", "users: 030", 1), encoding="utf-8")
    out = tmp_path / "rejected"
    result = CliRunner().invoke(app, [*command, "--out", str(out)])

    assert result.exit_code == 2 and not result.stdout and not out.exists(), result.output
    assert len(result.stderr.splitlines()) == 1
    assert "inputs.yaml" in result.stderr and "target_costs.partial_exit.users" in result.stderr
    line = next(i for i, text in enumerate(original.splitlines(), 1) if "users: 30" in text)
    location = f"line {line}" if lang == "en" else f"Zeile {line}"
    guidance = (
        "whole number without leading zeros" if lang == "en" else "ganze Zahl ohne führende Nullen"
    )
    assert location in result.stderr and guidance in result.stderr
