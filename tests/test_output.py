# SPDX-License-Identifier: AGPL-3.0-or-later
import os
from pathlib import Path
from stat import S_IMODE

import pytest

from fazit.errors import InputError
from fazit.output import write_files, write_inside


def test_write_creates_the_output_directory_and_replaces_regular_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    out = Path("new") / "report"
    destination = tmp_path / out / "report.html"

    assert write_inside(out, "report.html", "Übersicht\n") == destination
    assert destination.read_bytes() == "Übersicht\n".encode()
    if os.name == "posix":
        assert S_IMODE(destination.stat().st_mode) == 0o600
        destination.chmod(0o644)
    assert write_inside(out, "report.html", "Revised\n") == destination
    assert destination.read_bytes() == b"Revised\n"
    if os.name == "posix":
        assert S_IMODE(destination.stat().st_mode) == 0o600
    assert list(destination.parent.iterdir()) == [destination]


@pytest.mark.parametrize("name", ["", ".", "..", "../outside", "a/b", r"a\b", "a..b", "C:file"])
def test_write_refuses_names_that_are_not_basenames(tmp_path: Path, name: str) -> None:
    out = tmp_path / "out"

    with pytest.raises(InputError, match="write_failed") as caught:
        write_inside(out, name, "Never written")

    assert caught.value.field == "--out"
    assert not out.exists()


@pytest.mark.parametrize(
    ("kind", "error"),
    [
        ("symlink", "destination_is_link"),
        ("dangling", "destination_is_link"),
        ("directory", "destination_not_file"),
        pytest.param(
            "fifo",
            "destination_not_file",
            marks=pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="Requires FIFO support"),
        ),
    ],
)
def test_batch_rejects_unsafe_destinations_before_writing_any_output(
    tmp_path: Path, kind: str, error: str
) -> None:
    out = tmp_path / "out"
    out.mkdir()
    existing = out / "scan.json"
    existing.write_bytes(b"Previous scan")
    destination = out / "report.html"
    outside = tmp_path / "outside.html"
    if kind in {"symlink", "dangling"}:
        if kind == "symlink":
            outside.write_bytes(b"Keep this")
        destination.symlink_to(outside)
    elif kind == "directory":
        destination.mkdir()
    else:
        os.mkfifo(destination)
    metadata = destination.lstat()

    with pytest.raises(InputError, match=error) as caught:
        write_files(
            out,
            {
                existing.name: "New scan",
                "inputs.yaml": "New inputs",
                destination.name: "New report",
            },
        )

    assert caught.value.field == "--out" and caught.value.file == str(destination)
    assert set(out.iterdir()) == {existing, destination}
    assert existing.read_bytes() == b"Previous scan"
    assert destination.lstat() == metadata
    if kind == "symlink":
        assert outside.read_bytes() == b"Keep this"
    else:
        assert not outside.exists()


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


def test_batch_write_failure_while_staging_preserves_existing_outputs(tmp_path: Path) -> None:
    existing = tmp_path / "scan.json"
    existing.write_bytes(b"Previous scan")

    with pytest.raises(InputError, match="write_failed") as caught:
        write_files(tmp_path, {existing.name: "New scan", "report.html": "\ud800"})

    assert caught.value.file == str(tmp_path / "report.html")
    assert existing.read_bytes() == b"Previous scan"
    assert list(tmp_path.iterdir()) == [existing]
