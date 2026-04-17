---
name: content-refresher
description: 'Refresh outdated posts with current stats, new sections, freshness signals to restore rankings. 内容更新/排名恢复'
version: "9.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when updating outdated content, refreshing old articles, improving declining pages, or adding new information to existing content."
argument-hint: "<URL of outdated content>"
metadata:
  author: aaron-he-zhu
  version: "9.0.0"
  geo-relevance: "medium"
  tags:
    - seo
    - geo
    - content-refresh
    - content-update
    - content-decay
    - ranking-recovery
    - evergreen-content
    - content-lifecycle
    - 内容更新
    - コンテンツ更新
    - 콘텐츠갱신
    - actualizar-contenido
  triggers:
    # EN-formal
    - "update old content"
    - "refresh content"
    - "content is outdated"
    - "improve declining rankings"
    - "revive old blog posts"
    - "content decay"
    - "content refresh strategy"
    # EN-casual
    - "traffic is dropping"
    - "ranking dropped"
    - "this post is outdated"
    - "traffic is declining on this page"
    - "rankings dropped for this article"
    - "my old content needs updating"
    # EN-question
    - "how to fix declining traffic"
    - "why is my content losing rankings"
    - "how often should I update content"
    # EN-competitor
    - "Clearscope content refresh"
    - "MarketMuse content update"
    # ZH-pro
    - "内容更新"
    - "内容刷新"
    - "排名恢复"
    - "内容衰减"
    - "内容生命周期"
    # ZH-casual
    - "排名下降了"
    - "文章过时了"
    - "流量掉了"
    - "老文章怎么办"
    # JA
    - "コンテンツ更新"
    - "コンテンツリフレッシュ"
    - "記事更新"
    # KO
    - "콘텐츠 갱신"
    - "콘텐츠 업데이트"
    - "순위 하락"
    - "순위 하락 원인"
    - "오래된 글 어떻게 해?"
    # ES
    - "actualizar contenido"
    - "refrescar contenido antiguo"
    # PT
    - "atualizar conteúdo"
    # Misspellings
    - "content refesh"
    - "content refreshh"
---

# Content Refresher


> **[SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)
> **System Mode**: This optimization skill follows the shared [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) and [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md).


This skill helps identify and revitalize outdated content to reclaim lost rankings and traffic. It analyzes content freshness, identifies update opportunities, and guides the refresh process for maximum SEO and GEO impact.

**System role**: Optimization layer skill. It turns weak pages, structures, and technical issues into prioritized repair work.

## When This Must Trigger

Use this when the conversation involves a diagnosis or repair plan that should feed directly into remediation work — even if the user doesn't use SEO terminology:

- Content has lost rankings or traffic over time
- Statistics and information are outdated
- Competitors have published better content
- Content needs updating for a new year
- Industry changes require content updates
- Adding new sections to existing content
- Converting old content for GEO optimization

## What This Skill Does

1. **Freshness Analysis**: Identifies outdated content needing updates
2. **Performance Tracking**: Finds content with declining traffic
3. **Gap Identification**: Spots missing information competitors have
4. **Update Prioritization**: Ranks content by refresh potential
5. **Refresh Recommendations**: Provides specific update guidance
6. **GEO Enhancement**: Updates content for AI citation potential
7. **Republishing Strategy**: Advises on date and promotion tactics

## Quick Start

Start with one of these prompts. Finish with a short handoff summary using the repository format in [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md).

### Identify Content to Refresh

```
Find content on [domain] that needs refreshing
```

```
Which of my blog posts have lost the most traffic?
```

### Refresh Specific Content

```
Refresh this article for [current year]: [URL/content]
```

```
Update this content to outrank [competitor URL]: [your URL]
```

### Content Refresh Strategy

```
Create a content refresh strategy for [domain/topic]
```

## Skill Contract

**Expected output**: a scored diagnosis, prioritized repair plan, and a short handoff summary ready for `memory/audits/`.

- **Reads**: the current page or site state, symptoms, prior audits, and current priorities from [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) and the shared [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) when available.
- **Writes**: a user-facing audit or optimization plan plus a reusable summary that can be stored under `memory/audits/`.
- **Promotes**: blocking defects, repeated weaknesses, and fix priorities to `memory/open-loops.md` and `memory/decisions.md`.
- **Next handoff**: use the `Next Best Skill` below when the repair path is clear.

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

**With ~~analytics + ~~search console + ~~SEO tool connected:**
Claude can automatically pull historical traffic trends from ~~analytics, fetch impression and ranking data from ~~search console, retrieve keyword position history from ~~SEO tool, and identify content with declining performance. This enables data-driven refresh prioritization.

**With manual data only:**
Ask the user to provide:
1. Traffic data or screenshots showing performance trends
2. Ranking screenshots or history for key pages
3. Content publish dates and last update dates
4. List of pages the user suspects need refreshing

Proceed with the analysis using provided data. Note in the output which findings are from automated data vs. manual review.

## Instructions

When a user requests content refresh help:

1. **CORE-EEAT Quick Score — Identify Weak Dimensions**

   Before refreshing, run a quick CORE-EEAT assessment to focus effort on the weakest areas. Reference: [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)

   ```markdown
   ### CORE-EEAT Quick Assessment

   **Content**: [title or URL]
   **Content Type**: [type]

   Rapidly score each dimension (estimate 0-100):

   | Dimension | Quick Score | Key Weakness | Refresh Priority |
   |-----------|-----------|--------------|-----------------|
   | C — Contextual Clarity | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | O — Organization | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | R — Referenceability | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | E — Exclusivity | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | Exp — Experience | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | Ept — Expertise | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | A — Authority | [X]/100 | [main issue] | 🔴/🟡/🟢 |
   | T — Trust | [X]/100 | [main issue] | 🔴/🟡/🟢 |

   **Weakest Dimensions** (focus refresh here):
   1. [Dimension] — [what needs fixing]
   2. [Dimension] — [what needs fixing]

   **Refresh Strategy**: Focus on 🔴 dimensions first, then 🟡.

   _For full 80-item audit, use [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md)_
   ```

2. **Identify Content Refresh Candidates** — Build candidate list with criteria (age, dated info, declining traffic, lost rankings, broken links, missing topics), content audit results table, and prioritization matrix

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the refresh candidate identification template (Step 2).

3. **Analyze Individual Content for Refresh** — Per-URL deep analysis: performance metrics 6-mo-ago vs current, keyword position deltas, why-refresh rationale

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the individual content analysis template (Step 3).

4. **Identify Specific Updates Needed** — Outdated elements table, missing information (topics competitors cover), SEO and GEO update checklists

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the refresh requirements template (Step 4).

5. **Create Refresh Plan** — Structural changes, content additions, statistics/links/images to update

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the full refresh plan template (Step 5).

6. **Write Refresh Content** — Updated introduction, new sections, refreshed statistics, new FAQ section

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the refresh content writing template (Step 6).

7. **Optimize for GEO During Refresh** — Clear definitions, quotable statements, Q&A sections, updated citations

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the GEO enhancement template (Step 7).

8. **Generate Republishing Strategy** — Date strategy (update/add "last updated"/keep original), technical implementation, promotion plan

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the republishing strategy template (Step 8).

9. **Create Refresh Report** — Summary of changes, updates completed, expected outcomes, next review date

   > **Reference**: See [references/refresh-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) for the refresh report template (Step 9).

## Validation Checkpoints

### Input Validation
- [ ] Target content URL or title clearly identified
- [ ] Historical performance data available (traffic trends, rankings)
- [ ] Content publish/update dates known
- [ ] If comparing to competitors, competitor URLs provided

### Output Validation
- [ ] **Banned-vocab self-check** — scan the refreshed content (both new additions and proposed replacements) for banned words/phrases per [skill-contract.md §Output Voice](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md). A refresh that leaves filler intact misses the point.
- [ ] Every recommendation cites specific data points (not generic advice)
- [ ] Outdated elements identified with specific examples and replacement data
- [ ] All suggested additions include word counts and section locations
- [ ] Source of each data point clearly stated (~~analytics data, ~~search console, ~~SEO tool, user-provided, or estimated)

## Example

**User**: "Refresh my blog post about 'best cloud hosting providers'"

**Output** (abbreviated): CORE-EEAT quick score flags Referenceability 35, Experience 30, Trust 60 — recommends pricing refresh for Q1 2023 data, broken-link fixes (3 affiliate links dead), author credential additions, and affiliate disclosure. Delivers a Changes Made block ready for republish.

> **Reference**: See [references/refresh-example.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-example.md) for the full worked example (cloud hosting refresh) and the comprehensive content refresh checklist.

## Tips for Success

1. **Prioritize by ROI** - Refresh high-potential content first
2. **Don't just add dates** - Make substantial improvements
3. **Beat competitors** - Add what they have and more
4. **Track results** - Monitor ranking changes post-refresh
5. **Schedule regular audits** - Check content health quarterly
6. **Optimize for GEO** - Every refresh is a GEO opportunity

> **Reference data**: For content decay signal taxonomy, lifecycle stages, refresh vs. rewrite decision framework, and update strategy by content type, see [references/content-decay-signals.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/content-decay-signals.md).


### Save Results

After delivering audit or optimization findings to the user, ask:

> "Save these results for future sessions?"

If yes, write a dated summary to `memory/audits/content-refresher/YYYY-MM-DD-<topic>.md` containing:
- One-line verdict or headline finding
- Top 3-5 actionable items
- Open loops or blockers
- Source data references

If any veto-level issue was found (CORE-EEAT T04, C01, R10 or CITE T03, T05, T09), also append a one-liner to `memory/hot-cache.md` without asking.


**Gate check recommended**: Run content-quality-auditor on refreshed content before republishing.

## Reference Materials

- [Content Decay Signals](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/content-decay-signals.md) — Decay indicators, lifecycle stages, and refresh triggers by content type
- [Refresh Templates](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-templates.md) — Detailed output templates for steps 2-9 (candidate identification, individual analysis, refresh requirements, refresh plan, content writing, GEO enhancement, republishing, report)
- [Refresh Example & Checklist](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/references/refresh-example.md) — Full worked example and pre/post-refresh checklist

## Next Best Skill

- **Primary**: [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) — re-score the refreshed content before shipping.
