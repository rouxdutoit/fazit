// SPDX-License-Identifier: AGPL-3.0-or-later
import { readFile } from "node:fs/promises";
import { localContext, widths, withSite } from "./check_browser.mjs";

const design = await readFile(new URL("../DESIGN.md", import.meta.url), "utf8");
const relations = new Map(Array.from(
  design.matchAll(/^\| ([^|]+) \| `--([a-z-]+)` \| (\d+) px \| (\d+) px \| (\d+) px \|$/gm),
  ([, name, token, ...gaps]) => [token.replace(/^rhythm-/, ""), { name, expected: gaps.map(Number) }],
));
const scale = [4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 96];
// Allow for layout in steps of 1/64 of a CSS pixel.
const tolerance = 0.02;
if (relations.size !== 13 || [...relations.values()].some(({ expected }) => expected.some(gap => !scale.includes(gap)))) {
  throw new Error("DESIGN.md must give one spacing-scale value per width for each of the 13 relations.");
}

function measureInPage(filtered) {
  const measurements = [];
  const main = document.querySelector("main");
  const columns = matchMedia("(min-width: 880px)").matches;
  const visual = "figure, ul, ol, dl, table, .finding, .command, .summary-costs, .table-scroll, .cost-bars, .sec-body .note";
  const flows = [
    ".hero", ".page-intro", ".center-page > div", ".sec-body", ".subsection",
    ".preview-blockers", ".legal-part",
    ".scope-requirements", ".cost-bars", ".cost-chart-row", ".cost-notes", ".areas", ".finding",
    "[data-subsection]", "details", ".finding-missing", "#costs-missing", ".timeline",
  ].join(", ");

  const visible = el => !el.matches(".sr-only, .copy-message:empty") && el.checkVisibility({ visibilityProperty: true });
  const box = el => el.getBoundingClientRect();
  const link = el => el.matches("a.more, .flow-links, .summary-links, p:has(> a.more:only-child)");
  const firstLink = el => el.matches("a.more") ? el : el.querySelector(":scope > a.more");
  const paragraph = el => el.matches("p:not(.tile-title, .tile-label, .eyebrow)") && !link(el);

  function selector(element) {
    if (element.id) return `#${element.id}`;
    const classes = [...element.classList].filter(name => !name.startsWith("symbol-"));
    const key = element.getAttribute("data-section") ?? element.getAttribute("data-summary")
      ?? element.getAttribute("data-subsection") ?? element.getAttribute("aria-labelledby")
      ?? element.getAttribute("href");
    return `${element.localName}${classes.map(name => "." + name).join("")}${key ? ` (${key})` : ""}`;
  }

  function record(relation, first, second, gap = box(second).top - box(first).bottom, edge = "") {
    const scope = first.closest("[id], [data-section], [data-summary], section[aria-labelledby]");
    const pair = `${scope ? `${selector(scope)} / ` : ""}${selector(first)} → ${selector(second)}`;
    measurements.push({ relation, gap, pair: edge ? `${pair} (${edge})` : pair });
  }

  function measureStartAndEnd() {
    const heading = main.querySelector("h1");
    record("page-heading", main, heading, box(heading).top - box(main).top);
    const last = [...main.children].filter(visible).at(-1);
    record("section-gap", last, document.querySelector("footer"), undefined, "above footer");
  }

  function measureDivider(previous, section, firstItems, pseudo = false) {
    const style = getComputedStyle(section, pseudo ? "::before" : null);
    const size = pseudo ? parseFloat(style.height) : parseFloat(style.borderTopWidth);
    const offset = pseudo ? parseFloat(style.top) : 0;
    const hasRule = size > 0 && (!pseudo || style.content !== "none" && style.display !== "none");
    const top = hasRule ? box(section).top + offset : NaN;
    record("section-gap", previous, section, top - box(previous).bottom, "above divider");
    for (const first of firstItems) {
      record("section-gap", section, first, box(first).top - (top + size), "below divider");
    }
  }

  function measureLegalDividers(intro, layout) {
    const summary = layout.matches(".has-summary");
    const [first, article] = layout.children;
    measureDivider(intro, layout, summary && columns ? [first, article] : [first]);
    if (summary && !columns) measureDivider(first, article, [article.firstElementChild]);
    for (const part of layout.querySelectorAll(".legal-part + .legal-part")) {
      measureDivider(part.previousElementSibling, part, [part.firstElementChild]);
    }
  }

  function measureDividers() {
    const sections = [...main.children].filter(visible);
    for (const [index, section] of sections.entries()) {
      if (!index) continue;
      const previous = sections[index - 1];
      if (section.matches(".legal-layout")) {
        measureLegalDividers(previous, section);
      } else if (section.matches("section")) {
        const grid = section.querySelector(":scope > .sec") ?? section;
        const items = [...grid.children].filter(visible);
        measureDivider(previous, grid, columns ? items : items.slice(0, 1), true);
      }
    }
  }

  function measureCommand(block) {
    const code = block.querySelector("code");
    const symbol = block.querySelector(".copy > .symbol");
    const outer = box(block);
    const inner = box(code);
    record("card-padding", block, code, inner.top - outer.top, "top");
    record("card-padding", block, code, outer.bottom - inner.bottom, "bottom");
    record("card-padding", block, code, inner.left - outer.left, "left");
    record("card-padding", block, symbol ?? block, outer.right - symbol?.getBoundingClientRect().right, "right to copy symbol");
  }

  function measurePair(parent, previous, next) {
    if (previous.matches(".eyebrow") || parent.matches(".cost-chart-heading")) return;
    if (previous.matches(".sec-label, .preview-title")) {
      if (!columns) record("section-heading", previous, next);
      return;
    }
    if (previous.matches("h1, .legal-part > h2")) {
      record("section-heading", previous, next);
      return;
    }
    if (next.matches("figcaption, .table-note, .cost-known-blocks, .cost-chart-values")
      || previous.matches(".command-label, .cost-origin, .legend")) {
      record("caption", previous, next.matches("figcaption") ? firstLink(next) ?? next : next);
      if (link(next)) record("visual-link", previous, firstLink(next));
      return;
    }
    if (previous.matches("h3, h4, summary, .timeline-name, .finding-head, .cost-chart-heading")) {
      if (!previous.matches(".finding-area") && !parent.matches(".rows > div")) {
        record("subheading", previous, next);
      }
      return;
    }
    if (link(next) && !parent.matches(".flow-links, .summary-links, .finding-target")) {
      const lastVisual = previous.matches(".summary-costs, .subsection:has(> .tiles:last-child)")
        ? previous.lastElementChild : previous;
      if (lastVisual.matches(visual)) record("visual-link", lastVisual, firstLink(next));
      else if (paragraph(previous)) record("text-link", previous, firstLink(next));
      return;
    }
    if (previous.matches(".hero") && next.matches("figure")) {
      record("lede-visual", previous.lastElementChild, next);
      return;
    }
    if (paragraph(previous) && next.matches(visual)) {
      if (!parent.matches(".tiles li")) record("lede-visual", previous, next);
      return;
    }
    if (paragraph(previous) && paragraph(next)) {
      record("paragraph", previous, next);
      return;
    }
    if (parent.matches(flows)) record("group", previous, next);
  }

  function measureCaption(caption) {
    // Responsive tables keep a clipped header for assistive technology.
    const rows = [...caption.parentElement.rows].filter(row =>
      visible(row) && getComputedStyle(row.parentElement).position !== "absolute");
    const after = getComputedStyle(caption).captionSide === "bottom";
    const row = after ? rows.at(-1) : rows[0];
    if (row) record("caption", ...(after ? [row, caption] : [caption, row]));
  }

  function measureLinkRow(links) {
    for (const [index, left] of links.entries()) {
      const right = links[index + 1];
      if (right && box(right).top < box(left).bottom && box(right).left > box(left).left) {
        record("inline-links", left, right, box(right).left - box(left).right);
      }
    }
  }

  function measureCards(cards) {
    const rows = new Map();
    for (const card of cards) {
      const top = box(card).top;
      if (!rows.has(top)) rows.set(top, []);
      rows.get(top).push(card);
    }
    const ordered = [...rows.values()];
    for (const [index, row] of ordered.entries()) {
      for (const [column, card] of row.entries()) {
        const next = row[column + 1];
        if (next) record("card", card, next, box(next).left - box(card).right);
        for (const below of ordered[index + 1] ?? []) {
          if (box(below).left < box(card).right && box(below).right > box(card).left) record("card", card, below);
        }
      }
    }
  }

  if (filtered) {
    record("group", main.querySelector(".filters"), main.querySelector(".areas-empty"));
    return measurements;
  }

  measureStartAndEnd();
  measureDividers();
  for (const parent of [main, ...main.querySelectorAll("*")]) {
    const children = [...parent.children].filter(visible);
    if (parent.matches(".command-line")) measureCommand(parent);
    if (parent.matches(".tiles, .status-group, .finding-cards")) {
      measureCards(children.filter(el => el.matches("li, .finding")));
    }
    if (parent.matches(".flow-links, .summary-links")) measureLinkRow(children.filter(link));
    if (parent.matches("caption") && visible(parent)) measureCaption(parent);
    if (parent.matches(".finding-target")) {
      const anchor = children.find(link);
      const prose = anchor?.previousElementSibling;
      if (prose) record("text-link", prose, anchor);
    }
    for (const [index, next] of children.entries()) {
      if (index) measurePair(parent, children[index - 1], next);
    }
  }
  return measurements;
}

async function showEmptyResults(page) {
  const blocker = page.locator("#f-status-blocker");
  if (await blocker.isDisabled()) return false;
  const represented = await page.locator('.finding[data-status="blocker"]').evaluateAll(cards =>
    cards.map(card => card.dataset.category));
  const category = page.locator("#f-category");
  const options = await category.locator("option:not(:checked)").evaluateAll(items => items.map(item => item.value));
  const empty = options.find(value => !represented.includes(value));
  if (!empty) return false;
  await page.locator("label:has(#f-status-blocker)").click();
  await category.selectOption(empty);
  await page.locator(".areas-empty").waitFor();
  return true;
}

async function checkSpacing({ browser, origin, routes }) {
  const buckets = new Map(widths.map(width => [width, new Map([...relations.keys()].map(key => [key, []]))]));
  const errors = [];
  let views = 0;
  let expanded = 0;
  let filtered = 0;
  for (const width of widths) {
    for (const theme of ["light", "dark"]) {
      const context = await localContext(browser, origin, width, theme);
      const page = await context.newPage();
      for (const route of routes) {
        const collect = async state => {
          for (const { relation, ...result } of await page.evaluate(measureInPage, state === "filtered")) {
            const bucket = buckets.get(width).get(relation);
            if (!bucket) throw new Error(`Missing rhythm definition for ${relation}`);
            bucket.push({ ...result, page: route, theme, state });
          }
        };
        try {
          const response = await page.goto(origin + route);
          if (!response?.ok()) throw new Error("Page did not load");
          await page.evaluate(() => document.fonts.ready);
          await collect("initial");
          views += 1;
          const details = page.locator("main details:not([open])");
          if (await details.count()) {
            await details.evaluateAll(items => items.forEach(item => { item.open = true; }));
            await collect("expanded");
            expanded += 1;
          }
          if (route.startsWith("/demo/") && await showEmptyResults(page)) {
            await collect("filtered");
            filtered += 1;
          }
        } catch (error) {
          errors.push({ page: route, width, view: theme, error: error.message });
        }
      }
      await context.close();
    }
  }
  const { rows, offenders, count } = summarise(buckets);
  console.table(rows);
  console.log(`${views} page views, ${expanded} expanded views, ${filtered} empty filter views, ${count} spacing measurements (px).`);
  if (offenders.length) console.table(offenders);
  if (errors.length) console.table(errors);
  if (errors.length || rows.some(row => row.offenders)) process.exitCode = 1;
}

const onScale = gap => scale.find(value => Math.abs(gap - value) <= tolerance);
const display = gap => gap === null ? "missing box" : onScale(gap) ?? Number(gap.toFixed(2));
const widthBand = width => width < 768 ? 0 : width < 1080 ? 1 : 2;

function summarise(buckets) {
  const rows = [];
  const offenders = new Map();
  let count = 0;
  for (const [key, { name, expected }] of relations) {
    for (const [width, byRelation] of buckets) {
      const samples = byRelation.get(key);
      count += samples.length;
      const target = expected[widthBand(width)];
      const home = theme => samples.find(sample =>
        sample.page === "/" && sample.theme === theme && sample.state === "initial")?.gap;
      const homeGaps = { light: home("light"), dark: home("dark") };
      const values = [...new Set(samples.map(({ gap }) => display(gap)))].sort((a, b) => a - b);
      const invalid = samples.filter(({ gap, theme }) => gap === null || onScale(gap) !== target
        || (key === "section-gap" && (!Number.isFinite(homeGaps[theme]) || Math.abs(gap - homeGaps[theme]) > tolerance)));
      rows.push({ relation: name, width, expected: target, "values found": values.join(", ") || "—", offenders: invalid.length || (samples.length ? 0 : "no measurements") });
      for (const { page, pair, theme, state, gap } of invalid) {
        const actual = display(gap);
        const id = JSON.stringify([key, width, page, pair, actual]);
        if (!offenders.has(id)) {
          offenders.set(id, { relation: name, width, page, pair, gap: actual, expected: target, views: new Set(), hits: 0 });
        }
        const offender = offenders.get(id);
        offender.views.add(`${theme} ${state}`);
        offender.hits += 1;
      }
    }
  }
  return { rows, count, offenders: [...offenders.values()].map(({ views, ...row }) => ({ ...row, views: [...views].join(", ") })) };
}

await withSite(checkSpacing);
