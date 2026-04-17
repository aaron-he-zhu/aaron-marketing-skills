# Technical SEO — Pre-Migration Playbook

Referenced from [SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/SKILL.md). Use when the user is planning a migration (platform, domain, URL structure, or framework change) and needs an audit + risk assessment before the change ships.

---

## When to use

- WordPress → Headless (Next.js, Astro, Remix, Gatsby, etc.)
- Shopify → custom / BigCommerce / Magento
- Subdomain consolidation (blog.example.com → example.com/blog)
- Domain change (oldbrand.com → newbrand.com)
- URL structure rewrite (/category/product → /product)
- HTTP → HTTPS (rare now, still applicable on legacy sites)
- CMS upgrade that rewrites URLs (e.g., major theme refactor)

## The 6 pre-migration stages

### Stage 1 — Freeze current state (baseline snapshot)

Goal: capture the **current** SEO signals so you can diff after migration.

Capture in `memory/audits/pre-migration-YYYY-MM-DD.md`:

1. **URL inventory**
   - Full crawl via `~~web crawler` MCP or Screaming Frog / Sitebulb export
   - Canonical list of every indexable URL, with response code, canonical tag, redirect chain
   - Total indexable count

2. **Ranking baseline**
   - Top 100 ranking keywords (from `~~SEO tool` or `~~search console`)
   - For each: URL, position, volume, CTR, clicks last 90 days
   - Save as CSV: `memory/monitoring/pre-migration-ranks.csv`

3. **Traffic baseline**
   - Top 50 URLs by organic sessions (from `~~analytics` or `~~search console`)
   - Last 30 + 90-day session count per URL
   - Pages with >1% of total traffic flagged for VIP redirect review

4. **Backlink baseline**
   - Top 100 backlinks by referring domain authority (from `~~SEO tool`)
   - Top 50 linked URLs (on your site)
   - Flag any URL with 10+ backlinks as HIGH-VALUE — needs exact 301 after migration

5. **Schema & entity snapshot**
   - Current structured data (JSON-LD extracted from head) per page template
   - Entity representation (Organization, Person, Product, Article, etc.)

### Stage 2 — Risk map

For each proposed migration change, score risk:

| Change | Risk | Impact if mishandled |
|--------|------|---------------------|
| URL structure change | HIGH | traffic loss 20-40% for 2-12 weeks |
| Template rewrite (meta, headers) | HIGH | keyword targeting loss |
| Domain change | CRITICAL | full PageRank reset without redirects |
| Schema change | MEDIUM | rich result loss |
| JS-rendered content | MEDIUM | partial deindex if not SSR |
| robots.txt / noindex change | CRITICAL | accidental deindex |
| Internal link restructure | MEDIUM | topic cluster weakness |

Produce a **GO / NOGO** recommendation per change.

### Stage 3 — Redirect map

Before any URL changes, build a one-to-one redirect map:

```csv
old_url,new_url,reason,priority
/category/blue-shoes,/shop/blue-shoes,url structure,P0
/product/abc-123,/product/blue-shoe,slug change,P0
/blog/2020/seo-tips,/blog/seo-tips,year removed,P1
```

Rules:
- Every URL in the Stage 1 inventory MUST have a mapping or a documented decision to 410 / 404
- No chains (`A → B → C` must become `A → C` and `B → C`)
- No loops (never `A → B → A`)
- HIGH-VALUE URLs (Stage 1 flagged) verified manually

Save to `memory/audits/redirect-map-YYYY-MM-DD.csv`.

### Stage 4 — Staging QA

Before production cutover, QA the staging environment:

1. **Robots / indexing**: is `noindex` set on staging? Will it flip to `index` on launch? Any accidental `Disallow: /` in the production robots.txt draft?
2. **Template parity**: do new templates produce equivalent `<title>`, `<meta description>`, `<h1>`, canonical, schema for each page type?
3. **Internal linking**: run a crawl of staging; verify topic clusters intact; check for orphan pages introduced by the new template.
4. **Core Web Vitals**: run PSI / Lighthouse / WebPageTest on staging. LCP, INP, CLS per template. Compare to Stage 1 baseline.
5. **Schema validation**: validate every page-type template's JSON-LD with Schema.org validator and Google Rich Results Test.
6. **Pagination / facets**: if the site has collection pages, verify pagination canonical / facet canonical behavior matches or improves on the baseline.

### Stage 5 — Cutover day checklist

At launch:

1. Deploy redirects BEFORE touching DNS / robots (if possible)
2. Update `robots.txt` to production
3. Submit new `sitemap.xml` to Search Console and Bing Webmaster
4. Unblock crawling (remove any staging noindex)
5. Monitor: tail access logs for 5xx spikes, 404 spikes on old URLs
6. First-day rollback trigger: if 404 rate on old URLs exceeds 5% of old-URL traffic, immediately audit redirect map

### Stage 6 — Post-migration diff (T+1, T+7, T+30)

Run the same inventory as Stage 1 and diff:

- **T+1**: full crawl. Flag any URL that returns non-2xx when it should redirect.
- **T+7**: compare traffic per URL vs baseline. Flag URLs with >30% drop.
- **T+30**: compare rankings vs baseline for top 100 keywords. Flag URLs lost from top 10 / top 20.

Deliverables:

- `memory/audits/post-migration-T+1-YYYY-MM-DD.md`
- `memory/audits/post-migration-T+7-YYYY-MM-DD.md`
- `memory/audits/post-migration-T+30-YYYY-MM-DD.md`

## Handoff

- **Status**: DONE | DONE_WITH_CONCERNS | BLOCKED
- **Objective**: "Pre-migration audit for <change_description>"
- **Key Findings / Output**: baseline snapshot refs + risk map + redirect map + QA checklist
- **Evidence**: crawl counts, ranking CSV path, redirect CSV path, Core Web Vitals before/after (if staging ready)
- **Open Loops**: HIGH-VALUE URLs pending redirect confirmation, schema not validated for templates X/Y, rollback trigger thresholds not yet agreed with engineering
- **Recommended Next Skill**: `content-refresher` if template rewrite surfaced content-quality gaps; `schema-markup-generator` if new templates need schema authored; otherwise `rank-tracker` for post-launch monitoring

## Red-flag patterns (STOP — do not ship until fixed)

- Any redirect chain >1 hop
- Missing 301 on a URL with >100 monthly organic sessions
- `robots.txt` has `Disallow: /` anywhere in production draft
- Canonical tag on new URL points back to old URL
- JS-only content with no SSR fallback on key landing pages
- New template omits `<h1>` or has multiple `<h1>`
- Schema type changed without rich-result eligibility check
