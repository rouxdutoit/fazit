# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass, replace
from itertools import groupby
from operator import attrgetter

from hypothesis import strategies as st

from fazit import PROJECT_NAME, __version__, rules
from fazit.catalogue import FindingEntry, load_catalogue
from fazit.i18n import SUPPORTED_LANGUAGES
from fazit.inputs import CurrentCosts, ScenarioInputs
from fazit.licences import load_service_plans
from fazit.model import (
    COLLECTOR_STATUSES,
    COVERAGE_KINDS,
    Collector,
    Coverage,
    Finding,
    Licences,
    Product,
    Scan,
    ServicePlan,
    ToolInfo,
)
from fazit.status import load_status_rules

CATALOGUE = load_catalogue()
PLANS = load_service_plans(CATALOGUE)
STATUS_RULES = load_status_rules(CATALOGUE)
ROSTERS = tuple(tuple(plans) for _, plans in groupby(PLANS, key=attrgetter("sku_guid")))
PROFILES = sorted(
    path.name.removesuffix(".yaml")
    for path in rules.rules_dir().joinpath("mappings").iterdir()
    if path.name.endswith(".yaml")
)
DAY = "2026-11-22"
EMPTY_SCAN = Scan("1.0", ToolInfo(PROJECT_NAME, __version__), DAY, "sample", (), (), None)
COUNTS = st.sampled_from((0, 1, 10**15)) | st.integers(0, 3000)
INTERVIEWS = sorted(CATALOGUE.provided_sources - {"inputs_yaml", "sample.inputs_yaml"})


@dataclass(frozen=True)
class Tenant:
    scan: Scan
    inputs: dict | None
    lang: str
    profile: str


def _collector(draw: st.DrawFn, collector_id: str, thorough: bool) -> Collector:
    status = "ok" if thorough else draw(st.sampled_from(COLLECTOR_STATUSES))
    reasons = {
        "ok": st.none(),
        "partial": st.just("coverage_partial"),
        "skipped": st.sampled_from(("collector_skipped", "permission_denied")),
    }
    reason = draw(reasons[status])
    permissions = draw(st.lists(st.sampled_from(sorted(CATALOGUE.permissions)), max_size=2))
    return Collector(collector_id, status, reason, tuple(permissions))


def _coverage(draw: st.DrawFn, total: int, *, inventory: bool = False) -> Coverage:
    kind = draw(st.sampled_from(COVERAGE_KINDS))
    if kind == "complete":
        return (
            Coverage(kind, total, 0, total) if inventory or draw(st.booleans()) else Coverage(kind)
        )
    if draw(st.booleans()):
        return Coverage(kind)
    if inventory:
        scanned = total
        total += draw(st.integers(0, 5))
    else:
        scanned = draw(st.integers(0, total))
    return Coverage(kind, scanned, draw(st.integers(0, total - scanned)), total)


def _finding(
    draw: st.DrawFn,
    entry: FindingEntry,
    collectors: dict[str, Collector],
    totals: dict[str, int],
) -> Finding | None:
    if not draw(st.booleans()):
        return None
    methods = sorted(pair for pair in entry.measured_by if pair[0] in collectors)
    measured = [pair for pair in methods if collectors[pair[0]].status != "skipped"]
    can_provide = entry.provided == "answer"
    provenance = draw(
        st.sampled_from(["unknown"] + ["measured"] * bool(measured) + ["provided"] * can_provide)
    )
    if provenance == "measured":
        methods = measured
    collector, source = draw(st.sampled_from(methods)) if methods else (None, None)
    if provenance == "unknown":
        reason = collectors[collector].reason if collector is not None else None
        return Finding(
            entry.id,
            entry.workload,
            None,
            entry.unit,
            provenance,
            collector,
            source,
            None,
            None,
            None,
            reason or "not_in_export",
        )

    related = totals.get(entry.coverage_total_from)
    coverage = None
    if provenance == "measured":
        coverage = _coverage(draw, draw(COUNTS) if related is None else related)
    else:
        collector, source = None, draw(st.sampled_from(INTERVIEWS))
    count = totals.get(entry.id)
    if entry.type == "boolean":
        value = draw(st.booleans())
    elif count is not None:
        value = count
    elif related is not None:
        limit = related if coverage is None or coverage.scanned is None else coverage.scanned
        value = draw(st.integers(0, limit))
    else:
        value = draw(COUNTS)
    return Finding(
        entry.id,
        entry.workload,
        value,
        entry.unit,
        provenance,
        collector,
        source,
        DAY,
        "2026-10-01/2026-10-31" if collector else None,
        coverage,
        None,
    )


def _licences(draw: st.DrawFn, collector: Collector | None) -> Licences | None:
    if collector is None or collector.status == "skipped" or not draw(st.booleans()):
        return None
    products = []
    all_unassigned = draw(st.booleans())
    for roster in draw(
        st.lists(st.sampled_from(ROSTERS), unique_by=lambda plans: plans[0].sku_guid, max_size=5)
    ):
        first = roster[0]
        purchased = draw(COUNTS)
        assigned = 0 if all_unassigned else draw(st.integers(0, purchased))
        plans = tuple(ServicePlan(plan.name, plan.guid) for plan in roster)
        products.append(Product(first.sku_part_number, first.sku_guid, purchased, assigned, plans))
    coverage = _coverage(draw, len(products), inventory=True)
    return Licences(
        collector.id,
        draw(st.sampled_from(sorted(CATALOGUE.licence_sources))),
        DAY,
        coverage,
        tuple(products),
    )


def _money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


AMOUNTS = (st.sampled_from((0, 1, 10**17 - 1)) | st.integers(0, 10**9)).map(_money)


def _fields(draw: st.DrawFn, fields: dict[str, st.SearchStrategy], thorough: bool) -> dict:
    if thorough:
        return draw(st.fixed_dictionaries(fields))
    return draw(st.fixed_dictionaries({}, optional=fields))


def _inputs(draw: st.DrawFn) -> dict | None:
    if not draw(st.booleans()):
        return None
    thorough = draw(st.booleans())
    quantities = {
        "users": COUNTS,
        "training_days_per_person": st.one_of(st.integers(0, 30), AMOUNTS),
        "training_staff": COUNTS,
        "parallel_running_months": st.integers(0, 60),
    }
    target_fields = {name: quantities.get(name, AMOUNTS) for name in vars(ScenarioInputs())}
    answers = [entry for entry in CATALOGUE.findings if entry.provided == "answer"]
    inputs = {
        "currency": "EUR",
        "organisation_name": "Synthetic Council",
        "amounts_are_invented": draw(st.booleans()),
        "answers_are_sample": draw(st.booleans()),
        "current_costs": _fields(draw, dict.fromkeys(vars(CurrentCosts()), AMOUNTS), thorough),
        "target_costs": {
            name: _fields(draw, target_fields, thorough) for name in ("partial_exit", "full_exit")
        },
        "provided_counts": _fields(
            draw, {entry.id: COUNTS for entry in answers if entry.type == "count"}, thorough
        ),
        "confirmations": _fields(
            draw,
            {entry.id: st.booleans() for entry in answers if entry.type == "boolean"},
            thorough,
        ),
    }
    if draw(st.booleans()):
        inputs["as_of"] = DAY
    if draw(st.booleans()):
        inputs["windows_only_software"] = [
            {"name": f"Records & Maps {index}", "users": users, "vendor_has_web_version": web}
            for index, (users, web) in enumerate(
                draw(st.lists(st.tuples(COUNTS, st.none() | st.booleans()), max_size=4))
            )
        ]
    return inputs


@st.composite
def tenants(draw: st.DrawFn) -> Tenant:
    lang = draw(st.sampled_from(SUPPORTED_LANGUAGES))
    profile = draw(st.sampled_from(PROFILES))
    inputs = _inputs(draw)
    thorough = draw(st.booleans())
    collectors = {
        name: _collector(draw, name, thorough)
        for name in sorted(CATALOGUE.collector_ids)
        if thorough or draw(st.booleans())
    }
    totals = {
        reference: draw(COUNTS)
        for reference in dict.fromkeys(
            entry.coverage_total_from for entry in CATALOGUE.findings if entry.coverage_total_from
        )
    }
    findings = tuple(
        finding
        for entry in CATALOGUE.findings
        if (finding := _finding(draw, entry, collectors, totals)) is not None
    )
    if inputs is not None:
        counts = inputs["provided_counts"]
        for finding in findings:
            entry = CATALOGUE.finding(finding.id)
            if (
                entry.provided == "answer"
                and type(finding.value) is int
                and finding.provenance == "measured"
                and finding.coverage.kind == "complete"
                and draw(st.booleans())
            ):
                conflicts = (0, finding.value + 1) if finding.value else (1,)
                counts[finding.id] = draw(st.sampled_from(conflicts))
    scan = replace(
        EMPTY_SCAN,
        collectors=tuple(collectors.values()),
        findings=findings,
        licences=_licences(draw, collectors.get("licences")),
    )
    return Tenant(scan, inputs, lang, profile)


@st.composite
def degraded_tenants(draw: st.DrawFn) -> tuple[Tenant, Tenant]:
    tenant = draw(tenants())
    scan = tenant.scan
    candidates = [
        *(row for row in scan.collectors if row.status != "skipped"),
        *(
            row
            for row in scan.findings
            if row.coverage is not None and row.coverage.kind == "complete"
        ),
    ]
    if not candidates:
        return tenant, tenant
    changed = draw(st.sampled_from(candidates), label="evidence to degrade")
    if isinstance(changed, Finding):
        kind = draw(st.sampled_from(("partial", "unknown")), label="evidence coverage")
        findings = tuple(
            replace(row, coverage=replace(changed.coverage, kind=kind))
            if row.id == changed.id
            else row
            for row in scan.findings
        )
        worse = replace(scan, findings=findings)
        return tenant, replace(tenant, scan=worse)

    failures = [("skipped", "collector_skipped"), ("skipped", "permission_denied")]
    if changed.status == "ok":
        failures.append(("partial", "coverage_partial"))
    status, reason = draw(st.sampled_from(failures), label="collector state")
    collectors = tuple(
        replace(row, status=status, reason=reason) if row.id == changed.id else row
        for row in scan.collectors
    )
    findings = tuple(
        replace(row, value=None, provenance="unknown", coverage=None, missing_reason=reason)
        if row.collector == changed.id and status == "skipped"
        else row
        for row in scan.findings
    )
    licences = scan.licences
    if licences is not None and licences.collector == changed.id and status == "skipped":
        licences = None
    worse = replace(scan, collectors=collectors, findings=findings, licences=licences)
    return tenant, replace(tenant, scan=worse)
