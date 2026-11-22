# SPDX-License-Identifier: AGPL-3.0-or-later
"""Check the bilingual static site and verify the checked-in demo reports."""

import re
import struct
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from itertools import pairwise
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

from typer.testing import CliRunner

from fazit.catalogue import load_catalogue
from fazit.cli import app
from fazit.i18n import load_locale
from fazit.mappings import load_mapping
from fazit.status import STATUSES

ROOT = Path(__file__).resolve().parent
ORIGIN = "https://fazit.dev"
LANGUAGES = ("en", "de")
DEMO_ROUTES = ("/demo/en/", "/demo/de/")
ERROR_ROUTES = ("/404.html", "/de/404.html")
PAGE_PAIRS = (
    ("/", "/de/"),
    *(
        (f"/{page}/", f"/de/{page}/")
        for page in ("start", "pilots", "integrators", "security", "impressum", "privacy")
    ),
    DEMO_ROUTES,
    ERROR_ROUTES,
)
COVERAGE_BADGES = {
    "in_suite": ("cov-full", {"en": "In the suite", "de": "In der Suite"}),
    "in_suite_with_limits": ("cov-part", {"en": "With limits", "de": "Mit Einschränkungen"}),
    "open_source_community": ("cov-community", {"en": "Community app", "de": "Community-App"}),
    "not_available": ("cov-none", {"en": "Not in the suite", "de": "Nicht in der Suite"}),
}
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"
VOID = set("area base br col embed hr img input link meta param source track wbr".split())
CSS_REFS = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)|@import\s*["']([^"']+)""", re.I)


@dataclass(frozen=True)
class Reference:
    name: str
    value: str
    line: int
    plain_link: bool = False
    dimensions: tuple[int, int] | None = None


@dataclass(frozen=True)
class CoverageCell:
    workload: str
    target: str
    badge: str
    text: str


# Generated reports embed their fonts so they open offline; the CSP allows only font-src data:.
EMBEDDED_FONT = re.compile(r"data:font/woff2;base64,[A-Za-z0-9+/=]+")


def css_references(css: str, first_line: int) -> Iterator[Reference]:
    for match in CSS_REFS.finditer(css):
        value = (match[1] or match[2]).strip()
        yield Reference("CSS URL", value, first_line + css.count("\n", 0, match.start()))


class Page(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.tags: Counter[str] = Counter()
        self.ids: Counter[str] = Counter()
        self.stack: list[str] = []
        self.headings: list[int] = []
        self.references: list[Reference] = []
        self.canonicals: list[str] = []
        self.alternates: list[tuple[str, str]] = []
        self.switches: list[tuple[str, str, str]] = []
        self.meta: dict[str, str] = {}
        self.errors: list[str] = []
        self.coverage: Counter[CoverageCell] = Counter()
        self.status_counts: Counter[str] = Counter()
        self.tallies: list[str] = []
        self._coverage_table = False
        self._workload = ""
        self._target: str | None = None
        self._badge = ""
        self._cell_text: list[str] = []
        self._tally_text: list[str] | None = None
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
        values = {name: value or "" for name, value in attrs}
        line = self.getpos()[0]
        if tag == "html":
            self.language = values.get("lang", "")
        if element_id := values.get("id"):
            self.ids[element_id] += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag in {"base", "embed", "iframe", "object"}:
            self.errors.append(f"Unexpected <{tag}> on line {line}.")
        if tag == "script" and values.get("src") != "/site.js":
            self.errors.append(f"Expected the local script on line {line}.")
        if any(name.startswith("on") or name == "ping" for name in values):
            self.errors.append(f"Event handlers and link tracking are disallowed on line {line}.")
        self.record_metadata(tag, values, line)
        self.record_references(tag, values, line)

        classes = values.get("class", "").split()
        if tag == "table" and "coverage" in classes:
            self._coverage_table = True
        elif tag == "tr" and self._coverage_table:
            self._workload = values.get("data-workload", "")
        elif tag in {"th", "td"} and self._coverage_table and "tbody" in self.stack:
            self._target = values.get("data-label", "")
            self._badge = ""
            self._cell_text.clear()
        elif self._target is not None and "cov" in classes:
            self._badge = " ".join(name for name in classes if name.startswith("cov-"))
        elif tag == "p" and "tally" in classes:
            self._tally_text = []
        if tag == "tr" and values.get("id", "").startswith("readiness-"):
            self.status_counts[values.get("data-status", "")] += 1

    def record_metadata(self, tag: str, attrs: dict[str, str], line: int) -> None:
        href = attrs.get("href", "")
        hreflang = attrs.get("hreflang", "")
        if tag == "link":
            relations = attrs.get("rel", "").lower().split()
            if "canonical" in relations:
                self.canonicals.append(href)
            if "alternate" in relations:
                self.alternates.append((hreflang, href))
        if tag == "a" and "language" in attrs.get("class", "").split():
            self.switches.append((href, hreflang, attrs.get("lang", "")))
        if tag == "meta":
            if attrs.get("http-equiv", "").lower() == "refresh":
                self.errors.append(f"Unexpected meta refresh on line {line}.")
            key = attrs.get("property") or attrs.get("name", "")
            self.meta[key] = attrs.get("content", "")
            if key in {"og:url", "og:image", "twitter:image"}:
                self.references.append(Reference(key, self.meta[key], line))

    def record_references(self, tag: str, attrs: dict[str, str], line: int) -> None:
        dimensions = None
        if tag == "img" or (tag == "source" and "picture" in self.stack):
            dimensions = self.image_dimensions(attrs, line)
        if tag == "img" and (not attrs.get("src") or not attrs.get("alt", "").strip()):
            self.errors.append(f"Expected an image src and alt text on line {line}.")
        for name in ("href", "src", "poster", "background", "xlink:href", "action", "formaction"):
            if name in attrs:
                self.references.append(
                    Reference(name, attrs[name], line, tag == "a" and name == "href", dimensions)
                )
        for name in ("srcset", "imagesrcset"):
            if name in attrs:
                for candidate in attrs[name].split(","):
                    url = candidate.strip().split(maxsplit=1)
                    self.references.append(
                        Reference(name, url[0] if url else "", line, dimensions=dimensions)
                    )
        self.references.extend(css_references(attrs.get("style", ""), line))

    def image_dimensions(self, attrs: dict[str, str], line: int) -> tuple[int, int] | None:
        width, height = attrs.get("width", ""), attrs.get("height", "")
        if not all(re.fullmatch(r"[1-9][0-9]*", value) for value in (width, height)):
            self.errors.append(f"Expected positive image width and height on line {line}.")
            return None
        return int(width), int(height)

    def handle_data(self, data: str) -> None:
        if self.stack and self.stack[-1] == "style":
            self.references.extend(css_references(data, self.getpos()[0]))
        if self.stack and self.stack[-1] == "script" and data.strip():
            self.errors.append(f"Unexpected inline script on line {self.getpos()[0]}.")
        if self._target is not None:
            self._cell_text.append(data)
        if self._tally_text is not None:
            self._tally_text.append(data)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing tag </{tag}> on line {self.getpos()[0]}.")
        else:
            self.stack.pop()
        if tag in {"th", "td"} and self._target is not None:
            cell = " ".join("".join(self._cell_text).split())
            self.coverage[CoverageCell(self._workload, self._target, self._badge, cell)] += 1
            self._target = None
        elif tag == "table":
            self._coverage_table = False
        elif tag == "p" and self._tally_text is not None:
            self.tallies.append(" ".join("".join(self._tally_text).split()))
            self._tally_text = None

    def check_structure(self, lang: str, *, demo: bool) -> None:
        if not self.doctype or self.language != lang:
            self.errors.append(f"Expected an HTML doctype and document language {lang}.")
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
        if not demo and not any(ref.plain_link and ref.value == "#main" for ref in self.references):
            self.errors.append("Missing skip link to #main.")

    def check_metadata(self, route: str, other_lang: str, pair: dict[str, str]) -> None:
        if self.switches != [(pair[other_lang], other_lang, other_lang)]:
            self.errors.append("The language switch must link to the corresponding page.")
        if self.canonicals != [ORIGIN + route]:
            self.errors.append("Expected one canonical URL for the page.")
        if Counter(self.alternates) != Counter(alternates(pair).items()):
            self.errors.append("Expected English and German hreflang links for the page pair.")
        expected = {
            "og:url": ORIGIN + route,
            "og:image": ORIGIN + "/og.png",
            "og:image:width": "1200",
            "og:image:height": "630",
            "twitter:card": "summary_large_image",
        }
        for key, value in expected.items():
            if self.meta.get(key) != value:
                self.errors.append(f"Incorrect or missing metadata {key}.")
        for key in ("og:title", "og:description", "og:image:alt"):
            if not self.meta.get(key, "").strip():
                self.errors.append(f"Missing metadata {key}.")


def alternates(pair: dict[str, str]) -> dict[str, str]:
    return {lang: ORIGIN + route for lang, route in pair.items()}


def route_for(path: Path) -> str:
    relative = path.relative_to(ROOT)
    if relative.name == "index.html":
        return "/" if relative.parent == Path(".") else f"/{relative.parent.as_posix()}/"
    return f"/{relative.as_posix()}"


def local_path(route: str) -> Path:
    path = ROOT / unquote(route).lstrip("/")
    return (path / "index.html" if route.endswith("/") else path).resolve()


def png_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as image:
        header = image.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def webp_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as image:
        header = image.read(30)
    if header[:4] != b"RIFF" or header[8:12] != b"WEBP":
        return None
    chunk = header[12:16]
    chunk_size = int.from_bytes(header[16:20], "little")
    if chunk == b"VP8L" and len(header) >= 25 and chunk_size >= 5 and header[20] == 0x2F:
        # Each dimension occupies 14 bits, followed by alpha and version bits.
        bits = int.from_bytes(header[21:25], "little")
        if bits >> 29 == 0:
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X" and len(header) == 30 and chunk_size == 10:
        width = int.from_bytes(header[24:27], "little")
        height = int.from_bytes(header[27:30], "little")
        return width + 1, height + 1
    return None


def check_reference(route: str, ref: Reference, pages: dict[Path, Page]) -> str | None:
    if not ref.value.strip():
        return f"{ref.name} is empty."
    if ref.name == "CSS URL" and EMBEDDED_FONT.fullmatch(ref.value):
        return None
    raw = urlsplit(ref.value)
    if raw.scheme in {"https", "mailto", "tel"} and ref.plain_link and raw.netloc != "fazit.dev":
        return None
    resolved = urlsplit(urljoin(ORIGIN + route, ref.value))
    if resolved.scheme != "https" or resolved.netloc != "fazit.dev":
        return f"{ref.name}={ref.value!r} is an external resource or unsupported link."
    target = local_path(resolved.path or "/")
    if not target.is_relative_to(ROOT) or not target.is_file():
        return f"{ref.name}={ref.value!r} does not resolve to a file in the site."
    if (
        resolved.fragment
        and target in pages
        and unquote(resolved.fragment) not in pages[target].ids
    ):
        return f"{ref.name}={ref.value!r} does not resolve to an element."
    if ref.dimensions and target.suffix in {".png", ".webp"}:
        read_dimensions = png_dimensions if target.suffix == ".png" else webp_dimensions
        if read_dimensions(target) != ref.dimensions:
            return f"{ref.name}={ref.value!r} does not match its declared width and height."
    return None


def check_sitemap(expected: dict[str, dict[str, str]]) -> list[str]:
    try:
        urls = ElementTree.parse(ROOT / "sitemap.xml").getroot()
    except (OSError, ElementTree.ParseError) as error:
        return [f"sitemap.xml: {error}"]
    if urls.tag != f"{{{SITEMAP_NS}}}urlset":
        return ["sitemap.xml: Expected the sitemap urlset namespace."]
    locations = Counter(node.findtext(f"{{{SITEMAP_NS}}}loc") for node in urls)
    errors = []
    if locations != Counter(expected.keys()):
        errors.append("sitemap.xml: Expected exactly one canonical URL per indexable page.")
    for node in urls:
        location = node.findtext(f"{{{SITEMAP_NS}}}loc", "")
        links = Counter(
            (item.get("hreflang"), item.get("href"))
            for item in node.findall(f"{{{XHTML_NS}}}link")
            if item.get("rel") == "alternate"
        )
        if location in expected and links != Counter(expected[location].items()):
            errors.append(f"sitemap.xml: Incorrect alternates for {location}.")
    return errors


def check_security_txt(now: datetime) -> list[str]:
    path = ROOT / ".well-known" / "security.txt"
    if not path.is_file():
        return [".well-known/security.txt: File is missing."]
    fields: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            key, separator, value = line.partition(": ")
            if not separator or not value:
                return [f".well-known/security.txt: Invalid field {line!r}."]
            fields.setdefault(key, []).append(value)
    expected = {
        "Contact": [
            "https://github.com/rouxdutoit/fazit/security/advisories/new",
            "mailto:hello@rouxdutoit.com",
        ],
        "Preferred-Languages": ["de, en"],
        "Canonical": [ORIGIN + "/.well-known/security.txt"],
        "Policy": [ORIGIN + "/security/"],
    }
    errors = [
        f".well-known/security.txt: Incorrect or missing {field}."
        for field, values in expected.items()
        if fields.get(field) != values
    ]
    expires = fields.get("Expires", [])
    try:
        if len(expires) != 1 or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", expires[0]):
            raise ValueError
        if datetime.fromisoformat(expires[0]) <= now:
            errors.append(".well-known/security.txt: Expires must be in the future.")
    except ValueError:
        errors.append(".well-known/security.txt: Expected one UTC expiry timestamp.")
    return errors


def check_headers() -> list[str]:
    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    apache = (ROOT / ".htaccess").read_text(encoding="utf-8")
    errors = []
    pair = dict(zip(LANGUAGES, DEMO_ROUTES, strict=True))
    alternate_links = [
        f'<{url}>; rel="alternate"; hreflang="{lang}"' for lang, url in alternates(pair).items()
    ]
    for route in DEMO_ROUTES:
        header = ", ".join([f'<{ORIGIN}{route}>; rel="canonical"', *alternate_links])
        if f"\n{route}\n  Link: {header}\n" not in headers:
            errors.append(f"_headers: Missing canonical and language Link header for {route}.")
        if f"Header always set Link '{header}'" not in apache:
            errors.append(f".htaccess: Missing canonical and language Link header for {route}.")
    policies = (
        (
            "_headers",
            headers,
            r"^/\*\n  Content-Security-Policy: ",
            r"^/demo/\*\n  ! Content-Security-Policy\n  Content-Security-Policy: ",
        ),
        (
            ".htaccess",
            apache,
            r'^<Else>\n  Header always set Content-Security-Policy "',
            r'^<If "%\{REQUEST_URI\} =~ m#\^/demo/#">\n'
            r'  Header always set Content-Security-Policy "',
        ),
    )
    for name, contents, site_rule, demo_rule in policies:
        for rule, sources in ((site_rule, "'self'"), (demo_rule, "'self' data:")):
            if not re.search(rf"{rule}[^\n]*; font-src {sources};", contents, re.M):
                errors.append(f"{name}: Expected font-src {sources} in the matching CSP rule.")
    return errors


def check_coverage(page: Page, lang: str) -> list[str]:
    catalogue = load_catalogue()
    labels = load_locale(lang)["workload"]
    expected: Counter[CoverageCell] = Counter()
    errors = []
    for target in ("openDesk", "Nextcloud"):
        mapping = load_mapping(target.lower(), catalogue)
        for workload in catalogue.workload_ids:
            if workload in mapping.no_function:
                continue
            expected[CoverageCell(workload, "", "", labels[workload])] = 1
            functions = [row for row in mapping.functions if row.workload == workload]
            codes = {row.coverage for row in functions}
            code = codes.pop() if len(codes) == 1 else "in_suite_with_limits"
            if code not in COVERAGE_BADGES:
                errors.append(f"Coverage table {workload} / {target} has no badge for {code}.")
                continue
            badge, names = COVERAGE_BADGES[code]
            replacements = " · ".join(dict.fromkeys(row.replacement[lang] for row in functions))
            expected[CoverageCell(workload, target, badge, f"{names[lang]}: {replacements}")] = 1
    for cell in expected - page.coverage:
        name = f"{cell.workload} / {cell.target}" if cell.target else cell.workload
        errors.append(f"Coverage table {name} should show {cell.text!r}.")
    for cell in page.coverage - expected:
        name = f"{cell.workload} / {cell.target}" if cell.target else cell.workload
        errors.append(f"Coverage table {name} has an unexpected or duplicate cell {cell.text!r}.")
    return errors


def check_tally(page: Page, demo: Page, lang: str) -> list[str]:
    labels = load_locale(lang)["status"]
    total = demo.status_counts.total()
    prefix = {"en": "All {} areas in the sample", "de": "Alle {} Bereiche im Beispiel"}[lang]
    counts = ", ".join(f"{demo.status_counts[status]} {labels[status]}" for status in STATUSES)
    expected = f"{prefix.format(total)}: {counts}."
    return [] if page.tallies == [expected] else [f"Sample tally should read {expected!r}."]


def check_demo_reports() -> list[str]:
    errors = []
    runner = CliRunner()
    with TemporaryDirectory(prefix="fazit-site-") as temporary:
        for lang, route in zip(LANGUAGES, DEMO_ROUTES, strict=True):
            target = local_path(route)
            out = Path(temporary) / lang
            command = ("demo", "--lang", lang, "--sample", "town", "--profile", "opendesk")
            result = runner.invoke(app, [*command, "--out", str(out)])
            name = target.relative_to(ROOT)
            if result.exit_code != 0:
                errors.append(f"{name}: Fazit demo failed. {result.output.strip()}")
                continue
            generated = Path(result.stdout.splitlines()[-1])
            if not generated.is_file() or not target.is_file():
                errors.append(f"{name}: Demo report is missing.")
            elif target.read_bytes() != generated.read_bytes():
                errors.append(f"{name}: Differs from a fresh fazit {' '.join(command)} run.")
    return errors


def check_assets() -> list[str]:
    errors = []
    for filename, dimensions in (("og.png", (1200, 630)), ("apple-touch-icon.png", (180, 180))):
        image = ROOT / filename
        if not image.is_file() or png_dimensions(image) != dimensions:
            errors.append(f"{filename}: Expected a PNG with dimensions {dimensions}.")
    for preview in (ROOT / "images").glob("readiness-*"):
        if preview.suffix in {".png", ".webp"} and preview.stat().st_size >= 150_000:
            errors.append(f"{preview.relative_to(ROOT)}: Must be under 150 KB.")
    if f"Sitemap: {ORIGIN}/sitemap.xml" not in (ROOT / "robots.txt").read_text().splitlines():
        errors.append("robots.txt: Missing sitemap URL.")
    return errors


def check_pages(pages: dict[Path, Page]) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors = []
    declared = {}
    for en, de in PAGE_PAIRS:
        pair = {"en": en, "de": de}
        for lang, other in (("en", "de"), ("de", "en")):
            route = pair[lang]
            declared[ORIGIN + route] = alternates(pair)
            page = pages.get(local_path(route))
            if page is None:
                errors.append(f"{route}: Page is missing.")
                continue
            demo = route in DEMO_ROUTES
            page.check_structure(lang, demo=demo)
            if not demo:
                page.check_metadata(route, other, pair)
            if (en, de) == PAGE_PAIRS[0]:
                page.errors.extend(check_coverage(page, lang))
                if demo_page := pages.get(local_path(f"/demo/{lang}/")):
                    page.errors.extend(check_tally(page, demo_page, lang))
    for path, page in pages.items():
        if ORIGIN + route_for(path) not in declared:
            errors.append(f"{path.relative_to(ROOT)}: Page has no declared language pair.")
        errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in page.errors)
    error_urls = {ORIGIN + route for route in ERROR_ROUTES}
    return errors, {url: pair for url, pair in declared.items() if url not in error_urls}


def main() -> int:
    pages = {
        path: Page(path)
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
    }
    errors, sitemap = check_pages(pages)
    errors.extend(check_sitemap(sitemap))
    errors.extend(check_security_txt(datetime.now(UTC)))
    errors.extend(check_assets())
    errors.extend(check_headers())
    errors.extend(check_demo_reports())

    references = [(path, ref) for path, page in pages.items() for ref in page.references]
    stylesheet = ROOT / "style.css"
    references.extend(
        (stylesheet, ref) for ref in css_references(stylesheet.read_text(encoding="utf-8"), 1)
    )
    for path, ref in references:
        if error := check_reference(route_for(path), ref, pages):
            errors.append(f"{path.relative_to(ROOT)}:{ref.line}: {error}")

    for error in errors:
        print(error)
    if not errors:
        print(f"Checked {len(pages)} pages and {len(references)} references. No errors.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
