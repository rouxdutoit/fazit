# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Never

from .catalogue import Catalogue, FindingEntry
from .errors import InputError
from .i18n import SUPPORTED_LANGUAGES
from .model import Coverage, Finding, Scan
from .parsing import parse_yaml, read_text, reject_at_signs
from .rules import PROFILES, provided_answers_conflict, select_evidence

_INPUT_KEYS = (
    "organisation_name",
    "currency",
    "language",
    "target_profile",
    "as_of",
    "answers_are_sample",
    "amounts_are_invented",
    "current_costs",
    "target_costs",
    "windows_only_software",
    "provided_counts",
    "confirmations",
)
_CURRENT_AMOUNTS = ("microsoft_licences_per_year", "other_it_per_year")
_SCENARIO_AMOUNTS = (
    "retained_microsoft_licences_per_year",
    "hosting_per_user_per_month",
    "operations_per_year",
    "other_recurring_per_year",
    "one_time_migration",
    "application_adaptation",
    "external_advice",
    "training_day_rate",
    "productivity_loss",
)
_SCENARIOS = ("partial_exit", "full_exit")
_SCENARIO_KEYS = (
    *_SCENARIO_AMOUNTS,
    "users",
    "training_days_per_person",
    "training_staff",
    "parallel_running_months",
)
_SOFTWARE_KEYS = ("name", "users", "vendor_has_web_version")
_QUOTED_FIELDS = tuple(f"current_costs.{name}" for name in _CURRENT_AMOUNTS) + tuple(
    f"target_costs.{scenario}.{name}"
    for scenario in _SCENARIOS
    for name in (*_SCENARIO_AMOUNTS, "training_days_per_person")
)
_DECIMAL = re.compile(r"0|[1-9][0-9]*|[0-9]+\.[0-9]+")
_AMOUNT = re.compile(r"[0-9]{1,15}(?:\.[0-9]{1,2})?")


@dataclass(frozen=True)
class CurrentCosts:
    microsoft_licences_per_year: Decimal | None = None
    other_it_per_year: Decimal | None = None


@dataclass(frozen=True)
class ScenarioInputs:
    users: int | None = None
    retained_microsoft_licences_per_year: Decimal | None = None
    hosting_per_user_per_month: Decimal | None = None
    operations_per_year: Decimal | None = None
    other_recurring_per_year: Decimal | None = None
    one_time_migration: Decimal | None = None
    application_adaptation: Decimal | None = None
    external_advice: Decimal | None = None
    training_days_per_person: Decimal | None = None
    training_day_rate: Decimal | None = None
    training_staff: int | None = None
    productivity_loss: Decimal | None = None
    parallel_running_months: int | None = None


@dataclass(frozen=True)
class WindowsSoftware:
    name: str
    users: int | None = None
    vendor_has_web_version: bool | None = None


@dataclass(frozen=True)
class Inputs:
    organisation_name: str | None = None
    currency: str | None = None
    language: str | None = None
    target_profile: str | None = None
    as_of: str | None = None
    amounts_are_invented: bool = False
    current_costs: CurrentCosts = CurrentCosts()
    partial_exit: ScenarioInputs = ScenarioInputs()
    full_exit: ScenarioInputs = ScenarioInputs()
    windows_only_software: tuple[WindowsSoftware, ...] | None = None
    provided_counts: Mapping[str, int | None] = field(default_factory=lambda: MappingProxyType({}))
    confirmations: Mapping[str, bool | None] = field(default_factory=lambda: MappingProxyType({}))
    answers_are_sample: bool = False

    @property
    def answer_source(self) -> str:
        return "sample.inputs_yaml" if self.answers_are_sample else "inputs_yaml"


@dataclass(frozen=True)
class _InputsReader:
    file_name: str

    def fail(self, field: str, code: str = "invalid_field") -> Never:
        raise InputError(code, file=self.file_name, field=field or "$")

    def fields(self, value: object, field: str, allowed: Collection[str]) -> dict[str, object]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            self.fail(field)
        for index, key in enumerate(value):
            if key not in allowed:
                self.fail(f"{field or '$'}[{index}]", "unknown_field")
        return value

    def name(self, value: object, field: str, limit: int) -> str | None:
        if value is None:
            return None
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > limit
            or not value.isprintable()
        ):
            self.fail(field)
        return value

    def choice(self, value: object, field: str, allowed: tuple[str, ...], code: str) -> str | None:
        if value is not None and (not isinstance(value, str) or value not in allowed):
            self.fail(field, code)
        return value

    def currency(self, value: object) -> str | None:
        if value is not None and (
            not isinstance(value, str) or not re.fullmatch(r"[A-Z]{3}", value)
        ):
            self.fail("currency")
        return value

    def as_of(self, value: object) -> str | None:
        if value is None:
            return None
        if type(value) is date:
            return value.isoformat()
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            self.fail("as_of")
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            self.fail("as_of")

    def count(self, value: object, field: str) -> int | None:
        if value is not None and (type(value) is not int or value < 0):
            self.fail(field)
        return value

    def boolean(self, value: object, field: str) -> bool | None:
        if value is not None and type(value) is not bool:
            self.fail(field)
        return value

    def decimal(
        self, value: object, field: str, *, pattern: re.Pattern[str] = _DECIMAL
    ) -> Decimal | None:
        if value is None:
            return None
        if not isinstance(value, str):
            self.fail(field, "money_not_quoted")
        if not pattern.fullmatch(value):
            self.fail(field)
        return Decimal(value)

    def amounts(
        self, row: dict[str, object], field: str, keys: tuple[str, ...], currency: str | None
    ) -> dict[str, Decimal | None]:
        amounts = {
            key: self.decimal(row.get(key), f"{field}.{key}", pattern=_AMOUNT) for key in keys
        }
        if currency is None and any(value is not None for value in amounts.values()):
            self.fail("currency", "missing_field")
        return amounts

    def scenario(self, value: object, field: str, currency: str | None) -> ScenarioInputs:
        row = self.fields(value, field, _SCENARIO_KEYS)
        amounts = self.amounts(row, field, _SCENARIO_AMOUNTS, currency)
        months = self.count(row.get("parallel_running_months"), f"{field}.parallel_running_months")
        if months is not None and months > 60:
            self.fail(f"{field}.parallel_running_months")
        days = row.get("training_days_per_person")
        days_field = f"{field}.training_days_per_person"
        return ScenarioInputs(
            **amounts,
            users=self.count(row.get("users"), f"{field}.users"),
            training_days_per_person=(
                Decimal(days) if type(days) is int and days >= 0 else self.decimal(days, days_field)
            ),
            training_staff=self.count(row.get("training_staff"), f"{field}.training_staff"),
            parallel_running_months=months,
        )

    def software_entry(self, value: object, field: str) -> WindowsSoftware:
        row = self.fields(value, field, _SOFTWARE_KEYS)
        name = self.name(row.get("name"), f"{field}.name", 80)
        if name is None:
            self.fail(f"{field}.name", "missing_field")
        return WindowsSoftware(
            name,
            self.count(row.get("users"), f"{field}.users"),
            self.boolean(row.get("vendor_has_web_version"), f"{field}.vendor_has_web_version"),
        )

    def software_list(self, value: object) -> tuple[WindowsSoftware, ...] | None:
        if value is None:
            return None
        if not isinstance(value, list):
            self.fail("windows_only_software")
        return tuple(
            self.software_entry(item, f"windows_only_software[{i}]") for i, item in enumerate(value)
        )


def load_inputs_text(text: str, file_name: str, catalogue: Catalogue) -> Inputs:
    answers = {entry.id: entry.type for entry in catalogue.findings if entry.provided == "answer"}
    input_keys = {
        *_INPUT_KEYS,
        *_CURRENT_AMOUNTS,
        *_SCENARIOS,
        *_SCENARIO_KEYS,
        *_SOFTWARE_KEYS,
        *answers,
    }
    data = parse_yaml(
        text, file_name, quoted_fields=_QUOTED_FIELDS, allow_aliases=False, input_keys=input_keys
    )
    reject_at_signs(data, file_name)
    reader = _InputsReader(file_name)
    row = reader.fields(data, "", _INPUT_KEYS)
    currency = reader.currency(row.get("currency"))
    current = reader.fields(row.get("current_costs"), "current_costs", _CURRENT_AMOUNTS)
    targets = reader.fields(row.get("target_costs"), "target_costs", _SCENARIOS)
    counts = reader.fields(
        row.get("provided_counts"),
        "provided_counts",
        {key for key, kind in answers.items() if kind == "count"},
    )
    confirmations = reader.fields(
        row.get("confirmations"),
        "confirmations",
        {key for key, kind in answers.items() if kind == "boolean"},
    )
    return Inputs(
        organisation_name=reader.name(row.get("organisation_name"), "organisation_name", 120),
        currency=currency,
        language=reader.choice(
            row.get("language"), "language", SUPPORTED_LANGUAGES, "unsupported_language"
        ),
        target_profile=reader.choice(
            row.get("target_profile"), "target_profile", PROFILES, "unsupported_profile"
        ),
        as_of=reader.as_of(row.get("as_of")),
        answers_are_sample=reader.boolean(row.get("answers_are_sample"), "answers_are_sample")
        is True,
        amounts_are_invented=reader.boolean(row.get("amounts_are_invented"), "amounts_are_invented")
        is True,
        current_costs=CurrentCosts(
            **reader.amounts(current, "current_costs", _CURRENT_AMOUNTS, currency)
        ),
        partial_exit=reader.scenario(
            targets.get("partial_exit"), "target_costs.partial_exit", currency
        ),
        full_exit=reader.scenario(targets.get("full_exit"), "target_costs.full_exit", currency),
        windows_only_software=reader.software_list(row.get("windows_only_software")),
        provided_counts=MappingProxyType(
            {key: reader.count(value, f"provided_counts.{key}") for key, value in counts.items()}
        ),
        confirmations=MappingProxyType(
            {
                key: reader.boolean(value, f"confirmations.{key}")
                for key, value in confirmations.items()
            }
        ),
    )


def load_inputs(path: Path, catalogue: Catalogue) -> Inputs:
    return load_inputs_text(read_text(path), path.name, catalogue)


def _provided(
    entry: FindingEntry,
    value: int | bool | None,
    inputs: Inputs,
    coverage: Coverage | None = None,
) -> Finding:
    return Finding(
        id=entry.id,
        workload=entry.workload,
        unit=entry.unit,
        value=value,
        provenance="unknown" if value is None else "provided",
        collector=None,
        source=inputs.answer_source,
        collected_at=inputs.as_of,
        period=None,
        coverage=coverage,
        missing_reason="answer_not_provided" if value is None else None,
    )


def _without_web_version(
    software: tuple[WindowsSoftware, ...],
) -> tuple[int | None, Coverage | None]:
    confirmed = sum(item.vendor_has_web_version is False for item in software)
    answered = sum(item.vendor_has_web_version is not None for item in software)
    if answered == len(software):
        return confirmed, None
    return confirmed or None, Coverage("partial", scanned=answered, total=len(software))


def provided_findings(inputs: Inputs, catalogue: Catalogue) -> tuple[Finding, ...]:
    answers = {**inputs.provided_counts, **inputs.confirmations}
    software = inputs.windows_only_software
    findings: list[Finding] = []
    for entry in catalogue.findings:
        if entry.provided == "answer" and (value := answers.get(entry.id)) is not None:
            findings.append(_provided(entry, value, inputs))
        elif software is not None and entry.provided == "software_list":
            findings.append(_provided(entry, len(software), inputs))
        elif software is not None and entry.provided == "software_list_without_web_version":
            lower_bound, coverage = _without_web_version(software)
            findings.append(_provided(entry, lower_bound, inputs, coverage))
    return tuple(findings)


def combine(scan: Scan, provided: tuple[Finding, ...]) -> tuple[Scan, tuple[Finding, ...]]:
    if not provided:
        return scan, ()
    by_id = {finding.id: finding for finding in scan.findings}
    skipped = {collector.id for collector in scan.collectors if collector.status == "skipped"}
    alternatives: list[Finding] = []
    for supplied in {finding.id: finding for finding in provided}.values():
        recorded = by_id.get(supplied.id)
        selected = select_evidence(recorded, supplied)
        by_id[supplied.id] = selected
        if recorded and (
            (recorded.provenance == "measured" and supplied.provenance == "provided")
            or provided_answers_conflict(recorded, supplied)
            or (selected is supplied and recorded.collector in skipped)
        ):
            alternatives.append(recorded if selected is supplied else supplied)
    return replace(scan, findings=tuple(by_id.values())), tuple(alternatives)
