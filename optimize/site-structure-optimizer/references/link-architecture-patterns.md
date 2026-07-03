# Link Architecture Patterns (linking mode)

Internal-link topologies, selection thresholds, migration safeguards, and measurement targets. Used at Step 1 (Analyze Current Structure) of [SKILL.md](../SKILL.md) — the avg-links/page target range that drives the −10 score penalty comes from the model chosen here.

## The Five Models

| Model | Shape | Best for | Site-size fit | Authority flow |
|-------|-------|----------|---------------|----------------|
| Hub-spoke (topic cluster) | Pillar links to all spokes; every spoke links back to pillar; spokes cross-link where relevant | Blogs, SaaS use-cases, most content sites | 50–500 content pages | Concentrates authority on the pillar, distributes to spokes |
| Silo | Strict category trees; links stay within a category, minimal cross-links | Docs, large ecommerce categories | 100+ categories or distinct taxonomies | Contains authority within a topic; strong topical signal |
| Flat | Key pages linked from home; shallow URLs; free cross-linking; nav/menu support | Small sites, shallow URL structures | <50 ideal; 50–100 manageable; 100+ difficult | Even, home-centric distribution; little topical concentration |
| Pyramid | Home → category → subcategory → page hierarchy, 3–4 levels max, breadcrumbs | News/media, large blogs, corporate, gov/edu | 500+ posts or a clear hierarchy | Cascades down and back up the hierarchy |
| Mesh | Dense cross-linking across the whole site, few strict boundaries | Small sites (<50 pages), wikis, knowledge bases | Dense topic networks | Even distribution; dilutes topical concentration |

**Default**: hub-spoke. Use silo when topical separation matters more than cross-topic discovery; use flat on small/shallow sites; use pyramid on large hierarchical sites (news, corporate); use mesh only on small sites where every page is broadly relevant to every other.

## Selection Thresholds

Figures are **Estimated** defaults — adjust to the site.

| Signal | Hub-spoke | Silo | Flat | Pyramid | Mesh |
|--------|-----------|------|------|---------|------|
| Page count | 30–500 | 200+ | <50 | 500+ | <50 |
| Distinct topics | 3–15 pillars | many rigid categories | 1–3 | many, hierarchical | 1–2 |
| Cross-topic relevance | medium | low | high | low–medium | high |

## Measurement Targets (per model)

Used in the Step 1 score: `−10 if avg links/page is outside the model's target range`. All **Estimated**.

| Metric | Hub-spoke target | Silo target | Flat target | Pyramid target | Mesh target |
|--------|------------------|-------------|-------------|----------------|-------------|
| Avg internal links per page | 3–10 | 3–8 | 8–15 | 3–5 | 5–15 |
| Inbound contextual links per important page | ≥3 | ≥2 | ≥3 | ≥2 | ≥3 |
| Max click depth for important pages | ≤3 | ≤3 | ≤2 | ≤4 | ≤2 |
| Orphan pages | 0 | 0 | 0 | 0 | 0 |

Outside the target range = under-linked (crawl/authority starvation) or over-linked (diluted anchors, thin PageRank per link).

## Anchor-Text Distribution Targets

Cross-reference [Linking Templates §Step 3](linking-templates.md). Targets are **Estimated**.

| Anchor type | Target share | Note |
|-------------|--------------|------|
| Descriptive / topical | 60–80% | CORE-EEAT R08 — descriptive anchors forming clusters |
| Branded / navigational | 10–20% | menus, footer, breadcrumbs |
| Generic ("read more", "here") | <10% | minimize; not zero (some UX-driven) |
| Exact-match repeated | <5% per target | over-optimization risk above this |

## Orphan-Page Detection

An orphan has **zero inbound internal links** (no path from home via any link). Detect from the crawl link graph:

1. Build the internal link graph (`crawl.py | linkgraph.py` — see SKILL.md Data Sources).
2. Flag every node with in-degree 0 that is not the home page.
3. Also flag near-orphans: reachable only from XML sitemap or only via `nofollow` links.
4. Classify each for disposition — see [Linking Templates](linking-templates.md) Step 2 and the SKILL.md disposition ladder (keep + link / noindex / 301).

## Migration Safeguards (when linking work changes URLs)

- Every changed URL needs a planned **301** to its new location — no migration without a redirect (this is a blocking defect; hand to `content-quality-auditor`).
- Update internal links to point at the final URL, not through a redirect chain.
- Preserve links to pages listed in "existing URLs to preserve".
- Confirm each new target resolves (no 404) before recommending it — CORE-EEAT R10 (see SKILL.md Step 5).

## Link Rules by Model

| Model | Required links | Optional / conditional links | Avoid |
|-------|----------------|------------------------------|-------|
| Hub-spoke | Pillar → all spokes; every spoke → pillar | Spoke ↔ related spoke; hub ↔ hub bridge | Unrelated bridges that dilute topical focus |
| Silo | Parent → child; child → parent; sibling links within same parent | Modified cross-silo links when user intent overlaps | Strict model: broad cross-silo linking |
| Flat | Home/navigation → all key pages; contextual cross-links | HTML sitemap for larger flat sites | Letting pages drift beyond 2 clicks |
| Pyramid | Each level links down and up; breadcrumbs | Related-content links at page level | More than 4 levels without shortcuts |
| Mesh | Contextual links with descriptive anchors | Cross-topic links only with clear relevance | >15 contextual links per 1,000 words or generic anchors |

## Migration Between Models

| From | To | Trigger | Difficulty |
|------|----|---------|------------|
| Flat | Hub-spoke | Site grew beyond 100 pages | Medium |
| Silo | Hub-spoke | Silos too rigid for topical authority | Medium |
| Pyramid | Hub-spoke | Want topic clusters over hierarchy | High |
| No structure | Any model | Orphans, depth, or chaotic linking | High |

**Migration sequence** (any model change): audit current state (map links, orphans, click depth, top linked pages) → design the target architecture (assign every important page its new position) → write a link-change plan (each link to add / keep / move / remove) → implement in phases (highest-priority cluster or silo first, no sitewide flips) → preserve existing equity (no valuable link removed without replacement) → monitor rankings, crawl stats, traffic, and indexation for 4–8 weeks per phase → iterate only after measured impact is clear. Every changed URL still needs a 301 per Migration Safeguards above.

## Monthly Monitoring

| Check | Target | Action if failing |
|-------|--------|-------------------|
| Orphan pages | 0 | Add internal links immediately, or redirect/remove low-value pages |
| Average click depth | Model target above | Add home/category shortcuts to deep pages |
| Internal link count/page | Model target above | Add links to under-linked pages or prune over-linked pages |
| Anchor-text diversity | Natural, descriptive mix (§Anchor-Text Distribution Targets) | Vary anchors for over-optimized pages |
| Broken internal links | 0 | Fix, redirect, or remove — CORE-EEAT R10 |
| New content linked | Within 48 hours | Add to related pages on publish |

## Hybrid: Hub-spoke + Silo

For medium-large sites that need both taxonomy clarity and topical authority, layer hub-spoke clusters inside silo categories:

```text
Home
  +-- Category Silo A
  |     +-- Hub A1 (pillar) <-> cluster articles
  |     +-- Hub A2 (pillar) <-> cluster articles
  +-- Category Silo B
  |     +-- Hub B1 (pillar) <-> cluster articles
  +-- Cross-category bridge links only where user intent overlaps
```

Implementation priority: fix structural defects first (orphans, broken links, excessive crawl depth) → choose the primary architecture model → add cluster/silo cross-links where relevance is clear → tune anchor text once structure is stable → monitor, then iterate.

## Next

Apply these targets in Step 1's structure score; pull step-by-step output templates from [Linking Templates](linking-templates.md).
