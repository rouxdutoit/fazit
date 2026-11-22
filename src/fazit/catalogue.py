# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files
from pathlib import Path

from .i18n import SUPPORTED_LANGUAGES, load_locale
from .parsing import parse_yaml, read_text
from .validation import IDENTIFIER, Validator

VALUE_TYPES = ("count", "bytes", "boolean")
_PROVIDED_KINDS = ("no", "answer", "software_list", "software_list_without_web_version")
_CODE_LENGTH = r"(?=.{1,64}\Z)"
_CODE_PATH = r"[a-z0-9_]+(?:\.[a-z0-9_]+)*"
_CODE = re.compile(_CODE_LENGTH + _CODE_PATH)
_PERMISSION = re.compile(r"[A-Za-z0-9.]{1,64}")
_LABEL = re.compile(_CODE_LENGTH + rf"(?:workload|finding)\.{_CODE_PATH}")
_SKU_EXCEPTION = re.compile(r"[A-Za-z0-9_()/ ]{1,80}")


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
    subset_of: frozenset[str] = frozenset()
    aggregate: bool = False


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
            bool(IDENTIFIER.fullmatch(part_number))
            or (guid is not None and sku_key(part_number, guid) in self.sku_exceptions)
        )


def _rows(
    value: object, reader: Validator, field: str, keys: set[str], *, optional: tuple[str, ...] = ()
) -> list[tuple[str, dict]]:
    allowed = keys.union(optional)
    rows = []
    for index, row in enumerate(reader.rows(value, field, allow_empty=True)):
        member = f"{field}[{index}]"
        if not isinstance(row, dict) or not keys <= row.keys() <= allowed:
            reader.fail(member)
        rows.append((member, row))
    return rows


def _workloads(value: object, reader: Validator) -> tuple[WorkloadEntry, ...]:
    workloads: dict[str, WorkloadEntry] = {}
    for field, row in _rows(value, reader, "workloads", {"id", "label"}):
        workload_id = reader.matches(row["id"], f"{field}.id", _CODE)
        if workload_id in workloads:
            reader.fail(f"{field}.id", "duplicate_id")
        workloads[workload_id] = WorkloadEntry(
            workload_id, reader.matches(row["label"], f"{field}.label", _LABEL)
        )
    return tuple(workloads.values())


def _measurement_pairs(
    value: object,
    reader: Validator,
    field: str,
    collector_ids: frozenset[str],
    measured_sources: frozenset[str],
) -> frozenset[tuple[str, str]]:
    pairs = set()
    rows = reader.fields(value, field, (), optional=None)
    for index, (collector, values) in enumerate(rows.items()):
        member = f"{field}[{index}]"
        sources = _code_set(values, reader, member)
        if collector not in collector_ids or not sources or not sources <= measured_sources:
            reader.fail(member)
        pairs.update((collector, source) for source in sources)
    return frozenset(pairs)


def _finding(
    row: dict,
    finding_id: str,
    field: str,
    reader: Validator,
    workload_ids: set[str],
    collector_ids: frozenset[str],
    measured_sources: frozenset[str],
) -> FindingEntry:
    workload = reader.choice(row["workload"], f"{field}.workload", workload_ids, "invalid_field")
    value_type = reader.choice(row["type"], f"{field}.type", VALUE_TYPES, "invalid_field")
    provided = reader.choice(row["provided"], f"{field}.provided", _PROVIDED_KINDS, "invalid_field")
    headline = row["headline"]
    if not isinstance(headline, bool):
        reader.fail(f"{field}.headline")
    unit = row["unit"]
    if unit is not None:
        unit = reader.matches(unit, f"{field}.unit", _CODE)
    total = row.get("coverage_total_from")
    if total is not None:
        total = reader.matches(total, f"{field}.coverage_total_from", _CODE)
    subset_of = _code_set(row.get("subset_of", []), reader, f"{field}.subset_of")
    if subset_of and value_type != "count":
        reader.fail(f"{field}.subset_of")
    aggregate = row.get("aggregate", False)
    if type(aggregate) is not bool or (aggregate and value_type != "count"):
        reader.fail(f"{field}.aggregate")
    return FindingEntry(
        finding_id,
        workload,
        value_type,
        unit,
        reader.matches(row["label"], f"{field}.label", _LABEL),
        provided,
        headline,
        _measurement_pairs(
            row.get("measured_by", {}),
            reader,
            f"{field}.measured_by",
            collector_ids,
            measured_sources,
        ),
        total,
        subset_of,
        aggregate,
    )


def _findings(
    value: object,
    reader: Validator,
    workload_ids: set[str],
    collector_ids: frozenset[str],
    measured_sources: frozenset[str],
) -> tuple[FindingEntry, ...]:
    keys = {"id", "workload", "type", "unit", "label", "provided", "headline"}
    findings: dict[str, FindingEntry] = {}
    for field, row in _rows(
        value,
        reader,
        "findings",
        keys,
        optional=("measured_by", "coverage_total_from", "subset_of", "aggregate"),
    ):
        finding_id = reader.matches(row["id"], f"{field}.id", _CODE)
        if "." not in finding_id:
            reader.fail(f"{field}.id")
        if finding_id in findings:
            reader.fail(f"{field}.id", "duplicate_id")
        findings[finding_id] = _finding(
            row, finding_id, field, reader, workload_ids, collector_ids, measured_sources
        )
    for index, entry in enumerate(findings.values()):
        coverage_total = (entry.coverage_total_from,) if entry.coverage_total_from else ()
        for field, references in (
            ("coverage_total_from", coverage_total),
            ("subset_of", sorted(entry.subset_of)),
        ):
            for reference in references:
                population = findings.get(reference)
                if (
                    population is None
                    or population.type != "count"
                    or population.aggregate
                    or reference == entry.id
                ):
                    reader.fail(f"findings[{index}].{field}")
    return tuple(findings.values())


def _code_set(
    value: object, reader: Validator, field: str, pattern: re.Pattern[str] = _CODE
) -> frozenset[str]:
    codes: set[str] = set()
    for index, item in enumerate(reader.rows(value, field, allow_empty=True)):
        member = f"{field}[{index}]"
        code = reader.matches(item, member, pattern)
        if code in codes:
            reader.fail(member, "duplicate_id")
        codes.add(code)
    return frozenset(codes)


def _sku_exceptions(value: object, reader: Validator) -> frozenset[tuple[str, str]]:
    field = "codes.sku_exceptions"
    rows = reader.fields(value, field, (), optional=None)
    keys = set()
    for index, (raw_guid, part) in enumerate(rows.items()):
        member = f"{field}[{index}]"
        guid = reader.guid(raw_guid, member)
        keys.add(sku_key(reader.matches(part, member, _SKU_EXCEPTION), guid))
    return frozenset(keys)


def _require_label(labels: object, key: str, reader: Validator, field: str) -> None:
    text = labels.get(key) if isinstance(labels, dict) else None
    if not isinstance(text, str) or not text.strip():
        reader.fail(field, "invalid_label")


def load_catalogue(path: Path | None = None) -> Catalogue:
    source = path if path is not None else files("fazit").joinpath("rules", "findings.yaml")
    reader = Validator(source.name)
    catalogue = _parse_catalogue(read_text(source), reader)
    sections = (("workloads", catalogue.workloads), ("findings", catalogue.findings))
    for lang in SUPPORTED_LANGUAGES:
        strings = load_locale(lang, copy=False)
        for group, entries in sections:
            for index, entry in enumerate(entries):
                section, key = entry.label.split(".", 1)
                _require_label(strings.get(section), key, reader, f"{group}[{index}].label")
        for index, entry in enumerate(catalogue.findings):
            if entry.unit is not None:
                for group in ("units", "unit_one"):
                    _require_label(
                        strings.get(group), entry.unit, reader, f"findings[{index}].unit"
                    )
        locale_reader = Validator(f"{lang}.yaml")
        for code in sorted(catalogue.source_codes):
            _require_label(strings.get("source"), code, locale_reader, f"source.{code}")
    return catalogue


@lru_cache(maxsize=2)
def _parse_catalogue(text: str, reader: Validator) -> Catalogue:
    data = parse_yaml(text, reader.file_name)
    if not isinstance(data, dict) or data.keys() != {"workloads", "findings", "codes"}:
        reader.fail("", "invalid_field_document")
    workloads = _workloads(data["workloads"], reader)
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
        reader.fail("codes")
    collector_ids = _code_set(codes["collectors"], reader, "codes.collectors")
    measured_sources = _code_set(codes["sources"], reader, "codes.sources")
    licence_sources = _code_set(codes["licence_sources"], reader, "codes.licence_sources")
    if measured_sources & licence_sources:
        reader.fail("codes.licence_sources", "duplicate_id")
    measured_sources |= licence_sources
    provided_sources = _code_set(codes["provided_sources"], reader, "codes.provided_sources")
    if measured_sources & provided_sources:
        reader.fail("codes.provided_sources", "duplicate_id")
    findings = _findings(
        data["findings"],
        reader,
        {entry.id for entry in workloads},
        collector_ids,
        measured_sources,
    )
    return Catalogue(
        workloads=workloads,
        findings=findings,
        collector_ids=collector_ids,
        source_codes=measured_sources | provided_sources,
        reason_codes=_code_set(codes["reasons"], reader, "codes.reasons"),
        permissions=_code_set(codes["permissions"], reader, "codes.permissions", _PERMISSION),
        file_name=reader.file_name,
        checksum=sha256(text.encode("utf-8")).hexdigest(),
        provided_sources=provided_sources,
        sku_exceptions=_sku_exceptions(codes["sku_exceptions"], reader),
        licence_sources=licence_sources,
    )
