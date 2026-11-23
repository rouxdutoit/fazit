# Scan file format

Fazit reads inventory evidence from `scan.json` to build a local report. Today `fazit demo` writes a scan with simulated data. Fazit has no import command or live collection yet. Put the organisation's answers, costs and Windows-only applications in `inputs.yaml`. [Interview checklist](interview-checklist.md)

Use UTF-8 JSON up to 2 MiB. The format uses codes, counts and dates and has no fields for free text, person names or email addresses. Fazit rejects `@` in keys or string values and rejects duplicate JSON keys. It drops unrecognised fields and finding IDs and reports only how many it dropped.

## Scan fields

All top-level fields are required.

| Field | Value |
| --- | --- |
| `schema_version` | A string such as `"1.0"` with a major and minor version. Fazit accepts major version 1 and rejects other major versions. |
| `tool` | An object with `name` set to `"fazit"` and `version` set to the producer version, such as `"0.1.0"`. |
| `generated_at` | The date the scan was written or a timestamp with a UTC offset or `Z`. |
| `source_kind` | `sample` for fictional data, `import` for evidence supplied from outside Fazit, or `live` for live collection. A scan with a sample evidence source must use `sample`. |
| `collectors` | A list of collection records, which can be empty. |
| `findings` | A list of observations, which can be empty. |
| `licences` | A licence inventory or `null`. |

The catalogue lists finding IDs, workloads, types, units, collectors, sources, reason codes and permission codes. It defines which collector and source pairs a finding accepts. D31 describes the consistency checks for counts, dates and licences. [Finding catalogue](../src/fazit/rules/findings.yaml) · [Decisions log](../DECISIONS.md#2026-11-22--scan-consistency)

## Collectors

- `id` is a registered collection method. Use each collector ID once.
- `status` is `ok`, `partial` or `skipped`. For `ok`, omit `reason` or set it to `null`. For `partial` or `skipped`, give a registered reason code.
- `permissions_used` is a list of registered permission codes. Use an empty list if the method used none.

## Findings

Use each finding `id` once. Set `workload` and `unit` to the catalogue values, including `null` for a unitless finding. Give `value` as a JSON boolean or a non-negative integer, as specified by the finding type. Counts can be up to 999,999,999,999. A value in bytes can be up to 9,223,372,036,854,775,807.

All finding keys are required. The `provenance` determines which fields must have a value and which must be `null`.

| `provenance` | Required values | Fields set to `null` |
| --- | --- | --- |
| `measured` | `value`, `source`, `collected_at`, `coverage` and a `collector` with status `ok` or `partial`. | `missing_reason` |
| `provided` | `value` and a registered interview `source` for a finding that accepts supplied evidence. | `collector`, `coverage` and `missing_reason` |
| `unknown` | A registered `missing_reason`. You may include any collection details that are known. | `value` |

- If you supply a `collector`, its ID must appear in `collectors` and the catalogue must allow it for the finding. Any supplied `source` must be registered for that collector and finding. Without a collector, only findings that accept supplied evidence can name a source, and the source must be registered for supplied evidence. The codes `inputs_yaml` and `sample.inputs_yaml` belong to evidence read from the inputs file.
- Give `collected_at` as a date or a timestamp with a UTC offset or `Z`. A measurement without a reporting period requires the time of collection.
- Give `period` as `YYYY-MM-DD/YYYY-MM-DD`, or as `null` if there is no reporting period.
- Give `coverage` as an object when it applies. The next section describes its fields.

## Coverage

Set `kind` to `complete`, `partial` or `unknown`. The optional counts are `scanned` for successful checks, `failed` for failed checks and `total` for the population in scope. Use non-negative integers or leave a count unspecified. D31 explains when counts establish complete coverage and how they constrain findings.

## Licences

An inventory needs a `collector` of `licences` with status `ok` or `partial`, a registered licence `source`, a timestamp in `collected_at` and a `coverage` object. Use `products` for the list of observed products. Complete coverage requires a successful check for every product and zero failures, including when the list is empty.

Each product requires non-negative integer counts for `purchased` and `assigned`. It can also supply `sku_part_number`, `sku_guid` and a `service_plans` list. The identifier fields may be `null`. Each service plan has the keys `name` and `guid`, with `null` allowed if an identifier is unavailable. The catalogue lists the exceptions to the identifier format for product codes and service-plan names. [Finding catalogue](../src/fazit/rules/findings.yaml)

## Minimal example

This scan records one interview answer and one finding whose value is unknown. Save the example as `scan.json` and run `fazit report scan.json --out report`.

```json
{
  "schema_version": "1.0",
  "tool": {
    "name": "fazit",
    "version": "0.1.0"
  },
  "generated_at": "2026-11-02T09:00:00Z",
  "source_kind": "import",
  "collectors": [],
  "findings": [
    {
      "id": "directory.user_count",
      "workload": "directory",
      "value": null,
      "unit": "users",
      "provenance": "unknown",
      "collector": null,
      "source": null,
      "collected_at": null,
      "period": null,
      "coverage": null,
      "missing_reason": "not_collected_in_this_version"
    },
    {
      "id": "telephony.in_use",
      "workload": "telephony",
      "value": true,
      "unit": null,
      "provenance": "provided",
      "collector": null,
      "source": "interview",
      "collected_at": "2026-11-02",
      "period": null,
      "coverage": null,
      "missing_reason": null
    }
  ],
  "licences": null
}
```
