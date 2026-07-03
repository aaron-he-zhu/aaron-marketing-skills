# Backlink Analysis -- Output Templates

Compact copy-start templates for the backlink-analysis workflow. Use placeholders until real tool exports are available.

## 1. Profile Overview

```markdown
## Backlink Profile Overview
**Domain**: [domain] | **Period**: [period] | **Data date**: [date]

| Metric | Current | Prior / Benchmark | Status |
|--------|---------|-------------------|--------|
| Total backlinks | [X] | [Y] | [status] |
| Referring domains | [X] | [Y] | [status] |
| DA / DR | [X] | [Y] | [status] |
| Dofollow ratio | [X]% | [Y]% | [status] |
| Net velocity | [+/-X] | [prior] | [status] |

**Authority mix**: DA 80-100 [X]% | 60-79 [X]% | 40-59 [X]% | 20-39 [X]% | 0-19 [X]%
**Geo mix**: [top countries + share]
**Profile health score**: [X]/100 because [main drivers]
```

## 2. Quality, Anchors, And Toxicity

```markdown
## Link Quality Analysis

| Source Domain | DA/DR | Link Type | Follow | Anchor | Target | Quality Notes |
|---------------|-------|-----------|--------|--------|--------|---------------|
| [domain] | [X] | [editorial/resource/etc.] | dofollow/nofollow | [anchor] | [URL] | [reason] |

| Anchor Type | Count | Share | Risk / Note |
|-------------|-------|-------|-------------|
| Brand | [X] | [Y]% | [note] |
| Exact match | [X] | [Y]% | [note] |
| Partial match | [X] | [Y]% | [note] |
| URL / naked | [X] | [Y]% | [note] |
| Generic | [X] | [Y]% | [note] |

## Toxic Link Review
**Toxic score**: [X]/100 | **Action required**: [none / monitor / outreach / disavow candidate]

| Risk Signal | Count | Evidence | Recommended Action |
|-------------|-------|----------|--------------------|
| Spam / link farm | [X] | [examples] | [action] |
| PBN suspected | [X] | [pattern] | [action] |
| Irrelevant or hacked site | [X] | [evidence] | [action] |
| Manipulative anchor | [X] | [anchor pattern] | [action] |
```

## 3. Competitive And Opportunity Analysis

```markdown
## Competitive Backlink Analysis

| Metric | You | Comp 1 | Comp 2 | Comp 3 | Gap |
|--------|-----|--------|--------|--------|-----|
| Referring domains | [X] | [X] | [X] | [X] | [gap] |
| DA / DR | [X] | [X] | [X] | [X] | [gap] |
| Link velocity | [X] | [X] | [X] | [X] | [gap] |
| Avg link DA/DR | [X] | [X] | [X] | [X] | [gap] |

| Prospect / Content | Evidence | Approach | Effort | Impact | Priority |
|--------------------|----------|----------|--------|--------|----------|
| [domain or page] | [links to competitors / broken link / unlinked mention] | [outreach angle] | L/M/H | L/M/H | P0/P1/P2 |

**Top competitor-linked assets**: [asset] -- [why links accrue]
**Recommended asset gap**: [asset to build or update]
```

## 4. Change Tracking And Recovery

```markdown
## Link Change Tracking
**Window**: [30/90 days] | **Net change**: [+/-X]

| Change | Source | DA/DR | Anchor | Target | Date | Action |
|--------|--------|-------|--------|--------|------|--------|
| New / Lost | [domain] | [X] | [anchor] | [URL] | [date] | [monitor/reclaim/thank] |

### Recovery Priorities
| Lost Link | Value | Likely Cause | Recovery Strategy |
|-----------|-------|--------------|-------------------|
| [domain] | High/Med/Low | [reason] | [outreach/update/redirect] |
```

## 5. Summary Report

```markdown
# Backlink Analysis Report
**Domain**: [domain] | **Date**: [date] | **Period**: [period]

## Executive Summary
- Referring domains: [X] ([+/-Y] vs prior)
- Average authority: [X]
- Net velocity: [X]
- Toxic link share: [X]%
- Highest-value opportunity: [summary]

## Strengths
- [strength + evidence]

## Concerns
- [concern + evidence + risk]

## Recommended Actions
| Timing | Action | Owner | Expected Impact |
|--------|--------|-------|-----------------|
| Immediate | [action] | [owner] | [impact] |
| 30 days | [action] | [owner] | [impact] |
| 90 days | [action] | [owner] | [impact] |

## KPIs To Track
Referring domains, average authority, toxic link share, anchor mix, net link velocity, reclaimed lost links.
```
