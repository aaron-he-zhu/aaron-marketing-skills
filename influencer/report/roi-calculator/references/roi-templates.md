# ROI Calculator — Templates & Benchmark Inputs

Fill-in templates for each methodology in [../SKILL.md](../SKILL.md) Instructions, plus the worked example and benchmark-evidence contract. Each block maps to a numbered step.

**Identity, scope, and division guard**: saved/copyable rows use only the exact `campaign_id`, complete locked `creator_ref` scope, and opaque evidence refs. Raw handles, names, URLs, emails, and provider IDs are transient only. Before any ratio, verify numerator/denominator windows and units match and the denominator is numeric and `> 0`; otherwise output `undefined`/`NEEDS_INPUT`. Never simple-average creator/tier ratios or add overlapping attribution, EMV, or LTV scenarios.

## Step 1 — ROI Calculation Inputs

```markdown
### ROI Calculation Inputs

**Campaign Details**:
- Campaign: [name]
- Duration: [dates]
- Objective: [awareness/consideration/conversion]
- Attribution method/window: [method + dates or Unknown]
- Results source/status: [source_ref + observed_at + Measured/User-provided/Estimated]
- Cost-basis completeness: [complete/incomplete/unknown + included/excluded categories]

**Investment (Total Spend)**:
| Category | Amount |
|----------|--------|
| Influencer fees | $[X] |
| Product/Gifting | $[X] |
| Production costs | $[X] |
| Paid amplification | $[X] |
| Agency/Tools | $[X] |
| **Total Investment** | **$[X]** |

**Results Data**:
| Metric | Value |
|--------|-------|
| Total Reach | [X] |
| Total Impressions | [X] |
| Total Engagements | [X] |
| Video Views | [X] |
| Link Clicks | [X] |
| Conversions/Sales | [X] |
| Revenue | $[X] |
| New Customers | [X] |
```

## Step 2 — Direct ROI Calculation

```markdown
## Direct ROI Calculation

### Simple ROI

**Formula**: (Revenue - Investment) / Investment × 100

```
Revenue used in calculation: $[X] ([source/status/window])
Investment used in calculation: $[X] ([cost basis/source])
Net return under declared formula: $[X]

ROI = ($[Revenue] - $[Investment]) / $[Investment] × 100
ROI = [X]%
```

### Return on Ad Spend (ROAS)

**Formula**: Revenue / Investment

```
ROAS = $[Revenue] / $[Investment]
ROAS = [X]:1

Interpretation: On the declared attribution and cost basis, supplied revenue equals $[X] per $1 of supplied spend; this is not an incremental-revenue claim
```

### Direct ROI Summary

| Metric | Value | Declared target (source/date) | Comparison |
|--------|-------|-------------------------------|------------|
| ROI % | [X]% | [X]% ([source], [date]) | [above/below/equal/pending] |
| ROAS | [X]:1 | [X]:1 ([source], [date]) | [above/below/equal/pending] |
| Net return under declared formula | $[X] | Not applicable | Descriptive |

**Assessment**: [positive/zero/negative arithmetic return on the declared basis] · **Verification**: [verified/results-unverified]
```

## Step 3 — Earned Media Value (EMV)

```markdown
## Earned Media Value Calculation

### EMV Methodology

EMV estimates the equivalent paid media cost to achieve the same results.

### Impression-Based EMV

**Formula**: Impressions × declared comparable CPM / 1000

| Platform | Impressions | CPM | EMV |
|----------|-------------|-----|-----|
| Instagram | [X] | $[X] | $[X] |
| TikTok | [X] | $[X] | $[X] |
| YouTube | [X] | $[X] | $[X] |
| **Total** | **[X]** | - | **$[X]** |

### Engagement-Based EMV

**Formula**: Engagements × Cost per Engagement

| Engagement Type | Volume | CPE | EMV |
|-----------------|--------|-----|-----|
| Likes | [X] | $[X] | $[X] |
| Comments | [X] | $[X] | $[X] |
| Shares | [X] | $[X] | $[X] |
| Saves | [X] | $[X] | $[X] |
| Video Views | [X] | $[X] | $[X] |
| **Total** | - | - | **$[X]** |

### EMV Method Selection

| Method | Value | Comparator source/date | Applicability |
|--------|-------|------------------------|---------------|
| Impression EMV | $[X] or NEEDS_INPUT | [source/date or missing] | [applicable/not applicable/unknown] |
| Engagement EMV | $[X] or NEEDS_INPUT | [source/date or missing] | [applicable/not applicable/unknown] |
| **Declared valuation result** | **$[X] or NEEDS_INPUT** | [predeclared method/weighting rule] | [why this rule avoids overlap] |

Report the methods separately unless a supplied predeclared rule specifies how to select or weight them and explains why the inputs do not double-count the same exposure. Never average or add impression- and engagement-based EMV by default. If no compatible source-dated CPM/CPE exists, return `NEEDS_INPUT` instead of inventing one.

### EMV ROI

```
Calculated EMV scenario: $[X]
Investment:    $[X]
EMV Multiple:  [X]x

Under the declared comparator assumptions, the scenario equals $[X] in equivalent media value per $1 spent; it is not observed revenue
```

### EMV Caveats

⚠️ **Note**: EMV is an Estimated scenario and varies by methodology. Use only with explicitly supplied or cited inputs, label all assumptions, and do not present it as observed or causal return.
```

## Step 4 — Cost Efficiency Analysis

```markdown
## Cost Efficiency Analysis

### Cost Per Metrics

| Metric | Formula | Result | Declared target (source/date) | Comparison |
|--------|---------|--------|-------------------------------|------------|
| CPM | Spend ÷ (Impressions/1000) | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| CPR (Reach) | Spend ÷ (Reach/1000) | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| CPE | Spend ÷ Engagements | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| CPV (Video) | Spend ÷ Views | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| CPC | Spend ÷ Clicks | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| CPA | Spend ÷ Acquisitions | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| CAC | Total Spend ÷ New Customers | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |

### Comparison Contract

| Field | Required value |
|-------|----------------|
| Target metric and rule | [metric, threshold/range, better direction] |
| Source | [publisher or first-party cohort query] |
| Publication/retrieval date | [YYYY-MM-DD] |
| Market and comparison cohort | [market, industry, audience, platform] |
| Observation window | [dates and lag] |
| Attribution basis | [model and conversion definition] |
| Cost and currency basis | [included costs, currency, FX date] |
| Compatibility notes | [material differences or none] |

**Comparison result**: [above/below/equal/pending]. Use `pending` when the target is absent, stale, or materially incompatible.

### vs. Other Channels

Normalize currency, included costs, observation window, and attribution before comparing channels.

| Channel | CPA | Source/date | Comparable basis? | vs. Influencer |
|---------|-----|-------------|-------------------|----------------|
| Influencer Marketing | $[X] | [source/date] | Baseline | - |
| Paid Social | $[X] | [source/date] | [yes/no] | [+/-X% or pending] |
| Paid Search | $[X] | [source/date] | [yes/no] | [+/-X% or pending] |
| Display Ads | $[X] | [source/date] | [yes/no] | [+/-X% or pending] |
| Email Marketing | $[X] | [source/date] | [yes/no] | [+/-X% or pending] |
```

## Step 5 — Attribution Analysis

```markdown
## Attribution Analysis

### Attribution Lock

| Required lock | Value |
|---------------|-------|
| Deduplicated conversion universe | [count + exact source/window] |
| Order/event/customer dedupe key | [key + collision/refund rule] |
| Complete eligible journey/channel set | [scope + completeness evidence] |
| Predeclared controlling model | [first/last/linear/time-decay/position/custom + rule ref] |
| Allocation parameters | [exact parameters fixed before readback] |
| Model-selection authorization | [owner/ref/date] |

If any lock is absent, return `NEEDS_INPUT`; do not emit attributed revenue. A model may be omitted entirely when journey completeness is unknown.

### Attributed Revenue by Model

| Scenario | Attributed revenue | ROI | Status |
|----------|--------------------|-----|--------|
| Predeclared controlling model | $[X] | [X]% | controlling; exact model/rule ref |
| Optional alternative model | $[X] | [X]% | non-additive sensitivity only |
| Optional alternative model | $[X] | [X]% | non-additive sensitivity only |

All scenarios must use the same deduplicated conversion universe. Never add them, call every scenario observed revenue, or select the highest result after readback.

### Model Decision

**Controlling model**: [predeclared model + rule/authorization ref, or NEEDS_INPUT]
**Rationale fixed before readback**: [journey/business rule]

### Multi-Touch Journey Example

Illustrative structure only. Replace every touchpoint and allocation with supplied journey data and the declared attribution model; otherwise use `NEEDS_INPUT`.

```
Customer Journey:

Day 1: Sees [creator_ref-1] TikTok asset (Awareness) ─────┐
Day 3: Sees [creator_ref-2] Instagram asset ──────────────┤
Day 5: Clicks [creator_ref-1] link ref (Consideration)┼── Purchase Day 7
Day 7: Uses [creator_ref-2] code ref (Conversion) ─────┘

Attribution:
Last Touch:     100% to [creator_ref-2]
First Touch:    100% to [creator_ref-1]
Linear:         50% each
Position Based: 40% [creator_ref-1], 40% [creator_ref-2], 20% repeat exposure
```
```

## Step 6 — Lifetime Value Analysis

```markdown
## Lifetime Value Analysis

### New Customer Metrics

Use only new customers deduplicated against the controlling attribution universe. Declare whether first-order revenue is already included in LTV and never add it twice.

| Metric | Influencer Acquired | Overall Average |
|--------|--------------------|--------------------|
| New customers | [X] | - |
| First order AOV | $[X] | $[X] |
| Repeat purchase rate | [%] | [%] |
| Customer lifetime value | $[X] | $[X] |

| LTV economic-basis field | Required value |
|--------------------------|----------------|
| Basis | [revenue LTV / contribution-margin LTV] |
| Acquisition cohort and horizon | [cohort definition + months/years] |
| Retention/churn method | [method + source] |
| Returns/refunds/cancellations | [treatment] |
| Gross/contribution margin | [rate/source or not applicable for revenue scenario] |
| Discount rate / timing | [rate and convention] |
| First-order inclusion | [included/excluded; exact no-double-count rule] |
| Status | [Measured/User-provided/Estimated + source/date] |

### LTV-Based ROI

**Formula**: ((New Customers × Avg LTV) - Investment) / Investment × 100

```
New Customers:     [X]
Average LTV:       $[X]
Total LTV:         $[X]
Investment:        $[X]

LTV-Based ROI = ($[contribution-margin LTV total] - $[investment]) / $[investment] × 100
LTV-Based ROI = [X]% or NEEDS_INPUT
```

Only contribution-margin LTV with the complete fields above may support an economic ROI label. Revenue LTV produces an **Estimated revenue-basis scenario**, not profit, and must never be added to direct attributed revenue or another LTV horizon.

### Short-term vs. Long-term View

Keep horizons as separate, non-additive scenarios. Each row names its economic basis and status; never put a revenue-LTV projection in an ROI column.

| Timeframe | Basis | Status | Result | Evidence ref |
|-----------|-------|--------|--------|--------------|
| Immediate (this campaign) | Direct attributed revenue under complete cost basis | [Measured/User-provided/Calculated/NEEDS_INPUT] | [direct ROI % or NEEDS_INPUT] | [opaque ref] |
| 6-month projected | [contribution-margin LTV / revenue LTV] | [Estimated + source/date or NEEDS_INPUT] | [LTV-Based ROI % only for complete contribution-margin basis; otherwise Estimated revenue-basis $ scenario] | [opaque ref] |
| 12-month projected | [contribution-margin LTV / revenue LTV] | [Estimated + source/date or NEEDS_INPUT] | [LTV-Based ROI % only for complete contribution-margin basis; otherwise Estimated revenue-basis $ scenario] | [opaque ref] |
| Lifetime projected | [contribution-margin LTV / revenue LTV] | [Estimated + source/date or NEEDS_INPUT] | [LTV-Based ROI % only for complete contribution-margin basis; otherwise Estimated revenue-basis $ scenario] | [opaque ref] |

### Customer Quality Indicators

| Indicator | Influencer-Acquired | Organic | Paid Ads |
|-----------|--------------------|---------| ---------|
| AOV | $[X] | $[X] | $[X] |
| Return rate | [%] | [%] | [%] |
| Repeat rate | [%] | [%] | [%] |
| NPS/Satisfaction | [X] | [X] | [X] |
```

## Step 7 — Influencer-Level ROI

```markdown
## Influencer-Level ROI

**Locked creator scope**: [campaign_id + exact non-empty creator_ref list + scope ref]
**Comparability/attribution**: [same window, cost basis, currency, controlling deduplicated attribution model]
**Ranking rule**: [metric + better direction + minimum coverage + preregistered rule, or NOT_RANKED]

### Individual Influencer Performance

| Creator ref | Investment | Attributed revenue | ROI | ROAS | Rank |
|-------------|------------|--------------------|-----|------|------|
| creator-<UUIDv4> | $[X] | $[X] | [X]% | [X]:1 | 1 |
| creator-<UUIDv4> | $[X] | $[X] | [X]% | [X]:1 | 2 |
| creator-<UUIDv4> | $[X] | $[X] | [X]% | [X]:1 | 3 |
| creator-<UUIDv4> | $[X] | $[X] | [X]% | [X]:1 | 4 |
| creator-<UUIDv4> | $[X] | $[X] | [X]% | [X]:1 | 5 |

### ROI Distribution

```
Influencer ROI Distribution:

creator-<UUIDv4>  |[bar from supplied data]| [ROI]%
creator-<UUIDv4>  |[bar from supplied data]| [ROI]%
creator-<UUIDv4>  |[bar from supplied data]| [ROI]%
creator-<UUIDv4>  |[bar from supplied data]| [ROI]%
creator-<UUIDv4>  |[bar from supplied data]| [ROI]%

Campaign ROI = (sum attributed revenue - sum spend) / sum spend × 100 = [X]%
Campaign ROAS = sum attributed revenue / sum spend = [X]:1
```

### Investment Efficiency

| Creator ref | % of Budget | % of Attributed Revenue | Efficiency |
|-------------|-------------|-------------------------|------------|
| creator-<UUIDv4> | [%] | [%] | [X]x |
| creator-<UUIDv4> | [%] | [%] | [X]x |

### ROI by Tier

| Tier | Sum investment | Sum attributed revenue | Aggregate ROI | Aggregate ROAS |
|------|----------------|------------------------|---------------|----------------|
| Macro | $[X] | $[X] | [%] | [sum revenue / sum spend]:1 |
| Micro | $[X] | $[X] | [%] | [sum revenue / sum spend]:1 |
| Nano | $[X] | $[X] | [%] | [sum revenue / sum spend]:1 |
```

## Step 8 — ROI Summary Report

```markdown
# ROI Summary Report

## Campaign: [Name]
## Period: [Dates]

---

## Investment Summary

| Category | Amount | % of Total |
|----------|--------|------------|
| Influencer Fees | $[X] | [%] |
| Product/Gifts | $[X] | [%] |
| Amplification | $[X] | [%] |
| Other | $[X] | [%] |
| **Total Investment** | **$[X]** | **100%** |

## Returns Summary

| Return Type | Value |
|-------------|-------|
| Attributed Revenue | $[X] ([source/status/window]) |
| Earned Media Value | $[X] or NEEDS_INPUT ([comparator source/date + declared method]) |
| New Customers | [X] |
| Projected LTV | $[X] |

## ROI by Methodology

| Methodology | ROI | Notes |
|-------------|-----|-------|
| Attributed Revenue ROI | [X]% | Verified only when source, window, attribution, and cost basis are evidenced |
| ROAS | [X]:1 | Revenue per dollar |
| EMV Multiple | [X]x | Estimated media-value scenario |
| LTV-Based ROI | [X]% or NEEDS_INPUT | Economic ROI only from complete contribution-margin LTV; include cohort/horizon/basis/status and no double count |
| Estimated revenue-basis LTV scenario | $[X] or NEEDS_INPUT | Non-additive scenario only; not ROI or profit, with cohort/horizon/source/date |

## Key Metrics

| Metric | Result | Declared target (source/date) | Comparison |
|--------|--------|-------------------------------|------------|
| CPM | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| CPA | $[X] | $[X] ([source], [date]) | [above/below/equal/pending] |
| ROAS | [X]:1 | [X]:1 ([source], [date]) | [above/below/equal/pending] |

## Bottom Line

**Investment**: $[X]
**Return**: $[X]
**Net return under declared formula**: $[X]
**ROI**: [X]%

**Assessment**: [positive/zero/negative arithmetic return on the declared basis] · **Verification**: [verified/results-unverified]

## Recommendations

1. [Key recommendation 1]
2. [Key recommendation 2]
3. [Key recommendation 3]

**Decision owner and precommitted rule**: [owner / rule / UNDECIDED]

---

*Report Generated: [Date]*
```

## Worked Example

**User**: "Calculate ROI from these team-provided values: $25K campaign spend, $72K attributed revenue, and 2.1M reach. No source export, observation date, attribution window, conversion count, incrementality evidence, comparable CPM, or decision rule is supplied."

**Output**:

```markdown
# ROI Calculation Summary

**Verification status**: `results-unverified` — the values below are user-provided, and this skill has not verified their source, date, attribution, or incrementality.

## Investment & Returns

| Item | Value | Provenance |
|------|-------|------------|
| Campaign spend used in calculation | $25,000 | User-provided; cost basis unverified |
| Attributed revenue used in calculation | $72,000 | User-provided; source/window/incrementality unverified |
| Total reach | 2,100,000 | User-provided; source/date unverified |

## ROI Results

### Arithmetic ROI on the Supplied Basis
- **Net return under the declared formula**: $47,000
- **ROI**: 188%
- **ROAS**: 2.88:1

The supplied values equal $2.88 in attributed revenue per $1 of supplied spend. This is arithmetic, not a claim that the campaign generated incremental revenue or profit.

### Earned Media Value
- **EMV**: `NEEDS_INPUT` — no comparable CPM or other declared valuation input was supplied
- **EMV Multiple**: `NEEDS_INPUT`

### Cost Efficiency
- **CPM**: $11.90 (Calculated from supplied spend and reach; results-unverified)
- **CPA**: Unknown (conversion count was not supplied)

## Assessment: Positive arithmetic return on the supplied basis; profitability and causality unverified

Supplied attributed revenue exceeds supplied campaign spend under the declared formula, but no source-dated target, complete cost basis, attribution evidence, or incrementality evidence was provided. Do not infer profitability, causal lift, benchmark outperformance, or authorize a scale decision from this read alone; obtain verified conversions, sources/windows, attribution evidence, and the campaign owner's precommitted decision rule first.
```

## Benchmark Evidence Template

Do not use a repository-default industry threshold. Supply a first-party target or a source-dated external comparator whose market, cohort, window, attribution, and cost basis are compatible with the campaign.

| Field | Value |
|-------|-------|
| Metric | [ROAS / ROI / CPM / CPA / CAC / other] |
| Target or distribution | [value, range, or quantile] |
| Better direction | [higher/lower] |
| Source | [publisher, report, URL, or first-party query] |
| Publication/retrieval date | [YYYY-MM-DD] |
| Market / industry / platform | [scope] |
| Comparison cohort | [selection definition and sample size, if known] |
| Observation window and lag | [dates] |
| Attribution and conversion definition | [basis] |
| Included costs / currency / FX date | [basis] |
| Compatibility assessment | [compatible / materially different / unknown] |
| Comparison status | [above / below / equal / pending] |
