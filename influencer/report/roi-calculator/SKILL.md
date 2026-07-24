---
name: roi-calculator
slug: aaron-roi-calculator
displayName: "ROI Calculator · ROI 计算"
summary: "活动投入产出核算:成本归集、收益口径与 ROI 及 STAR 回报(R)证据汇总"
description: 'Use when the user asks to "calculate influencer ROI", "prove campaign value", or "what was our ROAS"; produces direct ROI/ROAS, earned media value, attribution-modeled revenue, LTV-based ROI, and a stakeholder-ready summary. Not for building the full slide/written report — use report-generator. 达人营销ROI计算/投资回报测算'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when measuring or projecting influencer campaign ROI, justifying or defending budgets, comparing ROI across campaigns or channels, evaluating individual influencer or tier value, or preparing executive-level ROI numbers. Activate when the user supplies spend and results data and wants ROI, ROAS, EMV, CPA/CAC, attribution, or LTV impact computed."
argument-hint: "<campaign name or spend> [revenue] [results data]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
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

- **Reads**: campaign spend breakdown, results data (reach, impressions, engagements, clicks, conversions, revenue, new customers), AOV and repeat-rate data if LTV is in scope, any prior performance output from `performance-analyzer`.
- **Writes**: ROI calculation file at `memory/influencer/roi-calculator/YYYY-MM-DD-<topic>.md` containing direct ROI/ROAS, EMV, cost-efficiency metrics, attribution-modeled revenue, LTV-based ROI, by-influencer ROI, and a summary report block.
- **Promotes**: only with separate authorization, durable headline numbers with their attribution window, source, and uncertainty; a calculation request alone does not authorize hot-cache writes.
- **Done when**:
  1. At least one ROI methodology is computed with the inputs and formula shown.
  2. Each headline metric is stated against a declared, source-dated comparison target; no universal benchmark is invented.
  3. A bottom-line assessment (profitable / break-even / loss) and 1-3 recommendations are written.
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

2. **Calculate direct ROI** — Simple ROI = (Revenue − Investment) / Investment × 100; ROAS = Revenue / Investment. State profit and a Profitable/Break-even/Loss assessment. ([template](references/roi-templates.md#step-2--direct-roi-calculation))

3. **Calculate Earned Media Value (EMV)** — impression-based (Impressions × CPM / 1000) and engagement-based (Engagements × CPE), then average. Flag EMV as directional, not absolute. ([template](references/roi-templates.md#step-3--earned-media-value-emv))

4. **Calculate cost-efficiency metrics** — CPM, CPR, CPE, CPV, CPC, CPA, and CAC. Compare only against a declared, source-dated target with a compatible market, window, and attribution basis; otherwise report the metric descriptively and mark the comparison pending. ([template](references/roi-templates.md#step-4--cost-efficiency-analysis))

5. **Apply attribution modeling** — run first-touch, last-touch, linear, time-decay, and position-based; recommend the model that fits the customer journey. ([template](references/roi-templates.md#step-5--attribution-analysis))

6. **Calculate customer lifetime value impact** — LTV-Based ROI = (New Customers × Avg LTV − Investment) / Investment; project short- vs. long-term and compare customer quality to organic/paid. ([template](references/roi-templates.md#step-6--lifetime-value-analysis))

7. **Calculate by-influencer ROI** — per-influencer ROI/ROAS rank, investment efficiency, and ROI by tier (macro/micro/nano). ([template](references/roi-templates.md#step-7--influencer-level-roi))

8. **Generate the ROI report summary** — investment, returns, ROI by methodology, key metrics vs. benchmark, bottom line, and 1-3 recommendations. ([template](references/roi-templates.md#step-8--roi-summary-report))

9. **Produce the measured Return (R) evidence for the gate**

   The financial outputs from steps 1–8 are the campaign's **measured Return (R) evidence** for STAR: ROI/ROAS read against the declared target (`R1`) and the alternative-channel baseline (`R3`), CPE/CPM/CPA benchmarked on a normalized window (`R2`), KPI attainment versus the pre-registered target (`R4`), conversions attributed with a stated method and rigor (`R5`), and incremental impact separated from baseline where measurable (`R6`). Measured Return exists only at `assessment_time: actual`; a forecast read has no `R1`–`R6`. Label each figure Measured / User-provided / Calculated / Estimated.

   Hand this Return evidence to the [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) gate — it folds R into the full actual STAR run and computes the profile-weighted **SQS**. This skill does not run the scorer or emit the composite. Unverified conversions emit `results-unverified`: report `R1`/`R2`/`R5` as low-confidence and make no attributable-return claims. These financial numbers are consumed as R evidence; they are not themselves an SQS.

   For a multi-creator campaign, the gate scores each creator partnership separately; a budget-weighted mean of the per-partnership SQS values may summarize the campaign but never replaces the per-partnership diagnosis. This skill supplies the per-partnership Return evidence; it does not aggregate or roll up a composite.

10. **Persist only with permission** — save under `memory/influencer/roi-calculator/` (or the paid path) only after authorization; request separate authorization for hot-cache promotion.

## Example

**User**: "Calculate ROI for our influencer campaign: $25K spend, $72K revenue, 2.1M reach"

**Output**:

```markdown
# ROI Calculation Summary

## Investment & Returns

| Item | Value |
|------|-------|
| Total Investment | $25,000 |
| Direct Revenue | $72,000 |
| Total Reach | 2,100,000 |

## ROI Results

### Direct ROI
- **Profit**: $47,000
- **ROI**: 188%
- **ROAS**: 2.88:1

For every $1 spent, you generated $2.88 in revenue.

### Earned Media Value
- **EMV** (directional scenario at a declared $8 CPM): $16,800
- **EMV Multiple**: 0.67x

### Cost Efficiency
- **CPM**: $11.90
- **CPA**: Unknown (conversion count was not supplied)

## Assessment: Profitable on the supplied direct-revenue basis

Direct revenue exceeds the supplied investment, but no source-dated peer target or incrementality evidence was provided. Do not infer benchmark outperformance or authorize a scale decision from this read alone; obtain verified conversions, attribution evidence, and the campaign owner's precommitted decision rule first.
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
