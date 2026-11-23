// SPDX-License-Identifier: AGPL-3.0-or-later
import { readdir, readFile } from "node:fs/promises";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const modules = process.env.PLAYWRIGHT_DIR ?? "/home/roux/.local/share/playwright-1.62.1/node_modules/";
const { chromium, webkit } = createRequire(resolve(modules, "check_browser.cjs"))(
  process.env.PLAYWRIGHT_MODULE ?? "playwright",
);
const engines = { chromium, webkit };
const site = fileURLToPath(new URL(".", import.meta.url));
const types = {
  ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp",
};

export const widths = [360, 768, 1280];

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

export async function withSite(check, { origin: suppliedOrigin, classicScrollbars = false } = {}) {
  const engine = process.env.PLAYWRIGHT_ENGINE;
  if (engine !== undefined && !Object.hasOwn(engines, engine)) {
    throw new Error("PLAYWRIGHT_ENGINE must be chromium or webkit.");
  }
  const files = await readdir(site, { recursive: true });
  const routes = files.filter(file => file.endsWith(".html") && !file.split(sep).some(part => part.startsWith(".")))
    .map(file => ("/" + file.split(sep).join("/")).replace(/\/index\.html$/, "/")).sort();
  const server = suppliedOrigin ? null : await serve();
  const origin = suppliedOrigin ?? `http://127.0.0.1:${server.address().port}`;
  try {
    for (const name of engine ? [engine] : Object.keys(engines)) {
      let browser;
      try {
        browser = await engines[name].launch(classicScrollbars && name === "chromium" ? {
          ignoreDefaultArgs: ["--hide-scrollbars"],
          args: ["--disable-features=OverlayScrollbar,FluentOverlayScrollbar"],
        } : {});
        console.log(`\n${name === "chromium" ? "Chromium" : "WebKit"} ${browser.version()}`);
        await check({ browser, origin, routes });
      } catch (error) {
        console.error(`${name}: ${error.message}`);
        process.exitCode = 1;
      } finally {
        await browser?.close();
      }
    }
  } finally {
    if (server) await new Promise(done => server.close(done));
  }
}

export async function localContext(browser, origin, width, colorScheme, options = {}) {
  const context = await browser.newContext({
    viewport: { width, height: 900 }, colorScheme, reducedMotion: "reduce", ...options,
  });
  await context.route("**/*", route =>
    new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
  return context;
}
