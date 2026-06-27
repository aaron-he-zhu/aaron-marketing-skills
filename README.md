# SEO & GEO Skills Library

**20 skills. 5 commands. Plan, audit, and monitor SEO/GEO work.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.9.10-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/aaron-he-zhu/seo-geo-claude-skills)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/commits/main)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)](https://claude.ai/download)

[English](README.md) | [中文](docs/README.zh.md)

Claude Skills and Commands for Search Engine Optimization (SEO) and Generative Engine Optimization (GEO). Skill content is zero-dependency Markdown; Claude Code hooks use a small Bash runner. Content quality uses [CORE-EEAT](https://github.com/aaron-he-zhu/core-eeat-content-benchmark) (80 items); domain trust uses [CITE](https://github.com/aaron-he-zhu/cite-domain-rating) (40 items).

## Quick Start

Install with Claude Code, any Agent Skills-compatible host, or a plain `git clone`:

| Tool | Install |
|------|---------|
| Claude Code | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` then `/plugin install aaron-seo-geo@aaron` |
| skills.sh / generic Agent Skills hosts | `npx skills add aaron-he-zhu/seo-geo-claude-skills` |
| Any host | `git clone https://github.com/aaron-he-zhu/seo-geo-claude-skills` |

Single skill: `npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research`.

If your host supports automatic skill routing, try a natural-language request:

```text
Research keywords for my SaaS product targeting small teams
```

Slash-command entrypoint when your host exposes `./commands/`:

```text
/aaron-seo-geo:auto audit https://example.com/blog/my-article
```

Optional tools are documented in [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md); every skill also works at Tier 1 with user-provided data.

## Operating Model

Every skill follows the same activation contract: Quick Start, Skill Contract, Handoff Summary, Data Sources, Instructions, Reference Materials, and Next Best Skill. Four cross-cutting skills form the protocol layer:

| Protocol skill | Role |
|----------------|------|
| `content-quality-auditor` | 80-item CORE-EEAT publish gate |
| `domain-authority-auditor` | 40-item CITE trust gate |
| `entity-optimizer` | Canonical entity profile |
| `memory-management` | HOT/WARM/COLD project memory (capture · promote · demote · archive · query) |

Shared refs: [skill-contract.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md), [state-model.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md), [auditor-runbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/auditor-runbook.md).

## Skills

<!-- SKILLS:START -->
| Phase | Skills |
|-------|--------|
| Research | [keyword-research](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/SKILL.md), [competitor-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/competitor-analysis/SKILL.md), [serp-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/serp-analysis/SKILL.md), [content-gap-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/SKILL.md) |
| Build | [seo-content-writer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/seo-content-writer/SKILL.md), [geo-content-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md), [meta-tags-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/SKILL.md), [schema-markup-generator](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/schema-markup-generator/SKILL.md) |
| Optimize | [on-page-seo-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/on-page-seo-auditor/SKILL.md), [technical-seo-checker](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/SKILL.md), [internal-linking-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/internal-linking-optimizer/SKILL.md), [content-refresher](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/SKILL.md) |
| Monitor | [rank-tracker](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/rank-tracker/SKILL.md), [backlink-analyzer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/backlink-analyzer/SKILL.md), [performance-reporter](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/SKILL.md), [alert-manager](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/alert-manager/SKILL.md) |
| Cross-cutting | [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md), [domain-authority-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/domain-authority-auditor/SKILL.md), [entity-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/SKILL.md), [memory-management](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md) |
<!-- SKILLS:END -->

## Commands

Five commands, organized by SEO/GEO intent:

| Command | Use it for |
|---------|-----------|
| `/aaron-seo-geo:auto` | Describe any goal — infers intent and runs the smallest useful workflow (`--deep` for exhaustive/stress-test) |
| `/aaron-seo-geo:research` | Keyword demand, SERP intent, competitors, content gaps, site/topic/entity maps |
| `/aaron-seo-geo:create` | Brief, write, series, refresh, CMS-neutral publish package (`--brief`/`--series`/`--refresh`/`--publish`/`--meta`/`--schema`) |
| `/aaron-seo-geo:audit` | On-page + CORE-EEAT quality, technical SEO, AI visibility, domain authority (`--full`/`--tech`/`--visibility`/`--authority`) |
| `/aaron-seo-geo:track` | Rankings, alerts, performance reports, project memory (`--alert`/`--report`/`--remember`) |

Daily work normally starts with `/aaron-seo-geo:auto`, which runs the workflow implied by your goal and stops only at blocking decisions. The other four are explicit mode entrypoints.

Breaking rename note: current commands use `/aaron-seo-geo:`. Paste any old `/seo:*` command into `/aaron-seo-geo:auto` to recover the new route; for example, `/aaron-seo-geo:auto /seo:audit-page https://example.com/blog/post` returns `/aaron-seo-geo:audit https://example.com/blog/post`.

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
