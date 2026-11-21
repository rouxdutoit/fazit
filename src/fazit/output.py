# SPDX-License-Identifier: AGPL-3.0-or-later
from collections.abc import Iterator, Mapping
from contextlib import ExitStack, contextmanager, suppress
from pathlib import Path
from stat import S_ISLNK, S_ISREG
from tempfile import NamedTemporaryFile

from .errors import InputError


def write_inside(out_dir: Path, file_name: str, text: str) -> Path:
    (destination,) = write_files(out_dir, {file_name: text})
    return destination


def write_files(out_dir: Path, outputs: Mapping[str, str]) -> tuple[Path, ...]:
    location = str(out_dir)
    for name in outputs:
        if name in {"", "."} or ".." in name or any(char in name for char in "/\\:\0"):
            raise InputError("write_failed", file=location, field="--out")

    try:
        directory = out_dir.resolve()
        directory.mkdir(parents=True, exist_ok=True)
    except (OSError, RuntimeError, ValueError):
        raise InputError("out_dir", file=location, field="--out") from None

    destinations = tuple(directory / name for name in outputs)
    for destination in destinations:
        _check_destination(destination)
    with ExitStack() as staged:
        pending = [
            (destination, staged.enter_context(_stage(destination, outputs[destination.name])))
            for destination in destinations
        ]
        for destination in destinations:
            _check_destination(destination)
        for destination, temporary in pending:
            try:
                temporary.replace(destination)
            except OSError:
                raise InputError("write_failed", file=str(destination), field="--out") from None
    return destinations


def _check_destination(destination: Path) -> None:
    try:
        mode = destination.lstat().st_mode
    except FileNotFoundError:
        return
    except OSError:
        raise InputError("write_failed", file=str(destination), field="--out") from None
    if S_ISLNK(mode):
        raise InputError("destination_is_link", file=str(destination), field="--out")
    if not S_ISREG(mode):
        raise InputError("destination_not_file", file=str(destination), field="--out")


@contextmanager
def _stage(destination: Path, text: str) -> Iterator[Path]:
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=destination.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        yield temporary
    except (OSError, UnicodeError):
        raise InputError("write_failed", file=str(destination), field="--out") from None
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)
