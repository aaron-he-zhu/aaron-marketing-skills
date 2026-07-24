---
name: report-generator
slug: aaron-report-generator
displayName: "Report Generator · 报告生成"
summary: "面向干系人的营销活动报告:叙事结构、图表建议与洞察提炼"
description: 'Use when the user asks to "create a campaign report", "build an executive summary", or "deliver client results"; produces audience-tailored influencer marketing reports (executive, client, internal team) with data tables, narrative, key learnings, and recommendations. Not for raw metric computation — use performance-analyzer. 达人营销报告/结案汇报'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate after a campaign or reporting period ends and the user needs a written report for a specific stakeholder. Triggers include post-campaign wrap-ups, executive or board summaries, client-facing results decks, internal team retrospectives, and monthly or quarterly performance reports. Pick this when the inputs are already-computed metrics that need structure, narrative, and recommendations for a named audience."
argument-hint: "<campaign name> [audience: executive|client|team|board]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Report Generator

This skill helps you create professional influencer marketing reports that tell the story of your campaign performance. It adapts content and depth based on the audience.

> **Cross-discipline (paid ads):** this is also the **paid-ads** reporting surface — build exec/client/channel reports from RQS history (`memory/audits/ad/`) and measurement-loop readback verdicts. It presents metrics; it does not compute them (return math stays in [roi-calculator](../roi-calculator/SKILL.md)). Save paid runs under `memory/ad/report-generator/`.

## Quick Start

Shortest invocation:

```
Create a campaign report for [campaign name] for [audience: executive/client/team]
```

Common scenario:

```
Generate an executive summary for our Q3 influencer campaigns
```

## Skill Contract

- **Reads**: campaign name, reporting period, target audience, and computed metrics (reach, engagement, conversions, spend, revenue, ROI/ROAS, per-influencer results). Prior outputs from `performance-analyzer` and `roi-calculator` if available.
- **Writes**: a finished report in the audience-appropriate template, saved to `memory/influencer/report-generator/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable verdicts (final ROI/ROAS, top performers, renew/drop calls, headline learnings) to `memory/hot-cache.md`.
- **Done when**:
  1. The report matches the requested audience template (executive, client, team, or board).
  2. Every metric is paired with context (target, benchmark, or prior period).
  3. The report ends with concrete recommendations and, where relevant, action items.
- **Primary next skill**: [content-quality-auditor](../../../seo-geo/tune/content-quality-auditor/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family ships Tier 1: every step works with no live integration. Give the skill the campaign metrics directly and it builds the report from your inputs.

Optional connectors that can pre-fill data where available:

- `~~social platform analytics` — reach, impressions, engagement, video views per post
- `~~influencer database` — creator handles, tiers, fees, audience demographics
- `~~analytics` — link clicks, conversions, attributed revenue
- `~~CRM` — new-customer counts and downstream revenue

Without any of these, the skill asks you for the numbers and proceeds. See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless data recipe per category.

## Instructions

When a user requests a report:

1. **Determine report parameters** — set report type (post-campaign/monthly/quarterly/annual), campaign(s), period, and audience. Match depth to the audience: executive wants ROI and strategy at a high level; client wants results and value; team wants detailed learnings and optimization; board wants business impact. See the audience-needs matrix in [report-templates.md](references/report-templates.md).

2. **Pick the audience template and fill it in** — full executive, client, and internal-team templates live in [report-templates.md](references/report-templates.md). Pull metrics from `performance-analyzer` and `roi-calculator` outputs when present; otherwise ask the user for the numbers. Pair every metric with context (target, benchmark, or prior period).

3. **Apply visualization and writing guidance** — choose the right chart per data point and per audience, and follow the lead-with-outcomes narrative arc. See the visualization recommendations and writing best practices in [report-templates.md](references/report-templates.md).

4. **Close with recommendations and action items** — end every report with concrete next steps; add an owner/deadline action-items table for team and board audiences.

5. **Save and promote** — write the finished report to `memory/influencer/report-generator/YYYY-MM-DD-<topic>.md` (paid runs to `memory/ad/report-generator/`). Promote durable verdicts (final ROI/ROAS, top performers, renew/drop calls, headline learnings) to `memory/hot-cache.md`.

## Example

**User**: "Create an executive report for our holiday campaign: $50K spend, $165K revenue, 3.5M reach across 15 influencers"

**Output** (excerpt — full template in [report-templates.md](references/report-templates.md)):

```markdown
# Holiday Campaign 2024: Executive Summary

## Bottom Line: Campaign Exceeded All Targets ✅

**ROI: 230%** | **ROAS: 3.3:1** | **Revenue: $165,000**

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Revenue | $100K | $165K | ✅ +65% |
| ROAS | 2:1 | 3.3:1 | ✅ +65% |
| Reach | 2M | 3.5M | ✅ +75% |

### Recommendation

Increase Q1 influencer budget by 25%, focused on TikTok micro-influencers and product-demo content.
```

## Reference Materials

- [report-templates.md](references/report-templates.md) — full executive/client/team templates, visualization recs, writing best practices, worked example
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff format
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path convention
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipes per connector category
- [performance-analyzer](../performance-analyzer/SKILL.md) — generates the metrics this report consumes
- [roi-calculator](../roi-calculator/SKILL.md) — supplies ROI/ROAS figures
- [campaign-planner](../../target/campaign-planner/SKILL.md) — original plan to compare results against
- [content-amplifier](../../activate/content-amplifier/SKILL.md) — amplification results to report on
- [content-quality-auditor](../../../seo-geo/tune/content-quality-auditor/SKILL.md) — quality gate for the report itself

## Next Best Skill

**Primary**: [content-quality-auditor](../../../seo-geo/tune/content-quality-auditor/SKILL.md) — run the finished report through the publish-readiness gate before it goes to a stakeholder.

**Alternates (same report phase / influencer family)**:

- [performance-analyzer](../performance-analyzer/SKILL.md) — if the report exposes data gaps, re-analyze before re-reporting.
- [roi-calculator](../roi-calculator/SKILL.md) — recompute return figures if the financial inputs changed.

**Termination note** (visited-set): if a recommended skill has already been invoked this session, stop and report the chain as complete instead of re-running it. Honor a max chain depth of 3 hops to avoid loops.
