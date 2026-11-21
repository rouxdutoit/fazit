# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files
from pathlib import Path

from .errors import InputError
from .parsing import parse_yaml, read_text

VALUE_TYPES = ("count", "bytes", "boolean")
_PROVIDED_KINDS = ("no", "answer", "software_list", "software_list_without_web_version")
_CODE = re.compile(r"[a-z0-9_]+(?:\.[a-z0-9_]+)*")
_PERMISSION = re.compile(r"[A-Za-z0-9.]+")
_LABEL = re.compile(r"(?:workload|finding)\.[a-z0-9_]+(?:\.[a-z0-9_]+)*")
_SKU_IDENTIFIER = re.compile(r"[A-Za-z0-9_]{1,64}")
_SKU_EXCEPTION = re.compile(r"[A-Za-z0-9_()/ ]{1,80}")
_GUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")


def sku_key(part_number: str, guid: str) -> tuple[str, str]:
    return part_number.replace("\u00a0", " ").casefold(), guid.lower()


@dataclass(frozen=True)
class WorkloadEntry:
    id: str
    label: str


@dataclass(frozen=True)
class FindingEntry:
    id: str
    workload: str
    type: str
    unit: str | None
    label: str
    provided: str
    headline: bool
    measured_by: frozenset[tuple[str, str]] = frozenset()
    coverage_total_from: str | None = None


@dataclass(frozen=True)
class Catalogue:
    workloads: tuple[WorkloadEntry, ...]
    findings: tuple[FindingEntry, ...]
    collector_ids: frozenset[str]
    source_codes: frozenset[str]
    reason_codes: frozenset[str]
    permissions: frozenset[str]
    file_name: str = "findings.yaml"
    checksum: str | None = None
    provided_sources: frozenset[str] = frozenset()
    sku_exceptions: frozenset[tuple[str, str]] = frozenset()
    licence_sources: frozenset[str] = frozenset()

    @property
    def workload_ids(self) -> tuple[str, ...]:
        return tuple(workload.id for workload in self.workloads)

    def finding(self, finding_id: str) -> FindingEntry | None:
        return next((entry for entry in self.findings if entry.id == finding_id), None)

    def accepts_sku_part_number(self, part_number: object, guid: str | None) -> bool:
        return isinstance(part_number, str) and (
            bool(_SKU_IDENTIFIER.fullmatch(part_number))
            or (guid is not None and sku_key(part_number, guid) in self.sku_exceptions)
        )


def _code(value: object, file_name: str, field: str, pattern: re.Pattern[str] = _CODE) -> str:
    if not isinstance(value, str) or len(value) > 64 or not pattern.fullmatch(value):
        raise InputError("invalid_field", file=file_name, field=field)
    return value


def _rows(
    value: object, file_name: str, field: str, keys: set[str], *, optional: tuple[str, ...] = ()
) -> list[dict]:
    if not isinstance(value, list):
        raise InputError("invalid_field", file=file_name, field=field)
    for index, row in enumerate(value):
        if not isinstance(row, dict) or not keys <= row.keys() <= keys.union(optional):
            raise InputError("invalid_field", file=file_name, field=f"{field}[{index}]")
    return value


def _workloads(value: object, file_name: str) -> tuple[WorkloadEntry, ...]:
    workloads: dict[str, WorkloadEntry] = {}
    for index, row in enumerate(_rows(value, file_name, "workloads", {"id", "label"})):
        field = f"workloads[{index}]"
        workload_id = _code(row["id"], file_name, f"{field}.id")
        if workload_id in workloads:
            raise InputError("duplicate_id", file=file_name, field=f"{field}.id")
        workloads[workload_id] = WorkloadEntry(
            workload_id, _code(row["label"], file_name, f"{field}.label", _LABEL)
        )
    return tuple(workloads.values())


def _measurement_pairs(
    value: object,
    file_name: str,
    field: str,
    collector_ids: frozenset[str],
    measured_sources: frozenset[str],
) -> frozenset[tuple[str, str]]:
    if not isinstance(value, dict):
        raise InputError("invalid_field", file=file_name, field=field)
    pairs = set()
    for index, (collector, values) in enumerate(value.items()):
        member = f"{field}[{index}]"
        sources = _code_set(values, file_name, member)
        if collector not in collector_ids or not sources or not sources <= measured_sources:
            raise InputError("invalid_field", file=file_name, field=member)
        pairs.update((collector, source) for source in sources)
    return frozenset(pairs)


def _findings(
    value: object,
    file_name: str,
    workload_ids: set[str],
    collector_ids: frozenset[str],
    measured_sources: frozenset[str],
) -> tuple[FindingEntry, ...]:
    keys = {"id", "workload", "type", "unit", "label", "provided", "headline"}
    findings: dict[str, FindingEntry] = {}
    for index, row in enumerate(
        _rows(value, file_name, "findings", keys, optional=("measured_by", "coverage_total_from"))
    ):
        field = f"findings[{index}]"
        finding_id = _code(row["id"], file_name, f"{field}.id")
        if "." not in finding_id:
            raise InputError("invalid_field", file=file_name, field=f"{field}.id")
        if finding_id in findings:
            raise InputError("duplicate_id", file=file_name, field=f"{field}.id")
        workload = _code(row["workload"], file_name, f"{field}.workload")
        value_type, provided, headline = row["type"], row["provided"], row["headline"]
        checks = {
            "workload": workload in workload_ids,
            "type": value_type in VALUE_TYPES,
            "provided": provided in _PROVIDED_KINDS,
            "headline": isinstance(headline, bool),
        }
        for name, valid in checks.items():
            if not valid:
                raise InputError("invalid_field", file=file_name, field=f"{field}.{name}")
        unit = row["unit"]
        if unit is not None:
            unit = _code(unit, file_name, f"{field}.unit")
        coverage_total_from = row.get("coverage_total_from")
        if coverage_total_from is not None:
            coverage_total_from = _code(
                coverage_total_from, file_name, f"{field}.coverage_total_from"
            )
        findings[finding_id] = FindingEntry(
            finding_id,
            workload,
            value_type,
            unit,
            _code(row["label"], file_name, f"{field}.label", _LABEL),
            provided,
            headline,
            _measurement_pairs(
                row.get("measured_by", {}),
                file_name,
                f"{field}.measured_by",
                collector_ids,
                measured_sources,
            ),
            coverage_total_from,
        )
    for index, entry in enumerate(findings.values()):
        if entry.coverage_total_from is not None:
            total = findings.get(entry.coverage_total_from)
            if total is None or total.type != "count" or total.id == entry.id:
                raise InputError(
                    "invalid_field", file=file_name, field=f"findings[{index}].coverage_total_from"
                )
    return tuple(findings.values())


def _code_set(
    value: object, file_name: str, field: str, pattern: re.Pattern[str] = _CODE
) -> frozenset[str]:
    if not isinstance(value, list):
        raise InputError("invalid_field", file=file_name, field=field)
    codes: set[str] = set()
    for index, item in enumerate(value):
        member = f"{field}[{index}]"
        code = _code(item, file_name, member, pattern)
        if code in codes:
            raise InputError("duplicate_id", file=file_name, field=member)
        codes.add(code)
    return frozenset(codes)


def _sku_exceptions(value: object, file_name: str) -> frozenset[tuple[str, str]]:
    field = "codes.sku_exceptions"
    if not isinstance(value, dict):
        raise InputError("invalid_field", file=file_name, field=field)
    keys = set()
    for index, (raw_guid, part) in enumerate(value.items()):
        member = f"{field}[{index}]"
        guid = _code(raw_guid, file_name, member, _GUID)
        if not isinstance(part, str) or not _SKU_EXCEPTION.fullmatch(part):
            raise InputError("invalid_field", file=file_name, field=member)
        keys.add(sku_key(part, guid))
    return frozenset(keys)


def load_catalogue(path: Path | None = None) -> Catalogue:
    source = path if path is not None else files("befund").joinpath("rules", "findings.yaml")
    return _parse_catalogue(read_text(source), source.name)


@lru_cache(maxsize=2)
def _parse_catalogue(text: str, file_name: str) -> Catalogue:
    data = parse_yaml(text, file_name)
    if not isinstance(data, dict) or data.keys() != {"workloads", "findings", "codes"}:
        raise InputError("invalid_field", file=file_name, field="$")
    workloads = _workloads(data["workloads"], file_name)
    codes = data["codes"]
    if not isinstance(codes, dict) or codes.keys() != {
        "collectors",
        "sources",
        "licence_sources",
        "provided_sources",
        "reasons",
        "permissions",
        "sku_exceptions",
    }:
        raise InputError("invalid_field", file=file_name, field="codes")
    collector_ids = _code_set(codes["collectors"], file_name, "codes.collectors")
    measured_sources = _code_set(codes["sources"], file_name, "codes.sources")
    licence_sources = _code_set(codes["licence_sources"], file_name, "codes.licence_sources")
    if measured_sources & licence_sources:
        raise InputError("duplicate_id", file=file_name, field="codes.licence_sources")
    measured_sources |= licence_sources
    provided_sources = _code_set(codes["provided_sources"], file_name, "codes.provided_sources")
    if measured_sources & provided_sources:
        raise InputError("duplicate_id", file=file_name, field="codes.provided_sources")
    findings = _findings(
        data["findings"],
        file_name,
        set(entry.id for entry in workloads),
        collector_ids,
        measured_sources,
    )
    return Catalogue(
        workloads=workloads,
        findings=findings,
        collector_ids=collector_ids,
        source_codes=measured_sources | provided_sources,
        reason_codes=_code_set(codes["reasons"], file_name, "codes.reasons"),
        permissions=_code_set(codes["permissions"], file_name, "codes.permissions", _PERMISSION),
        file_name=file_name,
        checksum=sha256(text.encode("utf-8")).hexdigest(),
        provided_sources=provided_sources,
        sku_exceptions=_sku_exceptions(codes["sku_exceptions"], file_name),
        licence_sources=licence_sources,
    )
