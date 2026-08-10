## What does this PR do?

<!-- Brief description of changes -->

## Type of change

- [ ] New skill
- [ ] Skill update
- [ ] Documentation
- [ ] Bug fix
- [ ] Other

## Checklist

### For new skills:
- [ ] `name` field matches directory name exactly
- [ ] `description` includes trigger phrases AND scope boundaries
- [ ] Placed in the correct phase directory (SEO/GEO: survey/implement/tune/evaluate · protocol: protocol · influencer: scout/target/activate/report · paid: `ad/<phase>/` — research/orchestrate/activate/scale)
- [ ] Uses `~~placeholder` pattern for tool references
- [ ] Includes validation checkpoints
- [ ] Includes at least one concrete example
- [ ] Related skills are linked correctly
- [ ] Has `evals/<skill>/cases.md` (eval structural-lint gate), incl. NEEDS_INPUT / BLOCKED cases where relevant
- [ ] Runs at Tier 1 keyless; any new `~~category` has a free/own-data fallback in CONNECTORS.md

### For all changes:
- [ ] Follows the [Agent Skills specification](https://agentskills.io/specification.md)
- [ ] `VERSIONS.md` updated with new version and date
- [ ] `marketplace.json` (repo root) skills array updated (if adding a new skill)
- [ ] `.claude-plugin/marketplace.json` byte-identical to root (`cp marketplace.json .claude-plugin/marketplace.json` — CI only diff-checks and fails on mismatch, it never copies)
- [ ] `.claude-plugin/plugin.json` skills array updated (if adding a new skill)
- [ ] Agent Plugins v1 impact reviewed for Skill/static-reference changes: Portable Lite builds and `python3 scripts/validate-agent-plugin.py <unpacked-package-dir>` passes with 120/120 strict Skills
- [ ] No generated root `skills/` mirror was added; the discipline/phase source tree remains authoritative
- [ ] Portable Lite still contains no `mcp.json`, commands, hooks, connector helpers, or executable repository runtime
- [ ] `README.md` skills table updated (if adding a new skill)
- [ ] `CLAUDE.md` category table updated (if counts/structure changed)
- [ ] `AGENTS.md` name/count line updated (if counts/structure changed)
- [ ] `docs/README.zh.md` counts + version badge updated (if counts/structure changed)
- [ ] No CORE-EEAT, CITE, STAR, ROAS, veto, cap, BLOCKED, or artifact-gate standard was weakened
- [ ] No new pip / third-party dependency in core/plugin/distribution or guard-scanned Python surfaces (stdlib-only; eval-only probes must stay isolated, locked, and non-distributed)
- [ ] No secrets / PII introduced (`scripts/check-pii.py` clean)
- [ ] Eval structure intact (`scripts/check-evals.py`; `--update` the manifest if skills changed)
- [ ] Human maintainer review completed before merge
