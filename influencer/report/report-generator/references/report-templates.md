# Report Templates & Writing Guide

Full audience templates, visualization recommendations, writing best practices, and a worked example for [report-generator](../SKILL.md). Pick the template that matches the requested audience.

**Copy/save contract**: populate numeric conclusions only from cited `performance-analyzer` / `roi-calculator` artifacts; use `Unknown`/`NEEDS_INPUT` when an artifact, compatible comparator, or provenance field is absent. Every saved/copyable identity field uses only opaque `client_ref`, `preparer_ref`, `contact_ref`, `owner_ref`, or `creator_ref`; never save a resolved client/staff/owner/creator name, organization label, email, profile URL, provider ID, or ref-to-identity map. A creator asset or screenshot may appear only through a frozen approved `asset_ref` plus active rights covering the report audience, channel, territory, format, and duration; otherwise omit it. Do not infer causal drivers from descriptive differences.

**Transient render and distribution gate**: resolve identity refs only in memory for one explicitly declared audience render, use only fields approved for that audience, and discard the resolution afterward. The ref-only source remains the saved artifact. Before any external send/share/export, require a new exact authorization naming the exact report artifact/version, recipient audience, delivery channel, and identity/asset refs permitted for that audience. A request to generate, render, or save the report is not distribution authorization.

## Report Parameters & Audience Needs

```markdown
### Report Parameters

**Report Type**: [Post-campaign/Monthly/Quarterly/Annual]
**Campaign(s)**: [campaign name(s)]
**Period**: [dates covered]
**Audience**: [Executive/Client/Team/Board]
**Supplied Tracker Stage**: [stage or `not supplied`]

**Audience Needs**:
| Audience | Focus | Detail Level | Key Questions |
|----------|-------|--------------|---------------|
| Executive | ROI, Strategy | High-level | "Was it worth it?" |
| Client | Results, Value | Medium | "What did I get?" |
| Team | Learnings, Optimization | Detailed | "What can we improve?" |
| Board | Business Impact | Summary | "How does this grow the business?" |
```

## Executive Report Template

```markdown
# [Campaign Name] Executive Report

**Prepared for**: [Executive/Leadership]
**Date**: [Date]
**Period**: [Campaign Dates]

---

## Executive Summary

[2-3 sentences summarizing the campaign and key outcome]

**Bottom Line**: [One-line verdict - e.g., "Campaign exceeded targets, achieving 3.2x ROAS"]

### Key Results at a Glance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| ROI | [X]% | [X]% | ✅/❌ |
| Revenue | $[X] | $[X] | ✅/❌ |
| Reach | [X]M | [X]M | ✅/❌ |
| New Customers | [X] | [X] | ✅/❌ |

---

## Investment & Return

| | Amount |
|---------|--------|
| **Total Investment** | $[X] |
| **Attributed Revenue** | $[X] (`roi_artifact_ref`) |
| **Net return under declared formula** | $[X] (`roi_artifact_ref`) |
| **ROI** | **[X]% (`roi_artifact_ref`)** |

---

## Strategic Highlights

### Observed Results
1. [Comparable descriptive result + evidence ref]
2. [Comparable descriptive result + evidence ref]

### Opportunities Identified
1. [Opportunity for future]
2. [Opportunity for future]

---

## Recommendation

[1-2 sentences on recommended next steps/future investment]

---

*Detailed analysis available in appendix*
```

## Client Report Template

```markdown
# [Campaign Name] Performance Report

**Client ref**: [client_ref]
**Campaign**: [Campaign Name]
**Period**: [Dates]
**Preparer ref**: [preparer_ref]

---

## Campaign Overview

### Objectives
[What we set out to achieve]

### Strategy
[Brief summary of approach]

### Execution
- **Influencers**: [X] creators across [platforms]
- **Content**: [X] pieces created
- **Timeline**: [X] weeks

---

## Performance Summary

### Overall Results

| Metric | Goal | Delivered | Performance |
|--------|------|-----------|-------------|
| Total Reach | [X] | [X] | [+/-X%] vs. goal |
| Impressions | [X] | [X] | [+/-X%] vs. goal |
| Engagements | [X] | [X] | [+/-X%] vs. goal |
| Engagement Rate | [X]% | [X]% | [+/-X%] vs. goal |
| Link Clicks | [X] | [X] | [+/-X%] vs. goal |
| Conversions | [X] | [X] | [+/-X%] vs. goal |

### Return on Investment

| Investment | Return |
|------------|--------|
| Total Spend: $[X] (`roi_artifact_ref`) | Attributed revenue: $[X] (`roi_artifact_ref`) |
| | **ROAS: [X]:1 (`roi_artifact_ref`)** |

---

## Content Performance

### Top Performing Content

**#1: [creator_ref] - [Platform]**

[rights-cleared frozen `asset_ref`, or omit]

- Reach: [X]
- Engagement Rate: [X]%
- Observed association: [descriptive difference + evidence ref]
- Causal status: [supported by supplied design / not established]

**#2: [creator_ref] - [Platform]**

[rights-cleared frozen `asset_ref`, or omit]

- Reach: [X]
- Engagement Rate: [X]%
- Observed association: [descriptive difference + evidence ref]
- Causal status: [supported by supplied design / not established]

---

## Influencer Performance

### Partner Summary

| Creator | Platform | Reach | ER | Conversions |
|---------|----------|-------|-------|-------------|
| [creator_ref] | [platform] | [X] | [%] | [X] |
| [creator_ref] | [platform] | [X] | [%] | [X] |
| [creator_ref] | [platform] | [X] | [%] | [X] |

### Top Performers

1. **[creator_ref]**: [comparable observed result + evidence ref; causal status]
2. **[creator_ref]**: [comparable observed result + evidence ref; causal status]

---

## Audience Insights

### Who We Reached

[Demographics, interests, behaviors observed]

### Sentiment & Feedback

**Positive Themes**:
- [Theme 1]
- [Theme 2]

**Questions/Feedback**:
- [Common question]
- [Common feedback]

---

## Key Learnings

### What Worked Well

1. **[Learning 1]**: [Explanation]
2. **[Learning 2]**: [Explanation]

### Opportunities for Future

1. **[Opportunity 1]**: [Recommendation]
2. **[Opportunity 2]**: [Recommendation]

---

## Recommendations

Based on campaign results, we recommend:

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

---

## Next Steps

- [Next step 1]
- [Next step 2]
- [Proposed timeline]

---

## Appendix

- Opaque performance artifact refs approved for this report audience
- Rights-cleared frozen asset refs only (no raw content gallery by default)
- Opaque detailed-analytics refs; attach raw exports only with separate exact audience-scoped authorization

---

*Thank you for your partnership. Questions: [contact_ref]*
```

## Internal Team Report Template

```markdown
# [Campaign] Internal Performance Report

**Date**: [Date]
**Preparer ref**: [preparer_ref]
**Distribution audience**: [Team/Board role scope only; no personal or organization name]

---

## TL;DR

[3-5 bullet points summarizing key outcomes and learnings]

---

## Campaign Overview

### Objectives & KPIs

| Objective | KPI | Target | Result | Status |
|-----------|-----|--------|--------|--------|
| [Objective 1] | [KPI] | [Target] | [Result] | ✅/❌ |
| [Objective 2] | [KPI] | [Target] | [Result] | ✅/❌ |

### Campaign Details

- **Duration**: [X] weeks ([dates])
- **Budget**: $[X]
- **Influencers**: [X] total ([breakdown by tier])
- **Platforms**: [platforms]
- **Content pieces**: [X]

---

## Detailed Performance Analysis

### Overall Metrics

| Metric | Result | Target | vs. Target | vs. Benchmark |
|--------|--------|--------|------------|---------------|
| Reach | [X] | [X] | [+/-X%] | [+/-X%] |
| Impressions | [X] | [X] | [+/-X%] | [+/-X%] |
| Engagements | [X] | [X] | [+/-X%] | [+/-X%] |
| ER | [X]% | [X]% | [+/-X%] | [+/-X%] |
| Video Views | [X] | [X] | [+/-X%] | [+/-X%] |
| Clicks | [X] | [X] | [+/-X%] | [+/-X%] |
| Conversions | [X] | [X] | [+/-X%] | [+/-X%] |
| Revenue | $[X] | $[X] | [+/-X%] | N/A |
| ROAS | [X]:1 | [X]:1 | [+/-X%] | [+/-X%] |

### Platform Breakdown

[Detailed platform-by-platform analysis]

### Influencer Analysis

#### Full Roster Performance

| Rank/status | Creator ref | Platform | Fee | Reach | ER | Conversions | ROAS artifact | Retro decision |
|-------------|-------------|----------|-----|-------|----|-------------|---------------|----------------|
| [1/NOT_RANKED] | [creator_ref] | [platform] | $[X] | [X] | [%] | [X] | [value + roi_ref] | [renew/retest/retire/unknown; default unknown] |
| [2/NOT_RANKED] | [creator_ref] | [platform] | $[X] | [X] | [%] | [X] | [value + roi_ref] | [renew/retest/retire/unknown; default unknown] |

#### Performance Insights

**Higher observed comparable rows**: [descriptive result + evidence; cause not established unless separately supported]
**Lower observed comparable rows**: [descriptive result + evidence; cause not established unless separately supported]
**Surprises**: [Any unexpected results]

### Content Analysis

#### By Format

| Format | Pieces | Avg Reach | Avg ER | Best Performer |
|--------|--------|-----------|--------|----------------|
| [Format 1] | [#] | [X] | [%] | [creator_ref] |
| [Format 2] | [#] | [X] | [%] | [creator_ref] |

#### By Theme

| Theme | Pieces | Avg ER | Conversions |
|-------|--------|--------|-------------|
| [Theme 1] | [#] | [%] | [X] |
| [Theme 2] | [#] | [%] | [X] |

#### Content Learnings

- [Learning about what content worked]
- [Learning about messaging]
- [Learning about creative approach]

---

## Cost Analysis

### Budget vs. Actual

| Category | Budgeted | Actual | Variance |
|----------|----------|--------|----------|
| Influencer fees | $[X] | $[X] | [+/-$X] |
| Product/Gifting | $[X] | $[X] | [+/-$X] |
| Production | $[X] | $[X] | [+/-$X] |
| Amplification | $[X] | $[X] | [+/-$X] |
| **Total** | **$[X]** | **$[X]** | **[+/-$X]** |

### Efficiency Metrics

| Metric | Result | Target + source/date | External comparator + source/date | Compatibility |
|--------|--------|----------------------|-----------------------------------|---------------|
| CPM | $[X] | $[X] ([source/date]) | $[X] or Unknown ([source/date]) | [compatible/pending] |
| CPE | $[X] | $[X] ([source/date]) | $[X] or Unknown ([source/date]) | [compatible/pending] |
| CPC | $[X] | $[X] ([source/date]) | $[X] or Unknown ([source/date]) | [compatible/pending] |
| CPA | $[X] | $[X] ([source/date]) | $[X] or Unknown ([source/date]) | [compatible/pending] |

---

## Learnings & Recommendations

### Key Learnings

| Learning | Evidence | Implication |
|----------|----------|-------------|
| [Learning 1] | [Data/example] | [What to do with this] |
| [Learning 2] | [Data/example] | [What to do with this] |
| [Learning 3] | [Data/example] | [What to do with this] |

### Higher Observed Results (Retest or Act per Rule)

1. [Tactic/approach]: [observed association + evidence; causal status]
2. [Tactic/approach]: [observed association + evidence; causal status]

### Lower Observed Results (Retest or Stop per Rule)

1. [Tactic/approach]: [observed association + evidence; causal status]
2. [Tactic/approach]: [observed association + evidence; causal status]

### Recommendations for Future Campaigns

| Area | Current Approach | Recommended Change | Expected Impact |
|------|------------------|-------------------|-----------------|
| [Area 1] | [Current] | [Recommended bounded test/action] | [model-backed estimate or Unknown] |
| [Area 2] | [Current] | [Recommended bounded test/action] | [model-backed estimate or Unknown] |

---

## Action Items

| Action | Owner ref | Deadline | Status |
|--------|-----------|----------|--------|
| [Action 1] | [owner_ref] | [Date] | ⬜ |
| [Action 2] | [owner_ref] | [Date] | ⬜ |
| [Action 3] | [owner_ref] | [Date] | ⬜ |

---

## Appendix

- Opaque raw-export refs; do not embed exports by default
- Rights-cleared frozen creator-asset refs; do not embed all screenshots by default
- Opaque contract-summary refs; do not disclose full contracts by default
- Opaque sentiment-analysis artifact refs with approved audience scope

---
```

## Campaign Retro Card — Measured/Closed Only

Place this compact WARM card alongside the report only when a current non-forked tracker-state artifact proves `measured` or `closed`. Preserve the exact card from `performance-analyzer`; this skill never derives or changes its decision. If the card is missing, stale, forked, or scope-mismatched, emit `decision: unknown`, list the blocker, and request the bound performance-analyzer artifact. Keep it outside a client/board-facing copy unless the user explicitly asks to include it.

```markdown
### Campaign Retro Card

- `campaign_id`: [exact campaign ID]
- `creator_ref`: [exact opaque creator ref]
- `tracker_state_ref`: [current non-forked state artifact/receipt ref proving measured or closed]
- `measurement_contract_ref`: [current locked contract ref]
- `decision_rule_ref`: [precommitted rule ref]
- `decision`: `renew | retest | retire | unknown`
- `evidence_backed_rationale`: [decision rule + observed result; cite, do not infer]
- `evidence_refs`: [[dated source/artifact reference], ...]
- `next_campaign_hypothesis`: [one falsifiable change to test next, or `none`]
- `unresolved_limitations`: [[missing source/window/attribution/comparability issue], ...]
```

Copy `renew | retest | retire` only from the exact bound performance-analyzer card; otherwise use `unknown`. The decision is qualitative WARM working state—not a STAR/SQS or creator-content-auditor verdict, and not a creator-registry fact.

After exact authorization saves the report/card, offer a separate `campaign-planner` handoff to append the artifact reference to the relevant tracker row's `evidence_refs`; do not edit the tracker or advance its stage here. An optional next-cycle `fit-scorer` handoff passes the cited evidence and hypothesis only after the user chooses it; it does not inherit or simulate a STAR/SQS verdict.

## Visualization Recommendations

```markdown
## Recommended Visualizations

### For Executive Reports

| Data | Visualization | Why |
|------|---------------|-----|
| ROI/ROAS | Large number callout | Immediate impact |
| Goal vs. Actual | Horizontal bar chart | Easy comparison |
| Budget allocation | Pie/donut chart | Distribution clarity |
| Timeline performance | Line chart | Show momentum |

### For Client Reports

| Data | Visualization | Why |
|------|---------------|-----|
| Overall results | Dashboard-style metrics | Professional look |
| Content examples | Rights-cleared frozen asset refs with metrics | Tangible deliverables without unapproved reuse |
| Influencer performance | Table with icons | Detailed but scannable |
| Engagement breakdown | Stacked bar | Show composition |

### For Team Reports

| Data | Visualization | Why |
|------|---------------|-----|
| Full metrics | Detailed tables | Complete data |
| Trends | Line charts over time | Pattern recognition |
| Comparisons | Side-by-side bars | Easy comparison |
| Distribution | Histograms | Understand spread |
```

## Report Writing Best Practices

```markdown
## Report Writing Guidelines

### Structure Principles

1. **Lead with outcomes**: Start with results, not methodology
2. **Answer "so what?"**: Every metric needs context
3. **Use progressive disclosure**: Summary -> Details -> Appendix
4. **Balance positive and constructive**: Celebrate wins, acknowledge learnings

### Writing Tips

**Instead of**: "We achieved [reach]"
**Write when result and target are supplied**: "The supplied reach result was [reach], [calculated delta] versus the supplied target. Platform or audience drivers are `NEEDS_INPUT` unless a comparable segmented breakdown was supplied."

**Instead of**: "Engagement rate was [rate]"
**Write when a source-dated comparator is supplied**: "The supplied engagement rate was [rate] versus [comparator]. This is a descriptive comparison; it does not by itself establish why engagement differed or prove audience resonance."

### Narrative Arc

1. **Setup**: What we set out to do
2. **Execution**: What we did
3. **Results**: What happened
4. **Analysis**: What it means
5. **Recommendations**: What to do next
```

## Tips for Better Reports

1. **Know your audience** — Executive wants ROI, team wants details
2. **Lead with the headline** — Don't bury the lede
3. **Visualize key data** — Charts > tables for executives
4. **Provide context** — Benchmarks make numbers meaningful
5. **End with action** — Reports should drive decisions

## Worked Example — Executive Report

**User**: "Create an executive report for Holiday Campaign 2024. `roi-ref-01` already contains $50K spend, $165K attributed revenue, $115K net return under its declared formula, 230% arithmetic ROI, and 3.3:1 ROAS. `performance-ref-01` contains 3.5M reach across 15 opaque creator refs and the target deltas. Targets were $100K attributed revenue, 2:1 ROAS, and 2M reach. No segmented breakdown, incrementality study, or reallocation rule is included."

**Output**:

```markdown
# Holiday Campaign 2024: Executive Summary

## Bottom Line: Campaign Exceeded the Supplied Targets ✅

**ROI: 230% (`roi-ref-01`)** | **ROAS: 3.3:1 (`roi-ref-01`)** | **Attributed Revenue: $165,000**

**Evidence basis**: financial values and calculation status come from `roi-ref-01`; reach and target deltas come from `performance-ref-01`. This report performs no metric recomputation. Attributed revenue is not relabeled as incremental revenue.

### Investment & Return

| | |
|---|---|
| Investment | $50,000 |
| Attributed revenue | $165,000 |
| **Net return under declared formula (`roi-ref-01`)** | **$115,000** |

### Key Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Attributed revenue | $100K | $165K | ✅ +65% |
| ROAS | 2:1 | 3.3:1 | ✅ +65% |
| Reach | 2M | 3.5M | ✅ +75% |

### Strategic Takeaways

1. **Attributed revenue cleared the supplied target** — $165K versus $100K; this does not establish incremental lift.
2. **Reach cleared the supplied target** — 3.5M versus 2M.
3. **Platform, creator-tier, and format drivers** — `NEEDS_INPUT`; no segmented evidence was supplied.

### Recommendation

Do not change the next budget or mix from this aggregate report alone. Request comparable platform, creator-tier, and content-format results plus the campaign owner's precommitted decision rule; treat any proposed reallocation as a hypothesis until that evidence is available.

---
*Full analysis available upon request*
```
