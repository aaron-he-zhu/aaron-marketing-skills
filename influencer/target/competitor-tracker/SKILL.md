---
name: competitor-tracker
slug: aaron-competitor-tracker
displayName: "Competitor Tracker · 竞对红人追踪"
summary: "竞品创作者合作动向:合作名单、投放节奏与策略启示"
description: 'Use when the user asks to "track competitor influencer marketing", "see who my rivals partner with", or "benchmark my influencer program"; produces a competitor partnership roster, campaign and content-strategy breakdown, performance estimates, and a gap/opportunity list. Not for finding your own new creators — use influencer-discovery. 竞品达人合作追踪/竞品营销分析'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when the user wants to understand a competitor's influencer marketing: which creators they partner with, what campaigns and content formats they run, estimated reach and spend, and where they leave gaps. Activate for competitive benchmarking, finding untapped or former-competitor creators, and spotting strategy shifts over time."
argument-hint: "<your brand> [competitor names] [platform]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "target", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "target"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Competitor Tracker

Monitor and analyze competitors' influencer marketing: who they partner with, what campaigns they run, how they structure collaborations, and what results they appear to achieve.

## Quick Start

Shortest invocation:

```
Monitor [competitor name]'s influencer marketing activities
```

Compare a set of rivals and surface gaps:

```
Compare influencer strategies across [competitor 1], [competitor 2], and [competitor 3], then show me which influencers they're missing in [category]
```

## Skill Contract

- **Reads**: your brand name, competitor set, platforms, time period, focus areas, and dated source records. Raw handles/profile URLs may be used transiently to resolve evidence, but saved/report/handoff creator identity uses only opaque `creator_ref`.
- **Writes**: return the competitive intelligence report inline by default; save it to `memory/influencer/competitor-tracker/YYYY-MM-DD-<topic>.md` only with exact WARM-save authorization.
- **Promotes**: only with separate exact authorization, promote durable facts (named competitors, their primary tiers/platforms, confirmed exclusive partners, recurring campaign windows) to `memory/hot-cache.md`. Each competitor-partner or exclusivity update for a rostered creator requires another exact authorization for an `operation: propose` request through `registry-events.py` to `memory/events/creators.ndjson`; only [creator-registry](../../../protocol/creator-registry/SKILL.md) can reconcile it into canonical state.
- **Done when**:
  1. Each tracked competitor has a partnership roster and campaign breakdown whose factual rows carry source ref, observation date, and window; otherwise the run returns `NEEDS_INPUT` with a collection plan.
  2. A side-by-side comparison table covers your brand plus every competitor.
  3. At least 3 ranked opportunities (untapped creators, strategy gaps, or open platforms) are listed.
- **Primary next skill**: [campaign-planner](../campaign-planner/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

Tier 1 can produce the tracking schema and exact collection/query plan. Named partners, campaigns, current activity, content patterns, and performance facts require dated user records, public-post evidence, or live connector results. Without them, return `NEEDS_INPUT`; do not reconstruct a roster or strategy from general knowledge. Estimates require an explicit formula and input refs and are never partnership facts.

Where a tool could speed things up, use `~~` connector placeholders:

- `~~influencer database` — pull a competitor's known partner roster and tier mix.
- `~~social platform analytics` — estimate reach, engagement rate, and post cadence per creator.
- `~~CRM` — cross-check whether a former competitor partner has already touched your pipeline.

**Keyless news read on rivals**: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/gdelt.py" '"<competitor>"' --days 30` lists index results with source URLs/dates. Label the retrieval Measured for the index query only; an article result does not verify a creator partnership or exclusivity until the underlying dated source explicitly supports it. See [scripts/connectors/README.md](../../../scripts/connectors/README.md).

**Rival-partner channel watch (free key / keyless)**: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" channel <partner-handle>` reads a competitor partner's real subscriber/view counts (free `YOUTUBE_API_KEY`), and every YouTube channel also has a **keyless RSS feed** — `https://www.youtube.com/feeds/videos.xml?channel_id=UC…` piped into `rss_monitor.py` — for tracking partner posting cadence and spotting a burst of sponsored content without any API at all.

Label every estimate as an estimate. See [CONNECTORS.md](../../../CONNECTORS.md) for the keyless/free recipe per category.

## Instructions

Each step has a fill-in template in [references/templates.md](references/templates.md).

1. **Define competitive set** — capture your brand, prioritized competitors (direct/indirect), platforms, time period, and focus areas. ([template](references/templates.md#1-define-competitive-set))
2. **Track influencer partnerships** — build current/recent rosters only from dated explicit partnership evidence. Use `creator_ref` in all durable output; never infer exclusivity. ([template](references/templates.md#2-track-influencer-partnerships))
3. **Analyze campaigns** — break down evidenced campaigns and retain source/date/window per fact. Replace “what worked” causation with observed association plus a labeled hypothesis. ([template](references/templates.md#3-analyze-campaigns))
4. **Review content strategy** — log format preferences, content themes, messaging, hashtag strategy, and creative direction. ([template](references/templates.md#4-review-content-strategy))
5. **Estimate performance** — only when the formula, source inputs, compatibility, and window are declared. Otherwise leave metrics `TBD/NEEDS_INPUT`. ([template](references/templates.md#5-estimate-performance))
6. **Generate competitive comparison** — a side-by-side table (your brand + every competitor), a strategy-element matrix, and a share-of-voice bar. ([template](references/templates.md#6-generate-competitive-comparison))
7. **Identify opportunities** — rank untapped and former-competitor creators, strategy gaps, and platform/niche/format openings (at least 3 ranked). ([template](references/templates.md#7-identify-opportunities))
8. **Generate insights report** — executive summary, strategic recommendations (immediate/short/long-term), tracking recommendations, and next review date. Return it inline and offer the exact WARM save path; do not save, promote, or propose registry facts without their separate authorizations. ([template](references/templates.md#8-generate-insights-report))

## Worked Example

**User**: "Track the influencer marketing activities of Glossier, Fenty Beauty, and Rare Beauty"

**Output**: `NEEDS_INPUT`. The names alone do not evidence current partners or strategies. Return exact public-post/news/provider queries and required source/date/window fields; do not name partners, characterize strategy, estimate performance, or rank opportunities until dated evidence arrives. Full invocation patterns live in [references/templates.md](references/templates.md#when-to-use-this-skill).

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in templates for all 8 steps, invocation patterns, worked example, and tips.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — keyless/free data recipe per `~~` connector category.
- Sibling Scout skills: [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — find creators competitors aren't using; [fit-scorer](../../scout/fit-scorer/SKILL.md) — score competitor partners for your brand.
- [trend-spotter](../../scout/trend-spotter/SKILL.md) — spot trends competitors are riding.

## Next Best Skill

- **Primary**: [campaign-planner](../campaign-planner/SKILL.md) — turn competitive gaps into a differentiated campaign.
- **Alternate (Scout)**: [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — pursue the untapped and former-competitor creators this analysis surfaced.
- **Alternate (Scout)**: [fit-scorer](../../scout/fit-scorer/SKILL.md) — score a competitor's roster against your brand before you poach.

Termination note: keep a visited-set of skills invoked this session. If the next skill has already run this session, stop and report the chain complete instead of re-invoking. Max chain depth is 3 hops.
