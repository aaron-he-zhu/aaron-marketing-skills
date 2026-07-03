---
name: content-gap-analysis
description: 'Use when the user asks to "find content gaps", "竞品写了什么", or "还应该写什么"; builds a competitor-relative coverage map of missing topics, keyword gaps, and editorial-calendar opportunities. Not for raw keyword demand discovery — use keyword-research. 内容缺口/选题规划'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when finding content gaps between two domains, discovering missing topics, or identifying coverage holes versus competitors."
argument-hint: "<your domain> <competitor domain>"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: seo-geo
  phase: research
  geo-relevance: "medium"
---

# Content Gap Analysis

Identifies content opportunities by comparing your site against competitors and scoring the gaps worth closing first.

## Quick Start

```
Find content gaps between my site [URL] and [competitor URLs]
```

```
What content am I missing compared to my top 3 competitors?
```

## Skill Contract

**Expected output**: a prioritized gap brief plus the standard handoff summary for `memory/research/`.

- **Reads**: your domain, competitor domains, topic/content-type focus, audience, business goals, and any user-provided or tool content inventory.
- **Writes**: a user-facing analysis and reusable summary.
- **Promotes**: durable keyword priorities, competitor facts, and pending strategy decisions to `memory/hot-cache.md`, `memory/open-loops.md`, and `memory/research/`.
- **Done when**: each prioritized gap names the competitor(s) that cover it and you don't; gaps are bucketed into Quick Wins / Strategic Builds / Long-term; and the deliverable includes a dated content calendar entry per Quick Win.
- **Primary next skill**: [content-writer](../../build/content-writer/SKILL.md) when the prioritized gap list is approved.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

Optional integrations: ~~SEO tool, ~~search console, ~~analytics, ~~AI monitor. Without tools, ask for site URL, content inventory, competitor URLs, and business goals. See [CONNECTORS.md](../../CONNECTORS.md).

**Trend-scout as a gap-discovery input (keyless)**: feed the multi-source trend scout — Google Trends RSS plus Hacker News and Reddit, via [`scripts/connectors/rss_monitor.py`](../../scripts/connectors/rss_monitor.py) — to surface rising topics your competitors and you may both miss. Treat each hit as a candidate gap, then check it against your and competitor coverage in steps 5-7. Mark these signals **Estimated**. See [CONNECTORS.md](../../CONNECTORS.md) `~~trend database`.

## Decision Gates

**Stop and ask** — gap analysis is competitor-relative and cannot run on demand alone:

1. No competitor domains given and none inferable from `CLAUDE.md` or prior research → ask the user to name 1-3 competitors, OR offer to switch to [keyword-research](../keyword-research/SKILL.md) for demand-side discovery instead.
2. Your own domain/content inventory is unavailable and cannot be fetched → ask for the site URL or a content list, since "gap" requires knowing current coverage.

**Continue silently** — do not stop for: which 3-5 named competitors to deep-dive (pick the closest); missing optional tool data (mark Estimated/N/A and proceed); ambiguous topic scope (analyze the full overlap and flag the broadest clusters).

## Instructions

When a user requests content gap analysis:

1. **Define Analysis Scope** — confirm your site, competitors, topic focus, content types, audience, and business goals.
2. **Audit Your Existing Content** — map indexed pages, content types, topic clusters, winners, and weaknesses.
3. **Analyze Competitor Content** — compare content volume, traffic, type mix, topic coverage, and unique assets.
4. **Identify Keyword Gaps** — group gaps into High Priority, Quick Wins, and Long-term based on volume, difficulty, and relevance.
5. **Map Topic Gaps** — compare topic-cluster coverage and recommend pillar / cluster approaches for missing themes.
6. **Identify Content Format Gaps** — compare guides, tutorials, comparisons, case studies, tools, templates, video, and research.
7. **Analyze GEO / AI Gaps** — identify missing Q&A, definition, and comparison content that competitors get cited for.
8. **Map to Audience Journey** — compare Awareness, Consideration, Decision, and Retention coverage.
9. **Prioritize and Create Action Plan** — deliver an Executive Summary, Prioritized Gap List (Quick Wins / Strategic Builds / Long-term), Content Calendar, and Success Metrics.

Label every metric **Measured** (tool/export), **User-provided**, or **Estimated** (model inference); never present an estimate as measured; if a required metric is unavailable, mark it N/A — do not invent it.

**Quality bar**: every gap names the competitor that covers it, its volume or traffic estimate, and why it is worth closing — never list a bare topic without that evidence.

> **Reference**: See [Analysis Templates](references/analysis-templates.md) for the compact templates used in each step.

## Example

See [references/example-report.md](references/example-report.md) for a full SaaS marketing sample.

## Advanced Analysis

### Competitive Cluster Comparison

```
Compare our topic cluster coverage for [topic] vs top 5 competitors
```

### Temporal Gap Analysis

```
What content have competitors published in the last 6 months that we haven't covered?
```

### Intent-Based Gaps

```
Find gaps in our [commercial/informational] intent content
```

## Save Results

Write path: `memory/research/content-gap-analysis/YYYY-MM-DD-<topic>.md`; promote durable gap priorities and competitor facts to `memory/hot-cache.md`. See [Skill Contract](../../references/skill-contract.md) §Save Results Template.

## Reference Materials

- [Analysis Templates](references/analysis-templates.md) — Gap-analysis templates
- [Gap Analysis Frameworks](references/gap-analysis-frameworks.md) — Audit and prioritization frameworks
- [Example Report](references/example-report.md) — Worked sample

## Next Best Skill

Primary: [content-writer](../../build/content-writer/SKILL.md).
