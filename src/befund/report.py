# SPDX-License-Identifier: AGPL-3.0-or-later
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import partial
from importlib.resources import files

from jinja2 import Environment, StrictUndefined

from . import PROJECT_NAME, REPOSITORY_URL, __version__
from .catalogue import Catalogue, load_catalogue
from .costs import CostLine, ScenarioResult, compute_scenarios
from .errors import InputError
from .i18n import SUPPORTED_LANGUAGES, Formatter, code_label, reason_text
from .inputs import Inputs, combine, empty_inputs, provided_findings
from .model import Coverage, Finding, FindingValue, Scan
from .parsing import read_text
from .rules import (
    STATUSES,
    classify_product,
    evaluate,
    evidence_conflicts,
    licence_findings,
    load_mapping,
    load_risky_file_types,
    load_service_plans,
    load_status_rules,
    mapping_need,
)

SECTION_ORDER = (
    "header",
    "found",
    "costs",
    "readiness",
    "moves",
    "attention",
    "path",
    "appendix",
    "footer",
)


def report_file_name(generated_at: str, *, lang: str) -> str:
    if lang not in SUPPORTED_LANGUAGES:
        raise InputError("unsupported_language", file=PROJECT_NAME, field="--lang")
    return f"report-{date.fromisoformat(generated_at[:10]).isoformat()}-{lang}.html"


def _coverage_text(
    coverage: Coverage | None, formatter: Formatter, *, provided: bool = False
) -> str:
    strings = formatter.strings
    if coverage is None:
        return strings["common"]["unavailable"]
    labels = strings["coverage"]
    parts = [labels[coverage.kind]]
    if coverage.scanned is not None and coverage.total is not None:
        key = "answers_of" if provided else "scanned_of"
        parts.append(
            labels[key].format(
                scanned=formatter.integer(coverage.scanned), total=formatter.integer(coverage.total)
            )
        )
    elif coverage.scanned is not None:
        key = "answers" if provided else "scanned"
        parts.append(labels[key].format(scanned=formatter.integer(coverage.scanned)))
    elif coverage.total is not None:
        parts.append(labels["total"].format(total=formatter.integer(coverage.total)))
    if coverage.failed is not None:
        parts.append(labels["failed"].format(failed=formatter.integer(coverage.failed)))
    return ", ".join(parts)


def _literal_text(value: FindingValue, formatter: Formatter) -> str:
    if isinstance(value, bool):
        return formatter.strings["common"]["yes" if value else "no"]
    return formatter.integer(value) if isinstance(value, int) else value


def _value_text(finding: Finding, formatter: Formatter) -> str:
    strings = formatter.strings
    value = finding.value
    if value is None:
        return strings["common"]["unavailable"]
    partial_coverage = finding.coverage is not None and finding.coverage.kind == "partial"
    if type(value) is int and finding.unit == "bytes":
        text = formatter.storage(value, lower_bound=partial_coverage)
    else:
        text = _literal_text(value, formatter)
        if finding.unit is not None:
            group = "unit_one" if type(value) is int and value == 1 else "units"
            text = f"{text} {code_label(strings, group, finding.unit)}"
    if type(value) is int and partial_coverage:
        key = "partial_positive" if value > 0 else "partial_zero"
        return strings["found"][key].format(value=text)
    return text


def _label(strings: dict, label: str) -> str:
    group, name = label.split(".", 1)
    return strings[group][name]


def _finding_labels(
    catalogue: Catalogue, strings: dict, workloads: dict[str, str]
) -> dict[str, str]:
    labels = {entry.id: _label(strings, entry.label) for entry in catalogue.findings}
    labels["licences.product_count"] = strings["licences"]["title"]
    for workload, label in workloads.items():
        for signal in ("add_on_assigned", "bundled_assigned"):
            labels[f"{workload}.licence_{signal}"] = strings["licences"][signal].format(
                workload=label
            )
    return labels


@dataclass(frozen=True)
class _CostTableBlock:
    id: str
    lines: tuple[tuple[str, tuple[CostLine | None, ...]], ...]
    totals: tuple[Decimal | None, ...]


def _cost_table_blocks(scenarios: tuple[ScenarioResult, ...]) -> tuple[_CostTableBlock, ...]:
    groups_by_scenario = ((result.running, *result.blocks) for result in scenarios)
    blocks = []
    for groups in zip(*groups_by_scenario, strict=True):
        scenario_lines = tuple({line.id: line for line in group.lines} for group in groups)
        ids = dict.fromkeys(id for lines in scenario_lines for id in lines)
        blocks.append(
            _CostTableBlock(
                groups[0].id,
                tuple((id, tuple(lines.get(id) for lines in scenario_lines)) for id in ids),
                tuple(group.total for group in groups),
            )
        )
    return tuple(blocks)


def _plain_amount(amount: Decimal | None) -> str:
    if amount is None:
        return "unknown"
    whole, _, fraction = f"{amount:f}".partition(".")
    fraction = fraction.rstrip("0")
    return f"{whole}.{fraction}" if fraction else whole


def render_report(
    scan: Scan,
    *,
    lang: str,
    profile: str = "opendesk",
    catalogue: Catalogue | None = None,
    provided: tuple[Finding, ...] = (),
    inputs: Inputs | None = None,
) -> str:
    formatter = Formatter(lang)
    strings = formatter.strings
    catalogue = catalogue if catalogue is not None else load_catalogue()
    checksums = {catalogue.file_name: catalogue.checksum} if catalogue.checksum else {}
    status_rules = load_status_rules(catalogue, checksums=checksums)
    plans = load_service_plans(catalogue, checksums=checksums)
    risky_kinds = load_risky_file_types(catalogue, checksums=checksums)
    mapping = load_mapping(profile, catalogue, checksums=checksums)
    scan_periods = sorted({item.period for item in scan.findings if item.period is not None})
    cost_inputs = inputs if inputs is not None else empty_inputs()
    scenarios = compute_scenarios(cost_inputs)
    if inputs is not None:
        provided += provided_findings(inputs, catalogue)
    scan, other_evidence = combine(scan, provided)
    derived = licence_findings(scan, plans, catalogue)
    products = () if scan.licences is None else scan.licences.products
    licences = [(product, classify_product(product, plans)) for product in products]
    workload_labels = {entry.id: _label(strings, entry.label) for entry in catalogue.workloads}
    by_id = {item.id: item for item in scan.findings + derived}
    alternatives = {item.id: item for item in other_evidence}
    conflicts = {item.id for item in other_evidence if evidence_conflicts(by_id[item.id], item)}
    statuses = evaluate(
        by_id,
        status_rules,
        catalogue,
        collectors={item.id: item for item in scan.collectors},
        alternatives=alternatives,
    )
    counts = Counter(row.status for row in statuses)
    move_evidence = {row.workload: [] for row in statuses}
    for finding in by_id.values():
        if finding.value is not None:
            move_evidence[finding.workload].append(finding)
    by_workload = {workload.id: [] for workload in catalogue.workloads}
    headlines = []
    software = []
    for entry in catalogue.findings:
        finding = by_id.get(entry.id)
        if finding is not None:
            by_workload[entry.workload].append((entry, finding))
        if entry.headline:
            headlines.append((entry, finding))
        if entry.provided in ("software_list", "software_list_without_web_version"):
            software.append((entry, finding))

    source = files("befund").joinpath("templates", "report.html.j2")
    template = Environment(autoescape=True, undefined=StrictUndefined).from_string(
        read_text(source)
    )
    return template.render(
        scan=scan,
        scan_periods=scan_periods,
        inputs=inputs,
        sample_inputs=cost_inputs.answers_are_sample,
        input_source=cost_inputs.answer_source,
        provided_sources=catalogue.provided_sources,
        scenarios=scenarios,
        cost_blocks=_cost_table_blocks(scenarios),
        current_costs=vars(cost_inputs.current_costs),
        target_costs=(vars(cost_inputs.partial_exit), vars(cost_inputs.full_exit)),
        cost_currency=cost_inputs.currency or "",
        plain_amount=_plain_amount,
        lang=lang,
        strings=strings,
        label=partial(_label, strings),
        code_label=partial(code_label, strings),
        reason_text=partial(reason_text, strings),
        value_text=partial(_value_text, formatter=formatter),
        literal_text=partial(_literal_text, formatter=formatter),
        coverage_text=partial(_coverage_text, formatter=formatter),
        format=formatter,
        workload_labels=workload_labels,
        finding_labels=_finding_labels(catalogue, strings, workload_labels),
        licences=licences,
        product_count=derived[0] if derived else None,
        statuses=statuses,
        status_counts=[(status, counts[status]) for status in STATUSES],
        status_rules=status_rules,
        mapping=mapping,
        status_by_workload={row.workload: row for row in statuses},
        move_evidence=move_evidence,
        mapping_need=mapping_need,
        mapping_gaps=[
            (item, by_id.get(item.need_finding) if item.need_finding else None)
            for item in mapping.functions
            if item.coverage == "not_available"
        ],
        risky_files=[(kind, by_id.get(kind.finding_id)) for kind in risky_kinds],
        software=software,
        alternatives=alternatives,
        conflicts=conflicts,
        unknown_findings=[finding for finding in by_id.values() if finding.provenance == "unknown"],
        skipped_collectors=[
            collector for collector in scan.collectors if collector.status == "skipped"
        ],
        checksums=checksums,
        headlines=headlines,
        groups=[(workload, by_workload[workload.id]) for workload in catalogue.workloads],
        project_name=PROJECT_NAME,
        repository_url=REPOSITORY_URL,
        tool_version=__version__,
    )
