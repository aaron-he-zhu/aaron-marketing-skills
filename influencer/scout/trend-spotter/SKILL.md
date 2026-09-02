---
name: trend-spotter
slug: trend-spotter
displayName: "Trend Spotter · 趋势侦察"
summary: "排名化趋势报告:品牌契合评分、rising/peak/declining 判断与 go/skip 建议"
description: 'Use when the user asks to "find trending topics", "what trends should my brand jump on", or "time a campaign around a cultural moment"; produces a ranked trend report with brand-fit scores, format calls (rising/peak/declining), a cultural calendar, and go/skip recommendations. Not for finding the creators to run those trends — use influencer-discovery; not for building the brand posting calendar from a go verdict — use social-calendar-builder. 热点趋势洞察/借势营销'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when planning campaign timing and themes, deciding whether to join a hashtag, sound, or challenge, scouting trending content formats on a platform, mapping upcoming cultural moments to lead times, or checking which trends competitors have adopted or missed. Auto-activate when the request is about what is trending, what to post around, or when to act."
argument-hint: "<brand or industry> [platform] [time horizon]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "scout", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "scout"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Trend Spotter

This skill helps you identify and capitalize on trends that matter to your audience. It monitors social conversations, emerging topics, viral content formats, and cultural moments to inform influencer campaign timing and content strategy.

## Quick Start

Shortest invocation:

```
What trends are relevant for [brand/industry] right now?
```

Common scenario — analyze one specific trend before committing:

```
Should [brand] participate in [trend/challenge]? Score the brand fit and give a go/skip call.
```

## Skill Contract

- **Reads**: brand/industry, target platforms, audience, geographic focus, time horizon, content categories; prior audience and niche findings from `memory/influencer/` if present.
- **Writes**: return the trend report inline by default; save it to `memory/influencer/trend-spotter/YYYY-MM-DD-<topic>.md` only with exact authorization for that WARM path.
- **Promotes**: only with separate exact authorization, promote durable facts (top trends to act on now, trends to avoid, next review date) to `memory/hot-cache.md`.
- **Done when**:
  1. Every named current trend, volume/growth/status claim, cultural moment, and competitor-adoption claim has a dated source ref plus the requested platform, geography, observation window, metric definition, and momentum comparison.
  2. Each candidate with complete current evidence for that exact scope has a brand-fit score and a go / caution / skip call; RSS/title overlap alone remains a `Proxy candidate` with `score_state: NOT_SCORED`.
  3. The report names the top 3 trends, watch list, and avoid list only when current evidence supports them; otherwise it returns `NEEDS_INPUT` with an exact query/collection plan.
- **Primary next skill**: [influencer-discovery](../influencer-discovery/SKILL.md) — find the creators who can execute the chosen trends.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

The intake and query plan work with no live integration. A report about what is current does not: it requires dated user-supplied evidence, a public fetch, or a live connector result for the requested platform, geography, and horizon. Brand inputs alone support search terms and evaluation criteria, not trend names, counts, growth, rising/peak/declining calls, or go/skip recommendations. Without current evidence, return `NEEDS_INPUT` and the exact queries/fields to collect. Where a tool supplies the read, use a `~~` connector placeholder:

- `~~social platform analytics` — trending hashtags, sounds, and view counts per platform.
- `~~trend database` — emerging topics, challenge participation, and growth rates.
- `~~social listening` — cultural conversations and sentiment around a topic.
- `~~competitor tracking` — which trends rival brands have adopted and how they performed.

No connector is required to produce a useful **query plan**. A named current-trend report requires the source records above. See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category.

For a keyless way to discover topics worth measuring, run the multi-source candidate scout — Google Trends RSS + Hacker News + Reddit + YouTube upload titles via the bundled stdlib `rss_monitor.py` (no new dependency): [references/trend-scout-recipe.md](references/trend-scout-recipe.md). RSS/title overlap is only a `Proxy candidate` and stays `NOT_SCORED`; it does not establish a platform trend, view-count outlier, lifecycle state, or act-now recommendation. This is the Tier-1 candidate recipe behind `~~trend database` (Google Trends RSS).

**Keyless news pulse (Tavily)**: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/tavily.py" search "<vertical or candidate trend>" --topic news --time-range w --limit 10` adds recency-filtered discovery refs. Agreement with an RSS title may raise query priority, but it remains a `Proxy candidate/NOT_SCORED`; news overlap does not prove momentum on TikTok, Reels, YouTube, or another requested platform.

**Keyless source-specific sharpeners**: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/pageviews.py" "<Topic_Article>" --granularity daily --days 30` measures Wikipedia page attention, and the Hacker News Algolia API (`https://hn.algolia.com/api/v1/search?query=<topic>`, keyless) measures HN points/comments. Those values are Measured only for their named source and window. Treat them as Proxy for a different requested platform; require dated momentum from the exact platform/geography/window before any rising / peak / declining or act-now call.

## Instructions

When a user requests trend analysis, run these steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — copy the matching block and populate it.

1. **Define trend parameters** — capture brand/industry, platforms, audience, geographic focus, time horizon, and content categories. (Template: Step 1.)
2. **Qualify current evidence** — for every candidate topic, hashtag, audio, challenge, format, cultural moment, and competitor observation, retain source ref, observed/retrieved date, measurement window, platform/geography, metric definition, current value, and comparable prior value. RSS/title overlap alone stays `Proxy candidate/NOT_SCORED`. Missing current evidence stops factual output and yields the query plan. (Template: Step 2.)
3. **Analyze content format trends** — list rising/peak/declining formats only from a dated momentum series for the exact requested platform/geography/window; label explanations as observed association or hypothesis, never unsupported causation. (Template: Step 3.)
4. **Track cultural moments** — source dates and current conversation/sentiment claims; otherwise return calendar/search fields as `TBD`. (Template: Step 4.)
5. **Assess trend relevance** — score only evidence-backed candidates on audience alignment, brand value fit, content adaptability, risk, and timing (X/25). Unsupported candidates remain `NOT_SCORED` with no go/caution/skip call. (Template: Step 5.)
6. **Monitor competitor trend adoption** — require dated post/campaign evidence; do not infer adoption, performance, gaps, or overuse from general brand knowledge. (Template: Step 6.)
7. **Generate the trend report** — fill top-3-act-now, watch, avoid, timed action, format, and hashtag blocks only for candidates that pass the complete current-evidence gate for the exact platform/geography/window; otherwise leave those blocks `TBD` and return `NEEDS_INPUT` with the collection plan. Return it inline; offer the exact WARM save path, then ask separately before any HOT promotion. (Template: Step 7.)

For repeatable monitoring, return any proposed ledger write as an inline plan first. Do not run `ledger.py record` until the user gives a separate exact authorization naming the normalized ledger path, the `record` operation, and the exact source/topic/platform/geography/window scope. Report-save or HOT-promotion authorization never covers that write.

## Example

**User**: "What TikTok trends should a fitness brand run right now?"

Output is `NEEDS_INPUT` because the prompt supplies no dated TikTok evidence. It returns platform/geography/window-specific queries for topic, hashtag, sound, format, safety, and competitor-adoption records, plus the fields `source_ref`, `observed_at`, and `measurement_window`. It names no trend, count, status, hashtag, format winner, or this-week action until those records arrive. Full version: [references/templates.md](references/templates.md#extended-example--tiktok-fitness-trends).

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in templates for every step, the extended worked example, and execution tips.

- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — HOT/WARM/COLD memory tiers and save paths.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipe per connector category.
- STAR benchmark scoring at [references/star-benchmark.md](../../../references/star-benchmark.md) — for grading trend-driven creative output downstream.
- Siblings in the scout phase: [audience-mapper](../audience-mapper/SKILL.md), [influencer-discovery](../influencer-discovery/SKILL.md), [fit-scorer](../fit-scorer/SKILL.md).

## Next Best Skill

- **Primary**: [influencer-discovery](../influencer-discovery/SKILL.md) — turn the chosen trends into a shortlist of creators who can execute them.
- **Alternate**: [audience-mapper](../audience-mapper/SKILL.md) — confirm which trends actually resonate with your audience before committing.
- **Alternate**: [fit-scorer](../fit-scorer/SKILL.md) — score which creators fit the chosen trends and the brand before committing.

Termination: keep a visited-set of skills invoked this session. If the primary next skill was already run this turn, stop and report the chain complete rather than re-invoking. Max handoff depth is 3; once reached, summarize and return control to the user.
