// SPDX-License-Identifier: AGPL-3.0-or-later
import assert from "node:assert/strict";
import { localContext, widths, withSite } from "./check_browser.mjs";

const capsules = ".btn, .badge, .segmented label, .category-filter > button";
const menuItems = ".bar-links a, .category-filter option";
const centredLabels = `${capsules}, ${menuItems}, a.language`;
const symbolOnly = ".copy, .menu-button, .foot-mail, .report-card-control, .cost-segment.is-unknown";
const textOnly = ".badge:not(.status), .bar-links a:not(.btn, .language), .segmented label:has(#f-status-all), .finding-evidence dd";
const chevronLabels = ".more, .tile-link h3, .replacement-status, .category-filter > button, summary:not(.menu-button)";
// Keep the component selectors so dropping the primitive from known markup fails the check.
const components = [
  centredLabels, symbolOnly, chevronLabels, ".symbol-label", ".status",
  ".cov-cell", ".coverage-key", ".safeguards li", ":is(h3, h4):has(> .tile-icon)",
  ".timeline-name", ".report-card-bar", ".cost-bars .legend li", ".command-line code > span",
  ".status-summary dt", ".finding-evidence dd", ".privacy-facts h3", ".flow-links > a",
].join(", ");

function measureInPage({ scope, components, centredLabels, symbolOnly, textOnly, chevronLabels, tolerance }) {
  const fontSample = 512;
  const surface = document.createElement("canvas");
  surface.width = surface.height = fontSample;
  const canvas = surface.getContext("2d", { willReadFrequently: true });
  const stems = new Map();
  const failures = [];
  let count = 0;
  let maximum = 0;

  function selector(element) {
    const id = element.closest("[id]")?.id;
    if (element.id) return "#" + CSS.escape(element.id);
    const classes = [...element.classList].filter(name => !["symbol-label", "symbol-text", "symbol-wrap"].includes(name));
    const href = element.getAttribute("href");
    return (id ? "#" + CSS.escape(id) + " " : "") + element.localName
      + classes.map(name => "." + CSS.escape(name)).join("") + (href ? `[href="${href}"]` : "");
  }

  function font(element, size) {
    const style = getComputedStyle(element);
    return `${style.fontStyle} ${style.fontWeight} ${size ?? style.fontSize} ${style.fontFamily}`;
  }

  function metrics(element, text, size) {
    canvas.font = font(element, size);
    return canvas.measureText(text);
  }

  function stemWidth(label, em) {
    canvas.font = font(label, `${fontSample}px`);
    if (!stems.has(canvas.font)) {
      // The left stem of H is clear of the crossbar at this height.
      const base = fontSample - 32;
      canvas.clearRect(0, 0, fontSample, fontSample);
      canvas.fillText("H", 16, base);
      const { data } = canvas.getImageData(0, base - Math.round(0.2 * fontSample), fontSample, 1);
      let first = 3;
      while (first < data.length && data[first] < 128) first += 4;
      let last = first;
      while (last < data.length && data[last] >= 128) last += 4;
      stems.set(canvas.font, (last - first) / (4 * fontSample));
    }
    return stems.get(canvas.font) * em;
  }

  function baseline(element) {
    const probe = document.createElement("span");
    probe.style.cssText = "display:inline-block;width:0;height:0;vertical-align:baseline";
    element.prepend(probe);
    const y = probe.getBoundingClientRect().bottom;
    probe.remove();
    return y;
  }

  function centre(box) {
    return (box.top + box.bottom) / 2;
  }

  function capCentre(label) {
    if (!label) return NaN;
    const { actualBoundingBoxAscent } = metrics(label, "H");
    return baseline(label) - actualBoundingBoxAscent / 2;
  }

  function inkCentre(symbol) {
    if (symbol.matches(".command-prompt")) {
      const { content } = getComputedStyle(symbol, "::before");
      const glyph = content.match(/^"([^"]+)"/)?.[1] ?? "";
      const { actualBoundingBoxAscent, actualBoundingBoxDescent } = metrics(symbol, glyph);
      return glyph ? baseline(symbol) + (actualBoundingBoxDescent - actualBoundingBoxAscent) / 2 : NaN;
    }
    if (symbol.matches(".menu-icon")) {
      const strokes = [...symbol.children].map(stroke => stroke.getBoundingClientRect());
      return (Math.min(...strokes.map(box => box.top)) + Math.max(...strokes.map(box => box.bottom))) / 2;
    }
    const box = symbol.getBoundingClientRect();
    return box.width && box.height ? centre(box) : NaN;
  }

  function compare(element, check, offset, limit = tolerance) {
    count += 1;
    if (Number.isFinite(offset)) maximum = Math.max(maximum, Math.abs(offset));
    if (!Number.isFinite(offset) || Math.abs(offset) > limit) {
      failures.push({ selector: selector(element), check, offset: Number.isFinite(offset) ? offset.toFixed(2) : "missing box" });
    }
  }

  function lastLetter(label, em) {
    // The picker clones the selected option's label into selectedcontent.
    const text = (label.querySelector(":scope > .symbol-text") ?? label).firstChild;
    if (text?.nodeType !== Node.TEXT_NODE || !text.data.trim()) return {};
    const letters = [...text.data.trim()];
    const first = text.data.length - text.data.trimStart().length;
    const end = text.data.trimEnd().length;
    const last = letters.at(-1);
    const range = document.createRange();
    range.setStart(text, first);
    range.setEnd(text, first + letters[0].length);
    const firstLine = range.getBoundingClientRect().top;
    range.setStart(text, end - last.length);
    range.setEnd(text, end);
    const box = range.getBoundingClientRect();
    const { width, actualBoundingBoxRight } = metrics(label, last, `${fontSample}px`);
    const tracking = parseFloat(getComputedStyle(label).letterSpacing) || 0;
    const bearing = (width - actualBoundingBoxRight) * em / fontSample + tracking;
    return { right: box.right - bearing, lineOffset: box.top - firstLine };
  }

  function measureChevron(pair, svg, label) {
    const path = svg.querySelector(":scope > path:only-child");
    const style = path && getComputedStyle(path);
    const labelStyle = getComputedStyle(label);
    if (!path || style.stroke !== labelStyle.color || style.fill !== "none"
      || style.strokeLinecap !== "round" || style.strokeLinejoin !== "round"
      || style.vectorEffect !== "non-scaling-stroke") {
      failures.push({ selector: selector(pair), check: "chevron path, stroke or colour", offset: "—" });
      return;
    }

    // Round caps and joins extend the line bounds by half the non-scaling stroke.
    const stroke = parseFloat(style.strokeWidth);
    const radius = stroke / 2;
    const matrix = path.getScreenCTM();
    const length = path.getTotalLength();
    const points = [0, length / 2, length].map(offset => path.getPointAtLength(offset).matrixTransform(matrix));
    const xs = points.map(point => point.x);
    const ys = points.map(point => point.y);
    const ink = {
      left: Math.min(...xs) - radius, right: Math.max(...xs) + radius,
      top: Math.min(...ys) - radius, bottom: Math.max(...ys) + radius,
    };
    const em = parseFloat(labelStyle.fontSize);
    const turned = pair.matches(".category-filter > button, details[open] > summary");
    const inkWidth = ink.right - ink.left;
    const inkHeight = ink.bottom - ink.top;
    const [ends, tip] = turned ? [ys, xs] : [xs, ys];
    if (ends[1] <= Math.max(ends[0], ends[2])) {
      failures.push({ selector: selector(pair), check: "chevron direction", offset: "—" });
    }
    compare(pair, "chevron angle", tip[1] - (tip[0] + tip[2]) / 2);
    compare(pair, "chevron ink width", (turned ? inkHeight : inkWidth) - 0.29 * em, 0.01 * em);
    compare(pair, "chevron ink height", (turned ? inkWidth : inkHeight) - 0.50 * em, 0.03 * em);
    compare(pair, "chevron stem width", stroke - stemWidth(label, em), 0.5);

    const disclosure = pair.matches("summary");
    const last = disclosure ? {} : lastLetter(label, em);
    const lineBaseline = baseline(label) + (last.lineOffset ?? 0);
    if (turned) {
      compare(pair, "rotated chevron centre", centre(ink) - (lineBaseline - 0.25 * em));
    } else {
      compare(pair, "chevron baseline", ink.bottom - lineBaseline);
    }
    if (!disclosure) compare(pair, "chevron ink gap", ink.left - last.right - 0.40 * em, 0.03 * em);
  }

  function measureButton(button, box) {
    const compact = button.matches(".bar-cta") && matchMedia("(min-width: 820px)").matches;
    const style = getComputedStyle(button);
    const token = compact ? "--btn-compact-height" : "--btn-height";
    compare(button, token, box.height - parseFloat(style.getPropertyValue(token)), 0);
    if (compact) {
      const hit = parseFloat(style.getPropertyValue("--hit"));
      const x = (box.left + box.right) / 2;
      const clicks = [-1, 1].map(side => document.elementFromPoint(x, centre(box) + side * (hit / 2 - 0.25)));
      if (!clicks.every(element => button.contains(element))) {
        failures.push({ selector: selector(button), check: "compact button hit area", offset: "—" });
      }
    }
  }

  for (const pair of document.querySelectorAll(components)) {
    if (scope && !pair.closest(scope)) continue;
    if (!pair.checkVisibility({ visibilityProperty: true })) continue;
    if (pair.matches("option") && !pair.closest("select:open")) continue;

    const labels = [...pair.querySelectorAll(":scope > .symbol-text:not(.command-prompt)")];
    const symbols = [...pair.querySelectorAll(":scope > :is(.symbol, .command-prompt), :scope > .report-card-controls .symbol")];
    const chevron = pair.querySelector(":scope > .chevron, :scope > .symbol-text .chevron");
    const onlySymbol = pair.matches(symbolOnly);
    const measuredEvidence = pair.matches(".finding-evidence dd[data-provenance=measured]");
    if (!pair.matches(".symbol-label") || (!onlySymbol && !labels.length)
      || (measuredEvidence && labels.length !== 2)
      || (pair.matches(chevronLabels) && !chevron)
      || (!pair.matches(textOnly) && !symbols.length && !chevron)) {
      failures.push({ selector: selector(pair), check: "missing primitive, label or symbol", offset: "—" });
      continue;
    }

    const capCentres = labels.map(capCentre);
    const box = pair.getBoundingClientRect();
    const { borderTopWidth, borderBottomWidth } = getComputedStyle(pair);
    const paddingCentre = centre(box) + (parseFloat(borderTopWidth) - parseFloat(borderBottomWidth)) / 2;
    for (const symbol of symbols) {
      compare(pair, selector(symbol), inkCentre(symbol) - (capCentres[0] ?? paddingCentre));
    }
    if (chevron) measureChevron(pair, chevron, labels[0]);
    if (pair.matches(".btn")) measureButton(pair, box);
    if (pair.matches(centredLabels)) {
      for (const cap of capCentres) compare(pair, "padding box", cap - paddingCentre);
    }
    if (pair.matches(".menu-button")) {
      const bar = pair.closest(".bar-in");
      const barBox = bar.getBoundingClientRect();
      const barStyle = getComputedStyle(bar);
      const hit = parseFloat(barStyle.getPropertyValue("--hit"));
      compare(pair, "hit target width", box.width - hit);
      compare(pair, "hit target height", box.height - hit);
      compare(pair, "top bar centre", centre(box) - centre(barBox));
      compare(pair, "right gutter", box.right - (barBox.right - parseFloat(barStyle.paddingInlineEnd)));
      const icon = pair.querySelector(".menu-icon")?.getBoundingClientRect();
      const iconSize = parseFloat(getComputedStyle(document.body).fontSize);
      compare(pair, "menu icon width", icon?.width - iconSize);
      compare(pair, "menu icon height", icon?.height - iconSize);
      const panel = pair.parentElement.querySelector(".bar-links");
      if (panel?.checkVisibility({ visibilityProperty: true })) {
        const panelBox = panel.getBoundingClientRect();
        compare(panel, "panel left edge", panelBox.left - barBox.left);
        compare(panel, "panel right edge", panelBox.right - barBox.right);
        compare(panel, "panel top edge", panelBox.top - barBox.bottom);
      }
    }
    for (const cap of capCentres.slice(1)) compare(pair, "label", cap - capCentres[0]);
    if (pair.matches(".finding-evidence dd")) {
      compare(pair, "evidence term", capCentres[0] - capCentre(pair.previousElementSibling));
    }
    if (pair.matches(".command-line code > span") && pair.previousElementSibling) {
      const preceding = pair.previousElementSibling.getBoundingClientRect();
      compare(pair, "command line gap", Math.min(0, box.top - preceding.bottom - 8));
    }
  }

  if (!scope) {
    const costTiles = [...document.querySelectorAll("#costs [data-cost-tile]")];
    const [firstTile] = costTiles;
    for (const tile of costTiles) {
      const label = tile.querySelector(".tile-label");
      const amount = tile.querySelector(".figure-num");
      const offset = amount?.getBoundingClientRect().left - label?.getBoundingClientRect().left;
      compare(tile, "cost figure column", offset);
      if (tile !== firstTile && matchMedia("(min-width: 640px)").matches) {
        compare(tile, "cost label row", capCentre(label) - capCentre(firstTile.querySelector(".tile-label")));
        compare(tile, "cost figure row", capCentre(amount) - capCentre(firstTile.querySelector(".figure-num")));
      }
    }
  }
  return { failures, count, maximum };
}

async function checkPage(page, route, width, origin, measure) {
  const report = route.startsWith("/demo/");
  const response = await page.goto(origin + route);
  if (!response?.ok()) throw new Error("Page did not load");
  await page.evaluate(() => document.fonts.ready);
  const languageName = route.startsWith("/de/") ? "English" : "Deutsch";
  const languageLink = page.getByRole("link", { name: languageName, exact: true });
  if (!report) await page.locator("footer a.language").and(languageLink).waitFor();
  await measure();

  const copy = page.locator("[data-copy]");
  for (const button of await copy.all()) {
    await button.click();
    await page.locator("[data-copy].done").waitFor();
    await measure(".copy.done");
  }

  const menu = page.locator(".menu-button");
  if (width < 820) {
    const open = report ? ".bar-menu[open]" : ".bar[data-open]";
    const panel = page.locator(report ? ".bar-menu .bar-links" : ".bar-links");
    const links = panel.locator("a");
    await links.first().waitFor({ state: "hidden" });
    await menu.press("Enter");
    await links.first().waitFor();
    if (!report) await panel.locator("a.language").and(languageLink).waitFor();
    await measure(open);
    if (report) {
      const costs = panel.locator('a[href="#costs-title"]');
      await costs.press("Enter");
      assert.equal(new URL(page.url()).hash, "#costs-title");
      assert.equal(await costs.evaluate(link => getComputedStyle(link).fontWeight), "600");
      assert.equal(await links.first().evaluate(link => getComputedStyle(link).fontWeight), "400");
      await menu.press("Space");
    } else {
      await page.keyboard.press("Escape");
    }
    await links.first().waitFor({ state: "hidden" });
  } else {
    await menu.waitFor({ state: "hidden" });
    if (!report) await page.locator(".bar-links a.language").waitFor({ state: "hidden" });
  }

  if (await page.locator("details:not(.bar-menu)").count()) {
    await page.locator("details:not(.bar-menu)").evaluateAll(details => details.forEach(detail => { detail.open = true; }));
    await measure("details[open]");
  }

  if (report) {
    const category = page.locator("#f-category");
    await category.click();
    await category.locator("option:checked > .symbol").waitFor();
    await measure("#f-category option");
    const nextOption = category.locator("option").nth(1);
    const nextValue = await nextOption.getAttribute("value");
    await nextOption.click();
    await category.locator(`option[value="${nextValue}"]:checked`).waitFor({ state: "attached" });
    await measure("#f-category > button");
  }
}

const tolerance = 0.75;
const failures = [];
let maximum = 0;
let count = 0;
let views = 0;
await withSite(async ({ browser, origin, routes }) => {
  for (const width of widths) {
    for (const theme of ["light", "dark"]) {
      const context = await localContext(browser, origin, width, theme);
      await context.grantPermissions(["clipboard-write"], { origin });
      const page = await context.newPage();
      page.setDefaultTimeout(3000);
      for (const route of routes) {
        const view = { page: route, width, theme };
        views += 1;
        try {
          await checkPage(page, route, width, origin, async scope => {
            const result = await page.evaluate(measureInPage, {
              scope, components, centredLabels, symbolOnly, textOnly, chevronLabels, tolerance,
            });
            failures.push(...result.failures.map(failure => ({ ...view, ...failure })));
            count += result.count;
            maximum = Math.max(maximum, result.maximum);
          });
        } catch (error) {
          failures.push({ ...view, selector: "page", check: error.message.split("\n").slice(0, 2).join(" "), offset: "—" });
        }
      }
      await context.close();
    }
  }
});

if (failures.length) {
  console.table(failures);
  process.exitCode = 1;
} else {
  console.log(`${views} page views, ${count} alignment measurements. Maximum offset ${maximum.toFixed(2)} px (limit ${tolerance} px).`);
}
