# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections.abc import Collection, Mapping
from datetime import date
from importlib.resources.abc import Traversable
from math import isfinite
from pathlib import Path
from typing import Never

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode
from yaml.tokens import AliasToken, AnchorToken

from .errors import InputError
from .validation import DATE, MAX_COUNT, MAX_STORAGE_BYTES

MAX_FILE_BYTES = 2 * 1024 * 1024
_COUNT_DIGITS = len(str(MAX_COUNT))
_JSON_INTEGER_LENGTH = len(str(MAX_STORAGE_BYTES)) + 1
type _SchemaPath = tuple[str | None, ...]
type FieldNames = Mapping[_SchemaPath, Collection[str]]
type ScalarFields = Mapping[_SchemaPath, str]

_YAML_TEXT = "tag:yaml.org,2002:str"
_YAML_INTEGER = "tag:yaml.org,2002:int"
_YAML_FLOAT = "tag:yaml.org,2002:float"
_YAML_TIMESTAMP = "tag:yaml.org,2002:timestamp"
_INPUT_SCALAR_SPELLINGS = {
    _YAML_INTEGER: re.compile(r"0|[1-9][0-9]*"),
    "tag:yaml.org,2002:bool": re.compile(r"true|false", re.IGNORECASE),
    "tag:yaml.org,2002:null": re.compile(r"null|~|", re.IGNORECASE),
    _YAML_TIMESTAMP: DATE,
}


def read_text(path: Path | Traversable) -> str:
    try:
        if path.is_dir():
            raise InputError("is_directory", file=path.name)
        if isinstance(path, Path) and path.stat().st_size > MAX_FILE_BYTES:
            raise InputError("file_too_large", file=path.name)
        with path.open("rb") as stream:
            data = stream.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise InputError("file_too_large", file=path.name)
        return data.decode("utf-8")
    except FileNotFoundError:
        raise InputError("file_not_found", file=path.name) from None
    except IsADirectoryError:
        raise InputError("is_directory", file=path.name) from None
    except UnicodeDecodeError:
        raise InputError("not_utf8", file=path.name) from None
    except (OSError, ValueError):
        raise InputError("not_readable", file=path.name) from None


def _has_at_sign(value: object) -> bool:
    if isinstance(value, str):
        return "@" in value
    if isinstance(value, dict):
        return any("@" in key or _has_at_sign(item) for key, item in value.items())
    return isinstance(value, list) and any(_has_at_sign(item) for item in value)


def parse_json(text: str, file_name: str) -> object:
    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        row = dict(pairs)
        if len(row) != len(pairs):
            raise InputError("duplicate_key_document", file=file_name)
        return row

    def finite_float(literal: str) -> float:
        number = float(literal)
        if not isfinite(number):
            raise InputError("non_finite_number_document", file=file_name)
        return number

    try:
        data = json.loads(
            text,
            object_pairs_hook=object_pairs,
            # Keep oversized integers invalid until validation can name their fields.
            parse_int=lambda literal: (
                int(literal) if len(literal) <= _JSON_INTEGER_LENGTH else object()
            ),
            parse_float=finite_float,
            parse_constant=finite_float,
        )
        if _has_at_sign(data):
            raise InputError("contains_at_document", file=file_name)
    except json.JSONDecodeError as error:
        raise InputError("invalid_json", file=file_name, line=error.lineno) from None
    except (ValueError, RecursionError):
        raise InputError("invalid_json_document", file=file_name) from None
    return data


def _check_yaml(
    root: Node,
    file_name: str,
    fields: FieldNames | None,
    scalar_fields: ScalarFields,
    *,
    strict_scalars: bool,
) -> None:
    checked: dict[Node, bool] = {}

    def fail(node: Node, code: str, field: str | None = None) -> Never:
        raise InputError(code, file=file_name, line=node.start_mark.line + 1, field=field)

    def visit(node: Node, path: _SchemaPath = (), field: str | None = None) -> None:
        if node in checked:
            if not checked[node]:
                fail(node, "invalid_yaml")
            return
        checked[node] = False
        if isinstance(node, MappingNode):
            allowed = fields.get(path) if fields is not None else None
            keys: set[str] = set()
            unknown = None
            for key, item in node.value:
                # Text keys avoid implicit aliases such as true and 1 for the same key.
                if not isinstance(key, ScalarNode) or key.tag != _YAML_TEXT:
                    fail(key, "invalid_yaml")
                name = key.value
                member = None
                if allowed is not None and name in allowed:
                    member = f"{field}.{name}" if field else name
                if name in keys:
                    fail(key, "duplicate_key_field" if member else "duplicate_key", member)
                keys.add(name)
                if allowed is not None and member is None:
                    if unknown is None:
                        unknown = key
                    continue
                if fields is not None and "@" in name:
                    fail(key, "contains_at_line")
                visit(item, (*path, name), member)
            if unknown is not None:
                fail(unknown, "contains_at_line" if "@" in unknown.value else "unknown_field")
        elif isinstance(node, SequenceNode):
            for index, item in enumerate(node.value):
                visit(item, (*path, None), f"{field}[{index}]" if field else None)
        else:
            if fields is not None and "@" in node.value:
                fail(node, "contains_at_field" if field else "contains_at_line", field)
            expected = scalar_fields.get(path)
            if node.tag == _YAML_FLOAT:
                number = yaml.safe_load(f"!!float {json.dumps(node.value, ensure_ascii=False)}")
                if not isfinite(number):
                    fail(node, "non_finite_number_field" if field else "non_finite_number", field)
            elif strict_scalars:
                pattern = _INPUT_SCALAR_SPELLINGS.get(node.tag)
                if node.tag == _YAML_TEXT and expected == "integer":
                    fail(node, "invalid_integer_field" if field else "invalid_integer", field)
                if pattern is not None and not pattern.fullmatch(node.value):
                    if node.tag == _YAML_INTEGER:
                        fail(node, "invalid_integer_field" if field else "invalid_integer", field)
                    fail(node, "invalid_scalar_field" if field else "invalid_scalar", field)
                if node.tag == _YAML_INTEGER and len(node.value) > _COUNT_DIGITS:
                    fail(node, "invalid_field" if field else "invalid_field_document", field)
                if node.tag == _YAML_TIMESTAMP or (
                    expected == "date" and DATE.fullmatch(node.value)
                ):
                    try:
                        date.fromisoformat(node.value)
                    except ValueError:
                        fail(node, "invalid_scalar_field" if field else "invalid_scalar", field)
                if expected == "quoted" and node.tag == _YAML_TEXT and node.style not in ("'", '"'):
                    fail(node, "money_not_quoted_field", field)
        checked[node] = True

    visit(root)


def parse_yaml(
    text: str,
    file_name: str,
    *,
    allow_aliases: bool = True,
    fields: FieldNames | None = None,
    scalar_fields: ScalarFields | None = None,
    strict_scalars: bool = False,
) -> object:
    try:
        if not allow_aliases:
            for token in yaml.scan(text, Loader=yaml.SafeLoader):
                if isinstance(token, (AliasToken, AnchorToken)):
                    raise InputError("yaml_anchors", file=file_name, line=token.start_mark.line + 1)
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            _check_yaml(node, file_name, fields, scalar_fields or {}, strict_scalars=strict_scalars)
        return yaml.safe_load(text)
    except yaml.reader.ReaderError as error:
        line = len(re.split(r"\r\n|[\r\n\x85\u2028\u2029]", text[: error.position]))
        raise InputError("invalid_yaml", file=file_name, line=line) from None
    except yaml.constructor.ConstructorError:
        raise InputError("invalid_yaml_document", file=file_name) from None
    except yaml.MarkedYAMLError as error:
        raise InputError("invalid_yaml", file=file_name, line=error.problem_mark.line + 1) from None
    # PyYAML constructors can raise LookupError or AttributeError for malformed scalars.
    except (ValueError, OverflowError, RecursionError, LookupError, AttributeError):
        raise InputError("invalid_yaml_document", file=file_name) from None
