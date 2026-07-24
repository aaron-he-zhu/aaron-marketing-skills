# Runtime Controller Protocol

`scripts/runtime-controller.py` is the supported orchestration path for one
verified skill run. It composes existing authorities; it does not replace them:

1. the typed system catalog selects a skill;
2. the generated machine contract supplies its exact authored context hints;
3. `context-plan.py` enumerates a closed candidate set;
4. `context-resolver.py` resolves and immutably installs the context manifest;
5. `run-events.py` records the typed route, snapshot, save point, and envelope.

The controller never writes a truth registry, performs the skill's business
action, or treats its operational projection as authoritative state.

## Lifecycle

```text
start request
  -> verify machine contract and current source hashes
  -> plan + resolve context
  -> run_started -> route_selected -> turn_started -> context_resolved
  -> immutable turn snapshot
  -> host performs the bounded skill action
  -> checkpoint (optional, exact expected head)
  -> finish as waiting / needs-input / blocked / succeeded / failed / aborted
  -> immutable run envelope
```

Every mutation after `start` requires the exact `{event_id, offset, hash}` head
returned by the previous operation. A stale head cannot advance another branch.
An identical retry reuses the immutable artifact and event; a changed retry with
the same identity fails.

## Start

Create a closed request conforming to
`references/runtime-controller-request.schema.json`. The request binds the host,
model, system-prompt hash, tool schemas, permission boundary, route, registry
offsets, and deterministic context budget.

```json
{
  "schema_version": "1.0",
  "run_id": "123e4567-e89b-42d3-a456-426614174000",
  "parent_run_id": null,
  "turn_id": "turn-1",
  "as_of": "2026-07-22T12:00:00Z",
  "route": {
    "target_skill": "content-writer",
    "command": "seo-geo",
    "reason_code": "user-request"
  },
  "budget": {
    "max_tokens": 65536,
    "bytes_per_token": 4,
    "max_resources": 128,
    "max_sensitivity": "confidential",
    "prefix_file_limit": 128
  },
  "registry_offsets": {
    "entities": null,
    "creators": null,
    "claims": null,
    "consent": null,
    "launches": null,
    "channels": null,
    "narrative": null
  },
  "host": {
    "adapter": "host-adapter",
    "adapter_version": "1.0.0",
    "model_provider": "provider",
    "model_id": "model"
  },
  "system_prompt_sha256": "<64 lowercase hex>",
  "tools": [],
  "permission_profile": {
    "mode": "read-only",
    "sandbox": "workspace",
    "network": false,
    "external_mutations": false
  }
}
```

Run it from the user's project root while passing the immutable bundle root:

```bash
python3 "$AARON_SKILLS_ROOT/scripts/runtime-controller.py" \
  --root "$PROJECT_ROOT" \
  --bundle-root "$AARON_SKILLS_ROOT" \
  start start-request.json
```

The result exposes references and hashes, not source payloads. Before acting,
the host uses the returned immutable snapshot and manifest. `machine_contract`
identifies the exact generated contract consumed by planning.

`permission_profile.external_mutations: true` is valid only with
`mode: write-gated`; it records a boundary but does not itself authorize any
write or external action.

## Checkpoint

A checkpoint captures only a verified head, latest snapshot/context pair,
validated artifact references, route chain, and proposed next action.

```json
{
  "schema_version": "1.0",
  "checkpoint_id": "123e4567-e89b-42d3-a456-426614174001",
  "occurred_at": "2026-07-22T12:05:00Z",
  "expected_head": {
    "event_id": "<event UUID>",
    "offset": 5,
    "hash": "<64 lowercase hex>"
  },
  "status": "ready",
  "artifacts": [],
  "pending_handoff": null,
  "next_action": {"code": "finish"}
}
```

```bash
python3 "$AARON_SKILLS_ROOT/scripts/runtime-controller.py" \
  --root "$PROJECT_ROOT" checkpoint "$RUN_ID" checkpoint-request.json
```

An artifact marked `valid` must already have the matching selected-ancestry
validation event, except for the auditor sink whose dedicated validator is
replayed. A checkpoint is rejected while a tool call remains unfinished.

## Finish and wait

Use the returned checkpoint head, or the start head when no checkpoint is
needed:

```json
{
  "schema_version": "1.0",
  "occurred_at": "2026-07-22T12:06:00Z",
  "expected_head": {
    "event_id": "<event UUID>",
    "offset": 6,
    "hash": "<64 lowercase hex>"
  },
  "status": "succeeded",
  "evidence_mode": "real",
  "artifacts": [],
  "metrics": {},
  "failure_class": null,
  "next_action": null
}
```

```bash
python3 "$AARON_SKILLS_ROOT/scripts/runtime-controller.py" \
  --root "$PROJECT_ROOT" finish "$RUN_ID" finish-request.json
```

Supported statuses are `waiting`, `needs-input`, `blocked`, `succeeded`,
`failed`, and `aborted`. `failed`, `blocked`, and `aborted` require a typed
`failure_class`. A successful envelope fails if a selected-branch tool call is
unfinished. Terminal finishes also require every selected workflow/audit loop
to have a verified terminal head.

The controller adds bounded `controller.*` metrics for turns, tool calls,
checkpoints, loops, automatic handoffs, and selected context resources. User
metrics cannot use that reserved prefix.

## Resume

```bash
python3 "$AARON_SKILLS_ROOT/scripts/runtime-controller.py" \
  --root "$PROJECT_ROOT" resume "$RUN_ID"
```

Resume ignores `session.json`, verifies the append-only event hash chain,
reconstructs selected ancestry, validates the latest snapshot/save point, and
reopens every current context source. A modified required or selected source
blocks resume instead of silently reusing stale context. The result is a
bounded operational summary and remains non-authoritative.

## Failure and privacy behavior

- Planning and source verification occur before the run starts, so an invalid
  contract or unresolved required source creates no partial run.
- If a newly created run fails while installing its context/snapshot, the
  controller makes a best-effort typed `failed` envelope. It never seals a
  pre-existing run after a conflicting retry.
- Runtime files are private mode `0600`, live below Git-ignored `memory/runs/`,
  reject links/special or multi-link files, and use no-replace immutable writes.
- Context manifests retain metadata, hashes, selected resource text, and the
  complete request. Keep the project `memory/` directory private; never put
  credentials or unnecessary personal data into candidate files.
