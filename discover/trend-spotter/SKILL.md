---
name: trend-spotter
description: 'Use when the user asks to "find trending topics", "what trends should my brand jump on", or "time a campaign around a cultural moment"; produces a ranked trend report with brand-fit scores, format calls (rising/peak/declining), a cultural calendar, and go/skip recommendations. Not for finding the creators to run those trends — use influencer-discovery.'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when planning campaign timing and themes, deciding whether to join a hashtag, sound, or challenge, scouting trending content formats on a platform, mapping upcoming cultural moments to lead times, or checking which trends competitors have adopted or missed. Auto-activate when the request is about what is trending, what to post around, or when to act."
argument-hint: "<brand or industry> [platform] [time horizon]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: influencer
  phase: discover
  family: influencer-marketing
  impact-phase: Insight
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
- **Writes**: a trend report (ranked trends, brand-fit scores, format calls, cultural calendar, go/skip recommendations) to `memory/influencer/trend-spotter/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable facts (top trends to act on now, trends to avoid, next review date) to `memory/hot-cache.md`.
- **Done when**:
  1. Each candidate trend has a brand-fit score and a go / caution / skip call.
  2. The report names the top 3 trends to act on now plus a watch list and an avoid list.
  3. Action items carry a timing window and a content-format recommendation.
- **Primary next skill**: [influencer-discovery](../../discover/influencer-discovery/SKILL.md) — find the creators who can execute the chosen trends.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This skill works with no live integrations (Tier 1): ask the user for the brand, platforms, audience, and time horizon, then reason from those inputs. Where a tool would sharpen the read, use a `~~` connector placeholder:

- `~~social platform analytics` — trending hashtags, sounds, and view counts per platform.
- `~~trend database` — emerging topics, challenge participation, and growth rates.
- `~~social listening` — cultural conversations and sentiment around a topic.
- `~~competitor tracking` — which trends rival brands have adopted and how they performed.

No connector is required to produce a useful report. See [CONNECTORS.md](../../CONNECTORS.md) for the free/keyless recipe per category.

For a keyless way to fill the trending tables with real signal, run the multi-source trend scout — Google Trends RSS + Hacker News + Reddit + YouTube-outlier, scored against the brand's verticals via the bundled stdlib `rss_monitor.py` (no new dependency): [references/trend-scout-recipe.md](references/trend-scout-recipe.md). This is the Tier-1 recipe behind `~~trend database` (Google Trends RSS).

## Instructions

When a user requests trend analysis, run these steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — copy the matching block and populate it.

1. **Define trend parameters** — capture brand/industry, platforms, audience, geographic focus, time horizon, and content categories. (Template: Step 1.)
2. **Identify current trends** — log trending topics, hashtags, audio/sounds, and challenges with volume, growth, lifespan, and brand-safety flags. (Template: Step 2.)
3. **Analyze content format trends** — list hot, emerging, and declining formats per platform with how-to-adapt notes. (Template: Step 3.)
4. **Track cultural moments** — build the cultural calendar (events + lead times), conversations to join vs avoid, and seasonal opportunities. (Template: Step 4.)
5. **Assess trend relevance** — for each candidate trend, score audience alignment, brand value fit, content adaptability, risk, and timing (X/25) and land a ✅ participate / ⚠️ caution / ❌ skip call. (Template: Step 5.)
6. **Monitor competitor trend adoption** — record which trends rivals adopted, gaps they missed, and what they overused. (Template: Step 6.)
7. **Generate the trend report** — assemble top-3-act-now, watch list, avoid list, timed action items, format and hashtag strategy, and a next-review date. Save to `memory/influencer/trend-spotter/YYYY-MM-DD-<topic>.md` and promote durable facts to `memory/hot-cache.md`. (Template: Step 7.)

## Example

**User**: "What TikTok trends should a fitness brand run right now?"

Output names the top trends to act on now — e.g. "Hot Girl Walk" Evolution (2.3B views, still growing, ⭐⭐⭐⭐⭐ for apparel/supplements via "walk with me" content), "75 Hard" challenge content (⭐⭐⭐⭐, sponsor creators mid-challenge), and GRWM Gym Edition (early-growth, first-mover, ⭐⭐⭐⭐⭐) — with a 15-30s format recommendation (hook in 2s, trending audio, text overlay, quick cuts), hashtags (#FitTok, #GymTok), and a this-week action to brief creators on GRWM Gym Edition. Full version: [references/templates.md](references/templates.md#extended-example--tiktok-fitness-trends).

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in templates for every step, the extended worked example, and execution tips.

- [skill-contract.md](../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../references/state-model.md) — HOT/WARM/COLD memory tiers and save paths.
- [CONNECTORS.md](../../CONNECTORS.md) — free/keyless data recipe per connector category.
- C3 benchmark scoring at [references/c3/scoring-architecture.md](../../references/c3/scoring-architecture.md) — for grading trend-driven creative output downstream.
- Siblings in the Insight phase: [audience-mapper](../audience-mapper/SKILL.md), [audience-mapper](../audience-mapper/SKILL.md).

## Next Best Skill

- **Primary**: [influencer-discovery](../../discover/influencer-discovery/SKILL.md) — turn the chosen trends into a shortlist of creators who can execute them.
- **Alternate**: [audience-mapper](../audience-mapper/SKILL.md) — confirm which trends actually resonate with your audience before committing.
- **Alternate**: [audience-mapper](../audience-mapper/SKILL.md) — dig into niche-specific trend pockets the broad scan missed.

Termination: keep a visited-set of skills invoked this session. If the primary next skill was already run this turn, stop and report the chain complete rather than re-invoking. Max handoff depth is 3; once reached, summarize and return control to the user.
