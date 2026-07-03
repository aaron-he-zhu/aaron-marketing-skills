# Site-Type Patterns (architecture mode)

Depth, topology, and URL taxonomy defaults by site type. Used at Step 2 (Pick the Model) and Step 4 (Define the URL Taxonomy) of [SKILL.md](../SKILL.md). State the chosen model and target depth before designing the hierarchy.

## Depth & Topology by Site Type

All depth/count figures are **Estimated** starting points — adjust to the actual inventory.

| Site type | Target max depth | Topology | Primary organizing unit | Typical page count (Estimated) |
|-----------|------------------|----------|-------------------------|-------------------------------|
| Blog / content | 3 clicks (Home → category/pillar → post) | Topic cluster (hub-spoke) | Pillar topic | 30–500 |
| Ecommerce | 3 clicks (Home → category → product); 4 with subcategory | Faceted category tree | Category / collection | 100–10,000+ |
| SaaS / marketing | 2–3 clicks (Home → section → detail) | Flat hub around features/use-cases | Feature / use-case | 20–150 |
| Docs / knowledge base | 3 clicks (Home → section → article) | Sidebar-driven silo | Product area / version | 50–2,000 |

**3-click rule** applies to all types: any important page deeper than 3 clicks from home is flagged at Step 3 and costs −5 in the architecture score.

## Hierarchy Levels

| Level | Blog | Ecommerce | SaaS | Docs |
|-------|------|-----------|------|------|
| L0 | Home | Home | Home | Docs home |
| L1 | Pillar / category | Category | Features, Use cases, Pricing, Blog | Section (Getting started, Guides, API, Reference) |
| L2 | Post (spoke) | Subcategory or product | Feature detail, use-case detail | Article |
| L3 | — (avoid) | Product | — (avoid) | Sub-article / version variant |

Keep L3 rare. If a type needs L3 routinely (deep ecommerce), confirm faceted navigation is `noindex`-able so facet combinations do not become crawlable dead pages (hand XML/indexation questions to `technical-seo-checker`).

## URL Taxonomy Rules

| Rule | Do | Avoid |
|------|-----|-------|
| Reflect hierarchy | `/guides/email/subject-lines` | `/page?id=482` |
| One organizing unit per segment | `/category/product` | mixed parents for peers |
| Lowercase, hyphen-separated | `/list-building` | `/List_Building`, `/listBuilding` |
| Stable, meaning-based slugs | `/email-automation` | dates in blog URLs (`/2024/03/...`) |
| Consistent trailing slash | pick one, apply everywhere | mixed `/x` and `/x/` |
| Shallow segments | 2–3 path segments | 5+ nested segments |

## URL Patterns by Type

Illustrative patterns (**Estimated** — confirm against existing URLs to preserve):

| Type | Pattern | Example |
|------|---------|---------|
| Blog | `/{pillar}/{post-slug}` | `/email-marketing/subject-line-tips` |
| Ecommerce | `/{category}/{product-slug}` | `/running-shoes/trail-x2` |
| SaaS | `/{section}/{detail-slug}` | `/features/reporting`, `/use-cases/agencies` |
| Docs | `/{section}/{article-slug}` | `/guides/authentication` |

## Common Mistakes (flag at Step 4)

- Dates in blog URLs — signals staleness, breaks on refresh
- Over-nesting — 4+ segments push pages past 3 clicks
- IDs / query params as canonical URLs — weak relevance, duplicate risk
- Inconsistent parents for peer pages — muddles the category signal
- Mixed case or inconsistent trailing slash — duplicate-URL risk

## Next

Feed the chosen model's depth target into Step 3 (hierarchy) and its topology into Step 6 (hub/spoke). For link-side thresholds tied to each model, see [Link Architecture Patterns](link-architecture-patterns.md).
