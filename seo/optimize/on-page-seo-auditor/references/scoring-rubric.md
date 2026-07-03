# On-Page SEO Scoring Rubric

Score each section independently, apply the weight, and report an overall score out of 100.

## Weighted Scorecard

| Section | Weight | Max | Required checks |
|---------|--------|-----|-----------------|
| Title tag | 15% | 15 | Primary keyword present and in first half; 50-60 chars; unique; compelling benefit/modifier; intent match; brand at end when useful; low truncation risk. |
| Meta description | 5% | 5 | Keyword appears naturally; 150-160 chars; CTA; unique; accurate page summary. |
| Header structure | 10% | 10 | Exactly one H1; H1 contains keyword; H1->H2->H3 hierarchy; H2s cover key facets; headers descriptive; variations in subheads. |
| Content quality | 25% | 25 | Query-appropriate length; comprehensive coverage; unique value; current stats/dates/references; readable formatting; audience-appropriate reading level; E-E-A-T signals. |
| Keyword optimization | 15% | 15 | Keyword in title, H1, first 100 words, URL, image alt, and meta; 2-3 secondary terms; semantic/LSI terms; natural density. |
| Internal/external links | 10% | 10 | 3-5+ contextual internal links per 1,000 words; relevant destinations; descriptive anchors; authoritative external sources; no broken links; natural placement. |
| Image optimization | 10% | 10 | Descriptive filenames; optimized file sizes; WebP/AVIF/SVG where appropriate; lazy loading below fold; accessible alt text. |
| Page-level technical | 10% | 10 | Clean URL; correct canonical; mobile-friendly; mobile LCP <=2.5s; HTTPS valid; appropriate schema. |

## Benchmarks

### Content Length by Query Type

| Query type | Full points | Partial | Poor |
|------------|-------------|---------|------|
| Informational | 1,500+ words | 500-1,499 | <500 |
| Commercial | 1,200+ | 400-1,199 | <400 |
| Transactional | 500+ | 200-499 | <200 |
| Local | 400+ | 150-399 | <150 |
| Definition | 800+ recommended | 300-799 | <300 |

### Keyword Density

| Density | Score impact |
|---------|--------------|
| 0.5-2.0% | Full points |
| 2.0-2.5% | -1 point |
| 2.5-3.0% | -2 points |
| >3.0% | 0 points for density; flag stuffing |
| <0.5% | -1 point unless query does not need repetition |

### Internal Link Count

| Content length | Minimum | Ideal | Too many |
|----------------|---------|-------|----------|
| <500 words | 2 | 2-4 | >8 |
| 500-1,000 | 3 | 3-6 | >12 |
| 1,000-2,000 | 4 | 5-10 | >20 |
| 2,000+ | 5 | 8-15 | >25 |

### Image Size Targets

| Image type | Target size | Format |
|------------|-------------|--------|
| Hero/banner | <200KB | WebP |
| Content photos | <150KB | WebP |
| Screenshots | <100KB | WebP/PNG |
| Icons/graphics | <30KB | SVG/WebP |
| Thumbnails | <50KB | WebP |

### Page Speed

| Metric | Good | Needs improvement | Poor |
|--------|------|-------------------|------|
| LCP | <=2.5s | 2.5-4.0s | >4.0s |
| INP | <=200ms | 200-500ms | >500ms |
| CLS | <=0.1 | 0.1-0.25 | >0.25 |
| TTFB | <=800ms | 800-1800ms | >1800ms |

## Accessibility Overlay

Flag WCAG 2.2 AA failures as **HIGH priority** because they affect users, legal risk, and search quality signals.

| WCAG criterion | Check |
|----------------|-------|
| 1.1.1 Non-text content | Content images have functional alt text; decorative images are empty alt. |
| 1.3.1 Info and relationships | Headings are nested logically; no empty headings. |
| 1.4.3 Contrast minimum | Normal text >=4.5:1; large text >=3:1. |
| 2.4.7 Focus visible | Keyboard focus indicator visible on interactive elements. |
| 4.1.2 Name, role, value | Custom controls and form fields expose accessible names. |

## Score Calculation

```text
Overall Score = Sum(Section Score / Section Max * Section Weight * 100)
```

| Score range | Grade | Assessment |
|-------------|-------|------------|
| 90-100 | A+ | Exceptional; minor tweaks only |
| 80-89 | A | Strong; a few optimization opportunities |
| 70-79 | B | Good; several areas need attention |
| 60-69 | C | Average; significant improvements needed |
| 50-59 | D | Below average; major issues present |
| <50 | F | Poor; comprehensive overhaul required |

| Section percentage | Meaning | Action |
|--------------------|---------|--------|
| 90-100% | Excellent | None |
| 70-89% | Good | Optional optimization |
| 40-69% | Needs work | Fix within this week |
| 1-39% | Poor | Fix immediately |
| 0% | Missing/broken | Blocking fix |

## Resolution Playbook

| Issue | Impact | Quick fix |
|-------|--------|-----------|
| Missing title | Critical | `[Primary Keyword]: [Benefit] | [Brand]` |
| Title >60 chars | Medium | Remove filler, move brand to end, keep keyword early |
| Duplicate title | High | Add page-specific modifier |
| Missing meta description | Medium | `[What page covers]. [Key benefit]. [CTA].` |
| Missing H1 | Critical | Add one H1 with primary keyword |
| Multiple H1s | High | Keep one H1, convert others to H2 |
| Skipped headings | Medium | Restore sequential H1->H2->H3 hierarchy |
| Thin content | Critical | Expand with subtopics, FAQ, examples, and evidence |
| Keyword stuffing >3% | High | Reduce exact matches, add synonyms/entities |
| Missing internal links | Medium | Add 3-5 contextual internal links |
| Broken links | High | Replace, redirect, or remove |
| Missing descriptive alt | High | Add functional alt text; avoid keyword lists |
| No schema on eligible page | Medium | Add Article, FAQPage, HowTo, Product, or LocalBusiness as appropriate |

## Weight Adjustments

| Page type | Increase weight | Decrease weight |
|-----------|-----------------|-----------------|
| E-commerce product | Image optimization, technical, schema | Long-form content depth |
| Long-form guide | Content quality, keywords, links | Image optimization |
| Landing page | Technical, title/meta, CTA clarity | Exhaustive content depth |
| Local service page | Technical, local schema, links | Keyword density |

Document any weight change and its reasoning in the audit report.
