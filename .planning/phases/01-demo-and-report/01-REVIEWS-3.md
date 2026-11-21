**Verdict — NOT READY**

| Findings | Gate result |
|---|---|
| 13, 01 | Resolved. Town mail and premium Power Platform show `Needs work` with the missing evidence listed. An unanswered phone-replacement question gives `Unknown`. |
| 14, 05 | Resolved for the reported cases. Failed items preclude complete coverage, partial storage cannot establish `Ready`, and a partial measured zero cannot override a complete positive answer. |
| 15, 06 | Resolved. D‑68 classifies SKU and service-plan pairs, assigns Audio Conferencing to meetings, and requires explicit confirmation to clear telephony. |
| 16, 02 | **Not resolved.** A person’s name or token without `@` can still reach the default report through either free-text field. The privacy test exempts both. |
| 17 | **Not resolved.** D‑70 rejects duplicates, but a populated licence block can still name `licences` when that collector was skipped. |
| 18, 03 | Resolved within D‑71’s accepted scope. All three destinations use the same writer and each gets an outside-file preservation test. |
| 19 | Resolved. The mixed Windows case shows `Blocker`, marked incomplete, with one confirmed application and one unanswered entry. |
| 20 | Resolved. Each gap has its own source and check date, and local need is assessed separately. |
| 21 | Resolved. The CLI test changes rule severity and checks the rendered status. Checksums cover the bytes actually parsed. |
| 22, 12 | Resolved. The installed-wheel test records socket and DNS audit events, including a deliberately caught attempt. |
| 10 | Resolved. The sample header identifies simulated measurements, and mixed tables label each row’s origin. |

**Blocking corrections**

- **D‑66/D‑67.** The reverse of finding 14 still fails. If a partial scan confirms one affected item and a provided answer says zero for the same population and period, D‑67 lets zero decide and can yield `Ready`. Preserve the confirmed lower bound and test that conflict. [D‑67](/home/roux/Documents/open/.planning/phases/01-demo-and-report/01-CONTEXT.md:193)
- **D‑69.** Use neutral labels by default and include the organisation and software fields in the privacy test. Escaping preserves the identifying text. [Privacy requirement](/home/roux/Documents/open/.planning/REQUIREMENTS.md:50)
- **D‑70.** Apply the measured-finding eligibility check to the licence block itself. Reject populated blocks when the `licences` collector is absent or skipped. [Plan 01‑01](/home/roux/Documents/open/.planning/phases/01-demo-and-report/01-01-PLAN.md:203)

**D‑71.** Yes, I accept omitting directory pinning for a local run where the invoking user controls the output directory and its parent throughout publication.