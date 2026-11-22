# SPDX-License-Identifier: AGPL-3.0-or-later
from copy import deepcopy
from datetime import date
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
from importlib.resources import files

from .errors import InputError
from .parsing import parse_yaml, read_text

SUPPORTED_LANGUAGES = ("en", "de")
DEFAULT_LANGUAGE = "en"


def check_language(value: object, *, file: str | None = None, field: str = "--lang") -> str:
    if not isinstance(value, str) or value not in SUPPORTED_LANGUAGES:
        raise InputError("unsupported_language", file=file, field=field)
    return value


def load_locale(lang: str) -> dict:
    check_language(lang)
    locale = files("fazit").joinpath("locales", f"{lang}.yaml")
    return deepcopy(_parse_locale(read_text(locale), locale.name))


@lru_cache(maxsize=2)
def _parse_locale(text: str, file_name: str) -> dict:
    strings = parse_yaml(text, file_name)
    if not isinstance(strings, dict):
        raise InputError("invalid_field", file=file_name, field="$")
    return strings


def error_sentence(strings: dict, error: InputError, *, input_role: str | None = None) -> str:
    code = error.code
    if error.file is None:
        code += "_option"
    elif error.line is not None and error.field is not None:
        code += "_field"
    elif error.field == "$" and code in ("invalid_field", "contains_at"):
        code += "_document"
    template = strings["errors"][code]
    file_name = error.file or ""
    if input_role is not None and "@" in file_name:
        cli = strings["cli"]
        file_name = cli["private_input_file"][input_role]
        template = cli["private_input_errors"].get(code, template)
    return template.format(
        file=escape_controls(file_name),
        field=escape_controls(error.field or ""),
        line=error.line,
        **error.details,
    )


def escape_controls(text: str) -> str:
    return "".join(
        char if char.isprintable() else char.encode("unicode_escape").decode("ascii")
        for char in text
    )


def code_label(strings: dict, group: str, code: str) -> str:
    labels = strings[group]
    return labels.get(code, code) if group == "collector" else labels[code]


def reason_text(strings: dict, code: str) -> tuple[str, str]:
    reasons = strings["reason"]
    reason = reasons.get(code, reasons["not_recognised"])
    return reason["label"], reason["fix"]


class Formatter:
    def __init__(self, lang: str) -> None:
        self.strings = load_locale(lang)

    def integer(self, value: int) -> str:
        return f"{value:,}".replace(",", self.strings["format"]["thousands_separator"])

    def number(self, value: Decimal) -> str:
        whole, point, fraction = f"{value:,f}".partition(".")
        settings = self.strings["format"]
        whole = whole.replace(",", settings["thousands_separator"])
        return f"{whole}{settings['decimal_separator']}{fraction}" if point else whole

    def money(self, amount: Fraction | Decimal, currency: str) -> str:
        cents = int(abs(Fraction(amount)) * 100 + Fraction(1, 2))
        whole, fraction = divmod(cents, 100)
        sign = "-" if amount < 0 and cents else ""
        settings = self.strings["format"]
        display = (
            f"{sign}{self.number(Decimal(whole))}{settings['decimal_separator']}{fraction:02d}"
        )
        return settings["money"].format(amount=display, currency=currency).strip()

    def storage(self, value: int, *, lower_bound: bool = False) -> str:
        settings = self.strings["format"]
        units = settings["storage_units"]
        divisor, index = 1, 0
        while value >= divisor * 1000 and index < len(units) - 1:
            divisor *= 1000
            index += 1
        rounding = 0 if lower_bound else divisor // 2
        tenths = (value * 10 + rounding) // divisor
        whole, fraction = divmod(tenths, 10)
        return f"{self.integer(whole)}{settings['decimal_separator']}{fraction} {units[index]}"

    def _date(self, day: date, layout: str, months: str) -> str:
        return self.strings["format"][layout].format(
            day=day.day, month=self.strings[months][day.month - 1], year=day.year
        )

    def date(self, value: str) -> str:
        return self._date(date.fromisoformat(value[:10]), "date", "months")

    def period(self, value: str) -> str:
        start, end = (date.fromisoformat(day) for day in value.split("/"))
        first_layout = "day_and_month" if start.year == end.year else "date"
        return self.strings["format"]["period"].format(
            start=self._date(start, first_layout, "short_months"),
            end=self._date(end, "date", "short_months"),
        )
