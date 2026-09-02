# Budget Optimizer — Templates, Cost Evidence & Scenarios

Fill-in templates, the source-dated cost-evidence intake, scenario A/B/C blocks, optimization strategies, and the mid-campaign reallocation template for [budget-optimizer](../SKILL.md). Each section maps to a numbered Instructions step in the parent skill. This reference supplies no default rate, multiplier, contingency, savings, or amplification percentage.

## Step 1 — Budget Parameters (intake template)

```markdown
### Budget Optimization Parameters

**Campaign Details**:
- Campaign Goal: [awareness/engagement/conversion]
- Target Audience: [description]
- Timeline: [duration]
- Geographic Focus: [regions]

**Budget Information**:
- Total Budget: $[X]
- Fixed Costs: $[X] (agency, tools, etc.)
- Available for Influencers: $[X]

**Platform Priorities**:
- Primary: [platform]
- Secondary: [platform(s)]

**Constraints**:
- Must include: [requirements]
- Maximum per influencer: $[X]
- Minimum influencers: [#]
```

## Step 2 — Cost Evidence

Numerical allocation begins only after at least one compatible user-provided,
first-party, quoted, or source-dated market anchor is available. Keep
incompatible evidence for context; do not silently transfer it across markets,
platforms, tiers, deliverables, rights, or dates.

```markdown
### Cost / Comparator Evidence Inventory

| Input | Value | Source ref | Published/retrieved | Market | Platform/tier | Deliverable + rights/exclusivity | Currency/FX date | Evidence window | Compatibility | Label |
|-------|-------|------------|---------------------|--------|---------------|----------------------------------|------------------|-----------------|---------------|-------|
| [quote/history/comparator] | [amount/range] | [opaque ref] | [date] | [market] | [scope] | [scope] | [currency/date] | [window] | compatible/context-only | User-provided/Measured/Estimated |

**Unsupported inputs**: [missing rate, multiplier, or comparator]
**Status**: [READY_FOR_MODELING / NEEDS_INPUT]
**Exact query/request plan**: [which rate cards, comparable campaign history, or approved assumptions are needed]
```

## Step 3 — Budget Allocation Recommendation

```markdown
## Budget Allocation Recommendation

### Total Budget: $[X]

#### By Influencer Tier

| Tier | % Budget | Amount | # Influencers | Cost/Influencer |
|------|----------|--------|---------------|-----------------|
| Macro | [%] | $[X] | [#] | ~$[X] |
| Micro | [%] | $[X] | [#] | ~$[X] |
| Nano | [%] | $[X] | [#] | ~$[X] |
| **Total** | **100%** | **$[X]** | **[#]** | |

**Rationale**: [Why this tier mix for this campaign goal]

#### By Platform

| Platform | % Budget | Amount | Rationale |
|----------|----------|--------|-----------|
| [Platform 1] | [%] | $[X] | [why] |
| [Platform 2] | [%] | $[X] | [why] |
| [Platform 3] | [%] | $[X] | [why] |

#### By Content Type

| Content Type | % Budget | Amount | Quantity |
|--------------|----------|--------|----------|
| [Type 1] | [%] | $[X] | [#] pieces |
| [Type 2] | [%] | $[X] | [#] pieces |

#### Other Budget Items

| Item | Amount | % of Total | Notes |
|------|--------|------------|-------|
| Product/Gifting | $[X] | [%] | [notes] |
| Content Amplification | $[X] | [%] | Boosting top content |
| Tools/Software | $[X] | [%] | [tools] |
| Contingency | $[X/TBD] | [%/TBD] | [user rule or source-dated anchor ref; otherwise TBD] |
```

## Step 4 — Return Projections

```markdown
## Return Projections

### Expected Results

| Metric | Projection | Formula | Input refs | Window | Label |
|--------|------------|---------|------------|--------|-------|
| Total Reach | [X/TBD] | [formula] | [refs] | [window] | [label] |
| Impressions | [X/TBD] | Reach × frequency | [refs] | [window] | Estimated/NEEDS_INPUT |
| Engagements | [X/TBD] | Reach × ER | [refs] | [window] | Estimated/NEEDS_INPUT |
| Video Views | [X/TBD] | [formula] | [refs] | [window] | [label] |
| Link Clicks | [X/TBD] | impressions × CTR | [refs] | [window] | Estimated/NEEDS_INPUT |
| EMV (separate non-revenue scenario) | $[X/TBD] | impressions ÷ 1,000 × declared equivalency CPM | [refs] | [window] | Estimated/NEEDS_INPUT |

### Cost Efficiency Metrics

| Metric | Projected | Declared comparator | Comparator source/date/scope | Comparison |
|--------|-----------|---------------------|------------------------------|------------|
| CPM | $[X/TBD] | $[Y/TBD] | [ref/date/scope] | [better/worse/NOT_COMPARABLE] |
| CPE | $[X/TBD] | $[Y/TBD] | [ref/date/scope] | [better/worse/NOT_COMPARABLE] |
| Cost per Video View | $[X/TBD] | $[Y/TBD] | [ref/date/scope] | [better/worse/NOT_COMPARABLE] |
| Cost per Click | $[X/TBD] | $[Y/TBD] | [ref/date/scope] | [better/worse/NOT_COMPARABLE] |

### Revenue-basis return calculation

- **Investment**: $[X]
- **Projected attributed revenue**: $[X/TBD] — [input refs + attribution method/window]
- **Projected ROAS**: [X:1/TBD] = attributed revenue ÷ spend
- **Arithmetic ROI**: [X%/TBD] = (attributed revenue - spend) ÷ spend × 100%
- **Profit/incrementality status**: [NOT_CLAIMED / supported by named cost and incrementality evidence]
- **EMV**: report separately above; never add it to attributed revenue or cash return.

### Conversion Projections (if applicable)

| Stage | Number | Rate | Notes |
|-------|--------|------|-------|
| Reach | [X] | - | Starting point |
| Clicks | [X] | [%] | Click-through rate |
| Site Visits | [X] | [%] | Bounce considered |
| Conversions | [X] | [%] | Conversion rate |
| Revenue | $[X] | [AOV] | Average order value |
| **ROAS** | **[X]:1/TBD** | attributed revenue ÷ spend | Not ROI and not proof of profit or incrementality |
```

## Step 5 — Budget Scenarios

```markdown
## Budget Scenarios

### Scenario Comparison

| Factor | Conservative | Recommended | Aggressive |
|--------|--------------|-------------|------------|
| **Budget** | $[X] | $[Y] | $[Z] |
| # Influencers | [#] | [#] | [#] |
| Tier Mix | [mix] | [mix] | [mix] |
| Est. Reach | [X] | [X] | [X] |
| Est. Engagements | [X] | [X] | [X] |
| Projected CPM | $[X] | $[X] | $[X] |
| Projected ROAS | [X:1/TBD] | [X:1/TBD] | [X:1/TBD] |
| Arithmetic ROI | [X%/TBD] | [X%/TBD] | [X%/TBD] |
| Evidence completeness | [state] | [state] | [state] |

### Scenario A: Conservative ($[X])

**Strategy**: Focus on proven micro-influencers with high engagement

| Tier | # | Budget | Content |
|------|---|--------|---------|
| Micro | [#] | $[X] | [#] posts |
| Nano | [#] | $[X] | [#] posts |

**Pros / cons**: [supported trade-offs; cite the input or label as hypothesis]

---

### Scenario B: Recommended ($[Y])

**Strategy**: Balanced mix with macro anchor and micro support

| Tier | # | Budget | Content |
|------|---|--------|---------|
| Macro | [#] | $[X] | [#] posts |
| Micro | [#] | $[X] | [#] posts |
| Nano | [#] | $[X] | [#] posts |

**Pros / cons**: [supported trade-offs; cite the input or label as hypothesis]

---

### Scenario C: Aggressive ($[Z])

**Strategy**: Macro-heavy with celebrity/mega-influencer

| Tier | # | Budget | Content |
|------|---|--------|---------|
| Mega | [#] | $[X] | [#] posts |
| Macro | [#] | $[X] | [#] posts |
| Micro | [#] | $[X] | [#] posts |

**Pros / cons**: [supported trade-offs; cite the input or label as hypothesis]

---

### Recommendation

**Recommended Scenario**: [Scenario X]
**Rationale**: [Why this scenario best meets campaign goals]
```

## Step 6 — Optimization Strategies

```markdown
## Budget Optimization Strategies

### Cost Reduction Strategies

| Strategy | Modeled savings | Evidence/assumption ref | Trade-offs |
|----------|-----------------|-------------------------|------------|
| Negotiate multi-post deals | [TBD/%] | [user/source-dated anchor] | Commitment required |
| Product-inclusive compensation | [TBD/%] | [user/source-dated anchor] | Creator acceptance and fair-value review required |
| Affiliate-heavy model | [TBD/%] | [user/source-dated anchor] | Performance-dependent |
| Long-term ambassadors | [TBD/%] | [user/source-dated anchor] | Less variety |
| Emerging creators | [TBD/%] | [user/source-dated anchor] | Less history |
| Off-peak timing | [TBD/%] | [user/source-dated anchor] | Timing trade-off |

### Value Maximization Strategies

1. **Bundle deliverables**: Model any package savings only from a quote, first-party history, or source-dated compatible anchor.
2. **Usage rights scope**: Default whitelisting and repurposing rights to a defined term, named channels, and territory; price extensions separately.
3. **Performance incentives**: Base fee + performance bonus to align interests and motivate quality content.
4. **Content amplification**: Allocate only the user-approved or source-dated amount and keep creator licensing/authorization separate.
5. **Expanded UGC rights**: Treat perpetual, global, or all-channel rights as an exception that requires incremental pricing and legal review before agreement.

### Budget Red Flags

- Concentration above the user-approved or source-dated threshold
- CPM above a declared compatible comparator
- No contingency allocated
- All budget on unproven creators
- Ignoring content amplification
```

## Step 7 — Mid-Campaign Reallocation

```markdown
## Mid-Campaign Budget Reallocation

### Current Performance vs. Plan

| Metric | Planned | Actual | Variance | Action |
|--------|---------|--------|----------|--------|
| Spend to Date | $[X] | $[X] | [%] | [action] |
| Content Live | [#] | [#] | [%] | [action] |
| Reach | [X] | [X] | [%] | [action] |
| Engagement | [X] | [X] | [%] | [action] |
| CPM | $[X] | $[X] | [%] | [action] |

### Top Performers

| Creator ref | Spend | Comparable result | Return metric | Decision-rule status |
|-------------|-------|-------------------|---------------|----------------------|
| [creator-<UUIDv4>] | $[X] | [result + source/window] | [ROAS x:1 or ROI %] | [CLEARED/KEEP_TESTING/NEEDS_INPUT] |

### Underperformers

| Creator ref | Spend | Comparable result | Return metric | Decision-rule status |
|-------------|-------|-------------------|---------------|----------------------|
| [creator-<UUIDv4>] | $[X] | [result + source/window] | [ROAS x:1 or ROI %] | [CLEARED/KEEP_TESTING/NEEDS_INPUT] |

### Reallocation Recommendation

| From creator_ref/pool | To creator_ref/pool | Amount | Preregistered rule + evidence | Authorization status |
|-----------------------|---------------------|--------|-------------------------------|----------------------|
| [ref] | [ref] | $[X/TBD] | [rule/window/refs] | PROPOSED_ONLY / AUTHORIZED |

**Expected impact**: [Unknown unless supported by approved modeled inputs]. A cleared recommendation still does not move spend without separate action authorization.
```

## Optimization tips

1. **Don't put all eggs in one basket** — diversify across tiers.
2. **Reserve amplification budget** — best content deserves reach.
3. **Plan for contingency** — things change mid-campaign.
4. **Negotiate packages** — multi-post deals save money.
5. **Track cost efficiency** — CPM/CPE matter more than raw spend.

## Second worked example — $30,000 skincare launch (Gen Z, IG + TikTok)

```markdown
## Budget Allocation: $30,000 Skincare Launch

**Status**: NEEDS_INPUT

Only the total, audience, goal, and platforms were supplied. Return the 100%
allocation worksheet with all rate-, quantity-, contingency-, and projection-
dependent cells marked `TBD`. Request dated compatible creator quotes (including
deliverable and rights scope), comparable reach/engagement history, and approved
conversion/AOV/attribution inputs. Do not invent a split, creator count, CPM,
EMV, ROAS, or ROI from this prompt.
```
