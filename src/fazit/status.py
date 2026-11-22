# SPDX-License-Identifier: AGPL-3.0-or-later
from collections import defaultdict
from collections.abc import Collection, Iterator, Mapping, MutableMapping
from dataclasses import dataclass, replace
from pathlib import Path
from string import Formatter
from types import MappingProxyType

from .catalogue import Catalogue, FindingEntry
from .evidence import evidence_conflicts, is_complete, provided_answers_conflict
from .licences import PLAN_GAP_REASONS, licence_finding_types
from .mappings import GAP_COVERAGE, FunctionMapping, TargetMapping
from .model import Collector, Finding, FindingValue
from .rules import read_rules
from .validation import RULE_ID, Validator, non_negative_integer

_OPERATORS = ("exists", "==", ">", ">=")
STATUSES = ("ready", "needs_work", "blocker", "unknown")
STEP_KINDS = ("clarify", "decide", "replace")


@dataclass(frozen=True)
class Condition:
    finding: str
    op: str
    value: FindingValue | None
    provenance: str | None = None
    accept_partial_true: bool = False


@dataclass(frozen=True)
class NextStep:
    kind: str
    text: Mapping[str, str]


@dataclass(frozen=True)
class StatusRule:
    id: str
    when: tuple[Condition, ...]
    status: str
    reason: Mapping[str, str]
    next_step: NextStep


@dataclass(frozen=True)
class WorkloadRules:
    ready: tuple[Condition, ...]
    ready_reason: Mapping[str, str]
    rules: tuple[StatusRule, ...]


@dataclass(frozen=True)
class TargetGapRule:
    id: str
    status: str
    reason: Mapping[str, str]
    next_step: NextStep


@dataclass(frozen=True)
class StatusRuleSet:
    workloads: Mapping[str, WorkloadRules]
    target_gaps: Mapping[str, TargetGapRule]
    file_name: str


@dataclass(frozen=True)
class MissingEvidence:
    finding_id: str
    reason_code: str
    collector: str | None


@dataclass(frozen=True)
class TransferGap:
    mapping: FunctionMapping
    finding: Finding | None
    need: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class WorkloadStatus:
    workload: str
    status: str
    reason_code: str | None
    missing: tuple[MissingEvidence, ...]
    deciding: StatusRule | None
    notes: tuple[StatusRule, ...]
    evidence: tuple[Finding, ...]
    transfer_gaps: tuple[TransferGap, ...] = ()

    @property
    def incomplete(self) -> bool:
        return bool(self.missing)


def _conditions(
    value: object, field: str, reader: Validator, types: Mapping[str, str]
) -> tuple[Condition, ...]:
    conditions = []
    for index, item in enumerate(reader.rows(value, field)):
        member = f"{field}[{index}]"
        row = reader.fields(
            item, member, ("finding", "op"), ("value", "provenance", "accept_partial_true")
        )
        finding_id = reader.choice(row["finding"], f"{member}.finding", types.keys())
        op = reader.choice(row["op"], f"{member}.op", _OPERATORS)
        kind = types[finding_id]
        literal = row.get("value")
        if op in (">", ">=") and kind == "boolean":
            reader.fail(f"{member}.op")
        if op == "exists":
            if "value" in row:
                reader.fail(f"{member}.value")
        elif kind == "boolean":
            if type(literal) is not bool:
                reader.fail(f"{member}.value")
        elif not non_negative_integer(literal):
            reader.fail(f"{member}.value")
        provenance = (
            reader.choice(row["provenance"], f"{member}.provenance", ("measured", "provided"))
            if "provenance" in row
            else None
        )
        accept_partial = row.get("accept_partial_true", False)
        if type(accept_partial) is not bool or (accept_partial and kind != "boolean"):
            reader.fail(f"{member}.accept_partial_true")
        conditions.append(Condition(finding_id, op, literal, provenance, accept_partial))
    return tuple(conditions)


def _next_step(value: object, field: str, reader: Validator) -> NextStep:
    row = reader.fields(value, field, ("kind", "en", "de"))
    kind = reader.choice(row["kind"], f"{field}.kind", STEP_KINDS)
    return NextStep(kind, reader.bilingual({"en": row["en"], "de": row["de"]}, field))


def _rule_id(value: object, field: str, reader: Validator, rule_ids: set[str]) -> str:
    rule_id = reader.matches(value, field, RULE_ID)
    if rule_id in rule_ids:
        reader.fail(field, "duplicate_id")
    rule_ids.add(rule_id)
    return rule_id


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
        row = reader.fields(item, member, ("id", "when", "status", "reason", "next_step"))
        rules.append(
            StatusRule(
                _rule_id(row["id"], f"{member}.id", reader, rule_ids),
                _conditions(row["when"], f"{member}.when", reader, types),
                reader.choice(row["status"], f"{member}.status", STATUSES[1:3]),
                reader.bilingual(row["reason"], f"{member}.reason"),
                _next_step(row["next_step"], f"{member}.next_step", reader),
            )
        )
    return WorkloadRules(conditions, reason, tuple(rules))


def _target_reason(value: object, field: str, reader: Validator) -> Mapping[str, str]:
    reason = reader.bilingual(value, field)
    for lang, text in reason.items():
        try:
            placeholders = {
                (name, spec, conversion)
                for _, name, spec, conversion in Formatter().parse(text)
                if name is not None
            }
        except ValueError:
            reader.fail(f"{field}.{lang}")
        if placeholders != {("profile", "", None), ("function", "", None)}:
            reader.fail(f"{field}.{lang}")
    return reason


def _target_gap_rules(
    value: object, reader: Validator, rule_ids: set[str]
) -> Mapping[str, TargetGapRule]:
    block = reader.fields(value, "target_gaps", GAP_COVERAGE)
    templates = {}
    for coverage in GAP_COVERAGE:
        field = f"target_gaps.{coverage}"
        row = reader.fields(block[coverage], field, ("id", "status", "reason", "next_step"))
        templates[coverage] = TargetGapRule(
            _rule_id(row["id"], f"{field}.id", reader, rule_ids),
            reader.choice(row["status"], f"{field}.status", ("needs_work",)),
            _target_reason(row["reason"], f"{field}.reason", reader),
            _next_step(row["next_step"], f"{field}.next_step", reader),
        )
    return MappingProxyType(templates)


def load_status_rules(
    catalogue: Catalogue,
    path: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> StatusRuleSet:
    reader, data = read_rules("status.yaml", path, checksums)
    root = reader.fields(data, "", ("workloads", "target_gaps"))
    workload_ids = catalogue.assessed_workload_ids
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
    target_gaps = _target_gap_rules(root["target_gaps"], reader, rule_ids)
    return StatusRuleSet(MappingProxyType(workloads), target_gaps, reader.file_name)


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
        and condition.accept_partial_true
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


def _mapping_gaps(
    mapping: TargetMapping, findings: Mapping[str, Finding], statuses: tuple[WorkloadStatus, ...]
) -> dict[str, list[TransferGap]]:
    missing: dict[str, list[str]] = defaultdict(list)
    for row in statuses:
        for gap in row.missing:
            missing[gap.finding_id].append(gap.reason_code)
    dispute_codes = ("confirmation_conflict", "provided_answers_conflict")
    gaps: dict[str, list[TransferGap]] = defaultdict(list)
    for item in mapping.functions:
        if item.coverage not in GAP_COVERAGE:
            continue
        finding = findings.get(item.need_finding) if item.need_finding else None
        need = "unknown"
        complete = is_complete(finding)
        confirmed_use = (
            finding is not None
            and finding.value is True
            and (complete or finding.provenance == "measured")
        )
        if confirmed_use or complete:
            need = "yes" if finding.value else "no"
        reasons = tuple(
            dict.fromkeys(
                code
                for code in missing.get(item.need_finding, ())
                if code != "answer_not_provided" or need == "unknown"
            )
        )
        if confirmed_use:
            reasons = tuple(code for code in reasons if code in dispute_codes)
        if reasons:
            need = "unknown"
        if need == "unknown" and not reasons:
            default = "answer_not_provided" if item.need_finding else "not_established"
            reasons = ((finding.missing_reason if finding else None) or default,)
        gaps[item.workload].append(TransferGap(item, finding, need, reasons))
    return gaps


def _target_rule(
    gap: TransferGap, template: TargetGapRule, profile: Mapping[str, str]
) -> StatusRule:
    finding = gap.finding
    assert finding is not None
    condition = (
        Condition(finding.id, "==", True)
        if finding.value is True
        else Condition(finding.id, ">", 0)
    )
    reason = {
        lang: text.format(profile=profile[lang], function=gap.mapping.microsoft[lang])
        for lang, text in template.reason.items()
    }
    suffix = gap.mapping.function.replace("_", "-")
    return StatusRule(
        f"{template.id}-{suffix}",
        (condition,),
        template.status,
        MappingProxyType(reason),
        template.next_step,
    )


def _apply_transfer_gaps(
    row: WorkloadStatus,
    gaps: tuple[TransferGap, ...],
    mapping: TargetMapping,
    templates: Mapping[str, TargetGapRule],
    bundled: Finding | None,
    provided_ids: Collection[str],
) -> WorkloadStatus:
    if not gaps:
        return row
    missing = list(row.missing)
    listed = {gap.finding_id for gap in missing}
    for gap in gaps:
        finding_id = gap.mapping.need_finding
        if gap.need == "unknown" and finding_id is not None and finding_id not in listed:
            finding = gap.finding
            collector = (
                finding.collector
                if finding is not None and finding.provenance == "measured"
                else None
            )
            missing.append(MissingEvidence(finding_id, gap.reasons[0], collector))
            listed.add(finding_id)
    row = replace(row, missing=tuple(missing), transfer_gaps=gaps)
    fired = tuple(
        _target_rule(gap, templates[gap.mapping.coverage], mapping.label)
        for gap in gaps
        if gap.need == "yes"
    )
    # An area's confirmed problem stays the deciding reason when the target adds work.
    if fired and row.deciding is not None:
        return replace(row, notes=(*row.notes, *fired))
    if fired:
        return replace(
            row, status=fired[0].status, reason_code=None, deciding=fired[0], notes=fired[1:]
        )
    # An unanswered need is missing evidence and cannot leave an area Ready.
    if row.status == "ready" and row.missing:
        return replace(
            row, status="unknown", reason_code=_unknown_code(row.missing, bundled, provided_ids)
        )
    return row


def evaluate(
    findings: Mapping[str, Finding],
    rule_set: StatusRuleSet,
    catalogue: Catalogue,
    mapping: TargetMapping,
    *,
    collectors: Mapping[str, Collector] | None = None,
    alternatives: Mapping[str, Finding] | None = None,
) -> tuple[WorkloadStatus, ...]:
    entries = {entry.id: entry for entry in catalogue.findings}
    alternatives = {} if alternatives is None else alternatives
    disputes = _observation_disputes(findings, alternatives)
    statuses = tuple(
        _evaluate_workload(
            workload,
            rule_set.workloads[workload],
            findings,
            entries,
            collectors or {},
            alternatives,
            disputes,
        )
        for workload in catalogue.assessed_workload_ids
    )
    gaps = _mapping_gaps(mapping, findings, statuses)
    provided_ids = {entry.id for entry in catalogue.findings if entry.provided != "no"}
    return tuple(
        _apply_transfer_gaps(
            row,
            tuple(gaps.get(row.workload, ())),
            mapping,
            rule_set.target_gaps,
            findings.get(f"{row.workload}.licence_bundled_assigned"),
            provided_ids,
        )
        for row in statuses
    )
