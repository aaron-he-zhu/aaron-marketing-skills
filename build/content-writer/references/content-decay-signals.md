# Content Decay Signals

## Primary Signals (High Reliability)

### 1. Organic Traffic Decline

| Severity | Threshold (MoM) | Action |
|----------|-----------------|--------|
| Watch | 10-20% decline | Add to monitoring list |
| Warning | 20-40% decline | Schedule refresh within 2 weeks |
| Critical | 40-60% decline | Refresh this week |
| Emergency | >60% decline | Investigate immediately (may be technical) |

**False positive check**: Rule out seasonality (compare YoY), algorithm updates, technical issues, tracking changes.

### 2. Ranking Position Drops

| Severity | Threshold (2-week avg) | Action |
|----------|------------------------|--------|
| Watch | 1-3 positions lost | Monitor |
| Warning | 3-5 positions lost | Investigate cause |
| Critical | 5-10 positions lost | Immediate refresh |
| Emergency | Off page 1 to page 3+ | Priority refresh or rewrite |

### 3. Click-Through Rate Decline

| Severity | Threshold | Action |
|----------|-----------|--------|
| Watch | CTR below expected for position | Review title + meta |
| Warning | CTR dropped 20%+ vs baseline | Rewrite title + meta |
| Critical | CTR dropped 40%+ vs baseline | Full refresh: title, description, structured data |

**Expected CTR benchmarks** (organic, desktop):
Pos 1: 25-35% (investigate <20%) | Pos 2: 12-18% (<10%) | Pos 3: 8-12% (<6%) | Pos 4-5: 5-8% (<4%) | Pos 6-10: 2-5% (<2%)

## Secondary Signals

| Signal | Decay Indicator |
|--------|----------------|
| Bounce rate increase >15% | Content no longer satisfies intent |
| Time on page decrease >20% | Users leaving faster |
| Published >12mo, never updated | High decay risk |
| Year references 2+ years old | High decay risk |
| Broken external links >10% | Medium decay risk |
| References to discontinued products | High decay risk |
| New competitor ranking above you | Competitive displacement |
| Featured snippet lost | Competitive displacement |
| AI overview answers query without click | Competitive displacement |

## Alert Priority Matrix

| Signal Combination | Priority | Response |
|--------------------|----------|----------|
| Traffic decline + Position drop | P1 Critical | Refresh within 48 hours |
| Traffic decline + CTR decline | P1 Critical | Rewrite title/desc immediately, schedule refresh |
| Position drop + Competitor displacement | P2 High | Refresh within 1 week |
| Traffic decline + Engagement decline | P2 High | Refresh within 1 week |
| CTR decline only | P3 Medium | Rewrite title + meta this week |
| Freshness indicators only | P3 Medium | Schedule refresh within 2 weeks |

## Composite Decay Score (0-100)

| Signal | Weight |
|--------|--------|
| Traffic decline | 30% |
| Position drops | 25% |
| CTR decline | 15% |
| Content freshness | 15% |
| Competitive displacement | 15% |

| Score | Stage | Action |
|-------|-------|--------|
| 0-20 | Healthy | Continue monitoring |
| 21-40 | Early decay | Refresh queue (next month) |
| 41-60 | Active decay | Refresh this week |
| 61-80 | Significant decay | Immediate refresh or rewrite |
| 81-100 | Terminal decay | Rewrite, redirect, or retire |

## Refresh vs. Rewrite Decision

**REFRESH when**: URL has backlinks, was ranking well, <50% content changing, intent unchanged.
**REWRITE when**: Never ranked well, no backlinks, >50% needs rewriting, search intent evolved.

## Content Retirement Checklist

Retire when: zero search volume keyword | topic irrelevant to business | no backlinks | never ranked well | refresh cost > 12-month recovery value | cannibalizes better page.

| Option | When to Use |
|--------|------------|
| 301 redirect | Has backlinks or residual traffic |
| Consolidate | Multiple weak pages on same topic |
| Noindex | Internal utility only |
| Delete (410) | No value, no links, no traffic |

## Refresh Frequency by Content Type

| Content Type | Frequency | Shelf Life |
|-------------|-----------|-----------|
| Statistics roundups | Every 6 months | 6-12 months |
| Tool comparisons | Every 3-6 months | 3-6 months |
| How-to guides | Annually | 12-18 months |
| Evergreen guides | Every 12-18 months | 18-24 months |
| News/trend content | Don't refresh | 1-3 months |
| Case studies | Rarely | 2-3 years |
