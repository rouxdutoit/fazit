// SPDX-License-Identifier: AGPL-3.0-or-later
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { iPhone, localContext, withSite } from "./check_browser.mjs";

const widths = [360, 390, 768, 960, 1130, 1280];
const routes = ["/", "/de/"];
const tolerance = 0.02;

function measureHome({ width, theme, contrast, tolerance }) {
  const select = selector => document.querySelector(selector);
  const all = selector => [...document.querySelectorAll(selector)];
  const box = element => element.getBoundingClientRect();
  const style = element => getComputedStyle(element);
  const columns = element => style(element).gridTemplateColumns.split(" ").map(parseFloat);
  const root = document.documentElement;
  const rem = parseFloat(style(root).fontSize);
  const errors = [];
  const expect = (condition, name) => { if (!condition) errors.push(name); };
  const near = (actual, expected, name) =>
    expect(Math.abs(actual - expected) <= tolerance, `${name} (${actual}, expected ${expected})`);
  const gutter = width <= 600 ? 16 : Math.min(64, width * 0.055);
  const overflow = Math.max(root.scrollWidth, document.body.scrollWidth) - root.clientWidth;
  expect(innerWidth === width && overflow === 0, "Horizontal overflow");
  near(parseFloat(style(select(".hero")).paddingInlineStart), gutter, "Site gutter");

  const preview = box(select(".report-card"));
  near(preview.width, Math.min(width - 2 * gutter, 62.5 * rem), "Report window width");
  near((preview.left + preview.right) / 2, width / 2, "Report window centre");

  const spread = values => Math.max(...values) - Math.min(...values);
  const groupSelectors = [".preview-statuses", ".preview-details", ".home-costs .tiles", ".privacy-facts"];
  const heightDifference = Math.max(...groupSelectors.map(selector =>
    spread([...select(selector).children].map(card => box(card).height))));
  near(heightDifference, 0, "Card heights");
  expect(columns(select(".preview-statuses")).length === (width < 760 ? 2 : 4), "Status tile columns");
  expect(columns(select(".preview-details")).length === (width < 760 ? 1 : 2), "Preview detail columns");
  expect(columns(select(".home-costs .tiles")).length === 1, "Cost tile columns");

  const cards = all(".preview-summary li");
  const offsets = selector => cards.map(card => box(card.querySelector(selector)).top - box(card).top);
  const valueDifference = spread(offsets(".preview-value"));
  const captionDifference = spread(offsets(".preview-caption"));
  near(valueDifference, 0, "Hero value alignment");
  near(captionDifference, 0, "Hero caption alignment");
  for (const card of cards) {
    const label = card.querySelector(".preview-label");
    const value = style(card.querySelector(".preview-value"));
    const caption = style(card.querySelector(".preview-caption"));
    near(box(label).height, 32, "Card label height");
    expect(label.scrollWidth === label.clientWidth, "Clipped card label");
    expect(parseFloat(value.fontSize) === 2.25 * rem && value.fontWeight === "600", "Card value type");
    expect(caption.fontSize === style(select(".hero-status")).fontSize, "Card caption type");
  }

  for (const [index, beat] of all(".home-beat").entries()) {
    const tracks = columns(beat);
    const copy = box(beat.querySelector(".home-beat-copy"));
    const panel = beat.querySelector(".home-panel");
    const panelBox = box(panel);
    const panelStyle = style(panel);
    const padding = parseFloat(panelStyle.paddingLeft);
    const group = box(panel.firstElementChild);
    const reversed = index % 2 !== 0;
    if (width < 880) {
      expect(tracks.length === 1 && copy.bottom < panelBox.top, "Stacked beat order");
      near(panelBox.width, tracks[0], "Stacked panel width");
    } else {
      expect(tracks.length === 2 && (reversed ? panelBox.right < copy.left : panelBox.left > copy.right), "Alternating beat order");
      near(tracks[reversed ? 1 : 0], 5 * (tracks[0] + tracks[1]) / 12, "Copy column width");
      near(panelBox.width, Math.min(tracks[reversed ? 0 : 1], 0.48 * width, 34 * rem), "Panel width");
    }
    near(padding, Math.min(32, Math.max(20, 0.026 * width)), "Panel padding");
    near(panelBox.height, group.height + 2 * padding, "Panel fits content");
    near(group.width, Math.min(panelBox.width - 2 * padding, 30 * rem), "Card group width");
    expect(panelStyle.borderRadius === "32px", "Panel radius");
    for (const card of panel.querySelectorAll(".finding, .tiles > li, .command")) {
      const surface = style(card);
      expect(surface.backgroundColor === style(document.body).backgroundColor, "Card surface");
      expect(surface.borderWidth === "0px" && surface.outlineStyle === "none", "Card edge");
    }
  }

  const privacy = select(".privacy-facts");
  const panel = privacy.parentElement;
  const privacyWidth = box(panel).width - 2 * parseFloat(style(panel).paddingLeft);
  const privacyColumns = columns(privacy).length;
  expect(privacyColumns === (privacyWidth < 26 * rem ? 1 : 3), "Privacy container breakpoint");
  let privacyTitleLines = 0;
  for (const title of privacy.querySelectorAll("h3")) {
    const range = new Range();
    range.selectNodeContents(title.querySelector(".symbol-text"));
    privacyTitleLines = Math.max(privacyTitleLines, range.getClientRects().length);
    expect(style(title).flexDirection === (privacyColumns === 3 ? "column" : "row"), "Privacy symbol position");
  }
  expect(privacyColumns === 1 || privacyTitleLines === 1, "Privacy titles stay on one line");

  const command = select(".home-panel .command");
  const commandLabel = command.querySelector(".command-label");
  const commands = select(".home-panel .command-line");
  const commandPadding = parseFloat(style(command).paddingLeft);
  const commandBox = box(command);
  const commandLines = box(commands);
  const labelBox = box(commandLabel);
  const icon = commands.querySelector(".copy > .symbol");
  near(commandLines.left - commandBox.left, commandPadding, "Command inset");
  near(commandBox.right - box(icon).right, commandPadding, "Copy symbol inset");
  near(labelBox.top - commandBox.top, commandPadding, "Command label top inset");
  near(commandBox.bottom - commandLines.bottom, commandPadding, "Command bottom inset");
  expect(style(commands).backgroundColor === "rgba(0, 0, 0, 0)", "Command uses one surface");

  expect(matchMedia(`(prefers-color-scheme: ${theme})`).matches, "Colour scheme");
  expect(matchMedia(`(prefers-contrast: ${contrast})`).matches, "Contrast preference");
  const surface = document.createElement("canvas").getContext("2d", { willReadFrequently: true });
  const luminance = colour => {
    surface.clearRect(0, 0, 1, 1);
    surface.fillStyle = colour;
    surface.fillRect(0, 0, 1, 1);
    const [r, g, b] = Array.from(surface.getImageData(0, 0, 1, 1).data).map(channel => {
      const value = channel / 255;
      return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const minContrast = Math.min(...all(".home :is(.badge, .lead, .note-text, .preview-caption, .hero-sub)").map(element => {
    let background = element;
    while (style(background).backgroundColor === "rgba(0, 0, 0, 0)") background = background.parentElement;
    const tones = [luminance(style(element).color), luminance(style(background).backgroundColor)];
    return (Math.max(...tones) + 0.05) / (Math.min(...tones) + 0.05);
  }));
  expect(minContrast >= 4.5, `Text contrast (${minContrast}:1)`);
  const palette = all(".preview-statuses .status .icon").map(icon => style(icon).color).join(", ");
  return { errors, overflow, heightDifference, valueDifference, captionDifference, privacyColumns, privacyTitleLines, minContrast, palette };
}

async function checkFocusOrder(page, mobile) {
  let stops = 0;
  const focus = locator => locator.evaluate(element => element === document.activeElement && element.matches(":focus-visible"));
  async function tabThrough(locators) {
    for (const locator of locators) {
      await page.keyboard.press("Tab");
      assert(await focus(locator), `Expected visible keyboard focus on ${locator}`);
      stops += 1;
    }
  }
  await tabThrough([page.locator(".skip"), page.locator("header .wordmark")]);
  const menu = page.locator(".menu-button");
  if (mobile) {
    await tabThrough([menu]);
    await page.keyboard.press("Enter");
  }
  await tabThrough(await page.locator(".bar-links a:visible").all());
  if (mobile) {
    await page.keyboard.press("Escape");
    assert(await focus(menu), "Closing the menu must return focus to its button");
  }
  const main = [
    "#hero .btn-solid", "#hero .btn-secondary", "#blocker .more", "#example .more",
    "#costs .more", "#privacy .more", "#how .note-text a", "#how .more", "#how .copy",
    "#status .btn-solid", "#status .btn-secondary",
  ].map(selector => page.locator(selector));
  await tabThrough([...main, ...await page.locator("footer a").all()]);
  await page.reload();
  await tabThrough([page.locator(".skip")]);
  await page.keyboard.press("Enter");
  assert(await page.locator("#main").evaluate(element => element === document.activeElement), "Skip link moves focus to main");
  await tabThrough(main.slice(0, 1));
  return stops;
}

export async function checkHomeLayout({ browser, origin }) {
  const rows = [];
  let focusStops = 0;
  for (const width of widths) {
    const measurements = [];
    for (const theme of ["light", "dark"]) {
      const palettes = new Map();
      for (const contrast of ["no-preference", "more"]) {
        const context = await localContext(browser, origin, width, theme, { ...(width === 390 && iPhone.options), contrast });
        try {
          const page = await context.newPage();
          const currentPalettes = [];
          for (const route of routes) {
            const response = await page.goto(origin + route);
            assert(response?.ok(), `Home page did not load: ${route}`);
            await page.evaluate(() => document.fonts.ready);
            const result = await page.evaluate(measureHome, { width, theme, contrast, tolerance });
            assert.deepEqual(result.errors, [], `${route}, ${width} px, ${theme}, contrast ${contrast}`);
            measurements.push(result);
            currentPalettes.push(result.palette);
            if (contrast === "no-preference" && theme === "light" && [390, 1280].includes(width)) {
              focusStops += await checkFocusOrder(page, width === 390);
            }
          }
          palettes.set(contrast, currentPalettes);
        } finally {
          await context.close();
        }
      }
      assert(palettes.get("more").every((palette, index) => palette !== palettes.get("no-preference")[index]),
        `Increased contrast did not change the ${theme} status colours at ${width} px`);
    }
    const maximum = key => Math.max(...measurements.map(result => result[key]));
    rows.push({
      width, views: measurements.length, overflow: maximum("overflow"),
      "height delta": maximum("heightDifference"), "value delta": maximum("valueDifference"),
      "caption delta": maximum("captionDifference"), "privacy columns": maximum("privacyColumns"),
      "privacy title lines": maximum("privacyTitleLines"),
      "minimum text contrast": Math.min(...measurements.map(result => result.minContrast)).toFixed(2),
    });
  }
  console.table(rows);
  console.log(`${focusStops} keyboard stops across both home pages at 390 and 1280 px, with menu and skip link verification.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await withSite(checkHomeLayout);
}
