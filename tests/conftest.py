# SPDX-License-Identifier: AGPL-3.0-or-later
import sys
from collections.abc import Iterator
from tempfile import TemporaryDirectory

import pytest
from hypothesis import settings
from hypothesis.configuration import set_hypothesis_home_dir

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
