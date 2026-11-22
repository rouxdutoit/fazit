# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from pathlib import Path

from .catalogue import Catalogue
from .rules import read_rules

_EXTENSION = re.compile(r"[a-z0-9]+")
_RISKY_FINDING_PREFIX = "office_files.kind."


@dataclass(frozen=True)
class RiskyKind:
    id: str
    finding_id: str
    label: Mapping[str, str]
    note: Mapping[str, str]
    extensions: tuple[str, ...]


def load_risky_file_types(
    catalogue: Catalogue,
    path: Path | None = None,
    *,
    checksums: MutableMapping[str, str] | None = None,
) -> tuple[RiskyKind, ...]:
    reader, data = read_rules("risky_file_types.yaml", path, checksums)
    root = reader.fields(data, "$", ("kinds",))
    finding_ids = {
        entry.id.removeprefix(_RISKY_FINDING_PREFIX): entry.id
        for entry in catalogue.findings
        if entry.id.startswith(_RISKY_FINDING_PREFIX) and entry.type == "count"
    }
    kinds: dict[str, RiskyKind] = {}
    seen_extensions: set[str] = set()
    for index, item in enumerate(reader.rows(root["kinds"], "kinds")):
        field = f"kinds[{index}]"
        row = reader.fields(item, field, ("id", "label", "note", "extensions"))
        kind = reader.choice(row["id"], f"{field}.id", finding_ids.keys())
        if kind in kinds:
            reader.fail(f"{field}.id", "duplicate_id")
        extensions = reader.rows(row["extensions"], f"{field}.extensions")
        for number, extension in enumerate(extensions):
            member = f"{field}.extensions[{number}]"
            extension = reader.matches(extension, member, _EXTENSION)
            if extension in seen_extensions:
                reader.fail(member, "duplicate_id")
            seen_extensions.add(extension)
        kinds[kind] = RiskyKind(
            kind,
            finding_ids[kind],
            reader.bilingual(row["label"], f"{field}.label"),
            reader.bilingual(row["note"], f"{field}.note"),
            tuple(extensions),
        )
    return tuple(kinds.values())
