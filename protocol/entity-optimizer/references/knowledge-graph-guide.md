# Knowledge Graph Guide

Use this guide to turn an entity into a consistent, verifiable profile that downstream SEO/GEO skills can cite.

## Entity Profile Core

| Field | Requirement |
|-------|-------------|
| Name | Canonical name plus common variants |
| Type | Organization, person, product, place, publication, or concept |
| Description | 1-2 sentence neutral definition |
| Website | Canonical URL |
| SameAs | Official social, Wikidata/Wikipedia, Crunchbase, app stores, profiles |
| Identifiers | Wikidata QID, schema IDs, product IDs, legal names when available |
| Claims | Source-backed facts only; date every volatile claim |
| Disambiguation | Similar names/entities and how to distinguish them |

## Signal Sources

| Source | Use | Evidence |
|--------|-----|----------|
| Official site/about/legal pages | Canonical facts | URL + accessed date |
| Schema.org markup | Machine-readable entity definition | JSON-LD type/fields |
| Wikidata/Wikipedia | Knowledge graph presence | QID/page + references |
| Social/profiles | SameAs corroboration | Verified handles |
| News/industry citations | Notability/trust | Source/date/context |
| Review/app/product platforms | Product/entity corroboration | Rating/count only if visible |

## Optimization Steps

1. Build or refresh the Canonical Entity Profile.
2. Normalize names, descriptions, URLs, and identifiers across owned surfaces.
3. Add or fix Organization/Person/Product/LocalBusiness schema where eligible.
4. Strengthen SameAs links with official, verifiable profiles.
5. Identify missing citations, weak sources, and conflicts.
6. Hand off to `serp-markup-builder`, `geo-content-optimizer`, or `domain-authority-auditor`.

## Wikidata / Wikipedia Notes

Do not create weak or promotional pages. Only propose Wikidata/Wikipedia work when notability, sourcing, neutrality, and conflict-of-interest handling are realistic.

## GEO Entity Pack

| Asset | Purpose |
|-------|---------|
| 40-60 word definition | AI answer citation seed |
| Fact table | Stable source-backed facts |
| Source list | Dated, authoritative references |
| SameAs list | Disambiguation and KG linking |
| Claim conflicts | Open loops to resolve |

## Quality Checks

- Every factual claim has source/date.
- Profile avoids marketing language.
- Volatile claims are labeled current as of date.
- Downstream schema fields match visible page content.
- Handoff includes confidence, gaps, and next best skill.
