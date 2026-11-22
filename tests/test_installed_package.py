# SPDX-License-Identifier: AGPL-3.0-or-later
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from email.parser import BytesParser
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

import pytest
from test_repo_basics import LICENSE_SHA256, ROOT

from fazit.i18n import load_locale
from fazit.report import SECTION_ORDER

pytestmark = pytest.mark.slow

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


@dataclass(frozen=True)
class InstalledPackage:
    wheel: Path
    venv: Path


def _venv_program(venv: Path, name: str) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / f"{name}.exe"
    return venv / "bin" / name


def _run(*args: str | Path, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, f"{args}\n{result.stdout}\n{result.stderr}"
    return result.stdout


@pytest.fixture(scope="session")
def installed_package(tmp_path_factory: pytest.TempPathFactory) -> InstalledPackage:
    work = tmp_path_factory.mktemp("installed-package")
    dist, venv = work / "dist", work / "venv"
    _run(
        "uv",
        "build",
        "--wheel",
        "--offline",
        "--python",
        sys.executable,
        "--out-dir",
        dist,
        cwd=ROOT,
    )
    (wheel,) = dist.glob("*.whl")
    _run("uv", "venv", "--offline", "--python", sys.executable, venv, cwd=ROOT)
    python = _venv_program(venv, "python")
    # The lock file identifies the cached distributions without a fresh registry lookup.
    _run(
        "uv",
        "sync",
        "--locked",
        "--offline",
        "--no-dev",
        "--no-install-project",
        "--python",
        python,
        cwd=ROOT,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": str(venv)},
    )
    _run("uv", "pip", "install", "--offline", "--python", python, wheel, cwd=ROOT)
    return InstalledPackage(wheel, venv)


def _audit_environment(work: Path) -> tuple[dict[str, str], Path]:
    (work / "sitecustomize.py").write_text(_SOCKET_AUDIT_HOOK, encoding="utf-8")
    log = work / "socket-events.log"
    return {**os.environ, "PYTHONPATH": str(work), "FAZIT_TEST_SOCKET_LOG": str(log)}, log


def test_installed_demo_renders_offline(
    installed_package: InstalledPackage, tmp_path: Path
) -> None:
    assert not tmp_path.resolve().is_relative_to(ROOT)
    env, audit_log = _audit_environment(tmp_path)
    venv = installed_package.venv
    out = tmp_path / "out"
    stdout = _run(
        _venv_program(venv, "fazit"), "demo", "--lang", "de", "--out", out, cwd=tmp_path, env=env
    )

    path = Path(stdout.splitlines()[-1])
    assert path.is_absolute() and path.parent == out and path.is_file()
    html = path.read_text(encoding="utf-8")
    assert '<html lang="de">' in html
    assert tuple(re.findall(r'data-section="([^"]+)"', html)) == SECTION_ORDER
    assert not audit_log.read_text(encoding="utf-8")
    location = _run(
        _venv_program(venv, "python"),
        "-c",
        "import fazit\nprint(fazit.__file__)",
        cwd=tmp_path,
        env=env,
    )
    module = Path(location.strip()).resolve()
    assert module.is_file() and module.is_relative_to(venv.resolve())
    assert not audit_log.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("name", "content", "code", "field"),
    [
        pytest.param("inventory.json", None, "file_not_found", "$", id="missing"),
        pytest.param("inventory.json", None, "is_directory", "$", id="directory"),
        pytest.param("inventory.json", b"", "invalid_json", "$", id="empty"),
        pytest.param("inventory.json", b"{", "invalid_json", "$", id="invalid-json"),
        pytest.param("inventory.json", b"[]", "invalid_field", "$", id="json-array"),
        pytest.param(
            "inventory.json",
            b'{"schema_version": "2.0"}',
            "schema_version",
            "schema_version",
            id="schema-version",
        ),
        pytest.param("inventory.json", b"\xff", "not_utf8", "$", id="utf8"),
        pytest.param(
            "answers.yaml",
            b"currency: EUR\ncurrency: CHF\n",
            "duplicate_key",
            "$[1]",
            id="duplicate-yaml-key",
        ),
        pytest.param(
            "answers.yaml",
            b"windows_only_software: 42\n",
            "invalid_field",
            "windows_only_software",
            id="wrong-type",
        ),
        pytest.param(
            "answers.yaml",
            b'currency: EUR\ncurrent_costs: {other_it_per_year: "-0.01"}\n',
            "invalid_field",
            "current_costs.other_it_per_year",
            id="negative",
        ),
        pytest.param(
            "answers.yaml",
            b"current_costs: {other_it_per_year: .inf}\n",
            "non_finite_number",
            "$[0][0]",
            id="non-finite",
        ),
        pytest.param(
            "inventory.json",
            b"[" * 1500 + b"0" + b"]" * 1500,
            "invalid_json",
            "$",
            id="deep-json",
        ),
        pytest.param(
            "answers.yaml",
            b"x: " + b"[" * 1500 + b"0" + b"]" * 1500,
            "invalid_yaml",
            "$",
            id="deep-yaml",
        ),
        pytest.param("out", b"Keep this file.\n", "out_dir", "--out", id="out-is-file"),
    ],
)
def test_installed_report_rejects_malformed_files_offline(
    installed_package: InstalledPackage,
    tmp_path: Path,
    name: str,
    content: bytes | None,
    code: str,
    field: str,
) -> None:
    source, bad, out = tmp_path / "inventory.json", tmp_path / name, tmp_path / "out"
    if bad != source:
        with ZipFile(installed_package.wheel) as wheel:
            source.write_bytes(wheel.read("fazit/demo/town/scan.json"))
    if content is not None:
        bad.write_bytes(content)
    elif code == "is_directory":
        bad.mkdir()
    command = [
        _venv_program(installed_package.venv, "fazit"),
        "report",
        str(source),
        "--out",
        str(out),
    ]
    if bad.suffix == ".yaml":
        command.extend(("--inputs", str(bad)))
    env, audit_log = _audit_environment(tmp_path)
    audit_log.touch()
    before = _contents(tmp_path)
    result = subprocess.run(
        command,
        cwd=tmp_path,
        env={**env, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    strings = load_locale("en")
    message = strings["errors"][code].format(
        file=str(out) if bad == out else name, field=field, found="2.0", supported="1.x"
    )
    assert result.returncode == 2 and not result.stdout
    assert result.stderr.splitlines() == [strings["cli"]["error_prefix"].format(message=message)]
    assert message.endswith(".")
    assert not audit_log.read_bytes()
    assert _contents(tmp_path) == before


def _contents(directory: Path) -> dict[Path, bytes | None]:
    return {
        path.relative_to(directory): path.read_bytes() if path.is_file() else None
        for path in directory.rglob("*")
    }


def test_subprocess_audit_records_a_caught_attempt(
    installed_package: InstalledPackage, tmp_path: Path
) -> None:
    env, audit_log = _audit_environment(tmp_path)
    attempt = """\
import socket

try:
    socket.create_connection(("127.0.0.1", 1), timeout=0.1)
except OSError as error:
    print(error)
"""
    output = _run(
        _venv_program(installed_package.venv, "python"), "-c", attempt, cwd=tmp_path, env=env
    )
    assert output.strip() == "Offline test blocked socket.getaddrinfo"
    assert audit_log.read_text(encoding="utf-8").splitlines() == ["socket.getaddrinfo"]


def test_wheel_contains_runtime_data(installed_package: InstalledPackage) -> None:
    resources = (
        "templates/report.html.j2",
        "locales/de.yaml",
        "locales/en.yaml",
        "rules/findings.yaml",
        "rules/status.yaml",
        "rules/service_plans.yaml",
        "rules/risky_file_types.yaml",
        *(f"rules/mappings/{profile}.yaml" for profile in ("generic", "nextcloud", "opendesk")),
        *(
            f"demo/{sample}/{name}"
            for sample in ("town", "nonprofit")
            for name in ("scan.json", "inputs.yaml")
        ),
    )
    with ZipFile(installed_package.wheel) as wheel:
        missing = sorted({f"fazit/{name}" for name in resources} - set(wheel.namelist()))
    assert not missing, f"Missing package data: {', '.join(missing)}"


def test_wheel_carries_the_license(installed_package: InstalledPackage) -> None:
    with ZipFile(installed_package.wheel) as wheel:
        (metadata,) = (name for name in wheel.namelist() if name.endswith(".dist-info/METADATA"))
        headers = BytesParser().parsebytes(wheel.read(metadata), headersonly=True)
        assert headers["License-Expression"] == "AGPL-3.0-or-later AND OFL-1.1 AND Apache-2.0"
        asset_licences = ["src/fazit/fonts/OFL.txt", "src/fazit/icons/LICENSE"]
        assert headers.get_all("License-File") == ["LICENSE", *asset_licences]
        directory = f"{metadata.rsplit('/', 1)[0]}/licenses"
        licence = wheel.read(f"{directory}/LICENSE")
        for asset in asset_licences:
            assert wheel.read(f"{directory}/{asset}") == (ROOT / asset).read_bytes()
    assert sha256(licence).hexdigest() == LICENSE_SHA256
