# SPDX-License-Identifier: AGPL-3.0-or-later
import json
from importlib.resources.abc import Traversable
from math import isfinite
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

from .errors import InputError


def read_text(path: Path | Traversable) -> str:
    try:
        if path.is_dir():
            raise InputError("is_directory", file=path.name, field="$")
        return path.read_bytes().decode("utf-8")
    except FileNotFoundError:
        raise InputError("file_not_found", file=path.name, field="$") from None
    except IsADirectoryError:
        raise InputError("is_directory", file=path.name, field="$") from None
    except UnicodeDecodeError:
        raise InputError("not_utf8", file=path.name, field="$") from None
    except (OSError, ValueError):
        raise InputError("not_readable", file=path.name, field="$") from None


def reject_at_signs(value: object, file_name: str, field: str = "$") -> None:
    if isinstance(value, str) and "@" in value:
        raise InputError("contains_at", file=file_name, field=field)
    if isinstance(value, dict):
        for index, (key, item) in enumerate(value.items()):
            member = f"{field}[{index}]"
            reject_at_signs(key, file_name, member)
            reject_at_signs(item, file_name, member)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_at_signs(item, file_name, f"{field}[{index}]")


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


def _check_yaml(node: Node, file_name: str, field: str, active: set[Node], seen: set[Node]) -> None:
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
            _check_yaml(item, file_name, member, active, seen)
    elif isinstance(node, SequenceNode):
        for index, item in enumerate(node.value):
            _check_yaml(item, file_name, f"{field}[{index}]", active, seen)
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


def parse_yaml(text: str, file_name: str, *, quoted_fields: tuple[str, ...] = ()) -> object:
    try:
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            _check_yaml(node, file_name, "$", set(), set())
            # YAML can interpret an unquoted amount with a leading zero as text.
            for field in quoted_fields:
                _check_quotes(node, file_name, field)
        return yaml.safe_load(text)
    except (yaml.YAMLError, ValueError, OverflowError, RecursionError, LookupError, AttributeError):
        raise InputError("invalid_yaml", file=file_name, field="$") from None
