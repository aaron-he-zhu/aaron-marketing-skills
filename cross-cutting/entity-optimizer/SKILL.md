---
name: entity-optimizer
description: 'Build entity presence in Knowledge Graph, Wikidata, AI systems for brand recognition and citations. 实体优化/知识图谱'
version: "9.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when optimizing entity presence for Knowledge Graph, Wikidata, or AI engine disambiguation. Also for brand entity canonicalization."
argument-hint: "<entity name or brand>"
metadata:
  author: aaron-he-zhu
  version: "9.0.0"
  geo-relevance: "high"
  tags:
    - seo
    - geo
    - entity-optimization
    - knowledge-graph
    - knowledge-panel
    - brand-entity
    - wikidata
    - entity-disambiguation
    - 实体优化
    - エンティティ
    - 엔티티
    - entidad-seo
  triggers:
    # EN-formal
    - "optimize entity presence"
    - "build knowledge graph"
    - "improve knowledge panel"
    - "entity audit"
    - "establish brand entity"
    - "entity disambiguation"
    # EN-casual
    - "Google doesn't know my brand"
    - "no knowledge panel"
    - "establish my brand"
    - "establish my brand as an entity"
    - "get a Google knowledge card"
    - "no Wikipedia entry"
    # EN-question
    - "how to get a knowledge panel"
    - "how to build brand entity"
    # ZH-pro
    - "实体优化"
    - "知识图谱"
    - "品牌实体"
    - "知识面板"
    - "品牌词"
    - "品牌词优化"
    # ZH-casual
    - "品牌搜不到"
    - "没有知识面板"
    - "Google不认识我的品牌"
    # JA
    - "エンティティ最適化"
    - "ナレッジパネル"
    # KO
    - "엔티티 최적화"
    - "지식 패널"
    - "구글이 내 브랜드 모르는데?"
    - "지식 패널 만들려면?"
    # ES
    - "optimización de entidad"
    - "panel de conocimiento"
    # PT
    - "otimização de entidade"
    # Misspellings
    - "knowlege panel"
    - "enity optimization"
---

# Entity Optimizer


> **[SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)
> **System Mode**: This cross-cutting skill is part of the protocol layer and follows the shared [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) and [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md).


Audits, builds, and maintains entity identity across search engines and AI systems. Entities — the people, organizations, products, and concepts that search engines and AI systems recognize as distinct things — are the foundation of how both Google and LLMs decide *what a brand is* and *whether to cite it*.

**Why entities matter for SEO + GEO:**

- **SEO**: Google's Knowledge Graph powers Knowledge Panels, rich results, and entity-based ranking signals. A well-defined entity earns SERP real estate.
- **GEO**: AI systems resolve queries to entities before generating answers. If an AI cannot identify an entity, it cannot cite it — no matter how good the content is.

**System role**: Canonical Entity Profile. It acts as the source of truth for entity identity, associations, and disambiguation across the library.

## When This Must Trigger

Use this when brand or entity identity needs to be established or verified — even if the user doesn't use entity terminology:

- User says "Google doesn't know my brand" or "no knowledge panel"
- Auto-recommended when `memory/entities/candidates.md` accumulates 3 or more uncanonized entity candidates from other skills
- Establishing a new brand/person/product as a recognized entity
- Auditing current entity presence across Knowledge Graph, Wikidata, and AI systems
- Improving or correcting a Knowledge Panel
- Building entity associations (entity ↔ topic, entity ↔ industry)
- Resolving entity disambiguation issues (your entity confused with another)
- Strengthening entity signals for AI citation
- After launching a new brand, product, or organization
- Preparing for a site migration (preserving entity identity)
- Running periodic entity health checks

## What This Skill Does

1. **Entity Audit**: Evaluates current entity presence across search and AI systems
2. **Knowledge Graph Analysis**: Checks Google Knowledge Graph, Wikidata, and Wikipedia status
3. **AI Entity Resolution Test**: Queries AI systems to see how they identify and describe the entity
4. **Entity Signal Mapping**: Identifies all signals that establish entity identity
5. **Gap Analysis**: Finds missing or weak entity signals
6. **Entity Building Plan**: Creates actionable plan to establish or strengthen entity presence
7. **Disambiguation Strategy**: Resolves confusion with similarly-named entities

## Quick Start

Start with one of these prompts. Finish with a canonical entity profile and a handoff summary using the repository format in [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md).

### Entity Audit

```
Audit entity presence for [brand/person/organization]
```

```
How well do search engines and AI systems recognize [entity name]?
```

### Build Entity Presence

```
Build entity presence for [new brand] in the [industry] space
```

```
Establish [person name] as a recognized expert in [topic]
```

### Fix Entity Issues

```
My Knowledge Panel shows incorrect information — fix entity signals for [entity]
```

```
AI systems confuse [my entity] with [other entity] — help me disambiguate
```

## Skill Contract

**Expected output**: an entity audit, a canonical entity profile, and a short handoff summary ready for `memory/entities/`.

- **Reads**: the entity name, primary domain, known profiles, topic associations, and prior brand context from [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) and the shared [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) when available.
- **Writes**: a user-facing entity report plus a reusable profile that can be stored under `memory/entities/`.
- **Promotes**: canonical names, sameAs links, disambiguation notes, and entity gaps to `memory/hot-cache.md`, `memory/entities/`, and `memory/open-loops.md`.

This skill is the sole writer of canonical entity profiles at `memory/entities/<name>.md`. Other skills write entity candidates to `memory/entities/candidates.md` only. When 3+ candidates accumulate, this skill should be recommended.

**Profile schema**: the frontmatter of every canonical entity profile follows the authoritative contract in [references/entity-geo-handoff-schema.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/entity-geo-handoff-schema.md). That schema defines which fields downstream skills (`geo-content-optimizer`, `schema-markup-generator`, `meta-tags-optimizer`, `ai-overview-recovery`) depend on. Do not omit required fields — the consumers will degrade gracefully to `DONE_WITH_CONCERNS` and surface an `open_loop` pointing back here.

- **Next handoff**: use the `Next Best Skill` below once the entity truth is clear.

### Handoff Summary

Emit this shape when finishing the skill (see [skill-contract.md §Handoff Summary Format](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) for the authoritative format):

- **Status**: DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_INPUT
- **Objective**: what was analyzed, created, or fixed
- **Key Findings / Output**: the highest-signal result
- **Evidence**: URLs, data points, or sections reviewed
- **Open Loops**: blockers, missing inputs, or unresolved risks
- **Recommended Next Skill**: one primary next move

## Data Sources

> See [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md) for tool category placeholders.

**With ~~knowledge graph + ~~SEO tool + ~~AI monitor + ~~brand monitor connected:**
Query Knowledge Graph API for entity status, pull branded search data from ~~SEO tool, test AI citation with ~~AI monitor, track brand mentions with ~~brand monitor.

**With manual data only:**
Ask the user to provide:
1. Entity name, type (Person, Organization, Brand, Product, Creative Work, Event)
2. Primary website / domain
3. Known existing profiles (Wikipedia, Wikidata, social media, industry directories)
4. Top 3-5 topics/industries the entity should be associated with
5. Any known disambiguation issues (other entities with same/similar name)

Without tools, Claude provides entity optimization strategy and recommendations based on information the user provides. The user must run search queries, check Knowledge Panels, and test AI responses to supply the raw data for analysis.

Proceed with the audit using public search results, AI query testing, and SERP analysis. Note which items require tool access for full evaluation.

## Instructions

When a user requests entity optimization:

2. **GDPR Art 6 lawful-basis prompt (for third-party persons, EU/EEA/UK data subjects)** — if the entity being canonicalized is an individual (founder, author, public figure) and may be an EU/EEA/UK resident, the skill MUST prompt the user before writing to `memory/entities/`: "You are about to create a canonical profile for a person. If this person is or may be an EU/EEA/UK resident, GDPR Art 6 requires a lawful basis: (1) consent, (2) legitimate interest, (3) contract, (4) other. For non-EU subjects, check local regimes (CCPA/CPRA, PIPEDA, LGPD, etc.). If unsure, skip and return NEEDS_INPUT." Only proceed if user confirms a basis. Advisory only — not legal advice. Reference: [memory-management §GDPR / Privacy Compliance](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md).

### Step 1: Entity Discovery

Establish the entity's current state across all systems.

```markdown
### Entity Profile

**Entity Name**: [name]
**Entity Type**: [Person / Organization / Brand / Product / Creative Work / Event]
**Primary Domain**: [URL]
**Target Topics**: [topic 1, topic 2, topic 3]

#### Current Entity Presence

| Platform | Status | Details |
|----------|--------|---------|
| Google Knowledge Panel | ✅ Present / ❌ Absent / ⚠️ Incorrect | [details] |
| Wikidata | ✅ Listed / ❌ Not listed | [QID if exists] |
| Wikipedia | ✅ Article / ⚠️ Mentioned only / ❌ Absent | [notability assessment] |
| Google Knowledge Graph API | ✅ Entity found / ❌ Not found | [entity ID, types, score] |
| Schema.org on site | ✅ Complete / ⚠️ Partial / ❌ Missing | [Organization/Person/Product schema] |

#### AI Entity Resolution Test

**Note**: Claude cannot directly query other AI systems or perform real-time web searches without tool access. When running without ~~AI monitor or ~~knowledge graph tools, ask the user to run these test queries and report the results, or use the user-provided information to assess entity presence.

Test how AI systems identify this entity by querying:
- "What is [entity name]?"
- "Who founded [entity name]?" (for organizations)
- "What does [entity name] do?"
- "[entity name] vs [competitor]"

| AI System | Recognizes Entity? | Description Accuracy | Cites Entity's Content? |
|-----------|-------------------|---------------------|------------------------|
| ChatGPT | ✅ / ⚠️ / ❌ | [accuracy notes] | [yes/no/partially] |
| Claude | ✅ / ⚠️ / ❌ | [accuracy notes] | [yes/no/partially] |
| Perplexity | ✅ / ⚠️ / ❌ | [accuracy notes] | [yes/no/partially] |
| Google AI Overview | ✅ / ⚠️ / ❌ | [accuracy notes] | [yes/no/partially] |
```

### Step 2: Entity Signal Audit

Evaluate entity signals across 6 categories. For the detailed 47-signal checklist with verification methods, see [references/entity-signal-checklist.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/entity-signal-checklist.md).

Evaluate each signal as Pass / Fail / Partial with a specific action for each gap. The 6 categories are:

1. **Structured Data Signals** -- Organization/Person schema, sameAs links, @id consistency, author schema
2. **Knowledge Base Signals** -- Wikidata, Wikipedia, CrunchBase, industry directories
3. **Consistent NAP+E Signals** -- Name/description/logo/social consistency across platforms
4. **Content-Based Entity Signals** -- About page, author pages, topical authority, branded backlinks
5. **Third-Party Entity Signals** -- Authoritative mentions, co-citation, reviews, press coverage
6. **AI-Specific Entity Signals** -- Clear definitions, disambiguation, verifiable claims, crawlability

> **Reference**: Use the audit template in [references/entity-signal-checklist.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/entity-signal-checklist.md) for the full 47-signal checklist with verification methods for each category.

### Step 3: Report & Action Plan

Produce an Entity Optimization Report with: overview (entity/type/date), signal category summary (6-category ✅/⚠️/❌ table with findings), critical issues, top 5 priority actions (impact × effort), entity building roadmap (Week 1-2 → Month 1 → Month 2-3 → Ongoing), and CORE-EEAT A07/A08 + CITE I01-I10 cross-reference.

> **Reference**: See [references/entity-signal-checklist.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/entity-signal-checklist.md) for the full Step 3 report template.

### Save Results

After delivering findings to the user, ask:

> "Save these results for future sessions?"

If yes, write a dated summary to the appropriate `memory/` path using filename `YYYY-MM-DD-<topic>.md` containing:
- One-line verdict or headline finding
- Top 3-5 actionable items
- Open loops or blockers
- Source data references

If any veto-level issue was found (CORE-EEAT T04, C01, R10 or CITE T03, T05, T09), also append a one-liner to `memory/hot-cache.md` without asking.

## Validation Checkpoints

### Input Validation
- [ ] Entity name and type identified
- [ ] Primary domain/website confirmed
- [ ] Target topics/industries specified
- [ ] Disambiguation context provided (if entity name is common)

### Output Validation
- [ ] All 6 signal categories evaluated
- [ ] AI entity resolution tested with at least 3 queries
- [ ] Knowledge Panel status checked
- [ ] Wikidata/Wikipedia status verified
- [ ] Schema.org markup on primary site audited
- [ ] Every recommendation is specific and actionable
- [ ] Roadmap includes concrete steps with timeframes
- [ ] Cross-reference with CORE-EEAT A07/A08 and CITE I01-I10 noted

## Example

**User**: "Audit entity presence for Acme Analytics, our B2B SaaS analytics platform at acme-analytics.example"

**Output** (abbreviated): AI resolution test shows partial recognition — ChatGPT described it as a generic "analytics tool" without B2B specificity; not listed among enterprise analytics players; founder unknown to AI systems. Health summary flags missing Wikidata entry, no Knowledge Panel, and 3 priority actions — Wikidata submission, sameAs links, and a founder-bio page.

> **Reference**: See [references/example-audit-report.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/example-audit-report.md) for the full entity audit report including AI resolution test results, entity health summary, top 3 priority actions, and CORE-EEAT/CITE cross-references.

## Tips for Success

> **Reference**: See [references/entity-signal-checklist.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/entity-signal-checklist.md) for the full 7-item Tips for Success list (start with Wikidata, leverage sameAs, test AI recognition before/after, compounding signals, consistency > completeness, disambiguation-first, pair with CITE I-dimension).

## Entity Type Reference

> **Reference**: See [references/entity-type-reference.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/entity-type-reference.md) for entity types with key signals, schemas, and disambiguation strategies by situation.

## Knowledge Panel & Wikidata Optimization

> **Reference**: See [references/knowledge-panel-wikidata-guide.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/knowledge-panel-wikidata-guide.md) for Knowledge Panel claiming/editing, common issues and fixes, Wikidata entry creation, key properties by entity type, and AI entity resolution optimization.

## Reference Materials

Detailed guides for entity optimization:
- [references/entity-signal-checklist.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/entity-signal-checklist.md) — Complete signal checklist with verification methods, Step 3 report template, and Tips for Success
- [references/knowledge-graph-guide.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/references/knowledge-graph-guide.md) — Wikidata, Wikipedia, and Knowledge Graph optimization playbook

## Next Best Skill

- **Primary**: [schema-markup-generator](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/schema-markup-generator/SKILL.md) — turn entity truth into machine-readable implementation.
- **Also consider**:
  - [geo-content-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md) — if the core gap is AI-engine recognition (ChatGPT / Perplexity don't know the brand).
  - [seo-content-writer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/seo-content-writer/SKILL.md) — if a new About / founder page is needed to establish the entity.
