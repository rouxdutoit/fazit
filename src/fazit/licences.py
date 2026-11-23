# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections.abc import Iterator, Mapping, MutableMapping
from dataclasses import asdict, dataclass, replace
from datetime import date
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType

from .catalogue import Catalogue, licence_name_key, sku_key
from .errors import InputError
from .model import (
    Collector,
    Coverage,
    Finding,
    Licences,
    Product,
    Scan,
    ServicePlan,
    same_collection_time,
)
from .parsing import parse_yaml
from .rules import read_rule_text
from .validation import Validator

_REFERENCE = re.compile(r"https://learn\.microsoft\.com/[^\s]+")
_SIGNALS = ("add_on", "bundled")
_PLAN_CLASSES = (*_SIGNALS, "no_workload")
PLAN_GAP_REASONS = (
    "licence_plan_list_incomplete",
    "licence_plan_list_missing",
    "licence_not_classified",
)
_PRODUCT_COUNT = "licences.product_count"


@dataclass(frozen=True)
class RegisteredPlan:
    sku_part_number: str
    sku_guid: str
    name: str
    guid: str
    workload: str | None
    signal: str
    reference_url: str
    checked_on: date
    note: Mapping[str, str] | None


@dataclass(frozen=True)
class ProductRoster:
    part_number: str
    sku_guid: str
    plans: Mapping[tuple[str, str], RegisteredPlan]
    plan_guids: frozenset[str]


@dataclass(frozen=True)
class ServicePlans:
    rosters: Mapping[tuple[str, str], ProductRoster]
    part_numbers: frozenset[str]
    sku_guids: frozenset[str]
    plan_names: Mapping[str, str]
    plan_guids: frozenset[str]
    sku_aliases: Mapping[tuple[str, str], ProductRoster]

    def __iter__(self) -> Iterator[RegisteredPlan]:
        return (plan for roster in self.rosters.values() for plan in roster.plans.values())

    def __bool__(self) -> bool:
        return bool(self.rosters)

    def roster_for(self, product: Product) -> ProductRoster | None:
        key = product.key
        return self.rosters.get(key) or self.sku_aliases.get(key)


type _PlanDetail = tuple[str, str | None, Mapping[str, str] | None]


def _plan_definitions(
    items: object, reader: Validator, catalogue: Catalogue
) -> dict[str, _PlanDetail]:
    plans: dict[str, _PlanDetail] = {}
    names: set[str] = set()
    for index, item in enumerate(reader.rows(items, "plans")):
        field = f"plans[{index}]"
        row = reader.fields(item, field, ("name", "guid", "workload"), ("note",))
        guid = reader.guid(row["guid"], f"{field}.guid")
        name = row["name"]
        if not catalogue.accepts_plan_name(name, guid):
            reader.fail(f"{field}.name")
        key = licence_name_key(name)
        if key in names:
            reader.fail(f"{field}.name", "duplicate_id")
        names.add(key)
        workload = row["workload"]
        if workload is not None:
            workload = reader.choice(workload, f"{field}.workload", catalogue.workload_ids)
        note = reader.bilingual(row["note"], f"{field}.note") if "note" in row else None
        plans[name] = (guid, workload, note)
    return plans


def _product_roster(
    product: dict,
    part_number: str,
    sku_guid: str,
    field: str,
    reader: Validator,
    definitions: Mapping[str, _PlanDetail],
    reference: str,
    checked_on: date,
) -> ProductRoster:
    plan_guids: set[str] = set()
    plans = {}
    for signal in _PLAN_CLASSES:
        members = reader.rows(product.get(signal, []), f"{field}.{signal}", allow_empty=True)
        for number, member in enumerate(members):
            path = f"{field}.{signal}[{number}]"
            name = reader.choice(member, path, definitions)
            guid, workload, note = definitions[name]
            if guid in plan_guids:
                reader.fail(path, "duplicate_id")
            if (signal == "no_workload") != (workload is None):
                reader.fail(path)
            plan_guids.add(guid)
            plans[licence_name_key(name), guid] = RegisteredPlan(
                part_number, sku_guid, name, guid, workload, signal, reference, checked_on, note
            )
    if not plan_guids:
        reader.fail(field)
    return ProductRoster(part_number, sku_guid, MappingProxyType(plans), frozenset(plan_guids))


def load_service_plans(
    catalogue: Catalogue,
    path: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> ServicePlans:
    reader, text = read_rule_text("service_plans.yaml", path)
    plans = _parse_service_plans(text, reader, catalogue)
    if checksums is not None:
        checksums[reader.file_name] = sha256(text.encode("utf-8")).hexdigest()
    return plans


@lru_cache(maxsize=2)
def _parse_service_plans(text: str, reader: Validator, catalogue: Catalogue) -> ServicePlans:
    data = parse_yaml(text, reader.file_name)
    root = reader.fields(data, "", ("reference_url", "checked_on", "plans", "products"))
    reference = reader.matches(root["reference_url"], "reference_url", _REFERENCE)
    checked_on = reader.calendar_date(root["checked_on"], "checked_on")
    definitions = _plan_definitions(root["plans"], reader, catalogue)
    rosters = {}
    sku_guids: set[str] = set()
    for index, item in enumerate(reader.rows(root["products"], "products")):
        field = f"products[{index}]"
        product = reader.fields(item, field, ("sku_part_number", "sku_guid"), _PLAN_CLASSES)
        sku_guid = reader.guid(product["sku_guid"], f"{field}.sku_guid")
        if sku_guid in sku_guids:
            reader.fail(f"{field}.sku_guid", "duplicate_id")
        sku_guids.add(sku_guid)
        part_number = product["sku_part_number"]
        if not catalogue.accepts_sku_part_number(part_number, sku_guid):
            reader.fail(f"{field}.sku_part_number")
        rosters[sku_key(part_number, sku_guid)] = _product_roster(
            product, part_number, sku_guid, field, reader, definitions, reference, checked_on
        )
    names = {
        name: plan.name for roster in rosters.values() for (name, _), plan in roster.plans.items()
    }
    by_guid = {roster.sku_guid: roster for roster in rosters.values()}
    aliases = {
        (name, guid): by_guid[guid]
        for name, guid in catalogue.sku_exceptions
        if guid in by_guid and (name, guid) not in rosters
    }
    return ServicePlans(
        MappingProxyType(rosters),
        frozenset(part for part, _ in rosters),
        frozenset(sku_guids),
        MappingProxyType(names),
        frozenset().union(*(roster.plan_guids for roster in rosters.values())),
        MappingProxyType(aliases),
    )


def classify_product(product: Product, plans: ServicePlans) -> tuple[RegisteredPlan | None, ...]:
    roster = plans.roster_for(product)
    matched = roster.plans if roster else {}
    return tuple(
        matched.get((licence_name_key(plan.name), plan.guid)) if plan.name is not None else None
        for plan in product.service_plans
    )


def _public_product(product: Product, plans: ServicePlans) -> Product:
    roster = plans.roster_for(product)
    if roster is None:
        return replace(
            product,
            sku_part_number=None,
            sku_guid=None,
            service_plans=(ServicePlan(None, None),) * len(product.service_plans),
        )
    # A registered half of a mismatched pair can still identify an affected workload.
    return replace(
        product,
        sku_part_number=roster.part_number,
        sku_guid=roster.sku_guid,
        service_plans=tuple(
            ServicePlan(
                plans.plan_names.get(licence_name_key(plan.name))
                if plan.name is not None
                else None,
                plan.guid if plan.guid in plans.plan_guids else None,
            )
            for plan in product.service_plans
        ),
    )


def scan_to_json(scan: Scan, *, plans: ServicePlans) -> str:
    if scan.licences is not None:
        products = tuple(_public_product(product, plans) for product in scan.licences.products)
        scan = replace(scan, licences=replace(scan.licences, products=products))
    data = asdict(scan)
    del data["dropped_count"]
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _licence_signals(
    products: tuple[Product, ...], plans: ServicePlans, file_name: str, *, incomplete: bool
) -> tuple[set[tuple[str, str]], str | None]:
    assigned: set[tuple[str, str]] = set()
    gaps: set[str] = set()
    for index, product in enumerate(products):
        roster = plans.roster_for(product)
        if roster is None:
            part, guid = sku_key(product.sku_part_number or "", product.sku_guid or "")
            if (guid in plans.sku_guids or part in plans.part_numbers) and (
                product.key is not None or not incomplete
            ):
                field = "sku_part_number" if guid in plans.sku_guids else "sku_guid"
                raise InputError(
                    "sku_identity_mismatch",
                    file=file_name,
                    field=f"licences.products[{index}].{field}",
                )
        elif not roster.plan_guids.issubset(plan.guid for plan in product.service_plans):
            # Missing plans still matter for known products with no assignments.
            gaps.add("licence_plan_list_incomplete")
        if not product.assigned:
            continue
        if not product.service_plans:
            gaps.add("licence_plan_list_missing")
        for match in classify_product(product, plans):
            if match is None:
                gaps.add("licence_not_classified")
            elif match.workload is not None:
                assigned.add((match.workload, match.signal))
    return assigned, next((code for code in PLAN_GAP_REASONS if code in gaps), None)


def _coverage_gap(coverage: Coverage | None) -> str | None:
    if coverage is None or coverage.kind == "unknown":
        return "coverage_unknown"
    return "coverage_partial" if coverage.kind == "partial" else None


def _inventory_evidence(
    licences: Licences, collector: Collector | None
) -> tuple[Finding, str | None]:
    coverage = licences.coverage
    coverage_gap = _coverage_gap(coverage)
    if collector and collector.status == "partial":
        if coverage.kind == "complete":
            coverage = replace(coverage, kind="partial")
        coverage_gap = collector.reason or "coverage_partial"
    count = len(licences.products)
    known_count = count > 0 or (
        coverage.kind == "complete" and collector is not None and collector.status == "ok"
    )
    return Finding(
        id=_PRODUCT_COUNT,
        workload="licences",
        value=count if known_count else None,
        unit="products",
        provenance="measured" if known_count else "unknown",
        collector=licences.collector,
        source=licences.source,
        collected_at=licences.collected_at,
        period=None,
        coverage=coverage,
        missing_reason=None if known_count else "licence_products_missing",
    ), coverage_gap


def _directory_cross_check(scan: Scan, licences: Licences) -> str | None:
    directory = scan.collector("directory")
    if directory is not None and directory.reason is not None:
        return directory.reason
    accounts = scan.finding("directory.licensed_user_count")
    if directory is None or accounts is None:
        return "not_in_scan"
    if accounts.missing_reason is not None:
        return accounts.missing_reason
    if (
        accounts.provenance != "measured"
        or type(accounts.value) is not int
        or accounts.period is not None
        or not same_collection_time(accounts.collected_at, licences.collected_at)
    ):
        return "licence_directory_unverified"
    if gap := _coverage_gap(accounts.coverage):
        return gap
    population = scan.directory_population
    if (
        population is None
        or population.coverage.kind != "complete"
        or not population.includes(accounts)
    ):
        return "licence_directory_unverified"
    # Only user SKUs have assigned seats.
    seats = [product.assigned for product in licences.products]
    if not max(seats, default=0) <= accounts.value <= sum(seats):
        return "licence_assignments_conflict"
    return None


def _assignment_findings(
    product_count: Finding,
    catalogue: Catalogue,
    assigned: set[tuple[str, str]],
    absence_gap: str | None,
    absence_collector: str,
) -> Iterator[Finding]:
    for workload in catalogue.workload_ids:
        for signal in _SIGNALS:
            value = (workload, signal) in assigned
            missing = None if value else absence_gap
            yield replace(
                product_count,
                id=f"{workload}.licence_{signal}_assigned",
                workload=workload,
                value=None if missing else value,
                unit=None,
                provenance="unknown" if missing else "measured",
                collector=absence_collector if missing else product_count.collector,
                missing_reason=missing,
            )


def licence_findings(
    scan: Scan, plans: ServicePlans, catalogue: Catalogue, *, file_name: str = "scan.json"
) -> tuple[Finding, ...]:
    licences = scan.licences
    if licences is None:
        return ()
    count, coverage_gap = _inventory_evidence(licences, scan.collector(licences.collector))
    assigned, classification_gap = _licence_signals(
        licences.products, plans, file_name, incomplete=coverage_gap is not None
    )
    absence_gap = count.missing_reason or classification_gap or coverage_gap
    absence_collector = licences.collector
    if coverage_gap is None:
        directory_gap = _directory_cross_check(scan, licences)
        if directory_gap == "licence_assignments_conflict":
            absence_gap = directory_gap
            count = replace(count, missing_reason=directory_gap)
        elif directory_gap is not None:
            if absence_gap is None:
                absence_gap, absence_collector = directory_gap, "directory"
            count = replace(count, missing_reason="licence_directory_unverified")
    return (
        count,
        *_assignment_findings(count, catalogue, assigned, absence_gap, absence_collector),
    )


def licence_finding_types(catalogue: Catalogue) -> dict[str, str]:
    return {
        _PRODUCT_COUNT: "count",
        **{
            f"{workload}.licence_{signal}_assigned": "boolean"
            for workload in catalogue.workload_ids
            for signal in _SIGNALS
        },
    }
