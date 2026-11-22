# Brief: a local open-weights review of Fazit

Written on 2026-11-22 for a Claude Code session on the founder's Windows computer. Give this whole file to that session as its task.

## Background

Fazit (github.com/rouxdutoit/fazit) is a free AGPL-3.0 Python command-line tool. It writes one offline HTML report on what moving an organisation off Microsoft 365 would take. The founder designs and directs it and does not write code, so explain things in plain product terms. Claude and Codex write the code, and frontier models review it before each release. Those records are in `.planning/phases/01-demo-and-report` and `.planning/research/launch-critique/`.

The founder wants one more review from an open model running on their own computer. The point is a review anyone can repeat offline with public weights, from a model family different from the ones that wrote the code. It is not a quality credential, and nothing about it goes on the website: two critic reviews warned that a list of models reads like a spec sheet and that "LLMs reviewing LLMs is not review".

## The computer

- AMD Ryzen 7 9800X3D, 32 GB RAM, NVIDIA RTX 5080 with 16 GB of graphics memory, Windows.
- About 459 GB of 932 GB disk free.
- Check first whether a model runner (Ollama, LM Studio, llama.cpp) is already installed, and whether the Fazit repository is already cloned. If it is not, clone it; Git and uv are the only tools Fazit itself needs.

## The task

Review Fazit's source code with one local model. Report findings. Change no code.

1. **Use LM Studio and Qwen3.8 27B, and ask before downloading.**
   - The founder chose LM Studio as the runner. Its catalogue was checked on 2026-11-22.
   - Model: `qwen/qwen3.8-27b`, 16.10 GB download, Apache-2.0, a dense 27B model with reasoning and a 262K-token context. It was the strongest open-licensed local coding model in the catalogue that this computer can run. Its benchmark figures are the maker's own.
   - It does not fit entirely in 16 GB of graphics memory once context is added, so LM Studio will place a few layers in system memory. Set the context to about 16,000 to 32,000 tokens and offload as many layers to the card as fit. If it is too slow, try a smaller quantisation of the same model before switching models.
   - Fallback that fits fully on the card: `gpt-oss` 20B (Apache-2.0), older and weaker.
   - Not these: Gemma and Meta's models (own licence terms), and anything marked Cloud (it leaves the computer).
   - Drive it through LM Studio's local server on localhost, or the `lms` command line.
   - Before any download or install, tell the founder the exact name, source, size on disk and licence of the runner and of the model. Wait for a clear yes.
   - Install only from the runner's official source. If an installer needs administrator rights, the founder runs it.

2. **Review file by file.**
   - `src/` is 42 files and about 360 KB, too much for one request. Send one file, or one small group of related files, per request.
   - Use one fixed prompt. Ask for concrete faults: bugs, unhandled inputs, and places where behaviour contradicts the comments or the principles at the top of `DECISIONS.md` (read-only, local, honest figures, unknown stays unknown).
   - Cover the Python files in `src/fazit/` and the rule files in `src/fazit/rules/`.
   - Keep the runner bound to localhost. Long runs go in the background.

3. **Triage honestly.**
   - A model this size raises false alarms. Check every finding against the code yourself.
   - Sort into confirmed, plausible and wrong, each with file and line.
   - Fix nothing.

4. **Write the record** in `.planning/research/local-model-review/`:
   - `REVIEW.md`: model name, exact version or file hash, licence, runner version, the prompt, the steps to repeat the run, the count of raw findings, and the triaged findings.
   - The raw output files beside it.
   - One plain paragraph on how useful this review was compared with the existing frontier-model reviews.

## Rules

- Touch only `.planning/research/local-model-review/`. Do not edit `site/`, `src/` or any other existing file.
- Do not commit or push unless the founder tells you to. If they do: `git commit -s -m "..." -- <paths>` with explicit paths, never `git add -A` or `git commit -a`, and never `drafts/` or `grants/`.
- Other sessions work in this repository on another computer. Pull before you start.

## Done means

The founder approved the downloads, the review ran over all of `src/fazit/`, and `REVIEW.md` holds the triaged findings and the steps to repeat the run. End with a short summary of the confirmed findings and whether this review is worth repeating before each release.
