# Bounded Workflow Loop Protocol

Use this runtime when a named workflow needs deterministic, recoverable execution across skills. It implements the sequence **objective + hypothesis + success criteria → action → independent verification → decision → memory proposal → terminal**.

## Authority boundary

This runtime is not a new truth ledger.

- A plan can start only under an existing `scripts/run-events.py` run. Plan creation holds that run's coordinator lock from the current-head read through the durable `plan.json` replacement. The immutable `evidence_cutoff` is therefore the exact protected selected head (event ID, hash, offset, and timestamps), not a best-effort observation vulnerable to an append race. `created_at` cannot precede that head's `occurred_at`.
- Every completed or failed action must cite a selected-ancestry event whose offset is strictly after `plan.evidence_cutoff.offset` and whose runtime-assigned `recorded_at` is at or after the cutoff's `recorded_at`, with a route matching that action's graph node. A completion must cite a successful typed action event; a failure must cite a failed `turn_finished` event. Verification, decision, and terminal run-event evidence has the same offset-and-recorded-time freshness rule. Caller-supplied `occurred_at` remains descriptive business time and never establishes freshness or approval validity.
- When an outgoing edge requires `action-receipt` as successful completion evidence, every cited, qualifying receipt must have business status `succeeded`. Validation success alone is insufficient, and mixing a successful receipt with `failed`, `partial`, or `unknown` receipts cannot release the edge. Those receipts remain valid operational records for monitoring, failure handling, and retrospective analysis; they do not establish successful `action-completed` transitions in this runtime.
- Each `action-completed` consumes its cited workflow/run-event references, one normalized identity for every direct or nested evidence binding, and each validated control artifact's exact binding, logical `kind + artifact_id`, and content digest for the lifetime of the run. The run coordinator replays one ledger across at most 32 workflow loops before any loop-local append or verification. Opening another loop, rewrapping direct evidence in a new run event, unwrapping nested evidence, relabeling its kind, or copying/renaming a control file cannot mint a new use. A `revise` decision may reset the frontier, but it never makes an earlier receipt, measurement, artifact validation, or ordinary action event reusable. Only an identical idempotency retry deduplicates to the already stored event; a new key must cite new qualifying evidence. Append recovery and `verify` replay the same run-scoped consumption check under the global lock order `run coordinator → workflow lock`.
- Every success criterion names its validator. Verification must cite a post-plan, selected-ancestry `artifact_validated` event whose typed validator matches that criterion; a loop cannot converge from its own assertion or a sibling branch.
- A gate-release action is stricter than ordinary completion. `launch-readiness-auditor → launch-day-conductor` opens only when its action evidence binds both (1) a canonical `validate-audit-artifact`-clean RAMP artifact in `memory/audits/launch/` whose accepted verdict is `SHIP`, and (2) a later, distinct `artifact_validated` event that references a validator-clean, host-signed execution-approval artifact. The signed record binds the exact run, loop, successor action, audit path and digest, validity window, key ID, and nonce. The runtime verifies RS256 against the immutable plan's externally pinned trust-anchor digest and consumes the nonce on success. `FIX`, `BLOCK`, `UNDECIDED`, malformed artifacts, missing or expired approvals, signature/binding failures, trust-anchor drift, and replayed nonces keep the successor closed.
- A run event's `actor.type`, status, reason code, or tool name is attribution metadata only. None of those caller-supplied fields grants approval authority; in particular, a self-reported `user` or `host` event cannot release a gate.
- Files under `memory/runs/<run-id>/workflow-plans/<loop-id>/` are private, non-authoritative operational evidence. The event stream is append-only; `state.json` is only a rebuildable projection.
- A memory result must be an immutable artifact with `proposal_only: true` and a named owning registry. It has no authority until the existing registry proposal/acceptance protocol accepts it.

The runtime stores no prompt, model transcript, or unbounded tool payload. Store only opaque IDs, reason/finding codes, and exact references with SHA-256 digests.

## Files

Each loop stores:

| File | Role |
|---|---|
| `plan.json` | Immutable snapshot of the objective, hypothesis, typed success criteria, graph digest, selected workflow, selected edge definitions, deadline, budgets, coordinator-protected evidence cutoff, and optional approval trust-anchor digest |
| `events.ndjson` | Non-authoritative append-only, hash-chained transition evidence; each stored event carries a runtime-assigned, strictly increasing `recorded_at` covered by its event hash |
| `state.json` | Deterministic projection rebuilt from `plan.json` and `events.ndjson`, including consumed execution-approval nonces and the last recorded persistence time |

The JSON contracts are `workflow-loop-plan.schema.json`, `workflow-loop-event.schema.json`, `workflow-loop-state.schema.json`, and `workflow-loop-request.schema.json`.

Gate-enabled workflows additionally use `workflow-execution-approval.schema.json` and `workflow-execution-approval-trust.schema.json`. Approval artifacts live only at their canonical private path, `memory/runs/<run-id>/approvals/<approval-id>.json`.

## Execution-approval trust boundary

Before creating or verifying a gate-enabled plan, the host must provide both variables below from outside the agent-controlled repository:

```bash
export AARON_WORKFLOW_APPROVAL_TRUST_ANCHOR=/absolute/host/path/workflow-approval-trust.json
export AARON_WORKFLOW_APPROVAL_TRUST_ANCHOR_SHA256=<64-lowercase-hex-digest>
```

The trust-anchor file is a bounded, single-link regular file outside the repository and contains only a public RS256 key (`key_id`, 2048–4096-bit modulus, exponent 65537) plus its validity window. The separately supplied SHA-256 digest pins its exact bytes; the resulting key ID, algorithm, and anchor digest are copied into the immutable plan. Missing configuration or later file/digest/key drift fails closed.

The private signing key must remain in a host-owned signer or secret boundary that the agent cannot read or invoke with arbitrary claims. The host signs canonical JSON containing every approval field except `signature`; the runtime never accepts a request actor string as a substitute. An approval is valid only after its bound audit, for at most 24 hours, within the trust anchor's validity, and for the exact successor action. Audit and approval order use their runtime-assigned run-event `recorded_at`; the first action append uses the workflow runtime's newly assigned `recorded_at` and requires it to fall inside the signed window. A backfilled `occurred_at` cannot revive an expired approval. Replay and `verify` reuse the persisted recorded times rather than the current clock, so a historically valid action does not become invalid merely because it is verified later. A nonce is single-use for the lifetime of the loop, including revised cycles.

## CLI and Python API

```bash
python3 scripts/workflow-loop.py plan --root . --request plan-request.json
python3 scripts/workflow-loop.py advance --root . --request advance-request.json
python3 scripts/workflow-loop.py verify --root . --run-id <uuid> --loop-id <id>
python3 scripts/workflow-loop.py verify --root . --run-id <uuid> --loop-id <id> --repair-projection
```

You can import the same behavior without invoking a subprocess:

```python
from scripts.workflow_loop import advance, plan, verify
```

`plan(root, request)` returns the planned event and projected state. `advance(root, request)` appends exactly one typed transition. `verify(root, run_id, loop_id, repair_projection=False)` verifies the run anchor, plan digest, event hashes, evidence hashes, transition replay, and projection.

## Plan request

```json
{
  "schema_version": "1.0",
  "run_id": "00000000-0000-4000-8000-000000000000",
  "loop_id": "launch-execution-1",
  "workflow_id": "product-launch-execution",
  "idempotency_key": "plan-v1",
  "occurred_at": "2026-07-22T10:00:00Z",
  "objective": "Execute the approved launch and preserve verified outcome evidence.",
  "hypothesis": "All required launch lanes can produce independently validated evidence.",
  "success_criteria": [
    {
      "id": "launch-proof",
      "description": "The joined launch outcome artifact passes independent validation.",
      "evidence_kind": "artifact-validation",
      "validator": "launch-outcome-verifier"
    }
  ],
  "run_event_anchor": {
    "kind": "run-event",
    "ref": "00000000-0000-4000-8000-000000000001",
    "sha256": "<64 lowercase hex characters>"
  }
}
```

The workflow's committed deadline and budgets are applied automatically. Transport retry uses the identical request and idempotency key. Action retries are a separate, explicitly bounded budget and never increment the outer verification cycle.

## Advance request

Every advance uses compare-and-swap against the current event head:

```json
{
  "schema_version": "1.0",
  "run_id": "00000000-0000-4000-8000-000000000000",
  "loop_id": "launch-execution-1",
  "workflow_id": "product-launch-execution",
  "idempotency_key": "asset-packaged-v1",
  "event_type": "action-completed",
  "occurred_at": "2026-07-22T10:05:00Z",
  "expected_head_sha256": "<current workflow event hash>",
  "payload": {
    "node": "launch-asset-packager",
    "evidence": [
      {
        "kind": "run-event",
        "ref": "00000000-0000-4000-8000-000000000001",
        "sha256": "<exact run event hash>"
      }
    ]
  }
}
```

The other payloads are:

| Event | Required payload |
|---|---|
| `action-completed` | `node`, route-matched evidence, and, for a release-gate source only, `gate_approval` with the canonical signed artifact reference, digest, and nonce |
| `action-failed` | `node`, stable `failure_code`, boolean `retryable`, and route-matched failed-action evidence |
| `verification-recorded` | Derived `result`, stable `finding_codes`, and exactly one typed result for every planned criterion, each with validator evidence |
| `decision-recorded` | `decision` (`accept`, `revise`, `escalate`, `wait`, or `abort`), `reason_codes`, and selected-ancestry evidence |
| `memory-proposal-recorded` | `target_registry`, `proposal_only: true`, a hashed artifact `proposal`, and `reason_codes` |
| `terminal-recorded` | `outcome` (`converged`, `waiting`, `exhausted`, `escalated`, `failed`, or `aborted`), `reason_codes`, and selected-ancestry evidence |

## Execution behavior

- The projected `frontier` is the only set of actions you may complete. A fan-out exposes all branch starts. An all-required join remains hidden until each declared predecessor is complete.
- A release gate adds its successor to the frontier only after the validator-clean `SHIP` and trusted signed execution-approval evidence both pass; a merely succeeded auditor action or self-asserted actor identity never opens the gate.
- Completing all workflow terminal nodes moves the loop to verification.
- A passing verification may be accepted. Acceptance requires a proposal-only memory artifact before `converged` is legal.
- A failed or inconclusive verification may be revised if a cycle remains. Revision resets the action frontier and increments the cycle.
- Revision or a new loop does not reset the run-scoped action-evidence consumption ledger; every repeated node must produce new qualifying evidence and any newly required control artifacts for that cycle.
- A retryable action failure leaves that node in the frontier only while the independent `max_retries` budget remains. A permanent or retry-exhausted branch failure applies the join's fail-closed policy.
- Repeating the same non-passing result and finding-code signature reaches the stall limit and requires escalation.
- The committed maximum cycle count is at most three. Deadline, event, action, retry, verification, memory-proposal, and stall limits cannot be widened by an advance request.
- One event slot is always reserved for `terminal-recorded`. Once normal work reaches the reserved slot, only a terminal exhaustion event may be appended.

## Idempotency, recovery, and verification

Each event ID is deterministic from the run ID, loop ID, and idempotency key. The runtime checks an existing idempotency key before checking a stale expected head, so an identical retry safely deduplicates after a timeout. Reusing a key with different content fails.

On the first append only, the runtime assigns the workflow event's UTC `recorded_at`, requires it to be strictly later than the stored head, includes it in `event_hash`, and then evaluates any gate approval against that persistence time. An idempotent retry reuses the already stored timestamp. Replay rejects missing, modified, or non-monotonic recorded times even if an attacker recomputes later public hash fields.

The event line is flushed before `state.json` is replaced. If projection installation fails after the append, the error contains `event_committed=true`. Retry the exact request and key; the runtime detects the committed event and rebuilds the projection without appending a duplicate.

`verify` fails on plan tampering, event-chain tampering, a stale or missing state projection, a missing or non-selected run-event anchor, a sibling/mismatched action route, a mismatched validator, changed or cross-action-reused evidence/control identity, approval signature/binding/replay failure, or trust-anchor drift. Use `--repair-projection` only for a projection mismatch: it replays the valid immutable plan and event stream; it does not repair or ignore broken evidence.
