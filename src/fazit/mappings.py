# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .catalogue import Catalogue
from .errors import InputError
from .rules import read_rules
from .validation import RULE_ID, Validator

PROFILES = ("opendesk", "nextcloud", "generic")
COVERAGE_LADDER = (
    "in_suite",
    "in_suite_with_limits",
    "announced",
    "component_vendor_solution",
    "open_source_community",
    "open_source_third_party",
    "proprietary_third_party",
    "not_available",
)
_MAPPING_REFERENCE = re.compile(r"https://[^/\s?#]+(?:[/?#][^\s]*)?")


@dataclass(frozen=True)
class FunctionMapping:
    function: str
    workload: str
    microsoft: Mapping[str, str]
    replacement: Mapping[str, str]
    coverage: str
    reference_url: str | None
    checked_on: date | None
    note: Mapping[str, str] | None
    need_finding: str | None = None
    need_if_positive: str | None = None


@dataclass(frozen=True)
class TargetMapping:
    profile: str
    label: Mapping[str, str]
    description: Mapping[str, str]
    product_profile: bool
    no_function: tuple[str, ...]
    functions: tuple[FunctionMapping, ...]
    file_name: str


def _need_conditions(
    row: dict, field: str, reader: Validator, catalogue: Catalogue, workload: str
) -> tuple[str | None, str | None]:
    need_finding = row.get("need_finding")
    entry = catalogue.finding(need_finding) if isinstance(need_finding, str) else None
    if need_finding is not None and (
        entry is None
        or not (
            (entry.type == "boolean" and entry.workload == workload)
            or (
                entry.type == "count"
                and entry.provided in ("software_list", "software_list_without_web_version")
            )
        )
    ):
        reader.fail(f"{field}.need_finding")
    need_if_positive = row.get("need_if_positive")
    if need_if_positive is not None:
        count = catalogue.finding(need_if_positive) if isinstance(need_if_positive, str) else None
        if entry is None or entry.type != "boolean" or count is None or count.type != "count":
            reader.fail(f"{field}.need_if_positive")
    return need_finding, need_if_positive


def _function_mapping(
    item: object, field: str, reader: Validator, catalogue: Catalogue, product_profile: bool
) -> FunctionMapping:
    references = ("reference_url", "checked_on")
    row = reader.fields(
        item,
        field,
        ("function", "workload", "microsoft", "replacement", "coverage")
        + (references if product_profile else ()),
        ("note", "need_finding", "need_if_positive") + (() if product_profile else references),
    )
    workload = reader.choice(row["workload"], f"{field}.workload", catalogue.workload_ids)
    steps = COVERAGE_LADDER if product_profile else COVERAGE_LADDER[4:]
    coverage = reader.choice(row["coverage"], f"{field}.coverage", steps)
    reference_url = None
    checked_on = None
    if product_profile:
        reference_url = reader.matches(
            row["reference_url"], f"{field}.reference_url", _MAPPING_REFERENCE
        )
        checked_on = reader.calendar_date(row["checked_on"], f"{field}.checked_on")
    else:
        for key in references:
            if row.get(key) is not None:
                reader.fail(f"{field}.{key}")
    need_finding, need_if_positive = _need_conditions(row, field, reader, catalogue, workload)
    return FunctionMapping(
        function=reader.matches(row["function"], f"{field}.function", RULE_ID),
        workload=workload,
        microsoft=reader.bilingual(row["microsoft"], f"{field}.microsoft"),
        replacement=reader.bilingual(row["replacement"], f"{field}.replacement"),
        coverage=coverage,
        reference_url=reference_url,
        checked_on=checked_on,
        note=reader.bilingual(row["note"], f"{field}.note") if "note" in row else None,
        need_finding=need_finding,
        need_if_positive=need_if_positive,
    )


def load_mapping(
    profile: str,
    catalogue: Catalogue,
    directory: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> TargetMapping:
    if profile not in PROFILES:
        raise InputError("unsupported_profile_option", field="--profile")
    name = f"mappings/{profile}.yaml"
    reader, data = read_rules(name, directory / name if directory is not None else None, checksums)
    root = reader.fields(
        data,
        "",
        ("profile", "label", "description", "product_profile", "no_function", "functions"),
    )
    reader.choice(root["profile"], "profile", (profile,))
    product_profile = root["product_profile"]
    if type(product_profile) is not bool:
        reader.fail("product_profile")
    workload_ids = catalogue.workload_ids
    no_function = []
    for index, item in enumerate(reader.rows(root["no_function"], "no_function", allow_empty=True)):
        field = f"no_function[{index}]"
        workload = reader.choice(item, field, workload_ids)
        if workload in no_function:
            reader.fail(field, "duplicate_id")
        no_function.append(workload)
    if any(
        not workload.assessed and workload.id not in no_function for workload in catalogue.workloads
    ):
        reader.fail("no_function")
    functions: dict[str, FunctionMapping] = {}
    for index, item in enumerate(reader.rows(root["functions"], "functions")):
        field = f"functions[{index}]"
        row = _function_mapping(item, field, reader, catalogue, product_profile)
        if row.function in functions:
            reader.fail(f"{field}.function", "duplicate_id")
        functions[row.function] = row
    covered = {row.workload for row in functions.values()}
    if covered.intersection(no_function) or covered.union(no_function) != set(workload_ids):
        reader.fail("no_function")
    return TargetMapping(
        profile=profile,
        label=reader.bilingual(root["label"], "label"),
        description=reader.bilingual(root["description"], "description"),
        product_profile=product_profile,
        no_function=tuple(no_function),
        functions=tuple(functions.values()),
        file_name=reader.file_name,
    )
