---
name: roi-calculator
description: 'Use when the user asks to "calculate influencer ROI", "prove campaign value", or "what was our ROAS"; produces direct ROI/ROAS, earned media value, attribution-modeled revenue, LTV-based ROI, and a stakeholder-ready summary. Not for building the full slide/written report — use report-generator.'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when measuring or projecting influencer campaign ROI, justifying or defending budgets, comparing ROI across campaigns or channels, evaluating individual influencer or tier value, or preparing executive-level ROI numbers. Activate when the user supplies spend and results data and wants ROI, ROAS, EMV, CPA/CAC, attribution, or LTV impact computed."
argument-hint: "<campaign name or spend> [revenue] [results data]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: influencer
  phase: measure
  family: influencer-marketing
  impact-phase: Track
---

# ROI Calculator

This skill helps you calculate and communicate the return on investment for influencer marketing campaigns using various methodologies appropriate for your goals and available data.

> **Cross-discipline (paid ads):** this is the shared **return-math engine** for paid ads — [paid-measurement-loop](../../paid/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../../paid/scale/attribution-reconciler/SKILL.md), and budget-optimizer delegate ROAS/CPA/payback ratios here rather than recomputing them. Save paid runs under `memory/paid-ads/roi-calculator/`.

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
- **Promotes**: durable headline numbers (final ROI %, ROAS, total investment, net profit, recommended attribution model) to `memory/hot-cache.md`.
- **Done when**:
  1. At least one ROI methodology is computed with the inputs and formula shown.
  2. Each headline metric is stated against a benchmark with a pass/fail status.
  3. A bottom-line assessment (profitable / break-even / loss) and 1-3 recommendations are written.
- **Primary next skill**: [report-generator](../../measure/report-generator/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family is Tier 1 — it works with no live integrations. Ask the user for spend and results data and compute everything from those inputs. Connectors below can pull the numbers automatically when available:

- `~~social platform analytics` — reach, impressions, engagements, video views per platform for EMV and cost-per-metric math.
- `~~ecommerce / analytics` — revenue, conversions, link clicks, and AOV for direct ROI and attribution.
- `~~CRM` — new-customer counts, repeat-purchase rate, and lifetime value for LTV-based ROI.
- `~~influencer database` — per-influencer fees and tier data for by-influencer ROI.

With zero integrations, supply the investment and results tables by hand and the skill still produces every calculation. See [CONNECTORS.md](../../CONNECTORS.md) for the free/keyless recipe per category.

## Instructions

When a user requests ROI calculation, work the steps below. Each step has a fill-in template in [references/roi-templates.md](references/roi-templates.md) — link the step number to its block there.

1. **Gather ROI inputs** — campaign details, the investment (total spend) table, and the results-data table. ([template](references/roi-templates.md#step-1--roi-calculation-inputs))

2. **Calculate direct ROI** — Simple ROI = (Revenue − Investment) / Investment × 100; ROAS = Revenue / Investment. State profit and a Profitable/Break-even/Loss assessment. ([template](references/roi-templates.md#step-2--direct-roi-calculation))

3. **Calculate Earned Media Value (EMV)** — impression-based (Impressions × CPM / 1000) and engagement-based (Engagements × CPE), then average. Flag EMV as directional, not absolute. ([template](references/roi-templates.md#step-3--earned-media-value-emv))

4. **Calculate cost-efficiency metrics** — CPM, CPR, CPE, CPV, CPC, CPA, CAC, each against a benchmark; rate the campaign and compare CPA to other channels. ([template](references/roi-templates.md#step-4--cost-efficiency-analysis))

5. **Apply attribution modeling** — run first-touch, last-touch, linear, time-decay, and position-based; recommend the model that fits the customer journey. ([template](references/roi-templates.md#step-5--attribution-analysis))

6. **Calculate customer lifetime value impact** — LTV-Based ROI = (New Customers × Avg LTV − Investment) / Investment; project short- vs. long-term and compare customer quality to organic/paid. ([template](references/roi-templates.md#step-6--lifetime-value-analysis))

7. **Calculate by-influencer ROI** — per-influencer ROI/ROAS rank, investment efficiency, and ROI by tier (macro/micro/nano). ([template](references/roi-templates.md#step-7--influencer-level-roi))

8. **Generate the ROI report summary** — investment, returns, ROI by methodology, key metrics vs. benchmark, bottom line, and 1-3 recommendations. ([template](references/roi-templates.md#step-8--roi-summary-report))

9. **Roll up into the C³ Campaign Value Index (CVI)**

   This skill emits the **ROI** scope score of [C³](../../references/c3-benchmark.md) and the **CVI** rollup. Score ROI on the **0–100 rubric** in [c3/roi-campaign-benchmark.md](../../references/c3/roi-campaign-benchmark.md) (Return · Orchestration · Impact, each on Pass/Partial/Fail → scaled to 0–100). **This 0–100 ROI score is not the financial ROI % from steps 1–8** — feed the rubric score into the formula, never the percentage (R1 simply *consumes* your ROI%/ROAS as one of its inputs). Then combine it with the Creator and Content scope scores — from [fit-scorer](../../discover/fit-scorer/SKILL.md) (ACE) and [content-reviewer](../../activate/content-reviewer/SKILL.md) (ART) — as a geometric mean:

   ```
   CVI = ( ACE_avg × ART_avg × ROI )^(1/3)
   ```

   `ACE_avg` is the **budget-weighted** mean of the campaign's creator ACE scores; `ART_avg` is the simple mean of its content ART scores (per scoring-architecture §8). Keep the three scope scores beside the CVI — the index ranks and alerts, the three scores diagnose. If ACE or ART is unavailable, emit the ROI score and mark CVI **pending (needs ACE/ART)** rather than guessing. A blocked scope (e.g. an ART T1/T2 veto on the content, or an ACE A2/C1/E2 veto on the creator) caps the rollup — surface it, don't average it away.

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
- **EMV** (at $8 CPM): $16,800
- **EMV Multiple**: 0.67x

### Cost Efficiency
- **CPM**: $11.90 (Good)
- **Est. CPA**: ~$54 (if 460 conversions)

## Assessment: ✅ Strong Performance

This campaign outperformed the typical 2:1 ROAS benchmark for influencer marketing. Recommend increasing investment in similar campaigns.
```

Industry ROAS benchmarks (Beauty, Fashion, Food & Beverage, Tech, Health) live in [references/roi-templates.md#industry-roi-benchmarks](references/roi-templates.md#industry-roi-benchmarks).

## Reference Materials

- [references/roi-templates.md](references/roi-templates.md) — fill-in templates for every Instructions step, the worked example, and industry ROAS benchmarks.
- [measurement-protocol.md](../../references/measurement-protocol.md) — read ROI/CVI deltas against a control over the readback window; do not over-claim attribution.
- [skill-contract.md](../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../CONNECTORS.md) — free/keyless data recipe per connector category.
- C³ scoring: [c3-benchmark.md](../../references/c3-benchmark.md) (CVI rollup formula) and [c3/roi-campaign-benchmark.md](../../references/c3/roi-campaign-benchmark.md) — the ROI Campaign rubric this skill emits into the CVI.
- [performance-analyzer](../performance-analyzer/SKILL.md) — supplies the results data this skill consumes.
- [report-generator](../../measure/report-generator/SKILL.md) — wraps these numbers into a full report.
- [budget-optimizer](../../plan/budget-optimizer/SKILL.md) — uses ROI output to reallocate spend.
- [campaign-planner](../../plan/campaign-planner/SKILL.md) — sets the ROI targets these results are checked against.

## Next Best Skill

**Primary**: [report-generator](../../measure/report-generator/SKILL.md) — turn the ROI numbers into a stakeholder-ready report.

**Alternates** (same Track family):

- [performance-analyzer](../performance-analyzer/SKILL.md) — go back for deeper performance breakdowns if the ROI math exposed gaps.
- [budget-optimizer](../../plan/budget-optimizer/SKILL.md) — feed by-influencer and by-tier ROI into the next budget allocation.

Termination note: keep a visited-set of skills invoked this session. If the primary next skill was already run, stop and report the chain complete rather than re-invoking it. Stop after at most 3 hops in a single chain.
