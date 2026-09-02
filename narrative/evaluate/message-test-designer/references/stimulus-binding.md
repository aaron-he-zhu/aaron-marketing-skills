# Narrative Truth, Stimulus, and Retro Binding

Use this profile when a narrative truth enters canon, a canon message becomes a test stimulus, or a result informs a drift/reversion decision. Shared artifact semantics remain in the root protocols; this file defines Narrative-specific fields.

## Truth observation and canon binding

Decision-critical truth fields retain `claim_id`, `stage_scope`, `source_ref`, `observed_at`, `window`, evidence label, conflict group, and missing reason. Preserve conflicting evidence. A stale or unresolved differentiator cannot enter canon as confirmed truth.

Every canon-dependent artifact binds:

```yaml
canon_id: <stable canon id>
canon_version: <immutable version>
canon_sha256: <exact canon hash>
current_head_ref: <selected non-forked canon head>
supersedes: <prior canon ref, if any>
```

## Stimulus and result binding

Every message test records `test_ref`, exact `stimulus_set_ref` and `stimulus_sha256`, canon binding, panel/cohort definition, protocol, measurement-contract ref/hash, primary metric, pass/stop rule, decision owner, start/stop/read dates, and current head. Results must reference that exact binding. A changed canon, stimulus, panel, protocol, or measurement contract starts a new test; it cannot validate the previous target.

Use the shared control semantics directly:

| Narrative meaning | Shared artifact |
|---|---|
| Locked test design, target/stimulus binding, population/panel, metric, dates, and precommitted rule | `measurement-contract` |
| Result source, observed window, sample/completion state, calculated effects, guardrails, and applied-rule evidence | `evidence-observation`, targeting the exact test/stimulus binding and citing versioned source bindings |
| Retain/retest/reversion proposal after the fixed read | `cycle-retro`, bound to that contract and result observation |

Do not create or name a Narrative “result receipt.” A measurement result is not an `action-receipt`. Narrative evaluation does not publish, send, or spend; if a separate executor performs an external action, its `action-intent`/`action-receipt` pair remains separate from the result observation and grants no permission.

## Narrative Cycle Retro

The retro references the current canon/test binding, exact result `evidence-observation`, fixed measurement contract, and relevant resonance/drift evidence. Allowed Narrative decisions are `retain`, `retest`, `reversion-proposal`, or `unknown`. A reversion remains a proposal for the narrative registry and preserves the supersedes chain. Without the matching result observation and contract, never call a message validated. Keep hypotheses separate and give them zero weight in the current decision.
