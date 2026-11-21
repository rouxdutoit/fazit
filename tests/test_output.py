# SPDX-License-Identifier: AGPL-3.0-or-later
import os
from pathlib import Path

import pytest

from fazit.errors import InputError
from fazit.output import write_inside


def test_write_creates_the_output_directory_and_replaces_regular_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    out = Path("new") / "report"
    destination = tmp_path / out / "report.html"

    assert write_inside(out, "report.html", "Übersicht\n") == destination
    assert destination.read_bytes() == "Übersicht\n".encode()
    assert write_inside(out, "report.html", "Revised\n") == destination
    assert destination.read_bytes() == b"Revised\n"
    assert list(destination.parent.iterdir()) == [destination]


@pytest.mark.parametrize("name", ["", ".", "..", "../outside", "a/b", r"a\b", "a..b", "C:file"])
def test_write_refuses_names_that_are_not_basenames(tmp_path: Path, name: str) -> None:
    out = tmp_path / "out"

    with pytest.raises(InputError, match="write_failed") as caught:
        write_inside(out, name, "Never written")

    assert caught.value.field == "--out"
    assert not out.exists()


def test_write_refuses_a_dangling_destination_link(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    outside = tmp_path / "missing"
    destination = out / "report.html"
    os.symlink(outside, destination)

    with pytest.raises(InputError, match="destination_is_link"):
        write_inside(out, destination.name, "Never written")

    assert not outside.exists()
    assert destination.is_symlink()


def test_replacement_failure_preserves_the_destination_and_cleans_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "report.html"
    destination.write_bytes(b"Keep this")

    def fail_replace(source: Path, target: Path) -> None:
        assert Path(source).parent == Path(target).parent == tmp_path
        assert Path(source).read_bytes() == b"New contents"
        raise OSError("Replacement failed")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(InputError, match="write_failed"):
        write_inside(tmp_path, destination.name, "New contents")

    assert destination.read_bytes() == b"Keep this"
    assert list(tmp_path.iterdir()) == [destination]
