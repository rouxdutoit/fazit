# Fazit

[Deutsch](https://github.com/rouxdutoit/fazit/blob/main/README.de.md)

Fazit is a free, open source command-line tool for assessing a move from Microsoft 365 to an open source setup such as openDesk or Nextcloud. It creates a self-contained HTML report locally in English or German.

Fazit is in early development (alpha). It builds reports from bundled samples or a compatible `scan.json` with your answers and costs in `inputs.yaml`. Measured figures currently come from the samples.

## Try it

Install `uv`, clone this repository and run the command from the clone.

```sh
uv run fazit demo
```

The first run needs a network connection to download the Python packages. After setup, disconnect from the network and run the same command again to check that the report works offline. You can run the demo without a Microsoft account.

The default is an English report for a fictional town office using the openDesk profile. Try German, the fictional non-profit sample or the Nextcloud profile with these commands.

```sh
uv run fazit demo --lang de --out ./report/de
uv run fazit demo --sample nonprofit --out ./report/nonprofit
uv run fazit demo --profile nextcloud --out ./report/nextcloud
```

The demo writes `report-<YYYY-MM-DD>-<lang>.html`, `scan-<YYYY-MM-DD>-<lang>.json` and `inputs-<YYYY-MM-DD>-<lang>.yaml` to `./report` by default. `--out` sets a different directory. The date comes from the sample scan. A repeat run replaces files with the same names. The last line gives the path to the HTML report, relative to the current directory if the report is inside it. For other locations, Fazit uses the directory you entered with `--out`.

On Unix, Fazit creates output files with owner-only permissions (mode `0600`) because they describe the organisation's IT.

## Rebuild a report

Use the scan and inputs copies from the first demo to rebuild the report in German.

```sh
uv run fazit report ./report/scan-2026-11-02-en.json --inputs ./report/inputs-2026-11-02-en.yaml --lang de --out ./report/rebuilt
```

To try your own answers and costs, copy the example file. Fill in the values you know and leave unanswered fields empty. [Interview checklist](https://github.com/rouxdutoit/fazit/blob/main/docs/interview-checklist.md)

```sh
cp inputs.example.yaml inputs.yaml
```

Rebuild from the same scan using your answers.

```sh
uv run fazit report ./report/scan-2026-11-02-en.json --inputs inputs.yaml --lang de --out ./report/with-answers
```

Use `--lang en` or `--lang de` to choose the report language and `--profile opendesk`, `--profile nextcloud` or `--profile generic` to choose the target. With `report`, these flags take precedence over the settings in the inputs file.

Fazit checks the files for contradictions and labels the source of each figure. A fabricated scan that is consistent with itself can still produce a report, so a report is only as trustworthy as the tool and the person that produced the scan.

## What the report shows

1. Header with the scan date, the source of the data and how the report was made.
2. What we found in the inventory.
3. Five-year cost comparison for staying, partial exit and full exit.
4. Readiness by workload, including what was left unexamined.
5. What moves where under the chosen target profile.
6. Needs attention, including functions whose direct transfer to the target profile is unverified.
7. Suggested path with blockers, questions to resolve and possible pilot areas.
8. Appendix with collectors, rules, mappings and run details.
9. Footer with the project name.

The report assesses fifteen areas. Each area has a status of Ready, Needs work, Blocker or Unknown, with a reason and its evidence. Figures are marked as measured, provided or unknown. An unknown comes with a reason and a next step. The report provides no overall score or verdict.

Your browser may add the local file path to printed headers and footers. Before saving a PDF to share, open the browser's print settings and turn off **Headers and footers**. Check the preview for the file path.

## Where the project stands

Fazit runs from a clone and is not yet published on PyPI. Import and live collection are not available yet.

The next steps are coverage of AI assistants and licence renewal deadlines (1.1), CSV export for project plans and a report integrity check (1.2), and links to sovereignty criteria (1.3). Local import of Microsoft 365 admin-centre exports will follow in phase 2. Phase 3 will add `doctor`, browser sign-in and live licence and directory counts. Phase 4 will bring bilingual guides, packaging and a signed Windows build. [Project roadmap](https://github.com/rouxdutoit/fazit/blob/main/.planning/ROADMAP.md)

## What Fazit will never do

- Write to a Microsoft tenant or call an endpoint outside the read allowlist.
- Contact any hosts other than Microsoft sign-in and Microsoft Graph. This version contacts no host.
- Write tokens, collected person names or email addresses to disk by default. Collected data contains no free text. The only free text from input data shown in the report is the organisation name and the names of Windows-only applications entered in `inputs.yaml`.
- Load external resources from the report.
- Invent figures or let a skipped collector improve a status.

Assessment data stays on your computer only when the scan, inputs and `--out` directory are on local storage, since a network share transfers those files over the network.

[Security and vulnerability reporting](https://github.com/rouxdutoit/fazit/blob/main/SECURITY.md)

## Change the rules

The workload catalogue, status rules, service plans, risky file types and target mappings are YAML files under `src/fazit/rules/`. Edit them in the clone and run the same command again. An option to use a separate rules directory is planned for the first release.

## How it is made

Fazit is AI-assisted and human-reviewed. A human maintainer directs the work and is responsible for it. Claude Opus 5.5 and Codex GPT-6.2-Sol write the code, both at maximum effort, and every change is tested before it is committed. Before each release, Claude Fable 5.2 and Codex GPT-6.2-Astra, also at maximum effort, review the whole codebase independently and then against each other, including security. Their reviews are public. [Phase 1 reviews](https://github.com/rouxdutoit/fazit/tree/main/.planning/phases/01-demo-and-report)

## Licence

AGPL-3.0-or-later. [Licence](https://github.com/rouxdutoit/fazit/blob/main/LICENSE), [Contributing](https://github.com/rouxdutoit/fazit/blob/main/CONTRIBUTING.md), [Decisions](https://github.com/rouxdutoit/fazit/blob/main/DECISIONS.md)
