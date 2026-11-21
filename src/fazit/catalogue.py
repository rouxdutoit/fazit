# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from pathlib import Path

from .errors import InputError
from .parsing import parse_yaml, read_text

VALUE_TYPES = ("count", "bytes", "boolean", "code")
_PROVIDED_KINDS = ("no", "answer", "software_list", "software_list_without_web_version")
_CODE = re.compile(r"[a-z0-9_]+(?:\.[a-z0-9_]+)*")
_PERMISSION = re.compile(r"[A-Za-z0-9.]+")
_LABEL = re.compile(r"(?:workload|finding)\.[a-z0-9_]+(?:\.[a-z0-9_]+)*")


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

    @property
    def workload_ids(self) -> tuple[str, ...]:
        return tuple(workload.id for workload in self.workloads)

    def finding(self, finding_id: str) -> FindingEntry | None:
        return next((entry for entry in self.findings if entry.id == finding_id), None)


def _code(value: object, file_name: str, field: str, pattern: re.Pattern[str] = _CODE) -> str:
    if not isinstance(value, str) or len(value) > 64 or not pattern.fullmatch(value):
        raise InputError("invalid_field", file=file_name, field=field)
    return value


def _rows(value: object, file_name: str, field: str, keys: set[str]) -> list[dict]:
    if not isinstance(value, list):
        raise InputError("invalid_field", file=file_name, field=field)
    for index, row in enumerate(value):
        if not isinstance(row, dict) or row.keys() != keys:
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


def _findings(value: object, file_name: str, workload_ids: set[str]) -> tuple[FindingEntry, ...]:
    keys = {"id", "workload", "type", "unit", "label", "provided", "headline"}
    findings: dict[str, FindingEntry] = {}
    for index, row in enumerate(_rows(value, file_name, "findings", keys)):
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
        findings[finding_id] = FindingEntry(
            finding_id,
            workload,
            value_type,
            unit,
            _code(row["label"], file_name, f"{field}.label", _LABEL),
            provided,
            headline,
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


def load_catalogue(path: Path | None = None) -> Catalogue:
    source = path if path is not None else files("fazit").joinpath("rules", "findings.yaml")
    text = read_text(source)
    data = parse_yaml(text, source.name)
    if not isinstance(data, dict) or data.keys() != {"workloads", "findings", "codes"}:
        raise InputError("invalid_field", file=source.name, field="$")
    workloads = _workloads(data["workloads"], source.name)
    findings = _findings(data["findings"], source.name, {entry.id for entry in workloads})
    codes = data["codes"]
    if not isinstance(codes, dict) or codes.keys() != {
        "collectors",
        "sources",
        "reasons",
        "permissions",
    }:
        raise InputError("invalid_field", file=source.name, field="codes")
    return Catalogue(
        workloads=workloads,
        findings=findings,
        collector_ids=_code_set(codes["collectors"], source.name, "codes.collectors"),
        source_codes=_code_set(codes["sources"], source.name, "codes.sources"),
        reason_codes=_code_set(codes["reasons"], source.name, "codes.reasons"),
        permissions=_code_set(codes["permissions"], source.name, "codes.permissions", _PERMISSION),
        file_name=source.name,
        checksum=sha256(text.encode("utf-8")).hexdigest(),
    )
