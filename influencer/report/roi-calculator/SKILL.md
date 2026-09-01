---
name: roi-calculator
slug: aaron-roi-calculator
displayName: "ROI Calculator · ROI 计算"
summary: "活动投入产出核算:成本归集、收益口径与 ROI 及 STAR 回报(R)证据汇总"
description: 'Use when the user asks to "calculate influencer ROI", "prove campaign value", or "what was our ROAS"; produces direct ROI/ROAS, earned media value, attribution-modeled revenue, LTV-based ROI, and a stakeholder-ready summary. Not for building the full slide/written report — use report-generator. 达人营销ROI计算/投资回报测算'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when measuring or projecting influencer campaign ROI, justifying or defending budgets, comparing ROI across campaigns or channels, evaluating individual influencer or tier value, or preparing executive-level ROI numbers. Activate when the user supplies spend and results data and wants ROI, ROAS, EMV, CPA/CAC, attribution, or LTV impact computed."
argument-hint: "<campaign name or spend> [revenue] [results data]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# ROI Calculator

This skill helps you calculate and communicate the return on investment for influencer marketing campaigns using various methodologies appropriate for your goals and available data.

> **Cross-discipline (paid ads):** this is the shared **return-math engine** for paid ads — [paid-measurement-loop](../../../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../../../ad/scale/attribution-reconciler/SKILL.md), and budget-optimizer delegate ROAS/CPA/payback ratios here rather than recomputing them. Save paid runs under `memory/ad/roi-calculator/`.

## Quick Start

Shortest invocation:

```
Calculate ROI for our influencer campaign: $25K spend, $72K revenue, 2.1M reach
```

Common scenario — compare methods before reporting:

```
What's the ROI of our campaign using direct revenue, EMV, and LTV-based methods?
```

## Skill Contract

- **Reads**: campaign ID, complete opaque creator scope when creator-level math is requested, spend/cost-basis breakdown, deduplicated results data (reach, impressions, engagements, clicks, conversions, attributed revenue, new customers), the predeclared attribution model/window/decision rule, AOV and economic LTV inputs if LTV is in scope, and prior performance output from `performance-analyzer`. Reuse authorized opaque `creator_ref` values; raw handles/names/URLs/provider IDs stay transient and never identify a saved row.
- **Writes**: return the ROI calculation and summary inline by default; save them to `memory/influencer/roi-calculator/YYYY-MM-DD-<topic>.md` (or the declared paid path) only with exact WARM-save authorization. Saved output uses `campaign_id`, complete opaque `creator_ref` scope, and opaque evidence/artifact refs—never raw identity locators.
- **Promotes**: only with separate exact authorization, promote durable headline numbers with their attribution window, source, and uncertainty to `memory/hot-cache.md`; a calculation or WARM-save request does not authorize this operation.
- **Done when**:
  1. At least one ROI methodology is computed with the inputs and formula shown.
  2. Each headline metric is stated against a declared, source-dated comparison target; no universal benchmark is invented.
  3. A bottom-line arithmetic assessment and 1-3 recommendations are written. Call the campaign profitable only when attributed revenue and a complete campaign cost basis are verified; otherwise state that profitability is unverified.
  4. Every denominator is verified numeric and `> 0`; zero, negative, missing, or incompatible denominators yield `undefined`/`NEEDS_INPUT`, never a ratio.
- **Primary next skill**: [report-generator](../report-generator/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family is Tier 1 — it works with no live integrations. Ask the user for spend and results data and compute everything from those inputs. Connectors below can pull the numbers automatically when available:

- `~~social platform analytics` — reach, impressions, engagements, video views per platform for EMV and cost-per-metric math.
- `~~ecommerce / analytics` — revenue, conversions, link clicks, and AOV for direct ROI and attribution.
- `~~CRM` — new-customer counts, repeat-purchase rate, and lifetime value for LTV-based ROI.
- `~~influencer database` — per-influencer fees and tier data for by-influencer ROI.

With zero integrations, supply the investment and results tables by hand and the skill still produces every calculation. See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category.

## Instructions

When a user requests ROI calculation, work the steps below. Each step has a fill-in template in [references/roi-templates.md](references/roi-templates.md) — link the step number to its block there.

1. **Gather ROI inputs** — campaign details, the investment (total spend) table, and the results-data table. ([template](references/roi-templates.md#step-1--roi-calculation-inputs))

2. **Calculate direct ROI** — Simple ROI = (Revenue − Investment) / Investment × 100; ROAS = Revenue / Investment. Call the difference **net return under the declared formula**, not profit, unless the revenue attribution and complete cost basis are verified. State positive/zero/negative arithmetic return and a separate profitability-verification status. ([template](references/roi-templates.md#step-2--direct-roi-calculation))

3. **Calculate Earned Media Value (EMV)** — impression-based (Impressions × comparable CPM / 1000) or engagement-based (Engagements × comparable CPE) only from supplied or cited, source-dated comparators. Report applicable methods separately and use a predeclared selection/weighting rule; never average or add overlapping methods by default. If no valid comparator exists, return `NEEDS_INPUT` for EMV. ([template](references/roi-templates.md#step-3--earned-media-value-emv))

4. **Calculate cost-efficiency metrics** — CPM, CPR, CPE, CPV, CPC, CPA, and CAC. Compare only against a declared, source-dated target with a compatible market, window, and attribution basis; otherwise report the metric descriptively and mark the comparison pending. ([template](references/roi-templates.md#step-4--cost-efficiency-analysis))

5. **Apply attribution modeling** — use one predeclared model only after the complete conversion universe, order/event dedupe key, journey touchpoints, eligible channels, and allocation rule are supplied. Optional alternative models are visibly non-additive sensitivity scenarios over the same deduplicated conversion set; never select the most favorable model after seeing results. Missing inputs or model-selection authority returns `NEEDS_INPUT`, not attributed revenue. ([template](references/roi-templates.md#step-5--attribution-analysis))

6. **Calculate customer lifetime value impact** — label the result **LTV-Based ROI** only when `New Customers` is deduplicated against the controlling attribution universe and the supplied LTV is a complete contribution-margin basis with cohort, horizon, retention/churn, refunds, margin, discount/timing, first-order inclusion, source/date, and a positive compatible investment denominator. Then use `((New Customers × contribution-margin LTV) − Investment) / Investment × 100`. A revenue-LTV input produces only an **Estimated revenue-basis scenario** with its basis/horizon/status; it is not economic ROI or profit and is never added to direct attributed revenue or another LTV horizon. Missing fields return `NEEDS_INPUT`. ([template](references/roi-templates.md#step-6--lifetime-value-analysis))

7. **Calculate by-creator ROI** — only for a complete locked creator scope with resolved opaque refs, compatible windows/cost bases, and deduplicated attributed revenue. Per-creator and tier aggregate ROAS is `sum(attributed revenue) / sum(spend)`, never a simple mean; rank only under a predeclared rule. ([template](references/roi-templates.md#step-7--influencer-level-roi))

8. **Generate the ROI report summary** — investment, returns, ROI by methodology, key metrics vs. benchmark, bottom line, and 1-3 recommendations. ([template](references/roi-templates.md#step-8--roi-summary-report))

9. **Qualify candidate Return (R) evidence for the gate**

   The financial outputs from steps 1–8 are **candidate Return (R) evidence** for STAR: ROI/ROAS read against the declared target (`R1`) and the alternative-channel baseline (`R3`), CPE/CPM/CPA benchmarked on a normalized window (`R2`), KPI attainment versus the pre-registered target (`R4`), conversions attributed with a stated method and rigor (`R5`), and incremental impact separated from baseline where measurable (`R6`). A field is Measured only when its exact source, entity, observation window, and attribution basis are verified; arithmetic on User-provided or Estimated inputs is Calculated, not Measured. Return evidence applies only at `assessment_time: actual`; a forecast read has no `R1`–`R6`.

   Hand this Return evidence to the [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) gate — it folds R into the full actual STAR run and computes the profile-weighted **SQS**. This skill does not run the scorer or emit the composite. Unverified conversions emit `results-unverified`: report `R1`/`R2`/`R5` as low-confidence and make no attributable-return claims. These financial numbers are consumed as R evidence; they are not themselves an SQS.

   For a multi-creator campaign, the gate scores each creator partnership separately; a budget-weighted mean of the per-partnership SQS values may summarize the campaign but never replaces the per-partnership diagnosis. This skill supplies the per-partnership Return evidence; it does not aggregate or roll up a composite.

10. **Persist only with permission** — save under `memory/influencer/roi-calculator/` (or the paid path) only after authorization; request separate authorization for hot-cache promotion.

For every formula in this skill, verify the denominator is numeric and strictly greater than zero. If investment, impressions, reach, engagements, views, clicks, acquisitions, customers, or another required denominator is zero, negative, missing, or incompatible with the numerator window, report the ratio as `undefined` and return `NEEDS_INPUT` for that metric. Never silently divide by zero, coerce it, or substitute a nominal value.

## Example

**User**: "Calculate ROI for our influencer campaign: $25K spend, $72K revenue, 2.1M reach"

**Output**:

```markdown
# ROI Calculation Summary

## Investment & Returns

| Item | Value |
|------|-------|
| Total Investment | $25,000 |
| Revenue used in calculation | $72,000 (User-provided; source/window unverified) |
| Total Reach | 2,100,000 |

## ROI Results

### Direct ROI — calculated on User-provided revenue basis
- **Net return under the declared formula**: $47,000
- **ROI**: 188%
- **ROAS**: 2.88:1

The supplied revenue implies $2.88 per $1 spent. `results-unverified`: no attribution source, method, or window was supplied, so this is not an attributable, causal, or incremental-return claim.

### Earned Media Value
- **EMV**: `NEEDS_INPUT` — no source-dated comparable CPM/CPE or declared valuation rule was supplied
- **EMV Multiple**: `NEEDS_INPUT`

### Cost Efficiency
- **CPM**: $11.90
- **CPA**: Unknown (conversion count was not supplied)

## Assessment: Positive arithmetic return on the supplied basis; profitability and causality unverified

Supplied revenue exceeds supplied investment under the declared formula, but no complete cost basis, attribution source/window, source-dated peer target, or incrementality evidence was provided. Do not infer profit, benchmark outperformance, or causal lift, and do not authorize a scale decision from this read alone; obtain verified conversions, attribution evidence, complete costs, and the campaign owner's precommitted decision rule first.
```

The source-dated benchmark evidence template lives in [references/roi-templates.md#benchmark-evidence-template](references/roi-templates.md#benchmark-evidence-template).

## Reference Materials

- [references/roi-templates.md](references/roi-templates.md) — fill-in templates for every Instructions step, the worked example, and benchmark evidence inputs.
- [measurement-protocol.md](../../../references/measurement-protocol.md) — read ROI and Return (R) deltas against a control over the readback window; do not over-claim attribution.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipe per connector category.
- STAR scoring: [star-benchmark.md](../../../references/star-benchmark.md) — the Return (R) dimension this skill's evidence feeds and the profile-weighted SQS the gate computes.
- [performance-analyzer](../performance-analyzer/SKILL.md) — supplies the results data this skill consumes.
- [report-generator](../report-generator/SKILL.md) — wraps these numbers into a full report.
- [budget-optimizer](../../target/budget-optimizer/SKILL.md) — uses ROI output to reallocate spend.
- [campaign-planner](../../target/campaign-planner/SKILL.md) — sets the ROI targets these results are checked against.

## Next Best Skill

**Primary**: [report-generator](../report-generator/SKILL.md) — turn the ROI numbers into a stakeholder-ready report.

**Alternates** (same Report family):

- [performance-analyzer](../performance-analyzer/SKILL.md) — go back for deeper performance breakdowns if the ROI math exposed gaps.
- [budget-optimizer](../../target/budget-optimizer/SKILL.md) — feed by-influencer and by-tier ROI into the next budget allocation.

Termination note: keep a visited-set of skills invoked this session. If the primary next skill was already run, stop and report the chain complete rather than re-invoking it. Stop after at most 3 hops in a single chain.
