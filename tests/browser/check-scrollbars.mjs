// SPDX-License-Identifier: AGPL-3.0-or-later
import assert from "node:assert/strict";
import { readdir } from "node:fs/promises";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const [siteOrigin, ...extraReports] = process.argv.slice(2);
assert(siteOrigin, "Usage: node tests/browser/check-scrollbars.mjs <local site origin> [report.html ...]");
const origin = new URL(siteOrigin).origin;
const site = new URL("../../site/", import.meta.url);
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE ?? "playwright");

async function check(page) {
  const problems = await page.evaluate(() => {
    const { documentElement: root, body } = document;
    const probe = document.createElement("div");
    probe.style.cssText = "position:fixed;width:40px;height:40px;overflow:scroll";
    body.append(probe);
    const classicScrollbars = probe.offsetWidth - probe.clientWidth > 0;
    probe.remove();
    const problems = [];
    if (!classicScrollbars) problems.push("Browser is hiding classic scrollbars");
    if (root.scrollWidth > root.clientWidth) problems.push("Page overflows horizontally");
    if (innerWidth > root.clientWidth || innerHeight > root.clientHeight) {
      problems.push("Viewport scrollbar");
    }
    for (const element of [body, ...body.querySelectorAll("*")]) {
      if (!(element instanceof HTMLElement) || !element.offsetWidth || !element.offsetHeight) continue;
      const css = getComputedStyle(element);
      if (css.visibility !== "visible") continue;
      const vertical = element.offsetWidth - element.clientWidth -
        parseFloat(css.borderLeftWidth) - parseFloat(css.borderRightWidth);
      const horizontal = element.offsetHeight - element.clientHeight -
        parseFloat(css.borderTopWidth) - parseFloat(css.borderBottomWidth);
      if ((vertical > 1 && (css.overflowY === "scroll" ||
        css.overflowY === "auto" && element.scrollHeight > element.clientHeight)) ||
        (horizontal > 1 && (css.overflowX === "scroll" ||
          css.overflowX === "auto" && element.scrollWidth > element.clientWidth))) {
        problems.push(element.tagName + (element.className ? "." + element.className : ""));
      }
    }
    return problems;
  });
  assert.deepEqual(problems, [], page.url() + " at " + page.viewportSize().width + " px");
}

const routes = (await readdir(fileURLToPath(site), { recursive: true }))
  .filter(path => path.endsWith(".html")).sort();
const reports = ["en", "de"].map(lang => new URL(`demo/${lang}/index.html`, site).href)
  .concat(extraReports.map(path => pathToFileURL(resolve(path)).href));
const browser = await chromium.launch({
  ignoreDefaultArgs: ["--hide-scrollbars"],
  args: ["--disable-features=OverlayScrollbar,FluentOverlayScrollbar"],
});
try {
  for (const width of [360, 768, 1280]) {
    for (const colorScheme of ["light", "dark"]) {
      const viewport = { width, height: 800 };
      const website = await browser.newPage({ viewport, colorScheme });
      const report = await browser.newPage({ viewport, colorScheme, offline: true, javaScriptEnabled: false });
      await website.route("**/*", route => route.request().url().startsWith(origin + "/")
        ? route.continue() : route.abort());
      try {
        for (const path of routes) {
          const response = await website.goto(new URL(path, origin).href);
          assert(response?.ok(), path);
          await website.evaluate(() => document.fonts.ready);
          await check(website);
        }
        for (const url of reports) {
          await report.goto(url);
          await report.evaluate(() => document.fonts.ready);
          await check(report);
          await report.locator("details").evaluateAll(details => {
            for (const disclosure of details) disclosure.open = true;
          });
          await check(report);
        }
        console.log(`${width} px, ${colorScheme}: ${routes.length} site pages and ${reports.length} offline reports passed`);
      } finally {
        await website.close();
        await report.close();
      }
    }
  }
} finally {
  await browser.close();
}
