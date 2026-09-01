# Launch Action Control

Use this control for a launch manifest and every launch-day action that can change an external surface. It specializes the shared state and receipt rules for launch operations; it does not replace the launch registry or the RAMP gate.

## Frozen manifest

Bind a launch package with `launch_ref`, `manifest_version`, `manifest_hash`, dependency offsets, `frozen_at`, and optional `supersedes`. Any asset, claim, destination, owner, or channel change produces a new manifest version. A SHIP verdict is valid only for the exact manifest hash it audited.

## Three separate records

- **SHIP verdict**: the RAMP gate's eligibility decision for one manifest version. It is neither permission to act nor evidence that an action occurred.
- **Action intent**: one exact irreversible operation with action ID, type, target, payload/manifest hash, owner, scheduled time, observation window, kill criteria, and rollback route.
- **Action receipt**: evidence returned or captured after that exact action is attempted: stable provider-operation or evidence ref, attempted/completed time, `succeeded | partial | failed | unknown`, accepted/rejected scope, and a bound domain evidence record. The domain record may preserve a live URL; the shared locator-free envelope carries only its ref and digest. A rollback is an `operation: rollback` action; `rolled_back` is not a receipt status.

Every irreversible action gets its own intent and its own receipt. A dry run, runbook row, registry proposal, SHIP verdict, or operator assertion without evidence is not a receipt. A rollback is a new action with its own receipt; it does not rewrite the original receipt.

## Lane joins and closeout

The current manifest declares the required action IDs for each lane. A lane is complete only when every required action has a terminal receipt matching the current manifest hash. Missing or `partial | unknown` receipts keep the lane and launch join `OPEN`; do not infer completion from a live URL, dashboard total, later snapshot, or another lane's success.

Monitoring binds snapshots to the manifest, action receipts, and predeclared measurement contract. The retro consumes those bound records. Facts worthy of long-term truth still travel as launch-registry proposals; receipts remain operational evidence and do not become registry truth by themselves.
