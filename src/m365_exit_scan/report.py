# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date
from functools import partial
from importlib.resources import files

from jinja2 import Environment, StrictUndefined

from . import PROJECT_NAME, REPOSITORY_URL, __version__
from .catalogue import Catalogue, FindingEntry, load_catalogue
from .errors import InputError
from .i18n import SUPPORTED_LANGUAGES, Formatter, code_label, reason_text
from .model import Coverage, Finding, Scan
from .parsing import read_text

SECTION_ORDER = (
    "header",
    "found",
    "costs",
    "readiness",
    "moves",
    "attention",
    "path",
    "appendix",
    "footer",
)


def report_file_name(generated_at: str, *, lang: str) -> str:
    if lang not in SUPPORTED_LANGUAGES:
        raise InputError("unsupported_language", file=PROJECT_NAME, field="--lang")
    return f"report-{date.fromisoformat(generated_at[:10]).isoformat()}-{lang}.html"


def _coverage_text(coverage: Coverage | None, formatter: Formatter) -> str:
    strings = formatter.strings
    if coverage is None:
        return strings["common"]["unavailable"]
    labels = strings["coverage"]
    parts = [labels[coverage.kind]]
    if coverage.scanned is not None and coverage.total is not None:
        parts.append(
            labels["scanned_of"].format(
                scanned=formatter.integer(coverage.scanned), total=formatter.integer(coverage.total)
            )
        )
    elif coverage.scanned is not None:
        parts.append(labels["scanned"].format(scanned=formatter.integer(coverage.scanned)))
    elif coverage.total is not None:
        parts.append(labels["total"].format(total=formatter.integer(coverage.total)))
    if coverage.failed is not None:
        parts.append(labels["failed"].format(failed=formatter.integer(coverage.failed)))
    return ", ".join(parts)


def _value_text(entry: FindingEntry, finding: Finding, formatter: Formatter) -> str:
    strings = formatter.strings
    value = finding.value
    if isinstance(value, bool):
        return strings["common"]["yes" if value else "no"]
    if isinstance(value, int) and entry.type == "bytes":
        return formatter.storage(value)
    if isinstance(value, int):
        text = formatter.integer(value)
    else:
        text = value if value is not None else strings["common"]["unavailable"]
    if finding.unit is not None:
        text = f"{text} {code_label(strings, 'units', finding.unit)}"
    if (
        isinstance(value, int)
        and finding.coverage is not None
        and finding.coverage.kind == "partial"
    ):
        key = "partial_positive" if value > 0 else "partial_zero"
        return strings["found"][key].format(value=text)
    return text


def _label(strings: dict, label: str) -> str:
    group, name = label.split(".", 1)
    return strings[group][name]


def render_report(scan: Scan, *, lang: str, catalogue: Catalogue | None = None) -> str:
    formatter = Formatter(lang)
    strings = formatter.strings
    catalogue = catalogue if catalogue is not None else load_catalogue()
    by_id = {finding.id: finding for finding in scan.findings}
    by_workload = {workload.id: [] for workload in catalogue.workloads}
    headlines = []
    for entry in catalogue.findings:
        finding = by_id.get(entry.id)
        if finding is not None:
            by_workload[entry.workload].append((entry, finding))
        if entry.headline:
            headlines.append((entry, finding))

    source = files("m365_exit_scan").joinpath("templates", "report.html.j2")
    template = Environment(autoescape=True, undefined=StrictUndefined).from_string(
        read_text(source)
    )
    return template.render(
        scan=scan,
        lang=lang,
        strings=strings,
        label=partial(_label, strings),
        code_label=partial(code_label, strings),
        reason_text=partial(reason_text, strings),
        value_text=partial(_value_text, formatter=formatter),
        coverage_text=partial(_coverage_text, formatter=formatter),
        format=formatter,
        headlines=headlines,
        groups=[(workload, by_workload[workload.id]) for workload in catalogue.workloads],
        project_name=PROJECT_NAME,
        repository_url=REPOSITORY_URL,
        tool_version=__version__,
    )
