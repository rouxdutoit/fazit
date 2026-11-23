---
created: 2026-11-23
source: release review round 1, R-41 / A-14 (Codex GPT-6.2-Astra); confirmed deferrable by both reviewers
severity: medium
area: output
---

# Output writes look the directory up by name again

`output.py` resolves `--out` and later stages, replaces and cleans up by path. Another writer that controls an ancestor of the output directory could redirect those operations. Needs an attacker with write access to the user's path. Anchor writes to an opened directory handle where the platform allows it.

## Done

2026-11-23. On platforms with directory-relative filesystem operations, Fazit opens the resolved path without following new links and uses the open directory for destination checks, staging, replacement and cleanup. Tests move an ancestor during both a successful write and a failed stage. Platforms without directory handles use the resolved-path fallback.
