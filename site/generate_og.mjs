// SPDX-License-Identifier: AGPL-3.0-or-later
import { writeFile } from "node:fs/promises";
import { localContext, withSite } from "./check_browser.mjs";

const width = 1200;
const height = 630;
const padding = 96;
const safeMargin = 80;
const previews = [["/", "og.png"], ["/de/", "og-de.png"]];

const layout = `
  .social-preview {
    color-scheme: light;
    display: grid;
    grid-template-rows: auto 1fr auto;
    align-items: center;
    padding: ${padding}px calc((100vw - 576px) / 2);
  }
  .social-preview .wordmark { font-size: var(--fs-headline); line-height: 1.2; }
  .social-preview h1 {
    font-size: var(--fs-display);
    line-height: 1.08;
    margin-block-start: var(--rhythm-section-heading);
  }
  .social-preview .eyebrow { font-size: var(--fs-lead); }
  .preview-domain { color: var(--fg-2); }
`;

await withSite(async ({ browser, origin }) => {
  const context = await localContext(browser, origin, width, "light", {
    viewport: { width, height }, deviceScaleFactor: 1, javaScriptEnabled: false,
  });
  const page = await context.newPage();
  const images = new Map();
  for (const [route, filename] of previews) {
    const response = await page.goto(origin + route);
    if (!response?.ok()) throw new Error(`Could not load ${route}.`);
    await page.evaluate(css => {
      const style = document.createElement("style");
      style.textContent = css;
      document.head.append(style);
      const wordmark = document.createElement("p");
      wordmark.className = "wordmark";
      wordmark.textContent = document.querySelector(".bar .wordmark").textContent.trim();
      const headline = document.createElement("div");
      headline.append(document.querySelector("#hero .eyebrow"), document.querySelector("#hero h1"));
      const domain = document.createElement("p");
      domain.className = "preview-domain";
      domain.textContent = "fazit.dev";
      document.body.classList.add("social-preview");
      document.body.replaceChildren(wordmark, headline, domain);
    }, layout);
    const ready = await page.evaluate(async (inset) => {
      await document.fonts.ready;
      const figtreeLoaded = [...document.fonts].some(font => font.family === "Figtree" && font.status === "loaded");
      const crop = (innerWidth - innerHeight) / 2;
      const labels = document.querySelectorAll(".wordmark, .eyebrow, h1, .preview-domain");
      return figtreeLoaded && [...labels].every(label => {
        const range = document.createRange();
        range.selectNodeContents(label);
        const { left, right, top, bottom } = range.getBoundingClientRect();
        return left >= crop && right <= innerWidth - crop && top >= inset && bottom <= innerHeight - inset;
      });
    }, safeMargin);
    if (!ready) throw new Error(`Figtree or the centre crop check failed for ${filename}.`);
    const png = await page.screenshot();
    if (png.length >= 100_000) throw new Error(`${filename} must be under 100 KB.`);
    images.set(filename, png);
  }
  for (const [filename, png] of images) {
    await writeFile(new URL(filename, import.meta.url), png);
    console.log(`${filename}: ${png.length} bytes`);
  }
}, { engine: "chromium" });
