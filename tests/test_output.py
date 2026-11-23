# SPDX-License-Identifier: AGPL-3.0-or-later
import os
from pathlib import Path
from stat import S_IMODE

import pytest

from fazit import output
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

    def fail_replace(
        source: str | Path,
        target: str | Path,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        assert src_dir_fd == dst_dir_fd
        parent = tmp_path if src_dir_fd is None else Path(".")
        assert Path(source).parent == Path(target).parent == parent
        if src_dir_fd is not None:
            assert os.path.samestat(os.fstat(src_dir_fd), tmp_path.stat())
        with os.fdopen(os.open(source, os.O_RDONLY, dir_fd=src_dir_fd), "rb") as stream:
            assert stream.read() == b"New contents"
        raise OSError("Replacement failed")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(InputError, match="write_failed"):
        write_inside(tmp_path, destination.name, "New contents")

    assert destination.read_bytes() == b"Keep this"
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.skipif(os.rename not in os.supports_dir_fd, reason="Requires directory handles")
@pytest.mark.parametrize("stage_fails", [False, True])
def test_output_stays_in_the_opened_directory_after_an_ancestor_moves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage_fails: bool
) -> None:
    ancestor = tmp_path / "ancestor"
    moved = tmp_path / "moved"
    out = ancestor / "out"
    out.mkdir(parents=True)
    name = "report.html"
    (out / name).write_bytes(b"Previous output")
    open_file = os.open

    def move_before_staging(
        path: str | Path, flags: int, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> int:
        if flags & os.O_CREAT and not moved.exists():
            ancestor.rename(moved)
            out.mkdir(parents=True)
            (out / name).write_bytes(b"Other output")
        return open_file(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", move_before_staging)
    if stage_fails:
        with pytest.raises(InputError, match="write_failed"):
            write_inside(out, name, "\ud800")
    else:
        write_inside(out, name, "New output")

    original = moved / "out"
    assert (original / name).read_bytes() == (b"Previous output" if stage_fails else b"New output")
    assert (out / name).read_bytes() == b"Other output"
    assert list(original.iterdir()) == [original / name]
    assert list(out.iterdir()) == [out / name]


def test_batch_write_failure_while_staging_preserves_existing_outputs(tmp_path: Path) -> None:
    existing = tmp_path / "scan.json"
    existing.write_bytes(b"Previous scan")

    with pytest.raises(InputError, match="write_failed") as caught:
        write_files(tmp_path, {existing.name: "New scan", "report.html": "\ud800"})

    assert caught.value.file == str(tmp_path / "report.html")
    assert existing.read_bytes() == b"Previous scan"
    assert list(tmp_path.iterdir()) == [existing]


@pytest.mark.parametrize("pathname_fallback", [False, True])
@pytest.mark.parametrize(("previous_count", "fail_at"), [(3, 2), (1, 3), (0, 2)])
def test_demo_replacement_failure_restores_the_previous_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    previous_count: int,
    fail_at: int,
    pathname_fallback: bool,
) -> None:
    if pathname_fallback:
        monkeypatch.setattr(output, "_DIR_FD", False)
    names = ("scan.json", "inputs.yaml", "report.html")
    previous = {name: f"Previous {name}".encode() for name in names[:previous_count]}
    for name, contents in previous.items():
        (tmp_path / name).write_bytes(contents)
    replace_file = os.replace
    attempts = 0

    def fail_once(
        source: str | Path,
        target: str | Path,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == fail_at:
            assert Path(target).name == names[fail_at - 1]
            raise PermissionError("Replacement failed")
        replace_file(source, target, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd)

    monkeypatch.setattr(os, "replace", fail_once)
    with pytest.raises(InputError, match="write_failed") as caught:
        write_files(tmp_path, {name: f"New {name}" for name in names})

    assert caught.value.file == str(tmp_path / names[fail_at - 1])
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == previous


def test_failed_restore_keeps_the_previous_contents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "scan.json"
    first.write_bytes(b"Previous scan")
    replace_file = os.replace

    def stop_replacing_after_the_first_write(
        source: str | Path,
        target: str | Path,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        if Path(target).name != first.name or Path(source).name.startswith(".fazit-previous-"):
            raise PermissionError("Replacement failed")
        replace_file(source, target, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd)

    monkeypatch.setattr(os, "replace", stop_replacing_after_the_first_write)
    with pytest.raises(InputError, match="restore_backup_failed") as caught:
        write_files(tmp_path, {first.name: "New scan", "inputs.yaml": "New inputs"})

    assert caught.value.file == str(first)
    assert (tmp_path / caught.value.details["backup"]).read_bytes() == b"Previous scan"
    assert first.read_bytes() == b"New scan"
    assert not (tmp_path / "inputs.yaml").exists()
