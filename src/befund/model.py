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
from .parsing import parse_json, read_text, reject_at_signs

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
_PERIOD = re.compile(rf"{_DATE}/{_DATE}")
_IDENTIFIER = re.compile(r"[A-Za-z0-9_]{1,64}")
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

type FindingValue = int | bool


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
        row = self.fields(value, "tool", required=("name", "version"))
        return ToolInfo(
            name=self.code(row["name"], "tool.name", (PROJECT_NAME,)),
            version=self.matches(row["version"], "tool.version", _TOOL_VERSION),
        )

    def collectors(self, value: object) -> dict[str, Collector]:
        collectors: dict[str, Collector] = {}
        for index, item in enumerate(self.list(value, "collectors")):
            field = f"collectors[{index}]"
            row = self.fields(
                item, field, required=("id", "status", "permissions_used"), optional=("reason",)
            )
            collector_id = self.code(row["id"], f"{field}.id", self.catalogue.collector_ids)
            if collector_id in collectors:
                self.fail(f"{field}.id", "duplicate_id")
            status = self.code(row["status"], f"{field}.status", COLLECTOR_STATUSES)
            reason = row.get("reason")
            if reason is not None or status != "ok":
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
        count_fields = ("scanned", "failed", "total")
        row = self.fields(value, field, required=("kind",), optional=count_fields)
        kind = self.code(row["kind"], f"{field}.kind", COVERAGE_KINDS)
        scanned, failed, total = (
            None if row.get(name) is None else self.count(row[name], f"{field}.{name}")
            for name in count_fields
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

    def findings(self, value: object, collectors: dict[str, Collector]) -> tuple[Finding, ...]:
        findings = []
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
                findings.append(self.finding(item, field, entry, collectors))
        return tuple(findings)

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
        row = self.fields(value, field, required=("name", "guid"))
        name, guid = row["name"], row["guid"]
        return ServicePlan(
            None if name is None else self.matches(name, f"{field}.name", _IDENTIFIER),
            None if guid is None else self.guid(guid, f"{field}.guid"),
        )

    def product(self, value: object, field: str) -> Product:
        row = self.fields(
            value,
            field,
            required=(
                "sku_part_number",
                "sku_guid",
                "purchased",
                "assigned",
            ),
            optional=("service_plans",),
        )
        sku_guid = row["sku_guid"]
        sku_part_number = row["sku_part_number"]
        if sku_guid is not None or sku_part_number is not None:
            sku_guid = self.guid(sku_guid, f"{field}.sku_guid")
            if not self.catalogue.accepts_sku_part_number(sku_part_number, sku_guid):
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
        row = self.fields(
            value,
            "licences",
            required=(
                "collector",
                "source",
                "collected_at",
                "coverage",
                "products",
            ),
        )
        collector = self.code(row["collector"], "licences.collector", ("licences",))
        if collector not in collectors or collectors[collector].status == "skipped":
            self.fail("licences.collector", "invalid_collector")
        products = []
        parts: set[str] = set()
        guids: set[str] = set()
        for index, item in enumerate(self.list(row["products"], "licences.products")):
            field = f"licences.products[{index}]"
            product = self.product(item, field)
            if (key := product.key) is not None:
                part_number, guid = key
                if part_number in parts:
                    self.fail(f"{field}.sku_part_number", "duplicate_id")
                if guid in guids:
                    self.fail(f"{field}.sku_guid", "duplicate_id")
                parts.add(part_number)
                guids.add(guid)
            products.append(product)
        return Licences(
            collector=collector,
            source=self.code(row["source"], "licences.source", self.catalogue.source_codes),
            collected_at=self.timestamp(row["collected_at"], "licences.collected_at"),
            coverage=self.coverage(row["coverage"], "licences.coverage"),
            products=tuple(products),
        )

    def scan(self, value: object) -> Scan:
        reject_at_signs(value, self.file_name)
        if not isinstance(value, dict):
            self.fail("$")
        version = self.schema_version(value.get("schema_version"))
        row = self.fields(
            value,
            "",
            required=(
                "schema_version",
                "tool",
                "generated_at",
                "source_kind",
                "collectors",
                "findings",
                "licences",
            ),
        )
        collectors = self.collectors(row["collectors"])
        return Scan(
            schema_version=version,
            tool=self.tool(row["tool"]),
            generated_at=self.timestamp(row["generated_at"], "generated_at"),
            source_kind=self.code(row["source_kind"], "source_kind", SOURCE_KINDS),
            collectors=tuple(collectors.values()),
            findings=self.findings(row["findings"], collectors),
            licences=self.licences(row["licences"], collectors),
            dropped_count=self.dropped_count,
        )


def load_scan_text(text: str, file_name: str, catalogue: Catalogue) -> Scan:
    return _ScanReader(file_name, catalogue).scan(parse_json(text, file_name))


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
