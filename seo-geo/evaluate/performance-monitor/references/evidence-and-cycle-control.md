# SEO/GEO Evidence and Cycle Control Profile

Use this profile for query/SERP observations, page-change measurement, index-submission receipts, and SEO/GEO retros. Shared artifact semantics remain in the root protocols; this file defines the domain binding.

## Search observation

Each query or SERP fact carries:

```yaml
query: <query text>
locale: <market/locale>
language: <language>
device: <desktop|mobile|other>
engine: <engine or answer surface>
serp_snapshot_ref: <snapshot or export ref>
result_ref: <stable result ref; keep the observed URL in the domain evidence record>
field: <rank|feature|volume|difficulty|clicks|impressions|ctr|position|citation>
value: <value>
source_ref: <provider/export ref>
observed_at: <ISO-8601 timestamp>
window: <start/end when aggregated>
label: <Measured|User-provided|Calculated|Estimated|Proxy|Unknown>
conflict_group: <optional ref>
missing_reason: <required when Unknown>
```

URL, domain, and query are ordinary search evidence, not PII by default. Preserve them in the SEO/GEO domain evidence record. The shared locator-free control artifact references that record by stable ref and digest rather than copying the URL into the envelope. Preserve source disagreement. A stale observation or locale/language/device/engine mismatch yields `NEEDS_REFRESH`; it must not be blended into a current comparison. An attention proxy never becomes search volume, and missing decision-critical difficulty inputs produce `NOT_SCORED`, not a partial score.

## Page and measurement binding

Every outcome claim binds `page_ref`, `content_version`, `content_sha256`, `change_ref`, `measurement_contract_ref`, its exact hash, baseline/candidate/control windows, truth source, and current non-forked head. A later edit supersedes the binding and starts a new readback window. Post-hoc windows are labeled `reconstructed` and cannot be presented as preregistered.

## Index intent and receipt

An index intent binds an immutable target spec containing the exact URL, engine, method, and content hash. The shared control artifact carries the target-spec ref and digest, not the raw URL. An index receipt exists only after an authorized live call returns the provider/HTTP response; it records the intent ref, target-spec/page ref, content hash, executed time, provider/request ref, status, and a bound evidence record containing the URL and response. A dry-run, generated request body, URL list, or absence of an error is not a receipt and must not be described as submitted.

## Cycle Retro

The SEO/GEO retro references the current page/change binding, measurement contract, control, fixed readback window, and any applicable index receipt. Decisions are `Promote`, `Keep-testing`, `Rollback`, or `Unproven`. Reports consume the computed readback artifact and do not recompute ratios or silently change the window. Hypotheses are future inputs with zero weight in the current decision.
