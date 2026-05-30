# SEO & GEO Skills Library

**21 skills. 20 commands. Plan, audit, monitor, and analyze SEO/GEO work.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.9.9-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/aaron-he-zhu/seo-geo-claude-skills)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/commits/main)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)](https://claude.ai/download)

[English](README.md) | [中文](docs/README.zh.md)

Claude Skills and Commands for Search Engine Optimization (SEO) and Generative Engine Optimization (GEO). This repository is the candidate SEO/GEO anchor capability pack for slash-aaron. Skill content is zero-dependency Markdown; Claude Code hooks use a small Bash runner. Install targets and support claims are maintained in the [Marketplace Module](marketplaces/README.md) and [platform registry](distribution/platforms.json). Content quality uses [CORE-EEAT](https://github.com/aaron-he-zhu/core-eeat-content-benchmark) (80 items); domain trust uses [CITE](https://github.com/aaron-he-zhu/cite-domain-rating) (40 items).

## Quick Start

Common install paths are below. Support level, evidence, manifest ownership, and release rules live in [marketplaces/README.md](marketplaces/README.md) and [distribution/platforms.json](distribution/platforms.json).

| Tool | Install |
|------|---------|
| Claude Code | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` |
| ClawHub.ai / OpenClaw | `clawhub install aaron-he-zhu/<skill>` or [bundle](https://clawhub.ai/plugins/aaron-seo-geo) |
| Gemini CLI | `gemini extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| Qwen Code | `qwen extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| Amp | `amp skill add aaron-he-zhu/seo-geo-claude-skills` |
| Kimi Code CLI | `kimi plugin install https://github.com/aaron-he-zhu/seo-geo-claude-skills.git` |
| CodeBuddy | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` then `/plugin install aaron-seo-geo` |
| skills.sh / generic Agent Skills hosts | `npx skills add aaron-he-zhu/seo-geo-claude-skills` |

Single skill: `npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research`.

If your host supports automatic skill routing, try a natural-language request:

```text
Research keywords for my SaaS product targeting small teams
```

Slash-command entrypoint when your host exposes `./commands/`:

```text
/aaron:auto audit https://example.com/blog/my-article
```

Optional tools are documented in [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md); every skill also works at Tier 1 with user-provided data.

## Operating Model

Every skill follows the same activation contract: Quick Start, Skill Contract, Handoff Summary, Data Sources, Instructions, Reference Materials, and Next Best Skill. Five cross-cutting skills form the protocol and shared-workflow layer:

| Protocol skill | Role |
|----------------|------|
| `content-quality-auditor` | 80-item CORE-EEAT publish gate |
| `domain-authority-auditor` | 40-item CITE trust gate |
| `entity-optimizer` | Canonical entity profile |
| `memory-management` | HOT/WARM/COLD project memory + wiki layer (compile · query · contradiction-resolution · retire · restore; v9.9.9+) |
| `data-flow-skill` | Dataset analysis, visualization, structured findings, reports, and slide-ready outputs |

Shared refs: [skill-contract.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md), [state-model.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md), [auditor-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/auditor-runbook.md).

### Wiki Layer (v9.9.9+)

Project memory matures from raw WARM files → derived wiki pages → optional retirement of covered WARM into COLD. Three phases:
- **Phase 1** — auto-refreshed `memory/wiki/index.md` (Phase 1 is automatic; no user action needed)
- **Phase 2** — compiled wiki pages: type `"compile a wiki page on X"` / `"synthesize what we know about X"` / `"整理一下X的资料"` once you have ≥3 WARM files referencing entity X. Contradictions surface at next session as `(a)/(b)/(s)/(i)` prompt.
- **Phase 3** — user-initiated retirement: `/aaron:guard --wiki --retire-preview` lists candidates; explicit confirmation moves WARM to `memory/archive/`. Recover any time by saying `/aaron:remember recover wiki` (memory-management runs the recovery for you). Power users can also `bash scripts/recover-retired-warm.sh` directly.

`rm -rf memory/wiki/` always reverts cleanly. Retirement history (Phase 3) survives in COLD frontmatter — not destroyed by wiki deletion. See [wiki-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/references/wiki-runbook.md) for full execution detail.

## Skills

<!-- SKILLS:START -->
| Phase | Skills |
|-------|--------|
| Research | [keyword-research](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/SKILL.md), [competitor-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/competitor-analysis/SKILL.md), [serp-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/serp-analysis/SKILL.md), [content-gap-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/SKILL.md) |
| Build | [seo-content-writer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/seo-content-writer/SKILL.md), [geo-content-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md), [meta-tags-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/SKILL.md), [schema-markup-generator](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/schema-markup-generator/SKILL.md) |
| Optimize | [on-page-seo-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/on-page-seo-auditor/SKILL.md), [technical-seo-checker](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/SKILL.md), [internal-linking-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/internal-linking-optimizer/SKILL.md), [content-refresher](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/SKILL.md) |
| Monitor | [rank-tracker](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/rank-tracker/SKILL.md), [backlink-analyzer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/backlink-analyzer/SKILL.md), [performance-reporter](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/SKILL.md), [alert-manager](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/alert-manager/SKILL.md) |
| Cross-cutting | [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md), [domain-authority-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/domain-authority-auditor/SKILL.md), [entity-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/SKILL.md), [memory-management](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md), [data-flow-skill](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/data-flow-skill/SKILL.md) |
<!-- SKILLS:END -->

## Commands
SEO/GEO pack-local entries: `/aaron:auto`; exceptional maximum-depth mode: `/aaron:max` (both included in user-facing commands below).
User commands: `/aaron:auto`, `/aaron:max`, `/aaron:discover`, `/aaron:compete`, `/aaron:map`, `/aaron:brief`, `/aaron:write`, `/aaron:series`, `/aaron:refresh`, `/aaron:publish`, `/aaron:audit`, `/aaron:visibility`, `/aaron:tech`, `/aaron:authority`, `/aaron:watch`, `/aaron:report`, `/aaron:remember`.

Maintenance commands: `/aaron:skillify`, `/aaron:evolve`, `/aaron:guard`.

Daily SEO/GEO work normally starts with `/aaron:auto`, which runs the SEO/GEO pack-local workflow implied by your goal and stops only at blocking decisions. Use `/aaron:max` only when you explicitly want maximum-depth, exhaustive, or stress-test analysis inside this pack. The remaining commands are expert shortcuts for repeatable jobs. Use `/aaron:skillify` to review proposed skills or routes, `/aaron:evolve` for controlled library changes from evidence, and `/aaron:guard` for maintainer validation.

Breaking rename note: current commands use `/aaron:`. Paste any old `/seo:*` command into `/aaron:auto` to recover the new route; for example, `/aaron:auto /seo:audit-page https://example.com/blog/post` returns `/aaron:audit https://example.com/blog/post`.

Command files: [commands/](https://github.com/aaron-he-zhu/seo-geo-claude-skills/tree/main/commands/).

## Recommended Workflow

1. Research: `keyword-research` -> `competitor-analysis` -> `content-gap-analysis`.
2. Build: `seo-content-writer` -> `geo-content-optimizer` -> `meta-tags-optimizer` / `schema-markup-generator`.
3. Optimize: `content-quality-auditor` -> `on-page-seo-auditor` -> `technical-seo-checker`.
4. Monitor: `rank-tracker` -> `performance-reporter` -> `alert-manager`.

For a full trust review, pair `content-quality-auditor` with `domain-authority-auditor` for a 120-item assessment. If `memory-management` is active, handoffs and open loops are retained in HOT/WARM/COLD memory.

## References

| Reference | Purpose |
|-----------|---------|
| [core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md) | 80-item content quality benchmark |
| [cite-domain-rating.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/cite-domain-rating.md) | 40-item domain authority benchmark |
| [auditor-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/auditor-runbook.md) | Auditor handoff schema, cap arithmetic, artifact gate |
| [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md) | Optional MCP/tool connector tiers |
| [marketplaces/README.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/marketplaces/README.md) | Marketplace install matrix and release-surface ownership |

## Contributing

See [CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md). Release state is tracked in [VERSIONS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md); security guidance is in [SECURITY.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/SECURITY.md).

## Disclaimer

These skills assist SEO/GEO workflows but do not guarantee rankings, AI citations, traffic, legal compliance, or business outcomes. Verify recommendations with qualified professionals before relying on them for major strategy or legal decisions.

## License

Apache License 2.0

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Fseo-geo-claude-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&legend=top-left" />
 </picture>
</a>
