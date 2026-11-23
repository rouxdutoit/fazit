# SPDX-License-Identifier: AGPL-3.0-or-later
"""Check the bilingual static site and verify the checked-in demo reports."""

import json
import re
import struct
from argparse import ArgumentParser
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, date, datetime
from html import escape
from html.parser import HTMLParser
from itertools import pairwise
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Never
from urllib.parse import unquote, unquote_to_bytes, urljoin, urlsplit
from xml.etree import ElementTree

from generate_llms import render_llms_full
from typer.testing import CliRunner

from fazit import REPOSITORY_URL, __version__
from fazit.catalogue import load_catalogue
from fazit.cli import app
from fazit.errors import InputError
from fazit.fonts.css import CSS_DECLARATION, CSS_FONT_FACE, check_font_families
from fazit.i18n import load_locale
from fazit.mappings import load_mapping
from fazit.output import write_inside
from fazit.status import STATUSES

ROOT = Path(__file__).resolve().parent
ORIGIN = "https://fazit.dev"
LANGUAGES = ("en", "de")
DEMO_ROUTES = ("/demo/en/", "/demo/de/")
ERROR_ROUTES = ("/404.html", "/de/404.html")
JSON_LD_TYPE = "application/ld+json"
STRUCTURED_TYPES = {
    "/": "SoftwareApplication",
    "/about/": "AboutPage",
    "/roadmap/": "WebPage",
    "/start/": "WebPage",
    "/security/": "WebPage",
}
ROBOTS_AGENTS = (
    "*",
    "GPTBot",
    "OAI-SearchBot",
    "ChatGPT-User",
    "ClaudeBot",
    "Claude-SearchBot",
    "PerplexityBot",
    "Google-Extended",
    "Applebot-Extended",
    "CCBot",
)
PAGE_PAIRS = (
    ("/", "/de/"),
    *(
        (f"/{page}/", f"/de/{page}/")
        for page in (
            "start",
            "pilots",
            "integrators",
            "security",
            "about",
            "roadmap",
            "impressum",
            "privacy",
        )
    ),
    ("/coverage/", "/de/coverage/"),
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
CSS_REFS = re.compile(
    r"""url\(\s*["']?(?P<url>[^"')]+)["']?\s*\)"""
    r"""(?:[ \t]+/\* (?P<symbol>icons/[\w-]+\.svg) \*/)?"""
    r"""|@import\s*["'](?P<import_url>[^"']+)""",
    re.I,
)
EMBEDDED_SVG = "data:image/svg+xml,"
CSS_COMMENTS = re.compile(r"/\*.*?\*/", re.S)
CSS_ROOT = re.compile(r"(?:^|(?<=[{}]))\s*:root\s*\{[^{}]*\}")
CSS_COVERAGE = re.compile(r"[^{};]*\.cov(?:-[\w-]+)?(?![\w-])[^{};]*\{([^{}]*)\}")
CSS_COLOUR = re.compile(r"#[0-9a-f]{3,8}\b|\b(?:rgba?|hsla?)\([^)]*\)", re.I)
STATUS_PALETTES = {
    "": {
        "--status-blocker": "light-dark(#ff8d28,#ff9230)",
        "--status-needs-work": "light-dark(#ffcc00,#ffd600)",
        "--status-ready": "light-dark(#34c759,#30d158)",
        "--status-unknown": "#8e8e93",
    },
    "screen and (prefers-contrast: more)": {
        "--status-blocker": "light-dark(#c55300,#ffa056)",
        "--status-needs-work": "light-dark(#a16a00,#fedf43)",
        "--status-ready": "light-dark(#008932,#4ad968)",
        "--status-unknown": "light-dark(#6c6c70,#aeaeb2)",
    },
}
# These neutral shadows give the menu and cards depth in either palette.
SHADOW_COLOURS = {"rgb(0 0 0 / 4%)", "rgb(0 0 0 / 8%)", "rgb(0 0 0 / 18%)"}


@dataclass(frozen=True)
class Reference:
    name: str
    value: str
    line: int
    plain_link: bool = False
    dimensions: tuple[int, int] | None = None
    symbol_source: str | None = None


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
        value = (match["url"] or match["import_url"]).strip()
        yield Reference(
            "CSS URL",
            value,
            first_line + css.count("\n", 0, match.start()),
            symbol_source=match["symbol"],
        )


def invalid_json_constant(value: str) -> Never:
    raise ValueError(f"{value} is not valid JSON.")


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
        self._buttons_needing_icons: dict[int, int] = {}
        self._buttons_without_icons: list[int] = []
        self._title_text: list[str] = []
        self._json_ld_text: list[str] | None = None
        self.json_ld: list[dict] = []
        self._coverage_table = False
        self._workload = ""
        self._target: str | None = None
        self._badge = ""
        self._cell_text: list[str] = []
        self.nav_controls: list[str] = []
        self.language = ""
        self.doctype = False
        self.source = path.read_text(encoding="utf-8")
        self.feed(self.source)
        self.close()
        self.title = " ".join("".join(self._title_text).split())

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
        if tag == "script":
            if attrs == [("type", JSON_LD_TYPE)] and self.stack[-2:-1] == ["head"]:
                self._json_ld_text = []
            elif (
                urlsplit(values.get("src", "")).path != "/site.js"
                or "type" in values
                or len(attrs) != len(values)
            ):
                self.errors.append(f"Expected the local script or inline JSON-LD on line {line}.")
        if any(name.startswith("on") or name == "ping" for name in values):
            self.errors.append(f"Event handlers and link tracking are disallowed on line {line}.")
        self.record_metadata(tag, values, line)
        self.record_references(tag, values, line)

        classes = values.get("class", "").split()
        self.record_button_icon(tag, classes, line)
        if tag == "button" and values.get("aria-controls") == "site-nav":
            self.nav_controls.append("toggle")
        elif tag == "nav" and values.get("id") == "site-nav":
            self.nav_controls.append("links")
        elif tag == "a" and "bar-cta" in classes:
            self.nav_controls.append("action")
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
        if tag == "article" and values.get("id", "").startswith("readiness-"):
            self.status_counts[values.get("data-status", "")] += 1

    def record_button_icon(self, tag: str, classes: list[str], line: int) -> None:
        if self._buttons_needing_icons and tag == "span" and "btn-icon" in classes:
            if any(
                re.fullmatch(r"icon-[\w-]+", name)
                and (ROOT / "icons" / f"{name.removeprefix('icon-')}.svg").is_file()
                for name in classes
            ):
                self._buttons_needing_icons.clear()
        if "btn" in classes:
            if tag in VOID:
                self._buttons_without_icons.append(line)
            else:
                self._buttons_needing_icons[len(self.stack)] = line

    def record_metadata(self, tag: str, attrs: dict[str, str], line: int) -> None:
        href = attrs.get("href", "")
        hreflang = attrs.get("hreflang", "")
        if tag == "link":
            relations = attrs.get("rel", "").lower().split()
            if {"canonical", "alternate"}.intersection(relations) and "head" not in self.stack:
                self.errors.append(f"Canonical and alternate links belong in head on line {line}.")
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
            if key in {"description", "robots"} or key.startswith(("og:", "twitter:")):
                attribute = "property" if key.startswith("og:") else "name"
                if "head" not in self.stack or attrs.get(attribute) != key or key in self.meta:
                    self.errors.append(f"Misplaced, malformed or duplicate metadata {key}.")
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
        if self.stack and self.stack[-1] == "script":
            if self._json_ld_text is not None:
                self._json_ld_text.append(data)
            elif data.strip():
                self.errors.append(f"Unexpected inline script on line {self.getpos()[0]}.")
        if self.stack[-2:] == ["head", "title"]:
            self._title_text.append(data)
        if self._target is not None:
            self._cell_text.append(data)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing tag </{tag}> on line {self.getpos()[0]}.")
        else:
            if button_line := self._buttons_needing_icons.pop(len(self.stack), None):
                self._buttons_without_icons.append(button_line)
            self.stack.pop()
        if tag == "script" and self._json_ld_text is not None:
            self.record_json_ld(self._json_ld_text)
            self._json_ld_text = None
        if tag in {"th", "td"} and self._target is not None:
            cell = " ".join("".join(self._cell_text).split())
            self.coverage[CoverageCell(self._workload, self._target, self._badge, cell)] += 1
            self._target = None
        elif tag == "table":
            self._coverage_table = False

    def record_json_ld(self, parts: list[str]) -> None:
        try:
            data = json.loads("".join(parts), parse_constant=invalid_json_constant)
        except ValueError as error:
            self.errors.append(f"Invalid JSON-LD: {error}")
            return
        if not isinstance(data, dict) or data.get("@context") != "https://schema.org":
            self.errors.append("Expected a Schema.org JSON-LD object.")
            return
        self.json_ld.append(data)

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
        if not demo:
            if not any(ref.plain_link and ref.value == "#main" for ref in self.references):
                self.errors.append("Missing skip link to #main.")
            if self.nav_controls != ["toggle", "links", "action"]:
                self.errors.append("Expected the menu toggle, navigation and one action in order.")
            self.errors.extend(
                f"Expected a btn-icon span with a matching SVG for the button on line {line}."
                for line in sorted(self._buttons_without_icons)
            )

    def check_metadata(self, route: str, pair: dict[str, str], lang: str) -> None:
        description = self.meta.get("description", "")
        if not self.title.endswith(" · Fazit") or len(self.title) >= 60:
            self.errors.append(
                "Title must have a subject, end in ' · Fazit' and be under 60 characters."
            )
        if not 120 <= len(description.strip()) <= 160:
            self.errors.append("Meta description must be 120–160 characters.")
        if self.canonicals != [ORIGIN + route]:
            self.errors.append("Expected one canonical URL for the page.")
        if Counter(self.alternates) != Counter(alternates(pair).items()):
            self.errors.append("Expected en, de and x-default hreflang links for the page pair.")
        noindex = "noindex" in re.split(r"[\s,]+", self.meta.get("robots", "").lower())
        if noindex != (route in ERROR_ROUTES):
            self.errors.append("Only the error pages should set noindex.")
        for key, value in social_metadata(route, lang, self.title, description).items():
            if self.meta.get(key) != value:
                self.errors.append(f"Incorrect or missing metadata {key}.")

    def check_structured_data(self, en_route: str) -> None:
        expected = STRUCTURED_TYPES.get(en_route)
        if len(self.json_ld) != int(expected is not None):
            self.errors.append("Incorrect number of Schema.org JSON-LD blocks.")
            return
        if expected is None:
            return
        (data,) = self.json_ld
        if en_route == "/":
            graph = data.get("@graph")
            if not isinstance(graph, list) or not all(isinstance(node, dict) for node in graph):
                self.errors.append("Home JSON-LD must have a graph of Schema.org objects.")
                return
            types = [node.get("@type") for node in graph]
            if len(types) != 3 or any(
                kind not in types for kind in (expected, "WebSite", "Person")
            ):
                self.errors.append("Home JSON-LD must describe the software, site and author.")
                return
            software = graph[types.index(expected)]
            if software.get("softwareVersion") != __version__:
                self.errors.append(f"JSON-LD softwareVersion must match Fazit {__version__}.")
        elif data.get("@type") != expected:
            self.errors.append(f"Expected JSON-LD of type {expected}.")


def social_metadata(route: str, lang: str, title: str, description: str) -> dict[str, str]:
    image = ORIGIN + "/og.png"
    alt = "Fazit-Wortmarke" if lang == "de" else "Fazit wordmark"
    locale, other = ("de_DE", "en_GB") if lang == "de" else ("en_GB", "de_DE")
    return {
        "og:type": "website",
        "og:site_name": "Fazit",
        "og:title": title,
        "og:description": description,
        "og:url": ORIGIN + route,
        "og:locale": locale,
        "og:locale:alternate": other,
        "og:image": image,
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": alt,
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": image,
        "twitter:image:alt": alt,
    }


def alternates(pair: dict[str, str]) -> dict[str, str]:
    return {lang: ORIGIN + route for lang, route in pair.items()} | {
        "x-default": ORIGIN + pair["en"]
    }


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


def check_embedded_symbol(ref: Reference) -> str | None:
    if ref.symbol_source is None:
        return "Expected an icons/*.svg source comment after the embedded symbol URL."
    if not ref.value.startswith(EMBEDDED_SVG) or re.search(r"[\s<>#]", ref.value):
        return f"Expected a URL-encoded SVG for {ref.symbol_source}."
    source = ROOT / ref.symbol_source
    decoded = unquote_to_bytes(ref.value.removeprefix(EMBEDDED_SVG))
    if not source.is_file() or decoded != source.read_bytes():
        return f"Embedded symbol does not match {ref.symbol_source} byte for byte."
    return None


def check_reference(route: str, ref: Reference, pages: dict[Path, Page]) -> str | None:
    if not ref.value.strip():
        return f"{ref.name} is empty."
    stylesheet_url = route == "/style.css" and ref.name == "CSS URL"
    if stylesheet_url and (ref.symbol_source or ref.value.startswith(EMBEDDED_SVG)):
        return check_embedded_symbol(ref)
    if ref.name == "CSS URL" and EMBEDDED_FONT.fullmatch(ref.value):
        return None
    raw = urlsplit(ref.value)
    if raw.scheme in {"https", "mailto", "tel"} and ref.plain_link and raw.netloc != "fazit.dev":
        return None
    resolved = urlsplit(urljoin(ORIGIN + route, ref.value))
    if resolved.scheme != "https" or resolved.netloc != "fazit.dev":
        return f"{ref.name}={ref.value!r} is an external resource or unsupported link."
    target = local_path(resolved.path or "/")
    if stylesheet_url and target.is_relative_to(ROOT / "icons"):
        return f"Expected an embedded symbol for {target.relative_to(ROOT)}."
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
        lastmods = node.findall(f"{{{SITEMAP_NS}}}lastmod")
        lastmod = (lastmods[0].text or "") if len(lastmods) == 1 else ""
        try:
            valid_lastmod = date.fromisoformat(lastmod).isoformat() == lastmod
        except ValueError:
            valid_lastmod = False
        if not valid_lastmod:
            errors.append(f"sitemap.xml: Expected one YYYY-MM-DD lastmod for {location}.")
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


def check_cache_headers(headers: str) -> list[str]:
    expected = {
        "/*": "no-cache",
        "/fonts/*": "public, max-age=86400",
        "/icons/*": "public, max-age=86400",
        "/images/*": "public, max-age=86400",
    }
    cache_headers: dict[str, list[str]] = {}
    path = ""
    for line in headers.splitlines():
        if line.startswith("/"):
            path = line.rstrip()
        else:
            name, _, value = line.strip().partition(":")
            if name.lower() == "cache-control":
                cache_headers.setdefault(path, []).append(value.strip())
    errors = [
        f"_headers: Expected exactly one Cache-Control value of {value!r} for {path}."
        for path, value in expected.items()
        if cache_headers.get(path) != [value]
    ]
    errors.extend(
        f"_headers: Unexpected Cache-Control rule for {path}."
        for path in cache_headers
        if path not in expected
    )
    return errors


def check_headers() -> list[str]:
    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    apache = (ROOT / ".htaccess").read_text(encoding="utf-8")
    errors = check_cache_headers(headers)
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
            matches = re.findall(rf'{rule}([^"\n]+)', contents, re.M)
            directives = [part.strip() for policy in matches for part in policy.split(";")]
            if [part for part in directives if part.startswith("font-src ")] != [
                f"font-src {sources}"
            ]:
                errors.append(f"{name}: Expected font-src {sources} in the matching CSP rule.")
            # JSON-LD is a data block. Executable scripts need a same-origin source.
            if [part for part in directives if part.lower().startswith("script-src")] != [
                "script-src 'self'"
            ]:
                errors.append(f"{name}: Expected only script-src 'self' in the matching CSP rule.")
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


def check_home_costs(markup: str, demo: Page) -> list[str]:
    summary = demo.source.partition('<div class="subsection summary-costs">')[2]
    summary = summary.partition("</ul>")[0]
    tiles = (
        r'<li data-cost-tile="([^"]+)">\s*<p class="tile-label">([^<]+)</p>\s*'
        r'<span class="figure-num">([^<]+)</span>'
    )
    origin = r'<p class="note-text cost-origin" data-cost-origin="([^"]+)">([^<]+)</p>'
    expected_tiles = re.findall(tiles, summary)
    expected_origin = re.findall(origin, summary)
    errors = []
    if len(expected_tiles) != 3 or re.findall(tiles, markup) != expected_tiles:
        errors.append("Cost tiles must show the three sample report totals.")
    if len(expected_origin) != 1 or re.findall(origin, markup) != expected_origin:
        errors.append("Cost tiles must show the calculation origin from the sample report.")
    return errors


def status_preview(markup: str) -> str:
    summary = re.search(
        r'<p class="sec-intro">[^<]+</p>\s*<dl class="status-summary">.*?</dl>', markup, re.S
    )
    return re.sub(r">\s+<", "><", summary[0]) if summary else ""


def check_home(page: Page, demo: Page, lang: str) -> list[str]:
    prefix = "/de" if lang == "de" else ""
    sample = f"/demo/{lang}/"
    destinations = {
        "hero": [f"{sample}#readiness-telephony", f"{sample}#status-blocker", sample],
        "example": [f"{sample}#readiness-title"],
        "costs": [f"{sample}#costs-title"],
        "privacy": [f"{prefix}/security/"],
        "how": [f"{prefix}/start/"],
        "status": [f"{prefix}/pilots/", f"{prefix}/about/"],
    }
    main = page.source.partition("<main")[2].partition("</main>")[0]
    sections = dict(re.findall(r'<section [^>]*\bid="([^"]+)"[^>]*>(.*?)</section>', main, re.S))
    if list(sections) != list(destinations):
        return ["Expected the six home sections in order."]
    errors = []
    for section, links in destinations.items():
        if re.findall(r'<a class="more(?: [^"]+)?" href="([^"]+)"', sections[section]) != links:
            errors.append(f"Home section {section} must link to {', '.join(links)}.")
    caption = re.search(r"<figcaption\b[^>]*>(.*?)</figcaption>", sections["hero"], re.S)
    download = rf'<a\b[^>]* href="{sample}" download="fazit-sample-report-{lang}\.html"'
    if (
        not caption
        or len(re.findall(r"<a\b", caption[1])) != 1
        or not re.search(download, caption[1])
    ):
        errors.append("The home report caption must contain one link that downloads the sample.")
    preview = status_preview(sections["hero"])
    if not preview or preview != status_preview(demo.source):
        errors.append("The hero preview must show the sample report's four status rows.")
    headings = re.findall(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", main, re.S)
    if any(re.sub(r"<[^>]+>", "", heading).rstrip().endswith(".") for heading in headings):
        errors.append("Home headings should omit the final full stop.")
    errors.extend(check_home_costs(sections["costs"], demo))
    return errors


def check_area_counts(demo: Page, lang: str) -> list[str]:
    total = str(demo.status_counts.total())
    prefix = "/de" if lang == "de" else ""
    pattern = r"<span data-assessed-areas>\s*([0-9]+)\s*</span>"
    errors = []
    for route, number in ((f"{prefix}/", 1), (f"{prefix}/pilots/", 1)):
        path = local_path(route)
        expected = [total] * number
        if path.is_file() and re.findall(pattern, path.read_text(encoding="utf-8")) != expected:
            errors.append(f"{path.relative_to(ROOT)}: Expected {total} assessed areas.")
    return errors


def check_commands(lang: str) -> list[str]:
    prefix = "/de" if lang == "de" else ""
    expected = [f"git clone {REPOSITORY_URL}", "cd fazit", "uv run fazit demo"]
    if lang == "de":
        expected[-1] += " --lang de"
    components = []
    errors = []
    for route in (f"{prefix}/", f"{prefix}/start/"):
        path = local_path(route)
        if not path.is_file():
            continue
        markup = path.read_text(encoding="utf-8")
        component = re.search(
            r'<div class="command"[^>]*>.*?<p class="copy-message" role="status"></p>\s*</div>',
            markup,
            re.S,
        )
        if component is None:
            errors.append(f"{route}: Expected the shared command block and its copy status.")
            continue
        block = component[0]
        components.append(re.sub(r">\s+<", "><", block))
        code = re.search(r"<code>(.*?)</code>", block, re.S)
        commands = (
            re.findall(r'<span class="symbol-text">([^<]+)</span>', code[1].replace("<wbr>", ""))
            if code
            else []
        )
        if commands != expected:
            errors.append(f"{route}: Expected the three demo commands for {lang}.")
        if not re.search(r"<button [^>]*\bdata-copy(?:\s|>)", block) or not all(
            re.search(rf'\b{flag}="[^"]+"', block) for flag in ("data-copied", "data-manual")
        ):
            errors.append(f"{route}: Expected copy feedback and manual-copy instructions.")
    if len(components) == 2 and components[0] != components[1]:
        errors.append(f"{prefix}/: Home and Start should use the same command block.")
    return errors


def check_roadmap(page: Page) -> list[str]:
    timeline = page.source.partition('<ol class="timeline"')[2].partition("</ol>")[0]
    steps = re.findall(r'<li class="timeline-step( on)?"', timeline)
    errors = []
    if steps != [" on", "", ""]:
        errors.append("Expected three timeline steps with only the first marked as available.")
    guide = f"{REPOSITORY_URL}/blob/main/CONTRIBUTING.md#translating-fazit"
    if not any(ref.plain_link and ref.value == guide for ref in page.references):
        errors.append("Expected a link to the translation guide.")
    return errors


def demo_with_metadata(markup: str, lang: str) -> str:
    pair = dict(zip(LANGUAGES, DEMO_ROUTES, strict=True))
    route = pair[lang]
    copy = load_locale(lang)["demo_page"]
    title, description = copy["title"], copy["description"]
    head = [
        f'<meta name="description" content="{escape(description)}">',
        f"<title>{escape(title)}</title>",
        f'<link rel="canonical" href="{ORIGIN}{route}">',
    ]
    head.extend(
        f'<link rel="alternate" hreflang="{language}" href="{url}">'
        for language, url in alternates(pair).items()
    )
    for key, value in social_metadata(route, lang, title, description).items():
        attribute = "property" if key.startswith("og:") else "name"
        head.append(f'<meta {attribute}="{key}" content="{escape(value)}">')
    result, count = re.subn(
        r"^  <title>[^<]+</title>$",
        lambda _: "\n".join(f"  {line}" for line in head),
        markup,
        count=1,
        flags=re.M,
    )
    if not count:
        raise ValueError("The CLI demo is missing its title.")
    return result


def check_demo_reports(*, write: bool = False) -> list[str]:
    errors = []
    runner = CliRunner()
    updates: dict[Path, str] = {}
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
            if not generated.is_file():
                errors.append(f"{name}: Fazit demo produced no report.")
                continue
            expected = demo_with_metadata(generated.read_text(encoding="utf-8"), lang)
            if write:
                updates[target] = expected
            elif not target.is_file() or target.read_bytes() != expected.encode("utf-8"):
                errors.append(f"{name}: Rebuild with python site/check_site.py --write-demos.")
    if not errors:
        for target, markup in updates.items():
            try:
                write_inside(target.parent, target.name, markup)
            except InputError:
                return [f"{target.relative_to(ROOT)}: Could not write the published demo."]
    return errors


def check_assets() -> list[str]:
    errors = []
    for filename, dimensions in (
        ("og.png", (1200, 630)),
        ("apple-touch-icon.png", (180, 180)),
    ):
        image = ROOT / filename
        if not image.is_file() or png_dimensions(image) != dimensions:
            errors.append(f"{filename}: Expected a PNG with dimensions {dimensions}.")
        elif filename.startswith("og") and image.stat().st_size >= 100_000:
            errors.append(f"{filename}: Must be under 100 KB.")
    return errors


def check_robots() -> list[str]:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    allowed = {
        line.removeprefix("User-agent: ")
        for part in robots.split("\n\n")
        if "Allow: /" in part.splitlines()
        for line in part.splitlines()
        if line.startswith("User-agent: ")
    }
    errors = [
        f"robots.txt: Explicitly allow {agent}." for agent in ROBOTS_AGENTS if agent not in allowed
    ]
    if re.search(r"^[ \t]*Disallow:[ \t]*\S", robots, re.M | re.I):
        errors.append("robots.txt: All paths should be allowed.")
    if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots.splitlines():
        errors.append("robots.txt: Missing sitemap URL.")
    return errors


def check_llms_full() -> list[str]:
    path = ROOT / "llms-full.txt"
    try:
        if path.read_text(encoding="utf-8") == render_llms_full(ROOT):
            return []
    except OSError as error:
        return [f"llms-full.txt: {error}"]
    return ["llms-full.txt: Rebuild with python site/generate_llms.py."]


def _check_design_urls(css: str) -> Iterator[str]:
    for face in CSS_FONT_FACE.findall(css):
        for ref in css_references(face, 1):
            if (
                not re.fullmatch(r"fonts/[\w-]+\.woff2", ref.value)
                or not (ROOT / ref.value).is_file()
            ):
                yield f"@font-face URL {ref.value!r} must name a local WOFF2 font."
    for ref in css_references(CSS_FONT_FACE.sub("", css), 1):
        # check_reference verifies the source comment and the bytes of each embedded symbol.
        if not ref.value.startswith(EMBEDDED_SVG) or ref.symbol_source is None:
            yield f"CSS URL {ref.value!r} must embed a symbol from icons/."


def _svg_paths(svg: bytes) -> set[str]:
    root = ElementTree.fromstring(svg)
    return {
        " ".join(path.attrib["d"].split())
        for path in root.findall(".//{*}path")
        if "d" in path.attrib
    }


def _check_coverage_symbols(css: str, template: str) -> Iterator[str]:
    package = ROOT.parent / "src" / "fazit"
    macro = template.partition("macro status_contents(")[2].split("endmacro", 1)[0]
    names = dict(re.findall(r"'([\w]+)'\s*:\s*'([\w-]+)'", macro))
    if set(names) != set(STATUSES):
        yield "Could not read every status symbol from status_contents in report.html.j2."
        return
    status_paths = {}
    for name in names.values():
        source = package / "icons" / f"{name}.svg"
        try:
            paths = _svg_paths(source.read_bytes())
        except (OSError, ElementTree.ParseError):
            yield f"Status symbol {name}.svg must be a readable SVG."
            continue
        if not paths:
            yield f"Status symbol {name}.svg has no SVG path."
        status_paths.update(dict.fromkeys(paths, name))
    for rule in CSS_COVERAGE.findall(css):
        for ref in css_references(rule, 1):
            if not ref.value.startswith(EMBEDDED_SVG):
                continue
            name = ref.symbol_source or "embedded coverage symbol"
            svg = unquote_to_bytes(ref.value.removeprefix(EMBEDDED_SVG))
            try:
                reused = _svg_paths(svg) & status_paths.keys()
            except ElementTree.ParseError:
                yield f"Coverage symbol {name} is not valid SVG."
                continue
            for status_icon in sorted({status_paths[path] for path in reused}):
                yield f"Coverage symbol {name} reuses the path of status symbol {status_icon}.svg."


def check_status_palette(css: str, filename: str) -> Iterator[str]:
    source = CSS_COMMENTS.sub("", css)
    for media, expected in STATUS_PALETTES.items():
        start = rf"@media\s+{re.escape(media)}\s*\{{\s*" if media else ""
        root = re.search(start + r":root\s*\{[^{}]*\}", source)
        actual = {
            name: re.sub(r"\s+", "", value.lower())
            for name, value in CSS_DECLARATION.findall(root[0] if root else "")
            if name.startswith("--status-")
        }
        for token in sorted(expected.keys() | actual.keys()):
            if actual.get(token) != expected.get(token):
                mode = "increased contrast" if media else "default"
                yield f"{filename}: {token} differs from the Apple {mode} palette."
    names = STATUS_PALETTES[""].keys()
    declarations = Counter(name for name, _ in CSS_DECLARATION.findall(source) if name in names)
    if declarations != dict.fromkeys(names, len(STATUS_PALETTES)):
        yield f"{filename}: Status tokens belong in the default and increased contrast palettes."
    if not re.search(r"@media\s+print\s*\{\s*:root\s*\{\s*color-scheme:\s*light;", source):
        yield f"{filename}: Print must use the default light palette."


def check_design(css: str, template: str) -> list[str]:
    source = CSS_COMMENTS.sub("", CSS_REFS.sub("", css))
    errors = []
    for prop, value in CSS_DECLARATION.findall(CSS_ROOT.sub("", source)):
        for colour in CSS_COLOUR.findall(value):
            if prop.lower() != "box-shadow" or colour not in SHADOW_COLOURS:
                errors.append(f"{prop}: {value.strip()} uses colour {colour} outside :root.")
    errors.extend(check_font_families(source))
    errors.extend(_check_design_urls(css))
    errors.extend(_check_coverage_symbols(css, template))
    return [f"style.css: {error}" for error in errors]


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
            page.check_metadata(route, pair, lang)
            page.check_structured_data(en)
            switch = (pair[other], other, other)
            if not demo and page.switches != [switch, switch]:
                page.errors.append("Both language links must point to the corresponding page.")
            if en == "/coverage/":
                page.errors.extend(check_coverage(page, lang))
            elif en == "/roadmap/":
                page.errors.extend(check_roadmap(page))
            elif en == "/":
                page.errors.extend(check_commands(lang))
                if demo_page := pages.get(local_path(f"/demo/{lang}/")):
                    page.errors.extend(check_home(page, demo_page, lang))
                    errors.extend(check_area_counts(demo_page, lang))
    for path, page in pages.items():
        if ORIGIN + route_for(path) not in declared:
            errors.append(f"{path.relative_to(ROOT)}: Page has no declared language pair.")
        errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in page.errors)
    error_urls = {ORIGIN + route for route in ERROR_ROUTES}
    return errors, {url: pair for url, pair in declared.items() if url not in error_urls}


def check_unique_metadata(pages: dict[Path, Page]) -> Iterator[str]:
    seen: dict[tuple[str, str], Path] = {}
    for path, page in pages.items():
        for field, value in (
            ("title", page.title),
            ("description", page.meta.get("description", "")),
        ):
            key = (field, " ".join(value.casefold().split()))
            if key in seen:
                first = seen[key].relative_to(ROOT)
                yield f"{path.relative_to(ROOT)}: Duplicate {field} from {first}."
            elif value:
                seen[key] = path


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-demos", action="store_true", help="Rebuild the public sample reports."
    )
    args = parser.parse_args()
    if args.write_demos:
        errors = check_demo_reports(write=True)
        for error in errors:
            print(error)
        return int(bool(errors))
    pages = {
        path: Page(path)
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
    }
    errors, sitemap = check_pages(pages)
    errors.extend(check_unique_metadata(pages))
    errors.extend(check_sitemap(sitemap))
    errors.extend(check_security_txt(datetime.now(UTC)))
    errors.extend(check_assets())
    errors.extend(check_robots())
    errors.extend(check_llms_full())
    errors.extend(check_headers())
    errors.extend(check_demo_reports())

    references = [(path, ref) for path, page in pages.items() for ref in page.references]
    stylesheet = ROOT / "style.css"
    css = stylesheet.read_text(encoding="utf-8")
    template_path = ROOT.parent / "src" / "fazit" / "templates" / "report.html.j2"
    template = template_path.read_text(encoding="utf-8")
    errors.extend(check_design(css, template))
    errors.extend(check_status_palette(css, stylesheet.name))
    report_css = template.partition("<style>")[2].partition("</style>")[0]
    errors.extend(check_status_palette(report_css, template_path.name))
    references.extend((stylesheet, ref) for ref in css_references(css, 1))
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
