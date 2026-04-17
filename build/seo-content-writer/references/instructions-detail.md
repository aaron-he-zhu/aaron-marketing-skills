# SEO Content Writer — Detailed Instructions

Full step-by-step workflow, templates, and content-type quick starts for the SEO Content Writer skill.

---

## Step-by-Step Workflow

### 1. Gather Requirements

Confirm or ask for:

```markdown
### Content Requirements

**Primary Keyword**: [main keyword]
**Secondary Keywords**: [2-5 related keywords]
**Target Word Count**: [length]
**Content Type**: [blog/guide/landing page/etc.]
**Target Audience**: [who is this for]
**Search Intent**: [informational/commercial/transactional]
**Tone**: [professional/casual/technical/friendly]
**CTA Goal**: [what action should readers take]
**Competitor URLs**: [top ranking content to beat]
```

### 2. Load CORE-EEAT Quality Constraints

Before writing, load content quality standards from the [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md):

```markdown
### CORE-EEAT Pre-Write Checklist

**Content Type**: [identified from requirements above]
**Loaded Constraints** (high-weight items for this content type):

Apply these standards while writing:

| ID | Standard | How to Apply |
|----|----------|-------------|
| C01 | Intent Alignment | Title promise must match content delivery |
| C02 | Direct Answer | Core answer in first 150 words |
| C06 | Audience Targeting | State "this article is for..." |
| C10 | Semantic Closure | Conclusion answers opening question + next steps |
| O01 | Heading Hierarchy | H1→H2→H3, no level skipping |
| O02 | Summary Box | Include TL;DR or Key Takeaways |
| O06 | Section Chunking | Each section single topic; paragraphs 3–5 sentences |
| O09 | Information Density | No filler; consistent terminology |
| R01 | Data Precision | ≥5 precise numbers with units |
| R02 | Citation Density | ≥1 external citation per 500 words |
| R04 | Evidence-Claim Mapping | Every claim backed by evidence |
| R07 | Entity Precision | Full names for people/orgs/products |
| C03 | Query Coverage | Cover ≥3 query variants (synonyms, long-tail) |
| O08 | Anchor Navigation | Table of contents with jump links |
| O10 | Multimedia Structure | Images/videos have captions and carry information |
| E07 | Practical Tools | Include downloadable templates, checklists, or calculators |

_These 16 items apply across all content types. For content-type-specific dimension weights, see the Content-Type Weight Table in [core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)._
_Full 80-item benchmark: [references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)_
_For complete content quality audit: use [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md)_
```

### 3. Research and Plan

Before writing:

```markdown
### Content Research

**SERP Analysis**:
- Top results format: [what's ranking]
- Average word count: [X] words
- Common sections: [list]
- SERP features: [snippets, PAA, etc.]

**Keyword Map**:
- Primary: [keyword] - use in title, H1, intro, conclusion
- Secondary: [keywords] - use in H2s, body paragraphs
- LSI/Related: [terms] - sprinkle naturally throughout
- Questions: [PAA questions] - use as H2/H3s or FAQ

**Content Angle**:
[What unique perspective or value will this content provide?]
```

### 4. Create Optimized Title

```markdown
### Title Optimization

**Requirements**:
- Include primary keyword (preferably at start)
- Under 60 characters for full SERP display
- Compelling and click-worthy
- Match search intent

**Title Options**:

1. [Title option 1] ([X] chars)
   - Keyword position: [front/middle]
   - Power words: [list]

2. [Title option 2] ([X] chars)
   - Keyword position: [front/middle]
   - Power words: [list]

**Recommended**: [Best option with reasoning]
```

### 5. Write Meta Description

```markdown
### Meta Description

**Requirements**:
- 150-160 characters
- Include primary keyword naturally
- Include call-to-action
- Compelling and specific

**Meta Description**:
"[Description text]" ([X] characters)

**Elements included**:
- Primary keyword
- Value proposition
- CTA or curiosity hook
```

### 6. Structure Content and Write

Structure: H1 (primary keyword, one per page) > Introduction (100-150 words, hook + promise + keyword in first 100 words) > H2 sections (secondary keywords/questions) > H3 sub-topics > FAQ section > Conclusion (summary + keyword + CTA).

### 7. Apply On-Page SEO Best Practices

See [seo-writing-checklist.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/seo-content-writer/references/seo-writing-checklist.md) for the full on-page SEO checklist, content writing template, and featured snippet optimization patterns.

Key requirements while writing:
- Primary keyword in title, H1, first 100 words, at least one H2, and conclusion
- Paragraphs of 3-5 sentences; varied sentence length; bullet points and bold key phrases
- Internal links (2-5) and external authoritative links (2-3)
- FAQ section with 40-60 word answers for featured snippet opportunity
- Optimize for definition, list, table, and how-to snippets where applicable

### 8. Add Internal/External Links

```markdown
### Link Recommendations

**Internal Links** (include 2-5):
1. "[anchor text]" → [/your-page-url] (relevant because: [reason])
2. "[anchor text]" → [/your-page-url] (relevant because: [reason])

**External Links** (include 2-3 authoritative sources):
1. "[anchor text]" → [authoritative-source.com] (supports: [claim])
2. "[anchor text]" → [authoritative-source.com] (supports: [claim])
```

### 9. Final SEO Review and CORE-EEAT Self-Check

Score content across 10 SEO factors (title, meta description, H1, keyword placement, H2s, internal links, external links, FAQ, readability, word count) and produce an Overall SEO Score out of 10.

Then verify the 16 CORE-EEAT pre-write constraints (C01, C02, C06, C10, O01, O02, O06, O09, R01, R02, R04, R07, C03, O08, O10, E07) with pass/warning/fail status. List items needing attention.

_For full 80-item audit, use [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md)_

---

## Issue Classification

When the self-check reveals issues, classify and handle them:

**Auto-correct (fix silently, then document in a `### Changes Made` block after the final content):**
- Meta description exceeds 160 characters → rewrite to fit while preserving primary keyword and CTA
- Title tag exceeds 60 characters → shorten while preserving primary keyword
- Missing alt text on images → generate descriptive alt text
- Duplicate H2 headings → differentiate with modifiers
- Keyword density above 2% → replace some instances with semantic variants
- Missing table of contents → generate TOC with anchor links for articles with 3+ H2 sections
- Paragraphs exceeding 5 sentences → split at the most natural break point

Use this format for the Changes Made block:

```markdown
### Changes Made During Self-Check

| Item | Original | Fixed |
|------|----------|-------|
| Meta description | 185 chars | 158 chars — removed non-essential qualifier |
| Keyword density | 2.4% | 1.8% — replaced 3 instances with semantic variants |
```

**Needs your decision (ask before changing):**
- H1 wording changes (may affect brand voice)
- Keyword density below 0.5% (may need structural rewrite)
- Tone adjustments (formal ↔ casual)
- Claim strength (e.g., "best" → "top-rated" for compliance)
- Content length significantly above/below target (±30%)
- Removing/replacing external links
- Statistics or data claims that cannot be verified against the cited source

---

## Content Type Templates

### How-To Guide

```
Write a how-to guide for [task] targeting [keyword]
```

### Comparison Article

```
Write a comparison article: [Option A] vs [Option B] for [keyword]
```

### Listicle

```
Write a list post: "X Best [Items] for [Audience/Purpose]" targeting [keyword]
```

### Ultimate Guide

```
Write an ultimate guide about [topic] (3,000+ words) targeting [keyword]
```

---

## Tips for Success

1. **Match search intent** - Informational queries need guides, not sales pages
2. **Front-load value** - Put key information early for readers and snippets
3. **Use data and examples** - Specific beats generic every time
4. **Write for humans first** - SEO optimization should feel natural
5. **Include visual elements** - Break up text with images, tables, lists
6. **Update regularly** - Fresh content signals to search engines
