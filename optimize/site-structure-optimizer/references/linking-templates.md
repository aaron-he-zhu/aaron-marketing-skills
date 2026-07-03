# Linking Templates (linking-mode steps 3–7)

Copy-paste output templates for linking mode in [SKILL.md](../SKILL.md). Each template maps to one step. Label every metric **Measured**, **User-provided**, or **Estimated**. Threshold defaults live in [Link Architecture Patterns](link-architecture-patterns.md).

## Anchor & Link Rules (apply throughout)

- **Descriptive over generic**: anchor should describe the target ("email segmentation guide"), not "click here" / "read more".
- **Contextual over navigational**: in-body links inside relevant prose carry more weight than menu/footer links. Count them separately.
- **Link-depth budget**: important pages ≤3 clicks from home; each in-body link ≈ 1 unit of PageRank divided among all links on the page — do not exceed the model's avg-links/page target.
- **One primary target per anchor**: avoid pointing the same exact-match anchor at multiple pages.
- **No redirect chains**: link to the final URL.

> Exact-match anchor guidance tightened: the old 10–20% allowance is retired in favor of **<5% per target** (the stricter current scheme) — repeated exact-match anchors above this read as over-optimization.

## Step 3 — Anchor-Text Distribution

```text
Anchor-Text Distribution — [domain]
Data source: [Measured/Estimated]

| Anchor type          | Count | Share | Target        | Flag |
|----------------------|-------|-------|---------------|------|
| Descriptive/topical  |       |    %  | 60–80%        |      |
| Branded/navigational |       |    %  | 10–20%        |      |
| Generic              |       |    %  | <10%          |      |
| Exact-match (repeat) |       |    %  | <5% / target  |      |

Over-optimized anchors (exact-match > threshold): [list target → anchor → count]
Generic anchors to rewrite: [source → current anchor → suggested descriptive anchor]

Anchor Score /10: [n]
  Start 10; −2 if generic >10%; −2 if any exact-match >5% to one target;
  −2 if descriptive <60%; −1 per over-optimized cluster (cap −4). Floor 0.
```

## Step 4 — Topic Cluster Link Strategy

```text
Topic Clusters — [domain]

| Pillar (hub) | Spokes (in-cluster) | Missing hub→spoke | Missing spoke→hub | Cross-links to add |
|--------------|---------------------|-------------------|-------------------|--------------------|
|              |                     |                   |                   |                    |

Recommended structure: [hub-spoke / silo / mesh] — see Link Architecture Patterns
Specific links to add: [source → target → anchor → reason]
```

## Step 5 — Contextual Link Opportunities

```text
Contextual Link Plan — [page or domain]

| # | Source page (+paragraph) | Target URL | Suggested anchor | Priority | Target resolves? |
|---|--------------------------|------------|------------------|----------|------------------|
| 1 |                          |            |                  | High     | Yes/No (404→flag)|

Broken targets flagged for content-quality-auditor (R10): [list]
```

## Step 6 — Navigation & Footer Links

```text
Navigation Review — [domain]

| Zone       | Current items | Add | Demote | Remove | Reason |
|------------|---------------|-----|--------|--------|--------|
| Header     |               |     |        |        |        |
| Footer     |               |     |        |        |        |
| Sidebar    |               |     |        |        |        |
| Breadcrumb |               |     |        |        |        |

Header rule: 4–7 items, CTA rightmost, logo → home. Breadcrumbs mirror the URL path.
```

## Step 7 — Implementation Plan

```text
Internal Linking Plan — [domain]  |  Structure Score: [n]/100

Executive summary: [1–2 lines: biggest structural gap + expected effect]

Current-state metrics (label each Measured/Estimated):
- Pages analyzed / total internal links / avg links per page
- Orphans / under-linked important pages / max click depth

Phased priority actions:
  P1 (blocking): [orphans of high-value pages, migrations without 301]
  P2 (this sprint): [add contextual links, rewrite generic anchors]
  P3 (backlog): [nav/footer tuning, low-value orphan disposition]

Implementation guide: [source → target → anchor, grouped by page]
Tracking plan: re-crawl cadence; metrics to watch (orphan count, avg depth, anchor mix)
Handoff: veto-level risks (migration w/o redirect, broken targets) → content-quality-auditor
```
