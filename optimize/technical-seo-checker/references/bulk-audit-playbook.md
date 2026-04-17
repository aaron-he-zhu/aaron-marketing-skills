# Technical SEO — Site-Wide / Bulk Audit Playbook

Referenced from [SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/SKILL.md). Use this when the user has >5 URLs to audit (e.g., all 50 Shopify product pages are not indexed).

---

## When to use bulk mode

- User reports "X of Y pages are not indexed" (ratio problem)
- User pastes a sitemap URL or a CSV/list of URLs
- User references GSC Coverage / Indexing report exports
- E-commerce sites with facet / pagination / variant patterns

## Inputs accepted

Bulk mode accepts **any one** of the following:

1. **Sitemap URL** — `https://example.com/sitemap.xml` (or `sitemap_index.xml`)
2. **GSC Coverage export** — CSV from Search Console with columns `URL | Issue | Last crawled`
3. **URL list** — plain text, one URL per line (user paste)
4. **Crawl data** — Screaming Frog export, Sitebulb export, or `~~web crawler` MCP output

## Workflow

### Step 1 — Inventory + group

Parse input into a URL inventory. Group by pattern:

- Content type: product page / category / blog / legal / tool
- Template: detected via URL path, meta signals, or sampling 3 pages per cluster
- Known issue from input (if GSC): indexed / excluded / crawl error / duplicate without user-selected canonical / soft 404

Output a table like:

```
| Group              | Count | Template | Known Issue        |
|--------------------|-------|----------|--------------------|
| /product/[slug]    | 32    | product  | Excluded by noindex |
| /collection/[slug] | 12    | category | Duplicate canonical |
| /blog/[slug]       | 4     | blog     | OK                  |
| /pages/[slug]      | 2     | landing  | OK                  |
```

### Step 2 — Sample deep, summarize shallow

Run the single-URL audit flow on **2 representative URLs per group** (the most and least recently indexed). Report pattern-level findings instead of per-URL findings.

**Output shape**:

```
### Group: /product/[slug] — 32 pages
- **Pattern issue**: `<meta name="robots" content="noindex">` injected by theme on all product pages with <5 variants
- **Root cause**: Shopify theme setting "Hide products with low stock"
- **Verified on**: /product/shoes-red, /product/shoes-blue (2/32 sampled)
- **Estimated affected**: 32 pages
- **Fix**: disable the theme option OR add `variant_count > 0` override in theme.liquid L247
- **Priority**: P0
```

### Step 3 — Portfolio-level prioritization

Produce a single prioritized list across all groups, not per-page:

```
P0 (fix affects 10+ pages):
1. Remove noindex from low-stock products (32 pages)  — theme.liquid
2. Fix canonical conflict on collection pages (12 pages)  — collection.liquid

P1 (fix affects 3-9 pages):
3. Add self-referential canonical on /blog/* (4 pages)

P2 (single-page):
4. /pages/about has meta description length 170 chars — trim
```

### Step 4 — Deliver

**Handoff Summary** adapts to bulk mode:

- **Status**: DONE | DONE_WITH_CONCERNS
- **Objective**: "Bulk audit of <inventory_size> URLs across <group_count> groups"
- **Key Findings / Output**: pattern-level issues + portfolio priority list
- **Evidence**: "Sampled N of M pages (deep audit); inferred group issues from URL structure + meta signals"
- **Open Loops**: un-sampled groups; access blockers; data freshness caveats
- **Recommended Next Skill**: `content-refresher` (if content issues dominate) OR `schema-markup-generator` (if structured data issues)

## Minimum viable bulk input

If user has none of the above:

```
Paste or describe your site's URL patterns:

1. Domain: [example.com]
2. How many total pages roughly? [50 / 500 / 5000]
3. Page types with approximate counts:
   - Products: [~32]
   - Categories: [~12]
   - Blog posts: [~4]
   - Pages: [~2]
4. What issue started the audit? (e.g., "40 of 50 products not indexed")
5. Any template/theme you know the issue is scoped to?
```

Then proceed from Step 1 with the user-provided inventory.

## E-commerce pattern reference

Common bulk-level issues and their usual fix locations:

| Symptom | Usual root cause | Check file |
|---------|------------------|-----------|
| Variants not indexed | Canonical pointing to parent | `product.liquid` |
| Facet/filter URLs indexed | Missing `rel="noindex,follow"` on filter links | `collection.liquid` |
| Duplicate pages on `?utm=*` | No canonical to clean URL | `theme.liquid` head |
| Old products return 404 | No 301 redirect after removal | platform redirect map |
| Pagination loop | `rel="prev/next"` wrong or missing self-canonical per page | `collection.liquid` |
| Robots.txt blocks all facets (aggressive) | `Disallow: /*?*` too broad | `/robots.txt` |
