# Keyword Research — Detailed Instructions

Compact workflow, scoring rules, and delivery templates for the Keyword Research skill.

At the start of each phase, announce `**[Phase X/8: Name]**`.

## Phase 1/8: Scope

Confirm the topic, audience, business goal, domain strength, geography, and language.

## Phase 2/8: Discover

**Start from Search Console when available (striking-distance first).** If `~~search console` is connected, your first opportunity set is queries already earning impressions at positions ~5–20 — proven demand a small push can convert. The Search Analytics API sorts by clicks and offers no position filter, so request a high `rowLimit` and filter the 5–20 window client-side, then carry that shortlist straight into Phase 5 scoring (label its metrics **Measured**). Only after working the striking-distance set, expand with the seeds below.

Then seed from:
- Core product and service terms
- Problem-focused keywords
- Solution-focused keywords
- Audience-specific language
- Industry terminology

## Phase 3/8: Variations

```markdown
## Keyword Expansion Patterns

### Modifiers
- Best [keyword]
- Top [keyword]
- [keyword] for [audience]
- [keyword] [year]
- How to [keyword]
- What is [keyword]
- [keyword] vs [alternative]
- [keyword] examples
- [keyword] tools

### Long-tail Variations
- [keyword] for beginners
- [keyword] for small business
- Free [keyword]
- [keyword] software/tool/service
- [keyword] template
- [keyword] checklist
- [keyword] guide
```

## Phase 4/8: Classify

| Intent | Signals | Example | Content Type |
|--------|---------|---------|--------------|
| Informational | what, how, why, guide, learn | "what is SEO" | Guides, explainers |
| Navigational | brand names, specific sites | "google analytics login" | Homepage, support |
| Commercial | best, review, vs, compare | "best SEO tools" | Comparisons, reviews |
| Transactional | buy, price, discount, order | "buy SEO software" | Product and pricing pages |

## Phase 5/8: Score

Difficulty bands:
- **Low (1-39)**: weak competitors, thin content, or long-tail intent
- **Medium (40-69)**: mixed authority landscape and moderate link/content bar
- **High (70-100)**: major brands, heavy backlink requirements, ad-heavy SERPs

Opportunity formula:

`Opportunity = (Volume × Intent Value) / Difficulty`

Intent values:
- Informational = 1
- Navigational = 1
- Commercial = 2
- Transactional = 3

| Scenario | Volume | Difficulty | Intent | Priority |
|----------|--------|------------|--------|----------|
| Quick Win | Low-Med | Low | High | 5 stars |
| Growth | High | Medium | High | 4 stars |
| Long-term | High | High | High | 3 stars |
| Research | Low | Low | Low | 2 stars |

## Phase 6/8: GEO-Check

Flag keywords with high AI-answer overlap:
- Questions, definitions, comparisons, lists, and how-to queries
- Queries that can be answered concisely or with structured facts
- Well-documented topics with low to medium commercial friction

## Phase 7/8: Cluster

```markdown
## Topic Cluster: [Main Topic]

**Pillar Content**: [Primary keyword]
- Search volume: [X]
- Difficulty: [X]
- Content type: [Guide / landing / comparison]

**Cluster Content**:
- [Secondary keyword] — Volume [X], Difficulty [X], links to [pillar]
- [Secondary keyword] — Volume [X], Difficulty [X], links to [pillar + related cluster]
```

## Phase 8/8: Deliver

Report sections:
- Executive Summary
- Top Opportunities: Quick Wins / Growth / GEO
- Topic Clusters
- Content Calendar
- Next Steps

**Quality bar**: every recommendation includes at least one specific number.

| Generic | Actionable |
|---|---|
| "Target long-tail keywords for better results" | "Target 'project management for nonprofits' (vol: 320, KD: 22) — no DR>40 sites in top 10" |
| "This keyword has good potential" | "Opportunity 8.4: vol 4,800, KD 28, transactional intent — top 5 content is stale" |
| "Consider creating content around this topic" | "Write '[Tool A] vs [Tool B] for small teams' — 1,200/mo searches, current #1 is from 2022" |

> **Reference**: See [references/example-report.md](example-report.md) for the full report template and example.

## Advanced Usage

- **Intent Mapping**: `Map all keywords for [topic] by search intent and funnel stage`
- **Seasonal Analysis**: `Identify seasonal keyword trends for [industry]`
- **Competitor Gap**: `What keywords do [competitor 1], [competitor 2] rank for that I'm missing?`
- **Local Keywords**: `Research local keywords for [business type] in [city/region]`

## Tips for Success

Start from strong seeds, respect intent, cluster tightly, include GEO candidates, and refresh the research quarterly.
