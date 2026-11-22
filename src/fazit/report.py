# SPDX-License-Identifier: AGPL-3.0-or-later
import base64
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from functools import lru_cache, partial
from importlib.resources import files

from jinja2 import Environment, StrictUndefined, Template

from . import PROJECT_NAME, REPOSITORY_URL, __version__
from .catalogue import Catalogue, load_catalogue
from .costs import CostGroup, CostLine, ScenarioResult, compute_scenarios
from .evidence import (
    combine,
    evidence_conflicts,
    is_complete,
    provided_answers_conflict,
    provided_findings,
)
from .i18n import Formatter, check_language, code_label, plain_amount, reason_text
from .inputs import Inputs
from .licences import (
    RegisteredPlan,
    ServicePlans,
    classify_product,
    licence_findings,
    load_service_plans,
    scan_to_json,
)
from .mappings import FunctionMapping, TargetMapping, load_mapping
from .model import Coverage, Finding, FindingValue, Product, Scan
from .parsing import read_text
from .risky_files import load_risky_file_types
from .status import STATUSES, StatusRuleSet, WorkloadStatus, evaluate, load_status_rules


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
        **_evidence_context(scan, by_id, other_evidence, status_rules, catalogue, mapping),
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


def _mapping_gaps(
    mapping: TargetMapping, by_id: dict[str, Finding], statuses: tuple[WorkloadStatus, ...]
) -> list[tuple[FunctionMapping, Finding | None, str, tuple[str, ...]]]:
    missing: dict[str, list[str]] = defaultdict(list)
    for row in statuses:
        for gap in row.missing:
            missing[gap.finding_id].append(gap.reason_code)
    dispute_codes = ("confirmation_conflict", "provided_answers_conflict")
    gaps = []
    for item in mapping.functions:
        if item.coverage != "not_available":
            continue
        finding = by_id.get(item.need_finding) if item.need_finding else None
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
        if item.need_if_positive and need != "yes":
            count = by_id.get(item.need_if_positive)
            disputes = tuple(
                code for code in dispute_codes if code in missing[item.need_if_positive]
            )
            if disputes:
                finding, need, reasons = count, "unknown", disputes
            elif count is not None and type(count.value) is int and count.value > 0:
                if need == "no":
                    need, reasons = "unknown", ("desktop_requirements_conflict",)
                elif finding is None or finding.value is None:
                    finding, need, reasons = count, "yes", ()
        if need == "unknown" and not reasons:
            default = "answer_not_provided" if item.need_if_positive else "not_established"
            reasons = ((finding.missing_reason if finding else None) or default,)
        gaps.append((item, finding, need, reasons))
    return gaps


def _evidence_context(
    scan: Scan,
    by_id: dict[str, Finding],
    other_evidence: tuple[Finding, ...],
    status_rules: StatusRuleSet,
    catalogue: Catalogue,
    mapping: TargetMapping,
) -> dict[str, object]:
    alternatives = {item.id: item for item in other_evidence}
    statuses = evaluate(
        by_id,
        status_rules,
        catalogue,
        collectors={item.id: item for item in scan.collectors},
        alternatives=alternatives,
    )
    counts = Counter(row.status for row in statuses)
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
        status_counts=[(status, counts[status]) for status in STATUSES],
        status_rules=status_rules,
        status_by_workload={row.workload: row for row in statuses},
        mapping_gaps=_mapping_gaps(mapping, by_id, statuses),
        unknown_findings=[finding for finding in by_id.values() if finding.provenance == "unknown"],
        skipped_collectors=[
            collector for collector in scan.collectors if collector.status == "skipped"
        ],
        headlines=[row for row in observations if row[0].headline],
        groups=[(workload, by_workload[workload.id]) for workload in catalogue.workloads],
        software=[
            row
            for row in observations
            if row[0].provided in ("software_list", "software_list_without_web_version")
        ],
    )


def _cost_context(inputs: Inputs | None) -> dict[str, object]:
    cost_inputs = inputs if inputs is not None else Inputs()
    scenarios = compute_scenarios(cost_inputs)
    return dict(
        inputs=inputs,
        sample_inputs=cost_inputs.answers_are_sample,
        input_source=cost_inputs.answer_source,
        scenarios=scenarios,
        cost_blocks=_cost_table_blocks(scenarios),
        current_costs=vars(cost_inputs.current_costs),
        target_costs=(vars(cost_inputs.partial_exit), vars(cost_inputs.full_exit)),
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


_ICONS = ("check-circle", "warning", "report", "help", "chevron-right")
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
