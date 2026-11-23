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
    DirectoryPopulation,
    Finding,
    Licences,
    Product,
    Scan,
    ServicePlan,
    ToolInfo,
)
from fazit.status import load_status_rules
from fazit.validation import MAX_COUNT

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
STAMP = f"{DAY}T09:00:00Z"
EMPTY_SCAN = Scan("1.0", ToolInfo(PROJECT_NAME, __version__), STAMP, "sample", (), (), None)
COUNTS = st.sampled_from((0, 1, MAX_COUNT)) | st.integers(0, 3000)
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
    can_provide = entry.provided != "no"
    provenance = draw(
        st.sampled_from(["unknown"] + ["measured"] * bool(measured) + ["provided"] * can_provide)
    )
    if provenance == "measured":
        methods = measured
    collector, source = draw(st.sampled_from(methods)) if methods else (None, None)
    related = totals.get(entry.coverage_total_from)
    count = totals.get(entry.id)
    coverage = collected_at = period = scanned = None
    if provenance == "measured":
        scope = related if related is not None else count
        if scope is None:
            scope = draw(COUNTS)
        coverage = _coverage(draw, scope)
        scanned = 0 if scope == 0 else coverage.scanned
        collected_at = STAMP
        if entry.workload != "directory":
            period = "2026-10-01/2026-10-31"
        if scanned == 0 and coverage.kind != "complete":
            provenance = "unknown"
    elif provenance == "provided":
        collector, source = None, draw(st.sampled_from(INTERVIEWS))
        collected_at = STAMP

    reason = None
    if provenance == "unknown":
        value = None
        reason = (
            collectors[collector].reason if collector is not None else None
        ) or "not_in_export"
    elif entry.type == "boolean":
        value = scanned != 0 and draw(st.booleans())
    else:
        bounds = [draw(COUNTS) if count is None else count]
        if related is not None:
            bounds.append(related)
        if entry.subset_of:
            bounds.append(sum(totals[parent] for parent in entry.subset_of))
        if entry.requires_population and totals[entry.requires_population] == 0:
            bounds.append(0)
        if scanned is not None and (
            scanned == 0 or (entry.type == "count" and not entry.aggregate)
        ):
            bounds.append(scanned)
        value = min(bounds)
    return Finding(
        entry.id,
        entry.workload,
        value,
        entry.unit,
        provenance,
        collector,
        source,
        collected_at,
        period,
        coverage,
        reason,
    )


def _licences(draw: st.DrawFn, collector: Collector | None, *, complete: bool) -> Licences | None:
    if collector is None or collector.status == "skipped" or not (complete or draw(st.booleans())):
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
    count = len(products)
    coverage = (
        Coverage("complete", count, 0, count)
        if complete
        else _coverage(draw, count, inventory=True)
    )
    return Licences(
        collector.id,
        draw(st.sampled_from(sorted(CATALOGUE.licence_sources))),
        STAMP,
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
        "training_days_per_person": COUNTS | st.integers(0, 10**9).map(_money),
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
    counts = inputs["provided_counts"]
    for entry in answers:
        if entry.id in counts and entry.subset_of and entry.subset_of <= counts.keys():
            counts[entry.id] = min(
                counts[entry.id], sum(counts[parent] for parent in entry.subset_of)
            )
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
    census = thorough and draw(st.booleans())
    collectors = {
        name: _collector(draw, name, thorough and not (census and name == "licences"))
        for name in sorted(CATALOGUE.collector_ids)
        if thorough or draw(st.booleans())
    }
    populations = {parent for entry in CATALOGUE.findings for parent in entry.subset_of}
    populations.update(
        entry.coverage_total_from for entry in CATALOGUE.findings if entry.coverage_total_from
    )
    populations.update(
        entry.requires_population for entry in CATALOGUE.findings if entry.requires_population
    )
    totals = {reference: draw(COUNTS) for reference in sorted(populations)}
    findings = [
        finding
        for entry in CATALOGUE.findings
        if (finding := _finding(draw, entry, collectors, totals)) is not None
    ]
    licences = _licences(draw, collectors.get("licences"), complete=census)
    population = None
    if census:
        products = licences.products if licences is not None else ()
        licensed = max((product.assigned for product in products), default=0)
        total = draw(st.integers(licensed, min(MAX_COUNT, licensed + 5)))
        guests = draw(st.just(0) | st.integers(0, total))
        coverage = Coverage("complete", total, 0, total)
        population = DirectoryPopulation("directory", STAMP, coverage)
        counts = {
            "directory.user_count": total - guests,
            "directory.guest_count": guests,
            "directory.licensed_user_count": licensed,
        }
        review = "directory.account_list_reviewed"
        census_ids = {*counts, review}
        findings = [finding for finding in findings if finding.id not in census_ids]
        findings.extend(
            Finding(
                key,
                "directory",
                value,
                "users",
                "measured",
                "directory",
                "sample.directory",
                STAMP,
                None,
                coverage,
                None,
            )
            for key, value in counts.items()
        )
        if inputs is None:
            inputs = {"provided_counts": {}, "confirmations": {}}
        inputs["confirmations"][review] = True
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
                conflicts = [
                    count
                    for count in (0, finding.value + 1)
                    if count != finding.value and count <= MAX_COUNT
                ]
                counts[finding.id] = draw(st.sampled_from(conflicts))
    scan = replace(
        EMPTY_SCAN,
        collectors=tuple(collectors.values()),
        findings=tuple(findings),
        licences=licences,
        directory_population=population,
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
    if scan.licences is not None and scan.licences.coverage.kind == "complete":
        candidates.append(scan.licences)
    if scan.directory_population is not None and draw(st.booleans()):
        candidates = [
            row
            for row in candidates
            if isinstance(row, Licences)
            or row.id in {"licences", "directory", "directory.licensed_user_count"}
        ]
    if not candidates:
        return tenant, tenant
    changed = draw(st.sampled_from(candidates), label="evidence to degrade")
    if isinstance(changed, Licences):
        kind = draw(st.sampled_from(("partial", "unknown")), label="inventory coverage")
        degraded = replace(changed, coverage=replace(changed.coverage, kind=kind))
        return tenant, replace(tenant, scan=replace(scan, licences=degraded))
    if isinstance(changed, Finding):
        kind = draw(st.sampled_from(("partial", "unknown")), label="evidence coverage")
        coverage = replace(changed.coverage, kind=kind)
        degraded = replace(changed, coverage=coverage)
        if coverage.scanned == 0:
            degraded = replace(
                degraded, provenance="unknown", value=None, missing_reason=f"coverage_{kind}"
            )
        findings = tuple(degraded if row.id == changed.id else row for row in scan.findings)
        worse = replace(scan, findings=findings)
        return tenant, replace(tenant, scan=worse)

    if changed.id == "licences" and draw(st.booleans(), label="drop licence collector"):
        collectors = tuple(row for row in scan.collectors if row.id != changed.id)
        return tenant, replace(tenant, scan=replace(scan, collectors=collectors, licences=None))

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
