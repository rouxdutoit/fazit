---
quick_id: 261122-rv2
slug: messages-wording
date: 2026-11-22
status: complete
---

# Quick task: release review batches 2 and 3, messages, CLI and report wording

Fix R-10 to R-19 from `.planning/quick/261122-rev-release-review/FINDINGS.md`. The reviewers' evidence is in `REVIEW-fable-1.md` and `REVIEW-astra-1.md` in the same folder. Batch 1 (`261122-rv1-judgement`) has just landed; read its `SUMMARY.md`.

## Items

1. **R-10 (high).** Printed output must not reveal more of the file system than the user typed. Print written paths relative to the current directory when they lie beneath it, otherwise as the user gave `--out` (not resolved, no home directory expansion added by Fazit). Error messages name a file by the name the user gave, never by a resolved absolute path. Test stdout and stderr with a working directory and file names that contain a person-like name and an `@`, and keep REPT-06 and CLI-06 true. Update `README.md` and `README.de.md` where they promise an absolute path.
2. **R-11 (medium).** Errors found while parsing (duplicate key, non-finite number, invalid integer spelling, YAML or JSON syntax) name the line, and the known field where there is one: "Remove the repeated key `currency` on line 2 of inputs.yaml." Keys that are not known fields are never echoed (they may be private): name the line only. An invalid integer spelling says what to write: "Write target_costs.partial_exit.users in inputs.yaml as a whole number without leading zeros." (batch 1 currently prints only "Check the value of ..."). No message ends in "at $" or "in fazit". Rewrite the affected strings in both locales; German formal and natural. Keep the existing privacy tests passing unchanged and add cases for the new wording.
3. **R-12 (low).** `fazit --debug` with no command prints the help and exits 2 (or 0 with help, matching how `fazit` alone behaves; choose one and test it). The usage line shows `SCAN_JSON`, not `{SCAN_JSON}`. An unreadable scan file reaches the localised `not_readable` sentence. Add `src/fazit/__main__.py` so `python -m fazit` works, and test it.
4. **R-13 (low).** Document in `SECURITY.md` (and the README section on output, if there is one) that written files are readable only by the user (mode 0600) because they describe the organisation's IT. Keep the behaviour.
5. **R-14 (high).** Nextcloud telephony: check the Nextcloud Talk documentation the reviewer cites (https://nextcloud-talk.readthedocs.io/en/stable/quick-install/#introduction) and Nextcloud's own pages on the SIP bridge. State in `rules/mappings/nextcloud.yaml` (both languages, with the source URL and check date) and in the home page coverage table, in both languages, that connecting to the public telephone network uses the SIP bridge, which is part of a Nextcloud Enterprise subscription, plus a SIP gateway; prompt the assessor to include the quoted recurring cost and to check routing and queues. If the documentation does not support the claim, change nothing and say so.
6. **R-15 (medium).** German wording that says more than English: "Nicht direkt übertragbar" becomes "Direkte Übernahme nicht belegt" (or better German with the same meaning), the README's "cannot be moved" matches, and the heading "Bereiche, in denen die Bestandsaufnahme kein Hindernis zeigt" is reworded so it does not reuse the Blocker status word. Check both locales side by side for any other pair whose meaning differs, and list each change in the summary.
7. **R-16 (low).** "Separat zugewiesene Lizenz für {workload}" becomes "Zugewiesene Zusatzlizenz für {workload}" in the report and in the site's quoted finding.
8. **R-17 (medium).** Add every macro-enabled Office format from Microsoft's file format table (https://support.microsoft.com/en-us/office/vba/open-xml-formats-and-file-name-extensions) that is missing from `rules/risky_file_types.yaml` (at least `.ppsm`, `.ppam`, `.sldm`; check `.potm`, `.xltm`, `.xlam`, `.dotm` too) and to both interview checklists in `docs/`. Keep "may contain macros" (D12) and keep `.dotx` out.
9. **R-18 (medium).** Link hover in the light theme must keep at least 4.5:1 against its background, in the report and on the site if they share the rule. Keep the founder's design intent (links brighten on hover, glow in dark mode, never underline): in light mode use a hover colour that still passes, for example a brighter but darker-enough shade. Extend the contrast test to the hover state.
10. **R-19 (low).** The design comment in the report's CSS (apple.com neutrals, iOS colours) becomes a Jinja comment so it is not in customers' reports.

## Rules

- If the report HTML changes, regenerate `site/demo/en/index.html` and `site/demo/de/index.html` and say what changed visibly.
- New and changed user-facing strings exist in both locales.
- Suggest one commit per item. Mark each that changes user-visible behaviour or wording.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
```
