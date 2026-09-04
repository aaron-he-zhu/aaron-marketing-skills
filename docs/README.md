# Docs index

This repository keeps **minimal in-repo docs**. Long-form narrative, SEO, and
product story live on the
[aaronmarketing.ai docs hub](https://aaronmarketing.ai/docs/)
(placeholder hub root until canonical paths are published). SKILL.md files
stay in the repo. This index does **not** migrate or delete the trees below.

## In-repo SSOT (stay here)

| Doc | Why it stays in Git |
|-----|---------------------|
| [ai-staff-install.md](ai-staff-install.md) | Operator generate → Hermes / Grok install + Phase 1 boundaries |
| [agent-compatibility.md](agent-compatibility.md) | Host matrix, degradation, owner-run smoke backlog |
| [agent-plugins-v1.md](agent-plugins-v1.md) | Portable Lite package / capability boundary |
| [distribution.md](distribution.md) | Release, archives, publisher order (maintainers) |
| [connector-playbook.md](connector-playbook.md) | How to add a connector (maintainers) |
| [registry-submissions.md](registry-submissions.md) | Marketplace / directory listing mechanics |
| [repo-family.md](repo-family.md) | Sibling signpost-repo policy |
| [system-architecture.md](system-architecture.md) | Generated four-layer map (from the typed catalog) |
| [workflow-graph.md](workflow-graph.md) | Generated workflow graph view |
| [mcp-catalog.json](mcp-catalog.json) | Copy-paste MCP reference (not auto-registered) |
| Root `CONTRIBUTING.md` | Authoring + team conventions + 10 tracking surfaces |
| Root `SECURITY.md` · `PRIVACY.md` | Policy |

## Site-hub destined (keep in repo this PR)

Do **not** batch-move these until a separate go-ahead. They remain readable
here; the hub is the intended long-form home.

| Doc | Notes |
|-----|-------|
| [context-engineering.md](context-engineering.md) | Long-form context / certification narrative |
| Root README Architecture / workflows / philosophy (now collapsed) | Pointers remain; full essay belongs on the hub |
| Localized `docs/README.*.md` (not linked from this index) | Authored translations — not mass-rewritten in Phase 1. Those files link to the repo-root README; keep them out of bot-roster static closure. |
| [aaronmarketing.ai/docs/ai-staff](https://aaronmarketing.ai/docs/ai-staff) | Placeholder Staff narrative/SEO path |

## Not docs (do not inject)

- `references/wiki/` — maintenance-time knowledge. Not a Skill, not a Runtime
  Read, not a plugin-distribution allowlist entry.
- `scripts/check-wiki.py` and other maintenance scripts — named from root
  docs when useful; `MAINTENANCE_TREES` / `MAINTENANCE_EXACT` keep them out of
  the plugin payload.
- Generated bot-roster output — outside the repository by design.

## Localized READMEs

`docs/README.*.md` are authored translations of the historical root README.
Phase 1 thins **English root `README.md` only**. Translations are left in
place so version badges and hook-term contracts stay green.
