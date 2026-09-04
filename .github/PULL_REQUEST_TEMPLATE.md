## What does this PR do?

<!-- Brief description of changes -->

## Type of change

Prefer a focused PR. New skills are rare and path-safe only — do not add a
121st Skill or rename/move/re-slug an existing Skill.

- [ ] Documentation (README / in-repo docs / docs-hub pointer)
- [ ] AI Staff install or smoke
- [ ] Skill update (existing skill body only — no path / slug / `name` change)
- [ ] Bug fix
- [ ] CI / guard
- [ ] Other

## Checklist

### For documentation / AI Staff / smoke:
- [ ] No Skill URL, directory, slug, or `name` change
- [ ] Wiki is not wired into runtime assembly, context-modules, or `### Runtime Reads`
- [ ] Maintenance scripts named from docs stay out of the plugin payload
- [ ] Staff changes stay generate-only (output outside the repo; no Gateway / Web UI / billing)

### For Skill-evolution / wiki proposals:
- [ ] Path-safe: no Skill URL / directory / slug / `name` change and no 121st Skill
- [ ] Pattern id cited (`AMS-P-…`) or this PR is wiki-only ingest
- [ ] Wiki is not wired into runtime assembly or `### Runtime Reads`
- [ ] Checklist: `references/wiki/skill-evolution-proposal.md`

### For skill-body updates:
- [ ] `name` field still matches directory name exactly
- [ ] `description` still includes trigger phrases AND scope boundaries
- [ ] Uses `~~placeholder` pattern for tool references
- [ ] Related skills are linked correctly
- [ ] Eval cases still valid (`evals/<skill>/cases.md`)
- [ ] Still runs at Tier 1 keyless

### For all changes:
- [ ] Follows the [Agent Skills specification](https://agentskills.io/specification.md)
- [ ] `VERSIONS.md` updated when a skill or bundle version changes
- [ ] Marketplace / plugin arrays updated only if a skill is added (avoid this)
- [ ] `.claude-plugin/marketplace.json` byte-identical to root when those files change
- [ ] Agent Plugins v1 impact reviewed for Skill/static-reference changes
- [ ] No generated root `skills/` mirror was added
- [ ] Portable Lite still contains no `mcp.json`, commands, hooks, connector helpers, or executable repository runtime
- [ ] No CORE-EEAT, CITE, STAR, ROAS, veto, cap, BLOCKED, or artifact-gate standard was weakened
- [ ] No new pip / third-party dependency in core/plugin/distribution or guard-scanned Python surfaces
- [ ] No secrets / PII introduced (`scripts/check-pii.py` clean)
- [ ] Human maintainer review completed before merge
