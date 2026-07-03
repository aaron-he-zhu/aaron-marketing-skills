# Performance Report Output Templates

Use one reporting shape: metric table -> what changed -> why it matters -> next action.

## Shared Conventions

| Item | Rule |
|------|------|
| Status | `On track`, `Watch`, `Off track`, or `N/A` |
| Delta | Show absolute and percentage change when possible |
| Audience | Executive = trends + actions; Technical = causes + owners |
| Missing inputs | Mark `Not yet evaluated` and point to the next-best skill |

## Report Configuration

Domain, period, comparison, data freshness, report type, Audience, focus, source/date for each imported data set.

## Executive Summary

```markdown
# SEO & GEO Performance Report
**Domain**: [domain] | **Period**: [date range] | **Prepared**: [date]

**Overall performance**: [Excellent/Good/Needs Attention/Critical]

| Metric | Current | Previous | Change | Target | Status |
|--------|---------|----------|--------|--------|--------|
| Organic Traffic | [X] | [Y] | [+/-Z%] | [T] | [status] |
| Keywords Top 10 | [X] | [Y] | [+/-Z] | [T] | [status] |
| Organic Conversions | [X] | [Y] | [+/-Z%] | [T] | [status] |
| Domain Authority / CITE | [X] | [Y] | [+/-Z] | [T] | [status] |
| AI Citations | [X] | [Y] | [+/-Z%] | [T] | [status] |

Wins: [bullets] | Watch areas: [bullets] | Action required: [bullets]
```

## Section Templates

| Section | Required fields |
|---------|-----------------|
| Organic Traffic | sessions, users, pageviews, bounce rate, top pages, device split, why it moved, next action |
| Keyword Rankings | position buckets, top improvements, declines, SERP features, traffic impact |
| GEO / AI Visibility | queries with AI answer, your citations, citation rate, wins, gaps |
| Domain Authority (CITE Score) | CITE score, C/I/T/E dimensions, veto status, `Not yet evaluated` fallback |
| Content Quality (CORE-EEAT) | pages audited, average CORE-EEAT/GEO/SEO, veto IDs, dimension trends |
| Backlinks | total backlinks, referring domains, average authority, notable links, toxic risk |
| Content Performance | new articles, updates, top performers, declining pages, refresh actions |
| Recommendations | horizon, priority, action, expected impact, owner |

## Full Report Skeleton

```markdown
# [Company] SEO & GEO Performance Report - [Month/Quarter] [Year]
## Executive Summary
## Organic Traffic
## Keyword Rankings
## GEO / AI Visibility
## Domain Authority (CITE Score)
## Content Quality (CORE-EEAT)
## Backlinks
## Content Performance
## Recommendations & Next Steps
## Appendix: data sources, methodology, missing inputs
```
