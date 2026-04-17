---
name: geo-content-optimizer
description: 'Optimize content for AI citations in ChatGPT, Perplexity, AI Overviews, Gemini, Claude. AI引用优化/GEO优化/AI搜索'
version: "9.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when optimizing content for AI engines like ChatGPT, Perplexity, AI Overviews, Gemini, Claude, or Copilot. Also for AI citation optimization and generative engine visibility."
argument-hint: "<content URL or text> [target AI engine]"
metadata:
  author: aaron-he-zhu
  version: "9.0.0"
  geo-relevance: "high"
  tags:
    - geo
    - ai-citations
    - chatgpt-optimization
    - perplexity-optimization
    - google-ai-overview
    - gemini
    - generative-engine-optimization
    - llm-citations
    - ai-seo
    - quotable-content
    - AI引用优化
    - GEO优化
    - AI最適化
    - AI최적화
    - optimizacion-ia
  triggers:
    # EN-formal
    - "optimize for AI"
    - "get cited by ChatGPT"
    - "AI optimization"
    - "appear in AI answers"
    - "GEO optimization"
    - "generative engine optimization"
    - "AI-friendly content"
    - "LLM citations"
    # EN-casual
    - "get cited by AI"
    - "show up in ChatGPT answers"
    - "AI doesn't mention my brand"
    - "make content AI-quotable"
    - "how do I get AI to mention me"
    - "ChatGPT doesn't know my brand"
    # EN-question
    - "how to appear in AI answers"
    - "how to get cited by AI"
    - "why doesn't AI mention my brand"
    # EN-competitor
    - "Perplexity optimization"
    - "how to rank in ChatGPT answers"
    - "AI Overview optimization tool"
    # ZH-pro
    - "AI引用优化"
    - "GEO优化"
    - "生成式引擎优化"
    - "AI搜索优化"
    - "AI可引用内容"
    # ZH-casual
    - "让AI引用我"
    - "ChatGPT搜不到我"
    - "AI不提我的品牌"
    - "怎么让AI推荐我"
    - "AI搜不到"
    # JA
    - "AIコンテンツ最適化"
    - "AI引用されるコンテンツ"
    - "ChatGPT対策"
    - "AI検索最適化"
    # KO
    - "AI 최적화"
    - "AI 검색 최적화"
    - "ChatGPT 인용"
    # ES
    - "optimización para IA"
    - "aparecer en respuestas de IA"
    - "citación de IA"
    # PT
    - "otimização para IA"
    - "aparecer nas respostas da IA"
    # Misspellings
    - "generative engine optimisation"
    - "GEO optimisation"
---

# GEO Content Optimizer

> **[SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)
> **System Mode**: This build skill follows the shared [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) and [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md).


This skill optimizes content to appear in AI-generated responses. As AI systems increasingly answer user queries directly, getting cited by these systems directly impacts visibility.

**System role**: Build layer skill. It turns briefs and signals into assets that other skills can review, publish, and monitor.

## When This Must Trigger

Use this when the conversation involves a shippable asset or transformation that should feed directly into quality review, deployment, or monitoring — even if the user doesn't use SEO terminology:

- Optimizing existing content for AI citations
- Creating new content designed for both SEO and GEO
- Improving chances of appearing in AI Overviews
- Making content more quotable by AI systems
- Adding authority signals that AI systems trust
- Structuring content for AI comprehension
- Competing for visibility in the AI-first search era

## What This Skill Does

1. **Citation Optimization**: Makes content more likely to be quoted by AI
2. **Structure Enhancement**: Formats content for AI comprehension
3. **Authority Building**: Adds signals that AI systems trust
4. **Factual Enhancement**: Improves accuracy and verifiability
5. **Quote Creation**: Creates memorable, citeable statements
6. **Source Attribution**: Adds proper citations that AI can verify
7. **GEO Scoring**: Evaluates content's AI-friendliness

## Quick Start

Start with one of these prompts. Finish with a short handoff summary using the repository format in [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md).

### Optimize Existing Content

```
Optimize this content for GEO/AI citations: [content or URL]
```

```
Make this article more likely to be cited by AI systems
```

### Create GEO-Optimized Content

```
Write content about [topic] optimized for both SEO and GEO
```

### GEO Audit

```
Audit this content for GEO readiness and suggest improvements
```

### AI Overview Recovery (traffic lost to SERP AI answers)

```
AI Overview is eating clicks on 12 head queries — build a recovery plan
```

See [references/ai-overview-recovery.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/ai-overview-recovery.md) for the 4-phase playbook (measure → diagnose → rewrite → monitor) tailored to recovery scenarios (as opposed to generic GEO optimization).

## Skill Contract

**Expected output**: a ready-to-use asset or implementation-ready transformation plus a short handoff summary ready for `memory/content/`.

- **Reads**: the brief, target keywords, entity inputs, quality constraints, and prior decisions from [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) and the shared [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) when available. **Canonical entity profiles**: if the content mentions a brand / person / product, this skill MUST consult `memory/entities/<slug>.md` (per the [entity-geo handoff schema](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/entity-geo-handoff-schema.md)) to populate `display_name`, `description_short`, `ai_resolution_status` and decide whether disambiguation boilerplate is needed. If the profile is missing or stale (>90 days), declare `DONE_WITH_CONCERNS` and recommend `entity-optimizer` as an open loop.
- **Writes**: a user-facing content, metadata, or schema deliverable plus a reusable summary that can be stored under `memory/content/`.
- **Promotes**: approved angles, messaging choices, missing evidence, and publish blockers to `memory/hot-cache.md`, `memory/decisions.md`, and `memory/open-loops.md`.
- **Next handoff**: use the `Next Best Skill` below when the asset is ready for review or deployment.

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

> **Note:** All integrations are optional. This skill works without any API keys — users provide data manually when no tools are connected.

**With ~~AI monitor + ~~SEO tool connected:**
Automatically pull AI citation patterns (which content is being cited by ChatGPT, Claude, Perplexity), current AI visibility scores, competitor citation frequency, and AI Overview appearance tracking.

**With manual data only:**
Ask the user to provide:
1. Target queries where they want AI citations
2. Current content URL or full content text
3. Any known instances where competitors are being cited by AI

Proceed with the full workflow using provided data. Note in the output which metrics are from automated collection vs. user-provided data.

## Instructions

When a user requests GEO optimization, run these five steps:

1. **Load CORE-EEAT GEO-First Targets** — Top 6 priority items (C02, C09, O03, O05, E01, O02) plus the full GEO-First set; consult the AI Engine Preferences table for engine-specific tuning
2. **Analyze Current Content** — score 8 GEO factors (clear definitions, quotable statements, factual density, source citations, Q&A format, authority signals, content freshness, structure clarity); identify weaknesses and quick wins
3. **Apply GEO Optimization Techniques** — 6 core techniques: definition optimization (25-50 words, standalone), quotable statements (specific stats with sources), authority signals (expert quotes, citations), structure (Q&A, tables, lists), factual density (specific data vs. vague claims), FAQ schema (JSON-LD FAQPage matching visible content)
4. **Generate GEO-Optimized Output** — report Changes Made, Before/After GEO score comparison, AI Query Coverage
5. **CORE-EEAT GEO Self-Check** — verify 14 GEO-First items (C02, C04, C09, O02, O03, O05, O06, R01, R02, R04, R07, E01, Exp10, Ept08) with Pass/Warn/Fail

> **Reference**: See [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/instructions-detail.md) for the full CORE-EEAT GEO target tables, AI engine preferences, analysis templates, optimization report template, self-check matrix, and examples.

## Validation Checkpoints

### Input Validation
- [ ] Content source identified (URL, full text, or content draft)
- [ ] Target AI queries or topics clearly defined
- [ ] Current GEO baseline assessed (if optimizing existing content)

### Output Validation
- [ ] **Banned-vocab self-check** — scan output for banned words/phrases per [skill-contract.md §Output Voice](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md). Replace any hit with a concrete alternative.
- [ ] At least 3 clear, quotable definitions added
- [ ] Factual density improved with at least 5 verifiable statistics
- [ ] All claims have source citations from authoritative sources
- [ ] Q&A format sections cover top 5 user queries
- [ ] GEO score improvement of at least 50% from baseline
- [ ] Source of each data point clearly stated (~~AI monitor data, user-provided, or estimated)

## Example

**User**: "Optimize this paragraph for GEO: 'Email marketing is a good way to reach customers. It's been around for a while and many businesses use it.'"

**Output** adds a clear definition, stats with DMA/Emarsys citations, structured list, and quotable facts — lifting GEO Score from 1/10 to 8/10. See the full before/after in [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/instructions-detail.md#example).

## GEO Optimization Checklist

> **Reference**: See the GEO Readiness Checklist in [references/geo-optimization-techniques.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/geo-optimization-techniques.md) for the full checklist covering definitions, quotable content, authority, structure, and technical elements.

## Tips for Success

Answer first; be specific; cite sources; stay current; match query format; build authority. Full list in [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/instructions-detail.md#tips-for-success).


### Save Results

After delivering content or optimization output to the user, ask:

> "Save these results for future sessions?"

If yes, write a dated summary to `memory/content/YYYY-MM-DD-<topic>.md` containing:
- One-line description of what was created
- Target keyword and content type
- Open loops or items needing review
- Source data references

**Gate check recommended**: Run content-quality-auditor before publishing (PostToolUse hook will remind automatically).

If any findings should influence ongoing strategy, recommend promoting key conclusions to `memory/hot-cache.md`.

## Reference Materials

- [Instructions Detail](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/instructions-detail.md) - Full 5-step workflow, CORE-EEAT GEO targets, self-check matrix, worked example, tips
- [GEO Optimization Techniques](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/geo-optimization-techniques.md) - Detailed before/after examples, templates, and checklists for each technique
- [AI Citation Patterns](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/ai-citation-patterns.md) - How Google AI Overviews, ChatGPT, Perplexity, and Claude select and cite sources
- [Quotable Content Examples](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/quotable-content-examples.md) - Before/after examples of content optimized for AI citation

## Next Best Skill

- **Primary**: [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) — verify the optimized content is strong enough to ship and cite.
