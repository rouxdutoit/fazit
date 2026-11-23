---
created: 2026-11-23
source: release review round 1, R-42 / A-15 (Codex GPT-6.2-Astra); confirmed deferrable by both reviewers
severity: medium
area: output
---

# A failed demo refresh can leave a mixed set of files

If the second of three demo replacements fails, the new scan sits beside the old inputs and report. Each file stays whole and the failure is reported. Restore the previous set on a handled replacement failure, or write each run to its own directory.

## Done

2026-11-23. A handled replacement failure restores the previous contents and removes any files created by the failed refresh. Tests cover existing, partly existing and fresh output sets through both filesystem paths. If the filesystem refuses restoration too, Fazit reports it and retains the saved copy.
