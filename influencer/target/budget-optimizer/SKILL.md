---
name: budget-optimizer
slug: budget-optimizer
displayName: "Budget Optimizer · 预算优化"
summary: "跨创作者与层级的预算分配:目标导向的花费拆分与情景对比"
description: 'Use when the user asks to "allocate my influencer budget", "optimize spend across tiers", or "compare budget scenarios"; produces a tier/platform/content allocation table, ROI and CPM/CPE projections, scenario comparisons, and mid-campaign reallocation moves. Not for building the full campaign plan — use campaign-planner. 达人预算分配/投放预算优化'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when planning budget allocation for a new influencer campaign, splitting spend across nano/micro/macro tiers or platforms, estimating influencer costs and projecting ROI, modeling conservative vs aggressive scenarios, justifying a budget request, or reallocating budget mid-campaign based on performance."
argument-hint: "<total budget> [platforms] [campaign goal]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "target", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "target"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
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
- **Writes**: a budget allocation recommendation (tier / platform / content tables), ROI and cost-efficiency projections, scenario comparison, optimization strategies, plus a handoff summary. Save path: `memory/influencer/budget-optimizer/YYYY-MM-DD-<topic>.md`.
- **Promotes**: approved total budget, the chosen scenario, locked tier mix, and any spend constraints — promote durable facts to `memory/hot-cache.md`.
- **Done when**:
  1. Allocation sums to 100% of the stated budget with a contingency line.
  2. Every projected metric is labeled Measured / User-provided / Estimated.
  3. One recommended scenario is named with its rationale.
- **Primary next skill**: [outreach-manager](../../activate/outreach-manager/SKILL.md) — turn the funded allocation into influencer outreach.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Cross-discipline: ad spend allocation

This skill also allocates **paid-ads** spend — the tier/platform tables map to channels/campaigns; use the ROAS profile (`direct-response|prospecting|incremental-profit`) as the scenario axis and read its declared CPA/payback/contribution constraint instead of substituting CPM/CPE. Scope: this computes the spend-reallocation **plan** only. It does **not** read in-flight pacing or issue scale-up/down moves — the live pacing read (pacing vs plan, learning-phase respect) belongs to [budget-pacing-monitor](../../../ad/scale/budget-pacing-monitor/SKILL.md), and bid-strategy choice belongs to [bid-strategy-planner](../../../ad/orchestrate/bid-strategy-planner/SKILL.md). [paid-measurement-loop](../../../ad/scale/paid-measurement-loop/SKILL.md) reads one shipped change back against a control, and premature scaling is an **S guardrail flag** in [ad-account-auditor](../../../ad/activate/ad-account-auditor/SKILL.md), not a separate skill or a veto. Save paid runs under `memory/ad/budget-optimizer/`.

## Data Sources

This family has no required live integrations (Tier 1). The skill works with nothing but the numbers you provide — give it your total budget, target platforms, and campaign goal, and it runs against the built-in cost benchmarks below.

Optional connectors that sharpen the estimates when present:

- `~~influencer database` — real rate cards instead of benchmark ranges.
- `~~social platform analytics` — actual reach, CPM, and engagement to replace estimated projections.
- `~~CRM` — past campaign spend and conversion data for ROI calibration.

Mark any connector-derived number Measured; mark benchmark-derived numbers Estimated; mark numbers you state as User-provided. See [CONNECTORS.md](../../../CONNECTORS.md) for the keyless data recipes.

## Instructions

When a user requests budget optimization, work these steps. Each step's fill-in template, benchmark table, and scenario block lives in [references/templates.md](references/templates.md) — copy the matching section and populate it.

1. **Gather budget parameters** — campaign goal, audience, timeline, total budget, fixed vs influencer-available split, platform priorities, and constraints (max per influencer, min count). Intake template: [§Step 1](references/templates.md#step-1--budget-parameters-intake-template).
2. **Analyze cost benchmarks** — apply the per-tier/per-platform rate tables (Instagram, TikTok, YouTube) and the industry cost multiplier. Tables: [§Step 2](references/templates.md#step-2--cost-benchmarks).
3. **Create the allocation** — split across tier, platform, content type, and other items (gifting, amplification, tools, contingency); sum must reach 100% with a 5-10% contingency line. Template: [§Step 3](references/templates.md#step-3--budget-allocation-recommendation).
4. **Project ROI** — expected reach/impressions/engagements/EMV, cost-efficiency (CPM/CPE/CPV/CPC vs industry avg), and a conversion funnel to ROAS when relevant. Label each metric Measured / User-provided / Estimated. Template: [§Step 4](references/templates.md#step-4--roi-projections).
5. **Model scenarios** — Conservative / Recommended / Aggressive side-by-side, then name one recommended scenario with rationale. A/B/C blocks: [§Step 5](references/templates.md#step-5--budget-scenarios).
6. **Optimization strategies** — cost-reduction levers, value-maximization moves, and budget red flags (e.g. >40% on a single influencer). Detail: [§Step 6](references/templates.md#step-6--optimization-strategies).
7. **Mid-campaign reallocation** (when spend-to-date + per-influencer results are provided) — actual vs plan, top/under performers, and move budget from losers to winners. Template: [§Step 7](references/templates.md#step-7--mid-campaign-reallocation).

Save the run to `memory/influencer/budget-optimizer/YYYY-MM-DD-<topic>.md` (paid-ads runs to `memory/ad/budget-optimizer/`); promote the approved total, chosen scenario, and locked tier mix to `memory/hot-cache.md`.

## Example

**User**: "Optimize a $30,000 budget for a skincare product launch on Instagram and TikTok targeting Gen Z"

**Output**:

```markdown
## Budget Allocation: $30,000 Skincare Launch

### Recommended Distribution

| Category | Allocation | Notes |
|----------|------------|-------|
| TikTok Influencers | $15,000 (50%) | Primary for Gen Z |
| Instagram Influencers | $9,000 (30%) | Credibility + visual |
| Content Amplification | $4,500 (15%) | Boost top performers |
| Contingency | $1,500 (5%) | Flexibility |

### Influencer Mix

| Platform | Tier | # | Cost Each | Total | Content |
|----------|------|---|-----------|-------|---------|
| TikTok | Micro (50-100K) | 5 | $1,500 | $7,500 | 5 videos |
| TikTok | Nano (10-50K) | 15 | $500 | $7,500 | 15 videos |
| Instagram | Micro (50-100K) | 3 | $2,000 | $6,000 | 3 Reels + Stories |
| Instagram | Nano (10-50K) | 6 | $500 | $3,000 | 6 posts |

**Total Influencers**: 29
**Total Content Pieces**: 29+ (excluding stories)

### Projected Results

- Reach: 2.8M - 3.5M (Estimated)
- Engagements: 280K - 400K (Estimated)
- CPM: $8.50 - $10.70 (Estimated)
- Projected ROI: 3.5:1 (Estimated)

This allocation prioritizes TikTok for viral potential while using Instagram for credibility and detailed product showcase.
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

**Primary**: [outreach-manager](../../activate/outreach-manager/SKILL.md) — once the allocation is funded and the tier mix is locked, move to recruiting the influencers it pays for.

**Alternates** (same influencer family):

- [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — if you need to source candidates that fit each tier's per-influencer budget first.
- [campaign-planner](../campaign-planner/SKILL.md) — if the budget exposed a gap in the underlying campaign plan.

**Termination**: keep a visited-set. If the recommended next skill was already invoked in this session's chain, stop and report chain-complete instead of re-invoking. Default `max-depth: 3`. When routing is ambiguous, present the options and stop rather than auto-following.
