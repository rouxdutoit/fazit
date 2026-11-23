// SPDX-License-Identifier: AGPL-3.0-or-later
import { writeFile } from "node:fs/promises";
import { localContext, withSite } from "./check_browser.mjs";

const width = 1200;
const height = 630;
const fontSize = 84;

await withSite(async ({ browser, origin }) => {
  const context = await localContext(browser, origin, width, "light", {
    viewport: { width, height }, deviceScaleFactor: 1, javaScriptEnabled: false,
  });
  const page = await context.newPage();
  const response = await page.goto(origin);
  if (!response?.ok()) throw new Error("Could not load the home page.");
  const image = await page.evaluate(async ({ width, height, fontSize }) => {
    const wordmark = document.querySelector(".bar .wordmark");
    const text = wordmark?.textContent.trim();
    if (!text) throw new Error("The home page wordmark is missing.");
    const { color, fontFamily, fontWeight } = getComputedStyle(wordmark);
    const font = `${fontWeight} ${fontSize}px ${fontFamily}`;
    if (!(await document.fonts.load(font, text)).length) {
      throw new Error("Could not load the wordmark font.");
    }

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const drawing = canvas.getContext("2d", { alpha: false });
    drawing.fillStyle = getComputedStyle(document.body).backgroundColor;
    drawing.fillRect(0, 0, width, height);
    drawing.font = font;
    const capHeight = drawing.measureText("H").actualBoundingBoxAscent;
    if (capHeight < 56 || capHeight > 64) {
      throw new Error(`Expected a wordmark cap height of 56–64 px, got ${capHeight} px.`);
    }
    const {
      actualBoundingBoxLeft: left, actualBoundingBoxRight: right,
      actualBoundingBoxAscent: ascent, actualBoundingBoxDescent: descent,
    } = drawing.measureText(text);
    // The glyph bounds account for the font's side bearings and baseline.
    drawing.fillStyle = color;
    drawing.fillText(text, (width + left - right) / 2, (height + ascent - descent) / 2);
    return canvas.toDataURL("image/png").split(",")[1];
  }, { width, height, fontSize });
  const png = Buffer.from(image, "base64");
  if (png.length >= 100_000) throw new Error("og.png must be under 100 KB.");
  await writeFile(new URL("og.png", import.meta.url), png);
  console.log(`og.png: ${png.length} bytes`);
}, { engine: "chromium" });
