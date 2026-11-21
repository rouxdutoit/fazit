# Security

## Report a vulnerability

Use GitHub's private vulnerability reporting for `rouxdutoit/befund`. [Report a vulnerability](https://github.com/rouxdutoit/befund/security/advisories/new)

If the form is unavailable, send the report by email. [hello@rouxdutoit.com](mailto:hello@rouxdutoit.com)

Keep the report private and use fictional examples in place of a real scan file or assessment report.

## Safeguards

This version runs locally and contains no network code. It contacts no host.

1. **Read-only.** Live collection will request read permissions and use an explicit allowlist of read requests. Requests that can make changes are excluded, even if they use `GET`.
2. **Local processing.** Scan data stays on the computer. The only hosts live collection may contact are `login.microsoftonline.com` and `graph.microsoft.com`.
3. **Tokens in memory.** Access and refresh tokens will stay in memory when sign-in is added.
4. **Counts and sizes.** Collection is limited to counts, sizes and coded evidence. Mail bodies and file contents are outside its scope.
5. **Privacy by construction.** Collected data contains no free text. The scan format holds aggregates and coded evidence, with no fields for person names or email addresses. Unrecognised fields are discarded. The appendix gives their count. The only free text from input data that can appear in the report is the organisation name and the names of Windows-only applications. Both come from text entered in `inputs.yaml` and are shown as entered.
6. **Offline report.** The HTML is self-contained and opens and prints with the network disconnected.
7. **One command.** After setup, `demo` builds the report from sample data with one command. `report` rebuilds it from an existing scan file.
8. **Honest numbers.** The report labels evidence and prices by their origin. Missing values stay unknown. A skipped collector never makes an area look more ready.

Browsers may add the local file path to printed headers and footers. Turn off **Headers and footers** in the browser's print settings and check the preview for the file path before sharing a PDF.

Tests enforce the safeguards for this version, including privacy, local operation, the offline HTML, output boundaries and honest figures. The host, endpoint and token safeguards will be tested when live collection is added. [Privacy tests](tests/test_privacy.py), [repository tests](tests/test_repo_basics.py), [installed package tests](tests/test_installed_package.py), [report tests](tests/test_report.py), [CLI tests](tests/test_cli.py), [output tests](tests/test_output.py), [cost tests](tests/test_costs.py), [rule tests](tests/test_rules.py)
