# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from collections import defaultdict
from collections.abc import Collection, Iterator, MutableMapping
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, replace
from datetime import date
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from types import MappingProxyType
from typing import Never

from . import PROJECT_NAME
from .catalogue import Catalogue, FindingEntry, sku_key
from .errors import InputError
from .model import Collector, Finding, FindingValue, Product, Scan
from .parsing import parse_yaml, read_text

_IDENTIFIER = re.compile(r"[A-Za-z0-9_]{1,64}")
_GUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
_LICENCE_REFERENCE = re.compile(r"https://learn\.microsoft\.com/[^\s]+")
_MAPPING_REFERENCE = re.compile(r"https://[^/\s?#]+(?:[/?#][^\s]*)?")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_SIGNALS = ("add_on", "bundled")
_PLAN_CLASSES = (*_SIGNALS, "no_workload")
_PLAN_GAP_REASONS = (
    "licence_plan_list_incomplete",
    "licence_plan_list_missing",
    "licence_not_classified",
)
_PRODUCT_COUNT = "licences.product_count"
_RULE_ID = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
_EXTENSION = re.compile(r"[a-z0-9]+")
_RISKY_FINDING_PREFIX = "office_files.kind."
_OPERATORS = ("exists", "==", ">", ">=")
STATUSES = ("ready", "needs_work", "blocker", "unknown")
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


@dataclass(frozen=True)
class ServicePlan:
    sku_part_number: str
    sku_guid: str
    name: str
    guid: str
    workload: str | None
    signal: str
    reference_url: str
    checked_on: date
    note: MappingABC[str, str] | None


@dataclass(frozen=True)
class Condition:
    finding: str
    op: str
    value: FindingValue | None
    provenance: str | None = None


@dataclass(frozen=True)
class StatusRule:
    id: str
    when: tuple[Condition, ...]
    status: str
    reason: MappingABC[str, str]


@dataclass(frozen=True)
class WorkloadRules:
    ready: tuple[Condition, ...]
    ready_reason: MappingABC[str, str]
    rules: tuple[StatusRule, ...]


@dataclass(frozen=True)
class StatusRuleSet:
    workloads: MappingABC[str, WorkloadRules]
    file_name: str


@dataclass(frozen=True)
class MissingEvidence:
    finding_id: str
    reason_code: str
    collector: str | None


@dataclass(frozen=True)
class WorkloadStatus:
    workload: str
    status: str
    reason_code: str | None
    missing: tuple[MissingEvidence, ...]
    deciding: StatusRule | None
    notes: tuple[StatusRule, ...]
    evidence: tuple[Finding, ...]

    @property
    def incomplete(self) -> bool:
        return bool(self.missing)


@dataclass(frozen=True)
class RiskyKind:
    id: str
    finding_id: str
    label: MappingABC[str, str]
    note: MappingABC[str, str]
    extensions: tuple[str, ...]


@dataclass(frozen=True)
class FunctionMapping:
    function: str
    workload: str
    microsoft: MappingABC[str, str]
    replacement: MappingABC[str, str]
    coverage: str
    reference_url: str | None
    checked_on: date | None
    note: MappingABC[str, str] | None
    need_finding: str | None = None


@dataclass(frozen=True)
class Mapping:
    profile: str
    label: MappingABC[str, str]
    description: MappingABC[str, str]
    product_profile: bool
    no_function: tuple[str, ...]
    functions: tuple[FunctionMapping, ...]
    file_name: str


def rules_dir() -> Traversable:
    return files("fazit").joinpath("rules")


class _RuleReader:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    def fail(self, field: str, code: str = "invalid_field") -> Never:
        raise InputError(code, file=self.file_name, field=field)

    def fields(
        self, value: object, field: str, required: tuple[str, ...], optional: tuple[str, ...] = ()
    ) -> dict:
        if not isinstance(value, dict) or value.keys() - {*required, *optional}:
            self.fail(field)
        for name in required:
            if name not in value:
                self.fail(f"{field}.{name}" if field != "$" else name, "missing_field")
        return value

    def rows(self, value: object, field: str, *, allow_empty: bool = False) -> list[object]:
        if not isinstance(value, list) or (not value and not allow_empty):
            self.fail(field)
        return value

    def matches(self, value: object, field: str, pattern: re.Pattern[str]) -> str:
        if not isinstance(value, str) or not pattern.fullmatch(value):
            self.fail(field)
        return value

    def choice(self, value: object, field: str, allowed: Collection[str]) -> str:
        if not isinstance(value, str) or value not in allowed:
            self.fail(field, "invalid_code")
        return value

    def bilingual(self, value: object, field: str) -> MappingABC[str, str]:
        text = self.fields(value, field, ("en", "de"))
        for lang, sentence in text.items():
            if not isinstance(sentence, str) or not sentence.strip():
                self.fail(f"{field}.{lang}")
        return MappingProxyType(text)

    def check_date(self, value: object, field: str) -> date:
        if type(value) is date:
            return value
        text = self.matches(value, field, _DATE)
        try:
            return date.fromisoformat(text)
        except ValueError:
            raise InputError("invalid_field", file=self.file_name, field=field) from None


def _read_rules(
    name: str, path: Path | None, checksums: MutableMapping[str, str] | None
) -> tuple[_RuleReader, object]:
    source = path if path is not None else rules_dir().joinpath(name)
    text = read_text(source)
    data = parse_yaml(text, source.name)
    if checksums is not None:
        checksums[source.name] = sha256(text.encode("utf-8")).hexdigest()
    return _RuleReader(source.name), data


def _function_mapping(
    item: object, field: str, reader: _RuleReader, catalogue: Catalogue, product_profile: bool
) -> FunctionMapping:
    references = ("reference_url", "checked_on")
    row = reader.fields(
        item,
        field,
        ("function", "workload", "microsoft", "replacement", "coverage")
        + (references if product_profile else ()),
        ("note", "need_finding") + (() if product_profile else references),
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
        checked_on = reader.check_date(row["checked_on"], f"{field}.checked_on")
    else:
        for key in references:
            if row.get(key) is not None:
                reader.fail(f"{field}.{key}")
    need_finding = row.get("need_finding")
    if need_finding is not None:
        entry = catalogue.finding(need_finding) if isinstance(need_finding, str) else None
        if entry is None or not (
            (entry.type == "boolean" and entry.workload == workload)
            or (
                entry.type == "count"
                and entry.provided in ("software_list", "software_list_without_web_version")
            )
        ):
            reader.fail(f"{field}.need_finding")
    return FunctionMapping(
        function=reader.matches(row["function"], f"{field}.function", _RULE_ID),
        workload=workload,
        microsoft=reader.bilingual(row["microsoft"], f"{field}.microsoft"),
        replacement=reader.bilingual(row["replacement"], f"{field}.replacement"),
        coverage=coverage,
        reference_url=reference_url,
        checked_on=checked_on,
        note=reader.bilingual(row["note"], f"{field}.note") if "note" in row else None,
        need_finding=need_finding,
    )


def load_mapping(
    profile: str,
    catalogue: Catalogue,
    directory: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> Mapping:
    if profile not in PROFILES:
        raise InputError("unsupported_profile", file=PROJECT_NAME, field="--profile")
    name = f"mappings/{profile}.yaml"
    reader, data = _read_rules(name, directory / name if directory is not None else None, checksums)
    root = reader.fields(
        data,
        "$",
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
    return Mapping(
        profile=profile,
        label=reader.bilingual(root["label"], "label"),
        description=reader.bilingual(root["description"], "description"),
        product_profile=product_profile,
        no_function=tuple(no_function),
        functions=tuple(functions.values()),
        file_name=reader.file_name,
    )


type _PlanDetail = tuple[str, str | None, MappingABC[str, str] | None]


def _plan_definitions(
    items: object, reader: _RuleReader, workload_ids: Collection[str]
) -> dict[str, _PlanDetail]:
    plans: dict[str, _PlanDetail] = {}
    names: set[str] = set()
    for index, item in enumerate(reader.rows(items, "plans")):
        field = f"plans[{index}]"
        row = reader.fields(item, field, ("name", "guid", "workload"), ("note",))
        name = reader.matches(row["name"], f"{field}.name", _IDENTIFIER)
        if name.casefold() in names:
            reader.fail(f"{field}.name", "duplicate_id")
        names.add(name.casefold())
        workload = row["workload"]
        if workload is not None:
            workload = reader.choice(workload, f"{field}.workload", workload_ids)
        guid = reader.matches(row["guid"], f"{field}.guid", _GUID).lower()
        note = reader.bilingual(row["note"], f"{field}.note") if "note" in row else None
        plans[name] = (guid, workload, note)
    return plans


def load_service_plans(
    catalogue: Catalogue,
    path: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> tuple[ServicePlan, ...]:
    source = path if path is not None else rules_dir().joinpath("service_plans.yaml")
    text = read_text(source)
    plans = _parse_service_plans(text, source.name, catalogue)
    if checksums is not None:
        checksums[source.name] = sha256(text.encode("utf-8")).hexdigest()
    return plans


@lru_cache(maxsize=2)
def _parse_service_plans(
    text: str, file_name: str, catalogue: Catalogue
) -> tuple[ServicePlan, ...]:
    reader = _RuleReader(file_name)
    data = parse_yaml(text, file_name)
    root = reader.fields(data, "$", ("reference_url", "checked_on", "plans", "products"))
    reference = reader.matches(root["reference_url"], "reference_url", _LICENCE_REFERENCE)
    checked_on = reader.check_date(root["checked_on"], "checked_on")
    definitions = _plan_definitions(root["plans"], reader, catalogue.workload_ids)
    plans = []
    sku_guids: set[str] = set()
    for index, item in enumerate(reader.rows(root["products"], "products")):
        field = f"products[{index}]"
        product = reader.fields(item, field, ("sku_part_number", "sku_guid"), _PLAN_CLASSES)
        sku_guid = reader.matches(product["sku_guid"], f"{field}.sku_guid", _GUID).lower()
        if sku_guid in sku_guids:
            reader.fail(f"{field}.sku_guid", "duplicate_id")
        sku_guids.add(sku_guid)
        part_number = product["sku_part_number"]
        if not catalogue.accepts_sku_part_number(part_number, sku_guid):
            reader.fail(f"{field}.sku_part_number")
        plan_guids: set[str] = set()
        for signal in _PLAN_CLASSES:
            members = reader.rows(product.get(signal, []), f"{field}.{signal}", allow_empty=True)
            for number, member in enumerate(members):
                path = f"{field}.{signal}[{number}]"
                name = reader.choice(member, path, definitions.keys())
                guid, workload, note = definitions[name]
                if guid in plan_guids:
                    reader.fail(path, "duplicate_id")
                if (signal == "no_workload") != (workload is None):
                    reader.fail(path)
                plan_guids.add(guid)
                plans.append(
                    ServicePlan(
                        part_number,
                        sku_guid,
                        name,
                        guid,
                        workload,
                        signal,
                        reference,
                        checked_on,
                        note,
                    )
                )
        if not plan_guids:
            reader.fail(field)
    return tuple(plans)


def classify_product(
    product: Product, plans: tuple[ServicePlan, ...]
) -> tuple[ServicePlan | None, ...]:
    key = product.key
    matched = {
        (plan.name.casefold(), plan.guid): plan
        for plan in plans
        if sku_key(plan.sku_part_number, plan.sku_guid) == key
    }
    return tuple(
        matched.get((plan.name.casefold(), plan.guid)) if plan.name is not None else None
        for plan in product.service_plans
    )


def _licence_signals(
    products: tuple[Product, ...], plans: tuple[ServicePlan, ...], file_name: str
) -> tuple[set[tuple[str, str]], str | None]:
    rosters: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for plan in plans:
        rosters[sku_key(plan.sku_part_number, plan.sku_guid)].add(plan.guid)
    parts = {part for part, _ in rosters}
    guids = {guid for _, guid in rosters}

    assigned: set[tuple[str, str]] = set()
    gaps: set[str] = set()
    for index, product in enumerate(products):
        key = sku_key(product.sku_part_number or "", product.sku_guid or "")
        part, guid = key
        # Roster completeness applies to every known product in the inventory.
        if expected := rosters.get(key):
            if not expected.issubset(plan.guid for plan in product.service_plans):
                gaps.add("licence_plan_list_incomplete")
        elif guid in guids or part in parts:
            field = "sku_part_number" if guid in guids else "sku_guid"
            raise InputError(
                "sku_identity_mismatch", file=file_name, field=f"licences.products[{index}].{field}"
            )
        if not product.assigned:
            continue
        if not product.service_plans:
            gaps.add("licence_plan_list_missing")
            continue
        for match in classify_product(product, plans):
            if match is None:
                gaps.add("licence_not_classified")
            elif match.workload is not None:
                assigned.add((match.workload, match.signal))
    return assigned, next((code for code in _PLAN_GAP_REASONS if code in gaps), None)


def licence_findings(
    scan: Scan,
    plans: tuple[ServicePlan, ...],
    catalogue: Catalogue,
    *,
    file_name: str = "scan.json",
) -> tuple[Finding, ...]:
    licences = scan.licences
    if licences is None:
        return ()
    licences.check_complete_coverage(file_name)
    coverage = licences.coverage
    collector = scan.collector(licences.collector)
    coverage_gap = None
    if collector is not None and collector.status == "partial":
        coverage_gap = collector.reason
        if coverage.kind == "complete":
            coverage = replace(coverage, kind="partial")
    coverage_gap = coverage_gap or {
        "partial": "coverage_partial",
        "unknown": "coverage_unknown",
    }.get(coverage.kind)
    count = len(licences.products)
    product_count = Finding(
        id=_PRODUCT_COUNT,
        workload=_PRODUCT_COUNT.split(".")[0],
        value=count or None,
        unit="products",
        provenance="measured" if count else "unknown",
        collector=licences.collector,
        source=licences.source,
        collected_at=licences.collected_at,
        period=None,
        coverage=coverage,
        missing_reason=None if count else "licence_products_missing",
    )
    assigned, classification_gap = _licence_signals(licences.products, plans, file_name)
    absence_gap = product_count.missing_reason or classification_gap or coverage_gap
    licensed_accounts = scan.finding("directory.licensed_user_count")
    if (
        licensed_accounts is not None
        and type(licensed_accounts.value) is int
        and licensed_accounts.value > 0
        and not any(product.assigned for product in licences.products)
    ):
        absence_gap = "licence_assignments_conflict"
    findings = [product_count]
    for workload in catalogue.workload_ids:
        for signal in _SIGNALS:
            value = (workload, signal) in assigned
            missing = None if value else absence_gap
            findings.append(
                replace(
                    product_count,
                    id=f"{workload}.licence_{signal}_assigned",
                    workload=workload,
                    value=None if missing else value,
                    unit=None,
                    provenance="unknown" if missing else "measured",
                    missing_reason=missing,
                )
            )
    return tuple(findings)


def _value_types(catalogue: Catalogue) -> dict[str, str]:
    return {
        **{entry.id: entry.type for entry in catalogue.findings},
        _PRODUCT_COUNT: "count",
        **{
            f"{workload}.licence_{signal}_assigned": "boolean"
            for workload in catalogue.workload_ids
            for signal in _SIGNALS
        },
    }


def _literal_matches(value: object, kind: str) -> bool:
    if kind in ("count", "bytes"):
        return type(value) is int and value >= 0
    return kind == "boolean" and type(value) is bool


def _conditions(
    value: object, field: str, reader: _RuleReader, types: MappingABC[str, str]
) -> tuple[Condition, ...]:
    conditions = []
    for index, item in enumerate(reader.rows(value, field)):
        member = f"{field}[{index}]"
        row = reader.fields(item, member, ("finding", "op"), ("value", "provenance"))
        finding_id = reader.choice(row["finding"], f"{member}.finding", types.keys())
        op = reader.choice(row["op"], f"{member}.op", _OPERATORS)
        kind = types[finding_id]
        literal = row.get("value")
        if op in (">", ">=") and kind not in ("count", "bytes"):
            reader.fail(f"{member}.op")
        if op == "exists":
            if "value" in row:
                reader.fail(f"{member}.value")
        elif not _literal_matches(literal, kind):
            reader.fail(f"{member}.value")
        provenance = (
            reader.choice(row["provenance"], f"{member}.provenance", ("measured", "provided"))
            if "provenance" in row
            else None
        )
        conditions.append(Condition(finding_id, op, literal, provenance))
    return tuple(conditions)


def _workload_rules(
    item: object,
    field: str,
    reader: _RuleReader,
    types: MappingABC[str, str],
    rule_ids: set[str],
) -> WorkloadRules:
    block = reader.fields(item, field, ("ready", "rules"))
    ready = reader.fields(block["ready"], f"{field}.ready", ("evidence", "reason"))
    conditions = _conditions(ready["evidence"], f"{field}.ready.evidence", reader, types)
    reason = reader.bilingual(ready["reason"], f"{field}.ready.reason")
    rules = []
    entries = reader.rows(block["rules"], f"{field}.rules", allow_empty=True)
    for index, item in enumerate(entries):
        member = f"{field}.rules[{index}]"
        row = reader.fields(item, member, ("id", "when", "status", "reason"))
        rule_id = reader.matches(row["id"], f"{member}.id", _RULE_ID)
        if rule_id in rule_ids:
            reader.fail(f"{member}.id", "duplicate_id")
        rule_ids.add(rule_id)
        rules.append(
            StatusRule(
                rule_id,
                _conditions(row["when"], f"{member}.when", reader, types),
                reader.choice(row["status"], f"{member}.status", STATUSES[1:3]),
                reader.bilingual(row["reason"], f"{member}.reason"),
            )
        )
    return WorkloadRules(conditions, reason, tuple(rules))


def load_status_rules(
    catalogue: Catalogue,
    path: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> StatusRuleSet:
    reader, data = _read_rules("status.yaml", path, checksums)
    root = reader.fields(data, "$", ("workloads",))
    workload_ids = catalogue.workload_ids
    blocks = reader.fields(root["workloads"], "workloads", workload_ids)
    types = _value_types(catalogue)
    rule_ids: set[str] = set()
    workloads = {
        workload: _workload_rules(
            blocks[workload], f"workloads.{workload}", reader, types, rule_ids
        )
        for workload in workload_ids
    }
    return StatusRuleSet(MappingProxyType(workloads), reader.file_name)


def _complete(finding: Finding | None) -> bool:
    if finding is None or finding.value is None or finding.provenance == "unknown":
        return False
    if finding.coverage is None:
        return finding.provenance == "provided"
    return finding.coverage.kind == "complete"


def mapping_need(finding: Finding | None) -> str:
    if finding is not None and _complete(finding):
        return "yes" if finding.value else "no"
    return "unknown"


def evidence_conflicts(measured: Finding, provided: Finding) -> bool:
    return (
        measured.provenance == "measured"
        and provided.provenance == "provided"
        and _complete(provided)
        and type(measured.value) is int
        and type(provided.value) is int
        and measured.value > 0
        and measured.value > provided.value
    )


def provided_answers_conflict(first: Finding, second: Finding) -> bool:
    return first.provenance == second.provenance == "provided" and first.value != second.value


def select_evidence(recorded: Finding | None, supplied: Finding) -> Finding:
    if recorded is None or recorded.provenance == "unknown":
        return supplied
    if supplied.provenance == "unknown":
        return recorded
    if recorded.provenance == "measured":
        if _complete(recorded) or evidence_conflicts(recorded, supplied):
            return recorded
        if not _complete(supplied) and recorded.is_lower_bound:
            return recorded
    return supplied


def _skipped_gap(
    finding: Finding | None, collectors: MappingABC[str, Collector]
) -> MissingEvidence | None:
    if finding is None or finding.collector is None:
        return None
    collector = collectors.get(finding.collector)
    if collector is not None and collector.status == "skipped":
        return MissingEvidence(
            finding.id, finding.missing_reason or "collector_skipped", collector.id
        )
    return None


def _condition_evidence(
    condition: Condition, finding: Finding | None, alternative: Finding | None
) -> Finding | None:
    if alternative is not None and alternative.provenance == condition.provenance:
        return alternative
    return finding


def _observation_gaps(
    workload: str,
    conditions: Collection[Condition],
    findings: MappingABC[str, Finding],
    alternatives: MappingABC[str, Finding],
    collectors: MappingABC[str, Collector],
) -> Iterator[MissingEvidence]:
    required = {condition.finding for condition in conditions}
    confirmations = {
        condition.finding for condition in conditions if condition.provenance == "provided"
    }
    for finding_id, alternative in alternatives.items():
        if alternative.workload != workload:
            continue
        if finding_id in required and (skipped := _skipped_gap(alternative, collectors)):
            yield skipped
        primary = findings.get(finding_id)
        if primary is None:
            continue
        if provided_answers_conflict(primary, alternative):
            yield MissingEvidence(finding_id, "provided_answers_conflict", None)
        elif evidence_conflicts(primary, alternative):
            yield MissingEvidence(finding_id, "confirmation_conflict", None)
        elif (
            finding_id in confirmations
            and {primary.provenance, alternative.provenance} == {"measured", "provided"}
            and primary.value is not None
            and alternative.value is not None
            and primary.value != alternative.value
            and (type(primary.value) is bool or (_complete(primary) and _complete(alternative)))
        ):
            yield MissingEvidence(finding_id, "confirmation_conflict", None)


def _collector_gaps(
    finding_ids: Collection[str],
    entries: MappingABC[str, FindingEntry],
    collectors: MappingABC[str, Collector],
    observed: Collection[MissingEvidence],
) -> Iterator[MissingEvidence]:
    recorded = {(gap.finding_id, gap.collector) for gap in observed}
    for finding_id in finding_ids:
        entry = entries.get(finding_id)
        if entry is None:
            continue
        for collector_id in sorted({method for method, _ in entry.measured_by}):
            collector = collectors.get(collector_id)
            if collector is None or collector.status == "ok":
                continue
            if (finding_id, collector_id) not in recorded:
                fallback = (
                    "collector_skipped" if collector.status == "skipped" else "coverage_partial"
                )
                yield MissingEvidence(finding_id, collector.reason or fallback, collector_id)


def _gap(
    condition: Condition,
    finding: Finding | None,
    provided_ids: Collection[str],
    collectors: MappingABC[str, Collector],
) -> MissingEvidence | None:
    expected_answer = condition.provenance == "provided" or (
        condition.provenance is None and condition.finding in provided_ids
    )
    if skipped := _skipped_gap(finding, collectors):
        return skipped
    collector_id = finding.collector if finding else None
    if finding is None:
        code = "answer_not_provided" if expected_answer else "not_in_scan"
    elif finding.provenance == "unknown":
        code = finding.missing_reason or "not_established"
    elif condition.provenance is not None and condition.provenance != finding.provenance:
        code = "answer_not_provided" if expected_answer else "not_in_scan"
        collector_id = None
    elif _complete(finding):
        return None
    elif finding.provenance == "provided":
        code = "answer_not_provided"
    elif finding.coverage is not None and finding.coverage.kind == "partial":
        code = "coverage_partial"
    else:
        code = "coverage_unknown"
    return MissingEvidence(condition.finding, code, collector_id)


def _matches_condition(condition: Condition, finding: Finding) -> bool:
    value, literal = finding.value, condition.value
    if condition.op == "exists":
        return value is not None
    if condition.op == "==":
        return type(value) is type(literal) and value == literal
    if type(value) is not int or type(literal) is not int:
        return False
    return value > literal if condition.op == ">" else value >= literal


def _problem_result(
    condition: Condition, finding: Finding | None, gap: MissingEvidence | None
) -> bool | None:
    if finding is None:
        return None
    if gap is None:
        return _matches_condition(condition, finding)
    if (
        gap.reason_code in ("coverage_partial", "coverage_unknown")
        and finding.id.endswith(".licence_add_on_assigned")
        and finding.value is True
        and condition.provenance in (None, finding.provenance)
    ):
        return _matches_condition(condition, finding)
    if (
        gap.reason_code in ("coverage_partial", "coverage_unknown", "answer_not_provided")
        and (condition.provenance is None or condition.provenance == finding.provenance)
        and condition.op != "=="
        and finding.is_lower_bound
        and _matches_condition(condition, finding)
    ):
        return True
    return None


def _unknown_code(
    gaps: tuple[MissingEvidence, ...], bundled: Finding | None, provided_ids: Collection[str]
) -> str:
    for code in (
        "licence_assignments_conflict",
        *_PLAN_GAP_REASONS,
        "provided_answers_conflict",
        "confirmation_conflict",
    ):
        if any(gap.reason_code == code for gap in gaps):
            return code
    if bundled is not None and bundled.value is True and _complete(bundled):
        if any(gap.finding_id in provided_ids for gap in gaps):
            return "licensed_use_not_measured"
    return gaps[0].reason_code if gaps else "not_established"


def _evaluate_workload(
    workload: str,
    block: WorkloadRules,
    findings: MappingABC[str, Finding],
    entries: MappingABC[str, FindingEntry],
    collectors: MappingABC[str, Collector],
    alternatives: MappingABC[str, Finding],
) -> WorkloadStatus:
    conditions = dict.fromkeys(
        (*block.ready, *(item for rule in block.rules for item in rule.when))
    )
    ids = dict.fromkeys(condition.finding for condition in conditions)
    provided_ids = {
        finding_id
        for finding_id in ids
        if finding_id in entries and entries[finding_id].provided != "no"
    }
    observations = {
        condition: _condition_evidence(
            condition, findings.get(condition.finding), alternatives.get(condition.finding)
        )
        for condition in conditions
    }
    observation_gaps = tuple(
        _observation_gaps(workload, conditions, findings, alternatives, collectors)
    )
    conflicted_answers = {
        gap.finding_id: gap
        for gap in observation_gaps
        if gap.reason_code == "provided_answers_conflict"
    }
    gaps = {
        condition: conflicted_answers.get(condition.finding)
        or _gap(condition, evidence, provided_ids, collectors)
        for condition, evidence in observations.items()
    }
    results = {
        condition: _problem_result(condition, evidence, gaps[condition])
        for condition, evidence in observations.items()
    }
    missing = {gap: None for condition in block.ready if (gap := gaps[condition]) is not None}
    fired = []
    for rule in block.rules:
        matches = [results[condition] for condition in rule.when]
        if False not in matches:
            missing.update(
                dict.fromkeys(
                    gap for condition in rule.when if (gap := gaps[condition]) is not None
                )
            )
        if all(matches):
            fired.append(rule)
    deciding = max(fired, key=lambda rule: STATUSES.index(rule.status), default=None)
    bundled_id = f"{workload}.licence_bundled_assigned"
    bundled = findings.get(bundled_id)
    missing.update(dict.fromkeys(observation_gaps))
    missing.update(dict.fromkeys(_collector_gaps(ids, entries, collectors, missing)))
    ids.update(dict.fromkeys(gap.finding_id for gap in missing))
    if bundled is not None and bundled.value is True:
        ids[bundled_id] = None
    evidence = tuple(findings[finding_id] for finding_id in ids if finding_id in findings)
    incomplete = tuple(missing)
    if deciding is not None:
        notes = tuple(rule for rule in fired if rule is not deciding)
        return WorkloadStatus(
            workload, deciding.status, None, incomplete, deciding, notes, evidence
        )
    if not incomplete and all(results[condition] for condition in block.ready):
        return WorkloadStatus(workload, "ready", None, (), None, (), evidence)
    code = _unknown_code(incomplete, bundled, provided_ids)
    return WorkloadStatus(workload, "unknown", code, incomplete, None, (), evidence)


def evaluate(
    findings: MappingABC[str, Finding],
    rule_set: StatusRuleSet,
    catalogue: Catalogue,
    *,
    collectors: MappingABC[str, Collector] | None = None,
    alternatives: MappingABC[str, Finding] | None = None,
) -> tuple[WorkloadStatus, ...]:
    entries = {entry.id: entry for entry in catalogue.findings}
    return tuple(
        _evaluate_workload(
            workload,
            rule_set.workloads[workload],
            findings,
            entries,
            collectors or {},
            alternatives or {},
        )
        for workload in catalogue.workload_ids
    )


def load_risky_file_types(
    catalogue: Catalogue,
    path: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> tuple[RiskyKind, ...]:
    reader, data = _read_rules("risky_file_types.yaml", path, checksums)
    root = reader.fields(data, "$", ("kinds",))
    finding_ids = {
        entry.id.removeprefix(_RISKY_FINDING_PREFIX): entry.id
        for entry in catalogue.findings
        if entry.id.startswith(_RISKY_FINDING_PREFIX) and entry.type == "count"
    }
    kinds: dict[str, RiskyKind] = {}
    seen_extensions: set[str] = set()
    for index, item in enumerate(reader.rows(root["kinds"], "kinds")):
        field = f"kinds[{index}]"
        row = reader.fields(item, field, ("id", "label", "note", "extensions"))
        kind = reader.choice(row["id"], f"{field}.id", finding_ids.keys())
        if kind in kinds:
            reader.fail(f"{field}.id", "duplicate_id")
        extensions = []
        for number, extension in enumerate(reader.rows(row["extensions"], f"{field}.extensions")):
            member = f"{field}.extensions[{number}]"
            extension = reader.matches(extension, member, _EXTENSION)
            if extension in seen_extensions:
                reader.fail(member, "duplicate_id")
            seen_extensions.add(extension)
            extensions.append(extension)
        kinds[kind] = RiskyKind(
            kind,
            finding_ids[kind],
            reader.bilingual(row["label"], f"{field}.label"),
            reader.bilingual(row["note"], f"{field}.note"),
            tuple(extensions),
        )
    return tuple(kinds.values())
