# SEO/GEO Report Templates

Copy-ready report skeletons for executive, marketing, technical, and client audiences. Use placeholders, not sample numbers, unless user data is available.

## 1. Executive Report

For C-suite/VP reporting. Keep to 1 page and lead with business impact.

```markdown
# SEO & GEO Performance Summary
**Period**: [Month Year] | **Audience**: [Audience] | **Prepared by**: [Name]

## Performance At A Glance
| KPI | Current | Prior | MoM/QoQ | YoY | Target | Status |
|-----|---------|-------|---------|-----|--------|--------|
| Organic revenue | [$] | [$] | [%] | [%] | [$] | [status] |
| Organic sessions | [X] | [X] | [%] | [%] | [X] | [status] |
| Keywords in Top 10 | [X] | [X] | [+/-X] | [+/-X] | [X] | [status] |
| Organic conversions | [X] | [X] | [%] | [%] | [X] | [status] |
| Domain Rating / Authority | [X] | [X] | [+/-X] | [+/-X] | [X] | [status] |
| AI citations | [X] | [X] | [%] | N/A | [X] | [status] |

## Competitive Position
**Share of voice**: [rank] of [N] tracked competitors ([change]).

| Rank | Competitor | Visibility Share | Change |
|------|------------|------------------|--------|
| [1] | [domain] | [%] | [+/-] |

## Wins, Risks, And Ask
- Wins: [business win], [SEO/GEO win], [authority/content win]
- Risks: [risk + mitigation/owner], [risk + mitigation/owner]
- Investment / ROI: [spend] -> [organic revenue/value] -> [ROI]
- Ask for next period: [decision/budget/resource] by [date]
```

## 2. Marketing Report

For marketing managers, content teams, and channel leads.

```markdown
# Monthly SEO & GEO Performance Report
**Domain**: [domain] | **Period**: [date range] | **Comparison**: [prior period + prior year]

| Area | Metric | Current | Prior | Change | YoY | Action |
|------|--------|---------|-------|--------|-----|--------|
| Traffic | Organic sessions / users | [X] | [X] | [%] | [%] | [action] |
| Engagement | Bounce or engagement rate / duration | [value] | [value] | [change] | [change] | [action] |
| Rankings | #1 / Top 3 / Top 10 / 11-50 | [counts] | [counts] | [+/-] | [+/-] | [action] |
| Content | Top pages / conversions | [values] | [values] | [change] | [change] | [action] |
| GEO | AI Overview queries / citations / citation rate | [values] | [values] | [change] | N/A | [action] |
| Authority | Referring domains / new links / avg new DR | [values] | [values] | [change] | [change] | [action] |

## Keyword Movers
| Keyword | Volume | Old -> New | Change | Action |
|---------|--------|------------|--------|--------|
| [keyword] | [X] | [X -> Y] | [+/-] | [action] |

## Action Items
| Priority | Action | Owner | Deadline | Expected Impact |
|----------|--------|-------|----------|-----------------|
| P0/P1/P2 | [action] | [owner] | [date] | [impact] |
```

## 3. Technical Report

For engineering teams and technical stakeholders. Add business impact only for prioritization.

```markdown
# Technical SEO Health Report
**Domain**: [domain] | **Period**: [date range] | **Data freshness**: [timestamp]

| Area | Metric | Current | Prior | Change | Status | Action |
|------|--------|---------|-------|--------|--------|--------|
| Crawl | Pages crawled / avg response time | [values] | [values] | [change] | [status] | [action] |
| Indexation | Valid indexed / excluded errors | [values] | [values] | [change] | [status] | [action] |
| CWV | LCP / CLS / INP | [values] | [values] | [change] | [status] | [action] |
| Errors | 404 / 5xx / redirect chains | [counts] | [counts] | [change] | [status] | [action] |
| Schema | Valid / warning / error pages | [counts] | [counts] | [change] | [status] | [action] |

## Technical Debt Tracker
| Item | Priority | Effort | Owner | Deadline | Status |
|------|----------|--------|-------|----------|--------|
| [issue] | P0/P1/P2 | L/M/H | [owner] | [date] | [status] |
```

## 4. Assembly Rules

| Audience | Include | Exclude |
|----------|---------|---------|
| CEO / Board | Executive summary, KPI status, ROI, risks, asks | Technical debugging detail |
| VP Marketing | Executive + marketing sections | Deep crawl/schema logs |
| Marketing Manager | Full marketing report | Engineering-only detail |
| Engineering Lead | Technical report + P0/P1 context | Keyword/revenue overload |
| Client / Agency | Executive + marketing + actions | Internal cost data |

### Data Freshness Requirements

| Report Type | Maximum Data Age |
|-------------|------------------|
| Executive monthly | 3 days after period end |
| Marketing weekly | 1 day after period end |
| Technical | Real-time where possible |
| Quarterly review | 5 days after quarter end |

### Delivery Checklist

- [ ] All data sources verified and dated
- [ ] Period-over-period comparisons included
- [ ] Authority metric included when reporting performance at a glance
- [ ] AI citation / GEO metric included when in scope
- [ ] Action items are specific, assigned, and time-bound
- [ ] Report tailored to audience level
- [ ] External benchmarks cited with source and date
