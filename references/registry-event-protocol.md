# Registry Event Protocol

This protocol is the executable write boundary for the seven truth registries. [`registry-event.schema.json`](registry-event.schema.json) documents request shape; [`scripts/registry-events.py`](../scripts/registry-events.py) validates, appends, verifies, and projects it.

## Invariants

- Event streams under `memory/events/<registry>.ndjson` are append-only and canonical.
- Every request has an idempotency key. An identical retry returns the existing event; reuse with different content fails.
- The runtime assigns a monotonic offset, deterministic event ID, recorded timestamp, previous hash, and SHA-256 event hash.
- Canonical `propose`, `upsert`, `transition`, `tombstone`, `restore`, and controller-side `erase` requests require optimistic `expected_revision`. Stale writes fail instead of silently overwriting newer state. A direct data-subject consent erasure is the narrow CAS exception; it still appends atomically and suppresses immediately.
- Governed channel and launch states use executable transition graphs. `upsert` may initialize their first state only; every later state change must use compare-and-set `transition` and a valid edge.
- Ordinary skills submit `propose`; only the owning registry accepts/rejects or writes canonical operations.
- `actor`, `authorized_by`, and `authorization_ref` are audit attribution, not credentials. Ordinary `append` accepts only proposals and deny-only consent suppression. Canonical operations require `owner-append`; data-subject erasure requires `safety-append`. Each host capability authorizes exactly one normalized request and binds registry, principal, operation, aggregate, idempotency key, resolved project-root hash, a single-use capability ID, and expiry. Library calls pass through the same checks, including a second expiry/binding check under the exclusive append lock.
- Capability-authored events persist an HMAC authority signature over their assigned event content. Replay verifies that signature, its request/root binding, recording-before-expiry, and capability-ID uniqueness; recomputing the public SHA-256 request/event chain cannot forge canonical authority. A stream containing canonical events therefore fails closed when the host verification key is unavailable.
- Projections under `memory/projections/` are rebuildable, atomic materialized views, never the history source.
- Consent `suppress` and verified `erase` apply without proposal delay and regenerate the live suppression projection before success returns. `is-suppressed` replays the stream and treats inaccessible/corrupt history as an error, never as permission to send.
- Generic `suppress` is intentionally privacy-first and deny-only: any schema-valid producer may add suppression for a pseudonymous aggregate. This accepts a bounded denial-of-contact risk so an unauthenticated unsubscribe/complaint cannot fail open; it cannot erase payload, restore consent, mutate other canonical fields, or authorize delivery. Data-subject `erase` is different: equality of self-reported actor/aggregate fields is insufficient, so the host must verify the requester and issue a safety capability bound to that exact request.
- Consent request strings/keys are checked after Unicode NFKC normalization. Only actual timestamp fields get an ISO date-time exemption from phone detection; date-shaped values elsewhere do not. Consent `set`/`unset` fields, reason codes, enums, and opaque references are closed/minimized by the runtime, so arbitrary names, addresses, notes, or free text cannot enter payloads.
- Consent restore requires owner capability, a string `basis_ref` equal to a measured/user-provided `source.ref`, and timezone-aware source evidence strictly newer than the latest withdrawal and no later than the restore event.
- Before any write in a Git worktree, every event/projection target and its exact atomic-temp/lock sibling must be ignored by Git. Missing ignore coverage fails closed. Streams must be regular single-link files. Supported mutations require POSIX anchored directory descriptors for open/stat/mkdir/rename/unlink, descriptor-based permission changes, and identity checks; platforms without that safe set may perform read-only queries but mutation/init/projection rebuild fail closed before creating paths. Directory creation and later stream/projection opens walk retained no-follow descriptors from the canonical project root, so an intermediate parent swap cannot redirect a write. Projection rebuild takes the exclusive writer lock on every supported mutating platform, so an unlocked stale snapshot is never installed. Read-only `get`, `verify`, and suppression checks do not create or chmod runtime paths.

## Registries and Owners

| Registry key | Owning skill | Optional human view path |
|---|---|---|
| `entities` | `entity-registry` | `memory/entities/` |
| `creators` | `creator-registry` | `memory/creators/` |
| `claims` | `offer-claims-registry` | `memory/claims/` |
| `consent` | `consent-registry` | `memory/consent/` |
| `launches` | `launch-registry` | `memory/launch-registry/` |
| `channels` | `channel-registry` | `memory/channels/` |
| `narrative` | `narrative-registry` | `memory/narrative-registry/` |

Human Markdown views are optional renderings of accepted events; the stdlib runtime always materializes `memory/projections/<registry>.json`. A host or registry skill may regenerate/reorganize human views, but consumers must fall back to the JSON projection and no view may contain history absent from the event stream.

## Operations

| Operation | Authority | Effect |
|---|---|---|
| `propose` | Any authorized producer | Adds pending intake; no canonical record change |
| `accept` / `reject` | Host-capability principal for owning registry | Resolves one proposal; accept applies its proposed operation |
| `upsert` | Host-capability principal for owning registry | Applies top-level `set`/`unset` fields |
| `transition` | Host-capability principal for owning registry | Compare-and-set of `data.state` using `from`/`to` |
| `tombstone` | Host-capability principal for owner or memory-management | Retires the record without deleting history |
| `suppress` | Any schema-valid consent producer; deny-only privacy policy | Immediately sets live suppression; cannot authorize delivery or clear state |
| `restore` | Host-capability principal for consent owner | Clears suppression only from a newer trusted basis event |
| `erase` | Request-bound safety capability for a verified data subject, or host-capability owner/memory-management | Removes projected payload and leaves a minimal audit tombstone |

Each request carries exactly one effective mutation shape: upsert uses non-empty `set`/`unset`, transition uses only `transition`, tombstone/suppress/erase use only `reason`, and restore uses a non-empty `set` plus `reason`. A proposal is validated against its `proposed_operation` before append, so it cannot defer an invalid or compound mutation until acceptance.

An accepted proposal preserves the original source and occurrence time in the projected record and decision metadata. Accept/reject requests omit `expected_revision`: acceptance inherits and checks the proposal's stored revision. The accepting event remains the canonical mutation event and records the registry's authorization and trusted principal attestation. Tombstoned IDs remain terminal. An erased consent ID stays suppressed unless the consent owner performs capability-gated `restore` from trusted opt-in evidence strictly newer than the erasure/withdrawal; the old payload is never resurrected. Governed `state` can never be unset or reinitialized; initialize once with owner upsert, then use graph transitions.

## CLI

```bash
AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
test -n "$AARON_SKILLS_ROOT" \
  && test -f "$AARON_SKILLS_ROOT/scripts/registry-events.py" \
  && test -f "$AARON_SKILLS_ROOT/references/registry-event.schema.json" \
  && test -f "$AARON_SKILLS_ROOT/references/system-catalog.json" \
  || { echo "full registry runtime unavailable; prepare a proposal only" >&2; exit 1; }

python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" init
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" append consent safety-event.json
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" owner-append claims owner-event.json
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" safety-append consent erasure-event.json
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" verify consent
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" project consent
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" get consent subject-sha256-prefix
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" is-suppressed subject-sha256-prefix
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" pending
```

`pending` is the read-only intake/projection report: per registry it returns the
pending proposal count, the chronologically oldest pending proposal's occurred_at
and age in days, and an explicit `projection_status`: `not-required` for an empty
stream with no projection, or `current`, `behind`, `ahead`, `missing`, `invalid`,
or `unknown` when the event stream itself is unverifiable. `projection_lag` is
retained as a non-negative compatibility value only for `current`/`behind`. With
the host key it fully verifies the stream; without it the report uses only the
publicly verifiable structure (canonical JSON, offsets, hash chain, request hashes,
principal bindings) and labels itself `authority_verified: false` — the pending
signal is an advisory nudge, never an authorization input. It creates no runtime
paths. The SessionStart hook surfaces stale intake (oldest verifiable pending
proposal > 14 days), behind/missing/invalid/ahead projections, and unverifiable
streams. For every non-empty stream read without the host key, it also labels the
pending/projection counts advisory and warns that resolved owner decisions were
not authority-signature verified, so neither authority loss, the owner ritual
queue, nor projection repair can stall silently.

`owner-append` and `safety-append` succeed only when a trusted host injects `AARON_REGISTRY_HOST_KEY` and a valid `AARON_REGISTRY_CAPABILITY` for that one request. The signing key must remain in a host boundary where the agent cannot run arbitrary code or inspect the launched process environment; exposing the key to an agent-controlled shell defeats this authority model. Inject the token directly when launching the registry subprocess, and never place key/token values in a request file, prompt, shell argument, artifact, or log. The stdlib issuance function is for that trusted integration and tests, not an agent tool.

## Owner Ritual (the trusted host for a solo operator)

No supported install form ships a hosted authority service, and an agent session must never hold the key — so for a solo operator the trusted host **is the owner's own terminal, outside any agent session**: a human shell where no agent runs and no transcript records the environment. Canonical writes happen there and only there.

1. Keep `AARON_REGISTRY_HOST_KEY` in the OS keychain/secret manager (≥32 bytes), exported only inside that shell — e.g. `export AARON_REGISTRY_HOST_KEY="$(security find-generic-password -w -s aaron-registry)"` on macOS. It never enters the repository, a request file, a prompt, or an agent-visible environment.
2. Review the agent-prepared request file (a `propose` awaiting decision, an owner `upsert`/`transition`/`accept`/`reject`/`restore`, or a verified erasure), then mint the one-shot capability bound to that exact request with the stdlib issuance function (`issue_host_capability` in `scripts/registry-events.py`) in the same shell, exporting it as `AARON_REGISTRY_CAPABILITY`.
3. Run `owner-append` / `safety-append`, then immediately `project` and `verify` for that registry in the same shell, so fresh JSON projections and a verified chain are on disk before the shell closes.
4. Close the shell. Nothing from steps 1–3 is pasted back into an agent session.

**Agent sessions around the ritual.** Agent sessions append `propose` and `suppress`, and prepare owner/safety request files for review. While a stream contains no signed canonical events, `verify`, `project`, `get`, and `is-suppressed` work keylessly. Once canonical events exist, those replaying reads require the verification key **by design** — agent sessions then treat the owner-installed JSON projections under `memory/projections/` (and per-registry dossier renderings) as read-only truth instead of replaying, and report the projection's recorded offset as their read basis.

**Pending without an owner decision is a designed state, not an error.** Proposals wait indefinitely until the ritual runs: builders proceed on `approved-fallback` per the state model, `suppress`/erasure safety paths never wait on proposal review, and a skill that needs an acceptance reports the pending proposal and points at this ritual (`NEEDS_INPUT`) — it never blocks the engagement or self-accepts.

**Reject-and-repropose for stale revisions.** A pending proposal that carries an `expected_revision` the aggregate has since moved past can never be accepted, and events are never cleared — the owner rejects it with a reason code during the ritual, and the producing skill re-proposes against the current revision. Skills listing pending proposals must surface revision-stale ones as reject-and-repropose candidates rather than eternally actionable work.

Standalone one-folder skill installs do not contain this root runtime/schema/catalog. They may prepare a schema-shaped proposal or erasure handoff, but cannot append/project it, mint a capability, or claim canonical truth. `verify`, `get`, and `is-suppressed` also require the host verification key once a stream contains signed canonical events.

Use a stable hash/token generated by the user's system as a consent `aggregate_id`; do not put direct contact data in request strings or fields. Use only the runtime's typed/minimized consent fields and subject-free reason codes. A data-subject erasure request uses the same aggregate ID as `actor.id`, but that equality is attribution; the host safety capability supplies authority.

## Failure and Recovery

The event append is fsynced before projections are installed. If projection installation fails, the command fails and replay repairs it; the canonical event is not removed. `verify` revalidates each stored request, authority signature, capability binding/uniqueness, request hash, offset, timestamp, hash chain, deterministic ID, idempotency identity, and projection semantics. Missing/inaccessible paths and non-regular or multiply linked streams fail closed. Never edit NDJSON by hand. Repair by restoring a verified backup or appending a compensating event.

## Capacity Boundary

Every append revalidates the whole stream inside the lock and rebuilds projections, so append cost grows with stream length, and streams are never cleared, rotated, or compacted. That is a deliberate trade: these are registries of durable business facts — consent states, creators, claims, launches, channels, canon versions — whose natural volume is hundreds to a few thousand events per registry, not telemetry. Keep high-churn observations (rank samples, pulse metrics, monitor readings) in WARM memory files, and register only durable truth transitions. If a stream's append latency becomes noticeable at that designed volume, treat it as a signal that observations are leaking into the registry, not as a reason to rotate the stream.
