# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import PROJECT_NAME
from .catalogue import Catalogue, FindingEntry, sku_key
from .errors import InputError
from .parsing import parse_json, read_text
from .validation import DATE, IDENTIFIER, MAX_COUNT, MAX_STORAGE_BYTES, Validator

SUPPORTED_SCHEMA_MAJOR = 1
SOURCE_KINDS = ("sample", "import", "live")
COLLECTOR_STATUSES = ("ok", "partial", "skipped")
PROVENANCES = ("measured", "provided", "unknown")
COVERAGE_KINDS = ("complete", "partial", "unknown")

_SCHEMA_VERSION = re.compile(r"[0-9]{1,8}\.[0-9]{1,8}")
_TOOL_VERSION = re.compile(r"[0-9]{1,8}(?:\.[0-9]{1,8}){1,2}")
_TIMESTAMP = re.compile(
    rf"{DATE.pattern}(?:T[0-9]{{2}}:[0-9]{{2}}(?::[0-9]{{2}}(?:[.,][0-9]{{1,6}})?)?"
    r"(?:Z|[+-][0-9]{2}(?::?[0-5][0-9])?)?)?"
)
_PERIOD = re.compile(rf"{DATE.pattern}/{DATE.pattern}")
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
type FindingValue = int | bool


def _timestamp_after(stamp: str, reference: str) -> bool:
    time, limit = datetime.fromisoformat(stamp), datetime.fromisoformat(reference)
    if len(stamp) == 10 or len(reference) == 10:
        return time.date() > limit.date()
    if time.tzinfo is None or limit.tzinfo is None:
        time, limit = time.replace(tzinfo=None), limit.replace(tzinfo=None)
    return time > limit


def same_collection_time(first: str | None, second: str | None) -> bool:
    return (
        first is not None
        and second is not None
        and len(first) > 10
        and len(second) > 10
        and datetime.fromisoformat(first) == datetime.fromisoformat(second)
    )


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

    @property
    def successful_limit(self) -> int | None:
        if self.scanned is not None:
            return self.scanned
        return None if self.total is None else self.total - (self.failed or 0)


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


def _population_bounds(
    subset: Finding, population: Finding | None
) -> tuple[int | None, int | None]:
    if (
        population is None
        or subset.source != population.source
        or subset.period != population.period
        or (
            subset.period is None
            and not same_collection_time(subset.collected_at, population.collected_at)
        )
    ):
        return None, None
    value = population.value if type(population.value) is int else None
    coverage = population.coverage
    if coverage is None or (value is not None and coverage.kind == "complete"):
        return value, value
    return value, coverage.total


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
        limit = self.coverage.successful_limit
        if limit is not None and count > limit:
            field = "scanned" if self.coverage.scanned is not None else "total"
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
        self.check = Validator(file_name)
        self.catalogue = catalogue
        self.dropped_count = 0

    def fields(
        self,
        value: object,
        field: str,
        required: tuple[str, ...],
        optional: tuple[str, ...] = (),
    ) -> dict:
        row = self.check.fields(value, field, required, optional=None)
        self.dropped_count += len(row.keys() - {*required, *optional})
        return row

    def timestamp(self, value: object, field: str, *, require_time: bool = False) -> str:
        stamp = self.check.matches(value, field, _TIMESTAMP)
        try:
            datetime.fromisoformat(stamp)
        except ValueError:
            self.check.fail(field)
        if require_time and len(stamp) == 10:
            self.check.fail(field, "observation_time_required")
        return stamp

    def period(self, value: object, field: str) -> str:
        interval = self.check.matches(value, field, _PERIOD)
        start, end = interval.split("/")
        if self.check.calendar_date(start, field) > self.check.calendar_date(end, field):
            self.check.fail(field)
        return interval

    def schema_version(self, value: object) -> str:
        version = self.check.matches(value, "schema_version", _SCHEMA_VERSION)
        if int(version.split(".", 1)[0]) != SUPPORTED_SCHEMA_MAJOR:
            raise InputError(
                "schema_version",
                file=self.check.file_name,
                field="schema_version",
                found=version,
                supported=f"{SUPPORTED_SCHEMA_MAJOR}.x",
            )
        return version

    def tool(self, value: object) -> ToolInfo:
        row = self.fields(value, "tool", _TOOL_FIELDS)
        return ToolInfo(
            name=self.check.choice(row["name"], "tool.name", (PROJECT_NAME,)),
            version=self.check.matches(row["version"], "tool.version", _TOOL_VERSION),
        )

    def collectors(self, value: object) -> dict[str, Collector]:
        collectors: dict[str, Collector] = {}
        for index, item in enumerate(self.check.rows(value, "collectors", allow_empty=True)):
            field = f"collectors[{index}]"
            row = self.fields(item, field, _COLLECTOR_REQUIRED, _COLLECTOR_OPTIONAL)
            collector_id = self.check.choice(row["id"], f"{field}.id", self.catalogue.collector_ids)
            if collector_id in collectors:
                self.check.fail(f"{field}.id", "duplicate_id")
            status = self.check.choice(row["status"], f"{field}.status", COLLECTOR_STATUSES)
            reason = row.get("reason")
            if (status == "ok") != (reason is None):
                self.check.fail(f"{field}.reason", "collector_reason_mismatch")
            if reason is not None:
                reason = self.check.choice(reason, f"{field}.reason", self.catalogue.reason_codes)
            permissions = self.check.rows(
                row["permissions_used"], f"{field}.permissions_used", allow_empty=True
            )
            collectors[collector_id] = Collector(
                collector_id,
                status,
                reason,
                tuple(
                    self.check.choice(
                        code, f"{field}.permissions_used[{i}]", self.catalogue.permissions
                    )
                    for i, code in enumerate(permissions)
                ),
            )
        return collectors

    def coverage(self, value: object, field: str) -> Coverage:
        row = self.fields(value, field, ("kind",), _COVERAGE_COUNTS)
        kind = self.check.choice(row["kind"], f"{field}.kind", COVERAGE_KINDS)
        scanned, failed, total = (
            self.check.optional_count(row.get(name), f"{field}.{name}") for name in _COVERAGE_COUNTS
        )
        if total is not None and (scanned or 0) + (failed or 0) > total:
            self.check.fail(field, "invalid_coverage")
        if kind == "complete" and any(count is not None for count in (scanned, failed, total)):
            if failed != 0 or scanned is None or total is None or scanned != total:
                self.check.fail(field, "invalid_coverage")
        return Coverage(kind, scanned, failed, total)

    def finding_value(self, value: object, field: str, entry: FindingEntry) -> FindingValue:
        if entry.type == "boolean":
            if not isinstance(value, bool):
                self.check.fail(field)
            return value
        maximum = MAX_STORAGE_BYTES if entry.unit == "bytes" else MAX_COUNT
        return self.check.count(value, field, maximum=maximum)

    def finding(
        self, item: object, field: str, entry: FindingEntry, collectors: dict[str, Collector]
    ) -> Finding:
        row = self.fields(item, field, _FINDING_FIELDS)
        if row["workload"] != entry.workload:
            self.check.fail(f"{field}.workload")
        if row["unit"] != entry.unit:
            self.check.fail(f"{field}.unit", "invalid_code")
        provenance = self.check.choice(row["provenance"], f"{field}.provenance", PROVENANCES)
        collector = row["collector"]
        if collector is not None:
            collector = self.check.choice(collector, f"{field}.collector", collectors)
        self.check_evidence(row, field, provenance, collectors.get(collector))
        value, source, reason = row["value"], row["source"], row["missing_reason"]
        if source is not None:
            source = self.check.choice(source, f"{field}.source", self.catalogue.source_codes)
        self.check_finding_source(entry, field, collector, source)
        collected_at, period = row["collected_at"], row["period"]
        coverage = (
            None if row["coverage"] is None else self.coverage(row["coverage"], f"{field}.coverage")
        )
        value = None if value is None else self.finding_value(value, f"{field}.value", entry)
        if provenance == "measured" and coverage is not None:
            limit = coverage.successful_limit
            if limit == 0 and (value or coverage.kind != "complete"):
                self.check.fail(f"{field}.value", "measurement_without_observations")
            if (
                type(value) is int
                and entry.type == "count"
                and not entry.aggregate
                and limit is not None
                and value > limit
            ):
                self.check.fail(f"{field}.value", "subset_count_exceeds_population")
        return Finding(
            id=entry.id,
            workload=entry.workload,
            unit=entry.unit,
            provenance=provenance,
            value=value,
            collector=collector,
            source=source,
            collected_at=None
            if collected_at is None
            else self.timestamp(
                collected_at,
                f"{field}.collected_at",
                require_time=provenance == "measured" and period is None,
            ),
            period=None if period is None else self.period(period, f"{field}.period"),
            coverage=coverage,
            missing_reason=None
            if reason is None
            else self.check.choice(reason, f"{field}.missing_reason", self.catalogue.reason_codes),
        )

    def check_finding_source(
        self, entry: FindingEntry, field: str, collector: str | None, source: str | None
    ) -> None:
        if source in ("inputs_yaml", "sample.inputs_yaml"):
            self.check.fail(f"{field}.source", "inputs_source_in_scan")
        if collector is not None:
            allowed = {code for method, code in entry.measured_by if method == collector}
            if not allowed:
                self.check.fail(f"{field}.collector", "invalid_evidence_source", finding=entry.id)
        else:
            allowed = self.catalogue.provided_sources if entry.provided != "no" else frozenset()
        if source is not None and source not in allowed:
            self.check.fail(f"{field}.source", "invalid_evidence_source", finding=entry.id)

    def check_evidence(
        self, row: dict, field: str, provenance: str, collector: Collector | None
    ) -> None:
        if provenance == "unknown":
            required, empty = ("missing_reason",), ("value",)
        elif provenance == "provided":
            required, empty = ("value", "source"), ("collector", "coverage", "missing_reason")
        else:
            if collector is None or collector.status == "skipped":
                self.check.fail(f"{field}.collector", "invalid_collector")
            required = ("value", "source", "collected_at", "coverage")
            empty = ("missing_reason",)
        for name in required:
            if row[name] is None:
                self.check.fail(f"{field}.{name}", "missing_field")
        for name in empty:
            if row[name] is not None:
                self.check.fail(f"{field}.{name}")

    def check_finding_dates(self, finding: Finding, field: str, generated_at: str) -> None:
        if (collected_at := finding.collected_at) is None:
            return
        if finding.period is not None and finding.period[-10:] > collected_at[:10]:
            self.check.fail(f"{field}.period", "period_after_collection")
        if _timestamp_after(collected_at, generated_at):
            self.check.fail(f"{field}.collected_at", "collection_after_scan")

    def findings(
        self, value: object, collectors: dict[str, Collector], generated_at: str
    ) -> tuple[Finding, ...]:
        findings: dict[str, Finding] = {}
        subsets: list[tuple[FindingEntry, Finding, str]] = []
        seen: set[str] = set()
        for index, item in enumerate(self.check.rows(value, "findings", allow_empty=True)):
            field = f"findings[{index}]"
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                self.check.fail(f"{field}.id")
            finding_id = item["id"]
            if finding_id in seen:
                self.check.fail(f"{field}.id", "duplicate_id")
            seen.add(finding_id)
            entry = self.catalogue.finding(finding_id)
            if entry is None:
                self.dropped_count += 1
            else:
                finding = self.finding(item, field, entry, collectors)
                self.check_finding_dates(finding, field, generated_at)
                findings[finding_id] = finding
                if entry.coverage_total_from or entry.subset_of:
                    subsets.append((entry, finding, field))
        self.check_subsets(findings, subsets)
        return tuple(findings.values())

    def check_subsets(
        self, findings: dict[str, Finding], subsets: list[tuple[FindingEntry, Finding, str]]
    ) -> None:
        for entry, subset, field in subsets:
            bounds = []
            if related := entry.coverage_total_from:
                lower, upper = _population_bounds(subset, findings.get(related))
                coverage = subset.coverage
                if coverage is not None:
                    total = coverage.total
                    if total is not None and (
                        (lower is not None and total < lower)
                        or (upper is not None and total != upper)
                    ):
                        self.check.fail(
                            f"{field}.coverage.total", "coverage_total_conflict", related=related
                        )
                    if upper is not None:
                        upper -= coverage.failed or 0
                        if (coverage.scanned or 0) > upper:
                            self.check.fail(f"{field}.coverage", "invalid_coverage")
                        if (
                            upper == 0
                            and coverage.kind != "complete"
                            and subset.provenance == "measured"
                        ):
                            self.check.fail(f"{field}.value", "measurement_without_observations")
                bounds.append(upper)
            if entry.subset_of:
                parts = [
                    _population_bounds(subset, findings.get(parent))[1]
                    for parent in entry.subset_of
                ]
                if None not in parts:
                    bounds.append(sum(part for part in parts if part is not None))
            if type(subset.value) is int and any(
                bound is not None and subset.value > bound for bound in bounds
            ):
                self.check.fail(f"{field}.value", "subset_count_exceeds_population")

    def service_plan(self, value: object, field: str) -> ServicePlan:
        row = self.fields(value, field, _SERVICE_PLAN_FIELDS)
        name, guid = row["name"], row["guid"]
        return ServicePlan(
            None if name is None else self.check.matches(name, f"{field}.name", IDENTIFIER),
            None if guid is None else self.check.guid(guid, f"{field}.guid"),
        )

    def product(self, value: object, field: str) -> Product:
        row = self.fields(value, field, _PRODUCT_REQUIRED, _PRODUCT_OPTIONAL)
        raw_guid = row.get("sku_guid")
        sku_guid = None if raw_guid is None else self.check.guid(raw_guid, f"{field}.sku_guid")
        sku_part_number = row.get("sku_part_number")
        if sku_part_number is not None and not self.catalogue.accepts_sku_part_number(
            sku_part_number, sku_guid
        ):
            self.check.fail(f"{field}.sku_part_number")
        plan_list = row.get("service_plans")
        plans = (
            []
            if plan_list is None
            else self.check.rows(plan_list, f"{field}.service_plans", allow_empty=True)
        )
        purchased = self.check.count(row["purchased"], f"{field}.purchased")
        assigned = self.check.count(row["assigned"], f"{field}.assigned")
        if assigned > purchased:
            self.check.fail(f"{field}.assigned", "assigned_exceeds_purchased")
        return Product(
            sku_part_number=sku_part_number,
            sku_guid=sku_guid,
            purchased=purchased,
            assigned=assigned,
            service_plans=tuple(
                self.service_plan(item, f"{field}.service_plans[{i}]")
                for i, item in enumerate(plans)
            ),
        )

    def licences(self, value: object, collectors: dict[str, Collector]) -> Licences | None:
        if value is None:
            return None
        row = self.fields(value, "licences", _LICENCE_FIELDS)
        collector = self.check.choice(row["collector"], "licences.collector", ("licences",))
        if collector not in collectors or collectors[collector].status == "skipped":
            self.check.fail("licences.collector", "invalid_collector")
        source = self.check.choice(row["source"], "licences.source", self.catalogue.licence_sources)
        products = []
        parts: set[str] = set()
        guids: set[str] = set()
        for index, item in enumerate(
            self.check.rows(row["products"], "licences.products", allow_empty=True)
        ):
            field = f"licences.products[{index}]"
            product = self.product(item, field)
            part_number, guid = sku_key(product.sku_part_number or "", product.sku_guid or "")
            for name, identity, seen in (
                ("sku_part_number", part_number, parts),
                ("sku_guid", guid, guids),
            ):
                if identity and identity in seen:
                    self.check.fail(f"{field}.{name}", "duplicate_id")
                seen.add(identity)
            products.append(product)
        licences = Licences(
            collector=collector,
            source=source,
            collected_at=self.timestamp(
                row["collected_at"], "licences.collected_at", require_time=True
            ),
            coverage=self.coverage(row["coverage"], "licences.coverage"),
            products=tuple(products),
        )
        licences.check_coverage(self.check.file_name)
        return licences

    def scan(self, value: object) -> Scan:
        if not isinstance(value, dict):
            self.check.fail("", "invalid_field_document")
        version = self.schema_version(value.get("schema_version"))
        row = self.fields(value, "", _SCAN_FIELDS)
        collectors = self.collectors(row["collectors"])
        generated_at = self.timestamp(row["generated_at"], "generated_at")
        scan = Scan(
            schema_version=version,
            tool=self.tool(row["tool"]),
            generated_at=generated_at,
            source_kind=self.check.choice(row["source_kind"], "source_kind", SOURCE_KINDS),
            collectors=tuple(collectors.values()),
            findings=self.findings(row["findings"], collectors, generated_at),
            licences=self.licences(row["licences"], collectors),
            dropped_count=self.dropped_count,
        )
        if scan.source_kind != "sample" and scan.is_sample:
            self.check.fail("source_kind", "sample_source_conflict")
        if scan.licences and _timestamp_after(scan.licences.collected_at, generated_at):
            self.check.fail("licences.collected_at", "collection_after_scan")
        return scan


def load_scan_text(text: str, file_name: str, catalogue: Catalogue) -> Scan:
    return _ScanReader(file_name, catalogue).scan(parse_json(text, file_name))


def load_scan(path: Path, catalogue: Catalogue) -> Scan:
    return load_scan_text(read_text(path), path.name, catalogue)
