# SPDX-License-Identifier: AGPL-3.0-or-later
from collections.abc import Iterator, Mapping
from contextlib import ExitStack, contextmanager, suppress
from os.path import join
from pathlib import Path
from stat import S_ISLNK, S_ISREG
from tempfile import NamedTemporaryFile

from .errors import InputError


def write_inside(out_dir: Path | str, file_name: str, text: str) -> Path:
    (destination,) = write_files(out_dir, {file_name: text})
    return destination


def write_files(out_dir: Path | str, outputs: Mapping[str, str]) -> tuple[Path, ...]:
    location = str(out_dir)
    for name in outputs:
        if name in {"", "."} or ".." in name or any(char in name for char in "/\\:\0"):
            raise InputError("write_failed", file=location, field="--out")

    try:
        directory = Path(out_dir).resolve()
        directory.mkdir(parents=True, exist_ok=True)
    except (OSError, RuntimeError, ValueError):
        raise InputError("out_dir", file=location, field="--out") from None

    destinations = [(directory / name, join(location, name)) for name in outputs]
    for destination, label in destinations:
        _check_destination(destination, label)
    with ExitStack() as staged:
        pending = [
            (
                destination,
                label,
                staged.enter_context(_stage(destination, label, outputs[destination.name])),
            )
            for destination, label in destinations
        ]
        for destination, label in destinations:
            _check_destination(destination, label)
        for destination, label, temporary in pending:
            try:
                temporary.replace(destination)
            except OSError:
                raise InputError("write_failed", file=label, field="--out") from None
    return tuple(destination for destination, _ in destinations)


def _check_destination(destination: Path, label: str) -> None:
    try:
        mode = destination.lstat().st_mode
    except FileNotFoundError:
        return
    except OSError:
        raise InputError("write_failed", file=label, field="--out") from None
    if S_ISLNK(mode):
        raise InputError("destination_is_link", file=label, field="--out")
    if not S_ISREG(mode):
        raise InputError("destination_not_file", file=label, field="--out")


@contextmanager
def _stage(destination: Path, label: str, text: str) -> Iterator[Path]:
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=destination.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        yield temporary
    except (OSError, UnicodeError):
        raise InputError("write_failed", file=label, field="--out") from None
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)
