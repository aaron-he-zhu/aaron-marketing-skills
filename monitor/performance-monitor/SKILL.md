---
name: performance-monitor
description: 'Use when the user asks to "generate an SEO report", "出月报", "set SEO alerts", or "排名掉了提醒我"; two modes — report builds multi-metric traffic/ranking/authority/content dashboards, and alert configures threshold notifications for future ranking, traffic, technical, backlink, competitor, and AI-visibility changes. Not for raw position-by-position deltas — use rank-tracker. SEO报告/绩效仪表盘/SEO预警/排名监控'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when generating multi-metric SEO/GEO performance reports, traffic summaries, stakeholder dashboards, SEO报告, 流量报告, 月报, 周报, 汇报给老板 (mode: report), OR when setting up monitoring alerts for rankings, traffic, backlinks, technical issues, competitor moves, or AI visibility changes, SEO预警, 排名监控 (mode: alert). Not for raw position-by-position ranking deltas — use rank-tracker."
argument-hint: "<domain> [--mode report|alert] [date range | metric]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: seo-geo
  phase: monitor
  geo-relevance: "medium"
---

# Performance Monitor

One monitor skill, two modes. **`report`** builds a stakeholder-facing multi-metric snapshot of what already happened (traffic, rankings, GEO/AI, authority, backlinks, content) and turns period-over-period deltas into prioritized recommendations. **`alert`** configures forward-looking threshold and anomaly notifications so a drop in rankings, traffic, technical health, backlinks, competitor position, or AI citations fires before someone eyeballs it. Pick the mode from intent: past-tense reporting → `report`; future-tense "tell me when" → `alert`.

**Mode set:** `report` (multi-metric snapshot, absorbed from performance-reporter) · `alert` (forward thresholds/anomalies, absorbed from alert-manager). Default when unstated: infer from verb tense (see Decision Gates).

**Scope guard — what this skill does NOT do:** it does not compute the CORE-EEAT content score or run its vetoes (T04/C01/R10) — that gate is [content-quality-auditor](../../optimize/content-quality-auditor/SKILL.md); it does not compute the CITE domain score or run its vetoes (T03/T05/T09) — that gate is [domain-authority-auditor](../domain-authority-auditor/SKILL.md). This skill *reports* those scores when a gate has already produced them and *watches* them for change; it never scores. Raw position-by-position ranking deltas belong to [rank-tracker](../rank-tracker/SKILL.md).

## Quick Start

```text
# report mode
Create an SEO performance report for [domain] for [time period]
Generate an executive summary of SEO performance for [month/quarter]
Create a GEO visibility report for [domain]

# alert mode
Set up SEO monitoring alerts for [domain]
Create ranking drop alerts for my top 20 keywords
Alert me when AI citations for [domain] drop
```

Shortest valid invocation: `performance-monitor <domain>` (mode inferred). Output: **report** returns a metric-table → what-changed → why → next-action dashboard with every figure source-tagged; **alert** returns an alert-config summary with named triggers, thresholds, priorities, and delivery routing. Both emit a handoff summary ready for `memory/monitoring/`.

## Skill Contract

**Expected output**: mode `report` → a delta-based multi-metric report/dashboard; mode `alert` → an alert configuration summary. Both include the standard handoff summary for `memory/monitoring/`.

- **Reads**: prior baselines and current performance data. `report` reads current + prior-period metrics across traffic/rankings/authority/content, report audience, and date range. `alert` reads baselines, critical keywords/metrics to watch, normal volatility, and delivery preferences. Plus any user-provided or tool data.
- **Writes**: a user-facing monitoring deliverable plus a reusable summary storable under `memory/monitoring/`.
- **Promotes**: significant changes, confirmed anomalies, durable thresholds, and follow-up actions; pending decisions go to `memory/open-loops.md` (never directly to `decisions.md`).
- **Done when**:
  - `report`: each in-scope section (traffic, rankings, GEO, authority, backlinks, content) is present or marked "Not yet evaluated"; every metric is source-tagged and compared to the prior period; recommendations carry owner, priority, and expected impact.
  - `alert`: each chosen alert category has a named trigger, threshold, and priority; a Critical/High/Medium/Low response plan and delivery routing are defined; thresholds are tuned to the metric's stated normal volatility.
- **Primary next skill**: see [Next Best Skill](#next-best-skill) — the two modes hand off to each other.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md). Name the active mode (`report` / `alert`) in the Objective line.

## Data Sources

All integrations optional (see [CONNECTORS.md](../../CONNECTORS.md)). Tier 1 (keyless) works for both modes; keyed tools are opt-in Tier 2/3.

- **report**: with tools connected, aggregates traffic from ~~analytics, search data from ~~search console, rankings/backlinks from ~~SEO tool, and AI visibility from ~~AI monitor. Without tools, ask the user for analytics exports, Search Console data, ranking data, and KPIs.
- **alert**: with tools, monitor real-time feeds from ~~SEO tool, ~~search console, and ~~web crawler. Without tools, ask for baselines, critical keywords, delivery preferences, and historical data.

**Zero-dependency measurement loop** (both modes): every reported change or fired alert should come from a computed delta, not an eyeballed estimate. Store each period's KPIs and let the ledger compute movement: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/ledger.py" record <domain> --source monitor --data '{"sessions": ..., "clicks": ..., ...}'`, then `ledger.py diff <domain> --source monitor` for the period delta and `ledger.py trend <domain> --source monitor --field <kpi>` for the trend line. Label every figure Measured / User-provided / Estimated, and attribute outcome movement against a control rather than to the latest change — see [references/measurement-protocol.md](../../references/measurement-protocol.md). See [scripts/connectors/README.md](../../scripts/connectors/README.md).

## Decision Gates

**Stop and ask the user when:**
- **Mode ambiguous** — the request fits neither past-tense ("report on last month") nor future-tense ("tell me when X drops"). Offer: (1) `report` a snapshot now, (2) `alert` for ongoing monitoring, (3) both.
- **report**: no reporting period or comparison period can be determined and none is in context — offer (1) last 30 days vs prior 30, (2) last calendar month vs prior month, (3) a custom range. A period comparison is required, not optional.
- **alert**: no baseline or normal-volatility reference exists for the metrics to watch — thresholds would be arbitrary. Offer (1) supply recent baseline data, (2) use the Alert Threshold Quick Reference defaults and label them Estimated, (3) cancel.

**Continue silently (never stop for):**
- A report section's source data is missing — mark that section "Not yet evaluated" and proceed; do not fabricate the metric.
- Audience not stated (report) — default to the executive template and note the assumption.
- Delivery channel not stated (alert) — default to the channel in context (or email) and note it.
- An alert category the user did not mention — leave it unconfigured; do not add alerts they did not request.

## Instructions

**Step 0 — Select mode.** Read `--mode` if given. Otherwise infer: past-tense / "how did we do" / "月报" → `report`; future-tense / "tell me when" / "预警" → `alert`. If neither fits, use the mode-ambiguous gate above.

### Mode: report

Use [Report Output Templates](references/report-output-templates.md) and cover:

1. **Define Report Parameters** — domain, period, comparison period, report type, audience, focus areas, data freshness.
2. **Executive Summary** — overall rating, wins, watch areas, required actions, metrics-at-a-glance (traffic, rankings, conversions, DA/authority, AI citations), and SEO ROI; tag each metric Measured / User-provided / Estimated.
3. **Organic Traffic** — sessions, users, pageviews, engagement/bounce, trend, source/device split, top pages, each figure source-tagged.
4. **Keyword Rankings** — position ranges, distribution change, top improvements/declines, SERP features. For raw position-by-position deltas, defer to [rank-tracker](../rank-tracker/SKILL.md) rather than recomputing here.
5. **GEO / AI Performance** — AI citation overview, citations by topic, GEO wins, optimization opportunities.
6. **Domain Authority (CITE)** — include CITE dimension scores and veto status **when a gate has already produced them**; otherwise mark "Not yet evaluated." Do not compute CITE here.
7. **Content Quality (CORE-EEAT)** — include average scores and trends **when already produced**; otherwise mark "Not yet evaluated." Do not compute CORE-EEAT here.
8. **Backlinks** — link-profile summary, acquisition trend, notable links, competitive position.
9. **Content Performance** — publishing summary, top content, content needing attention, content ROI.
10. **Recommendations** — immediate/short-term/long-term actions with priority, owner, expected impact, next-period goals.
11. **Compile Full Report** — table of contents, appendix, data sources, methodology, glossary.

### Mode: alert

Use [Alert Configuration Templates](references/alert-configuration-templates.md) and:

1. **Define Alert Categories** — choose from rankings, traffic, technical, backlinks, competitors, GEO / AI, and brand.
2. **Configure Alert Rules by Category** — define trigger condition, threshold, alert name, and priority for each relevant rule; tie each threshold to a stated baseline and label that baseline Measured / User-provided / Estimated.
3. **Define Alert Response Plans** — map Critical / High / Medium / Low to response time and next actions.
4. **Set Up Alert Delivery** — channels, routing, cooldowns, maintenance windows, escalation paths.
5. **Create Alert Summary** — output category counts, the critical playbook, and a weekly review checklist as the deliverable.

### Shared discipline (both modes)

Label every metric **Measured** (tool/export), **User-provided**, or **Estimated** (model inference); never present an estimate as measured; if a required metric is unavailable, mark it N/A — do not invent it. Separate an **observed change** from a **plausible explanation** (corroborate before stating a cause), an **optimization opportunity**, and **follow-up** needing crawl/SERP/rank/audit — never report an unverified explanation as a confirmed cause.

## Alert Threshold Quick Reference

| Metric | Warning | Critical | Frequency |
|--------|---------|----------|-----------|
| Organic traffic | -15% WoW | -30% WoW | Daily |
| Keyword positions | >3 position drop | >5 position drop | Daily |
| Pages indexed | -5% change | -20% change | Weekly |
| Crawl errors | >10 new/day | >50 new/day | Daily |
| Core Web Vitals | "Needs Improvement" | "Poor" | Weekly |
| Backlinks lost | >5% in 1 week | >15% in 1 week | Weekly |
| AI citation loss | Any key query | >20% queries | Weekly |
| Security issues | Any detected | Any detected | Daily |

**Steep-decline trigger (always on):** if organic traffic OR aggregate keyword rank falls **>30%** below its trailing baseline (default: prior 28-day median for the same weekday band), fire a Critical alert regardless of category. Use a trailing median, not a single prior day, so one noisy data point does not trip it. Label the baseline Measured / User-provided / Estimated.

## Reading Deltas Against a Control

A reported delta or a fired alert is only evidence if it beats a control over a **fixed readback window** set before the change — a raw before/after on a confounded outcome is a story, not proof. Attach the decision protocol from [references/measurement-protocol.md §Cross-discipline decision protocol](../../references/measurement-protocol.md):

- **Readback window** — pick the window for the change type up front (content refresh 7/14/28/56 days; new content 14/28/56/90; technical fix daily ×7 then 28; AEO/GEO surfacing weekly) and do not react to noise inside it. A fired alert opens a readback window, not an instant verdict — confirm the drop holds before declaring an incident.
- **Required readback fields** — record: change · owner · baseline window · candidate window · sources · primary + secondary metric · winner · caveats · decision · next-patch · next-readback date.
- **Decision** — mark each change **Promote** (beats control on the primary metric past the bar), **Keep-testing** (trending, not yet significant), **Rollback** (loses by the same bar), or **Unproven** (everything else). Report delta-vs-control, not raw delta.

## Example

- **report**: an executive summary with overall status, metrics-at-a-glance for traffic/rankings/conversions/authority/AI citations, SEO ROI, and immediate/month/quarter actions with owners and dates.
- **alert**: a keyword alert matrix with Critical vs High thresholds, a response plan for drops, and notification routing to email + Slack.

## Save Results

Ask "Save these results?" If yes, write to `memory/monitoring/` using filename `YYYY-MM-DD-<topic>.md` — see [skill-contract.md §Save Results Template](../../references/skill-contract.md). This is a non-auditor skill: ask before writing memory and hand off veto-like risks to the relevant auditor gate rather than appending veto markers itself.

## Reference Materials

- [Report Output Templates](references/report-output-templates.md) — compact starter blocks for all 11 report sections (report mode)
- [KPI Definitions](references/kpi-definitions.md) — SEO/GEO metric definitions with benchmarks, thresholds, trend analysis, attribution guidance
- [Report Templates by Audience](references/report-templates.md) — copy-ready templates for executive, marketing, technical, and client audiences
- [Alert Configuration Templates](references/alert-configuration-templates.md) — full category tables, thresholds, response-plan templates (alert mode)
- [Alert Threshold Guide](references/alert-threshold-guide.md) — threshold setting, fatigue prevention, escalation paths, response playbooks
- [Measurement & Attribution Protocol](../../references/measurement-protocol.md) — readback windows, required fields, and the promote / keep-testing / rollback / unproven decision rule

## Next Best Skill

Mode-conditional, then terminal:

- After **report** — a change needs ongoing monitoring → run this skill in `alert` mode. A section marked "Not yet evaluated" for authority → [domain-authority-auditor](../domain-authority-auditor/SKILL.md); for content quality → [content-quality-auditor](../../optimize/content-quality-auditor/SKILL.md). One-off report with no action → Terminal.
- After **alert** — a reporting cadence is requested → run this skill in `report` mode. Standalone alert setup → Terminal.

Termination: the visited-set and `max-depth: 3` rules from [skill-contract.md §Termination rules](../../references/skill-contract.md) apply. Do not re-enter a mode already run in this chain (report→alert→report is a visited-set stop); if routing is ambiguous, present the options and stop instead of auto-following.
