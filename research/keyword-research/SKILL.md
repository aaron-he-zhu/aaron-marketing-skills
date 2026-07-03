---
name: keyword-research
description: 'Use when the user asks to "find keywords", "挖词", or "搜什么词"; prioritizes search volume, keyword difficulty, intent, and topic clusters from provided or connected data. Not for competitor-relative coverage gaps — use content-gap-analysis. 关键词研究/内容选题'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when starting keyword research for a new page, topic, or campaign. Also when the user asks about search volume, keyword difficulty, topic clusters, long-tail keywords, what to write about, 关键词研究, 挖词, 内容选题, or 搜什么词."
argument-hint: "<topic or seed keyword> [market/language]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: seo-geo
  phase: research
  geo-relevance: "medium"
---

# Keyword Research

Discovers, scores, and clusters keywords for SEO and GEO planning.

## Quick Start

```
Research keywords for [topic/product/service]
```

```
What keywords is [competitor URL] ranking for that I should target?
```

## Skill Contract

**Expected output**: a prioritized keyword brief plus the standard handoff summary for `memory/research/`.

- **Reads**: topic or seed keyword, target market/language, business goal, site DR, and any user-provided or tool metrics.
- **Writes**: a user-facing research deliverable and reusable summary.
- **Promotes**: durable keyword priorities, competitor facts, and pending strategy decisions to `memory/hot-cache.md`, `memory/open-loops.md`, and `memory/research/`.
- **Done when**: every shortlisted keyword carries volume + difficulty + intent (or a labeled N/A); keywords are grouped into pillar + cluster hubs; and the deliverable names at least 3 prioritized Quick Win / Growth / GEO opportunities.
- **Primary next skill**: [competitor-analysis](../competitor-analysis/SKILL.md) when the keyword set is ready for market comparison.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

Optional integrations: ~~SEO tool, ~~search console. Without tools, ask for seed keywords, audience, goals, and any known metrics. See [CONNECTORS.md](../../CONNECTORS.md).

**Zero-dependency local helper** (no tool needed): `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/suggest.py" "<seed>" --expand` harvests free keyword ideas from Google Autocomplete (⚠️ unofficial endpoint). Search *volume / difficulty* still needs `~~SEO tool` or own Search Console data. See [scripts/connectors/README.md](../../scripts/connectors/README.md).

**Striking-distance shortcut** (when `~~search console` is connected): before broad discovery, mine your own GSC query data for terms already ranking in positions ~5–20 — page-one tail and page two. These are proven demand a small push can convert, so they are the fastest opportunity set. The Search Analytics API sorts by clicks and has **no position filter**, so request a high `rowLimit` and filter the 5–20 window client-side, then attach volume / difficulty / intent to that shortlist. Work this set first; treat its metrics as **Measured**.

## Instructions

When a user requests keyword research, run eight phases and announce each as `[Phase X/8: Name]`:

1. **Scope** — clarify product, audience, business goal, DR, geography, and language.
2. **Discover** — seed from core, problem, solution, audience, and industry terms.
3. **Variations** — expand with modifiers and long-tail patterns.
4. **Classify** — tag by intent (informational, navigational, commercial, transactional).
5. **Score** — assign difficulty (1-100) and compute `Opportunity = (Volume × Intent Value) / Difficulty`, with Intent Value `1 / 1 / 2 / 3`.
6. **GEO-Check** — flag AI-answer-friendly queries such as questions, definitions, comparisons, lists, and how-tos.
7. **Cluster** — group keywords into pillar + cluster topic hubs.
8. **Deliver** — output an Executive Summary, Quick Wins / Growth / GEO opportunities, Topic Clusters, Content Calendar, and Next Steps.

Label every metric **Measured** (tool/export), **User-provided**, or **Estimated** (model inference); never present an estimate as measured; if a required metric is unavailable, mark it N/A — do not invent it.

### Impact × Confidence lens (optional, layers onto Phase 5)

When you have richer signals than volume/difficulty alone, add a second pass on top of the `Opportunity` score:

- **Impact** = volume + CPC + funnel stage + trend direction (how much winning the term is worth).
- **Confidence** = difficulty + current ranking position + topic authority (how likely you are to win it).
- **Priority = Impact × Confidence** — surfaces terms that are both valuable *and* winnable, not just high-volume.

Tag each keyword by funnel stage from its pattern:

- **BOFU** — commercial/transactional, or contains "pricing", "best", "vs", "services", "agency", "hire", "buy".
- **MOFU** — informational with buying signals: "how to", "guide", "roi", "case study", "review".
- **TOFU** — pure informational (definitions, broad questions).

Work BOFU first when revenue is the goal; use TOFU/MOFU for reach and GEO answer coverage. (Impact×Confidence + funnel-stage scoring adapted from an external SEO-ops competitive analysis.)

**Quality bar**: every recommendation includes at least one specific number. Rewrite generic advice into a concrete keyword + volume + difficulty + reason.

> **Reference**: See [references/instructions-detail.md](references/instructions-detail.md) for the full 8-phase templates, expansion patterns, intent table, difficulty tiers, opportunity matrix, GEO indicators, cluster template, actionable-vs-generic examples, and advanced usage.

## Example

See [references/example-report.md](references/example-report.md) for a full worked sample.

## Save Results

Write path: `memory/research/keyword-research/YYYY-MM-DD-<topic>.md`; promote durable keyword priorities to `memory/hot-cache.md`. See [Skill Contract](../../references/skill-contract.md) §Save Results Template.

## Reference Materials

- [Instructions Detail](references/instructions-detail.md) — Workflow, scoring, cluster template, advanced usage
- [Keyword Intent Taxonomy](references/keyword-intent-taxonomy.md) — Intent signals and content mapping
- [Topic Cluster Templates](references/topic-cluster-templates.md) — Pillar and cluster patterns
- [Keyword Prioritization Framework](references/keyword-prioritization-framework.md) — Scoring and prioritization rules
- [Example Report](references/example-report.md) — Worked sample

## Next Best Skill

Primary: [competitor-analysis](../competitor-analysis/SKILL.md). Also: [content-gap-analysis](../content-gap-analysis/SKILL.md) and [serp-analysis](../serp-analysis/SKILL.md).
