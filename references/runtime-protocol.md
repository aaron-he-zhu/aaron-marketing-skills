# Runtime Protocol v1

This protocol makes one agent run explainable and resumable without creating another truth registry. [`run-event.schema.json`](run-event.schema.json), [`turn-snapshot.schema.json`](turn-snapshot.schema.json), [`save-point.schema.json`](save-point.schema.json), and [`run-envelope.schema.json`](run-envelope.schema.json) define portable document shapes. [`scripts/run-events.py`](../scripts/run-events.py) is the semantic executable contract: it additionally enforces cross-field identity equality, selected-branch ancestry, lifecycle transitions, typed-reference binding, and hash-chain continuity that JSON Schema alone does not express.

## Authority boundary

Run evidence is **private operational metadata**, not marketing truth, user approval, an external-action capability, or an auditor verdict.

- Store it only below `memory/runs/<run-id>/`; never append it to the seven `memory/events/<registry>.ndjson` streams.
- A SHA-256 chain proves local byte continuity after an observed head. It does not prove who acted, that a claim is true, or that an owner approved it.
- Registry offsets are observations. Re-read and verify the live registry before relying on them.
- A save point may resume work; it cannot accept a proposal, authorize a send/publish/ad change, or bypass a safety control.
- Delete run directories under the project's operational retention policy. Unlike registry history, run evidence is not permanent by design.

The runtime accepts only closed metadata, safe IDs, relative/opaque references, numeric metrics, and hashes. A syntactically safe ID is **not anonymization**: callers must use neutral codes or run-scoped hashes rather than customer/project names or low-entropy identifiers. Do not place raw prompts, chain-of-thought, tool arguments/results, transcripts, customer content, contact details, credentials, full source URLs, or secrets in any run artifact.

## Storage and tree model

```text
memory/runs/<run-id>/
├── .coordinator.lock
├── events.ndjson
├── session.json
├── turns/<turn-id>/context-manifest.json
├── turns/<turn-id>/snapshot.json
├── save-points/<save-point-id>.json
├── loops/<loop-id>/<sequence>-<transition-id>.json
└── envelopes/<summarized-head-event-id>.json
```

`events.ndjson` is the append-only run record. `session.json` is a disposable projection. `parent_event_id` forms the run-internal session tree: more than one child of an event creates a branch; leaf IDs are resumable heads. `parent_run_id` in an envelope can relate separate runs without merging their streams.

Runtime writes fail closed unless the project root is real, every target is Git-ignored, directory-descriptor operations and advisory locking are available, and streams/documents are single-link regular files. Directories use mode `0700`; files use `0600`.

After the genesis event creates a run, every event mutation shares one private
per-run coordinator. The fixed order is coordinator → loop lock when needed →
event stream. Generic/hook events, snapshots, save points, event-first loop
anchoring, and envelopes therefore cannot interleave inside one loop commit
sequence. If the reserved loop event is durable but its step is not, recovery
replays the same original loop request; it does not append around the gap.

## Event model

Every event request supplies:

```json
{
  "schema_version": "1.0",
  "run_id": "2a33a673-7074-4a80-ac13-c0ef7606ac64",
  "idempotency_key": "route:1",
  "event_type": "route_selected",
  "occurred_at": "2026-07-19T10:00:00Z",
  "actor": {"type": "system", "id": "host-adapter"},
  "parent_event_id": "76d0ad34-0b8b-57f7-adfc-9e8ad27c4521",
  "turn_id": "turn-1",
  "status": "succeeded",
  "subject": {"kind": "route", "ref": "content-writer"},
  "reason_code": "explicit-content-request",
  "references": [],
  "metrics": {},
  "dimensions": {
    "route_transition": "initial",
    "route_command": "seo-geo"
  }
}
```

The runtime assigns `event_id`, monotonic `offset`, `recorded_at`, `request_hash`, `previous_hash`, and `event_hash`. The genesis `run_started` event has no parent and uses 64 zeroes as `previous_hash`; all later events must reference an earlier event and chain to the previous stored offset. Event IDs are deterministic UUID5 values over `(run_id, idempotency_key)`. Reusing a key with changed content fails.

The closed event vocabulary covers run, route, context, turn, tool, artifact, save-point, loop, branch, waiting, and terminal lifecycle observations. `route_selected` is typed: `initial` may appear only once on an ancestry; `automatic-handoff` must target an unvisited skill and is capped at three handoffs/four skills; `user-reroute` resets that chain. Actor fields remain host-reported attribution, not proof that a user authorized anything. Route state and all transition checks inspect only the selected parent ancestry, never sibling events. Tool close events likewise require a matching open ancestor on the same selected turn branch, and a tool identity cannot be reused across turns on that branch. A terminal `run_finished`, `run_failed`, or `run_aborted` event seals the stream. The runtime reserves the final event-capacity slot for one of these terminal events: nonterminal events, snapshots, save points, loop anchors, and waiting envelopes fail before consuming it.

## Turn snapshot

A turn snapshot freezes the conditions visible to one model turn without copying those conditions:

- skill version and contract hash;
- optional derived prompt-contract reference and hash;
- host adapter and model identity;
- system-prompt hash;
- context-manifest reference, file hash, stable context signature, byte count, and explicitly advisory token estimate;
- ordered tool names/modes/schema hashes plus a computed toolset hash;
- all seven registry offsets, using `null` when the host did not observe one;
- permission, sandbox, network, and external-mutation posture;
- `parent_turn_id` when the turn branches from another turn.

Resolve the manifest first under the deterministic [`context-resolution.md`](context-resolution.md) contract. Before storing one immutable snapshot per turn, the runtime requires the canonical private manifest path, reopens the current catalog, target `SKILL.md`, and selected sources, and binds the snapshot's skill name/version/contract hash and registry offsets to that manifest. The manifest's `target_skill`, `command`, and `reason_code` must also equal the latest typed route on that selected ancestry. It verifies any optional project-relative prompt-contract reference and the toolset digest. Generated auditor prompt contracts are evaluation inputs derived from the topology/framework catalogs; referencing one binds evaluator context but grants no runtime, registry, persistence, or external-action authority. `parent_turn_id` is derived from the nearest ancestor snapshot on the selected event branch; a sibling branch cannot claim another branch's turn. A selected branch is capped at 256 snapshots, matching the envelope's manifest capacity; start a child run before turn 257 so the run remains finishable. Explicit `turn_started`/`turn_finished` events remain optional host telemetry—snapshot correctness does not depend on a hook.

## Save point

A save point binds a recovery instruction to the verified stream head (`last_event_id`, `last_event_offset`, and `last_event_hash`), the turn snapshot, the context manifest/signature, artifact hashes and validator states, all registry offsets, handoff depth, and a typed next action.

Creation fails when the head changed, an observed tool call is unfinished, a referenced file is missing/unsafe/hash-mismatched, or current context sources drifted. Project references are opened component-by-component from an anchored project-root descriptor, each file is capped at 10 MB, and a save point or envelope may inspect at most 64 MB of referenced artifacts. Audit artifacts are validated from the exact hash-checked bytes over stdin, avoiding a second path lookup. Registry offsets must equal the bound manifest and snapshot.

`visited_skills` and `chain_depth` must exactly equal the typed route chain and automatic-handoff depth derived from the bound event head. `pending_handoff` is only a proposed next action and never mutates that chain early. Untyped legacy `route_selected` records fail closed: this runtime was introduced and tightened within the same unpublished protocol-v1 implementation, so it deliberately provides no inference fallback that could confuse a user reroute with an automatic handoff. Re-run verification and reconcile; never edit the stream or save point in place.

## Run envelope

The envelope is a portable summary of the run, not the event history. It records the route, real/simulated evidence mode, every context manifest used across turns, the summarized head identity/hash, optional last save point, artifact hashes, registry offsets, numeric metrics, failure class, typed next action, and a runtime-derived `loop_closure`. Its ordered manifest references must exactly match turn snapshots on the selected event branch; its route must agree with the terminal typed route event, terminal manifest, and terminal snapshot, while offsets come from that bound manifest. Except for the failed/aborted degraded form described below, a run with no ancestor snapshot cannot emit a verified envelope.

Before installing an envelope event, the runtime derives bounded loop closure only from `loop_state_changed` events on the summarized head's selected ancestry. Caller-supplied closure claims are discarded, and sibling-only loops are ignored. `succeeded` requires exact step/event coverage and a terminal state for every selected loop. `waiting`, `needs-input`, and `blocked` require exact coverage but may preserve active loops. `failed` and `aborted` also require bounded inspection, but may record selected loops as `unresolved` for nonterminal, missing, corrupt, mismatched, over-budget, or timed-out state and still seal the run. That escape hatch preserves failure evidence; it does not validate the unresolved step or claim convergence. Failed/aborted runs may additionally use a no-context form when failure happened before those records existed; it requires an empty context-manifest list, null route/save point, and null values for all seven registry offsets. The sealing event references the immutable envelope file.

## Proposal-only audit loop

[`audit-loop-protocol.md`](audit-loop-protocol.md) defines an optional bounded outer loop for validated FIX audits. Each v2 transition derives the exact immutable, hash-linked step bytes, reserves a dedicated `loop_state_changed` event with the step reference/hash, and only then materializes those bytes under `loops/`. The step records its run-parent event identity, so one `loop_id` cannot fork across run branches. A terminal run rejects new loop transitions/events, but it may still materialize exact bytes for a matching anchor fsynced before sealing; that record repair changes neither the event head nor the sealed envelope/closure. The controller records proposals, owner review, non-empty intervention evidence, and re-audits; it never performs the proposed marketing repair, writes an audit sink, accepts registry truth, or grants external-action authority. Leases use generation fencing, retries return deterministic `not_before` values without sleeping, and improvement cycles are separately capped at one to three. Only a distinct, identity-compatible, medium/high-confidence SHIP re-audit whose observation date passes the baseline/intervention provenance floor can converge.

Keep two provenance questions separate:

1. **Case provenance** — did the underlying scenario originate in real observed work or a simulated fixture?
2. **Execution provenance** — which real host/model/adapter produced this run?

A real model executing a simulated fixture remains simulated case evidence.

## CLI

Resolve the bundle root according to [`runtime-invocation.md`](runtime-invocation.md), keep the working directory at the host project, and call:

```bash
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" start start-event.json
python3 "$AARON_SKILLS_ROOT/scripts/context-resolver.py" resolve --request context-request.json --project-root "$PROJECT_ROOT" --output "$CONTEXT_MANIFEST"
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" append "$RUN_ID" event.json
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" snapshot "$RUN_ID" turn-snapshot.json
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" save-point "$RUN_ID" save-point.json
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" loop-step "$RUN_ID" "$LOOP_ID" "$STEP_REF" "$STEP_SHA"
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" finish "$RUN_ID" run-envelope.json
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" verify "$RUN_ID"
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" project "$RUN_ID"
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" resume "$RUN_ID" --max-bytes 4096
```

`verify` and `resume` are read only. `loop-step` is verification-only: it can deduplicate an already event-bound immutable audit-loop head, but cannot create an event anchor or materialize a missing step. When a loop action reports `event_committed=true`, replay that same action with the same key, occurrence time, expected head, and exact inputs so the controller re-derives and installs only the bytes named by the reserved event. That recovery may fill an exact anchor on a historical sibling ancestry or after a later terminal event without appending an event or moving the selected head; it does not rewrite a sealed envelope or upgrade its recorded unresolved closure. A duplicate whose file already exists and every new transition still require the anchor ancestry to be selected, and terminal state forbids every new transition/event. `finish` enforces the selected-ancestry closure rules above; use `waiting`, `needs-input`, or `blocked` while an exactly covered loop remains active, and use failed/aborted unresolved closure only to preserve a run that cannot complete validation. `project` verifies the complete stream before atomically rebuilding `session.json`. A resume summary that cannot retain optional route, loop, or artifact fields inside the caller's byte limit returns a labeled minimal identity/hash view instead of cutting JSON. If any event mutation reports `event_committed=true`, the event is already durable: use the operation-specific recovery path and do not invent another idempotency key.

## Host hook integration

Hooks do not create runs implicitly. A host may opt in by setting a canonical UUID in `AARON_ACTIVE_RUN_ID`; turn lifecycle records also require a stable host `AARON_ACTIVE_TURN_ID`. `record-hook` run-scope-hashes host session, turn, tool, and batch identifiers before persistence and stores only those hashes, hook/tool names, typed status, and hashes. A PreToolUse observation is recorded as `tool_requested`, not as a claim that every host permission layer allowed execution. Hook parent selection and append happen under the per-run coordinator and one exclusive stream lock, so concurrent hook observations extend one current-head branch without crossing a loop transition. If the host cannot provide a stable session/turn/tool identity, recording is skipped so retries cannot pollute the stream.

SessionStart may load the bounded `resume` summary as untrusted project data. Its combined context assembly is capped at 24KB and gives each source a smaller injection allowance than its storage limit (active run 3KB, HOT 9KB, checkpoint 3KB); any otherwise-valid source truncated for that combined budget is labeled explicitly. A missing runtime, inactive run, invalid stream, or unavailable stable identity must degrade to no trace context; it must never widen permissions or make a registry projection authoritative.

## Recovery and retention

1. Run `verify <run-id>` before resuming a stale or copied run.
2. Run `project <run-id>` when `session.json` is absent or behind.
3. Select a leaf/head and re-verify every referenced artifact and current registry offset.
4. Resume from a save point only after re-checking permissions and external state.
5. On truncation, reorder, duplicate ID/key, hash mismatch, unsafe path, or unexpected terminal event, stop and restore a verified backup. Never repair NDJSON by hand.

Retention may delete a complete run directory after its required evidence has been exported or expired. Deletion does not erase filesystem snapshots, backups, synced copies, model-provider logs, or exported envelopes.
