# Rank Tracking Setup Guide

Configuration checklist and interpretation rules for reliable rank tracking.

## Tool Setup

| Step | Action | Notes |
|------|--------|-------|
| 1 | Select rank tracker | `~~SEO tool` with keyword/location/device support |
| 2 | Add target domain | Include key subdomains when relevant |
| 3 | Set location | Country, region, city, or separate project per market |
| 4 | Set device | Track mobile and desktop when budget allows |
| 5 | Set search engine/language | Match target audience |
| 6 | Add competitors | 3-5 direct competitors |
| 7 | Import keywords | From keyword research, GSC, or existing tracker |
| 8 | Configure frequency | Daily for priority terms; weekly for long-tail |
| 9 | Verify first pull | Spot-check against manual searches |

| Scenario | Location Setup |
|----------|----------------|
| National | Country |
| Regional | State/region |
| Local | City |
| Multi-location | Separate project per location |
| International | Separate project per country |

## Keyword Selection

| Site Size | Recommended Keywords | Breakdown |
|-----------|----------------------|-----------|
| Small (<50 pages) | 50-100 | brand + primary + secondary + long-tail |
| Medium (50-500 pages) | 100-500 | brand + priority pages + topic clusters |
| Large (500+ pages) | 500-2,000+ | scale by revenue pages |
| Enterprise | 2,000-10,000+ | automated grouping and governance |

| Include | Rule |
|---------|------|
| Revenue terms | Always track conversion-driving keywords |
| Page 1-3 terms | Track current opportunity set |
| Competitor terms | Track important competitor targets |
| Strategic terms | Track board/product priorities even if volume is lower |
| Content investments | Track every major page you are actively improving |

Skip zero-volume terms unless strategic, terms with no target content, broad one-word terms, and low-volume misspellings.

## Grouping

| Dimension | Use |
|-----------|-----|
| Topic cluster | Hub performance |
| Intent | Funnel-stage performance |
| Product/service | Product-line performance |
| Content type | Format effectiveness |
| Priority tier | Resourcing |
| URL | Page-level diagnosis |
| Competitor overlap | Competitive monitoring |

Recommended hierarchy: `Business unit -> Topic cluster -> Intent -> Priority tier`.

## Frequency and Alerts

| Keyword Tier | Tracking Frequency | Drop Alert | Gain Alert | Competitor Alert |
|--------------|-------------------|------------|------------|------------------|
| Tier 1 revenue | Daily | Drop >=3 positions | Gain >=3 | Competitor enters top 5 |
| Tier 2 growth | 2-3x/week | Drop >=5 | Enters top 10 | Competitor overtakes |
| Tier 3 monitor | Weekly | Drop >=10 | Enters top 20 | None |
| Brand | Daily | Any drop from #1 | N/A | Competitor ranks for brand |
| New/experimental | Daily for 30 days | Drop >=5 | Enters top 20 | Optional |

| Alert Type | Channel | Frequency |
|------------|---------|-----------|
| Critical drops | Email + Slack | Immediate |
| Significant changes | Email | Daily digest |
| Weekly summary | Email | Monday |
| Monthly report | Email + dashboard | 1st of month |

## Reporting Cadence

| Report | Audience | Frequency | Focus |
|--------|----------|-----------|-------|
| Quick pulse | SEO team | Daily | Major movement, fired alerts |
| Weekly summary | Marketing | Weekly | Position changes, SERP features, AI citations |
| Monthly report | Stakeholders | Monthly | MoM distribution, SOV, GEO visibility, actions |
| Quarterly review | Leadership | Quarterly | QoQ trend, ROI, competitive shifts |

## Interpretation Rules

| Pattern | Meaning | Action |
|---------|---------|--------|
| Daily +/-1-2 positions | Normal volatility | Ignore; track weekly trend |
| Sudden drop 5+ and recovery in 2-3 days | Test/data-center variation | Monitor |
| Steady decline for 2+ weeks | Real loss | Investigate content, links, SERP, technical |
| Many keywords drop together | Algorithm or technical issue | Check Search Status, crawlability, indexation |
| One URL drops across terms | Page-level issue | Check noindex, 404, speed, content decay |
| Competitor surges | Market or content shift | Analyze their page and backlink changes |

| Position Change | Typical Traffic Impact |
|-----------------|------------------------|
| #1 -> #2 | -50% to -60% click loss |
| #2 -> #3 | -25% to -30% |
| #3 -> #5 | -30% to -40% |
| #5 -> #10 | -50% to -60% |
| #10 -> #11 | -60% to -80% page-2 cliff |

## Data Quality Checks

| Check | Frequency |
|-------|-----------|
| Manual spot-check 5-10 keywords | Weekly |
| Compare with Search Console | Monthly |
| Check position 0/tracking errors | Weekly |
| Verify competitor data manually | Monthly |
| Confirm location accuracy | Quarterly |

## Migration / Tool Switching

| Step | Action |
|------|--------|
| 1 | Export historical data |
| 2 | Run old and new tools in parallel for 2-4 weeks |
| 3 | Compare systematic differences |
| 4 | Import history if supported |
| 5 | Rebuild alerts and reports |
| 6 | Decommission old tool after confidence is established |

1-2 position variance between tools is normal. Document any systematic bias before comparing historical trends.
