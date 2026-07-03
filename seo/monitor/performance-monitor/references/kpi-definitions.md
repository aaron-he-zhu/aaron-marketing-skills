# SEO/GEO KPI Definitions

Use these definitions when building recurring performance reports. Always show source, date range, comparison period, and whether the metric is brand, non-brand, or blended.

## KPI Matrix

| Category | KPI | Formula / source | Good | Warning / action trigger |
|----------|-----|------------------|------|--------------------------|
| Organic search | Organic sessions | Count sessions where medium = `organic`; analytics platform | Growing MoM; 3-10% MoM is healthy | Decline >10% MoM without seasonal cause; split brand vs non-brand |
| Organic search | Organic CTR | Organic clicks / impressions x 100; Search Console | >3% overall | <1.5% or declining; stable position + low CTR means title/meta issue |
| Organic search | Average position | Sum of positions / keyword count; Search Console or SEO tool | <20 for tracked keywords; improving | >30 or worsening; pair with top 10/top 20 distribution |
| Organic search | Keyword visibility | Sum of estimated CTR at position x monthly volume | Growing | Declining 3+ consecutive weeks |
| Organic search | Pages indexed | Valid indexed pages in Search Console | Close to intended indexable pages | Drop without intent; submitted/indexed gap; indexed > intended |
| Organic search | Organic CVR | Organic conversions / organic sessions x 100 | >2% lead gen; >1% e-commerce | <0.5% or declining while traffic grows |
| Organic search | Non-brand share | Non-brand organic sessions / total organic sessions x 100 | >50% | <30%, indicating brand dependency |
| GEO / AI | AI citation rate | Cited queries / monitored AI-answer queries x 100 | >20% | <5% or declining |
| GEO / AI | AI citation position | Sum citation positions / citation count | Top 3 average | Not cited or consistently 5+ |
| GEO / AI | AI answer coverage | Topics with AI answers / target topics x 100 | Growing | Declining coverage |
| GEO / AI | Brand mention in AI | AI responses containing brand name | Growing for authority topics | Zero mentions on priority topics |
| Authority | Domain Rating / Authority | Tool-specific 0-100 logarithmic link score | Growing and competitive | Flat while competitors grow |
| Authority | Referring domains | Distinct root domains linking | Growing MoM | Net loss for 2+ months |
| Authority | Backlink growth rate | New backlinks - lost backlinks | Positive and steady | Negative 2+ months or spam-like spike |
| Authority | Toxic link ratio | Toxic backlinks / total backlinks x 100 | <5% | 5-10% warning; >10% critical, review before disavow |
| Technical | Crawl budget utilization | Useful pages crawled / total pages crawled x 100 | >80% useful/indexable | High crawl of non-indexable or low-value pages |
| Technical | Index coverage rate | Indexed pages / submitted pages x 100 | >90% for curated sitemap | <80% or declining |
| Content | Content efficiency | Organic sessions per piece / cost per piece | Improving | Flat or declining after refresh window |
| Content | Content decay rate | Pages with >20% traffic decline over 6 months / pages with traffic | <20% | >30% |
| Business | Organic revenue/session | Organic revenue / organic sessions | Stable or growing | Declining while traffic grows |
| Competitive | Share of voice | Your visibility / total competitor visibility x 100 | Growing in core topics | Declining 3+ consecutive months |
| Competitive | Keyword overlap | Shared top-20 keywords / your tracked keywords x 100 | Expected for direct competitors | New high-overlap competitor = emerging threat |
| ROI | SEO ROI | (Organic revenue - SEO investment) / investment x 100 | >200% annually | <100% after 12+ months |
| ROI | Organic traffic value | Sum monthly organic clicks x CPC | Growing; exceeds SEO investment | Value compression or shrinking gap vs spend |

## Benchmarks

### CTR by Position

| Position | Typical CTR |
|----------|-------------|
| #1 | 25-35% |
| #2 | 12-18% |
| #3 | 8-13% |
| #4-5 | 4-8% |
| #6-10 | 2-5% |
| #11-20 | 0.5-2% |

### Organic Conversion Rate by Industry

| Industry | Typical range |
|----------|---------------|
| SaaS | 2-5% |
| E-commerce | 1-3% |
| Finance | 3-6% |
| Healthcare | 2-4% |
| B2B services | 2-5% |
| Media | 0.5-2% |

### Domain Authority Maturity

| Stage | Typical range |
|-------|---------------|
| New, 0-6 months | 0-15 |
| Early growth, 6-18 months | 15-30 |
| Established, 18-36 months | 25-50 |
| Mature, 3+ years | 40-70+ |
| Industry leader | 70-90+ |

### Core Web Vitals

| Metric | Good | Needs improvement | Poor |
|--------|------|-------------------|------|
| LCP | <=2.5s | 2.5-4.0s | >4.0s |
| CLS | <=0.1 | 0.1-0.25 | >0.25 |
| INP | <=200ms | 200-500ms | >500ms |

## Summary Tables

| Organic metric | Good | Warning | Source |
|----------------|------|---------|--------|
| Organic sessions | Growing MoM | >10% decline | Analytics |
| Keyword visibility | >60% in top 100 | <40% | SEO tool |
| Average position | <20 | >30 | Search Console |
| Organic CTR | >3% | <1.5% | Search Console |
| Pages indexed | Near intended indexable set | Dropping/gap | Search Console |
| Organic CVR | >2% lead gen | <0.5% | Analytics |
| Non-brand share | >50% | <30% | Analytics |

| GEO metric | Good | Warning | Source |
|------------|------|---------|--------|
| AI citation rate | >20% | <5% | AI monitor |
| AI citation position | Top 3 | Not cited / 5+ | AI monitor |
| AI answer coverage | Growing | Declining | AI monitor |
| Brand mention in AI | Growing | Zero | AI monitor |

## Trend Interpretation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Steady growth | Strategy working | Continue; optimize high performers |
| Sudden spike then drop | Viral content or algorithm volatility | Investigate source; replicate only if durable |
| Gradual decline | Content decay, competition, technical debt | Run content + technical audit |
| Flat line | Plateau | Expand topics, links, or formats |
| Seasonal pattern | Demand cycle | Compare YoY and plan calendar around peaks |

## Period Comparison Guide

| Comparison | Best for | Limitation |
|------------|----------|------------|
| WoW | Sudden changes | Noisy; weekday effects |
| MoM | Operating trends | Seasonal bias |
| YoY | Seasonality control | Can hide recent trajectory |
| Rolling 30-day | Noise smoothing | Lags real changes |

## Interpretation Notes

- Segment brand vs non-brand before drawing SEO conclusions.
- Pair position with CTR and SERP-feature context; AI Overview/PAA can steal clicks.
- Treat average position as directional, not a standalone success metric.
- Measure ROI over 12+ months because SEO compounds.
- Document every benchmark source and date in the report.
