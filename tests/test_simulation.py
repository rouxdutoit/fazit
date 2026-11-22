# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import replace
from fractions import Fraction
from html import unescape
from math import prod
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from helpers import (
    ADDRESS,
    CSS_RESOURCE,
    NAME,
    RESOURCE_ATTRIBUTES,
    RESOURCE_ELEMENTS,
    SINGLE_TOKENS,
    TOKEN,
    ReportDocument,
    assert_no_private_text,
    audit_environment,
    readiness_row,
    rebuild_report,
    report_section,
    runner,
    sample_inputs_path,
    sample_scan_path,
)
from hypothesis import example, given
from hypothesis import strategies as st
from tenants import (
    CATALOGUE,
    DAY,
    EMPTY_SCAN,
    PLANS,
    STATUS_RULES,
    Tenant,
    degraded_tenants,
    tenants,
)

from fazit.cli import app
from fazit.evidence import provided_findings
from fazit.i18n import load_locale
from fazit.inputs import load_inputs_text
from fazit.licences import scan_to_json
from fazit.model import Collector, Coverage, Finding, load_scan
from fazit.status import STATUSES

CSP = (
    "default-src 'none'; style-src 'unsafe-inline'; font-src data:; "
    "base-uri 'none'; form-action 'none'"
)
MACROS = Finding(
    "office_files.kind.macro",
    "office_files",
    0,
    "files",
    "measured",
    "office_files",
    "sample.office_files",
    DAY,
    None,
    Coverage("complete"),
    None,
)
OFFICE = Tenant(
    replace(
        EMPTY_SCAN,
        collectors=(Collector("office_files", "ok", None, ()),),
        findings=(MACROS,),
    ),
    {"provided_counts": {MACROS.id: 1}},
    "de",
    "nextcloud",
)
OFFICE_PARTIAL = replace(
    OFFICE, scan=replace(OFFICE.scan, findings=(replace(MACROS, coverage=Coverage("partial")),))
)
NONPROFIT = load_scan(sample_scan_path("nonprofit"), CATALOGUE)
LICENSED_ACCOUNTS = NONPROFIT.finding("directory.licensed_user_count")
assert LICENSED_ACCOUNTS is not None and NONPROFIT.licences is not None
UNASSIGNED = Tenant(
    replace(
        NONPROFIT,
        collectors=tuple(
            row for row in NONPROFIT.collectors if row.id in {"directory", "licences"}
        ),
        findings=(LICENSED_ACCOUNTS,),
        licences=replace(
            NONPROFIT.licences, products=(replace(NONPROFIT.licences.products[0], assigned=0),)
        ),
    ),
    {"confirmations": {"telephony.in_use": False}},
    "en",
    "opendesk",
)
DIRECTORY_DENIED = replace(
    UNASSIGNED,
    scan=replace(
        UNASSIGNED.scan,
        collectors=tuple(
            replace(row, status="skipped", reason="permission_denied")
            if row.id == "directory"
            else row
            for row in UNASSIGNED.scan.collectors
        ),
        findings=(
            replace(
                LICENSED_ACCOUNTS,
                value=None,
                provenance="unknown",
                coverage=None,
                missing_reason="permission_denied",
            ),
        ),
    ),
)


def _write_tenant(tenant: Tenant, directory: Path) -> tuple[Path, Path | None]:
    scan = directory / "scan.json"
    scan.write_text(scan_to_json(tenant.scan, plans=PLANS), encoding="utf-8")
    if tenant.inputs is None:
        return scan, None
    inputs = directory / "inputs.yaml"
    inputs.write_text(yaml.safe_dump(tenant.inputs), encoding="utf-8")
    return scan, inputs


def _render(tenant: Tenant) -> str:
    with TemporaryDirectory() as temporary:
        work = Path(temporary).resolve()
        scan, inputs = _write_tenant(tenant, work)
        return rebuild_report(
            scan, work / "out", tenant.lang, profile=tenant.profile, inputs=inputs
        )


def _statuses(html: str) -> dict[str, str]:
    readiness = report_section(html, "readiness")
    statuses = dict(re.findall(r'<tr data-workload="([^"]+)" data-status="([^"]+)"', readiness))
    assert tuple(statuses) == CATALOGUE.workload_ids
    assert set(statuses.values()) <= set(STATUSES)
    return statuses


@given(tenant=tenants())
@example(tenant=OFFICE)
def test_incomplete_required_evidence_prevents_ready(tenant: Tenant) -> None:
    html = _render(tenant)
    statuses = _statuses(html)
    recorded = {finding.id: finding for finding in tenant.scan.findings}
    supplied = {}
    if tenant.inputs is not None:
        inputs = load_inputs_text(yaml.safe_dump(tenant.inputs), "inputs.yaml", CATALOGUE)
        supplied = {finding.id: finding for finding in provided_findings(inputs, CATALOGUE)}
    unavailable = {row.id for row in tenant.scan.collectors if row.status != "ok"}
    licences = tenant.scan.licences
    readiness = report_section(html, "readiness")
    for key, answer in supplied.items():
        finding = recorded.get(key)
        if (
            finding
            and finding.provenance == "measured"
            and finding.coverage.kind == "complete"
            and (answer.coverage is None or answer.coverage.kind == "complete")
            and finding.value != answer.value
        ):
            row = readiness_row(readiness, finding.workload)
            assert 'data-reason="confirmation_conflict"' in row
            assert statuses[finding.workload] != "ready"
    for workload, block in STATUS_RULES.workloads.items():
        row = readiness_row(readiness, workload)
        gaps = re.findall(r'<li data-missing="([^"]+)">(.*?)</li>', row, re.S)
        assert ("data-incomplete" in row) == bool(gaps)
        if gaps:
            assert statuses[workload] != "ready"
            assert all("data-reason=" in text for _, text in gaps)
        listed = {key for key, _ in gaps}
        for condition in block.ready:
            key = condition.finding
            entry = CATALOGUE.finding(key)
            if entry is None:
                complete = (
                    licences is not None
                    and licences.coverage.kind == "complete"
                    and licences.collector not in unavailable
                )
                if (
                    complete
                    and (key != "licences.product_count" or not licences.products)
                    and not any(product.assigned for product in licences.products)
                ):
                    accounts = recorded.get("directory.licensed_user_count")
                    complete = (
                        accounts is not None
                        and accounts.value == 0
                        and accounts.coverage is not None
                        and accounts.coverage.kind == "complete"
                        and accounts.collector not in unavailable
                    )
            else:
                complete = not any(
                    method in unavailable for method, _ in entry.measured_by
                ) and any(
                    finding is not None
                    and finding.value is not None
                    and condition.provenance in (None, finding.provenance)
                    and (finding.coverage is None or finding.coverage.kind == "complete")
                    for finding in (recorded.get(key), supplied.get(key))
                )
            if not complete:
                assert key in listed, (workload, key)


@given(pair=degraded_tenants())
@example(pair=(OFFICE, OFFICE_PARTIAL))
@example(pair=(UNASSIGNED, DIRECTORY_DENIED))
def test_worse_collection_never_improves_status(pair: tuple[Tenant, Tenant]) -> None:
    original, degraded = pair
    if original == degraded:
        return
    before = _statuses(_render(original))
    after = _statuses(_render(degraded))
    for workload, previous in before.items():
        current = after[workload]
        # Losing a measurement can make an existing manual answer establish a problem.
        if previous == "unknown":
            assert current != "ready", workload
        elif current != "unknown":
            assert STATUSES.index(current) >= STATUSES.index(previous), (
                workload,
                previous,
                current,
            )


def _plant(node: object, private: tuple[str, ...]) -> None:
    if isinstance(node, list):
        for child in node:
            _plant(child, private)
    elif isinstance(node, dict):
        for child in node.values():
            _plant(child, private)
        for marker in private:
            node[f"extra field {marker}"] = {"payload": marker}


@given(tenant=tenants())
def test_person_data_stays_out_of_report_outputs(tenant: Tenant) -> None:
    with TemporaryDirectory() as temporary:
        work = Path(temporary).resolve()
        scan, inputs = _write_tenant(tenant, work)
        document = json.loads(scan.read_bytes())
        document["findings"].append({"id": NAME, "value": TOKEN})
        if document["licences"] is not None:
            products = document["licences"]["products"]
            if products:
                products[0].update(sku_part_number=SINGLE_TOKENS[1], sku_guid=None)
            for product in products:
                product["service_plans"].append({"name": SINGLE_TOKENS[0], "guid": None})
        _plant(document, (NAME, TOKEN))
        out = work / "out"
        command = ["report", str(scan), "--lang", tenant.lang, "--profile", tenant.profile]
        if inputs is not None:
            command.extend(("--inputs", str(inputs)))
        scan.write_text(json.dumps(document), encoding="utf-8")
        result = runner.invoke(app, [*command, "--out", str(out)])
        assert result.exit_code == 0 and not result.stderr, result.output
        assert list(out.iterdir()) == [Path(result.stdout.strip())]
        markers = (NAME, TOKEN, *SINGLE_TOKENS)
        assert_no_private_text(result, out, *markers)
        clean = scan_to_json(load_scan(scan, CATALOGUE), plans=PLANS)
        assert all(text not in clean for text in markers)

        _plant(document, (ADDRESS,))
        scan.write_text(json.dumps(document), encoding="utf-8")
        rejected = work / "rejected"
        result = runner.invoke(app, [*command, "--out", str(rejected)])
        assert result.exit_code == 2 and not result.stdout and not rejected.exists(), result.output
        assert len(result.stderr.splitlines()) == 1
        assert_no_private_text(result, rejected, ADDRESS, *markers)


@given(tenant=tenants(), compare_processes=st.just(False))
@example(tenant=OFFICE, compare_processes=True)
@example(
    tenant=Tenant(
        load_scan(sample_scan_path("town"), CATALOGUE),
        yaml.safe_load(sample_inputs_path("town").read_text(encoding="utf-8")),
        "en",
        "opendesk",
    ),
    compare_processes=True,
)
def test_same_tenant_produces_identical_bytes(tenant: Tenant, compare_processes: bool) -> None:
    with TemporaryDirectory() as temporary:
        work = Path(temporary).resolve()
        scan, inputs = _write_tenant(tenant, work)
        copies = []
        for index in range(2):
            out = work / str(index)
            rebuild_report(scan, out, tenant.lang, profile=tenant.profile, inputs=inputs)
            (report,) = out.iterdir()
            copies.append(report.read_bytes())
        assert copies[0] == copies[1]
        if compare_processes:
            env, audit_log = audit_environment(work)
            command = ["report", str(scan), "--lang", tenant.lang, "--profile", tenant.profile]
            if inputs is not None:
                command.extend(("--inputs", str(inputs)))
            for seed in ("17", "83"):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "from fazit.cli import main; main()",
                        *command,
                        "--out",
                        str(work / seed),
                    ],
                    env={**env, "PYTHONHASHSEED": seed},
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                assert result.returncode == 0 and not result.stderr, result.stderr
                assert Path(result.stdout.strip()).read_bytes() == copies[0]
            assert not audit_log.read_bytes()


type Amount = Fraction | None
type CostBlocks = dict[str, dict[str, Amount]]


def _product(*factors: Amount) -> Amount:
    if 0 in factors:
        return Fraction(0)
    if None in factors:
        return None
    return prod(factor for factor in factors if factor is not None)


def _sum(amounts: Iterable[Amount]) -> Amount:
    known = tuple(amounts)
    return None if None in known else sum((x for x in known if x is not None), Fraction(0))


def _exit_blocks(target: dict, current: Amount, other_it: Amount) -> CostBlocks:
    values = {name: Fraction(value) for name, value in target.items()}
    months = values.get("parallel_running_months")
    remaining = None if months is None else 60 - months
    return {
        "running": {
            "retained_licences": _product(
                values.get("retained_microsoft_licences_per_year"), remaining, Fraction(1, 12)
            ),
            "hosting": _product(
                values.get("hosting_per_user_per_month"), values.get("users"), Fraction(60)
            ),
            "operations": _product(values.get("operations_per_year"), Fraction(5)),
            "other_recurring": _product(values.get("other_recurring_per_year"), Fraction(5)),
            "other_it": other_it,
        },
        "direct_project": {
            "one_time_migration": values.get("one_time_migration"),
            "application_adaptation": values.get("application_adaptation"),
            "external_advice": values.get("external_advice"),
            "training": _product(
                values.get("training_days_per_person"),
                values.get("training_day_rate"),
                values.get("training_staff"),
            ),
        },
        "productivity_loss": {"productivity_loss": values.get("productivity_loss")},
        "parallel_running": {"parallel_running": _product(current, months, Fraction(1, 12))},
    }


def _cost_cells(row: str) -> list[str]:
    return [unescape(cell).strip() for cell in re.findall(r"<td\b[^>]*>([^<]*)</td>", row)]


def _display(amount: Amount, strings: dict, currency: str) -> str:
    if amount is None:
        return strings["status"]["unknown"]
    cents = int(abs(amount) * 100 + Fraction(1, 2))
    whole, decimal = divmod(cents, 100)
    settings = strings["format"]
    sign = "-" if amount < 0 and cents else ""
    grouped = f"{whole:,}".replace(",", settings["thousands_separator"])
    number = f"{sign}{grouped}{settings['decimal_separator']}{decimal:02d}"
    return settings["money"].format(amount=number, currency=currency).strip()


@given(tenant=tenants())
def test_report_costs_reconcile_against_exact_fractions(tenant: Tenant) -> None:
    inputs = tenant.inputs or {}
    strings = load_locale(tenant.lang)
    currency = inputs.get("currency", "")
    current = {name: Fraction(value) for name, value in inputs.get("current_costs", {}).items()}
    licences = current.get("microsoft_licences_per_year")
    other_it = _product(current.get("other_it_per_year"), Fraction(5))
    stay = {
        "running": {"microsoft_licences": _product(licences, Fraction(5)), "other_it": other_it}
    }
    scenarios = [
        stay,
        *(
            _exit_blocks(inputs.get("target_costs", {}).get(id, {}), licences, other_it)
            for id in ("partial_exit", "full_exit")
        ),
    ]
    html = report_section(_render(tenant), "costs")
    assert html.count("data-invented-amounts") == (2 if inputs.get("amounts_are_invented") else 0)
    groups = dict(re.findall(r'<tbody data-block="([^"]+)"[^>]*>(.*?)</tbody>', html, re.S))
    assert groups.keys() == scenarios[1].keys()
    totals = [[], [], []]
    for block, body in groups.items():
        lines = [scenario.get(block, {}) for scenario in scenarios]
        rows = dict(re.findall(r'<tr [^>]*data-cost-line="([^"]+)"[^>]*>(.*?)</tr>', body, re.S))
        assert rows.keys() == set().union(*lines)
        for name, row in rows.items():
            assert _cost_cells(row) == [
                _display(line[name], strings, currency)
                if name in line
                else strings["costs"]["not_applicable"]
                for line in lines
            ]
        subtotals = [_sum(line.values()) for line in lines]
        (subtotal,) = re.findall(r'<tr class="subtotals"[^>]*>(.*?)</tr>', body, re.S)
        assert _cost_cells(subtotal) == [_display(value, strings, currency) for value in subtotals]
        for scenario_total, subtotal_value in zip(totals, subtotals, strict=True):
            scenario_total.append(subtotal_value)
    results = [_sum(blocks) for blocks in totals]
    stay_total = results[0]
    differences = [
        None if amount is None or stay_total is None else amount - stay_total for amount in results
    ]
    ((total_row, difference_row),) = re.findall(
        r'<tr class="totals"[^>]*>(.*?)</tr>\s*<tr[^>]*>(.*?)</tr>', html, re.S
    )
    assert _cost_cells(total_row) == [_display(value, strings, currency) for value in results]
    assert _cost_cells(difference_row) == [
        _display(value, strings, currency) for value in differences
    ]


@given(tenant=tenants())
def test_generated_reports_keep_the_offline_csp(tenant: Tenant) -> None:
    document = ReportDocument(_render(tenant))
    policies = []
    for tag, attrs in document.tags:
        assert tag not in RESOURCE_ELEMENTS
        assert not (RESOURCE_ATTRIBUTES & attrs.keys())
        assert all(not name.startswith("on") for name in attrs)
        for name in ("href", "xlink:href"):
            assert name not in attrs or (attrs[name] or "").startswith("#")
        assert not CSS_RESOURCE.search(attrs.get("style") or "")
        if tag == "meta":
            directive = (attrs.get("http-equiv") or "").lower().strip()
            assert directive != "refresh"
            if directive == "content-security-policy":
                policies.append(attrs["content"])
    assert policies == [CSP]
