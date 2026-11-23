# SPDX-License-Identifier: AGPL-3.0-or-later
import sys
from collections.abc import Iterator
from tempfile import TemporaryDirectory

import pytest
from hypothesis import settings
from hypothesis.configuration import set_hypothesis_home_dir

from fazit.catalogue import Catalogue, load_catalogue

settings.register_profile(
    "fazit", derandomize=True, database=None, deadline=None, print_blob=True, max_examples=18
)
settings.register_profile("deep", settings.get_profile("fazit"), max_examples=300)
settings.load_profile("fazit")

_socket_events: list[str] | None = None


def pytest_configure(config: pytest.Config) -> None:
    # Hypothesis caches constants even when its example database is disabled.
    cache = TemporaryDirectory(prefix="fazit-hypothesis-")
    set_hypothesis_home_dir(cache.name)
    config.add_cleanup(cache.cleanup)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if (config.rootpath / ".git").exists() or not (config.rootpath / "PKG-INFO").is_file():
        return
    repo_test = "test_repo_basics.py"
    workflow = ".github/workflows/ci.yml"
    style = "site/style.css"
    checkout_files = {
        (repo_test, "test_dependency_cutoff_is_fourteen_days_before_head"): ".git",
        (repo_test, "test_ci_runs_the_required_checks_on_supported_python_versions"): workflow,
        (repo_test, "test_ci_uses_read_only_permissions_and_sha_pinned_actions"): workflow,
        (repo_test, "test_release_uses_trusted_publishing_on_version_tags"): (
            ".github/workflows/release.yml"
        ),
        ("test_report.py", "test_coverage_symbols_match_the_site"): "site/icons",
        ("test_report.py", "test_report_and_website_share_colour_tokens"): style,
        ("test_report.py", "test_status_palette_is_shared_by_the_site_and_report"): style,
        ("test_site.py", "test_site_only_accepts_inert_json_ld_inline"): "site/check_site.py",
        (
            "test_site.py",
            "test_llms_text_keeps_coverage_and_commands_readable",
        ): "site/generate_llms.py",
    }
    for item in items:
        path = checkout_files.get((item.path.name, item.name.partition("[")[0]))
        if path is not None and not (config.rootpath / path).exists():
            item.add_marker(pytest.mark.skip(reason=f"The source distribution omits {path}."))


@pytest.fixture
def catalogue() -> Catalogue:
    return load_catalogue()


def _record_socket_event(event: str, args: tuple[object, ...]) -> None:
    if _socket_events is not None and event.startswith("socket."):
        _socket_events.append(event)
        raise AssertionError(f"Network activity is forbidden ({event})")


sys.addaudithook(_record_socket_event)


@pytest.fixture(autouse=True)
def offline() -> Iterator[list[str]]:
    global _socket_events
    events: list[str] = []
    _socket_events = events
    try:
        yield events
    finally:
        _socket_events = None
        assert not events, f"Unexpected socket activity: {events}"
