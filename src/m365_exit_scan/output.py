# SPDX-License-Identifier: AGPL-3.0-or-later
from contextlib import suppress
from pathlib import Path
from tempfile import NamedTemporaryFile

from .errors import InputError


def write_inside(out_dir: Path, file_name: str, text: str) -> Path:
    location = str(out_dir)
    if file_name in {"", "."} or ".." in file_name or any(char in file_name for char in "/\\:\0"):
        raise InputError("write_failed", file=location, field="--out")

    try:
        directory = out_dir.resolve()
        directory.mkdir(parents=True, exist_ok=True)
    except (OSError, RuntimeError, ValueError):
        raise InputError("out_dir", file=location, field="--out") from None

    destination = directory / file_name
    temporary = None
    try:
        if destination.is_symlink():
            raise InputError("destination_is_link", file=str(destination), field="--out")
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=directory, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        temporary.replace(destination)
        return destination
    except (OSError, UnicodeError):
        raise InputError("write_failed", file=str(destination), field="--out") from None
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)
