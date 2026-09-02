# Performance Analyzer — Analysis Templates

Fill-in templates for each step of the influencer performance analysis. Each maps to a numbered step in [../SKILL.md](../SKILL.md) Instructions.

Repo-root links from this file use `../../../`.

- [skill-contract.md](../../../../references/skill-contract.md)
- [state-model.md](../../../../references/state-model.md)
- [CONNECTORS.md](../../../../CONNECTORS.md)

---

## Step 1 — Gather Performance Data

```markdown
### Performance Data Collection

**Campaign**: [name]
**Period**: [start] - [end]
**Influencers**: [count]
**Platforms**: [platforms]

### Data Sources

| Source | Metrics Available | Collection Method |
|--------|-------------------|-------------------|
| Native analytics | Reach, views, engagement | Platform export |
| Influencer reports | Screenshots/exports | From creators |
| Website analytics | Traffic, conversions | GA/tracking |
| Sales data | Revenue, orders | E-commerce platform |
| Promo code data | Redemptions | Sales system |
```

---

## Step 2 — Analyze Core Metrics

```markdown
## Campaign Performance Overview

### Summary Metrics

`Conversions` and `Revenue` below must reference the reconciled counted total from Step 7 under one deduplicated attribution model; until Step 7 passes, both are `Unknown/NEEDS_INPUT`. State whether reach is platform-reported (potentially overlapping) or deduplicated person-level reach. Recompute aggregate ER, CVR, CPA, and other rates from compatible summed numerators/denominators—never sum or simple-average row rates.

| Metric | Result | Target | vs. Target | vs. Benchmark |
|--------|--------|--------|------------|---------------|
| Total Reach | [X] | [X] | [+/-X%] | [+/-X%] |
| Total Impressions | [X] | [X] | [+/-X%] | [+/-X%] |
| Total Engagements | [X] | [X] | [+/-X%] | [+/-X%] |
| Engagement Rate | [X%] | [X%] | [+/-X%] | [+/-X%] |
| Total Video Views | [X] | [X] | [+/-X%] | [+/-X%] |
| Link Clicks | [X] | [X] | [+/-X%] | [+/-X%] |
| Promo Code Uses | [X] | [X] | [+/-X%] | N/A |
| Conversions | [X] | [X] | [+/-X%] | [+/-X%] |
| Revenue | $[X] | $[X] | [+/-X%] | N/A |

### Comparison Status

**Status**: [ABOVE_TARGET / AT_TARGET / BELOW_TARGET / MIXED / UNKNOWN / NOT_COMPARABLE]

Derive this only from the declared metric/target rule and compatible rows above. If a target, source date, window, attribution basis, or better-direction rule is missing, use `UNKNOWN` or `NOT_COMPARABLE`. Do not invent an aggregate `/10` score or adjective verdict.

### Key Highlights

✅ **What Exceeded Expectations**:
- [Highlight 1]
- [Highlight 2]

⚠️ **What Underperformed**:
- [Issue 1]
- [Issue 2]
```

---

## Step 3 — Analyze by Platform

```markdown
## Platform Performance

### Platform Comparison

| Platform | Reach | Engagements | ER | Clicks | Conversions | CPA |
|----------|-------|-------------|-------|--------|-------------|-----|
| Instagram | [X] | [X] | [%] | [X] | [X] | $[X] |
| TikTok | [X] | [X] | [%] | [X] | [X] | $[X] |
| YouTube | [X] | [X] | [%] | [X] | [X] | $[X] |
| **Total** | **[X]** | **[X]** | **[%]** | **[X]** | **[X]** | **$[X]** |

### Platform Insights

**Observed highest platform under the declared comparable metric**: [Platform / NOT_RANKED]
- Evidence: [metric, window, attribution basis, source_ref]
- Possible explanation: [explicit hypothesis or `not tested`]

**Observed lowest platform under the declared comparable metric**: [Platform / NOT_RANKED]
- Evidence: [metric, window, attribution basis, source_ref]
- Possible explanation: [explicit hypothesis or `not tested`]
- Improvement opportunity: [suggestion]

### Platform-Specific Metrics

#### Instagram

| Metric | Feed Posts | Reels | Stories |
|--------|------------|-------|---------|
| Reach | [X] | [X] | [X] |
| Engagements | [X] | [X] | [X] |
| ER | [%] | [%] | [%] |
| Saves | [X] | [X] | N/A |
| Shares | [X] | [X] | [X] |

#### TikTok

| Metric | Result | Benchmark |
|--------|--------|-----------|
| Views | [X] | |
| Likes | [X] | |
| Comments | [X] | |
| Shares | [X] | |
| Average Watch Time | [X]s | |
| Completion Rate | [%] | |
```

---

## Step 4 — Analyze by Influencer

```markdown
## Influencer Performance

### Creator Comparison

**Declared ranking metric/rule**: [metric, better direction, window, attribution basis, complete creator scope, decision/significance rule or missing]

| Rank/status | Creator ref | Reach | ER | Conversions | ROAS artifact value/ref | Comparability |
|-------------|-------------|-------|----|-------------|-------------------------|---------------|
| [1 / NOT_RANKED] | creator-<UUIDv4> | [X] | [%] | [X] | [X]:1 / [roi_ref] | [comparable/gap] |
| [2 / NOT_RANKED] | creator-<UUIDv4> | [X] | [%] | [X] | [X]:1 / [roi_ref] | [comparable/gap] |
| [3 / NOT_RANKED] | creator-<UUIDv4> | [X] | [%] | [X] | [X]:1 / [roi_ref] | [comparable/gap] |

### Highest Observed Comparable Row

#### [creator_ref / NOT_RANKED]

| Metric | Result | vs. Campaign Avg |
|--------|--------|------------------|
| Reach | [X] | [+/-X%] |
| Engagement Rate | [%] | [+/-X%] |
| Video Completion | [%] | [+/-X%] |
| Click-through Rate | [%] | [+/-X%] |
| Conversion Rate | [%] | [+/-X%] |
| Cost per Conversion | $[X] | [+/-X%] |

**Observed differences**:
- [dated metric difference + evidence ref]
- [dated metric difference + evidence ref]

**Causal explanation**: [supported by supplied experimental/quasi-experimental evidence, or `not established`]
**Hypothesis for next test**: [one falsifiable hypothesis or none]

**Content Analysis**:
- Format: [what they posted]
- Hook: [how they opened]
- Message: [how they communicated]
- CTA: [what they asked viewers to do]

**Retro decision**: [renew/retest/retire/unknown under the preregistered rule; default unknown]

### Lower Observed Comparable Row

#### [creator_ref / NOT_RANKED]

**Results**: [summary]
**Observed difference**: [dated metric + evidence ref]
**Causal explanation**: [supported evidence or `not established`]
**Learning**: [what to do differently]
```

---

## Step 5 — Content Performance Analysis

```markdown
## Content Performance

### Top Performing Content

| Rank/status | Creator ref | Platform | Format | Reach | ER | Observed feature |
|-------------|-------------|----------|--------|-------|----|------------------|
| [1/NOT_RANKED] | creator-<UUIDv4> | [platform] | [format] | [X] | [%] | [visible feature + source_ref] |
| [2/NOT_RANKED] | creator-<UUIDv4> | [platform] | [format] | [X] | [%] | [visible feature + source_ref] |
| [3/NOT_RANKED] | creator-<UUIDv4> | [platform] | [format] | [X] | [%] | [visible feature + source_ref] |

### Content Format Analysis

| Format | Pieces | Avg Reach | Avg ER | Best Performer |
|--------|--------|-----------|--------|----------------|
| Video (Reels/TikTok) | [#] | [X] | [%] | [creator_ref] |
| Static Images | [#] | [X] | [%] | [creator_ref] |
| Carousels | [#] | [X] | [%] | [creator_ref] |
| Stories | [#] | [X] | [%] | [creator_ref] |
| YouTube Videos | [#] | [X] | [%] | [creator_ref] |

### Content Theme Analysis

| Theme | Pieces | Avg ER | Conversion Rate | Notes |
|-------|--------|--------|-----------------|-------|
| Product demo | [#] | [%] | [%] | [notes] |
| Lifestyle | [#] | [%] | [%] | [notes] |
| Tutorial | [#] | [%] | [%] | [notes] |
| Review | [#] | [%] | [%] | [notes] |
| Unboxing | [#] | [%] | [%] | [notes] |

### Observed Content Associations

**Hook patterns associated with the observed result**:
- [Pattern 1]: [examples + comparable metric/evidence]
- [Pattern 2]: [examples + comparable metric/evidence]

**Messaging associations**:
- [Message type 1]: [observed result; causality not established / supplied causal evidence]
- [Message type 2]: [observed result; causality not established / supplied causal evidence]

**Visual Elements That Performed**:
- [Element 1]
- [Element 2]
```

---

## Step 6 — Engagement Quality Analysis

```markdown
## Engagement Quality

### Engagement Breakdown

| Type | Volume | % of declared sample | Quality state | Rubric/evidence ref |
|------|--------|----------------------|---------------|---------------------|
| Likes | [X] | [%] | [typed state or Unknown] | [ref] |
| Comments | [X] | [%] | [typed state or Unknown] | [ref] |
| Saves | [X] | [%] | [typed state or Unknown] | [ref] |
| Shares | [X] | [%] | [typed state or Unknown] | [ref] |
| Link clicks | [X] | [%] | [typed state or Unknown] | [ref] |

### Comment Sentiment Analysis

**Sampling/coding contract**: [platform/content scope, start/end, sampled and eligible counts, sampling method, coding rubric/model/version, denominator, source/evidence refs]. Without this contract, sentiment percentages and intent labels are `Unknown/NOT_SCORED`.

| Sentiment | % | Examples |
|-----------|---|----------|
| Positive | [%] | "[example]", "[example]" |
| Neutral/Questions | [%] | "[example]", "[example]" |
| Negative | [%] | "[example]", "[example]" |

**Key Themes in Comments**:
- [Theme 1]: [frequency] mentions
- [Theme 2]: [frequency] mentions
- [Theme 3]: [frequency] mentions

### Purchase Intent Signals

| Signal | Count | Examples |
|--------|-------|----------|
| "Where to buy" questions | [#] | |
| Price questions | [#] | |
| Code requests | [#] | |
| "Just ordered" | [#] | |
| Tagged friends | [#] | |

### Engagement Quality Read

**Status**: [SUPPORTED / MIXED / UNKNOWN / NOT_SCORED]
**Rubric/calculation ref**: [supplied rubric + inputs + formula, or none]

Do not emit a `/10` score unless the user supplies the rubric, required inputs, and calculation. Missing comment/source evidence is `UNKNOWN`/`NOT_SCORED`, not an estimated score.
```

---

## Step 7 — Conversion & Attribution Analysis

```markdown
## Conversion Analysis

### Conversion Funnel

```
Reach        [bar from supplied data] [reach]        ([share])
                  ↓
Engagements  [bar from supplied data] [engagements]  ([rate])
                  ↓
Link Clicks  [bar from supplied data] [clicks]       ([rate])
                  ↓
Site Visits  [bar from supplied data] [visits]       ([rate])
                  ↓
Add to Cart  [bar from supplied data] [adds]         ([rate])
                  ↓
Purchases    [bar from supplied data] [purchases]    ([rate])
```

Use `Unknown` for any stage not supplied or observed. Do not infer missing counts from the shape of the illustrative bars.

### Conversion Metrics

| Metric | Result | Benchmark + source/date | Status |
|--------|--------|-------------------------|--------|
| Click-through Rate | [%] | [%] ([source/date]) | [above/below/equal/pending] |
| Landing Page CVR | [%] | [%] ([source/date]) | [above/below/equal/pending] |
| Overall CVR | [%] | [%] ([source/date]) | [above/below/equal/pending] |
| Cost per Click | $[X] | $[X] ([source/date]) | [above/below/equal/pending] |
| Cost per Conversion | $[X] | $[X] ([source/date]) | [above/below/equal/pending] |

### Deduplicated Attribution

**Declared model/window**: [model + dates]
**Deduplication key/rule**: [order/event/customer key + precedence rule]

| Mutually exclusive counted bucket | Conversions | Attributed revenue | % of counted total | Evidence refs |
|-------------------------------------|-------------|--------------------|--------------------|---------------|
| Promo-only after reconciliation | [X] | $[X] | [%] | [refs] |
| UTM-only after reconciliation | [X] | $[X] | [%] | [refs] |
| Other direct bucket under model | [X] | $[X] | [%] | [refs] |

| Non-additive evidence | Value | Status |
|-----------------------|-------|--------|
| Overlapping promo + UTM/direct observations | [X] | [reconciled/unresolved] |
| Estimated influence | [X] | Estimated; excluded from counted total and percentages |

The mutually exclusive counted buckets must sum exactly to the declared counted total. Never add overlapping promo, UTM, and direct observations; unresolved overlaps return `NEEDS_INPUT` for the attribution total.

### Promo Code Performance

| Code ref | Creator ref | Uses | Attributed revenue | AOV |
|----------|-------------|------|--------------------|-----|
| [opaque code_ref] | [creator_ref] | [X] | $[X] | $[X] |
| [opaque code_ref] | [creator_ref] | [X] | $[X] | $[X] |
| [opaque code_ref] | [creator_ref] | [X] | $[X] | $[X] |
```

---

## Step 8 — Generate Insights & Recommendations

```markdown
## Insights & Recommendations

### Top 5 Learnings

1. **[Learning 1]**
   - What we observed: [data]
   - Why it matters: [significance]
   - Future application: [how to use this]

2. **[Learning 2]**
   - What we observed: [data]
   - Why it matters: [significance]
   - Future application: [how to use this]

[Continue for top 5]

### Observed Higher Results

| Element | Performance | Recommendation |
|---------|-------------|----------------|
| [Element 1] | [comparable metric + evidence] | [bounded retest or rule-backed action] |
| [Element 2] | [comparable metric + evidence] | [bounded retest or rule-backed action] |

### Observed Lower Results

| Element | Performance | Recommendation |
|---------|-------------|----------------|
| [Element 1] | [comparable metric + evidence] | [bounded retest or stop-rule action] |
| [Element 2] | [comparable metric + evidence] | [bounded retest or stop-rule action] |

### Optimization Opportunities

| Opportunity | Impact hypothesis | Evidence/model ref | Effort | Priority rule |
|-------------|-------------------|--------------------|--------|---------------|
| [Opportunity 1] | [testable hypothesis] | [ref or Unknown] | [effort] | [declared rule] |
| [Opportunity 2] | [testable hypothesis] | [ref or Unknown] | [effort] | [declared rule] |

### Influencer Roster Recommendations

| Creator ref | Next-cycle decision | Evidence-backed rationale |
|-------------|---------------------|---------------------------|
| [creator_ref] | `renew` | [decision rule cleared + evidence ref] |
| [creator_ref] | `retest` | [mixed/inconclusive evidence + testable change] |
| [creator_ref] | `retire` | [declared stop rule or hard constraint + evidence ref] |
| [creator_ref] | `unknown` | [missing/unaligned evidence] |

### Future Campaign Recommendations

1. **Platform Mix**: [recommendation]
2. **Influencer Tier**: [recommendation]
3. **Content Format**: [recommendation]
4. **Messaging**: [recommendation]
5. **Budget Allocation**: [recommendation]

### Campaign Retro Card — only with verified current tracker state `measured` or `closed`

Repeat this compact card for each creator decision requested. Do not inherit scope implicitly or trust a bare stage string: cite the current non-forked tracker-state evidence, measurement contract, and decision rule.

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

The card is WARM working state, not a STAR/SQS or creator-content-auditor verdict. A missing/mismatched/forked scope or state ref blocks the card; missing comparison/decision evidence forces `unknown`. After the analysis/card is saved with exact authorization, offer a separate handoff to `campaign-planner` to append that artifact reference to the relevant tracker row's `evidence_refs`; do not update the tracker or advance its stage from this skill. An optional next-cycle `fit-scorer` handoff passes only cited evidence and the hypothesis, requires an explicit user choice, and never carries a simulated STAR/SQS verdict.

---

## Worked Example (full)

**User**: "Analyze our summer skincare campaign using this supplied dated export: total reach 2.4M (target 2M) and engagement rate 4.2% (target 3.5%). Attribution artifact `attr-reconciliation-ref-01` covers the complete conversion universe, uses unique `order_id`, the predeclared last-non-direct model/window, and reports a reconciled counted total of 1,847 conversions and $142,500 attributed revenue (targets: 2,000 and $150,000). ROI-calculator artifact `roi-ref-01` reports campaign ROAS 2.8:1 (target 3:1) and creator-ref-01 ROAS 4.2:1 under that same counted universe/cost window. The supplied creator rows say creator-ref-01 has the highest conversion count, creator-ref-02 has the highest ER at 6.8%, and creator-ref-03 has the highest reach per dollar. No matched platform comparison, significance result, complete roster decision rule, or other evidence refs were supplied."

**Output**:

```markdown
# Summer Skincare Campaign Performance Analysis

## Executive Summary

**Campaign Performance**: Mixed against the supplied targets

**Provenance**: reach/engagement results and targets are user-provided from the stated export; conversions/revenue cite `attr-reconciliation-ref-01`; ROAS cites `roi-ref-01`; status deltas are Calculated. This analysis does not promote them to independently verified, causal, or incremental results.

| Metric | Result | Target | Status | Evidence ref |
|--------|--------|--------|--------|--------------|
| Total Reach | 2.4M | 2M | ✅ +20% | supplied export |
| Engagement Rate | 4.2% | 3.5% | ✅ +20% | supplied export |
| Conversions | 1,847 | 2,000 | ⚠️ -7.7% | attr-reconciliation-ref-01 |
| Revenue | $142,500 | $150,000 | ⚠️ -5% | attr-reconciliation-ref-01 |
| ROAS | 2.8:1 | 3:1 | ⚠️ -6.7% | roi-ref-01 |

## Supplied Creator Highlights

1. **creator-ref-01** — ROAS 4.2:1 from `roi-ref-01`; supplied highest conversion count under `attr-reconciliation-ref-01`
2. **creator-ref-02** — supplied highest engagement rate, 6.8%
3. **creator-ref-03** — supplied highest reach per dollar

## Key Learning

**Platform comparison**: `NEEDS_INPUT` — no matched TikTok/Instagram result, comparable attribution basis, or significance test was supplied. A possible platform-mix explanation may be recorded only as a hypothesis for a future test, not as an observed cause.

## Recommendation

Do not renew, replace, or reallocate from this input alone. Request the full creator/platform breakdown, comparable windows and attribution definitions, evidence refs, and the precommitted decision rule; until then, the creator decision is `unknown` and any next-cycle change is an explicitly labeled hypothesis.
```
