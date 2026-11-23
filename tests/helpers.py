# SPDX-License-Identifier: AGPL-3.0-or-later
import os
import re
from html.parser import HTMLParser
from importlib.resources import files
from pathlib import Path

from report_expectations import DISPLAY_ORDER
from typer.testing import CliRunner, Result

from fazit.cli import app

ROOT = Path(__file__).resolve().parents[1]
LICENSE_SHA256 = "0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0"
PLANTED_SCAN = ROOT / "tests" / "fixtures" / "planted_scan.json"
ALL_UNKNOWN_SCAN = ROOT / "tests" / "fixtures" / "all_unknown_scan.json"
NAME = "Erika Mustermann"
ADDRESS = "erika.mustermann@example.invalid"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJleGFtcGxlIn0.test-signature"
SINGLE_TOKENS = ("ReviewMarker", "Erika_Mustermann")

RESOURCE_ELEMENTS = {
    "audio",
    "base",
    "embed",
    "form",
    "frame",
    "iframe",
    "img",
    "link",
    "object",
    "script",
    "source",
    "track",
    "image",
    "use",
    "foreignobject",
    "feimage",
    "video",
}
RESOURCE_ATTRIBUTES = {"action", "background", "formaction", "ping", "poster", "src", "srcset"}
CSS_RESOURCE = re.compile(r"@import\b|\b(?:url|src|image-set)\s*\(", re.IGNORECASE)

runner = CliRunner()

_SOCKET_AUDIT_HOOK = """\
import os
import sys
from pathlib import Path

log = Path(os.environ["FAZIT_TEST_SOCKET_LOG"])

def record_socket_event(event: str, args: tuple[object, ...]) -> None:
    if event.startswith("socket."):
        with log.open("a", encoding="utf-8") as recorded:
            recorded.write(event + "\\n")
        raise OSError(f"Offline test blocked {event}")

sys.addaudithook(record_socket_event)
log.touch()
"""


class ReportDocument(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.styles: list[str] = []
        self._in_style = False
        self.feed(html)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        if tag == "style":
            self._in_style = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.styles.append(data)


def offline_policies(document: ReportDocument, *, demo_home: str | None = None) -> list[str]:
    policies = []
    for tag, attrs in document.tags:
        assert tag not in RESOURCE_ELEMENTS, tag
        assert not (RESOURCE_ATTRIBUTES & attrs.keys()), attrs
        for name, value in attrs.items():
            if name in {"href", "xlink:href"}:
                if demo_home and tag == "a" and attrs == {"class": "wordmark", "href": demo_home}:
                    continue
                assert (value or "").startswith("#"), value
            assert not name.startswith("on"), name
            if name == "style":
                assert not CSS_RESOURCE.search(value or ""), value
        if tag == "meta":
            directive = (attrs.get("http-equiv") or "").strip().lower()
            assert directive != "refresh"
            if directive == "content-security-policy":
                policies.append(attrs.get("content") or "")
    return policies


def readme_code_blocks(readme: str) -> list[str]:
    return re.findall(r"^```[^\n]*\n(.*?)^```[ \t]*$", readme, flags=re.M | re.S)


def report_section(html: str, name: str) -> str:
    section = re.search(rf'<section data-section="{name}">.*?</section>', html, re.S)
    assert section is not None, name
    return section[0]


def readiness_row(html: str, workload: str) -> str:
    row = re.search(rf'<article data-workload="{workload}"[^>]*>.*?</article>', html, re.S)
    assert row is not None, workload
    return row[0]


def assert_readiness_order(readiness: str, assessed: tuple[str, ...]) -> None:
    parts = re.split(r'<div class="status-group" data-status-group="([^"]+)">', readiness)
    group_statuses = parts[1::2]
    assert group_statuses == [status for status in DISPLAY_ORDER if status in group_statuses]
    assert "<article data-workload=" not in parts[0]
    workloads = []
    for status, group in zip(group_statuses, parts[2::2], strict=True):
        cards = re.findall(r'<article data-workload="([^"]+)" data-status="([^"]+)"', group)
        assert cards and all(card_status == status for _, card_status in cards)
        ids = [workload for workload, _ in cards]
        assert ids == [workload for workload in assessed if workload in ids]
        workloads.extend(ids)
    assert sorted(workloads) == sorted(assessed)


def rebuild_report(
    scan: Path, out: Path, lang: str, *, profile: str = "opendesk", inputs: Path | None = None
) -> str:
    command = ["report", str(scan), "--lang", lang, "--profile", profile, "--out", str(out)]
    if inputs is not None:
        command.extend(["--inputs", str(inputs)])
    result = runner.invoke(app, command)
    assert result.exit_code == 0, result.output
    path = Path(result.stdout.strip())
    assert path.is_file() and path.parent == out
    assert not result.stderr
    return path.read_text(encoding="utf-8")


def sample_scan_path(sample: str) -> Path:
    return Path(str(files("fazit").joinpath("demo", sample, "scan.json")))


def sample_inputs_path(sample: str) -> Path:
    return sample_scan_path(sample).with_name("inputs.yaml")


def audit_environment(work: Path) -> tuple[dict[str, str], Path]:
    (work / "sitecustomize.py").write_text(_SOCKET_AUDIT_HOOK, encoding="utf-8")
    log = work / "socket-events.log"
    return {**os.environ, "PYTHONPATH": str(work), "FAZIT_TEST_SOCKET_LOG": str(log)}, log


def assert_no_private_text(result: Result, out: Path, *planted: str) -> None:
    files_written = list(out.iterdir()) if out.exists() else []
    output = [result.stdout, result.stderr]
    for file in files_written:
        output.extend((file.name, file.read_text(encoding="utf-8")))
    for text in planted:
        assert all(text not in part for part in output), text
