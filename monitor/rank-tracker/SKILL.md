---
name: rank-tracker
description: 'Use when the user asks to "track rankings" or "查排名"; measures keyword and SERP-position deltas over time from provided exports or connected tools, including AI-response checks. Not for multi-metric stakeholder reports or setting alerts — use performance-monitor (report or alert mode). 排名追踪/SERP监控'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when tracking keyword rankings, monitoring position changes, comparing ranking snapshots, or detecting ranking drops."
argument-hint: "<domain> [keyword list]"
allowed-tools: WebFetch
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: seo-geo
  phase: monitor
  geo-relevance: "medium"
---

# Rank Tracker

Tracks keyword positions, SERP feature ownership, and AI visibility over time.

## Quick Start

```
Set up rank tracking for [domain] targeting these keywords: [keyword list]
```

```
Analyze ranking changes for [domain] over the past [time period]
```

## Skill Contract

**Expected output**: a ranking report or delta summary plus the standard handoff summary for `memory/monitoring/`.

- **Reads**: current rankings, prior baselines, target keyword list, market/device, and any user-provided or tool metrics.
- **Writes**: a user-facing monitoring deliverable and reusable summary.
- **Promotes**: significant changes, confirmed anomalies, follow-up actions, and pending decisions to `memory/open-loops.md`.
- **Done when**: every tracked keyword shows current position vs baseline with a labeled delta (or N/A); each position cites its source (tool export / user-provided / estimated); and biggest movers and likely causes are named.
- **Primary next skill**: [performance-monitor](../performance-monitor/SKILL.md) when recurring monitoring should become automated.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

All integrations optional (see [CONNECTORS.md](../../CONNECTORS.md)). With tools, pull rankings from ~~SEO tool, impressions from ~~search console, traffic from ~~analytics, and AI citations from ~~AI monitor. Without tools, ask for positions, volumes, competitor data, and SERP feature status.

**Zero-dependency measurement loop** (no paid tool needed): never narrate a ranking movement you did not measure — record each check as a snapshot and let the ledger compute the delta. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/ledger.py" record <domain> --source rank --data '{"<keyword>": <position>, ...}'`, then `ledger.py diff <domain> --source rank` for the change since the last check and `ledger.py trend <domain> --source rank --field "<keyword>"` for the series. Record real Search Console positions when connected, or the positions the user provides at Tier 1. A ranking delta is a **week-scale, confounded outcome** — attribute it against a control (a holdout keyword/competitor), not against zero; see [references/measurement-protocol.md](../../references/measurement-protocol.md). See [scripts/connectors/README.md](../../scripts/connectors/README.md).

## Decision Gates

**Stop and ask the user when:**
- No target keywords are provided and none can be inferred from `CLAUDE.md` or prior monitoring records — offer: (1) supply a keyword list, (2) track the domain's top known terms, (3) cancel.

**Continue silently (never stop for):**
- No prior baseline exists — record the current run as the baseline, label all positions as the first snapshot, and proceed (do not invent a "previous" position).
- Missing optional tool data (SERP features, AI citations) — mark N/A and proceed.

## Instructions

When a user requests rank tracking or analysis:

1. **Set Up Keyword Tracking** — configure domain, market, device, language, update frequency, priorities, and competitor watchlist.
2. **Record Current Rankings** — output a position table where every row cites its source (tool export / user-provided / estimated), with position ranges, ranking URLs, feature ownership, and movement vs baseline.
3. **Analyze Ranking Changes** — highlight biggest wins, declines, stable terms, new rankings, lost rankings, likely causes, and recovery ideas; each delta labeled against its baseline.
4. **Track SERP Features** — compare ownership of snippets, PAA, image/video packs, local packs, and related feature shifts.
5. **Track GEO / AI Visibility** — monitor AI Overview presence, citation rate, citation position, and trend; mark each value Measured (from an ~~AI monitor) or N/A if unobserved.
6. **Compare Against Competitors** — report share of voice, head-to-head comparisons, and threat levels.
7. **Generate Ranking Report** — output overall trend, key wins, concerns, opportunities, SERP feature changes, GEO visibility, and recommendations, with each metric carrying its source tag.

Label every metric **Measured** (tool/export), **User-provided**, or **Estimated** (model inference); never present an estimate as measured; if a required metric is unavailable, mark it N/A — do not invent it.

> **Reference**: See [Ranking Analysis Templates](references/ranking-analysis-templates.md) for the complete output templates for all seven steps.

## Example

A ranking report names the biggest winners, biggest drops, and next actions, with each position carrying its source tag and labeled delta against baseline.

## Rank Change Quick Reference

### Response Protocol

| Change | Timeframe | Action |
|--------|-----------|--------|
| Drop 1-3 positions | Wait 1-2 weeks | Monitor — may be normal fluctuation |
| Drop 3-5 positions | Investigate within 1 week | Check technical issues and competitor changes |
| Drop 5-10 positions | Investigate immediately | Run a full diagnostic: technical, content, links |
| Drop off page 1 | Emergency response | Comprehensive audit + recovery plan |
| Position gained | Document and learn | Identify what worked and replicate |

> **Reference**: See [Tracking Setup Guide](references/tracking-setup-guide.md) for tracking setup, root-cause taxonomy, CTR benchmarks, SERP feature impact, and algorithm-update assessment.

### Save Results

Ask "Save these results?" If yes, write to `memory/monitoring/` — see [Skill Contract](../../references/skill-contract.md) §Save Results Template.

## Reference Materials

- [Tracking Setup Guide](references/tracking-setup-guide.md) — Setup rules, feature tracking, and interpretation guidance

## Next Best Skill

Initial setup (no baseline) → [performance-monitor](../performance-monitor/SKILL.md). Subsequent runs (baseline exists) → Terminal. Visited-set rule applies per [skill-contract.md](../../references/skill-contract.md).
