# SPDX-License-Identifier: AGPL-3.0-or-later
import ast
import re
import subprocess
import tomllib
from collections.abc import Iterator
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPDX_IDENTIFIER = "SPDX-License-Identifier: AGPL-3.0-or-later"
LICENSE_SHA256 = "0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0"
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


def test_source_files_start_with_spdx_identifier() -> None:
    sources = (
        *ROOT.glob("src/**/*.py"),
        *ROOT.glob("tests/**/*.py"),
        *ROOT.glob("site/**/*.py"),
        *ROOT.glob("src/**/*.yaml"),
        *ROOT.glob(".github/workflows/**/*.yml"),
        ROOT / "pyproject.toml",
        ROOT / "inputs.example.yaml",
    )
    missing = [
        path.relative_to(ROOT).as_posix()
        for path in sources
        if path.read_text(encoding="utf-8").partition("\n")[0] != f"# {SPDX_IDENTIFIER}"
    ]
    missing.extend(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("src/**/*.j2")
        if SPDX_IDENTIFIER not in path.read_text(encoding="utf-8").partition("\n")[0]
    )
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


def test_contribution_and_security_documents() -> None:
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "Signed-off-by" in contributing
    assert "developercertificate.org" in contributing
    assert "first public release" in contributing and "outside the maintainer team" in contributing
    assert "The maintainers attest" in contributing and "initial repository history" in contributing
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for trailer in ("Assisted-by:", "Co-Authored-By:"):
        assert trailer in contributing and trailer in agents
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "login.microsoftonline.com" in security
    assert "graph.microsoft.com" in security
    assert (
        "[Report a vulnerability](https://github.com/rouxdutoit/fazit/security/advisories/new)"
        in security
    )
    assert "mailto:hello@rouxdutoit.com" in security
    assert set(re.findall(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", security, re.I)) == {
        "hello@rouxdutoit.com"
    }


def readme_code_blocks(readme: str) -> list[str]:
    return re.findall(r"^```[^\n]*\n(.*?)^```[ \t]*$", readme, flags=re.M | re.S)


def test_readmes_start_with_demo_and_describe_the_project() -> None:
    readmes = {
        "README.md": ("AI assistance", "not available yet", "disconnect", "](README.de.md)"),
        "README.de.md": ("KI", "noch nicht", "Trennen Sie", "](README.md)"),
    }
    for name, phrases in readmes.items():
        text = (ROOT / name).read_text(encoding="utf-8")
        blocks = readme_code_blocks(text)
        assert blocks and "uv run fazit demo" in blocks[0], name
        for phrase in (*phrases, "Claude", "Codex"):
            assert phrase in text, (name, phrase)
        assert "![" not in text and not re.search(r"<img\b", text, re.IGNORECASE), name
        assert all("uvx fazit" not in block for block in blocks), name


def test_ci_checks_both_python_versions_with_read_only_permissions() -> None:
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    assert set(workflow.get("on", workflow.get(True))) == {"push", "pull_request"}
    assert workflow["permissions"] == {"contents": "read"}
    (job,) = workflow["jobs"].values()
    assert job["runs-on"] == "${{ matrix.os }}"
    platforms = {row["os"] for row in job["strategy"]["matrix"]["include"]}
    assert platforms == {"windows-latest", "macos-latest"}
    assert job["strategy"]["fail-fast"] is False
    assert set(job["strategy"]["matrix"]["python-version"]) == {"3.12", "3.x"}
    assert "services" not in job and "secrets." not in text
    steps = job["steps"]
    actions = [step["uses"] for step in steps if "uses" in step]
    assert [value.partition("@")[0] for value in actions] == [
        "actions/checkout",
        "actions/setup-python",
        "astral-sh/setup-uv",
    ]
    assert all(re.search(r"@[0-9a-fA-F]{40}$", value) for value in actions)
    setup_uv = next(
        step for step in steps if step.get("uses", "").startswith("astral-sh/setup-uv@")
    )
    assert re.fullmatch(r"\d+\.\d+\.\d+", setup_uv["with"]["version"])
    commands = [step["run"] for step in steps if "run" in step]
    assert commands == [
        'uv sync --locked --python "${{ steps.python.outputs.python-path }}"',
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run pytest -q",
        "uv run pytest -q tests/test_simulation.py --hypothesis-profile=deep",
        "uv run fazit demo --lang de",
        "uv run fazit demo --lang en",
        "uv run python site/check_site.py",
    ]
