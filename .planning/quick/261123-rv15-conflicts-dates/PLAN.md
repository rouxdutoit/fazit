---
quick_id: 261123-rv15
slug: conflicts-dates
date: 2026-11-23
status: planned
---

# Quick task: round-9 items both reviewers agree on

Round 9 (`.planning/quick/261122-rev-release-review/REVIEW-astra-9.md`, `REVIEW-fable-9.md`). Each item is a test that fails first.

1. **No Directory Ready beside a flagged conflict (both).** When the report flags a contradiction between licence evidence and the declared census (two assignments on one user SKU against one declared account), Directory is not Ready and the report does not say "there are no guest accounts". Use the existing conflict reason.
2. **Joint counts (Astra).** Inside a declared census, internal and guest accounts together fit within the successful checks plus the rows not checked: one success and one failure cannot yield one internal account and one guest from that single success. Enumerate small censuses against an independent oracle and require that every truthful roster still loads.
3. **Dates by the earliest time zone (both).** A date-only value names a calendar day. It is valid for a scan if that day has begun somewhere on Earth by the scan's instant, that is if the scan instant is at or after 00:00 on that day at UTC+14. Replace the one-day allowance with this rule, in D31 too. Cases: at 00:00Z on 5 November, an interview dated 6 November is refused; a scan written at 20:05-05:00 accepts its interview of that local date; one instant gives one answer whatever offset it is written in.

## Done means

The "Done means" list in `AGENTS.md`, the deep simulation profile, `uv run python site/check_site.py`, and the truthful-tenant property loading every generated truthful scan.
