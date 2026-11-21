# SPDX-License-Identifier: AGPL-3.0-or-later
from collections.abc import Iterable
from dataclasses import dataclass, replace
from decimal import MAX_EMAX, MIN_EMIN, Context, Decimal, localcontext

from .inputs import Inputs, ScenarioInputs

YEARS = 5
MONTHS_PER_YEAR = 12
MONTHS = YEARS * MONTHS_PER_YEAR
SCENARIOS = ("stay", "partial_exit", "full_exit")
BLOCKS = ("direct_project", "productivity_loss", "parallel_running")

type _Factor = tuple[str, Decimal | int | None]


@dataclass(frozen=True)
class CostLine:
    id: str
    amount: Decimal | None
    missing: tuple[str, ...]


@dataclass(frozen=True)
class CostGroup:
    id: str
    lines: tuple[CostLine, ...]
    total: Decimal | None
    missing: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioResult:
    id: str
    running: CostGroup
    blocks: tuple[CostGroup, ...]
    total: Decimal | None
    missing_inputs: tuple[str, ...]
    difference_to_stay: Decimal | None


def _line(id: str, *factors: _Factor, multiplier: int = MONTHS_PER_YEAR) -> CostLine:
    if any(value == 0 for _, value in factors):
        return CostLine(id, Decimal(0), ())
    missing = tuple(path for path, value in factors if value is None)
    if missing:
        return CostLine(id, None, missing)
    amount = Decimal(multiplier)
    for _, value in factors:
        assert value is not None
        amount *= value
    return CostLine(id, amount, ())


def _sum(amounts: Iterable[Decimal | None]) -> Decimal | None:
    total = Decimal(0)
    for amount in amounts:
        if amount is None:
            return None
        total += amount
    return total


def _group(id: str, *lines: CostLine) -> CostGroup:
    total = _sum(line.amount for line in lines)
    missing = tuple(dict.fromkeys(path for line in lines for path in line.missing))
    return CostGroup(id, lines, total, missing)


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
            multiplier=1,
        ),
        _line(
            "hosting",
            (f"{prefix}.hosting_per_user_per_month", target.hosting_per_user_per_month),
            (f"{prefix}.users", target.users),
            multiplier=MONTHS * MONTHS_PER_YEAR,
        ),
        _line(
            "operations",
            (f"{prefix}.operations_per_year", target.operations_per_year),
            multiplier=YEARS * MONTHS_PER_YEAR,
        ),
        _line(
            "other_recurring",
            (f"{prefix}.other_recurring_per_year", target.other_recurring_per_year),
            multiplier=YEARS * MONTHS_PER_YEAR,
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
                multiplier=1,
            ),
        ),
    )


def _from_twelfths(amount: Decimal | None) -> Decimal | None:
    if amount is None:
        return None
    # Division by 12 may repeat, so divide each reconciled result only once.
    with localcontext(prec=max(28, len(amount.as_tuple().digits) + 4)):
        return amount / MONTHS_PER_YEAR


def _currency_group(group: CostGroup) -> CostGroup:
    return replace(
        group,
        lines=tuple(replace(line, amount=_from_twelfths(line.amount)) for line in group.lines),
        total=_from_twelfths(group.total),
    )


def _result(
    id: str, running: CostGroup, blocks: tuple[CostGroup, ...], stay_total: Decimal | None
) -> ScenarioResult:
    groups = (running, *blocks)
    total = _sum(group.total for group in groups)
    missing = tuple(dict.fromkeys(path for group in groups for path in group.missing))
    difference = total - stay_total if total is not None and stay_total is not None else None
    return ScenarioResult(
        id,
        _currency_group(running),
        tuple(_currency_group(group) for group in blocks),
        _from_twelfths(total),
        missing,
        _from_twelfths(difference),
    )


def _precision(inputs: Inputs) -> int:
    values = tuple(
        Decimal(value)
        for costs in (inputs.current_costs, inputs.partial_exit, inputs.full_exit)
        for value in vars(costs).values()
        if value
    )
    whole = max((max(0, value.adjusted() + 1) for value in values), default=0)
    fraction = max((max(0, -value.as_tuple().exponent) for value in values), default=0)
    # Training has three factors, and the line multipliers and sums need extra digits.
    return max(28, 3 * (whole + fraction) + 6)


def compute_scenarios(inputs: Inputs) -> tuple[ScenarioResult, ...]:
    current_licences = (
        "current_costs.microsoft_licences_per_year",
        inputs.current_costs.microsoft_licences_per_year,
    )
    # Sum in twelfths of the currency unit so that monthly proration cancels exactly.
    with localcontext(Context(prec=_precision(inputs), Emin=MIN_EMIN, Emax=MAX_EMAX)):
        other_it = _line(
            "other_it",
            ("current_costs.other_it_per_year", inputs.current_costs.other_it_per_year),
            multiplier=YEARS * MONTHS_PER_YEAR,
        )
        running = _group(
            "running",
            _line("microsoft_licences", current_licences, multiplier=YEARS * MONTHS_PER_YEAR),
            other_it,
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
