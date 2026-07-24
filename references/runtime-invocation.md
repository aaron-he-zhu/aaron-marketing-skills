# Root Runtime Invocation Contract

Runtime capabilities live under the bundle root, not inside an individual skill
folder. Resolve that root once, then resolve the project capability profile
before checking only the files needed by the requested mechanism:

```bash
AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
if [ ! -f "$AARON_SKILLS_ROOT/.claude-plugin/plugin.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/system-catalog.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/capability-profiles.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/scripts/profile-resolver.py" ]; then
  echo "Aaron Marketing Skills profile runtime unavailable." >&2
  exit 1
fi

python3 "$AARON_SKILLS_ROOT/scripts/profile-resolver.py" \
  --root "$PROJECT_ROOT" \
  --bundle-root "$AARON_SKILLS_ROOT" \
  diagnose --json
```

- In a **Claude Code plugin install**, use the host-provided `CLAUDE_PLUGIN_ROOT`; do not replace it with the user's project directory.
- In a **full clone**, the Git top level is the bundle root. Keep the process working directory at the user's project so runtime `memory/` stays with that project.
- In a **standalone one-folder skill install**, the physical ceiling is Lite and
  neither root runtime nor the authoritative catalogs are bundled. Do not search
  unrelated parent directories, download a mutable branch, or accept a root path
  from audit/event input.
- Quote every resolved path. Before each call, require only the specific script
  and typed catalog/schema it consumes to exist.

Profile request precedence is controller/profile-resolver CLI, then
`AARON_MARKETING_PROFILE`, then `.aaron-marketing/profile.json`, then the
state-derived default. The physical package ceiling is applied afterward and
cannot be raised by any of those inputs. A fresh project defaults to Lite
without writing a config or migration marker. Existing state with no config is
`legacy-read-only`; a malformed config fails closed.

Selection belongs to the installer or host-admin surface, a one-invocation
`--profile`, the host environment, or the closed project config—not to the
public slash-command grammar. The eight commands remain `auto` plus the seven
discipline entrypoints; there is no ninth profile command. A full
Governed-ceiling plugin therefore still starts a fresh project in Lite until
one of these explicit controls selects Pro or Governed. See the exact config
shape, precedence, and physical archive matrix in
[`capability-profiles.md`](capability-profiles.md).

The feature-specific runtime requirements are:

| Mechanism | Required capability | Required root files |
|---|---|---|
| scoring | Lite | `rubric-score.py`, framework/scoring catalogs |
| audit validation | Lite | `validate-audit-artifact.py`, audit schemas |
| connectors / saved audit | Pro | requested connector or validator plus its schema |
| canonical registry write | Governed | `registry-events.py`, registry schema/catalog |
| run evidence | Governed | `run-events.py` and run artifact schemas |
| context planning | Governed | contract index, `context-plan.py`, `context-resolver.py` |
| complete verified run | Governed | context requirements plus `runtime-controller.py` |

All profiles keep consent, claims, PII/secrets, external-mutation approval,
audit-verdict integrity, and release provenance enabled. A profile enables a
mechanism; it never grants owner authority or permission for a real-world
mutation. See [`capability-profiles.md`](capability-profiles.md).

A nonterminal stream without the v19 runtime identity returns
`LEGACY_RUN_BLOCKED`. Lite inline/read-only work may continue, but v19 must not
start a Governed run, write an ordinary registry event, resume, checkpoint,
finish, or append anything to that old stream. Drain it before upgrading; do
not reinterpret it with v19 contracts. “Drain” means using the pinned runtime
that created the stream to append its valid `run_finished`, `run_failed`, or
`run_aborted` terminal event. If v19 is already installed, restore that old
bundle temporarily, close and verify the old run, then reinstall v19. Never
hand-edit the stream or use v19 to synthesize its terminal event; when the old
runtime cannot be verified, keep the project read-only and recover a verified
backup.

Profile resolution and switching themselves write nothing. Lowering a profile
disables future mechanisms but does not delete or rewrite existing registries,
projections, memory, audits, manifests, save points, envelopes, or run evidence.

Standalone degradation is fail-closed:

- Scoring and auditor skills may collect typed observations, but return `score_state: NOT_SCORED` with `score_confidence: not_scored` and an appropriate execution status such as `NEEDS_INPUT` or `BLOCKED`; do not hand-calculate a total, claim a gate verdict, or persist an audit artifact.
- Registry skills may prepare a bounded proposal for later review, but cannot append, accept/reject, verify, project, or claim canonical truth. The deny-only consent `suppress` path is the exception to **proposal degradation**, not to runtime verification: when the root runtime is absent, return an exact immediate-suppress runtime handoff and `NEEDS_INPUT`, never convert the suppression into a proposal or route it through another skill, and never claim the mutation occurred.
- Hosts without the run runtime may still perform the authored workflow, but must not claim a verified event chain, turn snapshot, save point, or run envelope. Operational traces never substitute for a registry or audit verdict.
- Hosts without the context resolver may assemble supplied context, but must not claim a resolver-verified manifest, deterministic omission/conflict result, or stable context signature.

Repository/plugin calls use the resolved absolute path, for example:

```bash
python3 "$AARON_SKILLS_ROOT/scripts/rubric-score.py" score run.json
python3 "$AARON_SKILLS_ROOT/scripts/validate-audit-artifact.py" artifact.md --relative-path memory/audits/content/artifact.md
python3 "$AARON_SKILLS_ROOT/scripts/context-resolver.py" resolve --request context-request.json --project-root "$PROJECT_ROOT" --output "$CONTEXT_MANIFEST"
python3 "$AARON_SKILLS_ROOT/scripts/runtime-controller.py" --root "$PROJECT_ROOT" --bundle-root "$AARON_SKILLS_ROOT" --profile governed start controller-start.json
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" verify consent
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" verify "$RUN_ID"
```

For a complete new Governed run, prefer the controller path documented in
[`runtime-controller.md`](runtime-controller.md). Call `context-plan.py`,
`context-resolver.py`, or `run-events.py` directly only when implementing or
diagnosing one of those lower-level protocol boundaries. Direct invocation does
not bypass the profile, safety, or legacy-run boundary.
