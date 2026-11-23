# SPDX-License-Identifier: AGPL-3.0-or-later
"""Build llms-full.txt from the bilingual website's main content."""

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORIGIN = "https://fazit.dev"
MAIN_PAGES = (
    "",
    "start/",
    "coverage/",
    "security/",
    "roadmap/",
    "about/",
    "pilots/",
    "integrators/",
)
BLOCKS = set(
    "article br caption dd div dl dt figcaption li ol p section summary table tr ul".split()
)
HEADINGS = {f"h{level}": f"{'#' * min(level + 1, 6)} " for level in range(1, 7)}


class MainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.blocks: list[str] = []
        self._parts: list[str] = []
        self._main = False
        self._skip = ""
        self._heading = ""
        self._code = False

    def flush(self) -> None:
        content = " ".join("".join(self._parts).split())
        if self._heading == "h1":
            self.title = content
        elif content:
            self.blocks.append(HEADINGS.get(self._heading, "") + content)
        self._parts.clear()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "main":
            self._main = True
        if not self._main or self._skip:
            return
        classes = (dict(attrs).get("class") or "").split()
        if tag in {"script", "style", "svg"}:
            self._skip = tag
        elif tag in HEADINGS:
            self.flush()
            self._heading = tag
        elif tag in BLOCKS:
            self.flush()
        elif tag in {"th", "td"} and "".join(self._parts).strip():
            self._parts.append(" | ")
        elif tag == "span" and "row-count" in classes:
            self._parts.append(" ")
        elif tag == "code":
            self._code = True
        elif self._code and tag == "span" and "symbol-label" in classes:
            self.flush()

    def handle_endtag(self, tag: str) -> None:
        if self._skip:
            if tag == self._skip:
                self._skip = ""
            return
        if not self._main:
            return
        if tag in HEADINGS or tag in BLOCKS or tag == "main":
            self.flush()
            self._heading = ""
        if tag == "code":
            self._code = False
        if tag == "main":
            self._main = False

    def handle_data(self, data: str) -> None:
        if self._main and not self._skip:
            self._parts.append(data)


def render_llms_full(root: Path) -> str:
    blocks = ["# Fazit"]
    for language_path in ("", "de/"):
        for page in MAIN_PAGES:
            route = f"{language_path}{page}"
            reader = MainText()
            reader.feed((root / route / "index.html").read_text(encoding="utf-8"))
            reader.close()
            blocks.extend((f"## {reader.title}", f"{ORIGIN}/{route}", *reader.blocks))
    return "\n\n".join(blocks) + "\n"


if __name__ == "__main__":
    (ROOT / "llms-full.txt").write_text(render_llms_full(ROOT), encoding="utf-8", newline="\n")
