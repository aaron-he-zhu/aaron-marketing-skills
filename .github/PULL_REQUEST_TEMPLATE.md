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
- [ ] Placed in the correct phase directory (SEO/GEO: research/build/optimize/monitor · protocol: protocol · influencer: discover/plan/activate/measure · paid: `ad/<phase>/` — research/orchestrate/activate/scale)
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
- [ ] `README.md` skills table updated (if adding a new skill)
- [ ] `CLAUDE.md` category table updated (if counts/structure changed)
- [ ] `AGENTS.md` name/count line updated (if counts/structure changed)
- [ ] `docs/README.zh.md` counts + version badge updated (if counts/structure changed)
- [ ] No CORE-EEAT, CITE, C³, ROAS, veto, cap, BLOCKED, or artifact-gate standard was weakened
- [ ] No new pip / third-party dependency (stdlib-only; enforced by `scripts/check-stdlib-only.sh`)
- [ ] No secrets / PII introduced (`scripts/check-pii.py` clean)
- [ ] Eval structure intact (`scripts/check-evals.py`; `--update` the manifest if skills changed)
- [ ] Human maintainer review completed before merge
