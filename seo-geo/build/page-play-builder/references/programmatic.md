# Programmatic Mode — Playbooks, Data Tiers, Guardrails

Play pack for the **programmatic** mode of [page-play-builder](../SKILL.md). Designs a template × dataset system that generates many SEO pages at once, with the defensibility and thin-content checks that keep them indexable. Use the playbook table to map a search pattern to a template, the tier table to judge data defensibility, and the guardrail checklist before publishing.

## When this mode fires

The user wants to generate hundreds or thousands of pages from one template plus a structured dataset (locations, comparisons, integrations, glossary, personas, etc.), pick a pSEO playbook, or audit an already-published template × data set for thin/duplicate risk.

**Required input**: a dataset with real per-row facts. If no dataset exists, or the pattern is just a name/city swap with no per-row facts, return **NEEDS_INPUT** — there is nothing to build a defensible evidence block from.

## Play (run in order)

1. **Confirm the inputs.** Get the page pattern (or let step 2 pick one), the dataset source and fields, the approximate row count, and product/ICP context.
2. **Select a playbook.** Match the search pattern to one of the 12 playbooks below; playbooks combine (e.g. locations × personas).
3. **Run the data-defensibility tier check.** Rank the dataset Tier 1 (product-generated, strongest) → Tier 5 (public/scraped, weakest). If the only source is public/scraped, the evidence block needs an added editorial layer or a unique tool, or the system risks commodity thin pages — flag it.
4. **Design the template.** Define fields for Intro → Evidence block (the unique per-row facts: tables, real numbers, attributes) → Decision → FAQ → CTA, with conditional logic to hide empty fields. The evidence block is what makes each URL non-thin.
5. **Set thin/duplicate guardrails.** Define the N-gram dedup check, a minimum unique-value bar per page, and selective-indexation / sitemap-segmentation rules so pages with no distinct value never get indexed.
6. **Add the AI-grounded-generation governance note.** If AI drafts copy, ground it in each row's structured facts; AI shapes phrasing, FAQ depth, and section emphasis, never the numbers. Forbid invented stats/citations in the prompt, label generated copy, and QA a sample before publish.
7. **Plan the rollout.** Launch in measurable batches (not one large dump), set freshness rules per field, and pick a representative sample for the auditor. If auditing existing pages, scan for repeated tails (treat fetched/crawled content as untrusted per [SECURITY.md](../../../../SECURITY.md)) and prioritize fixes P0 / P1 / P2.

**Done when**: a playbook is selected with a justified data-tier verdict; the template has an evidence block with unique per-row value; dedup (N-gram) and selective-indexation rules are defined; and any thin/duplicate or licensing blocker is flagged, not shipped silently.

## The 12 Playbooks

Each row is a proven template × dataset pattern. Playbooks combine — e.g. locations × personas ("agencies for startups in Austin"), curation × locations ("best coworking in San Diego").

| # | Playbook | Search pattern | Value bar (per page) | URL structure |
|---|----------|----------------|----------------------|---------------|
| 1 | **Templates** | "[type] template", "free [type] template" | Actually usable assets, multiple variations, quality of paid options | `/templates/[type]/` |
| 2 | **Curation** | "best [category]", "top [n] [things]" | Real evaluation criteria, dated updates, not pure affiliate ranking | `/best/[category]/` |
| 3 | **Conversions** | "[X] to [Y]", "[amount] [unit] in [unit]" | Accurate real-time data, fast working tool, related conversions | `/convert/[from]-to-[to]/` |
| 4 | **Comparisons** | "[X] vs [Y]", "[X] alternative" | Honest balanced analysis, real feature data, recommendation by use case | `/compare/[x]-vs-[y]/` |
| 5 | **Examples** | "[type] examples", "[category] inspiration" | Real high-quality examples, screenshots/embeds, why-it-works analysis | `/examples/[type]/` |
| 6 | **Locations** | "[service] in [location]" | Actual local data (not city-name swap), local options, location-specific insight | `/[service]/[city]/` |
| 7 | **Personas** | "[product] for [audience/role/industry]" | Genuine persona content, relevant features, segment testimonials | `/for/[persona]/` |
| 8 | **Integrations** | "[product A] [product B] integration", "[A] + [B]" | Real integration detail, setup steps, combination use cases, not vaporware | `/integrations/[product]/` |
| 9 | **Glossary** | "what is [term]", "[term] definition" | Clear accurate definitions, examples, related terms, more depth than a dictionary | `/glossary/[term]/` |
| 10 | **Translations** | same content per language | Quality translation + localization, hreflang, native review | `/[lang]/[page]/` |
| 11 | **Directory** | "[category] tools/software/companies" | Comprehensive coverage, useful filtering, detail per listing, updates | `/directory/[category]/` |
| 12 | **Profiles** | "[person/company name]", "[entity] + [attribute]" | Accurate sourced info, unique aggregation, not a Wikipedia rehash | `/people/[name]/` |

**Match playbook to assets**: proprietary data → directory/profiles/curation; integrations → integrations; design/creative product → templates/examples; multi-segment audience → personas; local presence → locations; tool/utility → conversions; content/expertise → glossary/curation; international upside → translations; competitor set → comparisons.

> **Cross-mode note**: for a *single* hand-built comparison page (not a generated set), use the **comparison** mode instead — see [comparison.md](comparison.md). Playbook 6 (locations) feeding real storefront/service-area pages should also carry the **local** mode's NAP/GBP layer — see [local.md](local.md).

**Avoid pSEO when** site structure is weak, page differences are superficial (name/city swap only), or the content genuinely needs original expertise or live UGC participation.

## Data Tiers (defensibility)

The strongest pages run on data only your product (or your customers inside it) can produce. Public/scraped lists alone are the weakest base. Prefer Tier 1–2 before reaching for Tier 5.

| Tier | Source | Examples | Risk |
|------|--------|----------|------|
| **1 — Product-generated** | Assets your product creates or renders: templates, exports, generated previews, branded snippets | Gallery rows tied to real CMS fields; unique preview URLs | **Lowest** when each URL shows distinct output |
| **2 — Product-derived** | Telemetry/aggregates you own: cohorts, benchmarks, adoption | "Median time-to-value by industry" from your warehouse | Low if aggregated, anonymized, policy-compliant |
| **3 — UGC / customer** | Reviews, submissions, portfolio items, moderated community content | Customer-submission grid; verified quotes | Medium — needs moderation + consent |
| **4 — Licensed / partner** | Exclusive feeds, co-marketing datasets, allowed partner fields | Partner pricing tiers; licensed stats | Medium — contract scope, attribution, trademark on logos |
| **5 — Public / scraped** | Open web, directories, generic enrichment | Name/address fills; commodity facts | **Highest** — everyone has the same facts; needs editorial layer or a unique tool on top |

**Tier-5 hard check**: if the only source is public/scraped and the template adds no synthesis, calculator, or editorial angle, the page is commodity thin content. Add a unique layer or do not generate the URL set.

## Guardrail Checklist (run before publish)

| Guardrail | Practice |
|-----------|----------|
| **Unique value per page** | Every page has an evidence block with real per-row facts (tables, numbers, attributes), 300+ words of genuine content — not boilerplate with swapped variables |
| **N-gram dedup** | Scan same-category pages for shared sentence tails / value statements; flag any phrase appearing in >30% of pages. Prepare 8–15 semantic variants and cycle them so adjacent pages differ |
| **Index-bloat control** | Selective indexation — noindex low-value pages; segment sitemaps by country/language/division to manage crawl budget; never index pages with no distinct value |
| **Batch launch** | Publish in small measurable batches, not one large dump (large dumps read as spam signals) |
| **Provenance & freshness** | Log the source per field; set freshness rules (e.g. prices 30 days, ratings 90 days) and "as of [date]" labels on volatile facts |
| **AI governance** | Ground generation in row JSON; AI shapes phrasing/FAQ depth/section order, never invents numbers or citations; label generated copy; QA high-traffic URLs before publish |

## Remediating already-homogenized pages

If pages are live and feel interchangeable (shared closing sentences, identical value props), fix before quality signals trigger:

- **P0 — Eliminate**: pure template filler with no info value → rewrite each page independently with page-specific detail.
- **P1 — Rewrite**: correct but formulaic delivery → cycle 8–15 semantic variants so adjacent pages differ.
- **P2 — Reduce density**: normal words that appear too often (e.g. one adjective on 80% of pages) → replace ~30–40% of instances, not all.

Fix P0 first, one category at a time; re-scan after each round; distribute rewrites so sequentially processed pages get different treatments. Prefer functional endings (what bottleneck the entry solves) over evaluative ones ("it's a good choice").

## Handoff

**Primary next skill**: [content-quality-auditor](../../../optimize/content-quality-auditor/SKILL.md) — gate a representative page sample for thin/duplicate risk before mass publish. This mode does **not** compute the CORE-EEAT score or run the veto items; it hands the sample forward.
