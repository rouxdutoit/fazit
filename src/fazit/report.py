# SPDX-License-Identifier: AGPL-3.0-or-later
import base64
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache, partial
from importlib.resources import files
from typing import Literal

from jinja2 import Environment, StrictUndefined, Template

from . import PROJECT_NAME, REPOSITORY_URL, __version__
from .catalogue import ROLES, Catalogue, FindingEntry, load_catalogue
from .costs import YEARS, CostGroup, CostLine, ScenarioResult, compute_scenarios
from .evidence import (
    combine,
    evidence_conflicts,
    provided_answers_conflict,
    provided_findings,
)
from .i18n import Formatter, check_language, code_label, plain_amount, reason_text
from .inputs import Inputs
from .licences import (
    RegisteredPlan,
    ServicePlans,
    classify_product,
    licence_finding_types,
    licence_findings,
    load_service_plans,
    scan_to_json,
)
from .mappings import COVERAGE_LADDER, FunctionMapping, TargetMapping, load_mapping
from .model import Collector, Coverage, Finding, FindingValue, Product, Scan
from .parsing import read_text
from .risky_files import load_risky_file_types
from .status import (
    MissingEvidence,
    StatusRuleSet,
    TransferGap,
    WorkloadStatus,
    evaluate,
    load_status_rules,
)

_DISPLAY_ORDER = ("blocker", "needs_work", "unknown", "ready")


def report_file_name(generated_at: str, *, lang: str) -> str:
    check_language(lang)
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
    return formatter.integer(value)


def _value_text(finding: Finding, formatter: Formatter) -> str:
    strings = formatter.strings
    value = finding.value
    if value is None:
        return strings["common"]["unavailable"]
    lower_bound = finding.is_lower_bound
    if type(value) is int and finding.unit == "bytes":
        text = formatter.storage(value, lower_bound=lower_bound)
    else:
        text = _literal_text(value, formatter)
        if finding.unit is not None:
            group = "unit_one" if type(value) is int and value == 1 else "units"
            text = f"{text} {code_label(strings, group, finding.unit)}"
    if lower_bound:
        return strings["found"]["partial_positive"].format(value=text)
    if (
        type(value) is int
        and value == 0
        and finding.coverage
        and finding.coverage.kind != "complete"
    ):
        return strings["found"]["partial_zero"].format(value=text)
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
    groups: tuple[CostGroup, ...]


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
                groups,
            )
        )
    return tuple(blocks)


def render_report(
    scan: Scan,
    *,
    lang: str,
    profile: str = "opendesk",
    catalogue: Catalogue | None = None,
    inputs: Inputs | None = None,
    scan_file_name: str = "scan.json",
) -> str:
    context, _ = _prepare_report(
        scan, lang, profile, catalogue, inputs, scan_file_name=scan_file_name
    )
    return _render_html(context)


def render_demo(
    scan: Scan, *, lang: str, profile: str, catalogue: Catalogue, inputs: Inputs
) -> tuple[str, str]:
    context, plans = _prepare_report(scan, lang, profile, catalogue, inputs)
    return _render_html(context), scan_to_json(scan, plans=plans)


@dataclass(frozen=True)
class _LicenceRow:
    id: str
    label: str
    purchased: int
    assigned: int
    plans: tuple[RegisteredPlan | None, ...]
    sku_guid: str | None


def _licence_rows(
    products: tuple[Product, ...], plans: ServicePlans, formatter: Formatter
) -> tuple[_LicenceRow, ...]:
    rosters = tuple(plans.rosters.get(product.key) for product in products)
    part_counts = Counter(roster.part_number.casefold() for roster in rosters if roster is not None)
    unregistered = 0
    rows = []
    for product, roster in zip(products, rosters, strict=True):
        guid = None
        if roster is None:
            unregistered += 1
            code = f"unregistered-{unregistered}"
            label = formatter.strings["licences"]["unregistered_product"].format(
                number=formatter.integer(unregistered)
            )
        else:
            label = code = roster.part_number
            if part_counts[code.casefold()] > 1:
                guid = roster.sku_guid
        rows.append(
            _LicenceRow(
                code,
                label,
                product.purchased,
                product.assigned,
                classify_product(product, plans),
                guid,
            )
        )
    return tuple(rows)


def _prepare_report(
    scan: Scan,
    lang: str,
    profile: str,
    catalogue: Catalogue | None,
    inputs: Inputs | None,
    *,
    scan_file_name: str = "scan.json",
) -> tuple[dict[str, object], ServicePlans]:
    if scan.licences is not None:
        scan.licences.check_coverage(scan_file_name)
    formatter = Formatter(lang)
    catalogue = catalogue if catalogue is not None else load_catalogue()
    checksums = {catalogue.file_name: catalogue.checksum} if catalogue.checksum else {}
    status_rules = load_status_rules(catalogue, checksums=checksums)
    plans = load_service_plans(catalogue, checksums=checksums)
    risky_kinds = load_risky_file_types(catalogue, checksums=checksums)
    mapping = load_mapping(profile, catalogue, checksums=checksums)
    sample_scan = scan.is_sample
    scan_periods = sorted({item.period for item in scan.findings if item.period is not None})
    provided = provided_findings(inputs, catalogue) if inputs is not None else ()
    scan, other_evidence = combine(scan, provided)
    derived = licence_findings(scan, plans, catalogue, file_name=scan_file_name)
    products = () if scan.licences is None else scan.licences.products
    by_id = {item.id: item for item in scan.findings + derived}
    context = dict(
        **_formatting_context(formatter, catalogue),
        **_cost_context(inputs),
        **_evidence_context(
            scan,
            by_id,
            other_evidence,
            status_rules,
            catalogue,
            mapping,
            lang=lang,
            strings=formatter.strings,
        ),
        lang=lang,
        scan=scan,
        sample_scan=sample_scan,
        scan_periods=scan_periods,
        licences=_licence_rows(products, plans, formatter),
        product_count=derived[0] if derived else None,
        licence_plan_list_incomplete=any(
            finding.missing_reason == "licence_plan_list_incomplete" for finding in derived
        ),
        mapping=mapping,
        risky_files=[(kind, by_id.get(kind.finding_id)) for kind in risky_kinds],
        checksums=checksums,
        project_name=PROJECT_NAME,
        repository_url=REPOSITORY_URL,
        tool_version=__version__,
    )
    return context, plans


def _ordered_transfer_gaps(
    mapping: TargetMapping, statuses: tuple[WorkloadStatus, ...]
) -> tuple[TransferGap, ...]:
    by_function = {gap.mapping.function: gap for row in statuses for gap in row.transfer_gaps}
    return tuple(
        by_function[item.function] for item in mapping.functions if item.function in by_function
    )


@dataclass(frozen=True)
class ScopeStatement:
    profile: str
    total: int
    by_coverage: tuple[tuple[str, int], ...]
    needed: tuple[tuple[str, str], ...]
    unknown_need: int
    reviewed_on: date | None


def scope_statement(
    mapping: TargetMapping, statuses: tuple[WorkloadStatus, ...], lang: str
) -> ScopeStatement | None:
    if not mapping.product_profile:
        return None
    counts = Counter(item.coverage for item in mapping.functions)
    gaps = _ordered_transfer_gaps(mapping, statuses)
    return ScopeStatement(
        profile=mapping.label[lang],
        total=len(mapping.functions),
        by_coverage=tuple((code, counts[code]) for code in COVERAGE_LADDER if code in counts),
        needed=tuple(
            (gap.mapping.microsoft[lang], f"transfer-gap-{gap.mapping.function}")
            for gap in gaps
            if gap.need == "yes"
        ),
        unknown_need=sum(gap.need == "unknown" for gap in gaps),
        reviewed_on=mapping.reviewed_on,
    )


def _evidence_counts(
    observations: Iterable[Finding],
    rule_evidence: tuple[Finding, ...],
    alternatives: Mapping[str, Finding],
) -> dict[str, int]:
    distinct = {finding.id: finding for finding in observations}
    distinct.update((finding.id, finding) for finding in rule_evidence)
    counts = Counter(finding.provenance for finding in distinct.values())
    counts.update(
        alternatives[finding_id].provenance for finding_id in distinct if finding_id in alternatives
    )
    return {kind: counts[kind] for kind in ("measured", "provided", "unknown")}


def _target_functions(row: WorkloadStatus, mapping: TargetMapping) -> tuple[FunctionMapping, ...]:
    needed = {gap.mapping.function for gap in row.transfer_gaps if gap.need == "yes"}
    functions = (item for item in mapping.functions if item.workload == row.workload)
    return tuple(sorted(functions, key=lambda item: item.function not in needed)[:2])


@dataclass(frozen=True)
class _SummaryOpenArea:
    workload: str
    finding_id: str | None
    fix: str | None


@dataclass(frozen=True)
class _SummaryRows:
    blockers: tuple[WorkloadStatus, ...]
    open_areas: tuple[_SummaryOpenArea, ...]


def _summary_rows(
    statuses: tuple[WorkloadStatus, ...], catalogue: Catalogue, strings: dict
) -> _SummaryRows:
    open_areas = []
    for row in statuses:
        if row.status == "unknown" or row.incomplete:
            first_gap = row.missing[0] if row.missing else None
            code = row.reason_code or (first_gap.reason_code if first_gap else "not_established")
            gap = next((item for item in row.missing if item.reason_code == code), first_gap)
            _, fix = reason_text(strings, code)
            finding_id = gap.finding_id if gap else None
            if code == "answer_not_provided" and finding_id:
                entry = catalogue.finding(finding_id)
                if _finding_input_key(entry):
                    fix = None
            open_areas.append(_SummaryOpenArea(row.workload, finding_id, fix))
    return _SummaryRows(
        blockers=tuple(row for row in statuses if row.status == "blocker"),
        open_areas=tuple(open_areas),
    )


@dataclass(frozen=True)
class _OpenItem:
    id: str
    kind: Literal["finding", "area", "collector"]
    areas: tuple[str, ...]
    owner: str | None
    reasons: tuple[str, ...]
    unknown: bool = False
    gap: bool = False


@dataclass(frozen=True)
class _OpenPoint:
    key: str
    collector: str | None
    input_key: str | None
    items: tuple[_OpenItem, ...]
    owners: tuple[str, ...]
    reasons: tuple[str, ...]


def _finding_input_key(entry: FindingEntry | None) -> str | None:
    if entry is None or entry.provided == "no":
        return None
    if entry.provided in ("software_list", "software_list_without_web_version"):
        return "windows_only_software"
    if entry.type in ("boolean", "count"):
        group = "confirmations" if entry.type == "boolean" else "provided_counts"
        return f"{group}.{entry.id}"
    return None


def _open_finding_items(
    finding_id: str,
    entry: FindingEntry | None,
    unknown: Finding | None,
    gaps: list[tuple[str, MissingEvidence]],
    open_areas: set[str],
) -> Iterator[tuple[str, _OpenItem]]:
    input_key = _finding_input_key(entry)
    finding_key = f"finding.{finding_id}"
    requests: dict[str, list[tuple[str, MissingEvidence]]] = defaultdict(list)
    unknown_key = None
    if unknown is not None:
        unknown_key = input_key or (
            f"collector.{unknown.collector}" if unknown.collector else finding_key
        )
        requests[unknown_key] = []
    for area, gap in gaps:
        key = input_key or (f"collector.{gap.collector}" if gap.collector else finding_key)
        requests[key].append((area, gap))

    for key, missing in requests.items():
        areas = dict.fromkeys(area for area, _ in missing)
        reasons = dict.fromkeys(gap.reason_code for _, gap in missing)
        is_unknown = unknown is not None and key == unknown_key
        if unknown is not None and is_unknown:
            reasons.setdefault(unknown.missing_reason or "not_established", None)
            if not areas and unknown.workload in open_areas:
                areas[unknown.workload] = None
        yield (
            key,
            _OpenItem(
                finding_id,
                "finding",
                tuple(areas),
                entry.owner if entry else "licence_management",
                tuple(reasons),
                unknown=is_unknown,
                gap=bool(missing),
            ),
        )


def _open_point(key: str, items: list[_OpenItem], catalogue: Catalogue) -> _OpenPoint:
    group, _, name = key.partition(".")
    collector = name if group == "collector" else None
    input_key = None if group in ("area", "collector", "finding") else key
    owners = {item.owner for item in items if item.owner}
    if collector and not owners:
        owners = {
            entry.owner
            for entry in catalogue.findings
            if any(method == collector for method, _ in entry.measured_by)
        }
        if not owners:
            owners.add("licence_management" if collector == "licences" else "it_team")
    return _OpenPoint(
        key,
        collector,
        input_key,
        tuple(items),
        tuple(role for role in ROLES if role in owners),
        tuple(dict.fromkeys(code for item in items for code in item.reasons)),
    )


def _open_points(
    statuses: tuple[WorkloadStatus, ...],
    by_id: Mapping[str, Finding],
    alternatives: Mapping[str, Finding],
    catalogue: Catalogue,
    collectors: tuple[Collector, ...],
) -> tuple[_OpenPoint, ...]:
    entries = {entry.id: entry for entry in catalogue.findings}
    first_in_area = {}
    for entry in entries.values():
        first_in_area.setdefault(entry.workload, entry)
    unknown = {
        finding.id: finding
        for finding in (*alternatives.values(), *by_id.values())
        if finding.provenance == "unknown"
    }
    gaps: dict[str, list[tuple[str, MissingEvidence]]] = defaultdict(list)
    for row in statuses:
        for gap in row.missing:
            gaps[gap.finding_id].append((row.workload, gap))

    groups: dict[str, list[_OpenItem]] = defaultdict(list)
    order = {}
    finding_ids = (*entries, *licence_finding_types(catalogue))
    positions = {finding_id: index for index, finding_id in enumerate(finding_ids)}
    open_areas = {row.workload for row in statuses if row.status != "ready"}
    for finding_id in finding_ids:
        for key, item in _open_finding_items(
            finding_id,
            entries.get(finding_id),
            unknown.get(finding_id),
            gaps[finding_id],
            open_areas,
        ):
            groups[key].append(item)
            order.setdefault(key, positions[finding_id])
    for index, row in enumerate(statuses):
        if row.status == "unknown" and not row.missing:
            key = f"area.{row.workload}"
            first = first_in_area.get(row.workload)
            groups[key].append(
                _OpenItem(
                    row.workload,
                    "area",
                    (row.workload,),
                    first.owner if first else "it_team",
                    (row.reason_code or "not_established",),
                )
            )
            order[key] = positions[first.id] if first else len(finding_ids) + index
    for collector in collectors:
        if collector.status == "skipped":
            groups[f"collector.{collector.id}"].append(
                _OpenItem(
                    collector.id,
                    "collector",
                    (),
                    None,
                    (collector.reason or "collector_skipped",),
                )
            )
    last = len(finding_ids) + len(statuses)
    return tuple(
        _open_point(key, groups[key], catalogue)
        for key in sorted(groups, key=lambda key: order.get(key, last))
    )


@dataclass(frozen=True)
class _PathAction:
    kind: str
    text: str


def _area_actions(
    row: WorkloadStatus, status_rules: StatusRuleSet, lang: str, strings: dict
) -> Iterator[_PathAction]:
    functions: dict[str, list[str]] = defaultdict(list)
    for gap in row.transfer_gaps:
        if gap.need == "yes":
            functions[gap.mapping.coverage].append(gap.mapping.microsoft[lang])

    fired_steps = {rule.id: rule.next_step for rule in (row.deciding, *row.notes) if rule}
    for step in fired_steps.values():
        # The evaluator attaches the template's action to each fired transfer rule.
        coverage = next(
            (code for code, rule in status_rules.target_gaps.items() if step is rule.next_step),
            None,
        )
        if coverage is None:
            yield _PathAction(step.kind, step.text[lang])
        elif names := functions.pop(coverage, None):
            text = strings["path"]["transfer_actions"][coverage].format(functions=", ".join(names))
            yield _PathAction(step.kind, text)


def _next_steps(
    status_groups: list[tuple[str, tuple[WorkloadStatus, ...]]],
    status_rules: StatusRuleSet,
    lang: str,
    strings: dict,
) -> tuple[dict[str, list[_PathAction]], dict[str, list[_PathAction]]]:
    staying: dict[str, list[_PathAction]] = defaultdict(list)
    moving: dict[str, list[_PathAction]] = defaultdict(list)
    for status, rows in status_groups:
        if status not in ("blocker", "needs_work"):
            continue
        for row in rows:
            for action in _area_actions(row, status_rules, lang, strings):
                group = moving if action.kind == "replace" else staying
                group[row.workload].append(action)
    return staying, moving


def _evidence_context(
    scan: Scan,
    by_id: dict[str, Finding],
    other_evidence: tuple[Finding, ...],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    mapping: TargetMapping,
    *,
    lang: str,
    strings: dict,
) -> dict[str, object]:
    alternatives = {item.id: item for item in other_evidence}
    statuses = evaluate(
        by_id,
        status_rules,
        catalogue,
        mapping,
        collectors={item.id: item for item in scan.collectors},
        alternatives=alternatives,
    )
    counts = Counter(row.status for row in statuses)
    status_groups = [
        (status, tuple(row for row in statuses if row.status == status))
        for status in _DISPLAY_ORDER
        if counts[status]
    ]
    staying_steps, move_steps = _next_steps(status_groups, status_rules, lang, strings)
    observations = [(entry, by_id.get(entry.id)) for entry in catalogue.findings]
    by_workload = {workload.id: [] for workload in catalogue.workloads}
    for entry, finding in observations:
        if finding is not None:
            by_workload[entry.workload].append((entry, finding))

    return dict(
        alternatives=alternatives,
        conflicts={item.id for item in other_evidence if evidence_conflicts(by_id[item.id], item)},
        answer_conflicts={
            item.id for item in other_evidence if provided_answers_conflict(by_id[item.id], item)
        },
        statuses=statuses,
        status_counts=[(status, counts[status]) for status in _DISPLAY_ORDER],
        status_groups=status_groups,
        area_count=len(catalogue.assessed_workload_ids),
        summary_rows=_summary_rows(statuses, catalogue, strings),
        status_rules=status_rules,
        status_by_workload={row.workload: row for row in statuses},
        mapping_gaps=[
            (gap.mapping, gap.finding, gap.need, gap.reasons)
            for gap in _ordered_transfer_gaps(mapping, statuses)
        ],
        scope_statement=scope_statement(mapping, statuses, lang),
        open_points=_open_points(statuses, by_id, alternatives, catalogue, scan.collectors),
        staying_steps=staying_steps,
        move_steps=move_steps,
        headlines=[row for row in observations if row[0].headline],
        catalogue_evidence=by_workload,
        inventory_workloads=tuple(
            workload.id for workload in catalogue.workloads if not workload.assessed
        ),
        evidence_counts={
            row.workload: _evidence_counts(
                (finding for _, finding in by_workload[row.workload]), row.evidence, alternatives
            )
            for row in statuses
        },
        target_functions={row.workload: _target_functions(row, mapping) for row in statuses},
        software=[
            row
            for row in observations
            if row[0].provided in ("software_list", "software_list_without_web_version")
        ],
    )


def _missing_cost_paths(scenarios: tuple[ScenarioResult, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(path for result in scenarios for path in result.missing_inputs))


@dataclass(frozen=True)
class _CostComparison:
    direction: Literal["less", "more", "same", "sub_cent", "unknown"]
    amount: Fraction | None


def _cost_comparison(difference: Fraction | None) -> _CostComparison:
    if difference is None:
        return _CostComparison("unknown", None)
    amount = abs(difference)
    if amount == 0:
        return _CostComparison("same", amount)
    if plain_amount(amount) == "0.00":
        return _CostComparison("sub_cent", amount)
    return _CostComparison("less" if difference < 0 else "more", amount)


@dataclass(frozen=True)
class _BreakEven:
    amount: Fraction
    entered: Fraction
    none: bool


def _break_even(result: ScenarioResult, operations_per_year: Decimal | None) -> _BreakEven | None:
    if result.difference_to_stay is None or operations_per_year is None:
        return None
    entered = Fraction(operations_per_year)
    amount = entered - result.difference_to_stay / YEARS
    return _BreakEven(amount, entered, none=amount < 0)


@dataclass(frozen=True)
class _CostTile:
    result: ScenarioResult
    comparison: _CostComparison
    known_blocks: Fraction | None
    break_even: _BreakEven | None


def _known_block_sum(result: ScenarioResult) -> Fraction | None:
    amounts = [
        group.total
        for group in (result.running, *result.blocks)
        if group.lines and group.total is not None
    ]
    return sum(amounts, start=Fraction(0)) if amounts else None


def _cost_tiles(scenarios: tuple[ScenarioResult, ...], inputs: Inputs) -> tuple[_CostTile, ...]:
    operations = (
        None,
        inputs.partial_exit.operations_per_year,
        inputs.full_exit.operations_per_year,
    )
    return tuple(
        _CostTile(
            result,
            _cost_comparison(result.difference_to_stay),
            _known_block_sum(result),
            _break_even(result, entered),
        )
        for result, entered in zip(scenarios, operations, strict=True)
    )


@dataclass(frozen=True)
class _CostChartRow:
    tile: _CostTile
    blocks: tuple[CostGroup, ...]
    unknown_blocks: tuple[str, ...]
    share: str | None


def _cost_chart_rows(tiles: tuple[_CostTile, ...]) -> tuple[_CostChartRow, ...]:
    largest = max(
        (total for tile in tiles if (total := tile.result.total) is not None),
        default=Fraction(0),
    )
    rows = []
    for tile in tiles:
        result = tile.result
        blocks = (result.running, *result.blocks)
        unknown = tuple(block.id for block in blocks if block.total is None)
        share = None
        if result.total is not None:
            ratio = result.total / largest if largest else Fraction(0)
            share = f"{ratio:.4f}"
        rows.append(_CostChartRow(tile, blocks, unknown, share))
    return tuple(rows)


def _cost_context(inputs: Inputs | None) -> dict[str, object]:
    cost_inputs = inputs if inputs is not None else Inputs()
    scenarios = compute_scenarios(cost_inputs)
    tiles = _cost_tiles(scenarios, cost_inputs)
    current_costs = vars(cost_inputs.current_costs)
    target_costs = (vars(cost_inputs.partial_exit), vars(cost_inputs.full_exit))
    has_cost_inputs = any(
        value is not None for fields in (current_costs, *target_costs) for value in fields.values()
    )
    return dict(
        inputs=inputs,
        sample_inputs=cost_inputs.answers_are_sample,
        input_source=cost_inputs.answer_source,
        scenarios=scenarios,
        cost_blocks=_cost_table_blocks(scenarios),
        cost_tiles=tiles,
        cost_chart_rows=_cost_chart_rows(tiles) if has_cost_inputs else (),
        missing_cost_paths=_missing_cost_paths(scenarios),
        current_costs=current_costs,
        target_costs=target_costs,
        cost_currency=cost_inputs.currency or "",
        plain_amount=plain_amount,
    )


def _formatting_context(formatter: Formatter, catalogue: Catalogue) -> dict[str, object]:
    strings = formatter.strings
    workload_labels = {entry.id: _label(strings, entry.label) for entry in catalogue.workloads}
    return dict(
        strings=strings,
        provided_sources=catalogue.provided_sources,
        label=partial(_label, strings),
        code_label=partial(code_label, strings),
        reason_text=partial(reason_text, strings),
        value_text=partial(_value_text, formatter=formatter),
        literal_text=partial(_literal_text, formatter=formatter),
        coverage_text=partial(_coverage_text, formatter=formatter),
        format=formatter,
        workload_labels=workload_labels,
        workload_categories={
            entry.id: entry.category for entry in catalogue.workloads if entry.assessed
        },
        category_labels={entry.id: _label(strings, entry.label) for entry in catalogue.categories},
        categories=catalogue.categories,
        finding_labels=_finding_labels(catalogue, strings, workload_labels),
    )


_ICONS = (
    "check-circle",
    "warning",
    "report",
    "help",
    "chevron-right",
    "circle",
    "contrast",
    "code",
    "cancel",
)
_FONTS = ("figtree-latin", "geist-mono-latin")
_ICON_PATH = re.compile(r'<path d="([^"<>]+)"/>')


@lru_cache(maxsize=1)
def _assets() -> dict[str, dict[str, str]]:
    # Embed the assets so the report stays one file.
    package = files("fazit")
    fonts = {
        name: base64.b64encode(package.joinpath("fonts", f"{name}.woff2").read_bytes()).decode()
        for name in _FONTS
    }
    icons = {}
    for name in _ICONS:
        match = _ICON_PATH.search(package.joinpath("icons", f"{name}.svg").read_text("utf-8"))
        if match is None:
            raise RuntimeError(f"Icon {name} has no single path.")
        icons[name] = match[1]
    return {"fonts": fonts, "icons": icons}


def _render_html(context: dict[str, object]) -> str:
    source = files("fazit").joinpath("templates", "report.html.j2")
    html = _compile_template(read_text(source)).render(**context, **_assets()).strip()
    return "\n".join(line.rstrip(" \t") for line in html.split("\n")) + "\n"


@lru_cache(maxsize=1)
def _compile_template(text: str) -> Template:
    return Environment(autoescape=True, undefined=StrictUndefined).from_string(text)
