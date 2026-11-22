---
quick_id: 261122-rv2
status: complete
date: 2026-11-22
---

# CLI messages and report wording

## Results

- **R-10.** Output beneath the current directory is printed as a relative path. Other output uses the directory spelling supplied with `--out`, including any symlink alias. Input errors use the supplied filename. Write errors use the supplied output directory and the generated filename when one is available. CLI tests use fictional names and addresses in the working directory, symlink targets and input filenames. Both READMEs document the path users can open.
- **R-11.** Duplicate keys, non-finite numbers, ambiguous integer spellings and invalid syntax produce bilingual sentences with a line number. Scan and inputs diagnostics name a field when it is registered at that position. Unknown keys are identified by line alone. Count errors say to enter a whole number without leading zeros. Whole-file and command-line errors now name the file or option directly. The existing privacy tests pass unchanged.
- **R-12.** Both `fazit` and `fazit --debug` without a command show help and exit 2. Report usage shows `SCAN_JSON`. Unreadable scans and inputs use the localised file error. `python -m fazit` uses the console entry point and is included in the wheel.
- **R-13.** The security guide and READMEs document owner-only output permissions on Unix (mode `0600`) because the files describe the organisation's IT. The output test checks the permissions on creation and replacement.
- **R-14.** The Nextcloud report and both homepages identify the SIP bridge supplied with a Nextcloud Talk Enterprise subscription and the SIP gateway required for calls over the public telephone network. Both ask the assessor to include the quoted recurring cost and check call routing and queues. The mapping records the review date and the Talk installation guide. [Talk installation guide](https://nextcloud-talk.readthedocs.io/en/stable/quick-install/#introduction), [Nextcloud Talk user manual](https://docs.nextcloud.com/server/stable/user_manual/en/talk/conversations.html), [Nextcloud Enterprise pricing](https://nextcloud.com/Pricing/)
- **R-15.** The German transfer heading is now “Direkte Übernahme nicht belegt”, and both READMEs describe an unverified direct transfer. The path headings name the Ready status in both languages. In the side-by-side review, German “Aus Beispieldaten berechnet” became “Aus Beispielangaben berechnet” to identify sample inputs. The German skipped-collector reason now says the procedure was not run, matching the English description without implying a deliberate skip.
- **R-16.** The German report and homepage quote use “Zugewiesene Zusatzlizenz für Telefonie”. The report uses the corresponding workload name for each finding.
- **R-17.** Added `.ppam`, `.ppsm`, `.sldm` and the macro-capable Excel binary format `.xlsb` to the rules and both interview checklists. The list already included `.potm`, `.xltm`, `.xlam` and `.dotm`. The report says “May contain macros”, and `.dotx` is excluded. [Microsoft Open XML format table](https://support.microsoft.com/en-us/office/vba/open-xml-formats-and-file-name-extensions), [Microsoft Excel macro formats](https://support.microsoft.com/en-us/excel/copy-a-macro-module-to-another-workbook)
- **R-18.** Shared light-theme link hover now has 5.22:1 contrast on white and 4.79:1 on the light surface. Solid site links also pass on hover. The links brighten and dark-mode links retain their glow. The report and site tests cover the hover colours.
- **R-19.** The design comment is a Jinja comment, so generated reports omit it from the stylesheet source.

## Files changed

- `README.md` and `README.de.md` describe printed output paths, Unix permissions and unverified direct transfer in English and German.
- `SECURITY.md` explains output permissions on Unix and Windows.
- `docs/interview-checklist.md` and `docs/interview-checklist.de.md` list the additional macro-capable extensions in their Office questions.
- `src/fazit/cli.py` prints the caller's output paths, shows help when `--debug` has no command and routes unreadable files to the localised error handler.
- `src/fazit/__main__.py` provides the module entry point.
- `src/fazit/errors.py` carries the optional line number on input errors.
- `src/fazit/i18n.py` selects the sentence for a known field, a line, a whole file or a CLI option.
- `src/fazit/inputs.py` supplies the YAML parser with recognised field paths and count fields.
- `src/fazit/model.py` supplies the scan field paths and localises failures on deeply nested JSON.
- `src/fazit/output.py` uses the supplied path spelling in write errors.
- `src/fazit/parsing.py` takes positions from YAML marks and the JSON token stream and checks integer spellings before YAML conversion.
- `src/fazit/locales/en.yaml` and `src/fazit/locales/de.yaml` contain the revised CLI sentences and report wording in each language.
- `src/fazit/report.py` and `src/fazit/rules.py` identify invalid language and profile options in CLI terms.
- `src/fazit/rules/mappings/nextcloud.yaml` records the telephony prerequisites, procurement questions, source and date.
- `src/fazit/rules/risky_file_types.yaml` adds the Office extensions that can carry macros.
- `src/fazit/templates/report.html.j2` sets the hover colours and keeps the design note in the template.
- `site/index.html` and `site/de/index.html` carry the telephony guidance in their coverage sections. The German page also updates the quoted licence finding.
- `site/style.css` sets the accessible light hover colours for text and solid links.
- `site/demo/en/index.html` and `site/demo/de/index.html` were regenerated from the town openDesk demos. They show the revised headings, macro list and hover colours. The German report also shows the revised licence and evidence wording.
- `tests/test_cli.py` checks privacy-safe paths, bilingual parse sentences, help, unreadable files and module invocation.
- `tests/test_costs.py` checks the line and whole-number guidance when a padded headcount is rejected.
- `tests/test_evidence_cli.py` checks the German transfer heading.
- `tests/test_inputs.py` checks recognised YAML fields and line numbers for ambiguous spellings.
- `tests/test_installed_package.py` checks relative paths, updated error sentences and the module file in the wheel under the existing offline checks.
- `tests/test_model.py` checks line-only errors for unknown parser fields and rejection near the recursion limit.
- `tests/test_output.py` checks mode `0600` after creation and replacement on Unix.
- `tests/test_report.py` checks hover contrast, matching site colours and omission of the design comment.
- `tests/test_rules.py` checks the complete extension list.

## Verification

`uv sync` and all six checklist commands passed. `uv run pytest -q` passed 694 tests in 81.00 seconds. The site check inspected 16 pages and 519 references and matched both regenerated reports byte for byte. Chromium opened both demos offline at 360 px in light and dark mode with zero external requests. Each printed to A4 and passed the link hover check in both themes. Both Nextcloud demos showed the documented SIP prerequisites and check date.

## Deviations and open work

The mapping uses Nextcloud's documented product name, Talk Enterprise, for the subscription. The absolute-path promise mentioned in the plan had already been removed from the READMEs. The concurrent site commits `3dab9ac` and `fb6fc42` picked up the homepage, stylesheet and regenerated demo changes during this task. Git operations for this task were read-only. No task items remain open.

## Suggested commits

- R-10 `fix: preserve caller paths in terminal output` (visible).
- R-11 `fix: show safe source locations in parse errors` (visible).
- R-12 `fix: align CLI help and support python -m fazit` (visible).
- R-13 `docs: explain owner-only output permissions` (visible documentation).
- R-14 `fix: document Nextcloud Talk telephony requirements` (visible).
- R-15 `fix: align wording about transfer and readiness` (visible).
- R-16 `fix: label assigned add-on licences in German` (visible).
- R-17 `fix: list the missing macro-capable Office formats` (visible).
- R-18 `fix: meet AA contrast on link hover` (visible).
- R-19 `fix: omit design comments from generated reports` (HTML source only).

The site portions are already present in the concurrent commits above. Include this summary with the final commit.
