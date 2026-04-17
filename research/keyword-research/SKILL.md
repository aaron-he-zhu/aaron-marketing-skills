---
name: keyword-research
description: 'Find high-value SEO keywords: search volume, difficulty, intent classification, topic clusters. 关键词研究/内容选题'
version: "9.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when starting keyword research for a new page, topic, or campaign. Also when the user asks about search volume, keyword difficulty, topic clusters, long-tail keywords, or what to write about."
argument-hint: "<topic or seed keyword> [market/language]"
metadata:
  author: aaron-he-zhu
  version: "9.0.0"
  geo-relevance: "medium"
  tags:
    - seo
    - geo
    - keywords
    - keyword-research
    - search-volume
    - keyword-difficulty
    - topic-clusters
    - long-tail-keywords
    - search-intent
    - content-calendar
    - ahrefs
    - semrush
    - google-keyword-planner
    - 关键词研究
    - SEO关键词
    - キーワード調査
    - 키워드분석
    - palabras-clave
  triggers:
    # EN-formal
    - "keyword research"
    - "find keywords"
    - "keyword analysis"
    - "keyword discovery"
    - "search volume analysis"
    - "keyword difficulty"
    - "topic research"
    - "identify ranking opportunities"
    # EN-casual
    - "what should I write about"
    - "what are people searching for"
    - "what are people googling"
    - "find me topics to write"
    - "give me keyword ideas"
    - "which keywords should I target"
    - "why is my traffic low"
    - "I need content ideas"
    # EN-question
    - "how do I find good keywords"
    - "what keywords should I target"
    - "how competitive is this keyword"
    # EN-competitor
    - "Ahrefs keyword explorer alternative"
    - "Semrush keyword magic tool"
    - "Google Keyword Planner alternative"
    - "Ubersuggest alternative"
    # ZH-pro
    - "关键词研究"
    - "关键词分析"
    - "搜索量查询"
    - "关键词难度"
    - "SEO关键词"
    - "长尾关键词"
    - "词库整理"
    - "关键词布局"
    - "关键词挖掘"
    # ZH-casual
    - "写什么内容好"
    - "找选题"
    - "帮我挖词"
    - "不知道写什么"
    - "查关键词"
    - "选词"
    - "帮我找词"
    # JA
    - "キーワード調査"
    - "キーワードリサーチ"
    - "SEOキーワード分析"
    - "検索ボリューム"
    - "ロングテールキーワード"
    - "検索意図分析"
    # KO
    - "키워드 리서치"
    - "키워드 분석"
    - "검색량 분석"
    - "키워드 어떻게 찾아요?"
    - "검색어 분석"
    - "경쟁도 낮은 키워드는?"
    # ES
    - "investigación de palabras clave"
    - "análisis de palabras clave"
    - "volumen de búsqueda"
    - "posicionamiento web"
    - "cómo encontrar palabras clave"
    # PT
    - "pesquisa de palavras-chave"
    # Misspellings
    - "keywrod research"
    - "keywork research"
---

# Keyword Research


> **[SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)
> **System Mode**: This research skill follows the shared [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) and [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md).


Discovers, analyzes, and prioritizes keywords for SEO and GEO content strategies. Identifies high-value opportunities based on search volume, competition, intent, and business relevance.

**System role**: Research layer skill. It turns market signals into reusable strategic inputs for the rest of the library.

## When This Must Trigger

Use this when the conversation involves reusable market intelligence that should influence strategy — even if the user doesn't use SEO terminology:

- Starting a new content strategy or campaign
- Expanding into new topics or markets
- Finding keywords for a specific product or service
- Identifying long-tail keyword opportunities
- Understanding search intent for your industry
- Planning content calendars
- Researching keywords for GEO optimization

## What This Skill Does

1. **Keyword Discovery**: Generates comprehensive keyword lists from seed terms
2. **Intent Classification**: Categorizes keywords by user intent (informational, navigational, commercial, transactional)
3. **Difficulty Assessment**: Evaluates competition level and ranking difficulty
4. **Opportunity Scoring**: Prioritizes keywords by potential ROI
5. **Clustering**: Groups related keywords into topic clusters
6. **GEO Relevance**: Identifies keywords likely to trigger AI responses

## Quick Start

Start with one of these prompts. Finish with a short handoff summary using the repository format in [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md).

### Basic Keyword Research

```
Research keywords for [topic/product/service]
```

```
Find keyword opportunities for a [industry] business targeting [audience]
```

### With Specific Goals

```
Find low-competition keywords for [topic] with commercial intent
```

```
Identify question-based keywords for [topic] that AI systems might answer
```

### Competitive Research

```
What keywords is [competitor URL] ranking for that I should target?
```

## Skill Contract

**Expected output**: a prioritized research brief, evidence-backed findings, and a short handoff summary ready for `memory/research/`.

- **Reads**: user goals, target market inputs, available tool data, and prior strategy from [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) and the shared [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) when available.
- **Writes**: a user-facing research deliverable plus a reusable summary that can be stored under `memory/research/`.
- **Promotes**: durable keyword priorities, competitor facts, entity candidates, and strategic decisions to `memory/hot-cache.md`, `memory/decisions.md`, and `memory/research/`; hand canonical entity work to `entity-optimizer`.
- **Next handoff**: use the `Next Best Skill` below when the findings are ready to drive action.

### Handoff Summary

Emit this shape when finishing the skill (see [skill-contract.md §Handoff Summary Format](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) for the authoritative format):

- **Status**: DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_INPUT
- **Objective**: what was analyzed, created, or fixed
- **Key Findings / Output**: the highest-signal result
- **Evidence**: URLs, data points, or sections reviewed
- **Open Loops**: blockers, missing inputs, or unresolved risks
- **Recommended Next Skill**: one primary next move

## Data Sources

> **Note:** All integrations are optional. This skill works without any API keys — users provide data manually when no tools are connected.

> See [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md) for tool category placeholders.

**With ~~SEO tool + ~~search console connected:**
Automatically pull historical search volume data, keyword difficulty scores, SERP analysis, current rankings from ~~search console, and competitor keyword overlap. The skill will fetch seed keyword metrics, related keyword suggestions, and search trend data.

**With manual data only:**
Ask the user to provide:
1. Seed keywords or topic description
2. Target audience and geographic location
3. Business goals (traffic, leads, sales)
4. Current domain authority (if known) or site age
5. Any known keyword performance data or search volume estimates

Proceed with the full analysis using provided data. Note in the output which metrics are from automated collection vs. user-provided data.

## Instructions

When a user requests keyword research, run eight phases (announce each as `[Phase X/8: Name]`):

1. **Scope** — clarify product, audience, business goal, DR, geography, language
2. **Discover** — seed from core/problem/solution/audience/industry terms
3. **Variations** — expand with modifier and long-tail patterns
4. **Classify** — tag each by intent (informational/navigational/commercial/transactional)
5. **Score** — assign difficulty (1-100) and compute `Opportunity = (Volume × Intent Value) / Difficulty` with Intent Value 1/1/2/3
6. **GEO-Check** — flag AI-answer-friendly queries (questions, definitions, comparisons, lists, how-tos)
7. **Cluster** — group keywords into pillar + cluster topic hubs
8. **Deliver** — Executive Summary, Quick Wins / Growth / GEO opportunities, Topic Clusters, Content Calendar, Next Steps

**Quality bar** — every recommendation must include at least one specific number. Generic advice like "target long-tail keywords for better results" must be rewritten as "Target 'project management for nonprofits' (vol: 320, KD: 22) — no DR>40 sites in top 10" before including.

> **Reference**: See [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/instructions-detail.md) for the full 8-phase templates, expansion patterns, intent classification table, difficulty tiers, opportunity matrix, GEO indicators, cluster template, deliverable quality bar with actionable vs. generic examples, and tips.

## Validation Checkpoints

### Input Validation
- [ ] Seed keywords or topic description clearly provided
- [ ] Target audience and business goals specified
- [ ] Geographic and language targeting confirmed
- [ ] Domain authority or site maturity level established

### Output Validation
- [ ] Every recommendation cites specific data points (not generic advice)
- [ ] Search volume and difficulty scores included for each keyword
- [ ] Keywords grouped by intent and mapped to content types
- [ ] Topic clusters show clear pillar-to-cluster relationships
- [ ] Source of each data point clearly stated (~~SEO tool data, user-provided, or estimated)

## Example

**User**: "Research keywords for a project management software company targeting small businesses"

**Output** (abbreviated): 150+ keywords analyzed, 23 high-priority opportunities with ~45K/month traffic potential across 3 focus areas (task management workflows, team collaboration, small business productivity). Quick Wins prioritized by KD × volume × intent fit.

> **Reference**: See [references/example-report.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/example-report.md) for the full report for "project management software for small businesses".

### Advanced Usage

Intent Mapping, Seasonal Analysis, Competitor Gap, Local Keywords — see [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/instructions-detail.md#advanced-usage).

## Tips for Success

Start with seeds; don't ignore long-tail; match intent; cluster for topical authority; prioritize quick wins; include GEO keywords; review quarterly. See [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/instructions-detail.md#tips-for-success).


### Save Results

After delivering findings to the user, ask:

> "Save these results for future sessions?"

If yes, write a dated summary to `memory/research/keyword-research/YYYY-MM-DD-<topic>.md` containing:
- One-line headline finding
- Top 3-5 actionable items
- Open loops or blockers
- Source data references

If any findings should influence ongoing strategy, recommend promoting key conclusions to `memory/hot-cache.md`.

## Reference Materials

- [Instructions Detail](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/instructions-detail.md) — Full 8-phase workflow, expansion patterns, scoring, cluster templates, advanced usage, tips
- [Keyword Intent Taxonomy](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/keyword-intent-taxonomy.md) — Complete intent classification with signal words and content strategies
- [Topic Cluster Templates](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/topic-cluster-templates.md) — Hub-and-spoke architecture templates for pillar and cluster content
- [Keyword Prioritization Framework](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/keyword-prioritization-framework.md) — Priority scoring matrix, categories, and seasonal keyword patterns
- [Example Report](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/keyword-research/references/example-report.md) — Complete example keyword research report for project management software

## Next Best Skill

- **Primary**: [competitor-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/competitor-analysis/SKILL.md) — turn keyword opportunities into a competitive benchmark.
- **Also consider** (pick by goal):
  - [content-gap-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/SKILL.md) — if competitors are already known and the goal is producing content fast.
  - [serp-analysis](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/serp-analysis/SKILL.md) — if SERP features (featured snippets, PAA, AI Overviews) must be understood before writing.
