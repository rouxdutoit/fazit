# SPDX-License-Identifier: AGPL-3.0-or-later
from collections.abc import MutableMapping
from hashlib import sha256
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

from .parsing import parse_yaml, read_text
from .validation import Validator


def rules_dir() -> Traversable:
    return files("fazit").joinpath("rules")


def read_rule_text(name: str, path: Path | None) -> tuple[Validator, str]:
    source = path if path is not None else rules_dir().joinpath(name)
    return Validator(source.name), read_text(source)


def read_rules(
    name: str, path: Path | None, checksums: MutableMapping[str, str] | None
) -> tuple[Validator, object]:
    reader, text = read_rule_text(name, path)
    data = parse_yaml(text, reader.file_name)
    if checksums is not None:
        checksums[reader.file_name] = sha256(text.encode("utf-8")).hexdigest()
    return reader, data
