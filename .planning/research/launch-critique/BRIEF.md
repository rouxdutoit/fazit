You are a sharp, sceptical Hacker News reader. The maintainer of Fazit is about to post it as a "Show HN". Read the project as the harshest fair critics in that thread would, and tell the maintainer what they will say before they say it.

Repository: the current directory (read-only). Fazit is a local, read-only Python CLI that writes one offline HTML report on what moving an organisation off Microsoft 365 would take (targets: openDesk, Nextcloud, a product-neutral profile), aimed at public bodies and integrators in Germany, Austria and Switzerland.

Read at least: site/index.html, site/start/index.html, site/security/index.html, site/pilots/index.html, site/integrators/index.html, site/privacy/index.html, site/demo/en/index.html (the sample report), README.md, SECURITY.md if present, CONTRIBUTING.md, DECISIONS.md, .planning/ROADMAP.md, pyproject.toml, and skim src/fazit/ and tests/.

Deliver, in English, plain Markdown, no preamble:
1. "Top comments": the 12 most likely critical comments, ranked by how much damage each would do to the thread. For each: the comment as a real HN commenter would write it (one or two sentences, in their voice); what in the repository or site triggers it (file and line or quote, max 15 words); whether the criticism is fair; and the smallest concrete change that answers it (copy, code, process or timing).
2. "Claims that overreach": every sentence on the site or in the README that a critic could call false, unverifiable, marketing or AI filler. Quote it (max 15 words each), say why, propose replacement wording.
3. "Remove or cut": anything that hurts more than it helps in front of this audience (features, sections, wording, animations, pages, files).
4. "Missing before launch": what an HN audience will expect that is absent (e.g. install path, binaries, signatures, threat model, screenshots of the CLI, comparison with alternatives, limitations).
5. "Launch timing": should this be posted now, or what must exist first? One paragraph.
Be specific and blunt. Do not praise. Do not suggest changes that contradict the project's privacy stance (no telemetry, no third-party requests).
