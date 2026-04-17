---
tier: hot
project: null
# Set `project: acme-q2` (or any slug) to scope this session's wiki/memory reads
# to a specific project. Leave null for global/default scope.
# See state-model.md §Project Isolation for the full lifecycle.
---

# Hot Cache

> Auto-loaded at session start. Hard limit: 80 lines / 25KB. See [memory-management](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md). Project isolation: set `project:` in the frontmatter above to scope wiki reads (e.g. `memory/wiki/acme-q2/index.md`).

## Active Index

- Auditor Runbook: [references/auditor-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/auditor-runbook.md) — SSOT for auditor handoff schema, cap arithmetic, guardrails, and user-facing translation. Inlined into `content-quality-auditor` and `domain-authority-auditor`.
- v7.1.0 contract upgrades: Critical Fail Cap (60/100), Guardrail Negatives (windowed positive reframes), Artifact Gate self-check, User-Facing Translation layer, Auditor-class handoff extension. All auditor-class skills must comply.
