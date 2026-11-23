# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import asdict, replace
from datetime import UTC, datetime, timedelta, timezone
from fractions import Fraction
from html import unescape
from math import prod
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml
from helpers import (
    ADDRESS,
    NAME,
    SINGLE_TOKENS,
    TOKEN,
    ReportDocument,
    assert_no_private_text,
    assert_readiness_order,
    audit_environment,
    offline_policies,
    readiness_row,
    rebuild_report,
    report_section,
    runner,
    sample_inputs_path,
    sample_scan_path,
)
from hypothesis import event, example, given
from hypothesis import strategies as st
from tenants import (
    CATALOGUE,
    EMPTY_SCAN,
    PLANS,
    STAMP,
    STATUS_RULES,
    Tenant,
    degraded_tenants,
    tenants,
)

from fazit.cli import app
from fazit.errors import InputError
from fazit.evidence import combine, provided_findings
from fazit.i18n import error_sentence, load_locale
from fazit.inputs import load_inputs_text
from fazit.licences import licence_findings, scan_to_json
from fazit.mappings import GAP_COVERAGE, PROFILES, load_mapping
from fazit.model import (
    Collector,
    Coverage,
    DirectoryPopulation,
    Finding,
    Product,
    ServicePlan,
    load_scan,
    load_scan_text,
)
from fazit.status import STATUSES, evaluate

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
    STAMP,
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
NONPROFIT_REVIEWED = Tenant(
    NONPROFIT, {"confirmations": {"directory.account_list_reviewed": True}}, "en", "opendesk"
)
NONPROFIT_LICENCES_SKIPPED = replace(
    NONPROFIT_REVIEWED,
    scan=replace(
        NONPROFIT,
        licences=None,
        collectors=tuple(
            replace(collector, status="skipped", reason="collector_skipped")
            if collector.id == "licences"
            else collector
            for collector in NONPROFIT.collectors
        ),
    ),
)
NONPROFIT_LICENSED_COUNT_PARTIAL = replace(
    NONPROFIT_LICENCES_SKIPPED,
    scan=replace(
        NONPROFIT_LICENCES_SKIPPED.scan,
        findings=tuple(
            replace(finding, coverage=Coverage("partial"))
            if finding.id == LICENSED_ACCOUNTS.id
            else finding
            for finding in NONPROFIT.findings
        ),
    ),
)
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
UNDERASSIGNED = replace(
    UNASSIGNED,
    scan=replace(
        UNASSIGNED.scan,
        licences=replace(
            NONPROFIT.licences, products=(replace(NONPROFIT.licences.products[0], assigned=1),)
        ),
    ),
)
OVERASSIGNED = replace(
    UNDERASSIGNED,
    scan=replace(UNDERASSIGNED.scan, findings=(replace(LICENSED_ACCOUNTS, value=0),)),
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
EMPTY_EXPORTS = {
    "mail.storage_bytes": "mail.mailbox_count",
    "mail.item_count": "mail.mailbox_count",
    "onedrive.storage_bytes": "onedrive.account_count",
    "teams.channel_count": "teams.team_count",
}


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
    statuses = dict(
        re.findall(r'<article data-workload="([^"]+)" data-status="([^"]+)"', readiness)
    )
    assert_readiness_order(readiness, CATALOGUE.assessed_workload_ids)
    assert set(statuses.values()) <= set(STATUSES)
    return statuses


@pytest.mark.parametrize(
    "violation",
    [
        "coverage",
        "count",
        "accounts",
        "account-upper-bound",
        "teams",
        "team-total",
        "team-checks",
        "unobserved",
        "rows",
        "time",
        "snapshot-offset",
        "inventory-offset",
        "scan-offset",
        "future-interview-date",
        "future-interview-period",
        *EMPTY_EXPORTS,
    ],
)
@given(size=st.integers(2, 10**6), phone_in_use=st.booleans())
def test_load_rejects_one_inconsistent_field(violation: str, size: int, phone_in_use: bool) -> None:
    scan = json.loads(scan_to_json(NONPROFIT, plans=PLANS))
    findings = {row["id"]: (index, row) for index, row in enumerate(scan["findings"])}
    accounts_index, accounts = findings["directory.licensed_user_count"]
    accounts.update(
        value=size,
        coverage={"kind": "partial", "scanned": size + 1, "failed": 1, "total": size + 2},
    )
    scan["directory_population"]["coverage"] = asdict(Coverage("complete", size + 2, 0, size + 2))
    internal = findings["directory.user_count"][1]
    internal["value"] = 1
    guests = findings["directory.guest_count"][1]
    guests["value"] = size + 1
    if violation == "account-upper-bound":
        internal.update(
            value=0, coverage={"kind": "partial", "scanned": size + 1, "total": size + 2}
        )
        guests["value"] = size
        accounts.update(value=size + 1, coverage={"kind": "complete"})
    findings["teams.team_count"][1].update(
        value=size, coverage={"kind": "partial", "scanned": size, "total": size + 1}
    )
    teams_index, teams = findings["teams.teams_with_guests_count"]
    teams["coverage"]["kind"] = "partial"
    phone_index, phone = findings["telephony.in_use"]
    scan["collectors"].append(
        {
            "id": "telephony",
            "status": "partial",
            "reason": "coverage_partial",
            "permissions_used": [],
        }
    )
    phone.update(
        value=phone_in_use,
        provenance="measured",
        collector="telephony",
        source="sample.telephony",
        collected_at=scan["generated_at"],
        coverage={"kind": "partial", "scanned": 1, "failed": size - 1, "total": size},
    )
    interview_index, interview = findings["device_management.device_count"]
    interview.update(collected_at=None, period="2026-10-01/2026-11-05")
    inventory = scan["licences"]
    inventory["coverage"] = {"kind": "partial", "failed": size - 1, "total": size}
    (product,) = inventory["products"]
    product.update(purchased=size, assigned=size)

    account_field = f"findings[{accounts_index}]"
    team_field = f"findings[{teams_index}]"
    mutations = {
        "coverage": (accounts["coverage"], "failed", 2, f"{account_field}.coverage"),
        "count": (accounts, "value", size + 2, f"{account_field}.value"),
        "accounts": (guests, "value", 0, f"{account_field}.value"),
        "account-upper-bound": (accounts, "value", size + 2, f"{account_field}.value"),
        "teams": (teams, "value", size + 2, f"{team_field}.value"),
        "team-total": (teams["coverage"], "total", size + 2, f"{team_field}.coverage.total"),
        "team-checks": (teams["coverage"], "failed", size + 1, f"{team_field}.value"),
        "unobserved": (phone["coverage"], "scanned", 0, f"findings[{phone_index}].value"),
        "rows": (inventory["coverage"], "failed", size, "licences.coverage.total"),
        "time": (
            accounts,
            "collected_at",
            accounts["collected_at"][:10],
            f"{account_field}.collected_at",
        ),
        "snapshot-offset": (
            accounts,
            "collected_at",
            accounts["collected_at"].removesuffix("Z"),
            f"{account_field}.collected_at",
        ),
        "inventory-offset": (
            inventory,
            "collected_at",
            inventory["collected_at"].removesuffix("Z"),
            "licences.collected_at",
        ),
        "scan-offset": (
            scan,
            "generated_at",
            scan["generated_at"].removesuffix("Z"),
            "generated_at",
        ),
        "future-interview-date": (
            interview,
            "collected_at",
            "2026-11-07",
            f"findings[{interview_index}].collected_at",
        ),
        "future-interview-period": (
            interview,
            "period",
            "2026-10-01/2026-11-07",
            f"findings[{interview_index}].period",
        ),
    }
    if population := EMPTY_EXPORTS.get(violation):
        findings[population][1].update(value=0, coverage={"kind": "complete"})
        for finding_id, parent in EMPTY_EXPORTS.items():
            if parent == population:
                findings[finding_id][1]["value"] = 0
        if population == "teams.team_count":
            teams.update(value=0, coverage={"kind": "complete"})
        index, content = findings[violation]
        if population == "onedrive.account_count":
            content["coverage"] = {"kind": "complete"}
        mutations[violation] = (content, "value", size, f"findings[{index}].value")
    node, key, value, field = mutations[violation]
    file = "inventory.json"
    load_scan_text(json.dumps(scan), file, CATALOGUE)
    node[key] = value
    with pytest.raises(InputError) as caught:
        load_scan_text(json.dumps(scan), file, CATALOGUE)
    assert (caught.value.file, caught.value.field) == (file, field)
    for lang in ("en", "de"):
        sentence = error_sentence(load_locale(lang), caught.value)
        assert file in sentence and field in sentence and len(sentence.splitlines()) == 1


@given(purchased=st.integers(0, 10**6), excess=st.integers(1, 10**6), reverse=st.booleans())
def test_truthful_inventory_loads_with_excess_assignments_and_shared_part_number(
    purchased: int, excess: int, reverse: bool
) -> None:
    products = tuple(
        Product(
            roster.part_number,
            roster.sku_guid,
            purchased,
            purchased + excess,
            tuple(ServicePlan(plan.name, plan.guid) for plan in roster.plans.values()),
        )
        for roster in PLANS.rosters.values()
        if roster.part_number == "MCOPSTN5"
    )
    assert len(products) == 2
    inventory = replace(
        NONPROFIT.licences,
        coverage=Coverage("complete", 2, 0, 2),
        products=products[::-1] if reverse else products,
    )
    scan = replace(NONPROFIT, findings=(), licences=inventory)
    loaded = load_scan_text(scan_to_json(scan, plans=PLANS), "inventory.json", CATALOGUE)
    assert loaded.licences == inventory


@given(rows=st.lists(st.tuples(st.booleans(), st.booleans(), st.booleans()), max_size=60))
@example(rows=[(True, True, True)] * 10 + [(False, True, True)] + [(False, True, False)] * 9)
def test_truthful_filtered_directory_stays_unverified(
    rows: list[tuple[bool, bool, bool]],
) -> None:
    licensed = sum(assigned for _, _, assigned in rows)
    counts = {
        "directory.user_count": sum(internal and included for internal, included, _ in rows),
        "directory.guest_count": sum(not internal and included for internal, included, _ in rows),
        LICENSED_ACCOUNTS.id: licensed,
    }
    findings = tuple(
        replace(finding, value=count, coverage=Coverage("complete", count, 0, count))
        if (count := counts.get(finding.id)) is not None
        else finding
        for finding in NONPROFIT.findings
    )
    (product,) = NONPROFIT.licences.products
    licences = replace(
        NONPROFIT.licences, products=(replace(product, purchased=licensed, assigned=licensed),)
    )
    scan = replace(NONPROFIT, findings=findings, licences=licences, directory_population=None)
    answers = yaml.safe_load(sample_inputs_path("nonprofit").read_text(encoding="utf-8"))
    html = _render(Tenant(scan, answers, "en", "opendesk"))
    statuses = _statuses(html)
    for workload in ("power_platform", "telephony", "identity_access", "security_compliance"):
        assert statuses[workload] == "unknown"
        assert 'data-reason="licence_directory_unverified"' in readiness_row(html, workload)


@pytest.mark.parametrize("scope", ["declared", "undeclared", "filtered"])
@given(
    rows=st.lists(
        st.tuples(
            st.booleans(),
            st.booleans(),
            st.sampled_from(("checked", "failed", "pending")),
            st.tuples(st.booleans(), st.booleans(), st.booleans()),
        ),
        max_size=40,
    ),
    omit_total=st.booleans(),
    minute=st.integers(0, 1439),
    offsets=st.tuples(st.integers(-12, 14), st.integers(-12, 14)),
)
@example(
    rows=[(True, True, "checked", (True, False, True))],
    omit_total=True,
    minute=1439,
    offsets=(-5, 14),
)
def test_truthful_directory_exports_load(
    scope: str,
    rows: list[tuple[bool, bool, str, tuple[bool, bool, bool]]],
    omit_total: bool,
    minute: int,
    offsets: tuple[int, int],
) -> None:
    instant = datetime(2026, 11, 5, tzinfo=UTC) + timedelta(minutes=minute)
    scan_zone, interview_zone = (timezone(timedelta(hours=offset)) for offset in offsets)
    generated_at = instant.astimezone(scan_zone).isoformat()
    stamp = instant.isoformat()
    interview_day = (instant - timedelta(minutes=1)).astimezone(interview_zone).date().isoformat()
    checked_rows = [row for row in rows if row[2] == "checked"]
    failed = sum(row[2] == "failed" for row in rows)
    kind = "complete" if len(checked_rows) == len(rows) else "partial"
    coverage = Coverage(kind, len(checked_rows), failed, len(rows))
    population = DirectoryPopulation("directory", stamp, coverage) if scope == "declared" else None
    findings = []
    for index, field in enumerate(("user_count", "guest_count", "licensed_user_count")):
        observed = checked_rows
        observation_coverage = coverage
        if scope == "filtered":
            observed = [row for row in rows if row[3][index]]
            observation_coverage = Coverage("complete", len(observed), 0, len(observed))
        elif not observed and rows:
            continue
        elif population is not None and omit_total:
            observation_coverage = replace(coverage, total=None)
        count = sum((member, not member, licensed)[index] for member, licensed, *_ in observed)
        findings.append(
            Finding(
                f"directory.{field}",
                "directory",
                count,
                "users",
                "measured",
                "directory",
                "sample.directory",
                stamp,
                None,
                observation_coverage,
                None,
            )
        )
    findings.append(
        Finding(
            "directory.account_list_reviewed",
            "directory",
            True,
            None,
            "provided",
            None,
            "interview",
            interview_day,
            f"{interview_day}/{interview_day}",
            None,
            None,
        )
    )
    scan = replace(
        EMPTY_SCAN,
        generated_at=generated_at,
        collectors=(Collector("directory", "ok", None, ()),),
        findings=tuple(findings),
        directory_population=population,
    )
    assert load_scan_text(scan_to_json(scan, plans=PLANS), "inventory.json", CATALOGUE) == scan


@given(tenant=tenants())
@example(tenant=OFFICE)
@example(tenant=UNDERASSIGNED)
@example(tenant=OVERASSIGNED)
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
    accounts = recorded.get("directory.licensed_user_count")
    population = tenant.scan.directory_population
    reconciled = contradiction = False
    complete_assignments = set()
    if (
        licences is not None
        and licences.coverage.kind == "complete"
        and licences.collector not in unavailable
    ):
        complete_assignments = {
            f"{plan.workload}.licence_{plan.signal}_assigned"
            for product in licences.products
            if product.assigned
            for plan in PLANS.rosters[product.key].plans.values()
            if plan.workload is not None
        }
        if (
            accounts is not None
            and accounts.provenance == "measured"
            and accounts.collector not in unavailable
            and accounts.coverage.kind == "complete"
            and accounts.period is None
            and accounts.collected_at == licences.collected_at
            and population is not None
            and population.coverage.kind == "complete"
            and population.collector == accounts.collector
            and population.collected_at == accounts.collected_at
        ):
            seats = [product.assigned for product in licences.products]
            contradiction = accounts.value > sum(seats) or any(
                seat > accounts.value for seat in seats
            )
            reconciled = not contradiction
    if not reconciled:
        assert statuses["directory"] != "ready"
        if contradiction:
            assert 'data-reason="licence_assignments_conflict"' in report_section(html, "found")
        assert "licences" not in statuses
        signals = re.findall(
            r'<li data-evidence="[^"]+\.licence_(?:add_on|bundled)_assigned">.*?</li>',
            readiness,
            re.S,
        )
        no = re.escape(load_locale(tenant.lang)["common"]["no"])
        assert all(
            not re.search(rf'<div data-provenance="measured">\s*{no}\b', signal)
            for signal in signals
        )
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
                complete = reconciled or key in complete_assignments
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
@example(pair=(NONPROFIT_REVIEWED, NONPROFIT_LICENCES_SKIPPED))
@example(pair=(NONPROFIT_LICENCES_SKIPPED, NONPROFIT_LICENSED_COUNT_PARTIAL))
def test_worse_collection_never_improves_status(pair: tuple[Tenant, Tenant]) -> None:
    original, degraded = pair
    if original == degraded:
        return
    before = _statuses(_render(original))
    after = _statuses(_render(degraded))
    event(f"Directory {before['directory']} to {after['directory']}")
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


@given(tenant=tenants())
def test_target_gaps_cannot_improve_readiness(tenant: Tenant) -> None:
    scan = load_scan_text(scan_to_json(tenant.scan, plans=PLANS), "scan.json", CATALOGUE)
    inputs = load_inputs_text(yaml.safe_dump(tenant.inputs or {}), "inputs.yaml", CATALOGUE)
    scan, other = combine(scan, provided_findings(inputs, CATALOGUE))
    findings = {item.id: item for item in scan.findings + licence_findings(scan, PLANS, CATALOGUE)}
    collectors = {item.id: item for item in scan.collectors}
    alternatives = {item.id: item for item in other}
    possible = {
        "ready": {"ready", "unknown", "needs_work"},
        "unknown": {"unknown", "needs_work"},
        "needs_work": {"needs_work"},
        "blocker": {"blocker"},
    }
    for profile in PROFILES:
        mapping = load_mapping(profile, CATALOGUE)
        without_gaps = replace(
            mapping,
            functions=tuple(
                replace(item, coverage="in_suite") if item.coverage in GAP_COVERAGE else item
                for item in mapping.functions
            ),
        )
        before = evaluate(
            findings,
            STATUS_RULES,
            CATALOGUE,
            without_gaps,
            collectors=collectors,
            alternatives=alternatives,
            directory_population=scan.directory_population,
        )
        after = evaluate(
            findings,
            STATUS_RULES,
            CATALOGUE,
            mapping,
            collectors=collectors,
            alternatives=alternatives,
            directory_population=scan.directory_population,
        )
        for previous, row in zip(before, after, strict=True):
            assert row.workload == previous.workload
            assert row.status in possible[previous.status], (profile, previous.workload)
            assert not previous.incomplete or row.incomplete
            if row.status == "ready":
                assert all(gap.need == "no" for gap in row.transfer_gaps)
            if row.deciding is not None and row.deciding.id.startswith("target-"):
                assert row.status == "needs_work"
            if row.status == "blocker":
                assert row.deciding == previous.deciding


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
    sign = "−" if amount < 0 and cents else ""
    grouped = f"{whole:,}".replace(",", settings["thousands_separator"])
    number = f"{sign}{grouped}"
    if decimal:
        number += f"{settings['decimal_separator']}{decimal:02d}"
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
    assert offline_policies(document) == [CSP]
