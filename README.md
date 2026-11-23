# Fazit

[Deutsch](https://github.com/rouxdutoit/fazit/blob/main/README.de.md)

Fazit is a free, open source command-line tool for assessing a move from Microsoft 365 to an open source setup such as openDesk or Nextcloud. It creates a self-contained HTML report locally in English or German.

Fazit is in early development (alpha). It builds reports from bundled samples with your answers and costs in `inputs.yaml`. The measured figures in the samples are simulated; import of your own Microsoft 365 exports comes next.

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

Rebuild from the same scan using your answers. The inventory figures still belong to the fictional town; only your answers and costs change. Do not share such a report as an assessment of your organisation.

```sh
uv run fazit report ./report/scan-2026-11-02-en.json --inputs inputs.yaml --lang de --out ./report/with-answers
```

Use `--lang en` or `--lang de` to choose the report language and `--profile opendesk`, `--profile nextcloud` or `--profile generic` to choose the target. With `report`, these flags take precedence over the settings in the inputs file.

Fazit checks the structure of its inputs and selected relationships between figures, and labels the source of each figure. It cannot establish that a supplied inventory is true, so a report is only as trustworthy as the tool and the people that produced its evidence.

## What the report shows

1. Header with the scan date, the source of the data and how the report was made.
2. What we found in the inventory.
3. Five-year cost comparison for staying, a partial move and a full move, at the prices you enter.
4. Readiness by area, including what was left unexamined.
5. What moves where under the chosen target profile.
6. Needs attention, including functions whose direct transfer to the target profile is unverified.
7. Suggested path with blockers, open questions and the areas that pass the current checks.
8. Appendix with collectors, rules, mappings and run details.

The report assesses fourteen areas. Each area has a status of Ready, Needs work, Blocker or Unknown, with a reason and its evidence. Inventory figures are marked as measured, provided or unknown, and cost figures as entered or calculated. An unknown comes with a reason and a next step. The report provides no overall score or verdict.

Your browser may add the local file path to printed headers and footers. Before saving a PDF to share, open the browser's print settings and turn off **Headers and footers**. Check the preview for the file path.

## Where the project stands

Fazit runs from a clone. The name `fazit` is reserved on PyPI with an empty 0.0.0 release; the first installable release comes with phase 2.1. Import and live collection are not available yet, and the measured figures in the samples are simulated.

Next comes local import of Microsoft 365 admin-centre exports (phase 2), then packaging: `uvx fazit` from PyPI and a signed Windows build (phase 2.1). After that come AI assistants and licence renewal deadlines (1.1), CSV export for project plans and a report integrity check (1.2), and links to sovereignty criteria (1.3). Phase 3 adds `doctor`, browser sign-in and live licence and directory counts, and phase 4 the guides for live scans. [Project roadmap](https://github.com/rouxdutoit/fazit/blob/main/.planning/ROADMAP.md)

## What Fazit will never do

- Write to a Microsoft tenant or call an endpoint outside the read allowlist.
- Contact any hosts other than Microsoft sign-in and Microsoft Graph. This version contacts no host.
- Write tokens, collected person names or email addresses to disk by default. The only free text from input data shown in the report is the organisation name and the names of Windows-only applications entered in `inputs.yaml`.
- Load external resources from the report.
- Present a missing figure as measured, or let a skipped collector improve a status.

Each of these gets a test when the code it guards exists. Today's tests cover offline operation and report output.

Assessment data stays on your computer only when the scan, inputs and `--out` directory are on local storage, since a network share transfers those files over the network.

[Security and vulnerability reporting](https://github.com/rouxdutoit/fazit/blob/main/SECURITY.md)

## Change the rules

The workload catalogue, status rules, service plans, risky file types and target mappings are YAML files under `src/fazit/rules/`. Edit them in the clone and run the same command again. A separate rules directory is deferred.

## How it is made

Fazit is written with AI tools and directed by a person. Claude and Codex write the code. The maintainer decides what is built and answers for it, without reading every line. CI runs the test suite on Linux, Windows and macOS. Before each release, other models look for faults, including security, and their findings and the fixes are public. [Phase 1 reviews](https://github.com/rouxdutoit/fazit/tree/main/.planning/phases/01-demo-and-report)

## Licence

AGPL-3.0-or-later. [Licence](https://github.com/rouxdutoit/fazit/blob/main/LICENSE), [Contributing](https://github.com/rouxdutoit/fazit/blob/main/CONTRIBUTING.md), [Decisions](https://github.com/rouxdutoit/fazit/blob/main/DECISIONS.md)
