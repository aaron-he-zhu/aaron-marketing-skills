# Schema Markup Generator — Detailed Instructions

Full workflow templates, CORE-EEAT schema mapping, rich result eligibility, implementation guide, full FAQ example, schema quick reference, and tips for the Schema Markup Generator skill.

---

## Step-by-Step Workflow

### 1. Identify Content Type and Rich Result Opportunity

Reference the [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md) item **O05 (Schema Markup)** for content-type to schema mapping:

```markdown
### CORE-EEAT Schema Mapping (O05)

| Content Type | Required Schema | Conditional Schema |
|-------------|----------------|--------------------|
| Blog (guides) | Article, Breadcrumb | FAQ, HowTo |
| Blog (tools) | Article, Breadcrumb | FAQ, Review |
| Blog (insights) | Article, Breadcrumb | FAQ |
| Alternative | Comparison*, Breadcrumb, FAQ | AggregateRating |
| Best-of | ItemList, Breadcrumb, FAQ | AggregateRating per tool |
| Use-case | WebPage, Breadcrumb, FAQ | — |
| FAQ | FAQPage, Breadcrumb | — |
| Landing | SoftwareApplication, Breadcrumb, FAQ | WebPage |
| Testimonial | Review, Breadcrumb | FAQ, Person |

*Use the mapping above to ensure schema type matches content type (CORE-EEAT O05: Pass criteria).*
```

```markdown
### Schema Analysis

**Content Type**: [blog/product/FAQ/how-to/local business/etc.]
**Page URL**: [URL]

**Eligible Rich Results**:

| Rich Result Type | Eligibility | Impact |
|------------------|-------------|--------|
| FAQ | Yes/No | High - Expands SERP presence |
| How-To | Yes/No | Medium - Shows steps in SERP |
| Product | Yes/No | High - Shows price, availability |
| Review | Yes/No | High - Shows star ratings |
| Article | Yes/No | Medium - Shows publish date, author |
| Breadcrumb | Yes/No | Medium - Shows navigation path |
| Video | Yes/No | High - Shows video thumbnail |

**Recommended Schema Types**:
1. [Primary schema type] - [reason]
2. [Secondary schema type] - [reason]
```

### 2. Generate Schema Markup

Based on the identified content type, generate the appropriate JSON-LD schema. Supported types: FAQPage, HowTo, Article/BlogPosting/NewsArticle, Product, LocalBusiness, Organization, BreadcrumbList, Event, Recipe, and combined multi-type schemas.

> **Reference**: See [references/schema-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/schema-markup-generator/references/schema-templates.md) for complete, copy-ready JSON-LD templates for all schema types with required and optional properties.

For each schema generated, include:
- All required properties for the chosen type
- Rich result preview showing expected SERP appearance
- Notes on which properties are required vs. optional

When combining multiple schema types on one page, wrap them in a JSON array inside a single `<script type="application/ld+json">` tag.

### 3. Provide Implementation and Validation

```markdown
## Implementation Guide

### Adding Schema to Your Page

**Option 1: In HTML <head>**
```html
<head>
  <script type="application/ld+json">
    [Your JSON-LD schema here]
  </script>
</head>
```

**Option 2: Before closing </body>**
```html
  <script type="application/ld+json">
    [Your JSON-LD schema here]
  </script>
</body>
```

### Validation Steps

1. **~~schema validator**
   - Test your live URL or paste code
   - Check for errors and warnings

2. **Schema.org Validator**
   - URL: https://validator.schema.org/
   - Validates against Schema.org spec

3. **~~search console**
   - Monitor rich results in ~~search console
   - Check Enhancements reports for issues

### Validation Checklist

- [ ] JSON syntax is valid (no trailing commas)
- [ ] All required properties present
- [ ] URLs are absolute, not relative
- [ ] Dates are in ISO 8601 format
- [ ] Content matches visible page content
- [ ] No policy violations
```

---

## Example: FAQ Schema for SEO Page

**User**: "Generate FAQ schema for a page about SEO with 3 questions"

**Output**:

```markdown
## FAQ Schema for SEO Page

### Schema Markup

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is SEO?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SEO (Search Engine Optimization) is the practice of optimizing websites and content to rank higher in search engine results pages (SERPs). It involves technical optimizations, content creation, and link building to increase organic visibility and drive qualified traffic to your website."
      }
    },
    {
      "@type": "Question",
      "name": "How long does SEO take to work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SEO typically takes 3-6 months to show significant results, though this varies based on competition, domain authority, and effort invested. New websites may take 6-12 months, while established sites with existing authority can see improvements in 1-3 months for less competitive keywords."
      }
    },
    {
      "@type": "Question",
      "name": "Is SEO better than paid advertising?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SEO and paid advertising serve different purposes. SEO provides sustainable, long-term traffic without per-click costs but takes time to build. Paid advertising delivers immediate results but stops when you stop paying. Most successful businesses use both: paid ads for immediate leads and SEO for long-term growth."
      }
    }
  ]
}
```

_Implementation: Wrap the above JSON-LD in `<script type="application/ld+json">...</script>` and place in `<head>` or before `</body>`. Test with ~~schema validator._

### SERP Preview

```
SEO Guide: Complete Beginner's Tutorial
yoursite.com/seo-guide/
Learn SEO from scratch with our comprehensive guide...

▼ What is SEO?
  SEO (Search Engine Optimization) is the practice of optimizing...
▼ How long does SEO take to work?
  SEO typically takes 3-6 months to show significant results...
▼ Is SEO better than paid advertising?
  SEO and paid advertising serve different purposes...
```
```

---

## Schema Type Quick Reference

| Content Type | Schema Type | Key Properties |
|--------------|-------------|----------------|
| Blog Post | BlogPosting/Article | headline, datePublished, author |
| Product | Product | name, price, availability |
| FAQ | FAQPage | Question, Answer |
| How-To | HowTo | step, totalTime |
| Local Business | LocalBusiness | address, geo, openingHours |
| Recipe | Recipe | ingredients, cookTime |
| Event | Event | startDate, location |
| Video | VideoObject | uploadDate, duration |
| Course | Course | provider, name |
| Review | Review | itemReviewed, ratingValue |

---

## Tips for Success

1. **Match visible content** - Schema must reflect what users see
2. **Don't spam** - Only add schema for relevant content
3. **Keep updated** - Update dates and prices when they change
4. **Test thoroughly** - Validate before deploying
5. **Monitor Search Console** - Watch for errors and warnings
