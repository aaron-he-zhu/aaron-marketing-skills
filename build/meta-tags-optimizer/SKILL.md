---
name: meta-tags-optimizer
description: 'Optimize title tags, meta descriptions, Open Graph, Twitter cards for maximum CTR with A/B variations. 标题优化/元描述/CTR'
version: "9.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when optimizing title tags, meta descriptions, Open Graph tags, or Twitter Cards for a page."
argument-hint: "<page URL or content>"
metadata:
  author: aaron-he-zhu
  version: "9.0.0"
  geo-relevance: "low"
  tags:
    - seo
    - meta-tags
    - title-tag
    - meta-description
    - open-graph
    - twitter-card
    - ctr-optimization
    - social-sharing
    - 标题优化
    - 元描述
    - メタタグ
    - 메타태그
    - meta-tags-seo
  triggers:
    # EN-formal
    - "optimize title tag"
    - "write meta description"
    - "improve CTR"
    - "Open Graph tags"
    - "social media preview"
    - "title optimization"
    - "meta tags"
    - "Twitter cards"
    # EN-casual
    - "my title tag needs work"
    - "low click-through rate"
    - "fix my meta tags"
    - "OG tags not showing"
    - "social preview looks wrong"
    - "my click rate is low"
    # EN-question
    - "how to write a good title tag"
    - "how to improve click-through rate"
    - "what is a good meta description"
    # EN-competitor
    - "Yoast SEO title tool"
    - "RankMath title optimizer"
    # ZH-pro
    - "标题标签优化"
    - "元描述优化"
    - "OG标签"
    - "点击率提升"
    - "社交预览"
    - "TDK优化"
    # ZH-casual
    - "标题不好"
    - "点击率太低"
    - "社交分享预览不对"
    - "标题怎么写"
    - "TDK怎么写"
    # JA
    - "メタタグ最適化"
    - "タイトルタグ"
    - "CTR改善"
    # KO
    - "메타 태그 최적화"
    - "제목 태그"
    - "클릭률 개선"
    # ES
    - "optimizar meta tags"
    - "mejorar CTR"
    - "etiquetas Open Graph"
    # PT
    - "otimizar meta tags"
    # Misspellings
    - "meta discription"
    - "tittle tag"
---

# Meta Tags Optimizer

> **[SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)
> **System Mode**: This build skill follows the shared [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) and [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md).


This skill creates compelling, optimized meta tags that improve click-through rates from search results and enhance social media sharing. It covers title tags, meta descriptions, and social meta tags.

**System role**: Build layer skill. It turns briefs and signals into assets that other skills can review, publish, and monitor.

## When This Must Trigger

Use this when the conversation involves a shippable asset or transformation that should feed directly into quality review, deployment, or monitoring — even if the user doesn't use SEO terminology:

- Creating meta tags for new pages
- Optimizing existing meta tags for better CTR
- Preparing pages for social media sharing
- Fixing duplicate or missing meta tags
- A/B testing title and description variations
- Optimizing for specific SERP features
- Creating meta tags for different page types

## What This Skill Does

1. **Title Tag Creation**: Writes compelling, keyword-optimized titles
2. **Meta Description Writing**: Creates click-worthy descriptions
3. **Open Graph Optimization**: Prepares pages for social sharing
4. **Twitter Card Setup**: Optimizes Twitter-specific meta tags
5. **CTR Analysis**: Suggests improvements for better click rates
6. **Character Counting**: Ensures proper length for SERP display
7. **A/B Test Suggestions**: Provides variations for testing

## Quick Start

Start with one of these prompts. Finish with a short handoff summary using the repository format in [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md).

### Create Meta Tags

```
Create meta tags for a page about [topic] targeting [keyword]
```

```
Write title and meta description for this content: [content/URL]
```

### Optimize Existing Tags

```
Improve these meta tags for better CTR: [current tags]
```

### Social Media Tags

```
Create Open Graph and Twitter card tags for [page/URL]
```

## Skill Contract

**Expected output**: a ready-to-use asset or implementation-ready transformation plus a short handoff summary ready for `memory/content/`.

- **Reads**: the brief, target keywords, entity inputs, quality constraints, and prior decisions from [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) and the shared [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) when available.
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

**With ~~search console + ~~SEO tool connected:**
Automatically pull current meta tags, CTR data by query, competitor title/description patterns, SERP preview data, and impression/click metrics to identify optimization opportunities.

**With manual data only:**
Ask the user to provide:
1. Current title and meta description (if optimizing existing)
2. Target primary keyword and 2-3 secondary keywords
3. Page URL and main content/value proposition
4. Competitor URLs or examples of well-performing titles in the SERP

Proceed with the full workflow using provided data. Note in the output which metrics are from automated collection vs. user-provided data.

## Instructions

When a user requests meta tag optimization, run these six steps:

1. **Gather Page Information** — URL, page type, primary/secondary keywords, target audience, primary CTA, unique value prop
2. **Create Optimized Title Tag** — 50-60 chars, primary keyword front-loaded; pick from 5 formula options (Keyword|Benefit|Brand, Number+Keyword+Promise, How-to, Question, Year+Keyword); generate 3 options with power word analysis
3. **Write Meta Description** — 150-160 chars, primary keyword, CTA; use `[Offer] + [Benefit] + [CTA]` formula; generate 3 options with CTA and emotional trigger labels
4. **Create Open Graph, Twitter Card, and Additional Meta Tags** — OG (og:type/url/title/description/image), Twitter Card, canonical, robots, viewport, author, article tags; combine into full block
5. **CORE-EEAT Alignment Check** — verify C01 (Intent Alignment) and C02 (Direct Answer) with Pass/Warn/Fail
6. **Provide CTR Optimization Tips** — power words analysis, CTR boosting elements table (Numbers +20-30%, Year +15-20%, Power Words +10-15%, Question +10-15%, Brackets +10%), A/B test suggestions

> **Reference**: See [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/instructions-detail.md) for full templates (page analysis, title/description formula options, CORE-EEAT alignment matrix, CTR optimization analysis), worked example, and tips. See [references/meta-tag-code-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/meta-tag-code-templates.md) for HTML code templates.

## Validation Checkpoints

### Input Validation
- [ ] Primary keyword confirmed and matches page content
- [ ] Page type identified (blog/product/landing/service/homepage)
- [ ] Target audience and search intent clearly defined
- [ ] Unique value proposition articulated

### Output Validation
- [ ] **Banned-vocab self-check** — scan titles and descriptions for banned words/phrases per [skill-contract.md §Output Voice](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md). Especially: `crucial, robust, leverage, seamless, unlock, cutting-edge, empower, streamline`. Meta tags are short — every word counts.
- [ ] Title length 50-60 characters (displays fully in SERP)
- [ ] Meta description length 150-160 characters
- [ ] Primary keyword appears in both title and description
- [ ] Open Graph image specified (1200x630px recommended)
- [ ] All HTML syntax valid (no unclosed quotes or tags)
- [ ] Source of each data point clearly stated (~~search console CTR data, ~~SEO tool competitor data, user-provided, or estimated)

## Example

**User**: "Create meta tags for a blog post about 'how to start a podcast in [current year]'"

**Output** (abbreviated):
- Title: `<title>How to Start a Podcast in [year]: Complete Beginner's Guide</title>` (~55 chars, keyword front-loaded, power words: Complete, Beginner's)
- Description: `<meta name="description" content="Learn how to start a podcast in [year] with our step-by-step guide. Covers equipment, hosting, recording, and launching your first episode. Start podcasting today!">` (~163 chars, CTA included)

See the full example (with OG, Twitter, Article tags and 3 A/B variations) in [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/instructions-detail.md#example).

## Tips for Success

Front-load keywords; match intent; be specific; test variations; update regularly; check competitors. Full list in [references/instructions-detail.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/instructions-detail.md#tips-for-success).


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

- [Instructions Detail](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/instructions-detail.md) — Full 6-step workflow, title/description formulas, CORE-EEAT alignment matrix, CTR analysis, worked example, tips
- [Meta Tag Formulas](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/meta-tag-formulas.md) — Proven title and description formulas
- [Meta Tag Code Templates](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/meta-tag-code-templates.md) — HTML templates (OG, Twitter, article tags)
- [CTR and Social Reference](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/ctr-and-social-reference.md) — Page-type templates, CTR data, OG best practices

## Next Best Skill

- **Primary**: [schema-markup-generator](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/schema-markup-generator/SKILL.md) — complete the SERP packaging with structured data.
