---
name: performance-analyzer
slug: performance-analyzer
displayName: "Performance Analyzer · 效果分析"
summary: "活动效果分析:达成 vs 目标、平台与创作者维度拆解、优化建议"
description: 'Use when the user asks to "analyze influencer campaign performance", "compare influencers", or "find what content worked"; produces metric scorecards vs target and benchmark, platform/influencer/content rankings, engagement-quality and sentiment reads, conversion-attribution breakdowns, and ranked learnings. Not for dollar-level return math — use roi-calculator. 达人营销效果分析/投放复盘'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use mid-flight or post-campaign when a user wants to evaluate influencer results, compare creators against each other, find top-performing content or formats, judge engagement quality and comment sentiment, connect influencer activity to conversions, or build performance benchmarks for future planning."
argument-hint: "<campaign name> [platform or influencer handles]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
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

- **Reads**: campaign name and date range; native platform analytics (reach, views, engagement); influencer-supplied reports or screenshots; website/GA traffic and conversion data; sales and promo-code redemption data; targets, benchmarks, and the preregistered decision rule/readback window if supplied; the optional lightweight campaign tracker and its `evidence_refs`; and any ROI/ROAS artifact already computed by [roi-calculator](../roi-calculator/SKILL.md). Reuse each explicit upstream opaque `creator_ref` or a verified creator-registry aggregate ID; a raw handle/name/URL/provider ID is transient lookup input only and never becomes a saved identity. Per-creator baselines come from `memory/creators/<aggregate-id>.md` only when an authorized artifact or verified registry link resolves that ref. Never derive the path from a raw locator.
- **Writes**: return the performance analysis inline by default. When a current non-forked tracker-state artifact proves `measured` or `closed`, include the compact Campaign Retro Card from step 8 bound to that campaign, creator, measurement contract, and decision rule. Save the analysis and card together to `memory/influencer/performance-analyzer/YYYY-MM-DD-<campaign>.md` only with exact WARM-save authorization; saved tables, headings, evidence, and handoffs use `creator_ref` plus opaque source refs, never raw handles, names, profile URLs, email addresses, or provider IDs.
- **Promotes**: only with separate exact authorization, promote durable evidence-backed campaign facts (verified metric results and descriptive format/platform associations) to `memory/hot-cache.md`; any ROI/ROAS value remains tied to its exact roi-calculator artifact. The Retro Card's qualitative `renew | retest | retire | unknown` decision, rationale, next hypothesis, and limitations remain WARM and are never promoted as registry truth. This skill makes no creator-registry proposal: after a creator row is closed, the existing boundary still permits only a separately authorized, evidence-backed **actual rate**, **signed rights window/expiry**, or **measured performance baseline** to be proposed by the owning workflow; [creator-registry](../../../protocol/creator-registry/SKILL.md) alone decides whether it becomes canonical.
- **Done when**:
  - Core metrics are compared against compatible source-dated targets/benchmarks. Missing or incompatible context is `Unknown`/`NOT_SCORED`, never an invented `/10` score or adjective verdict.
  - Creators/platforms/content are ranked only under a declared metric, compatible window/basis, complete candidate set, and preregistered decision rule; descriptive associations and causal hypotheses stay visibly separate.
  - Conversions use one declared attribution model with deduplicated, mutually exclusive counted buckets; overlapping promo/UTM/direct observations remain reconciliation evidence, and modeled influence stays Estimated outside the counted total.
  - With verified current `measured` or `closed` state, each requested next-cycle decision has a scope-bound Campaign Retro Card with campaign/creator/state/measurement/decision-rule refs, evidence-backed rationale, `evidence_refs`, next-campaign hypothesis, and unresolved limitations; insufficient decision evidence resolves to `unknown`, while missing/forked state blocks the card.
- **Primary next skill**: [roi-calculator](../roi-calculator/SKILL.md) — turn measured performance into dollar-level return.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). The skill runs entirely on inputs you provide — paste platform exports, influencer report screenshots, GA numbers, and promo-code redemption counts, and it analyzes the supported fields. Missing inputs do not block a partial descriptive read, but any dependent score, verdict, rank, causal explanation, attribution total, or decision becomes `Unknown`/`NOT_SCORED`/`NEEDS_INPUT` rather than being filled in.

Where a connector could speed the work, the skill marks it with a `~~` placeholder:

- `~~social platform analytics` — native reach/engagement/video metrics per post.
- `~~web analytics` — site traffic, click-through, and on-site conversion data.

**Measured YouTube post-performance (free key)**: when campaign content lives on YouTube, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" videos @creator --limit 20` pulls the actual per-video views/likes/comments for the campaign window — **Measured** platform metrics without waiting for the creator's screenshot export. Keep both labels honest: API numbers are Measured, creator-supplied numbers are User-provided, and the two can legitimately disagree (display rounding, timing). Free `YOUTUBE_API_KEY`. See [scripts/connectors/README.md](../../../scripts/connectors/README.md).
- `~~ecommerce / sales platform` — revenue, orders, AOV, promo-code redemptions.
- `~~influencer database` — historical creator benchmarks for comparison.

No placeholder is required to run. See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless data recipe per category.

## Instructions

Work the steps below as one dependency-aware pass. Each fill-in template lives in [references/analysis-templates.md](references/analysis-templates.md). Build the Step 2 shell after intake, but run Step 7 before populating or publishing Step 2 `Conversions`, `Revenue`, or any rate/cost that depends on them; those fields must cite Step 7's reconciled counted total or remain `Unknown/NEEDS_INPUT`.

1. **Gather performance data** — log campaign/period/influencers/platforms and the available sources (native analytics, influencer reports, web analytics, sales, promo codes). Template: step 1.
2. **Analyze core metrics** — compare reach, impressions, engagements, ER, video views, clicks, promo uses, conversions, and revenue against compatible source-dated targets/benchmarks. Emit field-level comparison states; do not invent an aggregate score or adjective verdict. Template: step 2.
3. **Analyze by platform** — compare platforms on compatible reach/ER/click/conversion/CPA windows and state observed differences. Put any explanation in a separately labeled hypothesis unless a designed comparison supports it. Template: step 3.
4. **Analyze by creator** — use opaque `creator_ref`; rank only comparable rows under the declared rule. Consume ROI/ROAS only from a cited roi-calculator artifact, do not compute it here, and separate observed content anatomy from causal hypotheses. A renew/retest/retire call comes only from the Retro decision gate. Template: step 4.
5. **Content performance analysis** — compare formats/themes under compatible exposure and attribution bases. Name observed higher/lower associations; describe a hook/message/visual as causal or "winning" only when the supplied design clears the measurement protocol. Template: step 5.
6. **Engagement quality analysis** — break engagement by type/intent, run evidenced comment sentiment, and surface purchase-intent signals. Use typed observations or `Unknown`; emit no `/10` quality score without a supplied rubric, inputs, and calculation. Template: step 6.
7. **Conversion & attribution analysis** — draw the observed funnel and use one declared attribution model. Deduplicate events into mutually exclusive counted buckets; preserve promo/UTM/direct overlap as reconciliation evidence, and report Estimated influence outside the counted total. Template: step 7.
8. **Generate insights & recommendations** — write 3–5 evidence-backed observations, separately labeled hypotheses, and bounded next tests. Add one compact Campaign Retro Card per creator decision requested only when a verified current, non-forked tracker-state artifact proves that exact campaign/creator is `measured` or `closed` and the matching measurement-contract and decision-rule refs are supplied; a bare stage string never qualifies. Use only `renew | retest | retire | unknown`. Template: step 8.

Before naming any creator/format/platform a real winner, clear the comparability, complete-scope, preregistered-rule, and significance bars in [measurement-protocol.md](../../../references/measurement-protocol.md) — otherwise mark it `Keep-testing` or `NOT_RANKED`. When a structured score is needed, apply per-dimension STAR analysis (Suitability/Trust/Appeal/Return dimension reads) from [star-benchmark.md](../../../references/star-benchmark.md), and hand financial inputs to [roi-calculator](../roi-calculator/SKILL.md) for Return (R) math — this skill contributes inputs but does not compute ROI/ROAS or SQS (the creator-content-auditor gate computes SQS).

For the Retro Card, use `renew` only when comparable measured evidence clears the preregistered decision rule without a material unresolved limitation; use `retest` for a plausible but inconclusive or correctable test; use `retire` only when measured evidence or a documented hard constraint clears the declared stop rule; otherwise use `unknown`. This operating decision is not a STAR dimension, SQS, or creator-content-auditor verdict—do not simulate or carry forward one.

After an authorized WARM save, offer a handoff to [campaign-planner](../../target/campaign-planner/SKILL.md) to append the saved analysis/card reference to the relevant tracker row's `evidence_refs`; the tracker edit needs its own exact authorization, and neither the card nor this skill advances `stage`. Also offer [fit-scorer](../../scout/fit-scorer/SKILL.md) as an explicit next-cycle handoff with the card's evidence references and hypothesis. Do not invoke it automatically, and do not translate the Retro decision into a STAR/SQS verdict.

## Example

**User**: "Analyze this dated summer-skincare export for 10 creators. It contains opaque creator refs, the metric/target table below, per-creator and per-platform results, one deduplicated attribution model, and a completed significance read. ROI comes from roi-calculator artifact `roi-ref-01`."

**Output** (abridged — full version in [references/analysis-templates.md](references/analysis-templates.md)):

```markdown
# Summer Skincare Campaign Performance Analysis — illustrative export-backed read

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Total Reach | 2.4M | 2M | ✅ +20% |
| Engagement Rate | 4.2% | 3.5% | ✅ +20% |
| Conversions | 1,847 | 2,000 | ⚠️ -8% |
| Revenue | $142,500 | $150,000 | ⚠️ -5% |
| ROAS (from `roi-ref-01`) | 2.8:1 | 3:1 | ⚠️ -7% |

**Top 3**: the three `creator_ref` rows that clear the declared ranking and significance rule, using only comparable metrics in the export.
**Key learning**: report the export-backed TikTok/Instagram delta only if the comparison windows and attribution bases match; otherwise mark it Keep-testing.
**Recommendation**: renew/drop and reallocation calls remain conditional on the predeclared decision rule rather than invented from the campaign count alone.
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
