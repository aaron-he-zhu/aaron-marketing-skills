---
name: performance-analyzer
slug: performance-analyzer
displayName: "Performance Analyzer · 效果分析"
summary: "活动效果分析:达成 vs 目标、平台与创作者维度拆解、优化建议"
description: 'Use when the user asks to "analyze influencer campaign performance", "compare influencers", or "find what content worked"; produces metric scorecards vs target and benchmark, platform/influencer/content rankings, engagement-quality and sentiment reads, conversion-attribution breakdowns, and ranked learnings. Not for dollar-level return math — use roi-calculator. 达人营销效果分析/投放复盘'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use mid-flight or post-campaign when a user wants to evaluate influencer results, compare creators against each other, find top-performing content or formats, judge engagement quality and comment sentiment, connect influencer activity to conversions, or build performance benchmarks for future planning."
argument-hint: "<campaign name> [platform or influencer handles]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Performance Analyzer

Analyze influencer campaign performance past surface metrics — score results vs target/benchmark, rank platforms/creators/content, read engagement quality and sentiment, attribute conversions, and write ranked learnings.

> **Cross-discipline (paid ads):** this is also the cross-channel **paid-ads** scorecard/anomaly lens — account-wide metric rollups vs target/benchmark that feed [ad-test-designer](../../../ad/orchestrate/ad-test-designer/SKILL.md) (what to test) and [paid-measurement-loop](../../../ad/scale/paid-measurement-loop/SKILL.md) (what to read back). Save paid runs under `memory/ad/performance-analyzer/`.

## Quick Start

```
Analyze performance of [campaign name] influencer campaign
```

Compare creators within one campaign:

```
Compare performance of these influencers from [campaign]: @handle1, @handle2, @handle3
```

## Skill Contract

- **Reads**: campaign name and date range; native platform analytics (reach, views, engagement); influencer-supplied reports or screenshots; website/GA traffic and conversion data; sales and promo-code redemption data; targets and benchmarks if the user has them; per-creator performance baselines from `memory/creators/<handle-slug>.md` ([creator-registry](../../../protocol/creator-registry/SKILL.md) roster records) when present.
- **Writes**: a performance analysis to `memory/influencer/performance-analyzer/YYYY-MM-DD-<campaign>.md` covering core-metric scorecards, platform/influencer/content rankings, engagement-quality and sentiment reads, conversion attribution, and ranked learnings.
- **Promotes**: durable facts (top-performing creators, winning formats, platform ROI splits, roster renew/drop calls) to `memory/hot-cache.md`.
- **Done when**:
  - Core metrics are scored against target and benchmark with a performance verdict.
  - Top and bottom performers are ranked with reasons, and content patterns that worked are named.
  - Conversions are attributed by method (promo code / UTM / direct / estimated) and 3-5 learnings are written.
- **Primary next skill**: [roi-calculator](../roi-calculator/SKILL.md) — turn measured performance into dollar-level return.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). The skill runs entirely on inputs you provide — paste platform exports, influencer report screenshots, GA numbers, and promo-code redemption counts, and it builds the full analysis. Ask the user for whatever is missing rather than blocking.

Where a connector could speed the work, the skill marks it with a `~~` placeholder:

- `~~social platform analytics` — native reach/engagement/video metrics per post.
- `~~web analytics` — site traffic, click-through, and on-site conversion data.

**Measured YouTube post-performance (free key)**: when campaign content lives on YouTube, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" videos @creator --limit 20` pulls the actual per-video views/likes/comments for the campaign window — **Measured** platform metrics without waiting for the creator's screenshot export. Keep both labels honest: API numbers are Measured, creator-supplied numbers are User-provided, and the two can legitimately disagree (display rounding, timing). Free `YOUTUBE_API_KEY`. See [scripts/connectors/README.md](../../../scripts/connectors/README.md).
- `~~ecommerce / sales platform` — revenue, orders, AOV, promo-code redemptions.
- `~~influencer database` — historical creator benchmarks for comparison.

No placeholder is required to run. See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless data recipe per category.

## Instructions

Work the steps in order. Each fill-in template lives in [references/analysis-templates.md](references/analysis-templates.md) — copy the matching block and populate it.

1. **Gather performance data** — log campaign/period/influencers/platforms and the available sources (native analytics, influencer reports, web analytics, sales, promo codes). Template: step 1.
2. **Analyze core metrics** — score reach, impressions, engagements, ER, video views, clicks, promo uses, conversions, and revenue against target and benchmark; assign a performance verdict and call out over/underperformers. Template: step 2.
3. **Analyze by platform** — compare platforms on reach/ER/clicks/conversions/CPA, name the best and worst with reasons, and break out platform-specific formats (IG feed/Reels/Stories, TikTok watch time/completion). Template: step 3.
4. **Analyze by influencer** — rank creators on reach/ER/conversions/ROI, deep-dive top performers (why they won, content anatomy, renew call), and explain underperformers. Template: step 4.
5. **Content performance analysis** — rank top content, compare formats and themes, and name the winning hook/messaging/visual patterns. Template: step 5.
6. **Engagement quality analysis** — break engagement by type and intent, run comment sentiment, surface purchase-intent signals, and score quality /10. Template: step 6.
7. **Conversion & attribution analysis** — draw the funnel, score conversion metrics vs benchmark, attribute by method (promo / UTM / direct / estimated), and table promo-code performance. Template: step 7.
8. **Generate insights & recommendations** — write the top-5 learnings, what worked / what didn't, optimization opportunities, roster renew/drop calls, and future-campaign guidance. Template: step 8.

Before naming any creator/format/platform a real winner, clear the significance bar in [measurement-protocol.md](../../../references/measurement-protocol.md) — otherwise mark it Keep-testing. When a structured score is needed, apply per-dimension STAR analysis (Suitability/Trust/Appeal/Return dimension reads) from [star-benchmark.md](../../../references/star-benchmark.md), and hand the measured inputs to [roi-calculator](../roi-calculator/SKILL.md) for the measured Return (R) evidence — this skill contributes the inputs but does not compute the SQS (the creator-content-auditor gate does).

## Example

**User**: "Analyze performance of our summer skincare campaign with 10 influencers"

**Output** (abridged — full version in [references/analysis-templates.md](references/analysis-templates.md)):

```markdown
# Summer Skincare Campaign Performance Analysis — Above Average (7.5/10)

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Total Reach | 2.4M | 2M | ✅ +20% |
| Engagement Rate | 4.2% | 3.5% | ✅ +20% |
| Conversions | 1,847 | 2,000 | ⚠️ -8% |
| Revenue | $142,500 | $150,000 | ⚠️ -5% |
| ROI | 2.8:1 | 3:1 | ⚠️ -7% |

**Top 3**: @skincaresarah (ROI 4.2:1), @glowwithgrace (ER 6.8%), @beautyreview (reach/$).
**Key learning**: TikTok beat Instagram (3.5:1 vs 2.1:1 ROI) — shift 20% of IG budget to TikTok.
**Recommendation**: Renew top 5; replace bottom 2 with TikTok-native creators.
```

## Reference Materials

- [references/analysis-templates.md](references/analysis-templates.md) — the eight fill-in step templates plus the full worked example.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — verified free/keyless data recipes per connector category.
- [measurement-protocol.md](../../../references/measurement-protocol.md) — preregistered readback windows, outcome unit, alpha, practical-effect boundary, multiplicity/sequential policy, guardrails, and decision owner. Report statistical and practical flags separately; use `experiment.py` for deterministic `Calculated` evidence, and never substitute a universal p-value/lift rule or attribute a business action to the helper.
- The STAR benchmark at [references/star-benchmark.md](../../../references/star-benchmark.md) — scoring architecture when a structured score is needed.
- Sibling skills: [roi-calculator](../roi-calculator/SKILL.md), [report-generator](../report-generator/SKILL.md), [fit-scorer](../../scout/fit-scorer/SKILL.md), [campaign-planner](../../target/campaign-planner/SKILL.md).

## Next Best Skill

**Primary**: [roi-calculator](../roi-calculator/SKILL.md) — convert measured performance into dollar-level ROI, cost-per-result, and payback math.

**Alternates** (same Report family):

- [report-generator](../report-generator/SKILL.md) — package the analysis into a formal stakeholder report.
- [fit-scorer](../../scout/fit-scorer/SKILL.md) — feed proven performers back into creator scoring for the next round.

**Termination note**: Maintain a visited-set. If a skill has already been invoked this session, stop and report chain-complete rather than re-running it. Cap the chain at max-depth 3 hops; if results are inconclusive after that, surface the open loops to the user instead of continuing.
