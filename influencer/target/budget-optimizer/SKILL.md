---
name: budget-optimizer
slug: budget-optimizer
displayName: "Budget Optimizer · 预算优化"
summary: "跨创作者与层级的预算分配:目标导向的花费拆分与情景对比"
description: 'Use when the user asks to "allocate my influencer budget", "optimize spend across tiers", or "compare budget scenarios"; produces a tier/platform/content allocation table, ROI and CPM/CPE projections, scenario comparisons, and mid-campaign reallocation moves. Not for building the full campaign plan — use campaign-planner. 达人预算分配/投放预算优化'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when planning budget allocation for a new influencer campaign, splitting spend across nano/micro/macro tiers or platforms, estimating influencer costs and projecting ROI, modeling conservative vs aggressive scenarios, justifying a budget request, or reallocating budget mid-campaign based on performance."
argument-hint: "<total budget> [platforms] [campaign goal]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "target", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "target"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Budget Optimizer

This skill helps you allocate and optimize your influencer marketing budget to maximize return on investment. It considers platform costs, influencer tier economics, and campaign objectives to recommend optimal budget distribution.

## Quick Start

Shortest invocation:

```
Help me allocate a $30,000 budget for an influencer campaign on Instagram and TikTok
```

Common scenario:

```
Optimize my influencer budget across micro and macro influencers for a Gen Z product launch — compare a $50K and a $100K scenario
```

Output: a tier/platform/content allocation table, projected reach + CPM/CPE, 2-3 budget scenarios, and a recommended split.

## Skill Contract

- **Reads**: total budget, fixed vs influencer-available split, campaign goal, target platforms, tier constraints (max per influencer, minimum count), industry, and — for mid-campaign work — spend-to-date and per-influencer results. Connector data via `~~influencer database` / `~~social platform analytics` when available.
- **Writes**: return the budget allocation recommendation and handoff inline by default; save to `memory/influencer/budget-optimizer/YYYY-MM-DD-<topic>.md` (or the declared paid path) only with exact WARM-save authorization.
- **Promotes**: only with separate exact authorization, promote the approved total budget, chosen scenario, locked tier mix, and spend constraints to `memory/hot-cache.md`.
- **Done when**:
  1. Allocation sums to 100% of the stated budget; any contingency amount follows a user rule or a source-dated planning anchor rather than a repository default.
  2. Every projected metric includes its formula, input refs, evidence window, and Measured / User-provided / Estimated label.
  3. One recommended scenario is named with its rationale, or the numerical scenario remains `NEEDS_INPUT` with an exact evidence-request plan.
- **Primary next skill**: use the readiness-gated `Next Best Skill` block below; a budget handoff never authorizes outreach or a send.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Cross-discipline: ad spend allocation

This skill also allocates **paid-ads** spend — the tier/platform tables map to channels/campaigns; use the ROAS profile (`direct-response|prospecting|incremental-profit`) as the scenario axis and read its declared CPA/payback/contribution constraint instead of substituting CPM/CPE. Scope: this computes the spend-reallocation **plan** only. It does **not** read in-flight pacing or issue scale-up/down moves — the live pacing read (pacing vs plan, learning-phase respect) belongs to [budget-pacing-monitor](../../../ad/scale/budget-pacing-monitor/SKILL.md), and bid-strategy choice belongs to [bid-strategy-planner](../../../ad/orchestrate/bid-strategy-planner/SKILL.md). [paid-measurement-loop](../../../ad/scale/paid-measurement-loop/SKILL.md) reads one shipped change back against a control, and premature scaling is an **S guardrail flag** in [ad-account-auditor](../../../ad/activate/ad-account-auditor/SKILL.md), not a separate skill or a veto. Save paid runs under `memory/ad/budget-optimizer/`.

## Data Sources

This family has no required live integration, but numerical rate, multiplier, reach, engagement, revenue, and return projections require a compatible anchor: a user-provided quote or assumption, source-dated market evidence, or comparable first-party history. With only a total budget, platforms, and goal, return an allocation skeleton plus the exact rate-card/forecast queries needed and status `NEEDS_INPUT`; do not invent a repository rate table or multiplier.

Optional connectors that sharpen the estimates when present:

- `~~influencer database` — real rate cards instead of benchmark ranges.
- `~~social platform analytics` — actual reach, CPM, and engagement to replace estimated projections.
- `~~CRM` — past campaign spend and conversion data for ROI calibration.

Classify evidence **field by field**, not by connector provenance. Mark a connector value **Measured** only when it is an observed result for that exact metric, entity, and campaign window (record the source and as-of/window); mark numbers the user states **User-provided**; and mark benchmarks, forecasts, inferred values, and modeled downstream projections **Estimated**. A connector-backed input never upgrades an entire row or a projection derived from assumptions to Measured. See [CONNECTORS.md](../../../CONNECTORS.md) for the keyless data recipes.

## Instructions

When a user requests budget optimization, work these steps. Each step's fill-in template and scenario block lives in [references/templates.md](references/templates.md) — copy the matching section and populate it.

1. **Gather budget parameters** — campaign goal, audience, timeline, total budget, fixed vs influencer-available split, platform priorities, and constraints (max per influencer, min count). Intake template: [§Step 1](references/templates.md#step-1--budget-parameters-intake-template).
2. **Qualify cost evidence** — inventory source-dated, market/platform/tier/deliverable/rights-compatible quotes or first-party history. A rate or multiplier without a compatible source and date stays `NEEDS_INPUT`; never supply a built-in default. Template: [§Step 2](references/templates.md#step-2--cost-evidence).
3. **Create the allocation** — split across tier, platform, content type, and other items (gifting, amplification, tools, contingency); sum to 100%. Use a contingency only when the user or a dated planning source supplied the rule. Template: [§Step 3](references/templates.md#step-3--budget-allocation-recommendation).
4. **Project returns** — record each formula and input ref. Keep EMV as a separate media-equivalency scenario; never add it to attributed revenue or count it as cash return. Report `ROAS = attributed revenue / spend` as `x:1`; report arithmetic ROI as `(attributed revenue - spend) / spend × 100%`; do not claim profitability or incrementality without the required evidence. Template: [§Step 4](references/templates.md#step-4--return-projections).
5. **Model scenarios** — compare only scenarios supported by declared inputs; otherwise return named scenario shells and the missing-input plan. Template: [§Step 5](references/templates.md#step-5--budget-scenarios).
6. **Optimization strategies** — label savings, concentration, and amplification thresholds as user rules or source-dated assumptions. Do not present unsourced percentages as standard. Detail: [§Step 6](references/templates.md#step-6--optimization-strategies).
7. **Mid-campaign reallocation** — require comparable observed results plus a preregistered readback window and decision rule. Recommend `KEEP_TESTING` or `NEEDS_INPUT` when those are absent; a recommendation requires separate action authorization before spend changes. Persist and hand off creators only as `creator_ref`. Template: [§Step 7](references/templates.md#step-7--mid-campaign-reallocation).

Return the run inline. Offer `memory/influencer/budget-optimizer/YYYY-MM-DD-<topic>.md` (or `memory/ad/budget-optimizer/` for paid-ads runs) for exact WARM-save authorization, and request a separate authorization before promoting the approved total, chosen scenario, or locked tier mix to `memory/hot-cache.md`.

## Example

**User**: "Optimize a $30,000 budget for a skincare product launch on Instagram and TikTok targeting Gen Z"

**Output**:

```markdown
## Budget Allocation: $30,000 Skincare Launch

**Status**: NEEDS_INPUT

The budget, platforms, audience, and goal are User-provided. No compatible creator quotes, deliverable/rights scope, contingency rule, reach/engagement history, conversion rate, AOV, or attribution basis was supplied, so no creator count, platform split, CPM, revenue, ROAS, ROI, or EMV is fabricated.

### Evidence request

| Needed input | Exact request |
|--------------|---------------|
| Cost basis | Dated creator quotes or first-party rates for the target market, platform, tier, deliverable, usage-rights term, exclusivity, and currency |
| Forecast basis | Comparable reach/engagement observations with source refs and windows |
| Return basis | Approved conversion rate, AOV, attribution window/method, and whether revenue is gross or net |
| Planning rules | User-approved platform/tier constraints, amplification amount, and contingency rule |

Until these arrive, provide only a 100%-summing allocation worksheet with `TBD` cells and no recommended numerical scenario.
```

## Reference Materials

- Templates, cost benchmarks, scenario A/B/C blocks, optimization tips & second example: [references/templates.md](references/templates.md)
- Shared contract: [skill-contract.md](../../../references/skill-contract.md)
- Shared state model: [state-model.md](../../../references/state-model.md)
- Connector recipes: [CONNECTORS.md](../../../CONNECTORS.md)
- Sibling skills:
  - [campaign-planner](../campaign-planner/SKILL.md) — the campaign plan this budget funds
  - [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — find influencers in budget range
  - [outreach-manager](../../activate/outreach-manager/SKILL.md) — turn the allocation into outreach
  - [roi-calculator](../../report/roi-calculator/SKILL.md) — calculate actual ROI post-campaign
  - [performance-analyzer](../../report/performance-analyzer/SKILL.md) — inform reallocation decisions

## Next Best Skill

**Primary**: [campaign-planner](../campaign-planner/SKILL.md) — when no approved execution-ready campaign plan exists, lock objectives, deliverables, rights, measurement, and decision rules before execution.

**Alternates** (same influencer family):

- [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — when the approved plan exists but a sourced shortlist does not; continue through discovery's documented typed-Fit handoff before treating any creator as selected.
- [outreach-manager](../../activate/outreach-manager/SKILL.md) — only when the campaign plan is approved, creators are selected after Fit, and contact/consent/channel readiness is documented. The handoff prepares outreach; it does not authorize a send.

**Termination**: keep a visited-set. If the recommended next skill was already invoked in this session's chain, stop and report chain-complete instead of re-invoking. Default `max-depth: 3`. When routing is ambiguous, present the options and stop rather than auto-following.
