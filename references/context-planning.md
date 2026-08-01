# Machine Contracts and Context Planning

`scripts/generate-skill-contracts.py` projects the authored Markdown contract of
all 120 catalogued skills into closed JSON. `scripts/context-plan.py` consumes
one of those projections and produces an explicit request for
`scripts/context-resolver.py`. The planner performs discovery; the resolver only
validates and selects from the declared candidate set.

## Machine-contract boundary

Each `references/skill-contracts/<skill>.json` binds the live `SKILL.md` path,
SHA-256, independent skill version, discipline, and phase. It preserves authored
routing triggers and boundaries, argument hint, Reads, Writes, Done when, output
summary, handoff text/targets, bundle references, and project-memory read hints.
The projection does not invent missing semantics:

- a description without quoted examples uses the complete authored
  `when_to_use` value and marks `trigger_source: when-to-use-fallback`;
- a missing Expected output uses authored Writes and marks
  `summary_source: writes-fallback`;
- the eight auditors point at the shared handoff contract when their local
  contract intentionally delegates that format.

Reads, Writes, Done when, and Next Best Skill also expose source-derived
`clauses`/`items`. Every item carries its exact field-text character span and an
`extraction_status`. Inputs distinguish required/optional only when the authored
text says so; writes expose side-effect and permission posture only from explicit
language; completion items are typed as success/blocking conditions; handoffs
retain condition and target skills. Ambiguous dimensions remain
`unclassified`—the raw display text remains authoritative.

Everything else required by the projection fails closed. The generated index
pins every per-skill JSON hash and the source catalog/shared-contract hashes.

```bash
python3 scripts/generate-skill-contracts.py --write
python3 scripts/generate-skill-contracts.py --check
```

`--check` is the drift gate: changed Markdown, catalog, schemas, shared contract,
or generated JSON causes a non-zero exit until the artifacts are regenerated.

## Planner contract

Planning requires an explicit skill, run/turn identity, inspection time, and
project root. It emits a context-request JSON file only; it does not initialize
memory, create run directories, or append a run ledger.

```bash
python3 scripts/context-plan.py plan \
  --skill content-writer \
  --run-id 123e4567-e89b-42d3-a456-426614174000 \
  --turn-id turn-1 \
  --as-of 2026-07-22T12:00:00Z \
  --project-root /path/to/project \
  --reason-code user-request \
  --distribution-profile repository \
  --max-tokens 65536 \
  --output /path/to/request.json

python3 scripts/context-plan.py validate \
  --request /path/to/request.json \
  --project-root /path/to/project
```

The closed candidate set always names the target skill, its machine contract,
the shared contract, authored bundle references, the four standard working-memory
files, exact project read hints, and every regular file found under authored
prefix hints. Prefix enumeration is sorted, bounded, rejects symlinks/non-regular
entries, and fails instead of silently truncating. Each prefix has a typed
`enumerated` outcome or an `unresolved` / `missing-prefix` omission in planner
provenance, so no later host search is implied. Missing exact project files
stay explicit optional candidates with a null expected hash. `/auto` requests
also contain the required topical routing shard, including a fixed mapping for
each protocol skill.

`--distribution-profile` is exactly `repository`, `plugin`, or
`standalone-skill` and is pinned in planner v1.1 provenance. For an auditor,
the planner emits both typed branches of one `auditor-runtime-chain` exclusive
group. Repository/plugin root sources use `condition_code:
repository-or-plugin`; the generated immutable local fallback uses
`condition_code: standalone-skill`. The resolver selects exactly one branch and
records the inactive branch as `condition-not-met` without reading it. This
distribution selector describes physical policy availability only; it does not
select Lite/Pro/Governed or grant authority.

The caller may supply a safe typed `reason_code`; it is carried unchanged into
the planned route and later must match the controller's `route_selected` event.

Every generated candidate also carries `load_policy`; distribution alternatives
carry `exclusive_group` and `condition_code`. These fields are closed metadata,
not prose inference. Every candidate states required/optional policy, authority,
sensitivity, observation time, freshness ceiling, priority, reason, and expected SHA-256.
The request's `planner` object pins the selected contract, index, catalog,
context-hint hash, and complete candidate-set hash. `validate` rechecks those
pins and asks the resolver to inspect every candidate source.

## Honest token and freshness semantics

The repository has no tokenizer dependency. `--max-tokens N` therefore uses the
declared `--bytes-per-token` factor (default 4) to derive the resolver's hard
`max_bytes` ceiling. The request records
`utf8-bytes-per-token-proxy-v1` and `derived-byte-ceiling`; this is a deterministic
capacity proxy, not a claim about model-specific tokenization.

Likewise, `--as-of` is the explicit planner inspection time and becomes every
candidate's `observed_at`. The default `max_age_seconds` is null because the
authored contracts do not contain reliable per-resource freshness SLAs. A caller
that needs a stricter freshness policy must add one deliberately and recompute
the candidate-set hash; the planner does not fabricate it.
