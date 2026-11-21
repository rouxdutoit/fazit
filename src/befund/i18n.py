# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date
from decimal import MAX_EMAX, ROUND_HALF_UP, Context, Decimal, localcontext
from importlib.resources import files

from . import PROJECT_NAME
from .errors import InputError
from .parsing import parse_yaml, read_text

SUPPORTED_LANGUAGES = ("en", "de")
DEFAULT_LANGUAGE = "en"


def load_locale(lang: str) -> dict:
    if lang not in SUPPORTED_LANGUAGES:
        raise InputError("unsupported_language", file=PROJECT_NAME, field="--lang")
    locale = files("befund").joinpath("locales", f"{lang}.yaml")
    strings = parse_yaml(read_text(locale), locale.name)
    if not isinstance(strings, dict):
        raise InputError("invalid_field", file=locale.name, field="$")
    return strings


def error_sentence(strings: dict, error: InputError) -> str:
    return strings["errors"][error.code].format(
        file=" ".join(str(error.file or PROJECT_NAME).splitlines()),
        field=" ".join(str(error.field or "$").splitlines()),
        **error.details,
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

    def money(self, amount: Decimal, currency: str) -> str:
        with localcontext(Context(prec=max(3, amount.adjusted() + 4), Emax=MAX_EMAX)):
            rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rounded == 0:
            rounded = rounded.copy_abs()
        template = self.strings["format"]["money"]
        return template.format(amount=self.number(rounded), currency=currency).strip()

    def storage(self, value: int) -> str:
        settings = self.strings["format"]
        units = settings["storage_units"]
        divisor, index = 1, 0
        while value >= divisor * 1000 and index < len(units) - 1:
            divisor *= 1000
            index += 1
        tenths = (value * 10 + divisor // 2) // divisor
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
