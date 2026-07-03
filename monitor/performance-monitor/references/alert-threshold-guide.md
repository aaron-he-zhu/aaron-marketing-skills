# Alert Threshold Guide

## Severity Levels

**Standard Deviation method**: Info (1 SD), Warning (1.5 SD), Critical (2 SD), Emergency (3 SD) from baseline mean.

## Thresholds by Metric Category

### Traffic

| Metric | Warning | Critical | Emergency |
|--------|---------|----------|-----------|
| Organic sessions (WoW) | -15% | -30% | -50% |
| Organic sessions (DoD) | -25% weekday | -40% | Site appears down |
| Non-brand sessions (WoW) | -20% | -35% | -50% |
| Organic conversions (WoW) | -20% | -40% | -60% |
| Top 10 page traffic (WoW) | -25% | -40% | -60% |

### Rankings

| Metric | Warning | Critical |
|--------|---------|----------|
| Tier 1 keyword position | Drop >= 3 | Drop >= 5 |
| Tier 2 keyword position | Drop >= 5 | Drop >= 10 |
| Tier 3 keyword position | Drop >= 10 | Off page 3 |
| Average position (all) | +2.0 worsening | +5.0 worsening |
| Keywords in top 10 | -10% count | -20% count |
| Brand keyword | Any drop from #1 | Below #3 |
| Featured snippet | Any loss | 3+ losses |

### Technical

| Metric | Warning | Critical | Emergency |
|--------|---------|----------|-----------|
| New 4xx errors | >5/day | >20/day | >100/day |
| New 5xx errors | >1/day | >5/day | >20/day |
| Crawl rate change | -30% baseline | -60% baseline | Near-zero |
| Index coverage drop | -5% | -15% | -30% |
| Server response time | >500ms | >1000ms | >2000ms |
| LCP (mobile) | Needs Improvement | Poor | >6s |
| CLS | >0.1 | >0.25 | >0.5 |
| INP | >200ms | >500ms | >1000ms |

### Backlinks

| Metric | Warning | Critical |
|--------|---------|----------|
| Referring domains lost (weekly) | >5% total | >15% total |
| High-authority link lost (DR 60+) | Any loss | 3+ in one week |
| Toxic link spike | >10/week | >50/week |
| Exact match anchor % | Reaches 20% | Reaches 30% |

### GEO / AI Visibility

| Metric | Warning | Critical |
|--------|---------|----------|
| AI citation rate | Drops 10+ pp | Below 10% |
| Key query citation lost | Any Tier 1 | 3+ Tier 1 queries |
| Citation position | Worsens by 2+ | Dropped entirely |

## Alert Routing

| Priority | Channel | Escalation |
|----------|---------|------------|
| P0 Emergency | SMS + Phone + Slack #emergencies | PagerDuty on-call |
| P1 Urgent | Slack #alerts + Email | SMS if unacknowledged in 4h |
| P2 Important | Email + Slack #daily | Auto-escalate to P1 after 1 week |
| P3 Monitor | Weekly digest | Auto-escalate to P2 after 1 month |

## Suppression Rules

| Rule | Configuration |
|------|--------------|
| Duplicate cooldown | No re-alert same metric for 24h |
| Maintenance window | Suppress non-security alerts |
| Weekend adjustment | Increase traffic thresholds +20% |
| Recovery auto-close | Close if metric normalizes within 48h |
| Batch related | Group multiple ranking drops into one alert |

## Threshold Tuning

| Signal | Action |
|--------|--------|
| >30% false positives | Widen thresholds by 0.5 SD |
| Missed real problem | Tighten the specific threshold |
| Seasonal change | Adjust baselines for known patterns |
| Major site change | Re-establish baseline (2-4 week observation) |
| After algorithm update | Stabilize 2-4 weeks, then recalibrate |

### Site Maturity Guidelines

| Stage | Approach |
|-------|----------|
| New (0-6mo) | Wide thresholds, few alerts |
| Growing (6-18mo) | Moderate thresholds, expand coverage |
| Established (18mo+) | Tight thresholds, comprehensive |
| Post-migration | Reset to wide, re-tighten over 4-8 weeks |
