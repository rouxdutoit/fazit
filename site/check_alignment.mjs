// SPDX-License-Identifier: AGPL-3.0-or-later
import { readFile } from "node:fs/promises";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const modules = process.env.PLAYWRIGHT_DIR ?? "/home/roux/.local/share/playwright-1.62.1/node_modules/";
const { chromium } = createRequire(resolve(modules, "check_alignment.cjs"))("playwright");
const site = fileURLToPath(new URL(".", import.meta.url));
const routes = [
  ...["/", "/start/", "/coverage/", "/about/", "/security/", "/pilots/",
    "/integrators/", "/roadmap/", "/privacy/", "/impressum/", "/404.html"].flatMap(route => [route, "/de" + route]),
  "/demo/en/", "/demo/de/",
];
const types = {
  ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp",
};

async function serve() {
  const server = createServer(async (request, response) => {
    const { pathname } = new URL(request.url, "http://127.0.0.1");
    const file = resolve(site, "." + (pathname.endsWith("/") ? pathname + "index.html" : pathname));
    const type = types[extname(file)];
    try {
      if (!file.startsWith(resolve(site) + sep) || !type) throw new Error("Outside the site");
      const content = await readFile(file);
      response.writeHead(200, { "Content-Type": type }).end(content);
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise((ready, fail) => server.listen(0, "127.0.0.1", ready).once("error", fail));
  return server;
}

const capsules = ".btn, .language, .badge, .segmented label, .category-filter > button, .bar-menu > summary";
const menuItems = ".bar-links a, .category-filter option";
const centredLabels = `${capsules}, ${menuItems}`;
const symbolOnly = ".copy, .menu-button, .foot-mail, .tile-arrow, .report-card-control, .cost-segment.is-unknown";
const textOnly = ".language, .badge:not(.status), .bar-links a:not(.btn), .segmented label:has(#f-status-all), .finding-evidence dd";
// Keep the component selectors so dropping the primitive from known markup fails the check.
const components = [
  centredLabels, symbolOnly, ".symbol-label", ".more", "summary", ".status",
  ".cov-cell", ".coverage-key", ".safeguards li", ".tile-link h3", ":is(h3, h4):has(> .tile-icon)",
  ".timeline-name", ".report-card-bar", ".cost-bars .legend li", ".command-line code > span",
  ".status-summary dt", ".finding-evidence dd", ".privacy-facts h3", ".flow-links > a",
].join(", ");

function measureInPage({ scope, components, centredLabels, symbolOnly, textOnly, tolerance }) {
  const canvas = document.createElement("canvas").getContext("2d");
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

  function metrics(element, text) {
    const style = getComputedStyle(element);
    canvas.font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
    return canvas.measureText(text);
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

  function compare(element, check, offset) {
    count += 1;
    if (Number.isFinite(offset)) maximum = Math.max(maximum, Math.abs(offset));
    if (!Number.isFinite(offset) || Math.abs(offset) > tolerance) {
      failures.push({ selector: selector(element), check, offset: Number.isFinite(offset) ? offset.toFixed(2) : "missing box" });
    }
  }

  for (const pair of document.querySelectorAll(components)) {
    if (scope && !pair.closest(scope)) continue;
    if (!pair.checkVisibility({ visibilityProperty: true })) continue;
    if (pair.matches("option") && !pair.closest("select:open")) continue;

    const labels = [...pair.querySelectorAll(":scope > .symbol-text:not(.command-prompt)")];
    const symbols = [...pair.querySelectorAll(":scope > :is(.symbol, .command-prompt), :scope > .report-card-controls .symbol")];
    const onlySymbol = pair.matches(symbolOnly);
    const measuredEvidence = pair.matches(".finding-evidence dd[data-provenance=measured]");
    if (!pair.matches(".symbol-label") || (!onlySymbol && !labels.length)
      || (measuredEvidence && labels.length !== 2)
      || (!pair.matches(textOnly) && !symbols.length)) {
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
    if (pair.matches(centredLabels)) {
      for (const cap of capCentres) compare(pair, "padding box", cap - paddingCentre);
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
  const response = await page.goto(origin + route);
  if (!response?.ok()) throw new Error("Page did not load");
  await page.evaluate(() => document.fonts.ready);
  await measure();

  const copy = page.locator("[data-copy]");
  for (const button of await copy.all()) {
    await button.click();
    await page.locator("[data-copy].done").waitFor();
    await measure(".copy.done");
  }

  if (!route.startsWith("/demo/") && width < 820) {
    await page.locator(".menu-button").click();
    await page.locator(".bar[data-open] .bar-links a").first().waitFor();
    await measure(".bar[data-open]");
    await page.keyboard.press("Escape");
  }

  if (route.startsWith("/demo/") && width < 640) {
    await page.locator(".bar-menu > summary").click();
    await page.locator(".bar-menu[open] .bar-links a").first().waitFor();
    await measure(".bar-menu[open]");
    await page.locator(".bar-menu > summary").click();
  }

  if (await page.locator("details:not(.bar-menu)").count()) {
    await page.locator("details:not(.bar-menu)").evaluateAll(details => details.forEach(detail => { detail.open = true; }));
    await measure("details[open]");
  }

  if (route.startsWith("/demo/")) {
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

const server = await serve();
const origin = `http://127.0.0.1:${server.address().port}`;
const tolerance = 0.75;
const failures = [];
let maximum = 0;
let count = 0;
let views = 0;
let browser;
try {
  browser = await chromium.launch();
  for (const width of [360, 768, 1280]) {
    for (const theme of ["light", "dark"]) {
      const context = await browser.newContext({
        viewport: { width, height: 900 }, colorScheme: theme, reducedMotion: "reduce",
      });
      await context.grantPermissions(["clipboard-write"], { origin });
      await context.route("**/*", route =>
        new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
      const page = await context.newPage();
      page.setDefaultTimeout(3000);
      for (const route of routes) {
        const view = { page: route, width, theme };
        views += 1;
        try {
          await checkPage(page, route, width, origin, async scope => {
            const result = await page.evaluate(measureInPage, {
              scope, components, centredLabels, symbolOnly, textOnly, tolerance,
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
} finally {
  await browser?.close();
  await new Promise(done => server.close(done));
}

if (failures.length) {
  console.table(failures);
  process.exitCode = 1;
} else {
  console.log(`${views} page views, ${count} alignment measurements. Maximum offset ${maximum.toFixed(2)} px (limit ${tolerance} px).`);
}
