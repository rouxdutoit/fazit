# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType

from .catalogue import Catalogue
from .i18n import check_language
from .mappings import PROFILES
from .parsing import FieldNames, parse_yaml, read_text
from .validation import MAX_COUNT, Validator, non_negative_integer

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
_SCENARIO_COUNTS = ("users", "training_staff", "parallel_running_months")
_SCENARIO_KEYS = (*_SCENARIO_AMOUNTS, *_SCENARIO_COUNTS, "training_days_per_person")
_SOFTWARE_KEYS = ("name", "users", "vendor_has_web_version")
# Bounded before Decimal(): pure-Python decimal fails on very long digit strings.
_DECIMAL = re.compile(r"0|[1-9][0-9]{0,11}|[0-9]{1,12}\.[0-9]{1,6}")
_AMOUNT = re.compile(r"[0-9]{1,15}(?:\.[0-9]{1,2})?")
_CURRENCY = re.compile(r"[A-Z]{3}")


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
    validator: Validator

    def fields(self, value: object, field: str) -> dict[str, object]:
        return {} if value is None else self.validator.fields(value, field, (), optional=None)

    def name(self, value: object, field: str, limit: int) -> str | None:
        if value is None:
            return None
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > limit
            or not value.isprintable()
        ):
            self.validator.fail(field)
        return value

    def boolean(self, value: object, field: str) -> bool | None:
        if value is not None and type(value) is not bool:
            self.validator.fail(field)
        return value

    def decimal(
        self, value: object, field: str, *, pattern: re.Pattern[str] = _DECIMAL
    ) -> Decimal | None:
        if value is None:
            return None
        if not isinstance(value, str):
            self.validator.fail(field, "money_not_quoted")
        return Decimal(self.validator.matches(value, field, pattern))

    def amounts(
        self, row: dict[str, object], field: str, keys: tuple[str, ...], currency: str | None
    ) -> dict[str, Decimal | None]:
        amounts = {
            key: self.decimal(row.get(key), f"{field}.{key}", pattern=_AMOUNT) for key in keys
        }
        if currency is None and any(value is not None for value in amounts.values()):
            self.validator.fail("currency", "missing_field")
        return amounts

    def scenario(self, value: object, field: str, currency: str | None) -> ScenarioInputs:
        row = self.fields(value, field)
        amounts = self.amounts(row, field, _SCENARIO_AMOUNTS, currency)
        months = self.validator.optional_count(
            row.get("parallel_running_months"), f"{field}.parallel_running_months"
        )
        if months is not None and months > 60:
            self.validator.fail(f"{field}.parallel_running_months")
        days = row.get("training_days_per_person")
        days_field = f"{field}.training_days_per_person"
        training_days = (
            Decimal(days) if non_negative_integer(days) else self.decimal(days, days_field)
        )
        if training_days is not None and training_days > MAX_COUNT:
            self.validator.fail(days_field)
        return ScenarioInputs(
            **amounts,
            users=self.validator.optional_count(row.get("users"), f"{field}.users"),
            training_days_per_person=training_days,
            training_staff=self.validator.optional_count(
                row.get("training_staff"), f"{field}.training_staff"
            ),
            parallel_running_months=months,
        )

    def software_entry(self, value: object, field: str) -> WindowsSoftware:
        row = self.fields(value, field)
        name = self.name(row.get("name"), f"{field}.name", 80)
        if name is None:
            self.validator.fail(f"{field}.name", "missing_field")
        return WindowsSoftware(
            name,
            self.validator.optional_count(row.get("users"), f"{field}.users"),
            self.boolean(row.get("vendor_has_web_version"), f"{field}.vendor_has_web_version"),
        )

    def software_list(self, value: object) -> tuple[WindowsSoftware, ...] | None:
        if value is None:
            return None
        rows = self.validator.rows(value, "windows_only_software", allow_empty=True)
        return tuple(
            self.software_entry(item, f"windows_only_software[{i}]") for i, item in enumerate(rows)
        )

    def provided_counts(
        self, value: object, subset_parents: Mapping[str, frozenset[str]]
    ) -> Mapping[str, int | None]:
        counts = {
            key: self.validator.optional_count(raw_count, f"provided_counts.{key}")
            for key, raw_count in self.fields(value, "provided_counts").items()
        }
        for finding_id, parents in subset_parents.items():
            count = counts.get(finding_id)
            population = [part for parent in parents if (part := counts.get(parent)) is not None]
            if count is not None and len(population) == len(parents) and count > sum(population):
                self.validator.fail(
                    f"provided_counts.{finding_id}", "subset_count_exceeds_population"
                )
        return MappingProxyType(counts)


def load_inputs_text(text: str, file_name: str, catalogue: Catalogue) -> Inputs:
    count_ids = {
        entry.id
        for entry in catalogue.findings
        if entry.provided == "answer" and entry.type == "count"
    }
    subset_parents = {
        entry.id: entry.subset_of
        for entry in catalogue.findings
        if entry.id in count_ids and entry.subset_of and entry.subset_of <= count_ids
    }
    boolean_ids = {
        entry.id
        for entry in catalogue.findings
        if entry.provided == "answer" and entry.type == "boolean"
    }
    fields: FieldNames = {
        (): _INPUT_KEYS,
        ("current_costs",): _CURRENT_AMOUNTS,
        ("target_costs",): _SCENARIOS,
        **{("target_costs", scenario): _SCENARIO_KEYS for scenario in _SCENARIOS},
        ("windows_only_software", None): _SOFTWARE_KEYS,
        ("provided_counts",): count_ids,
        ("confirmations",): boolean_ids,
    }
    data = parse_yaml(
        text,
        file_name,
        allow_aliases=False,
        fields=fields,
        strict_scalars=True,
        scalar_fields={
            **{("current_costs", key): "quoted" for key in _CURRENT_AMOUNTS},
            **{
                ("target_costs", scenario, key): "quoted"
                for scenario in _SCENARIOS
                for key in (*_SCENARIO_AMOUNTS, "training_days_per_person")
            },
            **{
                ("target_costs", scenario, key): "integer"
                for scenario in _SCENARIOS
                for key in _SCENARIO_COUNTS
            },
            ("windows_only_software", None, "users"): "integer",
            **{("provided_counts", key): "integer" for key in count_ids},
            ("as_of",): "date",
        },
    )
    return _read_inputs(data, Validator(file_name), subset_parents)


def _read_inputs(
    data: object, validator: Validator, subset_parents: Mapping[str, frozenset[str]]
) -> Inputs:
    reader = _InputsReader(validator)
    row = reader.fields(data, "")
    currency = row.get("currency")
    if currency is not None:
        currency = validator.matches(currency, "currency", _CURRENCY)
    current = reader.fields(row.get("current_costs"), "current_costs")
    targets = reader.fields(row.get("target_costs"), "target_costs")
    confirmations = reader.fields(row.get("confirmations"), "confirmations")
    language, profile, as_of = (row.get(name) for name in ("language", "target_profile", "as_of"))
    return Inputs(
        organisation_name=reader.name(row.get("organisation_name"), "organisation_name", 120),
        currency=currency,
        language=None
        if language is None
        else check_language(language, file=validator.file_name, field="language"),
        target_profile=None
        if profile is None
        else validator.choice(profile, "target_profile", PROFILES, "unsupported_profile"),
        as_of=None if as_of is None else validator.calendar_date(as_of, "as_of").isoformat(),
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
        provided_counts=reader.provided_counts(row.get("provided_counts"), subset_parents),
        confirmations=MappingProxyType(
            {
                key: reader.boolean(value, f"confirmations.{key}")
                for key, value in confirmations.items()
            }
        ),
    )


def load_inputs(path: Path, catalogue: Catalogue) -> Inputs:
    return load_inputs_text(read_text(path), path.name, catalogue)
