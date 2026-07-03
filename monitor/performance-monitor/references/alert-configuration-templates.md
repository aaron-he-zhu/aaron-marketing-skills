# Alert Configuration Templates

Compact alert thresholds and response plans for SEO/GEO monitoring.

## 1. Alert Thresholds

| Area | Alert | Condition | Priority |
|------|-------|-----------|----------|
| Rankings | Critical drop | Top 3 keyword drops 5+ positions | Critical |
| Rankings | Top 10 loss | Top 10 keyword drops out of top 10 | High |
| Rankings | Moderate drop | Any keyword drops 10+ positions | Medium |
| Rankings | Competitor overtake | Competitor passes you for key term | Medium |
| Rankings | Positive movement | New Top 3, page 1 entry, 10+ position climb | Positive |
| SERP features | Snippet lost / won | Featured snippet ownership changes | High / Positive |
| SERP features | AI Overview change | Appears or disappears | Medium |
| Traffic | Traffic crash | Day-over-day decline >=50% | Critical |
| Traffic | Significant drop | Week-over-week decline >=30% | High |
| Traffic | Moderate decline | Month-over-month decline >=20% | Medium |
| Traffic | Trend warning | 3 consecutive weeks decline | Medium |
| Conversions | Conversion drop | Organic conversions down 30%+ | Critical |
| Conversions | CVR decline | Conversion rate drops 20%+ | High |
| Technical | Site down | HTTP 5xx errors | Critical |
| Technical | SSL expiry | Certificate expires in 14 days | Critical |
| Technical | Robots.txt block | Important pages blocked | Critical |
| Technical | Index drop | Important pages drop from index | Critical |
| Technical | Crawl/index/CWV/mobile issue | Error spike 50%+, 10% index drop, CWV poor, mobile errors | High |
| Technical | New 404 pages | 404 errors on important pages | Medium |
| Technical | Redirect chains | 3+ redirect hops | Medium |
| Security | Manual action / malware | GSC warning or flagged issue | Critical |
| Backlinks | High-value link lost | DA 70+ link removed | High |
| Backlinks | High-value link gained | New DA 70+ link | Positive |
| Backlinks | Multiple lost links | 10+ links lost in a day | Medium |
| Backlinks | Toxic / negative SEO | Spam pattern or toxic score +20% | High |
| Competitors | Competitor content/backlink move | New content/update or high-DA link | Info |
| GEO | Citation lost/won | AI citation ownership changes | Medium / Positive |
| GEO | Citation rate drop | AI citation rate drops 20%+ | High |
| Brand | Negative mention / rating drop | Sentiment or rating deterioration | High |
| Brand | Unlinked mention | Brand mention without link | Opportunity |

## 2. Page-Level Traffic Rules

| Page Type | Alert Condition | Priority |
|-----------|-----------------|----------|
| Homepage | 20%+ decline | Critical |
| Top 10 pages | 30%+ decline | High |
| Conversion pages | 25%+ decline | High |
| Blog posts | 40%+ decline | Medium |

## 3. Response Plans

| Priority | Response Time | Immediate Actions |
|----------|---------------|-------------------|
| Critical | Within 1 hour | Confirm data, check server/GSC/indexing, assign owner, start incident log |
| High | Same day | Diagnose cause, compare competitors/SERP, create recovery plan |
| Medium | Within 48 hours | Investigate trend, batch with related alerts, schedule fix |
| Low / Info | Weekly review | Document, tag trend, no interruption |
| Positive | Weekly review | Record win and identify repeatable driver |

| Alert Type | First Checks |
|------------|--------------|
| Site down | Server, DNS, CDN, deploy status |
| Traffic crash | Algorithm update, GSC errors, analytics tag, competitors |
| Manual action | GSC message, affected URLs, remediation path |
| Critical rank drop | Indexing, SERP change, page changes, competitor movement |
| Backlink loss | Source page status, relationship owner, outreach path |
| CWV failure | Template, script, image, hosting, field data |

## 4. Notification Setup

| Priority | Channels | Frequency | Escalation |
|----------|----------|-----------|------------|
| Critical | Email + SMS + Slack | Immediate | No response in 1hr -> Director |
| High | Email + Slack | Immediate | No response in 4hr -> Manager |
| Medium | Email + Slack | Daily digest | No response in 24hr -> Lead |
| Low / Positive | Email | Weekly digest | None |

| Role | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| SEO Manager | Yes | Yes | Yes | Yes |
| Dev Team | Yes | Tech only | No | No |
| Marketing Lead | Yes | Yes | No | No |
| Executive | Yes | No | No | No |

## 5. Suppression Rules

- Suppress duplicate alerts for 24 hours.
- Suppress known maintenance windows.
- Batch low-priority alerts into digests.
- Require source timestamp and metric source on every alert.
- Mark unresolved alerts with owner, status, and next check time.
