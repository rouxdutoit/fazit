# SPDX-License-Identifier: AGPL-3.0-or-later
import ast
import re
import subprocess
import tomllib
from collections.abc import Iterable, Iterator
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path

import pytest
import yaml
from helpers import LICENSE_SHA256, ROOT, readme_code_blocks

SPDX_IDENTIFIER = "SPDX-License-Identifier: AGPL-3.0-or-later"
NETWORK_IMPORTS = {
    "adal",
    "aiohttp",
    "azure.identity",
    "ftplib",
    "http",
    "httpcore",
    "httplib2",
    "httpx",
    "msal",
    "msgraph",
    "msgraph_core",
    "requests",
    "smtplib",
    "socket",
    "ssl",
    "urllib.request",
    "urllib3",
}


def _missing_first_line_spdx(sources: Iterable[Path]) -> list[str]:
    return [
        path.relative_to(ROOT).as_posix()
        for path in sources
        if path.read_text(encoding="utf-8").partition("\n")[0] != f"# {SPDX_IDENTIFIER}"
    ]


def test_source_files_start_with_spdx_identifier() -> None:
    sources = (
        *ROOT.glob("src/**/*.py"),
        *ROOT.glob("tests/**/*.py"),
        *ROOT.glob("src/**/*.yaml"),
        *ROOT.glob(".github/workflows/**/*.yml"),
        ROOT / "pyproject.toml",
        ROOT / "inputs.example.yaml",
    )
    missing = _missing_first_line_spdx(sources)
    missing.extend(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("src/**/*.j2")
        if SPDX_IDENTIFIER not in path.read_text(encoding="utf-8").partition("\n")[0]
    )
    assert not missing, f"Missing first-line SPDX identifier: {', '.join(sorted(missing))}"


def test_site_python_files_start_with_spdx_identifier() -> None:
    missing = _missing_first_line_spdx(ROOT.glob("site/**/*.py"))
    assert not missing, f"Missing first-line SPDX identifier: {', '.join(sorted(missing))}"


def test_license_matches_canonical_text() -> None:
    assert sha256((ROOT / "LICENSE").read_bytes()).hexdigest() == LICENSE_SHA256


def _dependency_names(requirements: list[str]) -> list[str]:
    return sorted(re.split(r"[\s\[<>=!~;@]", item, maxsplit=1)[0].lower() for item in requirements)


def test_dependencies_follow_the_decisions() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = config["project"]
    assert _dependency_names(project["dependencies"]) == ["jinja2", "pyyaml", "typer"]
    assert not project.get("optional-dependencies")
    groups = config["dependency-groups"]
    assert groups.keys() == {"dev"}
    assert _dependency_names(groups["dev"]) == ["hypothesis", "pytest", "ruff"]
    assert "hypothesis==6.170.15" in groups["dev"]
    (backend,) = config["build-system"]["requires"]
    assert re.fullmatch(r"hatchling==\d+(?:\.\d+)+", backend)


def test_dependency_cutoff_is_fourteen_days_before_head() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    cutoff = datetime.fromisoformat(config["tool"]["uv"]["exclude-newer"])
    head = subprocess.run(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert cutoff <= datetime.fromisoformat(head.stdout.strip()) - timedelta(days=14)


def test_locked_artifacts_were_uploaded_by_the_dependency_cutoff() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    cutoff = config["tool"]["uv"]["exclude-newer"]
    assert lock["options"]["exclude-newer"] == cutoff
    before = datetime.fromisoformat(cutoff)
    indexed = [package for package in lock["package"] if "registry" in package["source"]]
    assert indexed
    for package in indexed:
        artifacts = package.get("wheels", []) + ([package["sdist"]] if "sdist" in package else [])
        assert artifacts, package["name"]
        for artifact in artifacts:
            assert datetime.fromisoformat(artifact["upload-time"]) <= before, artifact["url"]


def _imported_modules(tree: ast.AST) -> Iterator[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module
            yield from (f"{node.module}.{alias.name}" for alias in node.names)


def test_package_imports_no_network_or_sign_in_modules() -> None:
    forbidden = set()
    for path in ROOT.glob("src/**/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for module in _imported_modules(tree):
            if any(module == name or module.startswith(f"{name}.") for name in NETWORK_IMPORTS):
                forbidden.add(f"{path.relative_to(ROOT)}: {module}")
    assert not forbidden, f"Network imports: {', '.join(sorted(forbidden))}"


def test_contribution_and_security_links_and_trailers() -> None:
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for trailer in ("Signed-off-by:", "Assisted-by:", "Co-Authored-By:"):
        assert trailer in contributing and trailer in agents
    assert "git commit -s" in contributing
    assert "](https://developercertificate.org/)" in contributing
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    for host in ("login.microsoftonline.com", "graph.microsoft.com"):
        assert host in security
    assert "](https://github.com/rouxdutoit/fazit/security/advisories/new)" in security
    assert "](mailto:hello@rouxdutoit.com)" in security
    assert set(re.findall(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", security, re.I)) == {
        "hello@rouxdutoit.com"
    }


@pytest.mark.parametrize(
    ("readme", "translation"), [("README.md", "README.de.md"), ("README.de.md", "README.md")]
)
def test_readmes_show_the_checkout_demo_and_no_published_install(
    readme: str, translation: str
) -> None:
    text = (ROOT / readme).read_text(encoding="utf-8")
    commands = "\n".join(readme_code_blocks(text))
    assert f"](https://github.com/rouxdutoit/fazit/blob/main/{translation})" in text
    assert not re.search(r"\]\((?!https://|#)[^)]+\)", text)
    assert "Claude" in text and "Codex" in text
    assert "![" not in text and not re.search(r"<img\b", text, re.I)
    assert re.search(r"(?m)^\s*uv run fazit demo\b", commands)
    assert not re.search(
        r"(?m)^\s*(?:uvx|pipx? install|uv (?:pip install|tool (?:run|install)))\s+fazit\b",
        commands,
    )


@pytest.fixture(scope="module")
def ci_workflow() -> dict:
    return yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))


def test_ci_runs_the_required_checks_on_supported_python_versions(ci_workflow: dict) -> None:
    assert {"push", "pull_request"} <= set(ci_workflow.get("on", ci_workflow.get(True, [])))
    job = ci_workflow["jobs"]["checks"]
    assert job["runs-on"] == "${{ matrix.os }}"
    strategy = job["strategy"]
    assert strategy["fail-fast"] is False
    matrix = strategy["matrix"]
    assert "ubuntu-latest" in matrix["os"]
    assert {"3.12", "3.x"} <= set(matrix["python-version"])
    platforms = {(row.get("os"), row.get("python-version")) for row in matrix.get("include", [])}
    assert {("windows-latest", "3.12"), ("macos-latest", "3.12")} <= platforms

    steps = job["steps"]
    actions = {step["uses"].partition("@")[0]: step for step in steps if "uses" in step}
    assert "actions/checkout" in actions
    setup_python = actions["actions/setup-python"]
    assert setup_python["with"]["python-version"] == "${{ matrix.python-version }}"
    assert re.fullmatch(r"\d+\.\d+\.\d+", actions["astral-sh/setup-uv"]["with"]["version"])
    commands = {
        " ".join(line.split())
        for step in steps
        if "if" not in step
        for line in step.get("run", "").splitlines()
    }
    assert any(
        command.startswith("uv sync ")
        and "--locked" in command.split()
        and f"steps.{setup_python['id']}.outputs.python-path" in command
        for command in commands
    )
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required = set(re.findall(r"^uv run .+$", agents, re.M))
    assert not (missing := required - commands), sorted(missing)

    deep = "uv run pytest -q tests/test_simulation.py --hypothesis-profile=deep"
    (step,) = (step for step in steps if step.get("run") == deep)
    assert set(step["if"].split(" && ")) == {
        "github.event_name == 'push'",
        "matrix.os == 'ubuntu-latest'",
        "matrix.python-version == '3.12'",
    }


def test_ci_uses_read_only_permissions_and_sha_pinned_actions(ci_workflow: dict) -> None:
    assert ci_workflow["permissions"] == {"contents": "read"}
    assert "secrets." not in str(ci_workflow)
    for job in ci_workflow["jobs"].values():
        assert "services" not in job
        permissions = job.get("permissions", {})
        assert permissions == "read-all" or (
            isinstance(permissions, dict) and set(permissions.values()) <= {"read", "none"}
        )
        for step in job.get("steps", []):
            if "uses" in step:
                assert re.fullmatch(r"[^@]+@[0-9a-fA-F]{40}", step["uses"])


def test_release_uses_trusted_publishing_on_version_tags(ci_workflow: dict) -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8"))
    assert workflow["on"] == {"push": {"tags": ["v*"]}}
    assert workflow["permissions"] == {"contents": "read"}
    assert "secrets." not in str(workflow)
    assert workflow["jobs"].keys() == {"build", "publish"}

    build = workflow["jobs"]["build"]
    assert build.get("permissions", workflow["permissions"]) == {"contents": "read"}
    checkout, setup_uv, upload = (step for step in build["steps"] if "uses" in step)
    assert checkout["with"]["persist-credentials"] is False
    ci_actions = {step["uses"] for step in ci_workflow["jobs"]["checks"]["steps"] if "uses" in step}
    assert {checkout["uses"], setup_uv["uses"]} <= ci_actions

    publish = workflow["jobs"]["publish"]
    assert publish["needs"] == "build"
    assert publish["environment"] == {"name": "pypi", "url": "https://pypi.org/p/fazit"}
    assert publish["permissions"] == {"id-token": "write"}
    download, publish_pypi = publish["steps"]
    assert upload["with"]["name"] == download["with"]["name"]
    assert upload["with"]["path"] == download["with"]["path"] == "dist/"
    assert not publish_pypi.get("with")

    for step, action in (
        (checkout, "actions/checkout"),
        (setup_uv, "astral-sh/setup-uv"),
        (upload, "actions/upload-artifact"),
        (download, "actions/download-artifact"),
        (publish_pypi, "pypa/gh-action-pypi-publish"),
    ):
        name, _, ref = step["uses"].partition("@")
        assert name == action and re.fullmatch(r"[0-9a-f]{40}", ref)
