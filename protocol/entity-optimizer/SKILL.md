---
name: entity-optimizer
description: 'Use when the user asks to "optimize entity presence"; builds Knowledge Graph, Wikidata, sameAs, and AI recognition signals for a canonical entity identity. Not for page-level AI-citation readiness — use geo-content-optimizer. 实体优化/知识图谱'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when optimizing entity presence for Knowledge Graph, Wikidata, or AI engine disambiguation. Also for brand entity canonicalization."
argument-hint: "<entity name or brand>"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: protocol
  phase: protocol
  geo-relevance: "high"
---

# Entity Optimizer

Audits, builds, and maintains entity identity across search engines and AI systems. Entities — the people, organizations, products, and concepts that search engines and AI systems recognize as distinct things — are the foundation of how both Google and LLMs decide *what a brand is* and *whether to cite it*.

**Why entities matter for SEO + GEO:**

- **SEO**: Google's Knowledge Graph powers Knowledge Panels, rich results, and entity-based ranking signals. A well-defined entity earns SERP real estate.
- **GEO**: AI systems resolve queries to entities before generating answers. If an AI cannot identify an entity, it cannot cite it — no matter how good the content is.

## What This Skill Does

Audits entity presence across Knowledge Graph, Wikidata, Wikipedia, and AI systems; maps all 6 signal categories (47 signals); produces a gap analysis, building plan, and disambiguation strategy.

## Quick Start

Start with one of these prompts. Finish with a canonical entity profile and a handoff summary using the repository format in [Skill Contract](../../references/skill-contract.md).

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

- **Reads**: the entity name, primary domain, known profiles, topic associations, and prior brand context.
- **Writes**: a user-facing entity report plus a reusable profile that can be stored under `memory/entities/`.
- **Promotes**: canonical names, sameAs links, disambiguation notes, and entity gaps to `memory/hot-cache.md`, `memory/entities/`, and `memory/open-loops.md`.
- **Done when**: the 6 signal categories are each scored Pass/Fail/Partial, the AI-resolution test is run (or flagged as user-to-run), and a canonical profile plus top-5 priority actions are produced.

This skill is the sole writer of canonical entity profiles at `memory/entities/<name>.md`. Other skills write entity candidates to `memory/entities/candidates.md` only. When 3+ candidates accumulate, this skill should be recommended.

**Profile schema**: the frontmatter of every canonical entity profile follows the authoritative contract in [Entity-GEO Handoff Schema](../../references/entity-geo-handoff-schema.md). That schema defines which fields downstream skills (`geo-content-optimizer` — including its [AI-overview-recovery playbook](../../build/geo-content-optimizer/references/ai-overview-recovery.md) — `serp-markup-builder`, `serp-markup-builder`) depend on. Do not omit required fields — the consumers will degrade gracefully to `DONE_WITH_CONCERNS` and surface an `open_loop` pointing back here.

- **Primary next skill**: use the `Next Best Skill` below once the entity truth is clear.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

With tools: query Knowledge Graph API, ~~SEO tool, ~~AI monitor, ~~brand monitor. Without tools: ask the user for entity name/type, domain, profiles, topics, and disambiguation context. See [CONNECTORS.md](../../CONNECTORS.md).

**Zero-dependency local helper** (keyless): `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/kg.py" reconcile "<entity>"` resolves the name to a Wikidata QID with a confidence score (does the open KG that feeds Knowledge Panels & AI answers recognize it?); `kg.py entity <QID>` returns claims + sameAs. See [scripts/connectors/README.md](../../scripts/connectors/README.md).

## Decision Gates

**Stop and ask the user when:**
- No entity name is provided and none is inferable from project context — ask for the entity name and type before auditing.
- The entity is an individual (founder, author, public figure) who may be an EU/EEA/UK resident, before writing to `memory/entities/` — prompt: "You are about to create a canonical profile for a person. If this person is or may be an EU/EEA/UK resident, GDPR Art 6 requires a lawful basis: (1) consent, (2) legitimate interest, (3) contract, (4) other. For non-EU subjects, check local regimes (CCPA/CPRA, PIPEDA, LGPD, etc.). If unsure, skip and return NEEDS_INPUT." Only proceed once the user confirms a basis. Advisory only — not legal advice. Reference: [Memory Management — GDPR / Privacy Compliance](../memory-management/SKILL.md).

**Continue silently (never stop for):**
- Missing ~~AI monitor or ~~knowledge graph tool access — mark those rows as user-to-run and proceed with user-provided observations.
- Individual signals being unknown — score them Partial with a verification action and continue.

## Instructions

When a user requests entity optimization:

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

Evaluate entity signals across 6 categories. For the detailed 47-signal checklist with verification methods, see [Entity Signal Checklist](references/entity-signal-checklist.md).

Evaluate each signal as Pass / Fail / Partial with a specific action for each gap. The 6 categories are:

1. **Structured Data Signals** — Organization/Person schema, sameAs links, @id consistency, author schema
2. **Knowledge Base Signals** — Wikidata, Wikipedia, CrunchBase, industry directories
3. **Consistent NAP+E Signals** — Name/description/logo/social consistency across platforms
4. **Content-Based Entity Signals** — About page, author pages, topical authority, branded backlinks
5. **Third-Party Entity Signals** — Authoritative mentions, co-citation, reviews, press coverage
6. **AI-Specific Entity Signals** — Clear definitions, disambiguation, verifiable claims, crawlability

> **Reference**: Use the audit template in [Entity Signal Checklist](references/entity-signal-checklist.md) for the full 47-signal checklist with verification methods for each category.

### Step 3: Report & Action Plan

Produce an Entity Optimization Report with: overview (entity/type/date), signal category summary (6-category ✅/⚠️/❌ table with findings), critical issues, top 5 priority actions (impact × effort), entity building roadmap (Week 1-2 → Month 1 → Month 2-3 → Ongoing), and CORE-EEAT A07/A08 + CITE I01-I10 cross-reference.

> **Reference**: See [Entity Signal Checklist](references/entity-signal-checklist.md) for the full Step 3 report template.

### Save Results

Ask "Save these results for future sessions?" (see [Skill Contract](../../references/skill-contract.md) §Save Results Template) — if yes, write the canonical entity profile to `memory/entities/<entity-slug>.md` using the Profile schema above. If the entity is project-critical, also add a 1-3 line pointer to `memory/hot-cache.md`; do not save canonical profiles to the generic `memory/YYYY-MM-DD-<topic>.md` pattern.

Before writing any canonical profile, check `memory/audits/gdpr-purges.md` for a prior purge of this entity (by redacted label or domain). If one exists, do not silently recreate the profile; return `NEEDS_INPUT` and ask the user to confirm the entity should be re-added.

## Example

**User**: "Audit entity presence for Acme Analytics, our B2B SaaS analytics platform at acme-analytics.example"

**Output** (abbreviated): AI resolution test shows partial recognition — ChatGPT described it as a generic "analytics tool" without B2B specificity; not listed among enterprise analytics players; founder unknown to AI systems. Health summary flags a missing Wikidata entry and no Knowledge Panel, with priority actions covering Wikidata submission, sameAs links, and a founder-bio page.

> **Reference**: See [Example Audit Report](references/example-audit-report.md) for the full entity audit report including AI resolution test results, entity health summary, top 3 priority actions, and CORE-EEAT/CITE cross-references.

## Entity Type Reference

> **Reference**: See [Entity Type Reference](references/entity-type-reference.md) for entity types with key signals, schemas, and disambiguation strategies by situation.

## Knowledge Panel & Wikidata Optimization

> **Reference**: See [Knowledge Panel & Wikidata Guide](references/knowledge-panel-wikidata-guide.md) for Knowledge Panel claiming/editing, common issues and fixes, Wikidata entry creation, key properties by entity type, and AI entity resolution optimization.

## Reference Materials

Detailed guides for entity optimization:
- [Entity Signal Checklist](references/entity-signal-checklist.md) — Complete signal checklist with verification methods, Step 3 report template, and Tips for Success
- [Knowledge Graph Guide](references/knowledge-graph-guide.md) — Wikidata, Wikipedia, and Knowledge Graph optimization playbook
- [Agent-Readable File Stack (llms.txt / OKF)](../../references/llms-txt-okf.md) — agent-readable entity files (llms.txt, OKF); honestly flagged: no current ranking signal

## Next Best Skill

Primary: [serp-markup-builder](../../build/serp-markup-builder/SKILL.md). Also consider: [geo-content-optimizer](../../build/geo-content-optimizer/SKILL.md) (AI recognition gap) or [content-writer](../../build/content-writer/SKILL.md) (new About/founder page needed).
