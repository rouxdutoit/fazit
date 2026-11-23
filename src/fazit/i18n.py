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
        code = "unsupported_language_option" if file is None else "unsupported_language"
        raise InputError(code, file=file, field=field)
    return value


def load_locale(lang: str, *, copy: bool = True) -> dict:
    strings = _read_locale(check_language(lang))
    return deepcopy(strings) if copy else strings


@lru_cache(maxsize=2)
def _read_locale(lang: str) -> dict:
    locale = files("fazit").joinpath("locales", f"{lang}.yaml")
    strings = parse_yaml(read_text(locale), locale.name)
    if not isinstance(strings, dict):
        raise InputError("invalid_field_document", file=locale.name)
    return strings


def error_sentence(strings: dict, error: InputError, *, input_role: str | None = None) -> str:
    template = strings["errors"][error.code]
    file_name = error.file or ""
    if input_role is not None and "@" in file_name:
        cli = strings["cli"]
        file_name = cli["private_input_file"][input_role]
        template = cli["private_input_errors"].get(error.code, template)
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


def _money_parts(amount: Fraction | Decimal, *, whole: bool = False) -> tuple[str, int, int]:
    scale = 1 if whole else 100
    rounded = int(abs(Fraction(amount)) * scale + Fraction(1, 2))
    units, fraction = divmod(rounded, scale)
    return "-" if amount < 0 and rounded else "", units, fraction


def plain_amount(amount: Fraction | None) -> str:
    if amount is None:
        return "unknown"
    sign, whole, fraction = _money_parts(amount)
    return f"{sign}{whole}.{fraction:02d}"


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

    def money(self, amount: Fraction | Decimal, currency: str, *, whole: bool = False) -> str:
        sign, units, fraction = _money_parts(amount, whole=whole)
        settings = self.strings["format"]
        display = f"{'−' if sign else ''}{self.integer(units)}"
        if fraction:
            display += f"{settings['decimal_separator']}{fraction:02d}"
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
        formatted = self.strings["format"][layout].format(
            day=day.day, month=self.strings[months][day.month - 1], year=day.year
        )
        return formatted.replace(" ", "\N{NO-BREAK SPACE}")

    def date(self, value: str) -> str:
        return self._date(date.fromisoformat(value[:10]), "date", "months")

    def period(self, value: str) -> str:
        start, end = (date.fromisoformat(day) for day in value.split("/"))
        first_layout = "day_and_month" if start.year == end.year else "date"
        return self.strings["format"]["period"].format(
            start=self._date(start, first_layout, "short_months"),
            end=self._date(end, "date", "short_months"),
        )
