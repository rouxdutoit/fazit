# SPDX-License-Identifier: AGPL-3.0-or-later
"""Check local site links and verify the checked-in demo reports."""

import re
from collections import Counter
from html.parser import HTMLParser
from itertools import pairwise
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urljoin, urlsplit

from typer.testing import CliRunner

from befund.cli import app

ROOT = Path(__file__).resolve().parent
DEMO_REPORTS = {ROOT / "demo" / lang / "index.html": lang for lang in ("en", "de")}
VOID = set("area base br col embed hr img input link meta param source track wbr".split())


class Page(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.tags: Counter[str] = Counter()
        self.ids: Counter[str] = Counter()
        self.stack: list[str] = []
        self.headings: list[int] = []
        self.links: list[tuple[str, str, str, int]] = []
        self.errors: list[str] = []
        self.language = ""
        self.doctype = False
        self.feed(path.read_text(encoding="utf-8"))
        self.close()

    def handle_decl(self, decl: str) -> None:
        self.doctype = decl.lower() == "doctype html"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag] += 1
        if tag not in VOID:
            self.stack.append(tag)
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang") or ""
        if element_id := values.get("id"):
            self.ids[element_id] += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        for name, value in attrs:
            if name in {"href", "src"}:
                self.links.append((tag, name, value or "", self.getpos()[0]))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing tag </{tag}> on line {self.getpos()[0]}.")
        else:
            self.stack.pop()

    def check_structure(self, *, require_skip_link: bool) -> None:
        if not self.doctype or self.language not in {"en", "de"}:
            self.errors.append("Expected an HTML doctype and an en or de document language.")
        if self.stack:
            self.errors.append(f"Unclosed tags {self.stack}.")
        for tag in ("html", "head", "title", "body", "main", "h1"):
            if self.tags[tag] != 1:
                self.errors.append(f"Expected one <{tag}> element.")
        if self.headings[:1] != [1] or any(
            after > before + 1 for before, after in pairwise(self.headings)
        ):
            self.errors.append("Heading levels are out of order.")
        for element_id, count in self.ids.items():
            if count > 1:
                self.errors.append(f"Duplicate id {element_id!r}.")
        if require_skip_link and not any(
            tag == "a" and value == "#main" for tag, _, value, _ in self.links
        ):
            self.errors.append("Missing skip link to #main.")


def check_reference(
    source: Path, tag: str, name: str, value: str, pages: dict[Path, Page]
) -> str | None:
    raw = urlsplit(value)
    if raw.scheme or raw.netloc:
        if tag == "a" and name == "href" and raw.scheme in {"https", "mailto", "tel"}:
            return None
        return f"{name}={value!r} is an external resource or unsupported link."
    if not value:
        return f"{name} is empty."
    origin = "/" + source.relative_to(ROOT).as_posix()
    url = urlsplit(urljoin(origin, value))
    target = (ROOT / unquote(url.path).lstrip("/")).resolve()
    if url.path.endswith("/"):
        target /= "index.html"
    if not target.is_relative_to(ROOT) or not target.is_file():
        return f"{name}={value!r} does not resolve to a file in the site."
    if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
        return f"{name}={value!r} does not resolve to an element."
    return None


def check_demo_reports() -> list[str]:
    errors = []
    runner = CliRunner()
    with TemporaryDirectory(prefix="befund-site-") as temporary:
        for target, lang in DEMO_REPORTS.items():
            out = Path(temporary) / lang
            command = ("demo", "--lang", lang, "--sample", "town", "--profile", "opendesk")
            result = runner.invoke(app, [*command, "--out", str(out)])
            name = target.relative_to(ROOT)
            if result.exit_code != 0:
                errors.append(f"{name}: Befund demo failed. {result.output.strip()}")
                continue
            generated = Path(result.stdout.splitlines()[-1])
            if not generated.is_file() or not target.is_file():
                errors.append(f"{name}: Demo report is missing.")
            elif target.read_bytes() != generated.read_bytes():
                errors.append(f"{name}: Differs from a fresh befund {' '.join(command)} run.")
    return errors


def main() -> int:
    pages = {
        path: Page(path)
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
    }
    references = []
    errors = check_demo_reports()
    for path, page in pages.items():
        page.check_structure(require_skip_link=path not in DEMO_REPORTS)
        errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in page.errors)
        references.extend((path, *ref) for ref in page.links)

    stylesheet = ROOT / "style.css"
    for line, text in enumerate(stylesheet.read_text(encoding="utf-8").splitlines(), 1):
        for value in re.findall(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", text):
            references.append((stylesheet, "css", "url", value.strip(), line))

    for path, tag, name, value, line in references:
        if error := check_reference(path, tag, name, value, pages):
            errors.append(f"{path.relative_to(ROOT)}:{line}: {error}")

    for error in errors:
        print(error)
    if not errors:
        print(f"Checked {len(pages)} pages and {len(references)} references. No errors.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
