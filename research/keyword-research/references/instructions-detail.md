# Keyword Research — Detailed Instructions

Full 8-phase workflow, expansion patterns, scoring formulas, and deliverables for the Keyword Research skill.

At the start of each phase, announce: **[Phase X/8: Name]** so the user can track progress.

---

## Phase 1/8: Scope

Ask clarifying questions if not provided:
- What is your product/service/topic?
- Who is your target audience?
- What is your business goal? (traffic, leads, sales)
- What is your current domain authority? (new site, established, etc.)
- Any specific geographic targeting?
- Preferred language?

## Phase 2/8: Discover

Start with:
- Core product/service terms
- Problem-focused keywords (what issues do you solve?)
- Solution-focused keywords (how do you help?)
- Audience-specific terms
- Industry terminology

## Phase 3/8: Variations

For each seed keyword, generate variations:

```markdown
## Keyword Expansion Patterns

### Modifiers
- Best [keyword]
- Top [keyword]
- [keyword] for [audience]
- [keyword] near me
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

Categorize each keyword:

| Intent | Signals | Example | Content Type |
|--------|---------|---------|--------------|
| Informational | what, how, why, guide, learn | "what is SEO" | Blog posts, guides |
| Navigational | brand names, specific sites | "google analytics login" | Homepage, product pages |
| Commercial | best, review, vs, compare | "best SEO tools [current year]" | Comparison posts, reviews |
| Transactional | buy, price, discount, order | "buy SEO software" | Product pages, pricing |

## Phase 5/8: Score

Score each keyword (1-100 scale):

```markdown
### Difficulty Factors

**High Difficulty (70-100)**
- Major brands ranking
- High domain authority competitors
- Established content (1000+ backlinks)
- Paid ads dominating SERP

**Medium Difficulty (40-69)**
- Mix of authority and niche sites
- Some opportunities for quality content
- Moderate backlink requirements

**Low Difficulty (1-39)**
- Few authoritative competitors
- Thin or outdated content ranking
- Long-tail variations
- New or emerging topics
```

### Opportunity Score

Formula: `Opportunity = (Volume × Intent Value) / Difficulty`

**Intent Value** assigns a numeric weight by search intent:
- Informational = 1
- Navigational = 1
- Commercial = 2
- Transactional = 3

```markdown
### Opportunity Matrix

| Scenario | Volume | Difficulty | Intent | Priority |
|----------|--------|------------|--------|----------|
| Quick Win | Low-Med | Low | High | 5 stars |
| Growth | High | Medium | High | 4 stars |
| Long-term | High | High | High | 3 stars |
| Research | Low | Low | Low | 2 stars |
```

## Phase 6/8: GEO-Check — AI Answer Overlap

Keywords likely to trigger AI responses:

```markdown
### GEO-Relevant Keywords

**High GEO Potential**
- Question formats: "What is...", "How does...", "Why is..."
- Definition queries: "[term] meaning", "[term] definition"
- Comparison queries: "[A] vs [B]", "difference between..."
- List queries: "best [category]", "top [number] [items]"
- How-to queries: "how to [action]", "steps to [goal]"

**AI Answer Indicators**
- Query is factual/definitional
- Answer can be summarized concisely
- Topic is well-documented online
- Low commercial intent
```

## Phase 7/8: Cluster

Group keywords into content clusters:

```markdown
## Topic Cluster: [Main Topic]

**Pillar Content**: [Primary keyword]
- Search volume: [X]
- Difficulty: [X]
- Content type: Comprehensive guide

**Cluster Content**:

### Sub-topic 1: [Secondary keyword]
- Volume: [X]
- Difficulty: [X]
- Links to: Pillar
- Content type: [Blog post/Tutorial/etc.]

### Sub-topic 2: [Secondary keyword]
- Volume: [X]
- Difficulty: [X]
- Links to: Pillar + Sub-topic 1
- Content type: [Blog post/Tutorial/etc.]

[Continue for all cluster keywords...]
```

## Phase 8/8: Deliver

Produce a report containing: Executive Summary, Top Keyword Opportunities (Quick Wins, Growth, GEO), Topic Clusters, Content Calendar, and Next Steps.

**Quality bar** — every recommendation must include at least one specific number. If it reads like the left column, rewrite it before including.

| Generic (rewrite before including) | Actionable |
|---|---|
| "Target long-tail keywords for better results" | "Target 'project management for nonprofits' (vol: 320, KD: 22) — no DR>40 sites in top 10" |
| "This keyword has good potential" | "Opportunity 8.4: vol 4,800, KD 28, transactional intent — gap analysis shows no content updated since 2023 in top 5" |
| "Consider creating content around this topic" | "Write '[Tool A] vs [Tool B] for small teams' — 1,200/mo searches, current #1 is a 2022 article with 12 backlinks" |
| "Optimize your page for this keyword" | "Add primary keyword to H1 (currently missing), write a 40-word direct answer in paragraph 1, add 3 internal links from your /blog/ cluster" |

> **Reference**: See [references/example-report.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/example-report.md) for the full report template and example.

---

## Advanced Usage

- **Intent Mapping**: `Map all keywords for [topic] by search intent and funnel stage`
- **Seasonal Analysis**: `Identify seasonal keyword trends for [industry]`
- **Competitor Gap**: `What keywords do [competitor 1], [competitor 2] rank for that I'm missing?`
- **Local Keywords**: `Research local keywords for [business type] in [city/region]`

---

## Tips for Success

1. **Start with seed keywords** that describe your core offering
2. **Don't ignore long-tail** - they often have highest conversion rates
3. **Match content to intent** - informational queries need guides, not sales pages
4. **Group into clusters** for topical authority
5. **Prioritize quick wins** to build momentum and credibility
6. **Include GEO keywords** in your strategy for AI visibility
7. **Review quarterly** - keyword dynamics change over time
