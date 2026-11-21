# Befund

[Deutsch](README.de.md)

Befund is a free, open source command-line tool for assessing a move from Microsoft 365 to an open source setup such as openDesk or Nextcloud. It shows what an organisation relies on, what would need work and how the costs compare. It runs locally and creates a self-contained HTML report in English or German.

## Try it

Install `uv`, clone this repository and run the command from the clone.

```sh
uv run befund demo
```

The first run needs a network connection to download the Python packages. After setup, disconnect from the network and run the same command again to check that the report works offline. You can run the demo without a Microsoft account.

The default is an English report for a fictional town office using the openDesk profile. Try German, the fictional non-profit sample or the Nextcloud profile with these commands.

```sh
uv run befund demo --lang de --out ./report/de
uv run befund demo --sample nonprofit --out ./report/nonprofit
uv run befund demo --profile nextcloud --out ./report/nextcloud
```

The demo writes `report-<YYYY-MM-DD>-<lang>.html`, `scan-<YYYY-MM-DD>-<lang>.json` and `inputs-<YYYY-MM-DD>-<lang>.yaml` to `./report` by default. `--out` sets a different directory. The date comes from the sample scan. A repeat run replaces files with the same names. The last line it prints is the absolute path of the HTML report.

## Rebuild a report

Use the scan and inputs copies from the first demo to rebuild the report in German.

```sh
uv run befund report ./report/scan-2026-11-02-en.json --inputs ./report/inputs-2026-11-02-en.yaml --lang de --out ./report/rebuilt
```

To try your own answers and costs, copy the example file. Fill in the values you know and leave unanswered fields empty. [Interview checklist](docs/interview-checklist.md)

```sh
cp inputs.example.yaml inputs.yaml
```

Rebuild from the same scan using your answers.

```sh
uv run befund report ./report/scan-2026-11-02-en.json --inputs inputs.yaml --lang de --out ./report/with-answers
```

Use `--lang en` or `--lang de` to choose the report language and `--profile opendesk`, `--profile nextcloud` or `--profile generic` to choose the target. With `report`, these flags take precedence over the settings in the inputs file.

## What the report shows

1. Header with the scan date, the source of the data and how the report was made.
2. What we found in the inventory.
3. Five-year cost comparison for staying, partial exit and full exit.
4. Readiness by workload, including what was left unexamined.
5. What moves where under the chosen target profile.
6. Needs attention, including functions that cannot be moved.
7. Suggested path with blockers, questions to resolve and possible pilot areas.
8. Appendix with collectors, rules, mappings and run details.
9. Footer with the project name.

The report assesses fifteen areas. Each area has a status of Ready, Needs work, Blocker or Unknown, with a reason and its evidence. Figures are marked as measured, provided or unknown. An unknown comes with a reason and a next step. The report provides no overall score or verdict.

Your browser may add the local file path to printed headers and footers. Before saving a PDF to share, open the browser's print settings and turn off **Headers and footers**. Check the preview for the file path.

## Where the project stands

Befund is in early development. It builds reports from bundled sample data or from a `scan.json` you already have. Scanning a real tenant is not available yet. Befund runs from a clone and is not yet published on PyPI.

The next step is local import of Microsoft 365 admin-centre exports. After that come the `doctor` command, browser sign-in and live licence and directory counts. Bilingual guides, packaging and a signed Windows build follow with the first release.

## What Befund will never do

- Write to a Microsoft tenant or call an endpoint outside the read allowlist.
- Contact any hosts other than Microsoft sign-in and Microsoft Graph. This version contacts no host.
- Write tokens, collected person names or email addresses to disk by default. Collected data contains no free text. The only free text from input data shown in the report is the organisation name and the names of Windows-only applications entered in `inputs.yaml`.
- Load external resources from the report.
- Invent figures or let a skipped collector improve a status.

[Security and vulnerability reporting](SECURITY.md)

## Change the rules

The workload catalogue, status rules, service plans, risky file types and target mappings are YAML files under `src/befund/rules/`. Edit them in the clone and run the same command again. An option to use a separate rules directory is planned for the first release.

## How it is built

Befund is written with AI assistance from Claude and Codex. Each reviews the other's work. A human maintainer directs the work and is responsible for it.

## Licence

AGPL-3.0-or-later. [Licence](LICENSE), [Contributing](CONTRIBUTING.md), [Decisions](DECISIONS.md)
