// SPDX-License-Identifier: AGPL-3.0-or-later
import assert from "node:assert/strict";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { widths, withSite } from "../../site/check_browser.mjs";

const [siteOrigin, ...extraReports] = process.argv.slice(2);
const site = new URL("../../site/", import.meta.url);

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

const reports = ["en", "de"].map(lang => new URL(`demo/${lang}/index.html`, site).href)
  .concat(extraReports.map(path => pathToFileURL(resolve(path)).href));

async function load(page, url, webkit) {
  const response = await page.goto(url);
  if (!url.startsWith("file:")) assert(response?.ok(), url);
  await page.evaluate(emulateClassic => {
    if (emulateClassic) {
      // Headless WebKit needs a classic gutter to expose scrollbars to the size check.
      const style = document.createElement("style");
      style.textContent = ":where(*)::-webkit-scrollbar { width: 15px; height: 15px; }";
      document.head.append(style);
    }
    return document.fonts.ready;
  }, webkit);
}

async function checkScrollbars({ browser, origin, routes }) {
  const webkit = browser.browserType().name() === "webkit";
  for (const width of widths) {
    for (const colorScheme of ["light", "dark"]) {
      const viewport = { width, height: 800 };
      const reducedMotion = "reduce";
      const website = await browser.newPage({ viewport, colorScheme, reducedMotion });
      // WebKit's offline flag also rejects file navigation. Block network requests directly.
      const report = await browser.newPage({ viewport, colorScheme, reducedMotion, offline: !webkit, javaScriptEnabled: false });
      const networkRequests = [];
      await report.route(/^https?:\/\//, route => {
        networkRequests.push(route.request().url());
        return route.abort("internetdisconnected");
      });
      await website.route("**/*", route => route.request().url().startsWith(origin + "/")
        ? route.continue() : route.abort());
      try {
        for (const route of routes) {
          await load(website, new URL(route, origin).href, webkit);
          await check(website);
        }
        for (const url of reports) {
          await load(report, url, webkit);
          await check(report);
          await report.locator("details").evaluateAll(details => {
            for (const disclosure of details) disclosure.open = true;
          });
          await check(report);
        }
        assert.deepEqual(networkRequests, [], "Offline reports made network requests");
        console.log(`${width} px, ${colorScheme}: ${routes.length} site pages and ${reports.length} offline reports passed`);
      } finally {
        await website.close();
        await report.close();
      }
    }
  }
}

await withSite(checkScrollbars, { origin: siteOrigin && new URL(siteOrigin).origin, classicScrollbars: true });
