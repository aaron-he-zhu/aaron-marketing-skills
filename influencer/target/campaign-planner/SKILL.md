---
name: campaign-planner
slug: aaron-campaign-planner
displayName: "Campaign Planner · 活动规划"
summary: "红人活动整体规划:目标、阶段、创作者组合、时间线与风险预案"
description: 'Use when the user asks to "plan an influencer campaign", "build a campaign blueprint", or "launch a product with creators"; produces campaign objectives, platform and influencer-tier strategy, content requirements, a phased timeline, budget allocation, and KPI targets. Not for writing individual creator briefs — use brief-generator; not for the overall product-launch plan (tiering, calendar, press, community day) — use launch-tier-planner, which hands this skill the creator lane. A launch request that does not mention creators routes to the launch discipline, not here. 达人营销策划/种草方案'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when planning a new influencer campaign, launching a product with influencer support, building seasonal or tentpole activations, designing always-on creator programs, restructuring an underperforming campaign, or preparing a campaign plan to present to stakeholders. Activate when the user gives a brand, budget, audience, or timeframe and wants the full strategy-to-execution blueprint before briefs or outreach begin."
argument-hint: "<brand or product> [budget] [platform] [timeframe]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "target", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "target"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Campaign Planner

Designs an influencer campaign from strategy to execution plan — an actionable blueprint that ties business objectives to creative execution.

**Scope edge — product launches**: this skill owns the **creator lane** of a launch. The launch itself — tier/type decision, launch calendar, press motion, community launch day, readiness gate — belongs to the launch discipline ([launch-tier-planner](../../../launch/research/launch-tier-planner/SKILL.md) and siblings), which hands this skill the creator-channel sub-plan aligned to the [launch-registry](../../../protocol/launch-registry/SKILL.md) date and stage. "Launch a product with creators" starts here; "launch a product" starts there.

## Quick Start

```
Create an influencer campaign plan for [product launch]
```

```
Plan an influencer campaign for [brand] with [budget] targeting [audience] during [timeframe]
```

## Skill Contract

- **Reads**: brand and product details, target audience, campaign type, budget, timeline, and any constraints supplied by the user. If `memory-management` is active, prior audience profiles and past-campaign benchmarks load from the hot cache.
- **Writes**: a campaign plan document saved to `memory/influencer/campaign-planner/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable facts (campaign name, primary objective, total budget, go-live date, KPI targets) to `memory/hot-cache.md`.
- **Done when**:
  - Objectives are SMART and have explicit success and failure definitions.
  - Influencer mix, content deliverables, timeline, budget, and KPIs are each specified with numbers, not placeholders.
  - The plan names the next step (brief generation) and any open approvals.
- **Primary next skill**: [brief-generator](../brief-generator/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family is Tier 1: every skill works with no live integrations. Provide the brand, audience, budget, and timeline directly and the plan builds from your inputs.

Optional connectors that strengthen the plan when available:

- `~~influencer database` — size the influencer mix and validate tier follower ranges.
- `~~social platform analytics` — set platform-specific reach and engagement benchmarks.
- `~~CRM` — align conversion targets and attribution with existing pipeline data.
- `~~analytics` — pull past-campaign actuals for realistic KPI and budget-efficiency targets.

See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless data recipe per category. Without any connector, ask the user for the missing inputs and proceed.

## Instructions

Work the nine steps in order. Each has a fill-in template in [references/templates.md](references/templates.md) — copy the matching block, replace every bracket with a real number or value (no placeholders left in the final plan), and assemble in step 9.

1. **Gather campaign requirements** — capture brand, value prop, audience, campaign type, timeline, budget, and constraints (template §1).
2. **Define objectives** — one SMART primary objective plus secondary objectives, with explicit success and failure definitions (template §2).
3. **Develop strategy** — big idea, strategy statement, audience, key messages, campaign pillars, platform split, and differentiation (template §3).
4. **Define influencer criteria** — tier mix, must-have and preferred selection criteria, exclusions, ideal profile, and relationship types. Validate follower ranges against [references/influencer-tiers.md](references/influencer-tiers.md) (template §4).
5. **Plan content requirements** — deliverables by platform/format, required elements, creative direction, themes, and the approval chain (template §5).
6. **Create the timeline** — key dates, a four-phase week-by-week plan, and a Gantt view (template §6).
7. **Allocate budget** — breakdown by category, by influencer tier, by platform, plus CPM/CPE/cost-per-content efficiency targets (template §7).
8. **Establish success metrics** — primary KPIs vs benchmarks, secondary metrics, conversion metrics, and reporting cadence (template §8).
9. **Compile the plan document** — executive summary, the full sections above, and an appendix with risk mitigation (template §9). Save to the Writes path and promote durable facts to the hot cache.

## Example

**User**: "Create a campaign plan for a new sustainable sneaker launch targeting Gen Z on TikTok and Instagram with a $50K budget"

**Output**: A complete plan with sustainability messaging, a micro-influencer-heavy mix, UGC-focused content, a phased launch timeline, and conversion tracking via promo codes. (Fuller walkthrough in [references/templates.md](references/templates.md#worked-example).)

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in templates for all nine steps, the worked example, and success tips.
- [references/influencer-tiers.md](references/influencer-tiers.md) — influencer-vs-affiliate-vs-creator decision table and nano/micro/mid/macro tier definitions; `fit-scorer` and `budget-optimizer` can consult it.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff schema.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipes per connector category.
- [audience-mapper](../../scout/audience-mapper/SKILL.md) — define the target audience this plan serves.
- [brief-generator](../brief-generator/SKILL.md) — turn the plan into per-influencer briefs.
- [budget-optimizer](../budget-optimizer/SKILL.md) — refine the budget allocation.
- [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — find influencers matching the criteria.

## Next Best Skill

- **Primary**: [brief-generator](../brief-generator/SKILL.md) — convert the approved plan into concrete influencer briefs.
- **Alternate**: [budget-optimizer](../budget-optimizer/SKILL.md) — pressure-test and optimize the budget split before locking the plan.
- **Alternate**: [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — build the shortlist against the selection criteria defined here.

Termination note: keep a visited-set of skills invoked this session. If the primary next skill has already run this session, stop and report the chain complete rather than re-invoking. Do not chain deeper than 3 hops from the originating request.
