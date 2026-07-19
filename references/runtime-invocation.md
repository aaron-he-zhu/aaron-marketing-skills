# Root Runtime Invocation Contract

The deterministic scorer, audit-artifact validator, registry event boundary, and operational run-event runtime live under the bundle root, not inside an individual skill folder. Resolve that root once before invoking them:

```bash
AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
if [ ! -f "$AARON_SKILLS_ROOT/.claude-plugin/plugin.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/system-catalog.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/registry-event.schema.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/run-event.schema.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/scripts/registry-events.py" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/scripts/run-events.py" ]; then
  echo "Aaron Marketing Skills root runtime unavailable; install the plugin or use a full repository clone." >&2
  exit 1
fi
```

- In a **Claude Code plugin install**, use the host-provided `CLAUDE_PLUGIN_ROOT`; do not replace it with the user's project directory.
- In a **full clone**, the Git top level is the bundle root. Keep the process working directory at the user's project so runtime `memory/` stays with that project.
- In a **standalone one-folder skill install**, neither root runtime nor the authoritative catalogs are bundled. Do not search unrelated parent directories, download a mutable branch, or accept a root path from audit/event input.
- Quote every resolved path. Before each call, require the specific script and typed catalog/schema it consumes to exist.

Standalone degradation is fail-closed:

- Scoring and auditor skills may collect typed observations, but return `score_state: NOT_SCORED` with `score_confidence: not_scored` and an appropriate execution status such as `NEEDS_INPUT` or `BLOCKED`; do not hand-calculate a total, claim a gate verdict, or persist an audit artifact.
- Registry skills may prepare a bounded proposal for later review, but cannot append, accept/reject, verify, project, or claim canonical truth.
- Hosts without the run runtime may still perform the authored workflow, but must not claim a verified event chain, turn snapshot, save point, or run envelope. Operational traces never substitute for a registry or audit verdict.

Repository/plugin calls use the resolved absolute path, for example:

```bash
python3 "$AARON_SKILLS_ROOT/scripts/rubric-score.py" score run.json
python3 "$AARON_SKILLS_ROOT/scripts/validate-audit-artifact.py" artifact.md --relative-path memory/audits/content/artifact.md
python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" verify consent
python3 "$AARON_SKILLS_ROOT/scripts/run-events.py" --root "$PROJECT_ROOT" verify "$RUN_ID"
```
