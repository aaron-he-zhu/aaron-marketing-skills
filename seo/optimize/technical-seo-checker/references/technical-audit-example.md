# Technical SEO Checker Worked Example and Checklist

Referenced from [SKILL.md](../SKILL.md). Use as a compact output model, not as fixed data.

## Worked Example Shape

```markdown
# Technical SEO Audit Report

**Domain**: [domain]
**Audit date**: [date]
**Pages analyzed**: [count]

## Crawlability

### robots.txt
| Check | Status | Evidence | Fix |
|-------|--------|----------|-----|
| File exists | [pass/warn/fail] | [status code] | [fix] |
| Valid syntax | [pass/warn/fail] | [rule] | [fix] |
| Sitemap directive | [pass/warn/fail] | [sitemap URL or missing] | Add `Sitemap: [absolute URL]` |
| Important pages blocked | [pass/warn/fail] | [blocked URL/rule] | [allow or revise rule] |
| Assets accessible | [pass/warn/fail] | [CSS/JS sample] | [fix] |

### XML sitemap
| Check | Status | Evidence | Fix |
|-------|--------|----------|-----|
| Sitemap exists | [pass/warn/fail] | [URL count] | [fix] |
| Only indexable URLs | [pass/warn/fail] | [noindex/canonical/redirect count] | Remove non-indexable URLs |
| lastmod accuracy | [pass/warn/fail] | [sample dates] | Update only when page content changes |
| Declared in robots.txt | [pass/warn/fail] | [yes/no] | Add sitemap directive |

**Crawlability score**: [X]/10

## Performance

| Metric | Mobile | Desktop | Target | Status |
|--------|--------|---------|--------|--------|
| LCP | [value] | [value] | <=2.5s | [status] |
| INP | [value] | [value] | <=200ms | [status] |
| CLS | [value] | [value] | <=0.1 | [status] |
| TTFB | [value] | [value] | <=800ms preferred | [status] |

**Top fixes**:
- [largest LCP/TTFB/render-blocking issue + estimated impact]
- [largest CLS issue + fix]

## Security

| Check | Status | Evidence | Fix |
|-------|--------|----------|-----|
| SSL certificate valid | [pass/warn/fail] | [expiry/source] | [fix] |
| HTTPS enforced | [pass/warn/fail] | [HTTP response behavior] | 301 HTTP to HTTPS |
| Mixed content | [pass/warn/fail] | [affected assets/pages] | Replace with HTTPS URLs |
| HSTS enabled | [pass/warn/fail] | [header value/missing] | Add appropriate HSTS header after HTTPS is stable |

## Structured Data

| Schema type | Pages | Valid | Errors / missing opportunities |
|-------------|-------|-------|--------------------------------|
| Organization | [count] | [yes/no] | [issues] |
| Article / BlogPosting | [count] | [yes/no] | [missing blog pages] |
| Product / Offer | [count] | [yes/no] | [missing commercial pages] |
| FAQPage | [count] | [yes/no] | [visible FAQ pages without schema] |

## Overall Technical Health: [X]/100

| Area | Score |
|------|-------|
| Crawlability | [X]/10 |
| Indexability | [X]/10 |
| Performance | [X]/10 |
| Mobile | [X]/10 |
| Security | [X]/10 |
| URL structure | [X]/10 |
| Structured data | [X]/10 |

## Priority Issues

### Critical
1. **[Issue]** — [evidence, affected URLs, fix, expected impact]

### Important
2. **[Issue]** — [evidence, affected URLs, fix]

### Minor
3. **[Issue]** — [optimization path]
```

## Technical SEO Checklist

| Area | Checks |
|------|--------|
| Crawlability | `robots.txt` valid; XML sitemap exists/submitted; no crawl errors; no redirect chains or loops; no important assets blocked |
| Indexability | Important pages indexable; canonical tags correct; no duplicate content issues; pagination handled correctly |
| Performance | Core Web Vitals pass; page speed under 3s where practical; images optimized; JS/CSS minimized and non-blocking where possible |
| Mobile | Mobile-friendly layout; viewport configured; touch targets usable |
| Security | HTTPS enforced; SSL valid; no mixed content; HSTS/security headers reviewed |
| Structure | URLs clean/descriptive; architecture logical; internal linking supports priority pages |
| Structured data | Relevant schema implemented; required fields present; visible content matches markup |

## Reporting Rules

- Use placeholders for domain/date/page counts in examples; never ship sample values as audit facts.
- Include current evidence for every failed or warning row.
- Keep robots.txt, sitemap, lastmod, HSTS, INP, and structured-data opportunities explicit.
- Prioritize by business impact: blocked commercial pages and failed Core Web Vitals outrank minor enhancements.
