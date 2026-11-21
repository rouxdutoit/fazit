# SPDX-License-Identifier: AGPL-3.0-or-later
class InputError(Exception):
    def __init__(
        self, code: str, *, file: str | None = None, field: str | None = None, **details: object
    ) -> None:
        super().__init__(code)
        self.code = code
        self.file = file
        self.field = field
        self.details = details
