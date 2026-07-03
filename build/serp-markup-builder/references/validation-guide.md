# Schema Markup Validation Guide

Compact reference for validating, testing, troubleshooting, and maintaining structured data.

## Validation Tools

| Tool | Use |
|------|-----|
| Google Rich Results Test | Check Google rich result eligibility. |
| Schema.org Validator | Validate against Schema.org syntax/spec. |
| Google Search Console Enhancements | Monitor structured-data issues at scale. |

## Common JSON-LD Errors

| Error | Bad pattern | Fix |
|-------|-------------|-----|
| Trailing comma | Last property ends with `,` | Remove comma after final property. |
| Missing quotes | `@context: "..."` | Quote property names: `"@context"`. |
| Wrong date format | Locale date such as `MM/DD/YYYY` | Use ISO 8601: `[ISO 8601 date-time]`. |
| Relative URL | `"/images/photo.jpg"` | Use absolute `https://...` URL. |
| Multiple values not in array | `"image": "a.jpg", "b.jpg"` | Use an array: `["a.jpg", "b.jpg"]`. |
| Dynamic-only injection | Schema absent from source/rendered test | Ensure crawler-visible JSON-LD is present. |

## Required and Recommended Properties

| Type | Required | Recommended / eligibility notes |
|------|----------|---------------------------------|
| FAQPage | `mainEntity`, `Question.name`, `Answer.text` | Minimum 2 visible Q&A pairs; not for forums, UGC Q&A, or promotional FAQs. |
| HowTo | `name`, `step`, `step.text` | Minimum 2 steps; complete process; use Recipe schema for recipes; add image/totalTime when available. |
| Article / BlogPosting | `headline`, `image`, `datePublished`, `author`, `publisher`, `publisher.logo` | Headline max 110 chars; image >=1200px wide; add `dateModified` when content changes. |
| Product | `name`, `image` | Price display needs `offers.price`, `priceCurrency`, `availability`; stars need genuine `aggregateRating` or `review`; add brand/sku. |
| LocalBusiness | `name`, `address` | Add `geo`, `telephone`, and `openingHoursSpecification`. |
| Organization | `name`, `url` | Add `logo` and `sameAs` profiles. |

## Rich Result Policy Checks

| Policy risk | Example | Fix |
|-------------|---------|-----|
| Content mismatch | FAQ schema not visible on page | Markup must match visible content. |
| Deceptive reviews | Fake, paid, or incentivized reviews | Use only genuine, verifiable review data. |
| Irrelevant schema | Product schema on generic blog post | Use schema types that match page purpose. |
| Hidden content | Answers only in JSON-LD | Make marked-up content visible to users. |
| Promotional FAQ | `Why is [Brand] best?` | Use neutral, informational questions. |

## Testing Workflow

| Stage | Steps |
|-------|-------|
| Initial implementation | Add schema in dev/staging; validate syntax; run Rich Results Test; confirm source/rendered page contains JSON-LD. |
| Pre-launch | Test staging URL; verify required properties; confirm visible content match; test combined schema types. |
| Post-launch | Submit sitemap; monitor Search Console Enhancements; re-test after content changes; fix errors within 30 days. |

## Troubleshooting

| Symptom | Checks |
|---------|--------|
| Schema not found | View source and rendered HTML; search for `"@type"`; confirm `type="application/ld+json"`; check dynamic rendering. |
| Rich result not showing | Check Enhancements, URL Inspection, eligibility, indexing status, and allow days/weeks for display. |
| Errors vs warnings | Errors block eligibility and must be fixed; warnings are recommended-property improvements. |

## Quick Error Reference

| Message | Fix |
|---------|-----|
| Missing required field | Add the required property for that schema type. |
| Invalid date format | Use ISO 8601 date/date-time. |
| URL is not absolute | Use full `https://` URLs. |
| Unexpected token | Check quotes, brackets, commas, and arrays. |
| Not eligible for rich results | Re-check type-specific eligibility and policy rules. |
| Image too small | Use image at least 1200px wide where required. |
| The attribute price is required | Add `offers.price` plus currency and availability when price display is needed. |

## Maintenance Checklist

| Timing | Action |
|--------|--------|
| Monthly | Check Search Console errors, verify rich result status, update `dateModified` only when content changes. |
| Quarterly | Audit key schema types, test priority pages, update outdated info, evaluate new relevant schema types. |
| After content changes | Sync visible content and schema, update `dateModified`, revalidate, request indexing if important. |
| After migration | Verify schema survived, update absolute URLs, submit sitemap. |

## Resources

- Schema.org: `https://schema.org/`
- Google structured data docs: `https://developers.google.com/search/docs/appearance/structured-data`
- Rich Results Test: `https://search.google.com/test/rich-results`
- Schema Validator: `https://validator.schema.org/`
- JSON-LD Playground: `https://json-ld.org/playground/`
