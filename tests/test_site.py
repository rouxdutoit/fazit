# SPDX-License-Identifier: AGPL-3.0-or-later
from importlib import import_module
from pathlib import Path

import pytest
from helpers import ROOT

JSON_LD = '{"@context": "https://schema.org", "@type": "WebPage"}'


@pytest.mark.parametrize(
    ("attributes", "content", "error"),
    [
        ('type="application/ld+json"', JSON_LD, ""),
        ('src="/site.js"', "", ""),
        ('type="application/ld+json"', "", "Invalid JSON-LD"),
        ('type="application/ld+json"', JSON_LD[:-1] + ', "price": NaN}', "Invalid JSON-LD"),
        ('type="application/ld+json" src="/site.js"', JSON_LD, "Expected the local script"),
        ('type="text/javascript" type="application/ld+json"', JSON_LD, "Expected the local script"),
        ('type="importmap"', JSON_LD, "Expected the local script"),
        ("", "alert(1)", "Unexpected inline script"),
        ('src="/site.js"', "alert(1)", "Unexpected inline script"),
    ],
)
def test_site_only_accepts_inert_json_ld_inline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, attributes: str, content: str, error: str
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "site"))
    page_path = tmp_path / "page.html"
    page_path.write_text(f"<head><script {attributes}>{content}</script></head>", encoding="utf-8")
    page = import_module("check_site").Page(page_path)

    if error:
        assert any(error in item for item in page.errors)
        assert not page.json_ld
    else:
        assert not page.errors
        assert bool(page.json_ld) == bool(content)


def test_llms_text_keeps_coverage_and_commands_readable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "site"))
    reader = import_module("generate_llms").MainText()
    reader.feed(
        """
        <header>Menu</header>
        <main>
          <h1>Compare the suites</h1>
          <p>Choose a target for Microsoft&nbsp;365.</p>
          <table>
            <tr><th>Area</th><th>openDesk</th><th>Nextcloud</th></tr>
            <tr><th>Mail</th><td>In the suite</td><td><span class="sr-only">With limits: </span>
            <svg><title>Decorative</title></svg>Mail app</td></tr>
          </table>
          <dl><dt>Blocker<span class="row-count">1</span></dt><dd>Needs a decision.</dd></dl>
          <h2>Try the demo</h2>
          <code><span class="symbol-label">git clone https://github.com/<wbr>rouxdutoit/fazit</span><span
          class="symbol-label">cd fazit</span></code>
        </main>
        <footer>Navigation</footer>
        """
    )
    reader.close()

    assert reader.title == "Compare the suites"
    assert reader.blocks == [
        "Choose a target for Microsoft 365.",
        "Area | openDesk | Nextcloud",
        "Mail | In the suite | With limits: Mail app",
        "Blocker 1",
        "Needs a decision.",
        "### Try the demo",
        "git clone https://github.com/rouxdutoit/fazit",
        "cd fazit",
    ]
