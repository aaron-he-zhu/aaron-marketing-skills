# Link Quality Rubric

Use this reference to score individual backlinks, audit link profiles, find competitive link gaps, and prepare disavow files without mistaking weak links for toxic links.

## 1. Individual Link Quality Score

Score each link across six factors, multiply by weight, then sum the weighted values for the final **Link Quality Score (LQS)**. Use scores 4 and 2 for cases between the table anchors.

| Factor | Weight | Score 5 | Score 3 | Score 1 | Guardrail |
|--------|--------|---------|---------|---------|-----------|
| Domain Authority | 25% | DR/DA 70+, established authority | DR/DA 30-49, credible niche site | DR/DA <15 or thin/abandoned | DR/DA is a proxy; relevance can beat raw authority. Check for inflated authority from bought links/PBNs. |
| Topical Relevance | 25% | Same niche and subtopic | Same broad field | Unrelated topic | Read the page, site focus, surrounding copy, and outbound-link pattern before scoring. |
| Linking Page Traffic | 15% | 10,000+ visits/mo | 100-999 visits/mo | <10 visits/mo | Real traffic suggests editorial value and referral upside. |
| Link Position | 15% | In-content editorial citation | Author bio/about section | Footer, sitewide, hidden, or template link | Editorial body links carry the most value. |
| Anchor Text | 10% | Descriptive, natural | Brand name | Generic | A single natural descriptive anchor can score high; a profile overloaded with exact-match anchors is risky. |
| Follow Status | 10% | Dofollow editorial | Sponsored/UGC disclosed | Nofollow | Nofollow is a hint, not zero value; high-authority nofollow links can still help brand/referral visibility. |

**Rating scale**

| LQS | Rating | Meaning |
|-----|--------|---------|
| 4.0-5.0 | Premium | High authority, relevant, editorial placement |
| 2.5-3.9 | Acceptable | Provides value and fits a healthy profile |
| 1.0-2.4 | Low quality | Minimal value; review for risk before acting |

**Healthy anchor/follow distribution**

| Signal | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Brand anchors | 30-40% | <15% | <5% |
| Naked URLs | 15-25% | <10% | <5% |
| Generic anchors | 10-20% | <5% | 0% |
| Descriptive/partial match | 15-25% | >35% | >50% |
| Exact match | 5-15% | 15-25% | >25% |
| Dofollow ratio | 60-80% | >90% | >95% |

## 2. Link Profile Calibration

Use these archetypes to interpret thresholds by site maturity.

| Profile | Healthy Signals | Risk Signals | Verdict |
|---------|-----------------|--------------|---------|
| Strong mid-size SaaS | 1,200 referring domains, 72% dofollow, avg DR 38, 35% brand anchors, 8% exact match, 3% toxic estimate | None material | Continue current strategy. |
| At-risk competitive niche | 800 referring domains, 92% dofollow, avg DR 18, 42% exact match, 30% topical relevance, 18% toxic estimate | Over-optimized anchors, low relevance, unnatural velocity | Review toxic links, diversify anchors, slow acquisition. |
| Healthy new site | 45 referring domains, 65% dofollow, avg DR 28, 40% brand anchors, 5% exact match, +8/month velocity | Low volume only | Do not judge by mature-site volume; scale carefully while preserving quality. |

## 3. Competitive Link Gap Analysis

| Step | Action | Output |
|------|--------|--------|
| 1 | Select 3-5 direct competitors ranking for target keywords | Competitor set |
| 2 | Export referring domains from ~~link database | Competitor link lists |
| 3 | Build an intersection matrix: domain, you, comp 1/2/3, overlap count | Shared opportunity map |
| 4 | Prioritize by overlap, DR, and topical relevance | Outreach priority list |
| 5 | Visit each high-priority linking page | Link context and outreach angle |
| 6 | Create outreach plan | Contact, angle, target asset, template |

**Opportunity priority**

| Priority | Criteria | Rationale |
|----------|----------|-----------|
| Highest | Links to 3+ competitors, DR 50+, relevant | Strong market signal and likely linkability |
| High | Links to 2+ competitors, DR 30+, relevant | Proven niche linker |
| Medium | Links to 1 competitor, DR 50+, relevant | High value but less proven access |
| Lower | DR <30, low relevance, or one-off competitor link | Diminishing return unless strategically useful |

## 4. Disavow File Safety Guide

Only disavow links when there is clear evidence of risk. Unnecessary disavow can hurt rankings.

| Situation | Disavow? | Reasoning |
|-----------|----------|-----------|
| Obvious PBN links | Yes | Clear manipulation signal |
| Paid links you cannot get removed | Yes | Only after attempting removal |
| Spam attack / negative SEO | Yes | Protect against third-party manipulation |
| Foreign-language spam | Yes | If clearly unnatural and irrelevant |
| Low-quality directory links | Maybe | Only if pattern is excessive |
| Low-DA sites with real content | No | Low quality is not automatically toxic |
| Nofollow links | No | Already nofollowed; usually no risk |

**Review workflow before upload**

| Step | Action | Required safeguard |
|------|--------|--------------------|
| 1 | Export full backlink profile | Keep raw export beside the audit |
| 2 | Filter known toxic patterns | Spam score, DR <10, foreign spam, PBN footprints |
| 3 | Manually review flagged domains | Visit each domain; do not rely only on metrics |
| 4 | Attempt removal first | Email webmasters where possible |
| 5 | Wait 2 weeks | Track outreach responses |
| 6 | Add only non-removed toxic links | Use comments and reasons |
| 7 | Upload to Google Search Console | Back up previous file first |
| 8 | Document all actions | Keep dates, reasons, and owner |
| 9 | Re-check in 4-6 weeks | Verify processing and recovery signals |

**File format**

```txt
# Disavow file for [domain]
# Generated: [date]
# Reason: [toxic link cleanup / negative SEO / paid links not removable]

# Individual URLs when only one page is toxic
https://spam-site.example/toxic-page

# Entire domains only when multiple pages are toxic
domain:pbn-network.example
domain:spam-directory.example
```

**Best practices**

| Practice | Why |
|----------|-----|
| Comment every entry or group | Future auditors need the reason |
| Use `domain:` for repeated toxic domains | Captures sitewide spam patterns |
| Use individual URLs for isolated pages | Avoids disavowing good links from the same domain |
| Never disavow your own domain | Severe self-inflicted damage |
| Keep changelog and backup | Enables rollback and accountability |
| Review quarterly | Remove entries if domains are cleaned up |

## 5. Link Profile Health Benchmarks

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Toxic link estimate | <5% | 5-10% | >10% |
| Referring domain growth | Positive, steady | Flat | Declining |
| Average linking DR | 25+ | 15-25 | <15 |
| Link diversity (unique domains / total links) | >0.3 | 0.1-0.3 | <0.1 |
| Topical relevance sample | >60% | 40-60% | <40% |

Authority expectations vary by vertical:

| Industry | Typical DR Range (Top 10) | Typical Referring Domains | Link Difficulty |
|----------|---------------------------|---------------------------|-----------------|
| Finance / Insurance | 60-90 | 5,000-50,000+ | Very High |
| Health / Medical | 50-85 | 3,000-30,000+ | Very High |
| Technology / SaaS | 40-80 | 1,000-20,000+ | High |
| E-commerce | 35-75 | 500-15,000+ | High |
| Legal | 40-70 | 1,000-10,000+ | High |
| Education | 50-90 | 2,000-25,000+ | Medium-High |
| Local services | 15-45 | 50-500 | Medium |
| B2B niche | 25-60 | 200-5,000+ | Medium |
| New startup | 5-25 | 10-200 | Starting point |

Use industry ranges as context, not hard pass/fail rules. Keyword competition and topical relevance decide the real bar.
