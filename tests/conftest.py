# SPDX-License-Identifier: AGPL-3.0-or-later
import sys
from collections.abc import Iterator

import pytest

_socket_events: list[str] | None = None


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
