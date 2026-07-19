# State Model

This document defines the v18 project-state architecture. Runtime state is private by default, registry history is event sourced, projections are disposable views, and ordinary skill outputs never become canonical merely because they were saved.

## State Classes

| Class | Authority | Location | Lifecycle |
|---|---|---|---|
| Registry event | Canonical truth history | `memory/events/<registry>.ndjson` | Append-only; never hand-edited or temperature-managed |
| Registry projection | Current accepted state | `memory/projections/<registry>.json` | Rebuilt atomically from events |
| Human registry view | Presentation only | Registry-owned paths under `memory/` | Regenerated from projection; never authoritative |
| HOT index | Retrieval pointer | `memory/hot-cache.md` | 80 lines and 25 KB maximum |
| Session checkpoint | Resume pointer | `memory/session-checkpoint.md` | 40 lines and 8 KB maximum; refreshed after each handoff; untrusted hint, re-verified against live projections |
| WARM artifact | Dated working evidence | Discipline/skill path under `memory/` | On-demand; archive review after 90 days |
| COLD artifact | Historical evidence | `memory/archive/` | Read only when requested; no automatic deletion |
| Approved decision | User governance input | `memory/decisions.md` | Requires approval provenance; cannot override a live safety control |
| Open loop | Unresolved work | `memory/open-loops.md` | Never treated as an approved decision or canonical fact |

The repository tracks only safe templates and guidance under `memory/`. A full clone ignores runtime `memory/**`. In plugin host projects, exact-path direct writes pass a PreToolUse Git-ignore preflight; opaque shell/MCP memory mutations are unsupported and denied when identified. Registry writes repeat final/temp/lock checks at their atomic boundary, while post-use/failure/batch and first-Stop hooks audit the resulting namespace. Hooks do not edit ignore rules or provide an OS sandbox. Projects that deliberately version operational data must disable this operated path and provide their own access, retention, secret-scanning, and erasure controls.

## Registry Event Model

[`registry-event-protocol.md`](registry-event-protocol.md), [`registry-event.schema.json`](registry-event.schema.json), and [`scripts/registry-events.py`](../scripts/registry-events.py) are the executable contract.

### Invariants

1. One NDJSON stream per registry is canonical.
2. Every request carries a stable idempotency key, source and observation date, actor, explicit authorization reference, and optional optimistic `expected_revision`.
3. The runtime assigns monotonic offsets, deterministic event IDs, recorded timestamps, request hashes, and a SHA-256 hash chain.
4. Ordinary producers may only `propose`. The owner may `accept`, `reject`, `upsert`, or `transition` — exercised outside agent sessions via the Owner Ritual in `references/registry-event-protocol.md`; a proposal waiting on that ritual is a designed state, and builders proceed on `approved-fallback` meanwhile. `memory-management` may `tombstone` or `erase` with explicit authority.
5. A proposal has no canonical effect until accepted. Rejecting or accepting never deletes the original event.
6. JSON projections are installed atomically and can be rebuilt from verified history. Human Markdown is a rendering of the projection.
7. Stale expected revisions fail. A caller must re-read and reconcile; force-overwrite is not a recovery path.
8. Proposals resolve individually in offset order — the owner adjudicates each `propose` on its own merits, in stream order, never as a batch. This is the clause launch-window (T-0) writers rely on: competing same-window proposals resolve deterministically, one offset at a time.
8. Event streams are never cleared, consumed, rotated, archived, or edited by a skill.

### Registry Ownership

| Registry | Canonical stream | Owner | Human view |
|---|---|---|---|
| Entities | `memory/events/entities.ndjson` | `entity-registry` | `memory/entities/` |
| Creators | `memory/events/creators.ndjson` | `creator-registry` | `memory/creators/` |
| Claims/offers | `memory/events/claims.ndjson` | `offer-claims-registry` | `memory/claims/` |
| Consent/suppression | `memory/events/consent.ndjson` | `consent-registry` | `memory/consent/` |
| Launches | `memory/events/launches.ndjson` | `launch-registry` | `memory/launch-registry/` |
| Channels | `memory/events/channels.ndjson` | `channel-registry` | `memory/channels/` |
| Narrative canon | `memory/events/narrative.ndjson` | `narrative-registry` | `memory/narrative-registry/` |

The seven owner skills and `memory-management` form the eight-skill protocol layer. Auditor-class gates remain inside their home disciplines and do not gain registry authority.

### Consent Safety Path

Consent is the safety-critical exception to delayed proposal review:

- `suppress` is a privacy-first, deny-only direct path: any validated producer may add it, but it cannot erase, restore, mutate canonical truth, or authorize delivery. A verified data-subject `erase` uses a host-issued safety capability bound to that exact request and still takes effect without proposal delay.
- The runtime rebuilds `memory/projections/consent-suppressions.json` before returning success.
- Send eligibility calls `is-suppressed`, which replays verified history instead of trusting a stale projection.
- `restore` is owner-capability-only and requires a new `subscription_status: subscribed`, a string `basis_ref` equal to the measured/user-provided source reference, and timezone-aware source evidence later than the latest withdrawal and no later than the restore event.
- Erasure leaves a minimal pseudonymous suppression tombstone. It does not permanently bar a later, genuinely new opt-in: only a consent-owner capability may restore the same pseudonymous ID, using trusted basis evidence strictly newer than the erasure, and prior payload data is not restored. Consent strings are NFKC-checked and payloads accept only the runtime's closed typed fields, opaque references, and subject-free reason codes; never place raw email, phone, postal address, names, or other direct contact data in IDs, refs, or payloads.

Logical erasure removes current projected payload and working views. Append-only history and external backups may have separate retention obligations; do not claim cryptographic destruction. Data minimization is therefore a design requirement, not a cleanup preference.

## Working Memory

### HOT

`memory/hot-cache.md` is a bounded index of current goals, approved priorities, active safety blocks, and pointers to evidence. It is never a truth ledger.

- Promote only with explicit user authorization.
- Keep each item at three lines or fewer and cite its WARM artifact or accepted registry record.
- Review entries older than 30 days for demotion.
- SessionStart may inject a sanitized bounded excerpt; hook loading never grants write permission.

### WARM

WARM paths hold dated artifacts produced by skills, for example:

| Discipline | Default path |
|---|---|
| SEO/GEO research | `memory/research/<skill>/` |
| SEO/GEO build | `memory/content/<skill>/` |
| SEO/GEO optimize | `memory/seo-geo/tune/<skill>/` |
| SEO/GEO monitor | `memory/monitoring/<skill>/` |
| Influencer | `memory/influencer/<skill>/` |
| Paid ads | `memory/ad/<skill>/` |
| Email | `memory/email/<skill>/` |
| Launch | `memory/launch/<skill>/` |
| Social | `memory/social/<skill>/` |
| Narrative | `memory/narrative/<skill>/` |

Each file records `last_updated`, unit, observation window, sources, assumptions, registry offsets read, and open loops. A WARM finding may generate a registry proposal, but the artifact itself is not canonical.

### COLD

`memory/archive/` contains dated historical WARM artifacts. Archive moves preserve the original path, content hash, and source pointers. Registry events/projections and live consent state never enter COLD storage.

### Supersession

Comparable non-canonical notes may use explicit invalidation:

```text
same unit + field + meaning, newer equal-or-higher authority evidence
  -> mark the old note superseded_by: <new artifact/date>
  -> keep both until normal retention processing
```

If unit, time window, source meaning, or authority differs, preserve both and open a conflict. Registry facts change only through an event with the current revision.

## Decisions and Permission

A persistent write requires explicit authorization in the current request or a separate direct confirmation that names the action. Read-only queries, dry runs, and validation do not.

Every approved decision includes:

```yaml
approved_by: user
approval_ref: <current request or confirmation reference>
approved_at: <ISO date-time>
scope: <what this decision governs>
```

Inferred recommendations are open loops, not decisions. Auditor gates may not write HOT, decisions, canon, claims, or audit files without permission. A hook trigger, a veto, previous save consent, or a broad desire to "remember things" is not standing authorization for unrelated future writes.

## Narrative and Claims Dependencies

Narrative is L1 strategy, not optional decoration. Any core downstream message builder must read a coherent accepted Narrative canon and current claims projection, or use an explicitly approved labeled fallback.

Every such output and handoff carries:

```yaml
narrative_canon_id: <aggregate-id or null>
narrative_canon_version: <accepted version or null>
claims_projection_offset: <integer or null>
dependency_status: verified | approved-fallback | blocked
```

- `verified`: both accepted projections were read and all used claims are approved for the target context.
- `approved-fallback`: no usable canon exists, the user explicitly authorized a named temporary message basis, and unsupported claims remain blocked.
- `blocked`: required truth is absent/conflicting or a material claim is not approved; do not present the asset as publish-ready.

A fallback never writes itself into Narrative canon. Route durable changes as proposals to the owning registries.

## Auditor Artifacts

The eight gate sinks are `memory/audits/{content,domain,influencer,ad,email,launch,social,narrative}/`. This namespace is reserved: non-auditor diagnostics, indexes, and privacy logs must not write there. Each gate write requires permission and a valid v3 artifact. PostToolUse/PostToolUseFailure validate known channels, PostToolBatch and the first Stop run bounded full sweeps, and [`validate-audit-artifact.py`](../scripts/validate-audit-artifact.py) enforces the schema. The active-stop loop guard means hooks request repair rather than form an OS-level transaction boundary. Pre-commit/CI protect committed Git content from PII; ignored runtime artifact validity remains the host's responsibility.

Audit artifacts retain framework, profile, version, target, observation date, evidence coverage/confidence, status, and verdict. Monthly pointer indexes live under `memory/indexes/audits/`; they may link artifacts but may not invent a cross-framework aggregate or strip profile/version context.

## Ownership Rules

- Ordinary skills write only their authorized WARM path and proposal events.
- Registry owners write canonical operations only through the host-capability `owner-append` entry for their registry. Request `actor`/authorization fields are attribution and cannot grant owner authority.
- `memory-management` manages HOT/WARM/COLD lifecycle and authorized tombstone/erase events; it cannot accept proposals or impersonate owners.
- Auditor gates write only their own validated sink after permission.
- No skill directly edits event streams, JSON projections, or another skill's artifact.
- Data-subject consent erasure binds `actor.id` to the same pseudonymous aggregate ID and also requires a host safety capability bound to the complete request; field equality alone is attribution, not authentication. Restore is owner-capability-only and requires a trusted basis source timestamp later than the withdrawal.
- Registry writes inside a Git worktree fail closed unless operational event/projection targets are ignored; read-only queries create no runtime paths.
- External side effects, uploads, publication, sends, ad changes, and destructive deletes require their own explicit approval even when a memory write was approved.

## Recovery

On projection loss, run `project <registry>`. On suspected corruption, run `verify <registry>` and stop on any offset/hash/idempotency failure. Restore a verified backup or append a compensating event; never patch NDJSON manually. A failed projection install does not justify deleting the fsynced event.
