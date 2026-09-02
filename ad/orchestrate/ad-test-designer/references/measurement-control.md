# Paid Measurement Control Profile

Use this profile when paid-ad evidence, a test, or a shipped-change readback must bind to the exact campaign state that produced it. The shared artifact semantics live in the root skill, state, measurement, and runtime protocols; this file supplies only Paid Ads fields and fail-closed rules.

## Evidence observation

For each decision-critical field retain:

```yaml
account_ref: <stable opaque account ref>
campaign_ref: <stable campaign ref>
adset_ref: <stable ad-set or asset-group ref, if applicable>
creative_ref: <stable creative ref, if applicable>
field: <metric or fact name>
value: <observed value>
source_ref: <export or provider-response ref>
observed_at: <ISO-8601 timestamp>
window: <start/end>
platform: <platform>
attribution_window: <declared window>
currency: <ISO-4217 code, when monetary>
timezone: <IANA timezone>
label: <Measured|User-provided|Calculated|Estimated|Proxy|Unknown>
conflict_group: <optional ref>
missing_reason: <required when Unknown>
```

Preserve conflicting provider and truth-set values as separate observations. Missing source, timestamp, attribution window, currency, or timezone on an applicable comparison makes the affected result `NEEDS_INPUT/UNDECIDED/NOT_SCORED`; it is never silently imputed.

## Test and change binding

Bind every design and readback to:

```yaml
test_ref: <stable test or change ref>
control_ref: <unchanged control or holdout>
candidate_ref: <candidate campaign/ad set/page>
variant_sha256: <exact creative or landing artifact hash>
measurement_contract_ref: <immutable contract ref>
measurement_contract_sha256: <exact contract hash>
signal_spec_ref: <conversion/UTM specification ref>
current_head_ref: <selected non-forked head>
supersedes: <prior binding, if any>
```

Do not read out a test when the live variant, signal specification, or measurement-contract hash differs from the bound value. A changed binding starts a new test/readback; it does not amend the old result.

## Readback and retro

A paid Cycle Retro references the current binding, normalized evidence observations, fixed-window measurement contract, control, and — only when a real executor changed a platform — its action receipt. Allowed paid decisions are `Promote`, `Keep-testing`, `Rollback`, or `Unproven`. If no verified execution receipt exists, describe the change as user-reported or recommended and never manufacture one. Keep hypotheses separate from evidence and give them zero weight in the current decision.

## External-action boundary

Campaign planning, QA, analysis, triggers, and recommendations are not platform mutations. Emit an action receipt only after an authorized live connector returns a provider result for the exact target and payload hash; dashboards, plans, dry-runs, gate verdicts, and proposed budget changes are not receipts.
