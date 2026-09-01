---
name: report-generator
slug: aaron-report-generator
displayName: "Report Generator · 报告生成"
summary: "面向干系人的营销活动报告:叙事结构、图表建议与洞察提炼"
description: 'Use when the user asks to "create a campaign report", "build an executive summary", or "deliver client results"; produces audience-tailored influencer marketing reports (executive, client, internal team) with data tables, narrative, key learnings, and recommendations. Not for raw metric computation — use performance-analyzer. 达人营销报告/结案汇报'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate after a campaign or reporting period ends and the user needs a written report for a specific stakeholder. Triggers include post-campaign wrap-ups, executive or board summaries, client-facing results decks, internal team retrospectives, and monthly or quarterly performance reports. Pick this when the inputs are already-computed metrics that need structure, narrative, and recommendations for a named audience."
argument-hint: "<campaign name> [audience: executive|client|team|board]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
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

- **Reads**: campaign name, reporting period, target audience, opaque `client_ref`, `preparer_ref`, `contact_ref`, and `owner_ref` values when those roles appear, plus already-computed metrics with their provenance, window, target/comparator, and source artifact refs. ROI/ROAS/net-return values must come from [roi-calculator](../roi-calculator/SKILL.md), and performance deltas/rankings from [performance-analyzer](../performance-analyzer/SKILL.md); raw spend plus revenue is not a computed ROI handoff. Reuse opaque `creator_ref` values from those artifacts, the optional tracker/stage, and an existing Campaign Retro Card. Raw client/staff/owner names, email addresses, and organization labels are transient resolver inputs only.
- **Writes**: return the finished audience-appropriate report inline by default. Preserve only a current scope-bound Campaign Retro Card from `performance-analyzer`; if it is absent or invalid, include an `unknown` placeholder rather than deriving a decision. Save the report/card together to `memory/influencer/report-generator/YYYY-MM-DD-<topic>.md` only with exact WARM-save authorization. Every saved report, template field, appendix, and handoff uses opaque `client_ref`, `preparer_ref`, `contact_ref`, `owner_ref`, `creator_ref`, and artifact/source refs—never resolved client/staff/owner/creator names, organization labels, contact emails, profile URLs, or provider IDs. Resolve those refs only in-memory for one explicitly named audience's transient render, discard the resolution afterward, and never save the mapping. Any external send/share/export requires a new exact authorization naming the report artifact/version, recipient audience, delivery channel, and identity/asset refs allowed for that audience; report creation or WARM save does not authorize distribution.
- **Promotes**: only with separate exact authorization, promote durable evidence-backed facts (verified final ROI/ROAS, measured performance baselines, and headline learnings) to `memory/hot-cache.md`. The Retro Card's qualitative `renew | retest | retire | unknown` decision, rationale, next hypothesis, and limitations remain WARM and are not creator-registry facts. This skill makes no creator-registry proposal: after a creator row is closed, only a separately authorized, evidence-backed **actual rate**, **signed rights window/expiry**, or **measured performance baseline** may be proposed by the owning workflow; [creator-registry](../../../protocol/creator-registry/SKILL.md) alone decides whether it becomes canonical.
- **Done when**:
  1. The report matches the requested audience template (executive, client, team, or board).
  2. Every metric is paired with compatible source-dated context (target, benchmark, or prior period) or explicitly marked `Unknown`/`NEEDS_INPUT`; the report does not manufacture context or recompute missing performance/return metrics.
  3. The report ends with concrete recommendations and, where relevant, action items.
  4. When current tracker-state evidence proves `measured` or `closed`, the report package preserves the matching performance-analyzer Retro Card with exact campaign/creator/state/measurement/decision-rule refs; a missing or invalid card produces an `unknown` placeholder and `NEEDS_INPUT`, never a newly derived decision.
  5. Saved/copyable output contains only opaque client/preparer/contact/owner/creator refs; any resolved labels/contact details exist only in a transient render for the declared audience, and external distribution is blocked without a fresh audience-scoped exact authorization.
- **Primary next skill**: [content-quality-auditor](../../../seo-geo/tune/content-quality-auditor/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family ships Tier 1: no live integration is required. Give it already-computed, provenance-labeled campaign metrics and it builds the report. If only raw observations are supplied, route metric analysis to `performance-analyzer`; if only spend/revenue/LTV inputs are supplied, route return math to `roi-calculator` before reporting.

Optional connectors that can pre-fill data where available:

- `~~social platform analytics` — reach, impressions, engagement, video views per post
- `~~influencer database` — creator handles, tiers, fees, audience demographics
- `~~analytics` — link clicks, conversions, attributed revenue
- `~~CRM` — new-customer counts and downstream revenue

Without any of these, the skill asks for the existing computed artifacts/metrics. It may return a partial report shell, but any missing dependent claim remains `Unknown`/`NEEDS_INPUT`; it does not calculate ROI/ROAS, rankings, attribution, or causal drivers here. See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless data recipe per category.

## Instructions

When a user requests a report:

1. **Determine report parameters** — set report type (post-campaign/monthly/quarterly/annual), campaign(s), period, one explicit audience, opaque `client_ref`/`preparer_ref`/`contact_ref`/`owner_ref` values where applicable, and supplied tracker stage when present. Match depth to the audience: executive wants ROI and strategy at a high level; client wants results and value; team wants detailed learnings and optimization; board wants business impact. Keep any raw identity/contact locator transient. See the audience-needs matrix in [report-templates.md](references/report-templates.md).

2. **Pick the audience template and fill it in** — full executive, client, and internal-team templates live in [report-templates.md](references/report-templates.md). Pull performance metrics/deltas only from `performance-analyzer` output and financial ratios only from `roi-calculator` output. If the required computed artifact is absent, return a partial shell plus `NEEDS_INPUT` and the exact handoff; do not recompute from raw numbers. Pair every metric with compatible source-dated context or mark the comparison pending.

3. **Apply visualization and writing guidance** — choose the right chart per data point and per audience, and follow the lead-with-outcomes narrative arc. See the visualization recommendations and writing best practices in [report-templates.md](references/report-templates.md).

4. **Close with recommendations and action items** — end every report with concrete next steps; add an opaque `owner_ref`/deadline action-items table for team and board audiences.

5. **Represent the measured cycle without re-deciding it** — only preserve an existing Campaign Retro Card from `performance-analyzer` when it explicitly binds the same `campaign_id`, opaque `creator_ref`, current non-forked measured/closed tracker-state ref, locked measurement contract, and precommitted decision-rule ref. Never derive or change the decision in this reporting skill. If the card is absent, mismatched, or stale, emit a bound `decision: unknown` placeholder plus `NEEDS_INPUT` for the performance-analyzer artifact. Keep the card outside a client/board-facing copy unless the user requests it.

6. **Return, then offer persistence or distribution** — return the ref-only report and any Retro Card inline. Offer `memory/influencer/report-generator/YYYY-MM-DD-<topic>.md` (or `memory/ad/report-generator/` for paid runs) for exact WARM-save authorization; the saved artifact keeps `client_ref`, `preparer_ref`, `contact_ref`, and `owner_ref` unresolved. If the user requests a human-readable audience copy, resolve only the approved refs in-memory for that one explicit audience and discard the mapping after rendering. Before any external send/share/export, require a new exact authorization naming the exact report artifact/version, recipient audience, delivery channel, and allowed identity/asset refs; never infer distribution authority from report generation, transient rendering, or WARM save. Request a separate authorization before promoting any eligible durable fact to `memory/hot-cache.md`. After an authorized save, offer a handoff to [campaign-planner](../../target/campaign-planner/SKILL.md) to append the saved artifact reference to the relevant tracker row's `evidence_refs`; that tracker edit needs a fresh path-and-operation-scoped exact WARM authorization, and this skill neither edits the tracker nor advances its `stage`.

7. **Offer, do not launch, the next-cycle assessment** — if the user wants to select the next roster, offer an explicit handoff to [fit-scorer](../../scout/fit-scorer/SKILL.md) with the Retro Card's cited evidence and `next_campaign_hypothesis`. Do not invoke it automatically and do not translate, invent, or carry forward a STAR/SQS verdict from the qualitative Retro decision.

## Example

**User**: "Create an executive report for Holiday Campaign 2024. `roi-ref-01` already reports $50K spend, $165K attributed revenue, 230% arithmetic ROI and 3.3:1 ROAS on its declared verified basis. `performance-ref-01` reports 3.5M reach across 15 opaque creator refs and calculated target deltas. The preregistered targets were $100K attributed revenue, 2:1 ROAS, and 2M reach. No segmented breakdown or reallocation rule is included."

**Output** (excerpt — full template in [report-templates.md](references/report-templates.md)):

```markdown
# Holiday Campaign 2024: Executive Summary

## Bottom Line: Campaign Exceeded the Supplied Targets ✅

**ROI: 230% (`roi-ref-01`)** | **ROAS: 3.3:1 (`roi-ref-01`)** | **Attributed Revenue: $165,000**

Metric status: financial values and their calculation/provenance come from `roi-ref-01`; reach and target deltas come from `performance-ref-01`. This report formats those outputs and performs no return or attribution recomputation. No incremental-revenue claim is made.

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Attributed revenue | $100K | $165K | ✅ +65% |
| ROAS | 2:1 | 3.3:1 | ✅ +65% |
| Reach | 2M | 3.5M | ✅ +75% |

### Recommendation

The supplied overall figures clear the supplied targets. A platform, creator-tier, content-format, or budget-change recommendation is `NEEDS_INPUT` because no segmented results or decision rule was supplied; request that evidence before proposing a Q1 reallocation.
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
