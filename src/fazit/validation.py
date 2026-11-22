# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Never, TypeGuard

from .errors import InputError

DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
GUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
IDENTIFIER = re.compile(r"[A-Za-z0-9_]{1,64}")
RULE_ID = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")


def non_negative_integer(value: object) -> TypeGuard[int]:
    return type(value) is int and value >= 0


@dataclass(frozen=True)
class Validator:
    file_name: str

    def fail(self, field: str, code: str = "invalid_field", **details: object) -> Never:
        raise InputError(code, file=self.file_name, field=field or "$", **details) from None

    def fields(
        self,
        value: object,
        field: str,
        required: Collection[str],
        optional: Collection[str] | None = (),
    ) -> dict:
        if not isinstance(value, dict) or (
            optional is not None and value.keys() - {*required, *optional}
        ):
            self.fail(field)
        for name in required:
            if name not in value:
                self.fail(f"{field}.{name}" if field not in ("", "$") else name, "missing_field")
        return value

    def rows(self, value: object, field: str, *, allow_empty: bool = False) -> list[object]:
        if not isinstance(value, list) or (not value and not allow_empty):
            self.fail(field)
        return value

    def matches(self, value: object, field: str, pattern: re.Pattern[str]) -> str:
        if not isinstance(value, str) or not pattern.fullmatch(value):
            self.fail(field)
        return value

    def choice(
        self, value: object, field: str, allowed: Collection[str], code: str = "invalid_code"
    ) -> str:
        if not isinstance(value, str) or value not in allowed:
            self.fail(field, code)
        return value

    def count(self, value: object, field: str) -> int:
        if not non_negative_integer(value):
            self.fail(field)
        return value

    def optional_count(self, value: object, field: str) -> int | None:
        return None if value is None else self.count(value, field)

    def guid(self, value: object, field: str) -> str:
        return self.matches(value, field, GUID).lower()

    def calendar_date(self, value: object, field: str) -> date:
        if type(value) is date:
            return value
        text = self.matches(value, field, DATE)
        try:
            return date.fromisoformat(text)
        except ValueError:
            self.fail(field)

    def bilingual(self, value: object, field: str) -> Mapping[str, str]:
        text = self.fields(value, field, ("en", "de"))
        for lang, sentence in text.items():
            if not isinstance(sentence, str) or not sentence.strip():
                self.fail(f"{field}.{lang}")
        return MappingProxyType(text)
