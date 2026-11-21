# Befund phase 1 confirmation

Checked HEAD `bda51df` offline with `uv run befund report scan.json --inputs inputs.yaml --out out` on temporary fixtures. Scan-only runs omitted `--inputs`. Both Ruff checks and all 522 tests passed (44.01 seconds).

Finding | Status | Evidence
--- | --- | ---
H1 | resolved | Fresh English and German demos and CLI rebuilds matched both checked-in site samples byte for byte.
H2 | resolved | Both footers printed `https://github.com/rouxdutoit/befund` as plain text.
H3 | resolved | `SECURITY.md` links the private advisory form for `rouxdutoit/befund` and gives a fallback.
H4 | resolved | Both home pages copy the clone command. Their only `uvx` examples say to wait for PyPI release.
H5 | resolved | Adding `EXCHANGE_S_ENTERPRISE` or an unlisted E3 plan kept Teams Ready. All 1,343 catalogue pairs matched the cached Microsoft reference.
M1 | resolved | The 700-byte alias fixture exited 2 in 0.35 seconds with one diagnostic.
M2 | resolved | With 500 macro-capable files measured and 271 supplied, “At least 500 files” came first with a conflict explanation.
M3 | resolved | Planting `Erika_Mustermann` in SKU and plan names yielded zero HTML or JSON occurrences.
M4 | resolved | Town showed Needs work for Windows software, identified the desktop obstacle and marked both mapping needs Yes.
M5 | resolved | `git log` counted 10 Codex and 24 Claude trailers. CONTRIBUTING scopes DCO to outside contributors from first release.
M6 | resolved | Counted eight current principles. AGENTS and CLAUDE point to them. HANDOFF is marked historical. The founder list is gone.
L1 | resolved | NUL and U+202E in organisation and application names produced four field-specific rejections.
L2 | resolved | Rendered headings read “Direct transfer unverified” and “Nicht direkt übertragbar”.
L3 | resolved | CLI enforced 15 integer and two fractional digits. English usage showed `SCAN_JSON`. HTML starts at doctype. CI runs the SPDX-marked checker. Both checklists omit the invented-price question.
A01 | resolved | Scan-only output showed “Unregistered product 1”. `ReviewMarker` occurred in neither HTML nor JSON. Both language sites disclose operator-entered organisation and application names.
A02 | partly | Three integrations measured plus zero supplied gave Needs work. Skipping directory gave Unknown with an explicit finding. Omitting that finding gave Ready despite `permission_denied`.
A03 | partly | Mailbox-usage zero for shared mailboxes exited 2. Recipient export zero gave Ready. With both phone answers false, a licence inventory with zero products and `licences.source=sample.mailbox_usage` gave Telephony Ready and labelled absence measured.
A04 | resolved | Twelve assigned MCOEV seats gave Blocker. Empty and omitted plan lists both gave Unknown.
A05 | resolved | The original directory measurement was rejected. With the permitted telephony source, agreeing answers preserved Blocker and disagreement prevented Ready.
A06 | resolved | Four measured integrations outranked one supplied with a conflict note. A 1,250-byte minimum displayed as “At least 1.2 kB”.
A07 | resolved | Partial licence coverage retained the phone Blocker and warning. Unconfirmed Power Platform absence stayed Unknown.
A08 | resolved | A shared YAML mapping and 2,097,153-byte JSON and YAML files each exited 2 within one second.
A09 | partly | CLI preserved the FIFO. A blocked HTML destination left zero companions. A simulated final rename failure left two. D-71 declines directory pinning because anyone able to replace the folder already controls its files.
A10 | resolved | Unknown key `ReviewMarker` produced `$[0]`. CLI escaped U+202E in stderr and a newline in the success path.
A11 | resolved | `git check-ignore` matched root answers and both the original and current report directories.
A12 | resolved | Firefox printed the path on 27/27 English and 28/28 German pages. Following the documented header/footer setting removed it from all 55.
A13 | resolved | Site checker passed 208 references and rejected either altered sample. Both reports showed totals 600,000, 527,800 and 464,350.
A14 | resolved | Both rebuilds retained four sample quantity labels. Removing the sample-answer flag gave four Provided labels while prices stayed invented.
A15 | resolved | Both checklists ask about use. Yes, no and blank gave Needs work, Ready and Unknown for sharing and SharePoint customisation.
A16 | resolved | A 2099 cutoff failed. HEAD’s cutoff was over 14 days old. All 189 artifacts predated it. CI pins uv 0.13.9.
A17 | resolved | Policy test passed with fallback `hello@rouxdutoit.com`. Hosted settings remain unverified.
A18 | resolved | Live 0.0.9 and import 0.1.0 produced distinct HTML hashes with origin, producer and renderer visible. Export codes await phase 2 by plan.
A19 | partly | Obsolete naming question removed. The plan reserves D25’s first-release clearance decision for the founder.
A20 | partly | Signed-off HEAD contains the initial-history attestation. The part B summary records founder confirmation as pending.

Source checks confirmed the deletions, split render function and links to workload evidence.

## New high regression

**An unclassified Teams Phone plan produces Ready.** Keep only town’s 12-seat `MCOEV` product and mark licence coverage complete (1/1). Set `telephony.in_use` and `telephony.replacement_available` to false in `confirmations`. Replace its sole plan with `{"name":"REVIEW_PLAN","guid":"00000000-0000-4000-8000-000000000001"}` and run the command above. The original plan gave Blocker on both revisions. The replacement gave Unknown on `e8975a3` and Ready on HEAD, which labelled the separate licence “No” and “Measured”.

## Verdict

**Not ready to make the repository public.** A02, A03 and the Teams Phone regression each allow Ready without sufficient evidence.
