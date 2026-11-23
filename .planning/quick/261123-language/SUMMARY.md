# Website language links

All 22 website pages show **Deutsch** on English pages and **English** on German pages in the footer and phone menu. Each link points to the corresponding page and carries the destination language in `lang` and `hreflang`. The visible name labels the link for assistive technology. The shared `.symbol-label` primitive centres the icon and name, and the links share the footer link colours and hover styling.

`site/icons/translate.svg` is the official Google Material Symbols Outlined asset at 24 px, weight 400, grade 0 and fill 0. It uses the existing Apache-2.0 licence and is embedded in `site/style.css` as a byte-matching data URL. D40 records the choice of Outlined for Translate. The shared icon set uses Rounded. [Google source SVG](https://github.com/google/material-design-icons/blob/6d7ca43bd6e6668531a00fcaca06d921b63dd716/symbols/web/translate/materialsymbolsoutlined/translate_24px.svg)

## Verification

- `uv run ruff check .` and `uv run ruff format --check .` passed.
- `uv run pytest -q` passed all 979 tests.
- `uv run python site/check_site.py` passed for 24 pages and 972 references. It checks the destination and language attributes of both links and the bytes of the embedded icon.
- `node site/check_alignment.mjs` passed 8,548 measurements across 144 page views at 360, 768 and 1280 px in light and dark. The maximum offset was 0.30 px against a 0.75 px limit. The check measures both language links wherever they are visible.
- At 360 px, pressing Enter on either language link opened the matching page. The footer link matched its neighbours at rest and on hover in both themes. The phone menu language link was visible with JavaScript disabled.
- Both demo commands succeeded. Their HTML matched the checked-in demos byte for byte, and both opened in offline Chromium with JavaScript disabled and zero HTTP requests.
