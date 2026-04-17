# On-Page SEO — Site-Wide / Bulk Audit Playbook

Referenced from [SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/on-page-seo-auditor/SKILL.md). Use when the user wants on-page audits across >5 pages at once.

---

## When to use bulk mode

- User wants to audit a content category (all blog posts, all product pages)
- User is triaging a site-wide traffic drop across many URLs
- Pre-publish audit for a content batch (5+ articles)
- Competitive benchmarking across many URLs

## Inputs accepted

1. **URL list** — user pastes 5+ URLs
2. **Sitemap URL** — scope to a section (e.g., `/sitemap-blog.xml`)
3. **GSC export** — URLs ranked for target queries
4. **Content type + sitemap** — "audit all 40 blog posts on example.com/blog/"

## Workflow

### Step 1 — Classify URLs into clusters

Group URLs by content-type template (blog post / product / landing / guide / comparison / listicle). Surface the cluster distribution to the user before spending effort:

```
Your 40 URLs:
- 24 blog posts (informational)
- 10 guide pages (commercial)
- 4 comparison pages (commercial)
- 2 landing pages (transactional)
```

### Step 2 — Sample 2-3 URLs per cluster

Run the standard on-page audit flow on the sampled URLs. Capture:
- Title pattern (e.g., "all titles start with product name + `| Brand`")
- H1 pattern consistency
- Meta description quality distribution
- CORE-EEAT dimension profile for the cluster

### Step 3 — Extrapolate + confirm

Produce cluster-level findings with scope:

```
### Cluster: Blog posts (24 URLs) — sample of 3

**Common strengths**:
- Title pattern is keyword-front-loaded + year qualifier (strong)
- H1 matches title (strong)

**Common weaknesses**:
- Meta description length distribution: 8 short (<120 chars), 16 OK, 0 over — sampled 3: 2 short, 1 OK. **Estimate: 67% need rewrite.**
- No H2 every 300 words — sampled 3: all violate. **Estimate: 24/24 affected.**
- Thin intro (<60 words before first H2) — sampled 3: 2 affected. **Estimate: 16/24.**

**CORE-EEAT profile (sampled)**:
- Strong: C02, O01, O02
- Weak: R01 (no citations), Exp02 (no first-person narrative), E01 (no original data)
```

### Step 4 — Portfolio priority

```
P0 (affects majority of cluster):
- Rewrite meta descriptions across blog cluster (est. 16 URLs) — template improvement

P1 (affects minority but high-impact):
- Add author bio + credentials to all blog posts (est. 24 URLs) — CORE-EEAT Ept
- Add 1 original stat per blog post (est. 20+ URLs) — CORE-EEAT R01

P2 (single-page refinements):
- Specific URLs flagged during deep sample: [list]
```

### Step 5 — Deliver bulk handoff

- **Status**: DONE | DONE_WITH_CONCERNS
- **Objective**: "Bulk on-page audit across <cluster_count> clusters (<total_urls> URLs)"
- **Key Findings / Output**: per-cluster pattern findings + portfolio priority
- **Evidence**: "Sampled N/M URLs; extrapolated to cluster level; confidence flagged per finding"
- **Open Loops**: un-sampled clusters, URLs flagged for individual attention, data gaps (no keyword data, etc.)
- **Recommended Next Skill**: `content-refresher` (for bulk content edits) OR `meta-tags-optimizer` (for title/description template work) OR `internal-linking-optimizer` (if linking pattern is the dominant issue)

## Template suggestions (common bulk outputs)

**Meta description template for a blog cluster**:

```
[Benefit in first 80 chars]. [Proof — number, source, or specific]. [CTA clause].
— Target: 140-155 chars. Front-load the benefit.
```

**H1 template for product cluster**:

```
[Product name]: [differentiator] for [audience]
— e.g., "Cloud Hosting: Managed Kubernetes for Small Teams"
```

**Alt-text template for images**:

```
[Descriptive noun phrase, 6-12 words, no "image of"]
```

## Minimum viable bulk input

```
1. URL list (or sitemap URL or content-type scope)
2. Are these already ranking, or new/pre-publish?
3. What's the business goal for this cluster?
4. Any known template/CMS that affects all of them?
```
