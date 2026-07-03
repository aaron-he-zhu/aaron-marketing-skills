---
name: competitor-analysis
description: 'Use when the user asks to "analyze competitors" or "竞品分析"; benchmarks competitor keywords, content, backlinks, AI citations, and traffic share into strengths, weaknesses, and an action plan. Not for a pairwise topic-coverage gap map — use content-gap-analysis. 竞品分析/竞争对手'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when analyzing competitor SEO strategy, comparing domains, benchmarking against competitors, or finding competitor keywords and content gaps."
argument-hint: "<competitor URL or domain>"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: seo-geo
  phase: research
  geo-relevance: "medium"
---

# Competitor Analysis

Analyzes competitor SEO and GEO strategies to reveal repeatable wins, weak spots, and market gaps.

## Quick Start

```
Analyze SEO strategy for [competitor URL]
```

```
Compare my site [URL] against [competitor 1], [competitor 2], [competitor 3]
```

## Skill Contract

**Expected output**: a prioritized competitor brief plus the standard handoff summary for `memory/research/`.

- **Reads**: competitor URLs/domains, your own site metrics, business model, target audience, industry context, and any user-provided or tool data.
- **Writes**: a user-facing analysis and reusable summary.
- **Promotes**: durable competitor facts, keyword priorities, entity candidates, and pending strategy decisions to `memory/hot-cache.md`, `memory/open-loops.md`, and `memory/research/`.
- **Done when**: 3-5 competitors are benchmarked across keywords, backlinks, and traffic share in one comparison table; each strength-to-learn and weakness-to-exploit cites evidence; and the deliverable closes with an Immediate / Short-term / Long-term plan.
- **Primary next skill**: [content-gap-analysis](../content-gap-analysis/SKILL.md) when the competitive landscape is clear.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

Optional integrations: ~~SEO tool, ~~analytics, ~~AI monitor. Without tools, ask for competitor URLs, your site metrics, and industry context. See [CONNECTORS.md](../../CONNECTORS.md).

## Decision Gates

**Stop and ask** — when the competitor set cannot be established:

1. No competitors named and none inferable from `CLAUDE.md`, prior research, or the user's niche → ask the user to name 2-5 competitors, OR offer to infer them from a target keyword via [serp-analysis](../serp-analysis/SKILL.md) first.

**Continue silently** — do not stop for: which 3-5 of a longer list to deep-dive (pick the closest direct competitors and note the rest); missing your-own-site metrics (benchmark competitors against each other and mark your row N/A); missing optional tool data (label Estimated and proceed).

## Instructions

When a user requests competitor analysis:

1. **Identify Competitors** — separate direct competitors, indirect alternatives, and content competitors if the user has not named them already.
2. **Gather Competitor Data** — capture URL, domain age, estimated traffic, domain authority, business model, target audience, and key offerings.
3. **Analyze Keyword Rankings** — document total rankings, top 10/top 3 counts, high-value keywords, intent mix, and keyword gaps.
4. **Audit Content Strategy** — review content volume, top performers, publishing patterns, themes, and success factors.
5. **Analyze Backlink Profile** — review backlink totals, quality mix, top linking domains, link acquisition patterns, and linkable assets.
6. **Technical SEO Assessment** — evaluate Core Web Vitals, mobile-friendliness, architecture, internal linking, URL structure, and standout strengths/weaknesses.
7. **GEO / AI Citation Analysis** — test which queries cite competitors, what formats get cited, and where competitors still leave openings.
8. **Synthesize Competitive Intelligence** — deliver an Executive Summary, comparison table, CITE comparison, strengths to learn from, weaknesses to exploit, keyword opportunities, content recommendations, and an Immediate / Short-term / Long-term plan.

Label every metric **Measured** (tool/export), **User-provided**, or **Estimated** (model inference); never present an estimate as measured; if a required metric is unavailable, mark it N/A — do not invent it.

**Quality bar**: every strength or weakness ties to a labeled metric and a named competitor — a specific ranking or backlink figure for a named domain, not "strong content presence".

> **Reference**: See [Analysis Templates](references/analysis-templates.md) for the compact templates used at each step.

## Example

See [references/example-report.md](references/example-report.md) for a full sample analyzing HubSpot's marketing keyword dominance.

## Advanced Analysis Types

### Content Gap Analysis

For a pairwise topic-coverage gap map ("content [competitor] has that I don't, sorted by traffic potential"), hand off to [content-gap-analysis](../content-gap-analysis/SKILL.md) — that is its dedicated job.

### Video Benchmarking

When a competitor invests in video, benchmark their YouTube outliers (views >=2x their channel average) and the title/thumbnail packaging that drives those wins — those patterns show what topics and framing earn reach. See [platforms/youtube.md](../../references/platforms/youtube.md).

### Link Intersection

```
Find sites linking to [competitor 1] AND [competitor 2] but not me
```

### SERP Feature Analysis

```
What SERP features do competitors win? (Featured snippets, PAA, etc.)
```

### Historical Tracking

```
How has [competitor]'s SEO strategy evolved over the past year?
```

## Save Results

Write path: `memory/research/competitor-analysis/YYYY-MM-DD-<topic>.md`; promote durable competitor facts and entity candidates to `memory/hot-cache.md`. See [Skill Contract](../../references/skill-contract.md) §Save Results Template.

## Reference Materials

- [Analysis Templates](references/analysis-templates.md) — Step-by-step analysis templates
- [Battlecard Template](references/battlecard-template.md) — Quick-reference battlecard format
- [Positioning Frameworks](references/positioning-frameworks.md) — Positioning and differentiation frameworks
- [Example Report](references/example-report.md) — Worked sample
- [platforms/youtube.md](../../references/platforms/youtube.md) — YouTube outlier and title-packaging benchmarks for video-heavy competitors

## Next Best Skill

Primary: [content-gap-analysis](../content-gap-analysis/SKILL.md). Also: [serp-analysis](../serp-analysis/SKILL.md) and [offsite-signal-analyzer](../../monitor/offsite-signal-analyzer/SKILL.md). If the goal is a head-to-head "us vs them" page, hand the vetted competitor set to [page-play-builder](../../build/page-play-builder/SKILL.md).
