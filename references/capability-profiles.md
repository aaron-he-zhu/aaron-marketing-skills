# Capability Profiles

Capability profiles change which local mechanisms are available; they never
grant registry authority, owner capability, or permission for an external
mutation. The authoritative matrix is
[`capability-profiles.json`](capability-profiles.json), and the optional project
configuration conforms to
[`profile-config.schema.json`](profile-config.schema.json).

## Profiles

| Profile | Use it for | Added mechanisms |
|---|---|---|
| **Lite** | Most briefs, drafts, plans, analysis, and inline scoring | All 120 authored skills, the unchanged eight-command router, deterministic scoring, inline delivery, and read-only use of existing canonical state |
| **Pro** | Work that needs a connector or an explicitly requested saved audit | Everything in Lite, plus connectors and audit persistence |
| **Governed** | Stateful or independently verifiable operations | Everything in Pro, plus working-memory and registry writes, run evidence, deterministic context planning, cross-discipline control-artifact validation, the runtime controller, workflow/audit loops, and owner-capability integration |

Consent, claims, PII/secret handling, external-mutation approval, audit-verdict
integrity, and release provenance are always-on overlays. Missing verification
therefore blocks the risky action; a lower profile never converts it into
permission.

The profile names describe **capability**, not skill inventory. All three plugin
archives contain the same 120 skills, preserve every 4×4 discipline loop and
TALE/SITE/ECHO/SEND/ROAS/STAR/RAMP acronym, and expose exactly the same eight
public slash commands. There is no profile command and no ninth command.

## v19 validation status

v19 is **engineering-validated** against its exact source: repository CI,
reproducible profile archives, and current-source real model/provider execution
over simulated semantic fixtures pass the release gate. A real provider does
not turn a simulated fixture into real-project evidence, so real-project
outcomes remain unvalidated.

Lite remains the fresh-project default. Governed capability availability means
only that its mechanisms are present and explicitly selectable; it does not
validate Governed outcomes or Governed-by-default. Promotion requires a
post-release real-project cohort of 14 pilots, 70 randomized paired
Lite/Governed projects, and 28 shadow projects. Until that full cohort passes,
do not publish empirical Governed outcome claims or describe Governed as the
validated default.

## Physical package versus effective profile

An installed archive sets a hard physical ceiling:

| Archive | Physical ceiling | Can resolve as |
|---|---|---|
| Lite | Lite | Lite |
| Pro | Pro | Lite or Pro |
| Governed | Governed | Lite, Pro, or Governed |
| Standalone one-folder skill | Lite degradation boundary | That skill's inline/read-only behavior only |

The ceiling can remove code; configuration cannot add it back. A request for a
profile above the installed ceiling fails with `PROFILE_CEILING_EXCEEDED`.
Conversely, installing the Governed-ceiling bundle does **not** activate
Governed behavior: a fresh project still resolves logically to Lite. This is
the bundle-plugin compatibility default.

Each plugin build carries its ceiling, resolved capability list, catalog hash,
profile-definition hash, package budget, and file hashes in
`distribution-manifest.json`. Build and verify a physical archive with:

```bash
python3 scripts/build-distribution.py \
  --plugin --profile lite --output /tmp/aaron-marketing-lite
python3 scripts/build-distribution.py \
  --verify-manifest /tmp/aaron-marketing-lite
```

Use `pro` or `governed` for the other archives. Bare `--plugin` is a deprecated
Governed-ceiling alias through v20; automation and release jobs should always
pass `--profile` explicitly.

The Governed build stays within its hard physical budget by replacing the
expanded `references/skill-contracts/` source tree with a deterministic,
bounded `references/skill-contracts.pack.json.gz`. Runtime lookup preserves the
same logical paths and fails closed unless every record hash and the aggregate
hash verify. The pack is a derived distribution artifact, not another source
of truth.

### Cross-discipline control verification

The complete authored evidence/measurement/action/retro semantics remain in
every profile. Their machine-verification surface is Governed-only: the
Governed archive includes the generated `control-bindings` catalog and schema,
the control-artifact schema, and `validate-control-artifact.py`. Lite and Pro
do not include the bindings or validator. Portable or other static projections
may include the schema as reference material, but a schema file is not an
executed validation result.

| Effective environment | Required result label | Claims that remain unavailable |
|---|---|---|
| Governed, exact bytes validated and bound to the selected run ancestry | `VERIFIED` only for the specific artifact checks that actually passed | The validator, intent, receipt, and `artifact_validated` event still do not grant external-action authority or create registry truth |
| Lite or Pro | `NOT_VERIFIED` | Selected ancestry, unique current head, verified receipt, permission consumption, compare-and-swap success, or persisted control state |
| Portable Lite, named-bot, or standalone | `NOT_VERIFIED` | The same claims, plus any claim that a local runtime/controller executed |

For a Governed run, record successful validation with the existing
`artifact_validated` event and rely on the run runtime for selected ancestry,
compare-and-swap current-head checks, checkpoints, and recovery. A sibling
branch, editable tracker, or rendered projection cannot replace the selected
artifact chain. `action-intent.permission_ref` is provenance-only and an
`action-receipt` is observed executor evidence; the executor must obtain and
re-check current exact authority before the real mutation.

The Governed runtime carries the compiled workflow graph, its authoritative
source/shards and schemas, and the workflow-loop executors. The separate
`scripts/workflow-graph.py` generator remains in the full repository for
authoring and CI and is not required by a packaged execution or verification
path. Complete context-planning, context-resolution, and runtime-controller
prose guides follow the same repository-only boundary. Packages keep compact
deterministic pointers at those paths so local links remain closed; Governed
retains the corresponding schemas and executable runtimes.

## Selecting a profile

Profile selection is an installer, project, environment, or host-admin control;
it is not conversational routing. Use the narrowest durable choice that
supports the work:

1. **Installer/admin surface** — install the matching physical archive. An
   admin UI may expose Lite / Pro / Governed, but it must map to one of those
   archive ceilings and the closed project configuration below.
2. **One invocation** — pass `--profile lite|pro|governed` to the profile-aware
   resolver/controller/runtime command. This does not persist a choice.
3. **Host environment** — set `AARON_MARKETING_PROFILE` for that host process.
4. **Project configuration** — create `.aaron-marketing/profile.json` as
   secret-free, closed JSON:

```json
{
  "schema_version": "1.0",
  "profile": "pro"
}
```

Requested profile precedence is CLI `--profile`, then
`AARON_MARKETING_PROFILE`, then `.aaron-marketing/profile.json`, then the state
default. The physical package ceiling is applied after that precedence and
cannot be raised by configuration or environment.

- A fresh project with no config or live state resolves to Lite without writing
  a config or marker.
- Existing state with no config resolves to computed `legacy-read-only`.
- A malformed config is fail-closed even when a higher-precedence override is
  supplied; repair or remove the file deliberately.
- A nonterminal run without the v19 runtime identity produces
  `LEGACY_RUN_BLOCKED`. Lite may continue inline/read-only work outside that
  stream, but v19 must not append to it or start Governed/registry writes.
- Profile resolution and switching are read-only and cannot modify canonical
  streams, projections, audits, memory, or run evidence.

Inspect the effective policy without changing the project:

```bash
python3 "$AARON_SKILLS_ROOT/scripts/profile-resolver.py" \
  --root "$PROJECT_ROOT" \
  --bundle-root "$AARON_SKILLS_ROOT" \
  diagnose --json
```

Check `status`, `reason_code`, `effective_profile`, `package_ceiling`,
`capabilities`, `safety_overlays`, and `policy`; do not infer permission from
the requested profile alone. `policy.external_mutation_authorized` remains
false in every profile because the relevant consent, claims, and host approval
must still authorize the specific action.

## Existing projects and profile switching

Canonical state is durable and independent of the current profile. Switching
from Governed to Lite or Pro stops new Governed writes; it does not delete,
truncate, migrate, or relabel registries, projections, audits, working memory,
context manifests, save points, envelopes, or run streams. Switching back to
Governed exposes the same state only after the normal integrity and authority
checks pass.

Existing state without an explicit profile is intentionally
`legacy-read-only`. Review it, resolve every active pre-v19 run, then select a
profile. A pre-v19 nonterminal stream must be drained by the runtime version
that created it:

1. Before upgrading, use the old runtime to `finish` or `abort` each active
   run and verify its terminal event.
2. If v19 is already installed and reports `LEGACY_RUN_BLOCKED`, temporarily
   restore the pinned old bundle, finish/abort there, and reinstall v19.
3. Never edit `events.ndjson`, append a v19 checkpoint/terminal event to the old
   stream, or start a new Governed run around it. If the old runtime/evidence
   cannot be verified, retain read-only state and restore a verified backup
   rather than fabricating a terminal event.

Terminal pre-v19 history remains readable; the resolver blocks only
nonterminal or unverifiable legacy streams.

## Standalone Lite degradation

A standalone one-folder skill does not include the root catalogs and runtimes.
It may execute its authored inline workflow and read supplied or available
canonical state, but it must not claim connector execution, a saved audit,
canonical mutation, a verified context manifest, a run evidence chain, or an
auditor verdict that requires missing runtime support. Exact fail-closed
handoffs for scoring, registries, consent suppression, context, and run
evidence are defined in
[`runtime-invocation.md`](runtime-invocation.md).

It likewise cannot machine-validate cross-discipline control artifacts.
Preserve the authored fields and discipline rules, but mark every
artifact/tracker/view `NOT_VERIFIED`; do not claim selected ancestry, one
current head, a verified receipt, permission consumption, compare-and-swap
success, or persistence.
