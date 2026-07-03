# HTTP Status Codes for Technical SEO

Use this as the technical audit decision table. Always cite sample URLs, response headers, and crawl date.

## Decision Matrix

| Code | SEO Meaning | Action |
|------|-------------|--------|
| 200 | Indexable response if canonical/noindex allow it | Keep; verify content, canonical, and cache headers |
| 204 | No content | Avoid for indexable URLs |
| 301 | Permanent redirect | Use for canonical migrations; keep one hop |
| 302/307 | Temporary redirect | Use only for temporary tests/campaigns |
| 304 | Not modified | Fine for caching; not a page status for indexing decisions |
| 400 | Bad request | Fix malformed links/parameters |
| 401/403 | Blocked/auth | Ensure private sections only; avoid blocking public resources |
| 404 | Missing URL | OK for removed pages; fix internal links and sitemap entries |
| 410 | Gone | Use for intentionally removed content |
| 429 | Rate limited | Check bot handling and crawl budget |
| 500 | Server error | P0 if affecting indexable pages |
| 502/503/504 | Gateway/availability issue | P0/P1; monitor uptime and origin/CDN |

## Redirect Rules

| Check | Good | Risk |
|-------|------|------|
| Hop count | 0-1 | 2+ chains waste crawl budget |
| Target | relevant equivalent URL | soft 404, homepage dumping, wrong locale |
| Method | 301 for permanent, 302/307 temporary | mixed signals after migration |
| Canonical | final URL self-canonical | canonical points to old URL |

## Error Handling

| Pattern | Fix |
|---------|-----|
| 404 in sitemap | Remove or redirect to equivalent page |
| Internal links to 404/410 | Update links to live equivalents |
| 5xx on important templates | Escalate hosting/app issue; retest after fix |
| Blocked CSS/JS | Unblock required resources; retest render |
| Soft 404 | Add useful content or return true 404/410 |

## Core Web Vitals Quick Reference

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | <=2.5s | 2.5-4s | >4s |
| INP | <=200ms | 200-500ms | >500ms |
| CLS | <=0.1 | 0.1-0.25 | >0.25 |
| TTFB | <=800ms | 800-1800ms | >1800ms |

## Priority Mapping

P0: 5xx on money/index pages, accidental noindex/canonical/robots block, migration redirect failure. P1: redirect chains, many 404s from internal links, poor CWV on key templates. P2: stale headers, minor 404s, noncritical cache issues.

## Report Fields

Status code, affected URL/pattern, count, first seen date, source, canonical/indexability impact, recommended fix, owner, retest date.
