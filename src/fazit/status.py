# SPDX-License-Identifier: AGPL-3.0-or-later
from collections.abc import Collection, Iterator, Mapping, MutableMapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from .catalogue import Catalogue, FindingEntry
from .evidence import evidence_conflicts, is_complete, provided_answers_conflict
from .licences import PLAN_GAP_REASONS, licence_finding_types
from .model import Collector, Finding, FindingValue
from .rules import read_rules
from .validation import RULE_ID, Validator, non_negative_integer

_OPERATORS = ("exists", "==", ">", ">=")
STATUSES = ("ready", "needs_work", "blocker", "unknown")


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
    reason: Mapping[str, str]


@dataclass(frozen=True)
class WorkloadRules:
    ready: tuple[Condition, ...]
    ready_reason: Mapping[str, str]
    rules: tuple[StatusRule, ...]


@dataclass(frozen=True)
class StatusRuleSet:
    workloads: Mapping[str, WorkloadRules]
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


def _conditions(
    value: object, field: str, reader: Validator, types: Mapping[str, str]
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
        elif kind == "boolean":
            if type(literal) is not bool:
                reader.fail(f"{member}.value")
        elif kind not in ("count", "bytes") or not non_negative_integer(literal):
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
    reader: Validator,
    types: Mapping[str, str],
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
        rule_id = reader.matches(row["id"], f"{member}.id", RULE_ID)
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
    reader, data = read_rules("status.yaml", path, checksums)
    root = reader.fields(data, "$", ("workloads",))
    workload_ids = catalogue.workload_ids
    blocks = reader.fields(root["workloads"], "workloads", workload_ids)
    types = {entry.id: entry.type for entry in catalogue.findings}
    types.update(licence_finding_types(catalogue))
    rule_ids: set[str] = set()
    workloads = {
        workload: _workload_rules(
            blocks[workload], f"workloads.{workload}", reader, types, rule_ids
        )
        for workload in workload_ids
    }
    return StatusRuleSet(MappingProxyType(workloads), reader.file_name)


def _skipped_gap(
    finding: Finding | None, collectors: Mapping[str, Collector]
) -> MissingEvidence | None:
    if finding is None or finding.collector is None:
        return None
    collector = collectors.get(finding.collector)
    if collector is not None and collector.status == "skipped":
        return MissingEvidence(
            finding.id, finding.missing_reason or "collector_skipped", collector.id
        )
    return None


def _observation_disputes(
    findings: Mapping[str, Finding],
    alternatives: Mapping[str, Finding],
) -> dict[str, MissingEvidence]:
    disputes = {}
    for finding_id, alternative in alternatives.items():
        primary = findings.get(finding_id)
        if primary is None:
            continue
        if provided_answers_conflict(primary, alternative):
            disputes[finding_id] = MissingEvidence(finding_id, "provided_answers_conflict", None)
        elif evidence_conflicts(primary, alternative):
            disputes[finding_id] = MissingEvidence(finding_id, "confirmation_conflict", None)
    return disputes


def _collector_gaps(
    finding_ids: Collection[str],
    entries: Mapping[str, FindingEntry],
    collectors: Mapping[str, Collector],
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
    collectors: Mapping[str, Collector],
) -> MissingEvidence | None:
    expected_answer = condition.provenance == "provided" or (
        condition.provenance is None and condition.finding in provided_ids
    )
    if skipped := _skipped_gap(finding, collectors):
        return skipped
    collector_id = finding.collector if finding else None
    if finding is None:
        code = "answer_not_provided" if expected_answer else "not_in_scan"
    elif finding.missing_reason is not None:
        code = finding.missing_reason
    elif finding.provenance == "unknown":
        code = "not_established"
    elif condition.provenance is not None and condition.provenance != finding.provenance:
        code = "answer_not_provided" if expected_answer else "not_in_scan"
        collector_id = None
    elif is_complete(finding):
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
    if condition.provenance not in (None, finding.provenance):
        return None
    if (
        gap.reason_code in ("coverage_partial", "coverage_unknown")
        and finding.id.endswith(".licence_add_on_assigned")
        and finding.value is True
    ):
        return _matches_condition(condition, finding)
    if (
        gap.reason_code
        in ("coverage_partial", "coverage_unknown", "answer_not_provided", "confirmation_conflict")
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
        *PLAN_GAP_REASONS,
        "provided_answers_conflict",
        "confirmation_conflict",
    ):
        if any(gap.reason_code == code for gap in gaps):
            return code
    if bundled is not None and bundled.value is True and is_complete(bundled):
        if any(gap.finding_id in provided_ids for gap in gaps):
            return "licensed_use_not_measured"
    return gaps[0].reason_code if gaps else "not_established"


type _ConditionResult = tuple[bool | None, MissingEvidence | None]


def _condition_results(
    conditions: Collection[Condition],
    findings: Mapping[str, Finding],
    alternatives: Mapping[str, Finding],
    provided_ids: Collection[str],
    collectors: Mapping[str, Collector],
    disputes: Mapping[str, MissingEvidence],
) -> dict[Condition, _ConditionResult]:
    results = {}
    for condition in conditions:
        evidence = alternatives.get(condition.finding)
        if evidence is None or evidence.provenance != condition.provenance:
            evidence = findings.get(condition.finding)
        gap = disputes.get(condition.finding) or _gap(condition, evidence, provided_ids, collectors)
        results[condition] = _problem_result(condition, evidence, gap), gap
    return results


def _matching_rules(
    block: WorkloadRules, results: Mapping[Condition, _ConditionResult]
) -> tuple[list[StatusRule], dict[MissingEvidence, None]]:
    missing = dict.fromkeys(
        gap for condition in block.ready if (gap := results[condition][1]) is not None
    )
    fired = []
    for rule in block.rules:
        matches = [results[condition] for condition in rule.when]
        if any(match is False for match, _ in matches):
            continue
        missing.update(dict.fromkeys(gap for _, gap in matches if gap is not None))
        if all(match for match, _ in matches):
            fired.append(rule)
    return fired, missing


def _evaluate_workload(
    workload: str,
    block: WorkloadRules,
    findings: Mapping[str, Finding],
    entries: Mapping[str, FindingEntry],
    collectors: Mapping[str, Collector],
    alternatives: Mapping[str, Finding],
    disputes: Mapping[str, MissingEvidence],
) -> WorkloadStatus:
    conditions = dict.fromkeys(
        (*block.ready, *(item for rule in block.rules for item in rule.when))
    )
    ids = dict.fromkeys(condition.finding for condition in conditions)
    provided_ids = {item for item in ids if item in entries and entries[item].provided != "no"}
    results = _condition_results(
        conditions, findings, alternatives, provided_ids, collectors, disputes
    )
    fired, missing = _matching_rules(block, results)
    deciding = max(fired, key=lambda rule: STATUSES.index(rule.status), default=None)
    bundled_id = f"{workload}.licence_bundled_assigned"
    bundled = findings.get(bundled_id)
    for finding_id in ids:
        if skipped := _skipped_gap(alternatives.get(finding_id), collectors):
            missing[skipped] = None
    missing.update(
        dict.fromkeys(
            gap
            for finding_id, gap in disputes.items()
            if finding_id in ids or findings[finding_id].workload == workload
        )
    )
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
    if not incomplete and all(results[condition][0] for condition in block.ready):
        return WorkloadStatus(workload, "ready", None, (), None, (), evidence)
    code = _unknown_code(incomplete, bundled, provided_ids)
    return WorkloadStatus(workload, "unknown", code, incomplete, None, (), evidence)


def evaluate(
    findings: Mapping[str, Finding],
    rule_set: StatusRuleSet,
    catalogue: Catalogue,
    *,
    collectors: Mapping[str, Collector] | None = None,
    alternatives: Mapping[str, Finding] | None = None,
) -> tuple[WorkloadStatus, ...]:
    entries = {entry.id: entry for entry in catalogue.findings}
    alternatives = {} if alternatives is None else alternatives
    disputes = _observation_disputes(findings, alternatives)
    return tuple(
        _evaluate_workload(
            workload,
            rule_set.workloads[workload],
            findings,
            entries,
            collectors or {},
            alternatives,
            disputes,
        )
        for workload in catalogue.workload_ids
    )
