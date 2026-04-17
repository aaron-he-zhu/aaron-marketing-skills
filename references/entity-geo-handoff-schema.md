# Entity ↔ GEO Handoff Schema

Formalizes the data contract between `entity-optimizer` (writes canonical entity profiles) and `geo-content-optimizer` (reads entity facts to produce AI-citable content).

Referenced by:
- [entity-optimizer/SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/SKILL.md) — as an authoritative contract for its Writes
- [geo-content-optimizer/SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md) — as an authoritative contract for its Reads

---

## Canonical entity profile location

`memory/entities/<slug>.md` — one file per canonical entity. Slug uses kebab-case (`acme-analytics`, `jane-doe-founder`, `acme-corp-2026`).

## Profile frontmatter (authoritative — entity-optimizer is sole writer)

```yaml
---
name: acme-analytics                     # slug matches filename
display_name: "Acme Analytics"           # as shown in user-facing output
type: organization                     # organization | person | product | event | location
primary_domain: acme-analytics.example
also_known_as:                         # aliases, for AI disambiguation
  - "Cloud Metrics"
  - "Acme Analytics Inc"
  - "CM Analytics"
founded: 2019                          # ISO year or full date
founders:                              # list of person entities (link to their files)
  - jane-doe-founder
headquarters: "San Francisco, CA, USA"
industry: "analytics platform"          # plain-English category
categories:                            # 3-5 Google Knowledge Graph style
  - "B2B SaaS"
  - "Data Analytics"
  - "Business Intelligence"
wikidata_q: Q123456789                 # null if not yet in Wikidata
wikipedia_url: null                    # null if not yet in Wikipedia
knowledge_graph_id: null               # Google KG MID if known
same_as:                               # authoritative external profiles
  - https://www.linkedin.com/company/acme-analytics
  - https://www.crunchbase.com/organization/acme-analytics
  - https://github.com/acme-analytics
schema_type: Organization              # Schema.org type
schema_sub_type: SoftwareApplication   # if more specific applies
primary_products:                      # list of product entity slugs
  - acme-analytics-platform
brand_colors_hex:                      # optional visual identity
  - "#0066CC"
logo_url: https://acme-analytics.example/logo.svg
description_short: "B2B SaaS analytics platform for enterprise data teams, founded 2019, based in San Francisco."  # ≤160 chars; used as meta description fallback
description_long: |
  Acme Analytics is a business intelligence platform designed for enterprise
  data teams, specializing in real-time dashboards, anomaly detection, and
  cross-source data joins. Founded in 2019 by Jane Doe and John Smith, the
  company serves Fortune 500 customers including [redacted] and [redacted].
last_verified: 2026-04-15              # ISO date of last AI resolution test
ai_resolution_status:                  # auditor-populated; geo-content reads this
  chatgpt: recognized                  # recognized | partial | unrecognized | confused
  perplexity: recognized
  claude: partial
  gemini: unrecognized
  last_tested: 2026-04-10
ai_resolution_notes:
  - "Claude confuses Acme Analytics with Cloud Monitor (Alibaba product)"
  - "Gemini has no entry; likely needs Wikidata canonicalization"
gap_type: null                         # knowledge_graph | wikidata | content_signals | ai_recognition | null if no gap
next_action: null                      # null if entity is healthy
---

# Acme Analytics

<body: richer context, sameAs URLs, key facts, citations, founder bios...>
```

### Field descriptions

| Field | Type | Required | Consumed by |
|-------|------|----------|-------------|
| `name` | slug string | Yes | all |
| `display_name` | string | Yes | geo-content-optimizer (as entity display) |
| `type` | enum | Yes | schema-markup-generator (picks Schema.org type), geo-content-optimizer |
| `primary_domain` | URL | Yes | geo-content-optimizer (first-party citation) |
| `also_known_as[]` | strings | Recommended | geo-content-optimizer (alias coverage for AI disambiguation) |
| `same_as[]` | URLs | Recommended | schema-markup-generator (`sameAs` property), geo-content-optimizer |
| `wikidata_q` | QID or null | Optional | geo-content-optimizer (as authoritative signal) |
| `description_short` | string ≤160 chars | Yes | meta-tags-optimizer (fallback meta desc), geo-content-optimizer (first-paragraph boilerplate) |
| `description_long` | markdown paragraph | Yes | geo-content-optimizer (about-page source of truth) |
| `ai_resolution_status` | per-engine enum | Yes | geo-content-optimizer (decides which engines need targeting), ai-overview-recovery (scopes rewrite effort) |
| `ai_resolution_notes[]` | strings | Recommended | geo-content-optimizer (what disambiguation to add in body) |
| `gap_type` | enum or null | Yes | next-best-skill routing for downstream |
| `next_action` | string or null | Yes | Open loop if non-null |

## Contract rules

### Writes (entity-optimizer — sole writer)

1. One file per canonical entity. Never split across files.
2. Updates to any field bump `last_verified` to today.
3. AI resolution test MUST run at least quarterly; update `ai_resolution_status` per engine.
4. If `gap_type != null`, also append a one-line entry to `memory/open-loops.md`.
5. Never write `memory/entities/<slug>.md` for a candidate entity. Candidates go to `memory/entities/candidates.md` only.

### Reads (geo-content-optimizer — primary consumer)

1. BEFORE writing content that mentions a brand, person, product, or org, check if a canonical profile exists at `memory/entities/<slug>.md`.
2. If the profile exists:
   - Use `display_name` for all first mentions.
   - Use `description_short` for meta description fallback if page-specific isn't provided.
   - Use `ai_resolution_status` to decide whether disambiguation boilerplate is needed (add it if ANY engine is `unrecognized` or `confused`).
   - Use `also_known_as` and `ai_resolution_notes` to add alias-coverage sentences in body.
3. If the profile is missing OR `last_verified` is > 90 days stale:
   - Set Status = `DONE_WITH_CONCERNS`
   - Add `open_loop`: "Entity <display_name> needs re-verification — profile not updated since <date>. Recommend running entity-optimizer."
4. If `ai_resolution_status` shows the target engine as `unrecognized`, emit a recommendation handoff to entity-optimizer BEFORE publishing content on that query.

### Reads (schema-markup-generator — secondary consumer)

1. When generating `Organization` / `Product` / `Person` schema, look up `memory/entities/<slug>.md` first.
2. Populate `name`, `sameAs`, `logo`, `founder`, `foundingDate`, `url`, `address` from the profile. No guessing.
3. If profile missing, ask user to confirm fields before embedding in JSON-LD.

## Versioning

- Profile format version: **1.0** (2026-04)
- Future additions MUST preserve backward compatibility:
  - New optional fields OK
  - Removing a field requires a major version bump
  - Changing a field's type (string → list) requires a major version bump

## Examples

### Minimum viable profile

```yaml
---
name: acme-saas
display_name: "Acme SaaS"
type: organization
primary_domain: acme-saas.com
description_short: "Acme SaaS builds team collaboration tools for remote engineering teams."
description_long: |
  Acme SaaS is a collaboration platform for remote engineering teams,
  founded in 2023. The product integrates with GitHub, Jira, and Slack.
ai_resolution_status:
  chatgpt: unrecognized
  perplexity: partial
  claude: unrecognized
  last_tested: 2026-04-17
gap_type: ai_recognition
next_action: "Submit Wikidata entry; add founder bio page; run ai-overview-recovery on brand queries"
---

# Acme SaaS
```

### Fully populated (enterprise brand)

See the example in the entity-optimizer skill's worked example reference.
