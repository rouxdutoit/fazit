# SPDX-License-Identifier: AGPL-3.0-or-later
"""Validate the font declarations shared by the website and the report."""

import re
from collections.abc import Iterator

CSS_DECLARATION = re.compile(r"(?:^|(?<=[;{]))\s*([-\w]+)\s*:\s*([^;{}]+)(?=[;}]|$)")
CSS_FONT_FACE = re.compile(r"@font-face\s*\{([^{}]*)\}", re.I)
FONT_FAMILY = re.compile(r"var\(--(?:sans|mono)\)")
FONT_SHORTHAND = re.compile(
    r"(?:(?:[1-9]00|normal|bold|italic|oblique|small-caps)\s+)*"
    r"(?:var\(--fs-[\w-]+\)|[\d.]+(?:px|rem|em|pt|%))"
    r"(?:\s*/\s*[\d.]+(?:px|rem|em|pt|%)?)?\s+" + FONT_FAMILY.pattern
)


def check_font_families(css: str) -> Iterator[str]:
    names = {
        value.strip().strip("\"'")
        for face in CSS_FONT_FACE.findall(css)
        for prop, value in CSS_DECLARATION.findall(face)
        if prop.lower() == "font-family"
    }
    if names != {"Figtree", "Geist Mono"}:
        yield f"Unexpected @font-face font-family set {sorted(names)}."

    expected = {"--sans": "Figtree", "--mono": '"Geist Mono"'}
    generic = {"ui-sans-serif", "system-ui", "sans-serif", "ui-monospace", "monospace"}
    fonts = {"font-family": FONT_FAMILY, "font": FONT_SHORTHAND}
    tokens = set()
    for prop, value in CSS_DECLARATION.findall(CSS_FONT_FACE.sub("", css)):
        value = value.strip()
        if prop in expected:
            family, *fallbacks = map(str.strip, value.split(","))
            if family != expected[prop] or not set(fallbacks) <= generic:
                yield f"{prop}: {value} must name the assigned font and only generic fallbacks."
            tokens.add(prop)
        if (pattern := fonts.get(prop.lower())) and value != "inherit":
            if not pattern.fullmatch(value):
                yield f"{prop}: {value} must use --sans, --mono or inherit for its family."
    for missing in sorted(expected.keys() - tokens):
        yield f"Missing font token {missing}."
