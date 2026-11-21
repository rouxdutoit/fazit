# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from collections.abc import Collection, MutableMapping
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, replace
from datetime import date
from hashlib import sha256
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from types import MappingProxyType
from typing import Never

from . import PROJECT_NAME
from .catalogue import Catalogue
from .errors import InputError
from .model import Collector, Finding, FindingValue, Product, Scan
from .parsing import parse_yaml, read_text

_IDENTIFIER = re.compile(r"[A-Za-z0-9_]{1,64}")
_GUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
_LICENCE_REFERENCE = re.compile(r"https://learn\.microsoft\.com/[^\s]+")
_MAPPING_REFERENCE = re.compile(r"https://[^/\s?#]+(?:[/?#][^\s]*)?")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_SIGNALS = ("add_on", "bundled")
_PRODUCT_COUNT = "licences.product_count"
_VALUE_CODE = re.compile(r"[a-z0-9_]+(?:\.[a-z0-9_]+)*")
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
    workload: str
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
    return files("befund").joinpath("rules")


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
        if entry is None or entry.workload != workload or entry.type != "boolean":
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


def _service_plan(
    item: object, field: str, reader: _RuleReader, workload_ids: Collection[str]
) -> ServicePlan:
    row = reader.fields(
        item,
        field,
        (
            "sku_part_number",
            "sku_guid",
            "name",
            "guid",
            "workload",
            "signal",
            "reference_url",
            "checked_on",
        ),
        ("note",),
    )
    return ServicePlan(
        sku_part_number=reader.matches(
            row["sku_part_number"], f"{field}.sku_part_number", _IDENTIFIER
        ),
        sku_guid=reader.matches(row["sku_guid"], f"{field}.sku_guid", _GUID).lower(),
        name=reader.matches(row["name"], f"{field}.name", _IDENTIFIER),
        guid=reader.matches(row["guid"], f"{field}.guid", _GUID).lower(),
        workload=reader.choice(row["workload"], f"{field}.workload", workload_ids),
        signal=reader.choice(row["signal"], f"{field}.signal", _SIGNALS),
        reference_url=reader.matches(
            row["reference_url"], f"{field}.reference_url", _LICENCE_REFERENCE
        ),
        checked_on=reader.check_date(row["checked_on"], f"{field}.checked_on"),
        note=reader.bilingual(row["note"], f"{field}.note") if "note" in row else None,
    )


def load_service_plans(
    catalogue: Catalogue,
    path: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> tuple[ServicePlan, ...]:
    reader, data = _read_rules("service_plans.yaml", path, checksums)
    root = reader.fields(data, "$", ("plans",))
    plans: dict[tuple[str, str], ServicePlan] = {}
    workload_ids = catalogue.workload_ids
    for index, item in enumerate(reader.rows(root["plans"], "plans")):
        field = f"plans[{index}]"
        plan = _service_plan(item, field, reader, workload_ids)
        key = plan.sku_guid, plan.guid
        if key in plans:
            reader.fail(f"{field}.name", "duplicate_id")
        plans[key] = plan
    return tuple(plans.values())


def classify_product(
    product: Product, plans: tuple[ServicePlan, ...]
) -> tuple[ServicePlan | None, ...]:
    matched = {
        (plan.name.casefold(), plan.guid): plan
        for plan in plans
        if (plan.sku_part_number.casefold(), plan.sku_guid)
        == (product.sku_part_number.casefold(), product.sku_guid)
    }
    return tuple(matched.get((plan.name.casefold(), plan.guid)) for plan in product.service_plans)


def _licence_signals(
    products: tuple[Product, ...], plans: tuple[ServicePlan, ...], workload_ids: tuple[str, ...]
) -> tuple[set[tuple[str, str]], set[str]]:
    assigned: set[tuple[str, str]] = set()
    unclassified: set[str] = set()
    for product in products:
        if not product.assigned:
            continue
        for identity, match in zip(
            product.service_plans, classify_product(product, plans), strict=True
        ):
            if match is not None:
                assigned.add((match.workload, match.signal))
                continue
            possible = {
                plan.workload
                for plan in plans
                if plan.guid == identity.guid or plan.name.casefold() == identity.name.casefold()
            }
            # An unrecognised plan cannot establish that a workload lacks a licence.
            unclassified.update(possible or workload_ids)
    return assigned, unclassified


def licence_findings(
    scan: Scan, plans: tuple[ServicePlan, ...], catalogue: Catalogue
) -> tuple[Finding, ...]:
    licences = scan.licences
    if licences is None:
        return ()
    product_count = Finding(
        id=_PRODUCT_COUNT,
        workload=_PRODUCT_COUNT.split(".")[0],
        value=len(licences.products),
        unit="products",
        provenance="measured",
        collector=licences.collector,
        source=licences.source,
        collected_at=licences.collected_at,
        period=None,
        coverage=licences.coverage,
        missing_reason=None,
    )
    workload_ids = catalogue.workload_ids
    assigned, unclassified = _licence_signals(licences.products, plans, workload_ids)
    findings = [product_count]
    for workload in workload_ids:
        for signal in _SIGNALS:
            value = (workload, signal) in assigned
            unknown = not value and workload in unclassified
            findings.append(
                replace(
                    product_count,
                    id=f"{workload}.licence_{signal}_assigned",
                    workload=workload,
                    value=None if unknown else value,
                    unit=None,
                    provenance="unknown" if unknown else "measured",
                    missing_reason="licence_not_classified" if unknown else None,
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
    if kind == "boolean":
        return type(value) is bool
    return isinstance(value, str) and len(value) <= 64 and bool(_VALUE_CODE.fullmatch(value))


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
    if finding is not None and type(finding.value) is bool and _complete(finding):
        return "yes" if finding.value else "no"
    return "unknown"


def _positive_partial(finding: Finding) -> bool:
    return (
        finding.provenance in ("measured", "provided")
        and finding.coverage is not None
        and finding.coverage.kind == "partial"
        and type(finding.value) is int
        and finding.value > 0
    )


def evidence_conflicts(measured: Finding, provided: Finding) -> bool:
    return (
        measured.provenance == "measured"
        and _positive_partial(measured)
        and provided.provenance == "provided"
        and type(provided.value) is int
        and provided.value == 0
    )


def select_evidence(recorded: Finding | None, supplied: Finding) -> Finding:
    if recorded is None or recorded.provenance == "unknown":
        return supplied
    if supplied.provenance == "unknown":
        return recorded
    if recorded.provenance == "measured":
        if _complete(recorded) or evidence_conflicts(recorded, supplied):
            return recorded
        if not _complete(supplied) and _positive_partial(recorded):
            return recorded
    return supplied


def _gap(
    condition: Condition,
    finding: Finding | None,
    provided_ids: Collection[str],
    collectors: MappingABC[str, Collector],
) -> MissingEvidence | None:
    expected_answer = condition.provenance == "provided" or (
        condition.provenance is None and condition.finding in provided_ids
    )
    collector_id = finding.collector if finding else None
    collector = collectors.get(collector_id) if collector_id else None
    if finding is None:
        code = "answer_not_provided" if expected_answer else "not_in_scan"
    elif finding.provenance == "unknown":
        code = finding.missing_reason or "not_established"
    elif collector is not None and collector.status == "skipped":
        code = "collector_skipped"
    elif condition.provenance is not None and condition.provenance != finding.provenance:
        code = "answer_not_provided" if expected_answer else "not_in_scan"
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
        gap.reason_code in ("coverage_partial", "answer_not_provided")
        and (condition.provenance is None or condition.provenance == finding.provenance)
        and condition.op != "=="
        and _positive_partial(finding)
        and _matches_condition(condition, finding)
    ):
        return True
    return None


def _unknown_code(
    gaps: tuple[MissingEvidence, ...], bundled: Finding | None, provided_ids: Collection[str]
) -> str:
    if any(gap.reason_code == "licence_not_classified" for gap in gaps):
        return "licence_not_classified"
    if bundled is not None and bundled.value is True and _complete(bundled):
        if any(gap.finding_id in provided_ids for gap in gaps):
            return "licensed_use_not_measured"
    return gaps[0].reason_code if gaps else "not_established"


def _evaluate_workload(
    workload: str,
    block: WorkloadRules,
    findings: MappingABC[str, Finding],
    provided_ids: Collection[str],
    collectors: MappingABC[str, Collector],
) -> WorkloadStatus:
    conditions = dict.fromkeys(
        (*block.ready, *(item for rule in block.rules for item in rule.when))
    )
    gaps = {
        condition: _gap(condition, findings.get(condition.finding), provided_ids, collectors)
        for condition in conditions
    }
    missing = {gap: None for condition in block.ready if (gap := gaps[condition]) is not None}
    fired = []
    for rule in block.rules:
        results = [
            _problem_result(condition, findings.get(condition.finding), gaps[condition])
            for condition in rule.when
        ]
        if False not in results:
            missing.update(
                dict.fromkeys(
                    gap for condition in rule.when if (gap := gaps[condition]) is not None
                )
            )
        if all(results):
            fired.append(rule)
    deciding = max(fired, key=lambda rule: STATUSES.index(rule.status), default=None)
    bundled_id = f"{workload}.licence_bundled_assigned"
    bundled = findings.get(bundled_id)
    ids = dict.fromkeys(condition.finding for condition in conditions)
    if bundled is not None and bundled.value is True:
        ids[bundled_id] = None
    evidence = tuple(findings[finding_id] for finding_id in ids if finding_id in findings)
    incomplete = tuple(missing)
    if deciding is not None:
        notes = tuple(rule for rule in fired if rule is not deciding)
        return WorkloadStatus(
            workload, deciding.status, None, incomplete, deciding, notes, evidence
        )
    if not incomplete and all(
        _matches_condition(condition, findings[condition.finding]) for condition in block.ready
    ):
        return WorkloadStatus(workload, "ready", None, (), None, (), evidence)
    code = _unknown_code(incomplete, bundled, provided_ids)
    return WorkloadStatus(workload, "unknown", code, incomplete, None, (), evidence)


def evaluate(
    findings: MappingABC[str, Finding],
    rule_set: StatusRuleSet,
    catalogue: Catalogue,
    *,
    collectors: MappingABC[str, Collector] | None = None,
) -> tuple[WorkloadStatus, ...]:
    provided_ids = {entry.id for entry in catalogue.findings if entry.provided != "no"}
    return tuple(
        _evaluate_workload(
            workload, rule_set.workloads[workload], findings, provided_ids, collectors or {}
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
