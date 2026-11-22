# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
import re
from collections.abc import Collection
from dataclasses import asdict, dataclass, replace
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Never
from uuid import UUID

from . import PROJECT_NAME
from .catalogue import Catalogue, FindingEntry, sku_key
from .errors import InputError
from .parsing import FieldNames, parse_json, read_text, reject_at_signs

if TYPE_CHECKING:
    from .rules import ServicePlan as RegisteredServicePlan

SUPPORTED_SCHEMA_MAJOR = 1
SOURCE_KINDS = ("sample", "import", "live")
COLLECTOR_STATUSES = ("ok", "partial", "skipped")
PROVENANCES = ("measured", "provided", "unknown")
COVERAGE_KINDS = ("complete", "partial", "unknown")

_SCHEMA_VERSION = re.compile(r"[0-9]{1,8}\.[0-9]{1,8}")
_TOOL_VERSION = re.compile(r"[0-9]{1,8}(?:\.[0-9]{1,8}){1,2}")
_DATE = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
_TIMESTAMP = re.compile(
    rf"{_DATE}(?:T[0-9]{{2}}:[0-9]{{2}}(?::[0-9]{{2}}(?:[.,][0-9]+)?)?"
    r"(?:Z|[+-][0-9]{2}(?::?[0-5][0-9])?)?)?"
)
_FRACTIONAL_SECONDS = re.compile(r"[.,]([0-9]+)")
_PERIOD = re.compile(rf"{_DATE}/{_DATE}")
_IDENTIFIER = re.compile(r"[A-Za-z0-9_]{1,64}")
_SCAN_FIELDS = (
    "schema_version",
    "tool",
    "generated_at",
    "source_kind",
    "collectors",
    "findings",
    "licences",
)
_TOOL_FIELDS = ("name", "version")
_COLLECTOR_REQUIRED = ("id", "status", "permissions_used")
_COLLECTOR_OPTIONAL = ("reason",)
_COVERAGE_COUNTS = ("scanned", "failed", "total")
_FINDING_FIELDS = (
    "id",
    "workload",
    "value",
    "unit",
    "provenance",
    "collector",
    "source",
    "collected_at",
    "period",
    "coverage",
    "missing_reason",
)
_LICENCE_FIELDS = ("collector", "source", "collected_at", "coverage", "products")
_PRODUCT_REQUIRED = ("purchased", "assigned")
_PRODUCT_OPTIONAL = ("sku_part_number", "sku_guid", "service_plans")
_SERVICE_PLAN_FIELDS = ("name", "guid")
_SCAN_FIELD_NAMES: FieldNames = {
    (): _SCAN_FIELDS,
    ("tool",): _TOOL_FIELDS,
    ("collectors", None): (*_COLLECTOR_REQUIRED, *_COLLECTOR_OPTIONAL),
    ("findings", None): _FINDING_FIELDS,
    ("findings", None, "coverage"): ("kind", *_COVERAGE_COUNTS),
    ("licences",): _LICENCE_FIELDS,
    ("licences", "coverage"): ("kind", *_COVERAGE_COUNTS),
    ("licences", "products", None): (*_PRODUCT_REQUIRED, *_PRODUCT_OPTIONAL),
    ("licences", "products", None, "service_plans", None): _SERVICE_PLAN_FIELDS,
}

type FindingValue = int | bool


def _timestamp_after(stamp: str, reference: str) -> bool:
    time, limit = datetime.fromisoformat(stamp), datetime.fromisoformat(reference)
    if len(stamp) == 10 or len(reference) == 10:
        return time.date() > limit.date()
    if time.tzinfo is None or limit.tzinfo is None:
        time, limit = time.replace(tzinfo=None), limit.replace(tzinfo=None)
    if time != limit:
        return time > limit
    # datetime truncates fractional seconds to microseconds.
    fraction, cutoff = (
        match[1].rstrip("0") if (match := _FRACTIONAL_SECONDS.search(value)) else ""
        for value in (stamp, reference)
    )
    return fraction > cutoff


@dataclass(frozen=True)
class ToolInfo:
    name: str
    version: str


@dataclass(frozen=True)
class Collector:
    id: str
    status: str
    reason: str | None
    permissions_used: tuple[str, ...]


@dataclass(frozen=True)
class Coverage:
    kind: str
    scanned: int | None = None
    failed: int | None = None
    total: int | None = None


@dataclass(frozen=True)
class Finding:
    id: str
    workload: str
    value: FindingValue | None
    unit: str | None
    provenance: str
    collector: str | None
    source: str | None
    collected_at: str | None
    period: str | None
    coverage: Coverage | None
    missing_reason: str | None

    @property
    def is_lower_bound(self) -> bool:
        if type(self.value) is not int or self.value <= 0 or self.coverage is None:
            return False
        if self.provenance == "measured":
            return self.coverage.kind != "complete"
        return self.provenance == "provided" and self.coverage.kind == "partial"


@dataclass(frozen=True)
class ServicePlan:
    name: str | None
    guid: str | None


@dataclass(frozen=True)
class Product:
    sku_part_number: str | None
    sku_guid: str | None
    purchased: int
    assigned: int
    service_plans: tuple[ServicePlan, ...]

    @property
    def key(self) -> tuple[str, str] | None:
        if self.sku_part_number is None or self.sku_guid is None:
            return None
        return sku_key(self.sku_part_number, self.sku_guid)


@dataclass(frozen=True)
class Licences:
    collector: str
    source: str
    collected_at: str
    coverage: Coverage
    products: tuple[Product, ...]

    def check_coverage(self, file_name: str) -> None:
        count = len(self.products)
        if self.coverage.kind == "complete" and self.coverage != Coverage(
            "complete", scanned=count, failed=0, total=count
        ):
            raise InputError("invalid_licence_coverage", file=file_name, field="licences.coverage")
        for field, bound in (("scanned", self.coverage.scanned), ("total", self.coverage.total)):
            if bound is not None and count > bound:
                raise InputError(
                    "licence_products_exceed_coverage",
                    file=file_name,
                    field=f"licences.coverage.{field}",
                )


@dataclass(frozen=True)
class Scan:
    schema_version: str
    tool: ToolInfo
    generated_at: str
    source_kind: str
    collectors: tuple[Collector, ...]
    findings: tuple[Finding, ...]
    licences: Licences | None
    dropped_count: int = 0

    @property
    def is_sample(self) -> bool:
        return (
            self.source_kind == "sample"
            or any(
                finding.source and finding.source.startswith("sample.") for finding in self.findings
            )
            or (self.licences is not None and self.licences.source.startswith("sample."))
        )

    def finding(self, finding_id: str) -> Finding | None:
        return next((finding for finding in self.findings if finding.id == finding_id), None)

    def collector(self, collector_id: str) -> Collector | None:
        return next(
            (collector for collector in self.collectors if collector.id == collector_id), None
        )


class _ScanReader:
    def __init__(self, file_name: str, catalogue: Catalogue) -> None:
        self.file_name = file_name
        self.catalogue = catalogue
        self.dropped_count = 0

    def fail(self, field: str, code: str = "invalid_field", **details: object) -> Never:
        raise InputError(code, file=self.file_name, field=field or "$", **details)

    def fields(
        self,
        value: object,
        field: str,
        *,
        required: tuple[str, ...],
        optional: tuple[str, ...] = (),
    ) -> dict:
        if not isinstance(value, dict):
            self.fail(field)
        for name in required:
            if name not in value:
                self.fail(f"{field}.{name}" if field else name, "missing_field")
        self.dropped_count += len(value.keys() - {*required, *optional})
        return value

    def list(self, value: object, field: str) -> list[object]:
        if not isinstance(value, list):
            self.fail(field)
        return value

    def code(self, value: object, field: str, allowed: Collection[str]) -> str:
        if not isinstance(value, str) or value not in allowed:
            self.fail(field, "invalid_code")
        return value

    def count(self, value: object, field: str) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            self.fail(field)
        return value

    def matches(self, value: object, field: str, pattern: re.Pattern[str]) -> str:
        if not isinstance(value, str) or not pattern.fullmatch(value):
            self.fail(field)
        return value

    def timestamp(self, value: object, field: str) -> str:
        stamp = self.matches(value, field, _TIMESTAMP)
        try:
            datetime.fromisoformat(stamp)
        except ValueError:
            raise InputError("invalid_field", file=self.file_name, field=field) from None
        return stamp

    def period(self, value: object, field: str) -> str:
        interval = self.matches(value, field, _PERIOD)
        start, end = interval.split("/")
        try:
            first, last = date.fromisoformat(start), date.fromisoformat(end)
        except ValueError:
            raise InputError("invalid_field", file=self.file_name, field=field) from None
        if last < first:
            self.fail(field)
        return interval

    def schema_version(self, value: object) -> str:
        version = self.matches(value, "schema_version", _SCHEMA_VERSION)
        if int(version.split(".", 1)[0]) != SUPPORTED_SCHEMA_MAJOR:
            raise InputError(
                "schema_version",
                file=self.file_name,
                field="schema_version",
                found=version,
                supported=f"{SUPPORTED_SCHEMA_MAJOR}.x",
            )
        return version

    def tool(self, value: object) -> ToolInfo:
        row = self.fields(value, "tool", required=_TOOL_FIELDS)
        return ToolInfo(
            name=self.code(row["name"], "tool.name", (PROJECT_NAME,)),
            version=self.matches(row["version"], "tool.version", _TOOL_VERSION),
        )

    def collectors(self, value: object) -> dict[str, Collector]:
        collectors: dict[str, Collector] = {}
        for index, item in enumerate(self.list(value, "collectors")):
            field = f"collectors[{index}]"
            row = self.fields(
                item, field, required=_COLLECTOR_REQUIRED, optional=_COLLECTOR_OPTIONAL
            )
            collector_id = self.code(row["id"], f"{field}.id", self.catalogue.collector_ids)
            if collector_id in collectors:
                self.fail(f"{field}.id", "duplicate_id")
            status = self.code(row["status"], f"{field}.status", COLLECTOR_STATUSES)
            reason = row.get("reason")
            if (status == "ok") != (reason is None):
                self.fail(f"{field}.reason", "collector_reason_mismatch")
            if reason is not None:
                reason = self.code(reason, f"{field}.reason", self.catalogue.reason_codes)
            permissions = self.list(row["permissions_used"], f"{field}.permissions_used")
            collectors[collector_id] = Collector(
                collector_id,
                status,
                reason,
                tuple(
                    self.code(code, f"{field}.permissions_used[{i}]", self.catalogue.permissions)
                    for i, code in enumerate(permissions)
                ),
            )
        return collectors

    def coverage(self, value: object, field: str) -> Coverage:
        row = self.fields(value, field, required=("kind",), optional=_COVERAGE_COUNTS)
        kind = self.code(row["kind"], f"{field}.kind", COVERAGE_KINDS)
        scanned, failed, total = (
            None if row.get(name) is None else self.count(row[name], f"{field}.{name}")
            for name in _COVERAGE_COUNTS
        )
        if total is not None and (scanned or 0) + (failed or 0) > total:
            self.fail(field, "invalid_coverage")
        if kind == "complete" and any(count is not None for count in (scanned, failed, total)):
            if failed != 0 or scanned is None or total is None or scanned != total:
                self.fail(field, "invalid_coverage")
        return Coverage(kind, scanned, failed, total)

    def finding_value(self, value: object, field: str, entry: FindingEntry) -> FindingValue:
        if entry.type == "boolean":
            if not isinstance(value, bool):
                self.fail(field)
            return value
        return self.count(value, field)

    def finding(
        self, item: object, field: str, entry: FindingEntry, collectors: dict[str, Collector]
    ) -> Finding:
        row = self.fields(item, field, required=_FINDING_FIELDS)
        if row["workload"] != entry.workload:
            self.fail(f"{field}.workload")
        if row["unit"] != entry.unit:
            self.fail(f"{field}.unit", "invalid_code")
        provenance = self.code(row["provenance"], f"{field}.provenance", PROVENANCES)
        collector = row["collector"]
        if collector is not None:
            collector = self.code(collector, f"{field}.collector", collectors)
        self.check_evidence(row, field, provenance, collectors.get(collector))
        value, source, reason = row["value"], row["source"], row["missing_reason"]
        if source is not None:
            source = self.code(source, f"{field}.source", self.catalogue.source_codes)
        self.check_finding_source(entry, field, collector, source)
        collected_at, period, coverage = row["collected_at"], row["period"], row["coverage"]
        return Finding(
            id=entry.id,
            workload=entry.workload,
            unit=entry.unit,
            provenance=provenance,
            value=None if value is None else self.finding_value(value, f"{field}.value", entry),
            collector=collector,
            source=source,
            collected_at=None
            if collected_at is None
            else self.timestamp(collected_at, f"{field}.collected_at"),
            period=None if period is None else self.period(period, f"{field}.period"),
            coverage=None if coverage is None else self.coverage(coverage, f"{field}.coverage"),
            missing_reason=None
            if reason is None
            else self.code(reason, f"{field}.missing_reason", self.catalogue.reason_codes),
        )

    def check_finding_source(
        self, entry: FindingEntry, field: str, collector: str | None, source: str | None
    ) -> None:
        if source in ("inputs_yaml", "sample.inputs_yaml"):
            self.fail(f"{field}.source", "inputs_source_in_scan")
        if collector is not None:
            allowed = {code for method, code in entry.measured_by if method == collector}
            if not allowed:
                self.fail(f"{field}.collector", "invalid_evidence_source", finding=entry.id)
        else:
            allowed = self.catalogue.provided_sources if entry.provided != "no" else frozenset()
        if source is not None and source not in allowed:
            self.fail(f"{field}.source", "invalid_evidence_source", finding=entry.id)

    def check_evidence(
        self, row: dict, field: str, provenance: str, collector: Collector | None
    ) -> None:
        if provenance == "unknown":
            required, empty = ("missing_reason",), ("value",)
        elif provenance == "provided":
            required, empty = ("value", "source"), ("collector", "coverage", "missing_reason")
        else:
            if collector is None or collector.status == "skipped":
                self.fail(f"{field}.collector", "invalid_collector")
            required = ("value", "source", "collected_at", "coverage")
            empty = ("missing_reason",)
        for name in required:
            if row[name] is None:
                self.fail(f"{field}.{name}", "missing_field")
        for name in empty:
            if row[name] is not None:
                self.fail(f"{field}.{name}")

    def check_finding_dates(self, finding: Finding, field: str, generated_at: str) -> None:
        if (collected_at := finding.collected_at) is None:
            return
        if finding.period is not None and finding.period[-10:] > collected_at[:10]:
            self.fail(f"{field}.period", "period_after_collection")
        if _timestamp_after(collected_at, generated_at):
            self.fail(f"{field}.collected_at", "collection_after_scan")

    def findings(
        self, value: object, collectors: dict[str, Collector], generated_at: str
    ) -> tuple[Finding, ...]:
        findings = []
        subsets: list[tuple[str, Finding, str]] = []
        seen: set[str] = set()
        for index, item in enumerate(self.list(value, "findings")):
            field = f"findings[{index}]"
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                self.fail(f"{field}.id")
            finding_id = item["id"]
            if finding_id in seen:
                self.fail(f"{field}.id", "duplicate_id")
            seen.add(finding_id)
            entry = self.catalogue.finding(finding_id)
            if entry is None:
                self.dropped_count += 1
            else:
                finding = self.finding(item, field, entry, collectors)
                self.check_finding_dates(finding, field, generated_at)
                findings.append(finding)
                if entry.coverage_total_from:
                    subsets.append((entry.coverage_total_from, finding, field))
        self.check_subsets(findings, subsets)
        return tuple(findings)

    def check_subsets(
        self, findings: list[Finding], subsets: list[tuple[str, Finding, str]]
    ) -> None:
        by_id = {finding.id: finding for finding in findings}
        for related, subset, field in subsets:
            population = by_id.get(related)
            coverage = subset.coverage
            total = coverage.total if coverage else None
            bounds = [coverage.scanned, total] if coverage else []
            if (
                population is not None
                and type(population.value) is int
                and subset.source == population.source
                and (subset.period or subset.collected_at)
                == (population.period or population.collected_at)
            ):
                exact = population.coverage is None or population.coverage.kind == "complete"
                if total is not None and (
                    total < population.value or (exact and total > population.value)
                ):
                    self.fail(f"{field}.coverage.total", "coverage_total_conflict", related=related)
                if exact:
                    bounds.append(population.value)
            if type(subset.value) is int and any(
                bound is not None and subset.value > bound for bound in bounds
            ):
                self.fail(f"{field}.value", "subset_count_exceeds_population")

    def guid(self, value: object, field: str) -> str:
        if not isinstance(value, str) or len(value) != 36:
            self.fail(field)
        try:
            guid = str(UUID(value))
        except ValueError:
            raise InputError("invalid_field", file=self.file_name, field=field) from None
        if guid != value.lower():
            self.fail(field)
        return guid

    def service_plan(self, value: object, field: str) -> ServicePlan:
        row = self.fields(value, field, required=_SERVICE_PLAN_FIELDS)
        name, guid = row["name"], row["guid"]
        return ServicePlan(
            None if name is None else self.matches(name, f"{field}.name", _IDENTIFIER),
            None if guid is None else self.guid(guid, f"{field}.guid"),
        )

    def product(self, value: object, field: str) -> Product:
        row = self.fields(value, field, required=_PRODUCT_REQUIRED, optional=_PRODUCT_OPTIONAL)
        raw_guid = row.get("sku_guid")
        sku_guid = None if raw_guid is None else self.guid(raw_guid, f"{field}.sku_guid")
        sku_part_number = row.get("sku_part_number")
        if sku_part_number is not None and not self.catalogue.accepts_sku_part_number(
            sku_part_number, sku_guid
        ):
            self.fail(f"{field}.sku_part_number")
        plan_list = row.get("service_plans")
        plans = [] if plan_list is None else self.list(plan_list, f"{field}.service_plans")
        return Product(
            sku_part_number=sku_part_number,
            sku_guid=sku_guid,
            purchased=self.count(row["purchased"], f"{field}.purchased"),
            assigned=self.count(row["assigned"], f"{field}.assigned"),
            service_plans=tuple(
                self.service_plan(item, f"{field}.service_plans[{i}]")
                for i, item in enumerate(plans)
            ),
        )

    def licences(self, value: object, collectors: dict[str, Collector]) -> Licences | None:
        if value is None:
            return None
        row = self.fields(value, "licences", required=_LICENCE_FIELDS)
        collector = self.code(row["collector"], "licences.collector", ("licences",))
        if collector not in collectors or collectors[collector].status == "skipped":
            self.fail("licences.collector", "invalid_collector")
        source = self.code(row["source"], "licences.source", self.catalogue.licence_sources)
        products = []
        parts: set[str] = set()
        guids: set[str] = set()
        for index, item in enumerate(self.list(row["products"], "licences.products")):
            field = f"licences.products[{index}]"
            product = self.product(item, field)
            part_number, guid = sku_key(product.sku_part_number or "", product.sku_guid or "")
            for name, identity, seen in (
                ("sku_part_number", part_number, parts),
                ("sku_guid", guid, guids),
            ):
                if identity:
                    if identity in seen:
                        self.fail(f"{field}.{name}", "duplicate_id")
                    seen.add(identity)
            products.append(product)
        licences = Licences(
            collector=collector,
            source=source,
            collected_at=self.timestamp(row["collected_at"], "licences.collected_at"),
            coverage=self.coverage(row["coverage"], "licences.coverage"),
            products=tuple(products),
        )
        licences.check_coverage(self.file_name)
        return licences

    def scan(self, value: object) -> Scan:
        if not isinstance(value, dict):
            self.fail("$")
        version = self.schema_version(value.get("schema_version"))
        row = self.fields(value, "", required=_SCAN_FIELDS)
        collectors = self.collectors(row["collectors"])
        generated_at = self.timestamp(row["generated_at"], "generated_at")
        scan = Scan(
            schema_version=version,
            tool=self.tool(row["tool"]),
            generated_at=generated_at,
            source_kind=self.code(row["source_kind"], "source_kind", SOURCE_KINDS),
            collectors=tuple(collectors.values()),
            findings=self.findings(row["findings"], collectors, generated_at),
            licences=self.licences(row["licences"], collectors),
            dropped_count=self.dropped_count,
        )
        if scan.source_kind != "sample" and scan.is_sample:
            self.fail("source_kind", "sample_source_conflict")
        if scan.licences and _timestamp_after(scan.licences.collected_at, generated_at):
            self.fail("licences.collected_at", "collection_after_scan")
        return scan


def load_scan_text(text: str, file_name: str, catalogue: Catalogue) -> Scan:
    data = parse_json(text, file_name, fields=_SCAN_FIELD_NAMES)
    try:
        reject_at_signs(data, file_name)
    except RecursionError:
        raise InputError("invalid_json", file=file_name, line=1) from None
    return _ScanReader(file_name, catalogue).scan(data)


def load_scan(path: Path, catalogue: Catalogue) -> Scan:
    return load_scan_text(read_text(path), path.name, catalogue)


def _public_products(
    products: tuple[Product, ...], plans: tuple[RegisteredServicePlan, ...]
) -> tuple[Product, ...]:
    registered = {sku_key(plan.sku_part_number, plan.sku_guid): plan for plan in plans}
    names = {plan.name.casefold(): plan.name for plan in plans}
    guids = {plan.guid for plan in plans}
    public = []
    for product in products:
        if (identity := registered.get(product.key)) is None:
            public.append(
                replace(
                    product,
                    sku_part_number=None,
                    sku_guid=None,
                    service_plans=(ServicePlan(None, None),) * len(product.service_plans),
                )
            )
            continue
        # A registered half of a mismatched pair can still identify an affected workload.
        public.append(
            replace(
                product,
                sku_part_number=identity.sku_part_number,
                sku_guid=identity.sku_guid,
                service_plans=tuple(
                    ServicePlan(
                        names.get(plan.name.casefold()) if plan.name is not None else None,
                        plan.guid if plan.guid in guids else None,
                    )
                    for plan in product.service_plans
                ),
            )
        )
    return tuple(public)


def scan_to_json(scan: Scan, *, plans: tuple[RegisteredServicePlan, ...]) -> str:
    if scan.licences is not None:
        licences = replace(scan.licences, products=_public_products(scan.licences.products, plans))
        scan = replace(scan, licences=licences)
    data = asdict(scan)
    del data["dropped_count"]
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
