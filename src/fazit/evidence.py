# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import replace

from .catalogue import Catalogue, FindingEntry
from .inputs import Inputs, WindowsSoftware
from .model import Coverage, Finding, Scan


def is_complete(finding: Finding | None) -> bool:
    if finding is None or finding.value is None or finding.provenance == "unknown":
        return False
    if finding.coverage is None:
        return finding.provenance == "provided"
    return finding.coverage.kind == "complete"


def evidence_conflicts(first: Finding, second: Finding) -> bool:
    measured, provided = (first, second) if first.provenance == "measured" else (second, first)
    if not (
        measured.provenance == "measured"
        and measured.value is not None
        and provided.provenance == "provided"
        and is_complete(provided)
    ):
        return False
    if is_complete(measured):
        return measured.value != provided.value
    if type(measured.value) is bool:
        return measured.value and provided.value is False
    return measured.is_lower_bound and measured.value > provided.value


def provided_answers_conflict(first: Finding, second: Finding) -> bool:
    return first.provenance == second.provenance == "provided" and first.value != second.value


def select_evidence(recorded: Finding | None, supplied: Finding) -> Finding:
    if recorded is None or recorded.provenance == "unknown":
        return supplied
    if supplied.provenance == "unknown":
        return recorded
    if recorded.provenance == "measured":
        if is_complete(recorded):
            return recorded
        if recorded.is_lower_bound and (
            not is_complete(supplied) or evidence_conflicts(recorded, supplied)
        ):
            return recorded
    return supplied


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
