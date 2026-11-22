# SPDX-License-Identifier: AGPL-3.0-or-later
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from math import prod

from .inputs import Inputs, ScenarioInputs

YEARS = 5
MONTHS_PER_YEAR = 12
MONTHS = YEARS * MONTHS_PER_YEAR
_MONTHLY = Fraction(1, MONTHS_PER_YEAR)
SCENARIOS = ("stay", "partial_exit", "full_exit")
BLOCKS = ("direct_project", "productivity_loss", "parallel_running")

type _Factor = tuple[str, Decimal | int | None]


@dataclass(frozen=True)
class CostLine:
    id: str
    amount: Fraction | None
    missing: tuple[str, ...]
    input_exponent: int = 0


@dataclass(frozen=True)
class CostGroup:
    id: str
    lines: tuple[CostLine, ...]
    total: Fraction | None
    missing: tuple[str, ...]
    input_exponent: int


@dataclass(frozen=True)
class ScenarioResult:
    id: str
    running: CostGroup
    blocks: tuple[CostGroup, ...]
    total: Fraction | None
    missing_inputs: tuple[str, ...]
    difference_to_stay: Fraction | None
    input_exponent: int


def _line(id: str, *factors: _Factor, multiplier: int | Fraction = 1) -> CostLine:
    if any(value == 0 for _, value in factors):
        return CostLine(id, Fraction(0), ())
    missing = tuple(path for path, value in factors if value is None)
    if missing:
        return CostLine(id, None, missing)
    values = [value for _, value in factors if value is not None]
    amount = prod((Fraction(value) for value in values), start=Fraction(multiplier))
    exponent = sum(value.as_tuple().exponent for value in values if isinstance(value, Decimal))
    return CostLine(id, amount, (), exponent)


def _sum(amounts: Iterable[Fraction | None]) -> Fraction | None:
    total = Fraction(0)
    for amount in amounts:
        if amount is None:
            return None
        total += amount
    return total


def _group(id: str, *lines: CostLine) -> CostGroup:
    total = _sum(line.amount for line in lines)
    missing = tuple(dict.fromkeys(path for line in lines for path in line.missing))
    exponent = min((0, *(line.input_exponent for line in lines)))
    return CostGroup(id, lines, total, missing, exponent)


def _exit_running(target: ScenarioInputs, prefix: str, other_it: CostLine) -> CostGroup:
    months = target.parallel_running_months
    months_left = MONTHS - months if months is not None else None
    return _group(
        "running",
        _line(
            "retained_licences",
            (
                f"{prefix}.retained_microsoft_licences_per_year",
                target.retained_microsoft_licences_per_year,
            ),
            (f"{prefix}.parallel_running_months", months_left),
            multiplier=_MONTHLY,
        ),
        _line(
            "hosting",
            (f"{prefix}.hosting_per_user_per_month", target.hosting_per_user_per_month),
            (f"{prefix}.users", target.users),
            multiplier=MONTHS,
        ),
        _line(
            "operations",
            (f"{prefix}.operations_per_year", target.operations_per_year),
            multiplier=YEARS,
        ),
        _line(
            "other_recurring",
            (f"{prefix}.other_recurring_per_year", target.other_recurring_per_year),
            multiplier=YEARS,
        ),
        other_it,
    )


def _exit_blocks(
    target: ScenarioInputs, prefix: str, current_licences: _Factor
) -> tuple[CostGroup, ...]:
    return (
        _group(
            "direct_project",
            _line(
                "one_time_migration", (f"{prefix}.one_time_migration", target.one_time_migration)
            ),
            _line(
                "application_adaptation",
                (f"{prefix}.application_adaptation", target.application_adaptation),
            ),
            _line("external_advice", (f"{prefix}.external_advice", target.external_advice)),
            _line(
                "training",
                (f"{prefix}.training_days_per_person", target.training_days_per_person),
                (f"{prefix}.training_day_rate", target.training_day_rate),
                (f"{prefix}.training_staff", target.training_staff),
            ),
        ),
        _group(
            "productivity_loss",
            _line("productivity_loss", (f"{prefix}.productivity_loss", target.productivity_loss)),
        ),
        _group(
            "parallel_running",
            _line(
                "parallel_running",
                current_licences,
                (f"{prefix}.parallel_running_months", target.parallel_running_months),
                multiplier=_MONTHLY,
            ),
        ),
    )


def _result(
    id: str, running: CostGroup, blocks: tuple[CostGroup, ...], stay_total: Fraction | None
) -> ScenarioResult:
    groups = (running, *blocks)
    total = _sum(group.total for group in groups)
    missing = tuple(dict.fromkeys(path for group in groups for path in group.missing))
    difference = total - stay_total if total is not None and stay_total is not None else None
    exponent = min(group.input_exponent for group in groups)
    return ScenarioResult(id, running, blocks, total, missing, difference, exponent)


def compute_scenarios(inputs: Inputs) -> tuple[ScenarioResult, ...]:
    current_licences = (
        "current_costs.microsoft_licences_per_year",
        inputs.current_costs.microsoft_licences_per_year,
    )
    other_it = _line(
        "other_it",
        ("current_costs.other_it_per_year", inputs.current_costs.other_it_per_year),
        multiplier=YEARS,
    )
    running = _group(
        "running", _line("microsoft_licences", current_licences, multiplier=YEARS), other_it
    )
    results = [_result("stay", running, tuple(_group(id) for id in BLOCKS), running.total)]
    for id, target in zip(SCENARIOS[1:], (inputs.partial_exit, inputs.full_exit), strict=True):
        prefix = f"target_costs.{id}"
        results.append(
            _result(
                id,
                _exit_running(target, prefix, other_it),
                _exit_blocks(target, prefix, current_licences),
                running.total,
            )
        )
    return tuple(results)
