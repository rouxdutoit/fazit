// SPDX-License-Identifier: AGPL-3.0-or-later
import assert from "node:assert/strict";
import { localContext } from "./check_browser.mjs";

async function underline(label, settle) {
  return label.evaluate(async (element, settle) => {
    const style = getComputedStyle(element);
    const size = style.backgroundSize;
    const transition = element.getAnimations().find(animation => animation.transitionProperty === "background-size");
    if (settle) await transition?.finished;
    const properties = style.transitionProperty.split(", ");
    const durations = style.transitionDuration.split(", ");
    const index = Math.max(properties.lastIndexOf("background-size"), properties.lastIndexOf("all"));
    return {
      size: settle ? style.backgroundSize : size,
      image: style.backgroundImage,
      colour: style.color,
      position: style.backgroundPositionX,
      duration: index < 0 ? 0 : parseFloat(durations[index % durations.length]),
      ease: style.transitionTimingFunction,
      decoration: style.textDecorationLine,
    };
  }, settle);
}

async function checkContentLink(link, motion, { inline = false, hit = link } = {}) {
  const page = link.page();
  const label = inline ? link : link.locator(".link-text");
  const baseSize = inline ? "0% 1px, 100% 1px" : "0% 1px";
  const activeSize = inline ? "100% 1px, 100% 1px" : "100% 1px";
  const name = (await label.textContent()).trim();
  const initial = await underline(label, false);
  assert.equal(initial.size, baseSize, `${name}: resting underline`);
  assert.equal(initial.decoration, "none", `${name}: screen underline uses a background`);
  assert.equal(initial.image.match(/linear-gradient\(/g)?.length, inline ? 2 : 1, `${name}: underline layers`);
  assert(initial.position.split(", ").every(position => position === "0%"), `${name}: underline starts at the left`);
  assert.equal(initial.duration, motion ? 0.25 : 0, `${name}: underline duration`);
  if (motion) assert(initial.ease.includes("cubic-bezier(0.32, 0.72, 0, 1)"), `${name}: site easing`);
  if (!inline) {
    const separatesChevron = await label.evaluate(element => {
      const tail = element.nextElementSibling;
      const lastLine = [...element.getClientRects()].at(-1);
      return tail?.matches(".chevron-tail") && tail.getBoundingClientRect().left >= lastLine.right - 0.1;
    });
    assert(separatesChevron, `${name}: underline ends before the chevron`);
  }

  await page.keyboard.press("Tab");
  await link.focus();
  assert(await link.evaluate(element => element.matches(":focus-visible")), `${name}: keyboard focus`);
  assert.equal((await underline(label, motion)).size, activeSize, `${name}: focus underline`);
  await link.blur();
  assert.equal((await underline(label, motion)).size, baseSize, `${name}: retraction after blur`);

  await hit.hover();
  assert(await link.evaluate(element => element.matches(":hover")), `${name}: hovered link`);
  const hovered = await underline(label, motion);
  assert.equal(hovered.size, activeSize, `${name}: hover underline`);
  assert(hovered.image.includes(hovered.colour), `${name}: underline in the link colour`);
  if (await link.evaluate(element => element.matches("a.more:not(.area-link)"))) {
    assert.equal(hovered.colour, initial.colour, `${name}: standalone link keeps the text colour`);
  }
  await page.mouse.move(0, 0);
  assert.equal((await underline(label, motion)).size, baseSize, `${name}: retraction after hover`);
}

async function checkExcludedLink(link, name) {
  await link.hover();
  const unchanged = await link.evaluate(element =>
    element.matches(":hover") && [element, ...element.querySelectorAll(".symbol-text, .link-text")].every(label => {
      const style = getComputedStyle(label);
      return style.backgroundImage === "none" && style.textDecorationLine === "none";
    }));
  assert(unchanged, `${name}: hover keeps the link plain`);
}

async function checkPrint(link, inline = false) {
  const page = link.page();
  await page.emulateMedia({ media: "print" });
  await link.focus();
  const label = inline ? link : link.locator(".link-text");
  const print = await underline(label, false);
  assert.equal(print.image, "none", "Print omits the animated underline");
  assert.equal(print.decoration, inline ? "underline" : "none", "Print keeps the resting decoration");
  await page.emulateMedia({ media: "screen" });
}

export async function checkLinkUnderlines({ browser, origin }) {
  for (const motion of [true, false]) {
    const options = { reducedMotion: motion ? "no-preference" : "reduce" };
    const website = await localContext(browser, origin, 1280, "light", options);
    const report = await localContext(browser, origin, 1280, "light", { ...options, javaScriptEnabled: false });
    try {
      const page = await website.newPage();
      const demo = await report.newPage();
      for (const tab of [page, demo]) tab.setDefaultTimeout(5000);
      await page.goto(origin);
      const standalone = page.locator('main a[href="/demo/en/#readiness-title"]');
      await checkContentLink(standalone, motion);
      await checkExcludedLink(page.locator(".bar-links a:visible").first(), "Desktop bar");
      await checkExcludedLink(page.locator("footer nav a").first(), "Footer");
      await checkPrint(standalone);

      await page.goto(origin + "/about/");
      const inline = page.locator('main a[href*="better-open-source"]');
      await checkContentLink(inline, motion, { inline: true });
      await checkPrint(inline, true);

      await page.goto(origin + "/start/");
      const card = page.locator(".tile-link").first();
      await checkContentLink(card, motion, { hit: card.locator("p") });

      await demo.goto(origin + "/demo/en/");
      const blockers = demo.locator('.summary-links a[href="#status-blocker"]');
      await checkContentLink(blockers, motion);
      await checkContentLink(demo.locator(".finding-area.area-link").first(), motion);
      await checkExcludedLink(demo.locator(".bar-links a:visible").first(), "Report desktop bar");
      await checkPrint(blockers);

      await demo.setViewportSize({ width: 360, height: 844 });
      await demo.reload();
      await demo.evaluate(() => document.fonts.ready);
      const wrapped = demo.locator('.scope-links a[href="#replacement-device_management"]');
      assert.equal(await wrapped.locator(".link-text").evaluate(label => label.getClientRects().length), 2);
      await checkContentLink(wrapped, motion);

      for (const [tab, route] of [[page, "/de/"], [demo, "/demo/de/"]]) {
        await tab.setViewportSize({ width: 390, height: 844 });
        await tab.goto(origin + route);
        await tab.locator(".menu-button").press("Enter");
        await checkExcludedLink(tab.locator(".bar-links a:visible").first(), `${route} phone menu`);
      }
    } finally {
      await website.close();
      await report.close();
    }
  }
  console.log("Content underlines passed hover, keyboard, reduced-motion, navigation and print checks.");
}
