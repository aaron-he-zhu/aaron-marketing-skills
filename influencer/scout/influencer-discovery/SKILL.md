---
name: influencer-discovery
slug: influencer-discovery
displayName: "Influencer Discovery · 红人发现"
summary: "多平台红人挖掘:候选池、画像与互动指标、真实性红旗筛查、分层短名单"
description: 'Use when the user asks to "find influencers", "build an influencer list", or "discover creators in [niche]"; produces a multi-platform candidate pool, per-influencer profiles with audience and engagement metrics, authenticity red-flag screening, and a tiered shortlist with fit scores. Not for scoring or ranking a known shortlist — use fit-scorer. 达人挖掘/找达人/创作者名单'
version: "18.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when building an influencer roster from scratch, expanding into a new platform or niche, replacing churned partners, finding micro and nano creators at scale, identifying which influencers a competitor partners with, or standing up an always-on discovery pipeline. The user names a niche, platform, follower band, or brand and wants a list of candidate creators to evaluate."
argument-hint: "<brand or niche> [platform] [follower-range]"
metadata: {"author": "aaron-he-zhu", "version": "18.0.0", "discipline": "influencer", "phase": "scout", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "scout"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Influencer Discovery

Find the right influencers for your brand by searching across platforms, screening for audience fit and authenticity, and building a tiered candidate list ready for scoring.

## Quick Start

```
Find 20 influencers in [niche] for [brand/product]
```

```
Find influencers in [niche] with 50K-200K followers on TikTok and Instagram,
based in [location], engagement above 4%, who have worked with brands like [brand]
```

## Skill Contract

- **Reads**: brand/product, niche or category, target platforms, follower range, engagement floor, location/language, audience demographics, exclusions; prior `entity-registry` brand profile and any `audience-mapper` output if present in memory; existing roster records under `memory/creators/` (dedupe the candidate pool against creators already rostered by [creator-registry](../../../protocol/creator-registry/SKILL.md)).
- **Writes**: discovery results to `memory/influencer/influencer-discovery/YYYY-MM-DD-<topic>.md` — search criteria, candidate pool stats, per-influencer profiles, tiered shortlist with fit scores. Roster-worthy shortlisted creators (verified handles, contact path, audience stats) go as one-line updates to `memory/events/creators.ndjson` via an authorized `operation: propose` request to `registry-events.py` — only `creator-registry` writes canonical records under `memory/creators/`.
- **Promotes**: durable facts (top-tier handles, confirmed niche/platform mix, competitor-saturated creators) to `memory/hot-cache.md`.
- **Done when**:
  - A candidate pool exists with at least the requested count screened past follower, engagement, and brand-safety filters.
  - Each shortlisted influencer has a profile with metrics, audience read, and a preliminary fit score.
  - A tiered shortlist (must-reach / strong / consider) is compiled with next-step pointers.
- **Primary next skill**: [fit-scorer](../fit-scorer/SKILL.md) — score and rank the discovered candidates with weighted criteria.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family has no live integrations required (Tier 1): the skill works with only the inputs the user provides. Ask the user for niche, platforms, follower band, engagement floor, location, and exclusions, then reason over what they supply plus any public handles they share.

Where a tool *could* sharpen results, use `~~` connector placeholders:

- `~~influencer database` — bulk discovery, follower/engagement metrics, audience demographics.
- `~~social platform analytics` — native creator-marketplace data, trending sounds, related accounts.
- `~~CRM` — import the shortlist and dedupe against existing partners.
- `~~audience overlap` — estimate creator-audience vs. brand-audience match.

**Keyless candidate-card metadata (oEmbed)**: YouTube (`https://www.youtube.com/oembed?url=<video-url>&format=json`), TikTok (`https://www.tiktok.com/oembed?url=<post-url>`), and X (`https://publish.twitter.com/oembed?url=<post-url>`) return a post's title, author name/handle, and thumbnail with **no key** — enough to auto-fill a candidate's profile row from pasted links instead of hand-copying. Metadata only: no follower or engagement metrics, so those stay `~~influencer database` or manual export — **except YouTube**, below.

**Measured YouTube metrics (free key)**: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" channel @handle` returns the real displayed subscriber count, total views, and video count, and `youtube.py videos @handle --limit 10` adds per-video views/likes/comments — upgrading a YouTube candidate's profile row from Estimated to **Measured**. Free `YOUTUBE_API_KEY` (10,000 units/day; one channel check ≈ 1–3 units). ToS boundary: vet a **named shortlist**, don't build a bulk creator database — quota extensions are refused for competitive harvesting. See [scripts/connectors/README.md](../../../scripts/connectors/README.md).

See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category and the opt-in MCP layer. None are required — every step degrades to user-supplied inputs.

## Instructions

Each step has a fill-in block in [references/templates.md](references/templates.md) — copy the matching block. This skill does *not* compute final fit scores; the per-influencer score in step 4 is a triage signal that [fit-scorer](../fit-scorer/SKILL.md) refines downstream.

1. **Define search criteria.** Capture brand, goal, budget tier, and the required/preferred parameter table plus nice-to-haves and exclusions. Step 1 template.
2. **Conduct the search.** Work hashtags, similar-accounts, competitor mentions, and platform-native discovery; log any tool queries used. Step 2 template.
3. **Initial screening.** Filter the pool on follower range, engagement, recency, relevance, and brand safety; tally red flags (fake followers, controversy, competitor exclusivity, inactivity). Per-platform reading cues: [references/platform-vetting.md](references/platform-vetting.md). Step 3 template.
4. **Build influencer profiles.** For each qualified creator, fill the profile (basics, metrics, audience, content, partnership history, contact, preliminary fit score). For a deep single-creator read with a contact waterfall, use [references/creator-dossier.md](references/creator-dossier.md). Step 4 template.
5. **Compile the discovery report.** Roll profiles into summary stats, by-platform and by-tier breakdowns, the three-tier shortlist, mix recommendation, and next steps. Step 5 template.
6. **Add insights.** Note niche content trends, the competitive picture, and recommendations for future searches. Step 6 template.

Save the report to `memory/influencer/influencer-discovery/YYYY-MM-DD-<topic>.md` and, with permission, cache the active shortlist in working memory. Submit each roster-worthy creator as an authorized `operation: propose` request through `registry-events.py` to `memory/events/creators.ndjson`, then recommend [creator-registry](../../../protocol/creator-registry/SKILL.md) for resolution; proposal count never changes authority.

## Compact Example

**User**: "Find 15 micro-influencers (10K-100K followers) in sustainable fashion for a new eco clothing brand."

**Output**: 43 candidates surfaced, 15 pass all filters with fit scores above 18/25. Top pick @sustainablestyle_sarah (47K IG + 23K TikTok, 5.2% ER, prior eco-brand partners) scores 24/25; shortlist tiered into 5 high-engagement leads, 7 mid-tier, 3 rising stars; report saved and top handles promoted. Full walkthrough in [references/templates.md](references/templates.md#worked-example--sustainable-fashion-micro-influencers).

## Reference Materials

- [references/templates.md](references/templates.md) — all step fill-in blocks (criteria, search, screening, profile, report, insights), the worked example, tips, and the "what/when" overview.
- [references/platform-vetting.md](references/platform-vetting.md) — per-platform creator playbooks (X/LinkedIn/TikTok/YouTube/Reddit) feeding screening and profiling in steps 3-4.
- [references/creator-dossier.md](references/creator-dossier.md) — structured per-creator dossier from public data, with a contact-discovery waterfall.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipes and opt-in MCP layer.
- STAR benchmark at [references/star-benchmark.md](../../../references/star-benchmark.md) — scoring framework that fit-scorer applies downstream.
- Siblings in the scout phase: [fit-scorer](../fit-scorer/SKILL.md), [audience-mapper](../audience-mapper/SKILL.md), [trend-spotter](../trend-spotter/SKILL.md).

## Next Best Skill

**Primary**: [fit-scorer](../fit-scorer/SKILL.md) — score and rank the discovered candidates with weighted criteria before outreach.

**Alternates (same influencer family)**:
- [competitor-tracker](../../target/competitor-tracker/SKILL.md) — when discovery surfaced competitor-saturated creators and you want to map the competitive field first.
- [audience-mapper](../audience-mapper/SKILL.md) — when the target audience is still fuzzy and criteria need sharpening before a re-search.

**Termination**: Maintain a visited-set. If a skill has already been invoked this session, stop and report chain-complete rather than re-invoking it. Max chain depth is 3 hops from the originating request; stop and summarize when reached.

## Related Skills

- [audience-mapper](../audience-mapper/SKILL.md) - Define who to reach
- [fit-scorer](../fit-scorer/SKILL.md) - Score and rank discovered influencers
- [competitor-tracker](../../target/competitor-tracker/SKILL.md) - Find competitor influencers
- [outreach-manager](../../activate/outreach-manager/SKILL.md) - Contact discovered influencers
