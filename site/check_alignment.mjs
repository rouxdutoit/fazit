// SPDX-License-Identifier: AGPL-3.0-or-later
import assert from "node:assert/strict";
import { iPhone, localContext, widths, withSite } from "./check_browser.mjs";
import { checkHomeLayout } from "./check_home_layout.mjs";
import { checkLinkUnderlines } from "./check_link_underlines.mjs";

const capsules = ".btn, .badge, .segmented label, .category-filter > button";
const menuItems = ".bar-links a, .category-filter option";
const singleLine = `${capsules}, ${menuItems}, button, .menu-button, .category-filter`;
const centredLabels = `${capsules}, ${menuItems}, a.language`;
const symbolOnly = ".copy, .menu-button, .foot-mail, .report-card-control, .cost-segment.is-unknown";
const textOnly = ".btn:not(.copy), .badge:not(.status), .bar-links a:not(.btn, .language), .segmented label:has(#f-status-all), .finding-evidence dd";
const chevronLabels = ".more, .tile-link h3, .replacement-status, summary:not(.menu-button)";
// Keep the component selectors so dropping the primitive from known markup fails the check.
const components = [
  centredLabels, symbolOnly, chevronLabels, ".symbol-label", ".status",
  ".cov-cell", ".coverage-key", ".safeguards li", ":is(h3, h4):has(> .tile-icon)",
  ".timeline-name", ".report-card-bar", ".cost-bars .legend li", ".command-line code > span",
  ".status-summary dt", ".finding-evidence dd", ".privacy-facts h3",
].join(", ");

function measureInPage({ scope, components, centredLabels, symbolOnly, textOnly, chevronLabels, singleLine, tolerance, scale }) {
  const fontSample = 512;
  const surface = document.createElement("canvas");
  surface.width = surface.height = fontSample;
  const canvas = surface.getContext("2d", { willReadFrequently: true });
  const stems = new Map();
  const bearings = new Map();
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

  function metrics(element, text) {
    canvas.font = font(element);
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

  function rightBearing(label, glyph) {
    canvas.font = font(label, `${fontSample}px`);
    const key = `${canvas.font} ${glyph}`;
    if (!bearings.has(key)) {
      // Canvas text bounds can include the glyph's advance. Read the painted ink instead.
      const start = 16;
      canvas.clearRect(0, 0, fontSample, fontSample);
      canvas.fillText(glyph, start, fontSample - 32);
      const { data } = canvas.getImageData(0, 0, fontSample, fontSample);
      let right = fontSample;
      search: for (; right > 0; right -= 1) {
        for (let alpha = 4 * right - 1; alpha < data.length; alpha += 4 * fontSample) {
          if (data[alpha] >= 128) break search;
        }
      }
      bearings.set(key, (start + canvas.measureText(glyph).width - right) / fontSample);
    }
    return bearings.get(key);
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

  function visible(element) {
    const style = getComputedStyle(element);
    return element.checkVisibility({ visibilityProperty: true })
      && !(style.position === "absolute" && style.clipPath !== "none");
  }

  function inScope(element) {
    return (!scope || element.closest(scope)) && visible(element)
      && (!element.matches("option") || element.closest("select:open"));
  }

  function oneRow(boxes) {
    // A symbol and a trimmed label have different top edges on the same line.
    return boxes.length < 2 ? 0 : Math.max(0,
      Math.max(...boxes.map(box => box.top)) - Math.min(...boxes.map(box => box.bottom)) + 0.02);
  }

  const inkSurface = document.createElement("canvas");
  const inkCanvas = inkSurface.getContext("2d", { willReadFrequently: true });
  const inkCache = new Map();

  function scanInk(text, label) {
    const scale = 4;
    const style = getComputedStyle(label);
    const em = scale * parseFloat(style.fontSize);
    const typeface = font(label, `${em}px`);
    const tracking = `${scale * (parseFloat(style.letterSpacing) || 0)}px`;
    const key = `${typeface} ${style.letterSpacing} ${text}`;
    if (inkCache.has(key)) return inkCache.get(key);

    inkCanvas.font = typeface;
    inkCanvas.letterSpacing = tracking;
    const advance = inkCanvas.measureText(text).width;
    inkSurface.width = Math.ceil(advance + 2 * em);
    inkSurface.height = Math.ceil(4 * em);
    inkCanvas.font = typeface;
    inkCanvas.letterSpacing = tracking;
    inkCanvas.fillText(text, em, 2 * em);
    const { width, height } = inkSurface;
    const { data } = inkCanvas.getImageData(0, 0, width, height);
    let left = width, right = 0, top = height, bottom = 0;
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        if (data[4 * (y * width + x) + 3] < 128) continue;
        left = Math.min(left, x);
        right = Math.max(right, x + 1);
        top = Math.min(top, y);
        bottom = Math.max(bottom, y + 1);
      }
    }
    // Offsets from the start, end and baseline of the text run in the document.
    const ink = { left: (left - em) / scale, right: (right - em - advance) / scale,
      top: (top - 2 * em) / scale, bottom: (bottom - 2 * em) / scale };
    inkCache.set(key, ink);
    return ink;
  }

  function paddingBox(element) {
    const box = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return {
      left: box.left + parseFloat(style.borderLeftWidth), right: box.right - parseFloat(style.borderRightWidth),
      top: box.top + parseFloat(style.borderTopWidth), bottom: box.bottom - parseFloat(style.borderBottomWidth),
    };
  }

  function measureScroll(element) {
    compare(element, "clipping: scroll height", Math.max(0, element.scrollHeight - element.clientHeight), 0);
    compare(element, "clipping: scroll width", Math.max(0, element.scrollWidth - element.clientWidth), 0);
  }

  function measureInk(element, ink) {
    const box = paddingBox(element);
    compare(element, "clipping: label ink beyond padding", Math.max(0,
      box.left - ink.left, ink.right - box.right, box.top - ink.top, ink.bottom - box.bottom), 0.25);
  }

  function textLines(node, range, first, end) {
    range.setStart(node, first);
    range.setEnd(node, end);
    const boxes = [...range.getClientRects()];
    if (boxes.length === 1) return [{ text: range.toString(), box: boxes[0] }];

    // Disclosure titles can wrap. Find which characters belong to each line for the ink check.
    return boxes.map(box => {
      let text = "";
      let offset = first;
      for (const glyph of node.data.slice(first, end)) {
        range.setStart(node, offset);
        offset += glyph.length;
        range.setEnd(node, offset);
        if (Math.abs(range.getBoundingClientRect().top - box.top) < 0.02) text += glyph;
      }
      return { text, box };
    }).filter(line => line.text.trim());
  }

  function measureControl(element) {
    const oneLine = element.matches(singleLine);
    const content = element.matches("select") ? element.querySelector(":scope > button") : element;
    measureScroll(element);
    if (!content || !visible(content)) return;
    const children = [...content.children].filter(visible).map(child => child.getBoundingClientRect())
      .filter(box => box.width && box.height);
    if (oneLine) compare(element, "wrap: control children", oneRow(children), 0);

    const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    const labelBoxes = [];
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const label = node.parentElement;
      if (!node.data.trim() || !visible(label)) continue;
      const first = node.data.length - node.data.trimStart().length;
      const end = node.data.trimEnd().length;
      const lines = textLines(node, range, first, end);
      if (oneLine) compare(element, "wrap: text fragments", lines.length - 1, 0);
      if (!lines.length) continue;
      const firstBaseline = baseline(label);
      const pickerLabel = element === content && label.closest("selectedcontent, option > .symbol-text");
      if (pickerLabel) measureScroll(pickerLabel);
      for (const { text, box } of lines) {
        labelBoxes.push(box);
        const ink = scanInk(text, label);
        const y = firstBaseline + box.top - lines[0].box.top;
        const footprint = { left: box.left + ink.left, right: box.right + ink.right,
          top: y + ink.top, bottom: y + ink.bottom };
        measureInk(element, footprint);
        // The engine can clip glyphs at a picker label's line box inside the control.
        if (pickerLabel) measureInk(pickerLabel, footprint);
      }
    }
    if (oneLine) compare(element, "wrap: control text", oneRow(labelBoxes), 0);
  }

  function measureSegments(track) {
    const segments = [...track.querySelectorAll(":scope > label")];
    const boxes = segments.map(segment => segment.getBoundingClientRect());
    const checked = track.querySelector("label:has(:checked)");
    const selected = checked?.getBoundingClientRect();
    const inner = paddingBox(track);
    const names = [...track.querySelectorAll(".segment-name")];
    const compact = names.length && !names.some(visible);
    compare(track, "wrap: segment tops", Math.max(...boxes.map(box => box.top)) - Math.min(...boxes.map(box => box.top)), 0.02);
    measureScroll(track);
    compare(track, "height: selection fills the inset track", selected?.height - (inner.bottom - inner.top - 4), 0.02);
    compare(track, "shape: selected segment top inset", selected?.top - inner.top - 2, 0.02);
    for (const element of [track, checked].filter(Boolean)) {
      const style = getComputedStyle(element);
      compare(element, "shape: capsule radius", style.borderRadius === style.getPropertyValue("--radius-pill").trim() ? 0 : NaN, 0);
    }
    for (const [index, box] of boxes.entries()) {
      compare(segments[index], "height: segment compared with selection", box.height - selected?.height, 0.02);
      if (compact) compare(segments[index], "compact segment width", box.width - boxes[0].width, 0.02);
    }
  }

  function lastLetter(label, em) {
    // The picker clones the selected option's label into selectedcontent.
    const content = label.querySelector(":scope > .symbol-text") ?? label;
    const text = (content.querySelector(":scope > .link-text") ?? content).firstChild;
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
    const tracking = parseFloat(getComputedStyle(label).letterSpacing) || 0;
    const bearing = rightBearing(label, last) * em + tracking;
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
    if (pair.matches(".tile-link h3")) {
      const tail = svg.parentElement;
      const surfaces = [getComputedStyle(svg), getComputedStyle(tail),
        getComputedStyle(tail, "::before"), getComputedStyle(tail, "::after")];
      if (!tail.matches(".symbol-text > .chevron-tail") || surfaces.some(style =>
        style.backgroundColor !== "rgba(0, 0, 0, 0)" || style.backgroundImage !== "none")) {
        failures.push({ selector: selector(pair.closest(".tile-link")), check: "plain card chevron", offset: "—" });
      }
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
    const category = pair.matches(".category-picker");
    const turned = category || pair.matches("details[open] > summary");
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

    const trailingLink = !category && !pair.matches("summary");
    const last = trailingLink ? lastLetter(label, em) : {};
    const lineBaseline = baseline(label) + (last.lineOffset ?? 0);
    if (turned) {
      compare(pair, "rotated chevron centre", centre(ink) - (lineBaseline - 0.25 * em));
    } else {
      compare(pair, "chevron baseline", ink.bottom - lineBaseline);
    }
    if (trailingLink) compare(pair, "chevron ink gap", ink.left - last.right - 0.40 * em, 0.03 * em);
    return ink;
  }

  function measureButtonGap(button, gap) {
    const style = getComputedStyle(button);
    const token = style.getPropertyValue("--btn-symbol-gap").trim();
    const expected = token === "0.4em" ? parseFloat(token) * parseFloat(style.fontSize) : NaN;
    compare(button, "button symbol gap", gap - expected, 0.5);
  }

  function measureCategory(select) {
    const picker = select.closest(".category-picker");
    if (!picker) {
      failures.push({ selector: selector(select), check: "missing category trigger", offset: "—" });
      return;
    }
    const custom = getComputedStyle(select).appearance === "base-select";
    const label = custom ? select.querySelector("selectedcontent > .symbol-text")
      : [...picker.querySelectorAll(".category-label")].find(visible);
    const arrow = picker.querySelector(":scope > .chevron");
    if (!label || !visible(label) || label.textContent !== select.selectedOptions[0].label || !arrow || !visible(arrow)) {
      failures.push({ selector: selector(select), check: "missing selected label or category chevron", offset: "—" });
      return;
    }
    const ink = measureChevron(picker, arrow, label);
    if (!ink) return;
    const box = paddingBox(picker);
    const range = document.createRange();
    range.selectNodeContents(label);
    const text = range.getBoundingClientRect();
    const start = text.left - box.left;
    const end = box.right - ink.right;
    measureButtonGap(picker, ink.left - text.right);
    compare(picker, "category start padding", start - 16, 0.5);
    compare(picker, "category start and end padding", start - end, 0.5);
    compare(picker, "wrap: category label", range.getClientRects().length - 1, 0);
    compare(select, "category hit target width", select.getBoundingClientRect().width - (box.right - box.left), 0.5);
    measureButton(select, select.getBoundingClientRect());
  }

  function measureButton(button, box) {
    const compact = button.matches(".bar-cta") && matchMedia("(min-width: 820px)").matches;
    const style = getComputedStyle(button);
    const token = compact ? "--btn-compact-height" : "--btn-height";
    const fill = compact && getComputedStyle(button, "::before");
    const height = fill && fill.backgroundColor !== "rgba(0, 0, 0, 0)" ? parseFloat(fill.height) : box.height;
    compare(button, token, height - parseFloat(style.getPropertyValue(token)), 0);
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
    if (!inScope(pair)) continue;

    const labels = [...pair.querySelectorAll(":scope > .symbol-text:not(.command-prompt)")].filter(visible);
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
    const pairStyle = getComputedStyle(pair);
    const { borderTopWidth, borderBottomWidth } = pairStyle;
    const paddingCentre = centre(box) + (parseFloat(borderTopWidth) - parseFloat(borderBottomWidth)) / 2;
    const symbolAbove = pair.matches(".privacy-facts h3") && pairStyle.flexDirection === "column";
    for (const symbol of symbols) {
      if (symbolAbove) {
        const icon = symbol.getBoundingClientRect();
        const text = labels[0].getBoundingClientRect();
        const gap = parseFloat(pairStyle.getPropertyValue("--rhythm-section-heading"));
        compare(pair, "privacy symbol left edge", icon.left - text.left, 0.02);
        compare(pair, "privacy symbol above title", text.top - icon.bottom - gap, 0.02);
      } else {
        compare(pair, selector(symbol), inkCentre(symbol) - (capCentres[0] ?? paddingCentre));
      }
    }
    if (!symbolAbove && symbols.length && labels.length) {
      const gap = labels[0].getBoundingClientRect().left - symbols[0].getBoundingClientRect().right;
      if (pair.matches(".badge")) compare(pair, "badge symbol gap", gap - 4, 0.5);
      if (pair.matches(".btn, a.language, .menu-button, .segmented label, .category-filter option")) {
        measureButtonGap(pair, gap);
      }
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
    if (pair.matches(".safeguards li")) {
      compare(pair, "safeguard top padding", parseFloat(pairStyle.paddingTop) - 16, 0);
      compare(pair, "safeguard bottom padding", parseFloat(pairStyle.paddingBottom) - 16, 0);
    }
    if (pair.matches(".command-line code > span")) {
      const { lineHeight, fontSize } = getComputedStyle(labels[0]);
      compare(pair, "command line height", parseFloat(lineHeight) - 1.7 * parseFloat(fontSize), 0.02);
      if (pair.previousElementSibling) {
        compare(pair, "command line gap", box.top - pair.previousElementSibling.getBoundingClientRect().bottom, 0.02);
      }
    }
    if (pair.matches(".copy")) {
      compare(pair, "copy hit target width", box.width - parseFloat(getComputedStyle(pair).getPropertyValue("--hit")), 0);
      compare(pair, "command block centre", centre(box) - centre(pair.closest(".command-line").getBoundingClientRect()));
    }
  }

  for (const control of document.querySelectorAll(`${singleLine}, summary`)) {
    if (inScope(control)) measureControl(control);
  }
  for (const track of document.querySelectorAll(".segmented")) {
    if (inScope(track)) measureSegments(track);
  }
  for (const select of document.querySelectorAll(".category-filter")) {
    if (inScope(select)) measureCategory(select);
  }

  function measureBar() {
    const bar = document.querySelector(".bar-in");
    const wordmark = bar?.querySelector(".wordmark");
    const visible = wordmark?.checkVisibility({ opacityProperty: true, visibilityProperty: true });
    compare(wordmark ?? document.body, "wordmark centre", visible
      ? centre(wordmark.getBoundingClientRect()) - centre(bar.getBoundingClientRect()) : NaN);
  }

  function measureTimeline(timeline) {
    const rail = getComputedStyle(timeline, "::before");
    const width = parseFloat(rail.width);
    const box = timeline.getBoundingClientRect();
    const railCentre = box.left + parseFloat(rail.left) + width / 2;
    const pageBg = getComputedStyle(document.body).backgroundColor;
    compare(timeline, "timeline device scale", devicePixelRatio - scale, 0);
    compare(timeline, "rail width", rail.content !== "none" && rail.backgroundImage !== "none" ? width - 1 : NaN, 0);
    for (const [index, step] of [...timeline.children].entries()) {
      const dot = step.querySelector(".timeline-dot");
      if (!dot) {
        compare(step, "timeline dot", NaN);
        continue;
      }
      const marker = dot.getBoundingClientRect();
      compare(step, "dot centred on rail", (marker.left + marker.right) / 2 - railCentre, 0.1);
      compare(step, "dot width equals height", marker.width - marker.height, 0.1);
      compare(step, "dot width in whole pixels", marker.width - 11, 0);
      compare(step, "dot starts at the timeline edge", marker.left - box.left, 0.1);
      if (index === 0) compare(step, "rail starts at first dot", box.top + parseFloat(rail.top) - centre(marker));

      const style = getComputedStyle(dot);
      if (style.borderRadius !== "50%" || style.aspectRatio !== "1 / 1" || style.boxSizing !== "border-box"
        || style.flexGrow !== "0" || style.flexShrink !== "0" || style.flexBasis !== "auto") {
        failures.push({ selector: selector(step), check: "fixed circular dot", offset: "—" });
      }
      const expectedFill = step.classList.contains("on") ? style.color : pageBg;
      if (style.backgroundColor !== expectedFill || !(Number(style.zIndex) > (Number(rail.zIndex) || 0))) {
        failures.push({ selector: selector(step), check: "dot covers the rail", offset: "—" });
      }
    }
  }

  const timelines = !scope || scope === ".timeline" ? document.querySelectorAll(".timeline") : [];
  for (const timeline of timelines) measureTimeline(timeline);
  if (!scope) {
    measureBar();
    const costTiles = [...document.querySelectorAll("#costs [data-cost-tile]")];
    const [firstTile] = costTiles;
    for (const tile of costTiles) {
      const label = tile.querySelector(".tile-label");
      const amount = tile.querySelector(".figure-num");
      const offset = amount?.getBoundingClientRect().left - label?.getBoundingClientRect().left;
      compare(tile, "cost figure column", offset);
      if (tile !== firstTile && !tile.closest(".home") && matchMedia("(min-width: 640px)").matches) {
        compare(tile, "cost label row", capCentre(label) - capCentre(firstTile.querySelector(".tile-label")));
        compare(tile, "cost figure row", capCentre(amount) - capCentre(firstTile.querySelector(".figure-num")));
      }
    }
  }
  return { failures, count, maximum, timelines: timelines.length };
}

async function clickCopyButton(page, button) {
  // WebKit can stop delivering animation frames after the layout probes.
  const point = await button.evaluate(element => {
    element.scrollIntoView({ block: "center", behavior: "instant" });
    const { x, y, width, height } = element.getBoundingClientRect();
    const centre = { x: x + width / 2, y: y + height / 2 };
    return element.contains(document.elementFromPoint(centre.x, centre.y)) ? centre : null;
  });
  assert(point, "Copy button centre is not a hit target");
  await page.mouse.click(point.x, point.y);
}

async function checkStatusKeyboard(page, measure) {
  const radios = await page.locator(".segmented input:enabled").all();
  const cards = page.locator(".areas .finding:visible");
  const all = await cards.count();
  await radios[0].focus();
  for (const radio of radios.slice(1)) {
    await page.keyboard.press("ArrowRight");
    assert(await radio.isChecked(), "ArrowRight selects the next status");
    const status = (await radio.getAttribute("id")).replace("f-status-", "");
    const shown = await cards.evaluateAll(rows => rows.map(row => row.dataset.status));
    assert(shown.length && shown.every(value => value === status), `Incorrect areas for ${status}`);
    await measure(".segmented");
  }
  for (const radio of radios.slice(0, -1).reverse()) {
    await page.keyboard.press("ArrowLeft");
    assert(await radio.isChecked(), "ArrowLeft selects the previous status");
  }
  assert.equal(await cards.count(), all);
}

async function checkStatusNames(page, width) {
  for (const segment of await page.locator(".segmented label.status").all()) {
    const name = await segment.getAttribute("title");
    const count = await segment.locator(".segment-count").textContent();
    assert(name && await segment.getByRole("radio", { name: `${name} ${count}`, exact: true }).count(),
      "Status title and radio name match");
    const word = segment.locator(".segment-name");
    assert.equal(await word.textContent(), name);
    assert.equal(await word.evaluate(element => getComputedStyle(element).clipPath !== "none"), width <= 390);
  }
}

async function checkCategoryChoices(category, measure) {
  const values = await category.locator("option").evaluateAll(options => options.map(option => option.value));
  for (const value of values) {
    await category.selectOption(value);
    await measure(".category-picker");
  }
}

async function disableCustomPicker(category) {
  const native = await category.evaluate(select => {
    // Exercise the native select used when appearance: base-select is unavailable.
    const sheet = document.querySelector("style").sheet;
    for (const media of [...sheet.cssRules].filter(rule => rule instanceof CSSMediaRule)) {
      const index = [...media.cssRules].findIndex(rule =>
        rule instanceof CSSSupportsRule && rule.conditionText.includes("appearance: base-select"));
      if (index !== -1) media.deleteRule(index);
    }
    return getComputedStyle(select).appearance !== "base-select";
  });
  assert(native, "Native category picker fallback is active");
}

async function checkCategoryPicker(page, measure) {
  const category = page.locator("#f-category");
  await page.keyboard.press("Tab");
  assert(await category.evaluate(element => element === document.activeElement), "Tab reaches the category picker");
  const custom = await category.evaluate(element => getComputedStyle(element).appearance === "base-select");
  if (custom) {
    await page.keyboard.press("Space");
    await category.locator("option:checked > .symbol").waitFor();
    await measure(".category-picker");
    const nextValue = await category.locator("option").nth(1).getAttribute("value");
    await page.keyboard.press("ArrowDown");
    await page.keyboard.press("Enter");
    assert.equal(await category.inputValue(), nextValue);
    const shown = await page.locator(".areas .finding:visible").evaluateAll(rows => rows.map(row => row.dataset.category));
    assert(shown.length && shown.every(value => value === nextValue), `Incorrect areas for ${nextValue}`);
    await checkCategoryChoices(category, measure);
    await disableCustomPicker(category);
  }
  assert(await category.evaluate(select => {
    const { left, right, top, height } = select.getBoundingClientRect();
    return [left + 5, right - 5].every(x => document.elementFromPoint(x, top + height / 2) === select);
  }), "Native select covers the entire category trigger");
  await checkCategoryChoices(category, measure);
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
    await clickCopyButton(page, button);
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
    await checkStatusKeyboard(page, measure);
    await checkCategoryPicker(page, measure);
    await checkStatusNames(page, width);
  }
}

const tolerance = 0.75;

async function checkScaledTimelines(browser, origin, timelineRoutes, viewports, measure) {
  for (const viewport of viewports) {
    const { width, device, options } = viewport;
    for (const scale of [1, 2, 3]) {
      if (scale === (options.deviceScaleFactor ?? 1)) continue;
      for (const theme of ["light", "dark"]) {
        const context = await localContext(browser, origin, width, theme, { ...options, deviceScaleFactor: scale });
        try {
          const page = await context.newPage();
          for (const route of timelineRoutes) {
            const response = await page.goto(origin + route);
            assert(response?.ok(), `Timeline page did not load: ${route}`);
            await page.evaluate(() => document.fonts.ready);
            await measure(page, { page: route, width, theme, device, scale }, ".timeline");
          }
        } finally {
          await context.close();
        }
      }
    }
  }
}

async function checkAlignment({ browser, origin, routes }) {
  const failures = [];
  const timelineRoutes = new Set();
  let maximum = 0;
  let count = 0;
  let views = 0;
  let timelineViews = 0;
  const chromium = browser.browserType().name() === "chromium";
  const viewports = [...widths, 390].sort((a, b) => a - b)
    .map(width => ({ width, device: "viewport", options: {} }));
  const sizes = [...viewports, iPhone];
  async function measure(page, view, scope) {
    const result = await page.evaluate(measureInPage, {
      scope, components, centredLabels, symbolOnly, textOnly, chevronLabels, singleLine, tolerance, scale: view.scale,
    });
    failures.push(...result.failures.map(failure => ({ ...view, ...failure })));
    count += result.count;
    maximum = Math.max(maximum, result.maximum);
    if (result.timelines) {
      timelineRoutes.add(view.page);
      timelineViews += 1;
    } else if (scope === ".timeline") {
      failures.push({ ...view, selector: ".timeline", check: "missing timeline", offset: "—" });
    }
  }
  for (const { width, device, options } of sizes) {
    for (const theme of ["light", "dark"]) {
      const context = await localContext(browser, origin, width, theme, options);
      const reportContext = await localContext(browser, origin, width, theme, { ...options, javaScriptEnabled: false });
      if (chromium) await context.grantPermissions(["clipboard-write"], { origin });
      const website = await context.newPage();
      const report = await reportContext.newPage();
      for (const page of [website, report]) page.setDefaultTimeout(3000);
      for (const route of routes) {
        const view = { page: route, width, theme, device, scale: options.deviceScaleFactor ?? 1 };
        const page = route.startsWith("/demo/") ? report : website;
        views += 1;
        try {
          await checkPage(page, route, width, origin, scope => measure(page, view, scope));
        } catch (error) {
          failures.push({ ...view, selector: "page", check: error.message.split("\n").slice(0, 6).join(" "), offset: "—" });
        }
      }
      await context.close();
      await reportContext.close();
    }
  }
  await checkScaledTimelines(browser, origin, timelineRoutes, sizes, measure);
  if (failures.length) {
    console.table(failures);
    process.exitCode = 1;
  }
  console.log(`${views} full page views including iPhone emulation and ${timelineViews} timeline views at device scales 1, 2 and 3.`);
  console.log(`${count} alignment measurements. Maximum offset ${maximum.toFixed(2)} px. ${failures.length} failures.`);
}

await withSite(async site => {
  await checkHomeLayout(site);
  await checkAlignment(site);
  await checkLinkUnderlines(site);
});
