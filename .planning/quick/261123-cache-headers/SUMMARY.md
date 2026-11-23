# Website cache headers

HTML, directory URLs, `sitemap.xml`, `robots.txt`, and `/.well-known/security.txt` use `Cache-Control: no-cache`. `style.css` and `site.js` also revalidate on each visit because their URLs stay the same across deploys.

`/fonts/*`, `/icons/*`, and `/images/*` keep `public, max-age=86400`. Bunny applies the two browser cache policies with opposite conditions on the same asset paths, so rule order is irrelevant. The browser header override runs on cache hits. Apache applies the same policies. [Bunny edge rule execution](https://bunny.net/docs/cdn/edge-rules/ordering)

The existing deploy script purges pull zone `7064266` after upload and cleanup when `BUNNY_API_KEY` is set. The edge rules workflow now checks the public cache headers after applying the rules. The new policy takes effect on Bunny when that workflow runs.

## Verification

- `uv run pytest -q` passed all 959 tests. `uv run ruff check .`, `uv run ruff format --check .`, and `uv run python site/check_site.py` passed. The site checker now checks the revalidation default and all three one-day asset rules.
- Local checks verified the generated Bunny rules, the deploy script's purge order, and the headers on Apache. Both demo reports opened in offline Chromium with zero HTTP requests.
