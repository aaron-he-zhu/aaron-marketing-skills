# SEO & GEO Skills Library — Claude Code Context

This plugin provides **20 skills and 20 commands** for Search Engine Optimization (SEO) and Generative Engine Optimization (GEO). All 20 skills follow one shared contract: trigger, quick start, skill contract, handoff summary, and next best skill. Skills are auto-loaded by context; commands are invoked with `/aaron:` on hosts that expose command playbooks. Codex loads the pack through `.codex-plugin/plugin.json` and the repo marketplace `.agents/plugins/marketplace.json`. Current bundle version: `9.9.9` (see [VERSIONS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)).

## Skills by Phase

| Phase | Skills |
|-------|--------|
| **Research** | `keyword-research`, `competitor-analysis`, `serp-analysis`, `content-gap-analysis` |
| **Build** | `seo-content-writer`, `geo-content-optimizer`, `meta-tags-optimizer`, `schema-markup-generator` |
| **Optimize** | `on-page-seo-auditor`, `technical-seo-checker`, `internal-linking-optimizer`, `content-refresher` |
| **Monitor** | `rank-tracker`, `backlink-analyzer`, `performance-reporter`, `alert-manager` |
| **Cross-cutting / Protocol** | `content-quality-auditor`, `domain-authority-auditor`, `entity-optimizer`, `memory-management` |

## One-Shot Commands

**SEO/GEO pack-local Product API commands (2)** — day-to-day SEO/GEO work starts with `/aaron:auto`; `/aaron:max` is only for explicit maximum-depth, exhaustive, or stress-test work inside this pack.

**User commands (17, including the two Product API entries)** — expert reference shortcuts. Not sure? Use `/aaron:auto`:

```
/aaron:auto       — Infer SEO/GEO intent and route to the smallest useful pack-local workflow
/aaron:max        — Explicit maximum-depth, exhaustive, or stress-test SEO/GEO workflow
/aaron:discover   — Keyword demand, SERP intent, topic clusters
/aaron:compete    — Competitor SEO/GEO, gaps, backlinks
/aaron:map        — Site/topic/entity map and internal-link architecture
/aaron:brief      — Executable content brief
/aaron:write      — One SEO/GEO content asset
/aaron:series     — Plan, write, continue, or hand off a series
/aaron:refresh    — Update stale or declining content
/aaron:publish    — CMS-neutral publish package
/aaron:audit      — On-page SEO + CORE-EEAT audit
/aaron:visibility — AI answer visibility and GEO citation readiness
/aaron:tech       — Technical SEO health check
/aaron:authority  — CITE, trust, backlinks, entity authority
/aaron:watch      — Rankings, alerts, AI citation checks, GEO drift
/aaron:report     — Performance report
/aaron:remember   — Project memory lifecycle
```

**Maintenance commands (3)** — for library maintainers / power users. Safe to ignore for daily use:

```
/aaron:skillify — Audit proposed or changed skills, commands, routes, evals, and release impact
/aaron:evolve   — Draft evidence-backed controlled evolution proposals; proposal-only, no edits
/aaron:guard    — Run eval, contract, wiki, version, release, and guardrail checks
```

## Quality Frameworks

- **CORE-EEAT** ([references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)): 80-item content quality framework (8 dimensions). GEO Score = CORE avg; SEO Score = EEAT avg. Three veto items: T04, C01, R10.
- **CITE** ([references/cite-domain-rating.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/cite-domain-rating.md)): 40-item domain authority framework (4 dimensions). Three veto items: T03, T05, T09.

## Operating Contract

- Shared contract reference: [references/skill-contract.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md)
- Shared state model: [references/state-model.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md)
- Protocol roles:
  - `content-quality-auditor` = publish readiness gate
  - `domain-authority-auditor` = citation trust gate
  - `entity-optimizer` = canonical entity profile
  - `memory-management` = campaign memory loop
- Hook automation: `hooks/hooks.json` — command-backed hooks for SessionStart, UserPromptSubmit, PostToolUse checks, and a silent allow-only Stop check
- Temperature memory: HOT (`memory/hot-cache.md`, 80 lines, auto-loaded) / WARM (`memory/` subdirs) / COLD (`memory/archive/`)
- Wiki compilation view: `memory/wiki/` — auto-refreshed structured index of WARM files (Phase 1), compiled pages with conversational reconciliation (Phase 2), and user-initiated WARM retirement to COLD with full recovery path (Phase 3). Project isolation via `<project>/index.md`, 健康度 scoring, user-tier guidance. See [wiki-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/references/wiki-runbook.md) for execution detail. Delete `memory/wiki/` to revert without losing retirement history (COLD frontmatter preserves `originally_at`; recovery via `scripts/recover-retired-warm.sh`). Design history archived in [proposal-wiki-layer-v3.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/proposal-wiki-layer-v3.md); v9.9.9 implementation in [proposal-wiki-phase-2-3-completion.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/proposal-wiki-phase-2-3-completion.md).
- Dual truncation: HOT tier limited to 80 lines AND 25KB (whichever triggers first)

## Inter-Skill Handoff

When a skill recommends running another, pass: objective, key findings/output, evidence, open loops, target keyword, content type, completion status (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_INPUT), CORE-EEAT dimension scores (e.g., `C:75 O:60 R:80 E:45`), CITE scores, priority item IDs, and content URL.

If `memory-management` is active, prior audit results load automatically from the hot cache in this [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) file.

## Tool Connector Pattern

Skills use `~~category` placeholders (e.g., `~~SEO tool`, `~~analytics`). Every skill works without any integrations (Tier 1). MCP servers in `.mcp.json` add Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack.

## Contribution Rules

- All `SKILL.md` files must include: `name`, `version`, `description`, `license`, `compatibility`, `metadata` frontmatter. Recommended: `when_to_use` (underscores, not hyphens) and `argument-hint`.
- `.claude-plugin/plugin.json` must include: `id` and `description` at top level. Commands auto-discovered from `./commands/` directory; skills listed as directory paths
- `.codex-plugin/plugin.json` must include Codex package metadata, `skills`, optional `mcpServers`, and `interface` install-surface copy. Keep manifest paths relative to the repository/plugin root and starting with `./`; this repository uses `skills: "./"` so Codex recursively discovers nested skill directories.
- Keep `SKILL.md` body under 350 lines — move detail to `references/` subdirectories. **Exception**: protocol-layer auditor skills (currently `content-quality-auditor` and `domain-authority-auditor`) may inline the authoritative Auditor Runbook §1-5 (~270 lines) directly in their SKILL.md body, bringing them to a ~750 line ceiling. Inlining is required because markdown-linked references do not execute reliably at skill activation. The inline block is delimited by `<!-- runbook-sync start: source_sha256=... block_sha256=... -->` markers and validated by `/aaron:guard --contracts`. See [references/decisions/2026-04-adr-001-inline-auditor-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/decisions/2026-04-adr-001-inline-auditor-runbook.md).
- High-volume `references/` packs should prefer compact starter templates, step matrices, and checklists over long worked outlines. Keep canonical examples only where they materially improve execution quality.
- **New auditor-class skill authors**: start with [references/AUDITOR-AUTHORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/AUDITOR-AUTHORS.md) — template skeleton, veto registration checklist, anti-patterns, and sync procedure.
- After updating a skill: update all tracking files — `VERSIONS.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `marketplace.json` (repo root), `README.md`, and this `CLAUDE.md`. Marketplace ownership and platform-specific install rules are centralized in [marketplaces/README.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/marketplaces/README.md). The root `marketplace.json` is mirrored to `.claude-plugin/marketplace.json` (both must be byte-identical — see [#8](https://github.com/aaron-he-zhu/seo-geo-claude-skills/issues/8) for why they can't be a symlink). The CI script `.github/scripts/sync-skills.js` keeps them in sync automatically. `/aaron:guard --release` catches drift.
- Version bumps also sync cross-agent manifests listed in [marketplaces/README.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/marketplaces/README.md), including `gemini-extension.json`, `qwen-extension.json`, `.codebuddy-plugin/marketplace.json`, and `.agents/plugins/marketplace.json`. Run `/aaron:guard --versions --apply` after editing `.claude-plugin/plugin.json` to propagate the version, then run `bash scripts/validate-slimming-guardrails.sh`.
- Design philosophy: the repo is content-only — no `.py` scripts. Developer utilities are either bash (`scripts/validate-skill.sh`) or pure-markdown slash commands. If a new utility is needed, add it as a `commands/*.md` file and mark it a maintenance command.
- Keep the shared contract and state-model language consistent with `references/skill-contract.md` and `references/state-model.md`
- Branch naming: `feature/skill-name`, `fix/skill-name`, `docs/description`

## CLI Tools

System PATH in Claude Code sessions is minimal (`/usr/bin:/bin:/usr/sbin:/sbin`). Tools installed via Homebrew or npm are NOT on PATH by default. Always use absolute paths:

- **gh** (GitHub CLI): `/opt/homebrew/bin/gh`
- **clawhub** (ClawHub CLI): `/usr/local/bin/clawhub` (requires node at `/usr/local/bin/node`)
- **node**: `/usr/local/bin/node`
- **bun**: `~/.bun/bin/bun`

Or prepend PATH at start of command: `export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"; gh ...`

### ClawHub / OpenClaw Publishing

OpenClaw bundle installs use `openclaw.plugin.json` and must provide host smoke evidence before claiming all 20 `/aaron:*` commands. Skill-only ClawHub publishing remains individual and does not prove slash-command exposure.

```bash
# Auth check
/usr/local/bin/clawhub whoami

# Publish one skill
/usr/local/bin/clawhub publish <category>/<slug> --version X.Y.Z --changelog "text" --tags latest --no-input

# Publish all discovered skills (batch)
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
find research build optimize monitor cross-cutting -mindepth 2 -maxdepth 2 -name SKILL.md -print | sort | while read -r file; do
  dir="$(dirname "$file")"
  clawhub publish "$dir" --version X.Y.Z --changelog "text" --tags latest --no-input
done
```

### GitHub Release

```bash
/opt/homebrew/bin/gh release create vX.Y.Z --title "title" --notes "body"
```

> [AGENTS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/AGENTS.md) · [README.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/README.md) · Install: [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)
