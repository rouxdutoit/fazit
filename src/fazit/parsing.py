# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
from collections.abc import Collection
from importlib.resources.abc import Traversable
from math import isfinite
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode
from yaml.tokens import AliasToken, AnchorToken

from .errors import InputError

MAX_FILE_BYTES = 2 * 1024 * 1024
_INPUT_SCALAR_SPELLINGS = {
    "tag:yaml.org,2002:int": re.compile(r"0|[1-9][0-9]*"),
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


def _finite(value: object, file_name: str, field: str) -> None:
    if isinstance(value, float) and not isfinite(value):
        raise InputError("non_finite_number", file=file_name, field=field)


def _json_value(value: object, file_name: str, field: str) -> object:
    if isinstance(value, tuple):
        result: dict[str, object] = {}
        for index, (key, item) in enumerate(value):
            # Keys can contain private text, so use positions in parser errors.
            member = f"{field}[{index}]"
            if key in result:
                raise InputError("duplicate_key", file=file_name, field=member)
            result[key] = _json_value(item, file_name, member)
        return result
    if isinstance(value, list):
        return [_json_value(item, file_name, f"{field}[{i}]") for i, item in enumerate(value)]
    _finite(value, file_name, field)
    return value


def parse_json(text: str, file_name: str) -> object:
    try:
        return _json_value(json.loads(text, object_pairs_hook=tuple), file_name, "$")
    except (ValueError, RecursionError):
        raise InputError("invalid_json", file=file_name, field="$") from None


def _check_yaml(
    node: Node,
    file_name: str,
    field: str,
    active: set[Node],
    seen: set[Node],
    input_keys: Collection[str],
    name: str | None,
) -> None:
    if node in seen:
        return
    if node in active:
        raise InputError("invalid_yaml", file=file_name, field=field)
    active.add(node)
    if isinstance(node, MappingNode):
        keys: set[str] = set()
        for index, (key, item) in enumerate(node.value):
            member = f"{field}[{index}]"
            # Text keys avoid implicit aliases such as true and 1 for the same key.
            if not isinstance(key, ScalarNode) or key.tag != "tag:yaml.org,2002:str":
                raise InputError("invalid_yaml", file=file_name, field=member)
            if key.value in keys:
                raise InputError("duplicate_key", file=file_name, field=member)
            keys.add(key.value)
            child_name = (
                f"{name}.{key.value}".lstrip(".")
                if name is not None and key.value in input_keys
                else None
            )
            _check_yaml(item, file_name, member, active, seen, input_keys, child_name)
    elif isinstance(node, SequenceNode):
        for index, item in enumerate(node.value):
            child_name = f"{name}[{index}]" if name is not None else None
            _check_yaml(item, file_name, f"{field}[{index}]", active, seen, input_keys, child_name)
    elif input_keys and (pattern := _INPUT_SCALAR_SPELLINGS.get(node.tag)):
        # Check spellings before YAML can turn octal counts or on/off into answers.
        if not pattern.fullmatch(node.value):
            raise InputError("invalid_field", file=file_name, field=name or field)
    elif node.tag == "tag:yaml.org,2002:float":
        _finite(yaml.safe_load(f"!!float {json.dumps(node.value)}"), file_name, field)
    active.remove(node)
    seen.add(node)


def _check_quotes(node: Node, file_name: str, field: str) -> None:
    member: Node | None = node
    for part in field.split("."):
        if not isinstance(member, MappingNode):
            return
        member = next((value for key, value in member.value if key.value == part), None)
    if (
        isinstance(member, ScalarNode)
        and member.tag == "tag:yaml.org,2002:str"
        and member.style not in ("'", '"')
    ):
        reject_at_signs(member.value, file_name, field)
        raise InputError("money_not_quoted", file=file_name, field=field)


def parse_yaml(
    text: str,
    file_name: str,
    *,
    quoted_fields: tuple[str, ...] = (),
    allow_aliases: bool = True,
    input_keys: Collection[str] = (),
) -> object:
    try:
        if not allow_aliases and any(
            isinstance(token, (AliasToken, AnchorToken))
            for token in yaml.scan(text, Loader=yaml.SafeLoader)
        ):
            raise InputError("yaml_anchors", file=file_name, field="$")
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            _check_yaml(node, file_name, "$", set(), set(), input_keys, "")
            # YAML can interpret an unquoted amount with a leading zero as text.
            for field in quoted_fields:
                _check_quotes(node, file_name, field)
        return yaml.safe_load(text)
    except (yaml.YAMLError, ValueError, OverflowError, RecursionError, LookupError, AttributeError):
        raise InputError("invalid_yaml", file=file_name, field="$") from None
