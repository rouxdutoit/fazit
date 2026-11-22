# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections.abc import Collection, Mapping
from importlib.resources.abc import Traversable
from math import isfinite
from pathlib import Path
from typing import Never

import yaml
from yaml.events import (
    DocumentStartEvent,
    Event,
    MappingEndEvent,
    MappingStartEvent,
    ScalarEvent,
    SequenceEndEvent,
    SequenceStartEvent,
)
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode
from yaml.tokens import AliasToken, AnchorToken

from .errors import InputError

MAX_FILE_BYTES = 2 * 1024 * 1024
type FieldNames = Mapping[tuple[str | None, ...], Collection[str]]
type _FieldPath = tuple[str | int | None, ...]

_JSON_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[^\s"{}\[\]:,]+|[{}\[\]:,]')
_YAML_TEXT = "tag:yaml.org,2002:str"
_YAML_INTEGER = "tag:yaml.org,2002:int"
_YAML_FLOAT = "tag:yaml.org,2002:float"
_INPUT_SCALAR_SPELLINGS = {
    _YAML_INTEGER: re.compile(r"0|[1-9][0-9]*"),
    "tag:yaml.org,2002:bool": re.compile(r"true|false", re.IGNORECASE),
    "tag:yaml.org,2002:null": re.compile(r"null|~|", re.IGNORECASE),
    "tag:yaml.org,2002:timestamp": re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}"),
}


def read_text(path: Path | Traversable) -> str:
    try:
        if path.is_dir():
            raise InputError("is_directory", file=path.name, field="$")
        if isinstance(path, Path) and path.stat().st_size > MAX_FILE_BYTES:
            raise InputError("file_too_large", file=path.name, field="$")
        with path.open("rb") as stream:
            data = stream.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise InputError("file_too_large", file=path.name, field="$")
        return data.decode("utf-8")
    except FileNotFoundError:
        raise InputError("file_not_found", file=path.name, field="$") from None
    except IsADirectoryError:
        raise InputError("is_directory", file=path.name, field="$") from None
    except UnicodeDecodeError:
        raise InputError("not_utf8", file=path.name, field="$") from None
    except (OSError, ValueError):
        raise InputError("not_readable", file=path.name, field="$") from None


def reject_at_signs(value: object, file_name: str, field: str = "$") -> None:
    seen: set[int] = set()

    def visit(item: object, position: str) -> None:
        if isinstance(item, str) and "@" in item:
            raise InputError("contains_at", file=file_name, field=position)
        if not isinstance(item, (dict, list)) or id(item) in seen:
            return
        seen.add(id(item))
        if isinstance(item, dict):
            for index, (key, child) in enumerate(item.items()):
                member = f"{position}[{index}]"
                visit(key, member)
                visit(child, member)
        else:
            for index, child in enumerate(item):
                visit(child, f"{position}[{index}]")

    visit(value, field)


def _schema_path(path: _FieldPath) -> tuple[str | None, ...]:
    return tuple(part if isinstance(part, str) else None for part in path)


def _field_name(path: _FieldPath, fields: FieldNames) -> str | None:
    if None in path:
        return None
    names = _schema_path(path)
    end = len(names)
    while end and names[end - 1] is None:
        end -= 1
    if not end or names[end - 1] not in fields.get(names[: end - 1], ()):
        return None
    return "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in path)[1:]


def _json_value(value: object) -> object:
    if isinstance(value, tuple):
        row: dict[str, object] = {}
        for key, item in value:
            if key in row:
                raise InputError("duplicate_key")
            row[key] = _json_value(item)
        return row
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, float) and not isfinite(value):
        raise InputError("non_finite_number")
    return value


def _json_location(text: str, code: str, offset: int | None) -> tuple[int, _FieldPath]:
    # The decoder checks syntax. Walk its accepted prefix to recover positions it omits.
    decoder = json.JSONDecoder()
    path: list[str | int | None] = []
    keys: list[set[str]] = []
    for match in _JSON_TOKEN.finditer(text):
        if offset is not None and (match.start() >= offset or match.end() > offset):
            break
        token = match[0]
        if token == "{":
            path.append(None)
            keys.append(set())
        elif token == "[":
            path.append(0)
        elif token in ("}", "]"):
            path.pop()
            if token == "}":
                keys.pop()
        elif token == ",":
            part = path[-1]
            path[-1] = part + 1 if isinstance(part, int) else None
        elif path and path[-1] is None and token.startswith('"'):
            key = decoder.decode(token)
            path[-1] = key
            if code == "duplicate_key" and key in keys[-1]:
                return text.count("\n", 0, match.start()) + 1, tuple(path)
            keys[-1].add(key)
        elif code == "non_finite_number" and token[0] in "-0123456789NI":
            number, _ = decoder.raw_decode(text, match.start())
            if isinstance(number, float) and not isfinite(number):
                return text.count("\n", 0, match.start()) + 1, tuple(path)
    return text.count("\n", 0, offset or 0) + 1, tuple(path)


def parse_json(text: str, file_name: str, *, fields: FieldNames | None = None) -> object:
    try:
        return _json_value(json.loads(text, object_pairs_hook=tuple))
    except json.JSONDecodeError as error:
        code, offset = "invalid_json", error.pos
    except InputError as error:
        code, offset = error.code, None
    except (ValueError, RecursionError):
        raise InputError("invalid_json", file=file_name, line=1) from None
    line, path = _json_location(text, code, offset)
    raise InputError(code, file=file_name, line=line, field=_field_name(path, fields or {}))


def _yaml_error(
    code: str, file_name: str, node: Node, path: _FieldPath, fields: FieldNames
) -> Never:
    raise InputError(
        code, file=file_name, line=node.start_mark.line + 1, field=_field_name(path, fields)
    )


def _check_yaml(
    node: Node,
    file_name: str,
    path: _FieldPath,
    checked: dict[Node, bool],
    fields: FieldNames,
    integer_fields: Collection[tuple[str | None, ...]],
) -> None:
    if node in checked:
        if not checked[node]:
            _yaml_error("invalid_yaml", file_name, node, path, fields)
        return
    checked[node] = False
    if isinstance(node, MappingNode):
        keys: set[str] = set()
        for key, item in node.value:
            # Text keys avoid implicit aliases such as true and 1 for the same key.
            if not isinstance(key, ScalarNode) or key.tag != _YAML_TEXT:
                _yaml_error("invalid_yaml", file_name, key, (), fields)
            child_path = (*path, key.value)
            if key.value in keys:
                _yaml_error("duplicate_key", file_name, key, child_path, fields)
            keys.add(key.value)
            _check_yaml(item, file_name, child_path, checked, fields, integer_fields)
    elif isinstance(node, SequenceNode):
        for index, item in enumerate(node.value):
            _check_yaml(item, file_name, (*path, index), checked, fields, integer_fields)
    elif integer_fields and (pattern := _INPUT_SCALAR_SPELLINGS.get(node.tag)):
        # Check spellings before YAML can turn octal counts or on/off into answers.
        if not pattern.fullmatch(node.value):
            code = "invalid_integer" if node.tag == _YAML_INTEGER else "invalid_scalar"
            _yaml_error(code, file_name, node, path, fields)
    elif node.tag == _YAML_TEXT and integer_fields and _schema_path(path) in integer_fields:
        _yaml_error("invalid_integer", file_name, node, path, fields)
    elif node.tag == _YAML_FLOAT:
        if not isfinite(yaml.safe_load(f"!!float {json.dumps(node.value)}")):
            _yaml_error("non_finite_number", file_name, node, path, fields)
    checked[node] = True


def _yaml_syntax_path(text: str) -> _FieldPath:
    # Events preserve the surrounding keys even if the document cannot be composed.
    events = iter(yaml.parse(text, Loader=yaml.SafeLoader))
    path: list[str | int | None] = []

    def visit(event: Event) -> None:
        if isinstance(event, MappingStartEvent):
            for key in events:
                if isinstance(key, MappingEndEvent):
                    break
                path.append(key.value if isinstance(key, ScalarEvent) else None)
                visit(key)
                visit(next(events))
                path.pop()
        elif isinstance(event, SequenceStartEvent):
            for index, item in enumerate(events):
                if isinstance(item, SequenceEndEvent):
                    break
                path.append(index)
                visit(item)
                path.pop()

    try:
        for event in events:
            if isinstance(event, DocumentStartEvent):
                visit(next(events))
    except yaml.YAMLError:
        return tuple(path)
    except RecursionError:
        return ()
    return ()


def _check_quotes(node: Node, file_name: str, field: str) -> None:
    member: Node | None = node
    for part in field.split("."):
        if not isinstance(member, MappingNode):
            return
        member = next((value for key, value in member.value if key.value == part), None)
    if (
        isinstance(member, ScalarNode)
        and member.tag == _YAML_TEXT
        and member.style not in ("'", '"')
    ):
        reject_at_signs(member.value, file_name, field)
        raise InputError(
            "money_not_quoted", file=file_name, field=field, line=member.start_mark.line + 1
        )


def parse_yaml(
    text: str,
    file_name: str,
    *,
    quoted_fields: tuple[str, ...] = (),
    allow_aliases: bool = True,
    fields: FieldNames | None = None,
    integer_fields: Collection[tuple[str | None, ...]] = (),
) -> object:
    names = fields or {}
    try:
        if not allow_aliases:
            for token in yaml.scan(text, Loader=yaml.SafeLoader):
                if isinstance(token, (AliasToken, AnchorToken)):
                    raise InputError("yaml_anchors", file=file_name, line=token.start_mark.line + 1)
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            _check_yaml(node, file_name, (), {}, names, integer_fields)
            # YAML can interpret an unquoted amount with a leading zero as text.
            for field in quoted_fields:
                _check_quotes(node, file_name, field)
        return yaml.safe_load(text)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        line = mark.line + 1 if mark else text.count("\n", 0, getattr(error, "position", 0)) + 1
        field = _field_name(_yaml_syntax_path(text), names) if names else None
        raise InputError("invalid_yaml", file=file_name, field=field, line=line) from None
    except (ValueError, OverflowError, RecursionError, LookupError, AttributeError):
        raise InputError("invalid_yaml", file=file_name, line=1) from None
