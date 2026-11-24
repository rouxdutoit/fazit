# SPDX-License-Identifier: AGPL-3.0-or-later
import os
from collections.abc import Iterator, Mapping
from contextlib import ExitStack, contextmanager, suppress
from dataclasses import dataclass
from os.path import join
from pathlib import Path
from secrets import token_hex
from shutil import copyfileobj
from stat import S_ISLNK, S_ISREG
from typing import BinaryIO

from .errors import InputError

try:
    import fcntl
except ImportError:
    fcntl = None

# stat advertises fstatat even on older CPython releases that omit lstat.
# The support set lists rename for both rename and replace.
_DIR_FD = (
    {os.open, os.mkdir, os.stat, os.rename, os.unlink} <= os.supports_dir_fd
    and os.stat in os.supports_follow_symlinks
    and all(hasattr(os, flag) for flag in ("O_DIRECTORY", "O_NOFOLLOW"))
)
_CREATE_PRIVATE = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
_READ_BACKUP = (
    os.O_RDONLY
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_NONBLOCK", 0)
    | getattr(os, "O_BINARY", 0)
)


@dataclass(frozen=True)
class _Directory:
    path: Path
    fd: int | None

    def entry(self, name: str) -> str | Path:
        return self.path / name if self.fd is None else name

    def replace(self, source: str, target: str) -> None:
        os.replace(self.entry(source), self.entry(target), src_dir_fd=self.fd, dst_dir_fd=self.fd)

    def unlink(self, name: str) -> None:
        os.unlink(self.entry(name), dir_fd=self.fd)


def _open_path(directory: Path) -> int:
    search = getattr(os, "O_SEARCH", getattr(os, "O_PATH", os.O_RDONLY))
    flags = search | os.O_DIRECTORY | os.O_NOFOLLOW
    current = os.open(directory.anchor, flags)
    try:
        for component in directory.parts[1:]:
            # A path already resolved by the caller must not acquire new links on the way down.
            try:
                child = os.open(component, flags, dir_fd=current)
            except FileNotFoundError:
                with suppress(FileExistsError):
                    os.mkdir(component, dir_fd=current)
                child = os.open(component, flags, dir_fd=current)
            os.close(current)
            current = child
    except BaseException:
        os.close(current)
        raise
    return current


@contextmanager
def _open_directory(out_dir: Path | str) -> Iterator[_Directory]:
    fd = None
    try:
        path = Path(out_dir).resolve()
        if _DIR_FD:
            fd = _open_path(path)
        else:
            path.mkdir(parents=True, exist_ok=True)
    except (OSError, RuntimeError, ValueError):
        raise InputError("out_dir", file=str(out_dir), field="--out") from None
    with ExitStack() as closing:
        if fd is not None:
            closing.callback(os.close, fd)
            if fcntl is not None:
                # Serialize Fazit writers where the directory supports advisory locking.
                with suppress(OSError):
                    lock = os.open(".", os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd)
                    closing.callback(os.close, lock)
                    fcntl.flock(lock, fcntl.LOCK_EX)
        yield _Directory(path, fd)


def write_inside(out_dir: Path | str, file_name: str, text: str) -> Path:
    (destination,) = write_files(out_dir, {file_name: text})
    return destination


def write_files(out_dir: Path | str, outputs: Mapping[str, str]) -> tuple[Path, ...]:
    location = str(out_dir)
    for name in outputs:
        if name in {"", "."} or ".." in name or any(char in name for char in "/\\:\0"):
            raise InputError("write_failed", file=location, field="--out")

    with _open_directory(out_dir) as directory, ExitStack() as staged:
        destinations = [(name, join(location, name)) for name in outputs]
        for name, label in destinations:
            _check_destination(directory, name, label)
        pending = []
        for name, label in destinations:
            temporary = _stage(directory, label, outputs[name])
            staged.callback(_discard, directory, temporary)
            pending.append((name, label, temporary))
        backups: dict[str, str] = {}
        try:
            for index, (name, label) in enumerate(destinations):
                previous = _check_destination(directory, name, label)
                # The last replacement has no later operation that could require its backup.
                if previous is not None and index < len(destinations) - 1:
                    backups[name] = _backup(directory, name, label, previous)
            _publish(directory, pending, backups)
        finally:
            for backup in backups.values():
                _discard(directory, backup)
    return tuple(directory.path / name for name, _ in destinations)


def _check_destination(directory: _Directory, name: str, label: str) -> os.stat_result | None:
    try:
        if directory.fd is None:
            metadata = os.lstat(directory.path / name)
        else:
            metadata = os.stat(name, dir_fd=directory.fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError:
        raise InputError("write_failed", file=label, field="--out") from None
    if S_ISLNK(metadata.st_mode):
        raise InputError("destination_is_link", file=label, field="--out")
    if not S_ISREG(metadata.st_mode):
        raise InputError("destination_not_file", file=label, field="--out")
    return metadata


def _discard(directory: _Directory, name: str) -> None:
    with suppress(OSError):
        directory.unlink(name)


def _stage(directory: _Directory, label: str, contents: str | BinaryIO) -> str:
    kind = "new" if isinstance(contents, str) else "previous"
    name = f".fazit-{kind}-{token_hex(16)}.tmp"
    try:
        fd = os.open(directory.entry(name), _CREATE_PRIVATE, 0o600, dir_fd=directory.fd)
    except OSError:
        raise InputError("write_failed", file=label, field="--out") from None
    try:
        with os.fdopen(fd, "wb") as stream:
            if isinstance(contents, str):
                stream.write(contents.encode("utf-8"))
            else:
                copyfileobj(contents, stream)
    except BaseException as error:
        _discard(directory, name)
        if isinstance(error, (OSError, UnicodeError)):
            raise InputError("write_failed", file=label, field="--out") from None
        raise
    return name


def _backup(directory: _Directory, name: str, label: str, previous: os.stat_result) -> str:
    try:
        fd = os.open(directory.entry(name), _READ_BACKUP, dir_fd=directory.fd)
        with os.fdopen(fd, "rb") as stream:
            if not os.path.samestat(previous, os.fstat(fd)):
                raise InputError("write_failed", file=label, field="--out")
            return _stage(directory, label, stream)
    except OSError:
        raise InputError("write_failed", file=label, field="--out") from None


def _publish(
    directory: _Directory, pending: list[tuple[str, str, str]], backups: dict[str, str]
) -> None:
    replaced = []
    try:
        for name, label, temporary in pending:
            _check_destination(directory, name, label)
            directory.replace(temporary, name)
            replaced.append((name, label))
    except (InputError, OSError) as error:
        if failure := _restore(directory, replaced, backups):
            raise failure from None
        if isinstance(error, InputError):
            raise
        raise InputError("write_failed", file=label, field="--out") from None


def _restore(
    directory: _Directory, replaced: list[tuple[str, str]], backups: dict[str, str]
) -> InputError | None:
    failure = None
    for name, label in reversed(replaced):
        backup = backups.pop(name, None)
        try:
            if backup is None:
                with suppress(FileNotFoundError):
                    directory.unlink(name)
            else:
                directory.replace(backup, name)
        except OSError:
            # Keep the saved copy when the filesystem also refuses restoration.
            if failure is None:
                code = "restore_backup_failed" if backup is not None else "restore_failed"
                failure = InputError(code, file=label, field="--out", backup=backup)
    return failure
