# Deterministic Context Resolution

`scripts/context-resolver.py` turns an explicit context request into a bounded,
metadata-only manifest. It does not infer intent, search for files, estimate
tokens, or copy source bodies. `scripts/context-plan.py` can perform closed,
machine-contract-backed candidate discovery; the resolver owns reproducible
selection and fail-closed evidence.

Schemas (the manifest schema embeds the request shape, so it has no external
`$ref` and can be resolved offline as one document):

- `references/context-request.schema.json` — caller input
- `references/context-manifest.schema.json` — immutable result

## Profile boundary

Context planning and creation of a verified run manifest are Governed
capabilities. Before planning or resolving output, the host must run the
read-only profile diagnostic in
[`runtime-invocation.md`](runtime-invocation.md) and require
`policy.new_run_allowed: true`. Lite and Pro may validate a supplied document
for diagnostics when the relevant validator is physically present, but they
must not create run evidence or claim a resolver-verified active run.

A nonterminal pre-v19 stream is `LEGACY_RUN_BLOCKED`. The v19 planner,
resolver, and controller must not resolve a replacement manifest against v19
catalog/skill bytes, resume the old run, or append a checkpoint/envelope. Lite
inline/read-only work can continue outside that stream until the old run is
drained before upgrade. Close it with the pinned pre-v19 runtime's valid
finish/abort path and verify the terminal event before invoking v19 again. If
that runtime cannot be verified, retain the stream read-only or restore a
verified backup; never hand-edit the event file or use a v19 manifest to
retrofit the old run.

Profile resolution and profile switching never rewrite a context manifest,
registry stream, projection, save point, or envelope. A v19 run binds its
runtime identity in the root `run_started` event; the catalog and target-skill
identities below remain independent content bindings.

## Request contract

A request binds one canonical `run_id`, one safe `turn_id`, an explicit `as_of`
date-time, a catalog-backed route, selected-byte/resource/sensitivity budgets,
an aggregate inspection-work budget, registry offsets, and at most 256
candidates. Every candidate declares:

| Field | Meaning |
|---|---|
| `scope` + `path` | A relative regular file below the bundle or project root |
| `requirement` | `required`, `optional`, or `forbidden` |
| `authority` | `canonical`, `approved`, `working`, or `untrusted` |
| `observed_at` + `max_age_seconds` | Freshness evidence evaluated against explicit `as_of` |
| `priority` | Caller priority after authority and freshness |
| `sensitivity` | `public`, `internal`, `confidential`, or `restricted` |
| `expected_sha256` | Optional content pin; a required mismatch stops resolution |
| `conflict_group` | Mutually exclusive alternatives |
| `supersedes` | Explicit replacement edges between candidate IDs |
| `load_policy` | Planner metadata: `always`, `activation`, `conditional`, `fallback`, or `lookup` |
| `exclusive_group` + `condition_code` | A closed distribution XOR; currently repository/plugin auditor sources versus the standalone fallback |

Unknown fields, duplicate IDs/JSON keys, non-finite numbers, future
observations, supersedes cycles, unsafe paths, and contradictory
forbidden/non-forbidden declarations fail closed.

A planner-backed request also binds `distribution_profile` to exactly
`repository`, `plugin`, or `standalone-skill`. Auditor candidates declare both
branches of `auditor-runtime-chain`: root policy/schema/benchmark sources use
`repository-or-plugin`, while the generated local `auditor-runtime.md` uses
`standalone-skill`. Missing either branch fails request validation. Resolution
omits the inactive branch as `condition-not-met` before reading it, so a
repository/plugin manifest and a standalone manifest can never select both
chains. `plugin` intentionally aliases repository policy availability; it does
not imply a capability profile or grant an external action.

The `auto` route must declare one primary allowlisted generated scenario shard,
may add `cross-discipline`, and may name a second primary only together with
`cross-discipline` (three shards total). Every bundle shard candidate must be in
that declared set, and each declared shard must appear exactly once as a direct,
required `routing-scenario` bundle candidate that cannot be superseded or deduplicated
away. Non-`auto` commands cannot declare scenario shards. For a discipline target,
`auto` must include that discipline's primary shard. Protocol targets are an explicit
cross-cutting exception: their selected primary shard records the topical entry path
(including the existing SEO/GEO shard for the memory-management lifecycle cases).
The target skill must exist in `references/system-catalog.json`; a discipline command can target
only a skill in that discipline. The resolver also checks the target
`SKILL.md` name plus independent semver and records its byte hash alongside the
separate catalog version/hash. A skill version is not required to equal the
architecture version.

## Selection algorithm

Resolution is deterministic and does not depend on request array order:

1. Resolve the closed distribution conditions and record every inactive branch
   as `condition-not-met` without reading it.
2. Record `forbidden` candidates without reading them.
3. Enforce sensitivity and freshness. A rejected required candidate stops the
   run; an optional candidate receives an omission reason.
4. Inspect required candidates first, then optional candidates by authority,
   freshness, priority, scope, path, and ID. Each stable source is read twice;
   `max_inspection_bytes` caps those aggregate reads independently of selected bytes.
   An over-budget required source stops resolution; an optional one receives
   `inspection-budget` without being read.
5. Calculate SHA-256 and bytes for each inspected source and enforce any expected hash.
6. Apply the acyclic `supersedes` graph. Replacements inherit the required
   status of resources they satisfy.
7. Fail closed when more than one active member of a conflict group has a
   different content hash. The caller must use explicit `supersedes` edges to
   resolve that conflict; equal-hash members are safe duplicates.
8. Deduplicate identical content hashes by required status, authority,
   freshness, priority, scope, path, then resource ID. A selected
   resource lists every candidate ID it satisfies.
9. Admit all effective-required resources, then optional resources in the same
   order until the resource or byte budget is reached. Required budget overflow
   stops resolution; optional overflow is explicit in `omitted`.

Every omission uses a typed reason (`forbidden`, `missing`, `stale`,
`sensitivity-budget`, `hash-mismatch`, `duplicate-content`, `superseded`,
`byte-budget`, `resource-budget`, `inspection-budget`, or
`condition-not-met`). Conflict and supersedes
decisions are retained separately from budget decisions.

## Filesystem and output guarantees

Bundle/project reads reject absolute paths, dot components, symlinks, hard-linked
files, non-regular files, and directory swaps detected during inspection. Files
are read twice through the same descriptor; content and inode metadata must stay
stable. This is a TOCTOU defense, not a claim that an external process can never
change a source after resolution. The manifest's source hashes are the boundary
used by downstream snapshots and save points.

Manifest output is fixed to `memory/runs/<run-id>/turns/<turn-id>/context-manifest.json`
and its parent directories must already exist. In a Git worktree, both the target
and temporary must be Git-ignored. Installation writes and fsyncs a unique
private temporary, then uses a
no-replace hard link as the arbitration point. Output uses mode `0600`; retries
re-check that installed mode rather than accepting a public pre-created file.
Parent run directories are expected to be private. Concurrent identical writers are
idempotent. An existing private, semantically identical JSON document is accepted; any
different document, symlink, or unsafe file is rejected. Mutation therefore
requires POSIX-style directory-descriptor and hard-link support; unsupported
hosts must treat resolver output as unavailable rather than weaken the install.

The manifest embeds the normalized metadata-only request plus `request_sha256`,
then records paths, target-skill/catalog identity, hashes, selected and inspected
byte counts, selection provenance, omissions, conflicts, and offsets—never source
bodies. This makes deterministic replay part of the artifact rather than a
caller-side assertion. `token_estimate` and
`estimator` are deliberately `null`; bytes are the host-independent budget.
The route records `skill_version` separately from `catalog_version`; the former
is the target SKILL.md contract version and the latter is architecture identity.

## Context identity

`context_signature` is SHA-256 over canonical JSON containing exactly:

- schema version
- catalog-bound route
- input limits plus inspected/selected byte and resource totals
- selected resource metadata/hashes and satisfied IDs
- omissions and conflicts
- registry offsets

It excludes the embedded request/request hash, `run_id`, `turn_id`, `as_of`,
`token_estimate`, and `estimator`, so
the same selection can be compared across runs and turns. A selected resource's
`observed_at` remains signed provenance; changing source freshness evidence is a
semantic context change. The manifest still carries the excluded invocation
fields and is compatible with the `context_signature` identity consumed by turn
snapshots, save points, and run envelopes.

## CLI

Resolve `AARON_SKILLS_ROOT` and a Governed effective profile with the
[root runtime invocation contract](runtime-invocation.md), then keep the
project root explicit:

```bash
python3 "$AARON_SKILLS_ROOT/scripts/context-resolver.py" validate-request \
  --request request.json --bundle-root .

python3 "$AARON_SKILLS_ROOT/scripts/context-resolver.py" resolve \
  --request request.json \
  --bundle-root . \
  --project-root /path/to/project \
  --output memory/runs/<run-id>/turns/<turn-id>/context-manifest.json

python3 "$AARON_SKILLS_ROOT/scripts/context-resolver.py" validate-manifest \
  --manifest /path/to/project/memory/runs/<run-id>/turns/<turn-id>/context-manifest.json

python3 "$AARON_SKILLS_ROOT/scripts/context-resolver.py" verify-manifest \
  --manifest /path/to/project/memory/runs/<run-id>/turns/<turn-id>/context-manifest.json \
  --bundle-root "$AARON_SKILLS_ROOT" \
  --project-root /path/to/project
```

`validate-manifest` verifies the closed document shape, embedded request hash and
identity, arithmetic, and signature. `verify-manifest` reruns the embedded request
against the current catalog, target `SKILL.md`, and candidate sources, then requires
the complete canonical result to match. Turn snapshots and save points perform that live verification
automatically; any drift requires a newly resolved manifest. Envelopes preserve the
historical snapshot evidence and do not relabel changed current inputs as unchanged.

The CLI exits `2` on contract, catalog, filesystem, budget, or immutable-output
failure. A caller may enumerate candidates itself or use the closed planner in
`references/context-planning.md`; creation of resolver output parent directories
remains a host responsibility. The resolver never broadens its own context scope.
