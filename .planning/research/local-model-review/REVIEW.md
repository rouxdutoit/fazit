# Local open-weights review of Fazit

Run on 2026-11-22 on the founder's Windows computer, against commit `8bc7e3715f2ce768261a3a10750306dded6c308a`. The model read Fazit's source one file (or file part) at a time and reported faults. Claude (Opus 5.5, in Claude Code) chose the setup, ran it and checked every finding against the code. No code was changed.

This is a record of a repeatable offline check. It is not a quality credential and is not for the website.

## Result in one paragraph

The model produced 80 raw findings. After checking each one against the code: **1 confirmed**, **2 plausible**, **77 wrong**. The confirmed finding is latent and has no effect on today's output. Neither plausible finding affects a status or a cost figure. Nothing found here needs fixing before a release.

## Setup

| Item | Value |
|---|---|
| Model | Qwen3.8-27B (Alibaba Qwen team, released 2026-08-05), dense 27B, hybrid attention |
| Upstream weights | `huggingface.co/Qwen/Qwen3.8-27B`, revision `37561816e66b5b9153b1b64c10968c18c1e6f4a0` |
| Model file | `Qwen3.8-27B-UD-IQ4_XS.gguf` (4-bit, Unsloth), from `huggingface.co/unsloth/Qwen3.8-27B-GGUF`, repo revision `4af51b3542f775b0a8e4b310bfb3f17e01c306c9` |
| File size and SHA-256 | 14,352,911,264 bytes, `4b194b34ecec99fdfb74caef84445ccd01c987de87d96ae8ca50dc434b4b0a38` (matches Hugging Face) |
| Model licence | Apache-2.0 (upstream and quantised repo) |
| Runner | llama.cpp build b12633, commit `9c10c94e1` (`version: 1.0.0-dev`), official Windows CUDA 13.5 x64 release from `github.com/ggml-org/llama.cpp` |
| Runner files and SHA-256 | `llama-b12633-bin-win-cuda-13.5-x64.zip` `5fadbb7d1f4b7e612f77c7b626c60445d5d1fc9d990425ee7f37d5f17a8c68ad`; `cudart-llama-bin-win-cuda-13.5-x64.zip` `c2bf4cc202bfbaaa7a0b75f5082457c3811326947bb216059b72839d844e9cba` (both match GitHub) |
| Runner licence | MIT |
| Hardware | AMD Ryzen 7 9800X3D, 32 GB RAM, NVIDIA RTX 5080 16 GB (driver 621.01), Windows 11 |
| Server | Bound to `127.0.0.1:8080` only (checked with `netstat`); 32,768-token context, one slot, q8_0 KV cache, flash attention, reasoning on with an 8,192-token thinking budget. The model fitted on the graphics card (14.6 of 16 GB used). |
| Sampling | temperature 0.6, top_p 0.95, top_k 20, min_p 0, seed 42, max 16,000 output tokens per request |
| Speed | about 33-36 output tokens per second |

Why this model: the brief asked for the strongest Apache-2.0 or MIT coding model that fits a 16 GB card, from a family other than the ones that wrote the code (Anthropic's Claude and OpenAI's Codex). That rules out gpt-oss (OpenAI), Gemma and Llama (own licences), and Qwen3.8-Flash-Next (custom licence). Qwen3.8-27B is the newest model meeting those conditions. The runner-up was Mistral's Devstral Small 2 24B (Apache-2.0, December 2025).

An earlier LM Studio installation on this computer had been removed; only its data folder remained (a Gemma 4 12B and a half-finished Ministral download). It was not used.

## Scope

35 requests covered:

- all 19 Python files in `src/fazit/` (`__init__.py`, `__main__.py` and `errors.py` together in one request; long files split into two parts);
- all 7 rule files in `src/fazit/rules/` (`service_plans.yaml` in five parts, `status.yaml` and `nextcloud.yaml` in two);
- the report template `src/fazit/templates/report.html.j2` in three parts.

Not sent: locale strings, demo data, fonts, icons and licence texts. These are data rather than code, and the brief asked for Python and rule files. Each part keeps the file's own line numbers. The split points are in `run_review.py`.

`src/` is 474 KB, not the 360 KB the brief estimated.

## The prompt

The fixed prompt is `prompt.txt`. `{principles}` is filled with the "Principles" section of `DECISIONS.md` at run time; `{path}`, `{part}` and `{code}` with the file label and the line-numbered code.

```text
You are reviewing one part of the source code of Fazit, a free command-line tool written in Python. Fazit reads an organisation's Microsoft 365 evidence (a scan.json file and an inputs.yaml file of answers and costs) and writes one offline HTML report on what moving off Microsoft 365 would take. Rule files in YAML hold the judgement: status rules, mappings, findings, risky file types and licence service plans.

The project's principles, copied from DECISIONS.md:

{principles}

Your task: find concrete faults in the code below. Report only:

1. bug: code that gives a wrong result, crashes, or does something other than what it plainly intends.
2. unhandled-input: an input the code accepts (from scan.json, inputs.yaml, a rule file, the command line or the file system) that leads to a crash, a traceback, or a silently wrong result.
3. contradicts-comment: behaviour that differs from what a comment or docstring in the same code says.
4. contradicts-principle: behaviour that breaks one of the principles above. Pay special attention to: anything that writes or sends data off the computer, a missing value being treated as zero or as good news, a skipped or unknown input making a status look better, and any figure that is invented rather than supplied or measured.

Do not report style, naming, missing type hints, missing tests, performance, or suggestions for new features. Do not report something you would need to guess about; you only see this part of the program, so if a fault depends on code you cannot see, say so in "confidence". Quote the exact line or lines.

The code has line numbers at the start of each line. Use them.

Answer in exactly this format, one block per finding, and nothing else:

FINDING
file: <path>
line: <line number or range>
kind: <bug | unhandled-input | contradicts-comment | contradicts-principle>
claim: <one sentence: what is wrong>
evidence: <the exact quoted line or lines>
why: <one to three sentences: the input or situation that triggers it and what goes wrong>
confidence: <high | medium | low>

If you find no faults, answer exactly: NO FINDINGS

File: {path}{part}

{code}
```

## How to repeat the run

Needs Git, Python 3.12 or newer (standard library only) and an NVIDIA card with 16 GB. No administrator rights.

1. Clone Fazit and check out `8bc7e3715f2ce768261a3a10750306dded6c308a` (or the commit you want to review).
2. Download the two llama.cpp zips above from release `b12633` on `github.com/ggml-org/llama.cpp/releases`, check the SHA-256 values and unzip both into `%USERPROFILE%\llm\llama.cpp-b12633`.
3. Download `Qwen3.8-27B-UD-IQ4_XS.gguf` from `huggingface.co/unsloth/Qwen3.8-27B-GGUF`, check the SHA-256 and put it in `%USERPROFILE%\llm\models`.
4. Start the server: `powershell -NoProfile -ExecutionPolicy Bypass -File .planning\research\local-model-review\start_server.ps1`. Wait until `http://127.0.0.1:8080/health` returns `{"status":"ok"}`.
5. From the repository root run `python -u .planning/research/local-model-review/run_review.py`. It writes one answer file per request to `raw/`, the model's thinking to `raw/reasoning/`, and timings and token counts to `raw/run-log.jsonl`. An answer file that already exists is skipped, so an interrupted run resumes; delete `raw/` for a fresh run. `--list` prints the 35 requests without running them.
6. Stop the server and triage every finding against the code.

The same seed and settings on different hardware, drivers or llama.cpp builds will not give byte-identical answers. Expect the same kind of output, not the same text.

## Run figures

| | |
|---|---|
| Requests | 35, all finished normally (`stop`), none cut off |
| Generation time | 8,360 s (2 h 19 min), about 4 minutes per request |
| Tokens in / out | 148,716 / 293,727 (output includes the model's thinking) |
| Raw findings | 80 (1 request answered NO FINDINGS) |
| Triage time | roughly as long again, done while the run continued |

## Triaged findings

Every finding was checked against the code in this commit. Six licence-data claims were also checked against Microsoft's "Product names and service plan identifiers for licensing" CSV, downloaded on 2026-11-22 from `download.microsoft.com`. That file is the source `service_plans.yaml` cites.

### Confirmed (1)

| # | File and line | Finding | Effect |
|---|---|---|---|
| C1 | `src/fazit/report.py:367`, `380-383` | The icon loader takes the first `<path>` in an SVG (`_ICON_PATH.search`). Its error says "has no single path", but nothing checks that there is only one. | Latent. All five bundled icons have exactly one path, so today's reports are correct. A future icon with two paths would be embedded incomplete without an error. |

### Plausible (2)

| # | File and line | Finding | Why only plausible |
|---|---|---|---|
| P1 | `src/fazit/model.py:59-65` | When one timestamp carries a time-zone offset and the other has none, `_timestamp_after` drops the offset and compares clock times, so the "collected after the scan" check can be off by the offset (up to about 14 hours). | A naive time has no defined zone, so any choice is a guess. It only affects a load-time sanity check, never a status or figure, and no comment says which reading was intended. |
| P2 | `src/fazit/rules/risky_file_types.yaml:34` | Visio lists only `.vsdx`, so legacy `.vsd` drawings (and macro-enabled `.vsdm`) are not counted. The same pattern applies to Access `.mde`/`.accde`. | As specified: `HANDOFF.md:86` and `SKELETON.md:132` list only `vsdx`. Whether old Visio files matter to the audience is a product decision, not a code fault. |

### Wrong (77)

The usual cause: the model saw one file and flagged a missing check that the loader already performs in a file it could not see. There were also misreadings of the code in front of it and a few factual errors.

| File and line (as reported) | Claim | Why it is wrong |
|---|---|---|
| `catalogue.py:67-71` | Non-string `guid` crashes `accepts_sku_part_number` | Both callers pass a GUID already checked by `Validator.guid` (`model.py:441`, `licences.py:155`). |
| `catalogue.py:23-24` | `sku_key` crashes on a non-string GUID | Same; other callers use `or ""` or check for `None` first (`licences.py:227`, `model.py:135,480`). |
| `catalogue.py:146-152` | `measured_by: null` mishandled | `Validator.fields(None, …)` raises the normal one-line error naming file and field (`validation.py:35-38`). |
| `cli.py:141` | Invalid `--lang` reaches the renderer | `check_language` runs first (`cli.py:149`), and the error path switches to English for exactly that error (`cli.py:80-81`). |
| `cli.py:155` | `language` from `inputs.yaml` is unchecked | Checked on load (`inputs.py:246-248`). |
| `cli.py:156` | `target_profile` from `inputs.yaml` is unchecked | Checked against `PROFILES` on load (`inputs.py:249-251`). |
| `costs.py:74-86` | Parallel-running months over 60 or negative give nonsense | Over 60 rejected (`inputs.py:150-151`); negatives rejected as counts (`validation.py:17-18`). |
| `evidence.py:93-94` | Software-list lower bound not marked as a lower bound | `is_lower_bound` is computed from partial coverage (`model.py:111-116`), which this finding has. |
| `evidence.py:45-48` | Partial measured yes/no discarded silently against an answer | Kept as an alternative (`evidence.py:108-113`) and flagged as a confirmation conflict (`status.py:182`), which prevents Ready. |
| `i18n.py:40` | Exposes a private file path | Backwards: a file name containing `@` is replaced by a generic label (`i18n.py:41-43`). |
| `i18n.py:38` | Unknown error code raises `KeyError` | Checked: every error code raised in `src/fazit/*.py` has a message in both `en.yaml` and `de.yaml`. |
| `i18n.py:61` | Missing label raises `KeyError` | Source and unit labels are checked when the catalogue loads (`catalogue.py:226-234`); collector labels fall back; the three collector statuses are in both locales. |
| `i18n.py:120` | Malformed date crashes | Every date is validated on load (`model.py:210-216`, `inputs.py:252`). |
| `i18n.py:123` | Malformed period crashes | Validated on load (`model.py:218-223`). |
| `inputs.py:87,94,253-256` | Omitted sample/invented flags present figures as real | By design: without the flags the figures are the organisation's own and are labelled as provided in `inputs.yaml`, not as measured. Nothing is invented. |
| `licences.py:178` | `product.key` can crash | `Product.key` returns `None` when either half is missing (`model.py:133-137`); the plans then count as unclassified, shown as unknown. |
| `licences.py:262` | `licences.coverage` may be `None` | Required and parsed on load (`model.py:145`, `495`). `_coverage_gap` accepts `None` only because it also serves optional finding coverage. |
| `licences.py:266` | Same, zero-product case | Same. |
| `licences.py:293` | Missing collection times treated as equal | `same_collection_time` returns `False` when either is missing (`model.py:68-71`). |
| `licences.py:302` | `missing_reason` alongside a measured value | The loader forbids a missing reason when a value is present (`model.py:347-361`). |
| `mappings.py:84-85` | Reference fields optional when they should be forbidden | Listing them lets the key appear; any non-null value is then rejected (`mappings.py:97-100`). |
| `model.py:206` | `optional=None` ignores optional fields | Intended: `None` means "allow unknown keys", which the wrapper counts and drops (D19). |
| `model.py:69` | Naive vs `Z` timestamps rejected by a length test | The length test only separates dates from date-times. Naive and aware times compare unequal, which makes the counts "not comparable", shown as unknown. That is conservative and correct. |
| `model.py:379-381` | Fails, then indexes `item["id"]` anyway | `Validator.fail` raises; nothing after it runs. |
| `model.py:352` | A "denied" collector is accepted | No such status exists; statuses are `ok`, `partial`, `skipped` (`model.py:15`). |
| `model.py:469` | Same for licences | Same. |
| `model.py:500-502` | Fails, then calls `value.get` anyway | `fail` raises. |
| `output.py:17-48` | Names differing only by case overwrite each other | The only names passed are fixed `scan-`, `inputs-` and `report-<date>-<lang>` names (`cli.py:113-119,167`). |
| `parsing.py:56-61` | Names without `@` get through | The scan format has only registered codes and counts; unknown fields are dropped (D19). The `@` check is a second net. |
| `parsing.py:143-147` | Floats skip the strict spelling check | No `inputs.yaml` field takes an unquoted number with decimals: amounts and training days must be quoted (`inputs.py:125-132`), and non-finite numbers are rejected (`parsing.py:145-146`). |
| `parsing.py:162-163` | Unquoted integer amounts not flagged | Rejected with the same "put it in quotation marks" message one step later (`inputs.py:130-131`), only without a line number. |
| `report.py:39-41` | Bad `generated_at` crashes | Validated on load (`model.py:505`, `210-216`). |
| `report.py:252` | Truthy non-yes/no values count as "yes" | Values are integers or yes/no only; for counts, positive means a need. |
| `report.py:308` | `by_id[item.id]` can raise `KeyError` | Every alternative's ID is in the combined findings (`evidence.py:104-113`, `report.py:217`). |
| `report.py:310` | Same | Same. |
| `risky_files.py:44-56` | Empty extension list accepted | `reader.rows` without `allow_empty` rejects it (`validation.py:44-46`). |
| `rules.py:18` | Rule files identified by base name only | The seven shipped rule files have distinct base names. |
| `status.py:261-274` | Disputed lower bound counts as a match | Matches here set a worse status, never Ready ("a partial count can confirm a positive finding", `DECISIONS.md`). Ready needs no gaps at all (`status.py:375`). |
| `status.py:200-206` | "Denied" collector treated as partial | No such status; the only non-ok, non-skipped status is `partial`. |
| `status.py:316-330` | Empty `when` fires a rule | `when: []` is rejected on load (`status.py:74`). |
| `status.py:346` | Missing `provided` treated as provided | `provided` is required and one of four values (`catalogue.py:128`). |
| `status.py:361` | Dispute ID missing from findings | Disputes are only created for IDs present (`status.py:177-179`). |
| `status.py:395` | Workload without a rule block | A block is required for every workload (`status.py:144-145`). |
| `validation.py:36` | Uses `required` twice, so optional fields are rejected | Misread: the line is `{*required, *optional}`. |
| `rules/findings.yaml:370` | `answer` missing from provided sources | `answer` is a way of supplying a finding (`catalogue.py:14`), not a source code. |
| `rules/mappings/generic.yaml:87` | `need_finding` on a count | Allowed for software-list counts and checked on load (`mappings.py:58-67`). |
| `rules/mappings/nextcloud.yaml:153` | Reference URL breaks the offline report | A citation link fetches nothing when the report opens. Principle 6 is about loaded resources. |
| `rules/mappings/opendesk.yaml:16` | `checked_on: 2026-11-21` is in the future | The model assumed today was 2026-06-22. The run was on 2026-11-22. |
| `rules/service_plans.yaml:2` | Microsoft Learn URL breaks the offline principle | A citation, never contacted. |
| `rules/service_plans.yaml:204-224` | Business Voice (US) lacks Phone System (`MCOEV`) | Microsoft lists only `MCOMEETADV` and `MCOPSTN1` for this product; the file matches. |
| `rules/service_plans.yaml:522` | E5 EEA (no Teams) with Calling Minutes has the wrong Power Automate tier | Microsoft lists `FLOW_O365_P1` for this product; the file matches. |
| `rules/service_plans.yaml:965-1001` | "No Teams" product lists Teams plans | `MCOEV` is Phone System and `MCOMEETADV` Audio Conferencing, not the Teams app (`TEAMS1`); Microsoft lists both for this product. |
| `rules/service_plans.yaml:1049-1085` | Same, 500-seat HUB variant | Same; matches Microsoft. |
| `rules/service_plans.yaml:1135-1162` | Same, without Audio Conferencing | Same; matches Microsoft. |
| `rules/service_plans.yaml:1324-1352` | Same, Office 365 E5 EEA | Same; matches Microsoft. |
| `rules/service_plans.yaml:1722` | Office 365 E1 wrongly includes Intune | `INTUNE_O365` is basic mobile device management for Office 365, which Microsoft lists for E1. Intune Plan 1 is `INTUNE_A`, which the file does not list for E1. |
| `rules/status.yaml:89-92,110` | Teams ready while add-on evidence is missing | Missing evidence becomes a "not in scan" gap (`status.py:221-222`), and any gap prevents Ready (`status.py:325-327,375`). |
| `rules/status.yaml:261-282` | Ready shadows the identity add-on rule | A fired rule decides first (`status.py:370-374`); Ready is only considered when none fired. |
| `templates/report.html.j2:89-91` | Non-ready row can get the ready reason | Needs-work and blocker always have a deciding rule, and Unknown always has a reason code (`status.py:278-292`). The last branch is reached only for Ready. |
| `templates/report.html.j2:400` | Evidence table loses its column labels on phones | Deliberate. The table has two columns, finding and value; stacked, the finding name sits above its value. Checked in the published sample report at 360 px. |
| `templates/report.html.j2:454` | `generated_at` may be missing or unrenderable | Required and validated on load. |
| `templates/report.html.j2:463` | `mapping.label[lang]` may be missing | Labels are checked as both English and German on load (`Validator.bilingual`), and the language is checked first. |
| `templates/report.html.j2:480` | Unknown finding with no missing reason | Unknown findings must carry a missing reason (`model.py:347-348`). Derived licence findings and unanswered questions set one (`licences.py:280,324-326`, `evidence.py:69`). |
| `templates/report.html.j2:496` | Product count date may be missing | Taken from `licences.collected_at`, which is required (`licences.py:277`). |
| `templates/report.html.j2:515` | Purchased/assigned may be missing | Required counts (`model.py:53`). |
| `templates/report.html.j2:518` | Plan list may be `None` | Built in code as a tuple from `classify_product`. |
| `templates/report.html.j2:522` | Workload or signal label may be missing | Workloads are checked on load; the two signals `add_on` and `bundled` have labels in both locales. |
| `templates/report.html.j2:598` | `target_costs` may be empty | Always the two scenarios, built in code (`report.py:341`). |
| `templates/report.html.j2:599` | `target_costs` may have only one entry | Same. |
| `templates/report.html.j2:629` | Missing subtotal breaks `data-amount` | `plain_amount(None)` returns `"unknown"` (`i18n.py:76-78`). |
| `templates/report.html.j2:638` | Missing total breaks `data-total` | Same. |
| `templates/report.html.j2:655` | Missing-input label may be absent | Paths come from `costs.py`; all 15 field names have labels in both locales. |
| `templates/report.html.j2:691` | `row.missing` may be `None` | Always a tuple (`status.py:369`). |
| `templates/report.html.j2:807` | Zero with no coverage shown as "none reported" | A measured finding must have coverage (`model.py:354`). No coverage means a provided answer, which counts as complete. Unknown findings have no value, so they never reach this branch. |
| `templates/report.html.j2:842` | Omitted `users` gives `Undefined` | `item` is a dataclass whose `users` defaults to `None`. |
| `templates/report.html.j2:845` | Omitted `vendor_has_web_version` gives `Undefined` | Same. |
| `templates/report.html.j2:928` | Missing `permissions_used` crashes | Required collector field (`model.py:36`). |

## How useful this was, compared with the frontier-model reviews

Much less useful. The two final frontier reviews (`01-FINAL-REVIEW-fable.md`, 14 findings; `01-FINAL-REVIEW-astra.md`, 20 findings) ran the tool and the tests. They fed it about fifty hand-made bad inputs, recomputed the cost totals by hand and read across files. They found real faults, for example an unlisted service plan turning every workload Unknown, and a 700-byte `inputs.yaml` that hangs the parser. This local review saw one file at a time and could not run anything. 77 of its 80 findings were false alarms, mostly checks it couldn't see because they live in another file, plus misreadings of the code and a wrong idea of today's date. Its one confirmed finding is harmless today. Checking its output took about as long as the run itself. Its value is narrower: it shows that a public model, run offline on ordinary hardware, found no fault in the code that the frontier reviews had missed, and checking its six licence-data claims confirmed that `service_plans.yaml` matches Microsoft's published list.

## Files in this folder

- `REVIEW.md`: this record.
- `prompt.txt`: the fixed prompt.
- `run_review.py`: sends the requests and records the answers (standard library only).
- `start_server.ps1`: the exact server command.
- `raw/*.txt`: the model's answer for each of the 35 requests, as returned.
- `raw/reasoning/*.txt`: the model's thinking for each request.
- `raw/run-log.jsonl`: time, finish reason and token counts per request.
