---
created: 2026-11-23
source: release review rounds 6 to 11, both reviewers (F6-01)
severity: low
area: licences
---

# Licence names outside the identifier pattern are refused

All 620 products in Microsoft's current licensing reference load, but a product code or plan name outside the pattern that Microsoft publishes later is refused; written as null it loads. Drop an unfit name and keep the GUID instead of refusing the scan. Matters once import reads real tenants (IMPT-06).
