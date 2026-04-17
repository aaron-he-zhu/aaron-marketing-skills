# Meta Tags Optimizer — Detailed Instructions

Full workflow templates, title formulas, meta description requirements, CORE-EEAT alignment, CTR optimization, examples, and tips for the Meta Tags Optimizer skill.

---

## Step-by-Step Workflow

### 1. Gather Page Information

```markdown
### Page Analysis

**Page URL**: [URL]
**Page Type**: [blog/product/landing/service/homepage]
**Primary Keyword**: [keyword]
**Secondary Keywords**: [keywords]
**Target Audience**: [audience]
**Primary CTA**: [action you want users to take]
**Unique Value Prop**: [what makes this page special]
```

### 2. Create Optimized Title Tag

```markdown
### Title Tag Optimization

**Requirements**:
- Length: 50-60 characters (displays fully in SERP)
- Include primary keyword (preferably near front)
- Make it compelling and click-worthy
- Match search intent
- Include brand name if appropriate

**Title Tag Formula Options**:

1. **Keyword | Benefit | Brand**
   "[Primary Keyword]: [Benefit] | [Brand Name]"
   
2. **Number + Keyword + Promise**
   "[Number] [Keyword] That [Promise/Result]"
   
3. **How-to Format**
   "How to [Keyword]: [Benefit/Result]"
   
4. **Question Format**
   "What is [Keyword]? [Brief Answer/Hook]"
   
5. **Year + Keyword**
   "[Keyword] in [Year]: [Hook/Update]"

**Generated Title Options**:

| Option | Title | Length | Power Words | Keyword Position |
|--------|-------|--------|-------------|------------------|
| 1 | [Title] | [X] chars | [words] | [Front/Middle] |
| 2 | [Title] | [X] chars | [words] | [Front/Middle] |
| 3 | [Title] | [X] chars | [words] | [Front/Middle] |

**Recommended**: Option [X]
**Reasoning**: [Why this option is best]

**Title Tag Code**:
```html
<title>[Selected Title]</title>
```
```

### 3. Write Meta Description

```markdown
### Meta Description Optimization

**Requirements**:
- Length: 150-160 characters (displays fully in SERP)
- Include primary keyword naturally
- Include clear call-to-action
- Match page content accurately
- Create urgency or curiosity
- Avoid duplicate descriptions

**Meta Description Formula**:

[What the page offers] + [Benefit to user] + [Call-to-action]

**Power Elements to Include**:
- Numbers and statistics
- Current year
- Emotional triggers
- Action verbs
- Unique value proposition

**Generated Description Options**:

| Option | Description | Length | CTA | Emotional Trigger |
|--------|-------------|--------|-----|-------------------|
| 1 | [Description] | [X] chars | [CTA] | [Trigger] |
| 2 | [Description] | [X] chars | [CTA] | [Trigger] |
| 3 | [Description] | [X] chars | [CTA] | [Trigger] |

**Recommended**: Option [X]
**Reasoning**: [Why this option is best]

**Meta Description Code**:
```html
<meta name="description" content="[Selected Description]">
```
```

### 4. Create Open Graph, Twitter Card, and Additional Meta Tags

Generate OG tags (og:type, og:url, og:title, og:description, og:image), Twitter Card tags, canonical URL, robots, viewport, author, and article-specific tags. Then combine into a complete meta tag block.

> **Reference**: See [references/meta-tag-code-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/meta-tag-code-templates.md) for OG type selection guide, Twitter card type selection, all HTML code templates, and the complete meta tag block template.

### 5. CORE-EEAT Alignment Check

Verify meta tags align with content quality standards. Reference: [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)

```markdown
### CORE-EEAT Meta Tag Alignment

| Check | Status | Notes |
|-------|--------|-------|
| **C01 Intent Alignment**: Title promise matches actual content delivery | Pass/Warn/Fail | [Does the title accurately represent what the page delivers?] |
| **C02 Direct Answer**: Meta description reflects the core answer available in first 150 words | Pass/Warn/Fail | [Does the description preview the direct answer?] |

**If C01 fails**: Title is misleading — rewrite to match actual content.
**If C02 fails**: Content may need restructuring to front-load the answer, or description should better reflect available content.
```

### 6. Provide CTR Optimization Tips

```markdown
## CTR Optimization Analysis

### Power Words Used
- [Word 1] - Creates [emotion/action]
- [Word 2] - Creates [emotion/action]

### CTR Boosting Elements

| Element | Present | Impact |
|---------|---------|--------|
| Numbers | Yes/No | +20-30% CTR |
| Current Year | Yes/No | +15-20% CTR |
| Power Words | Yes/No | +10-15% CTR |
| Question | Yes/No | +10-15% CTR |
| Brackets | Yes/No | +10% CTR |

### A/B Test Suggestions

Test these variations:

**Version A** (Current):
- Title: [Title]
- Description: [Description]

**Version B** (Test):
- Title: [Alternative title]
- Description: [Alternative description]
- Hypothesis: [Why this might perform better]
```

---

## Example

**User**: "Create meta tags for a blog post about 'how to start a podcast in [current year]'"

**Output**:

```markdown
## Meta Tags: How to Start a Podcast ([current year])

### Title Tag
```html
<title>How to Start a Podcast in [current year]: Complete Beginner's Guide</title>
```
**Length**: ~55 characters
**Keyword**: "how to start a podcast" at front
**Power Words**: "Complete", "Beginner's"

### Meta Description
```html
<meta name="description" content="Learn how to start a podcast in [current year] with our step-by-step guide. Covers equipment, hosting, recording, and launching your first episode. Start podcasting today!">
```
**Length**: ~163 characters
**Keyword**: Included naturally
**CTA**: "Start podcasting today!"

_Complete meta tag block (with OG, Twitter, Article tags) generated using template from [references/meta-tag-code-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/meta-tags-optimizer/references/meta-tag-code-templates.md)._

### A/B Test Variations

**Title Variation B**:
"Start a Podcast in [current year]: Step-by-Step Guide (+ Free Checklist)"

**Title Variation C**:
"How to Start a Podcast: [current year] Guide [Equipment + Software + Tips]"

**Description Variation B**:
"Want to start a podcast in [current year]? This guide covers everything: equipment ($100 budget option), best hosting platforms, recording tips, and how to get your first 1,000 listeners."
```

---

## Tips for Success

1. **Front-load keywords** - Put important terms at the beginning
2. **Match intent** - Description should preview what page delivers
3. **Be specific** - Vague descriptions get ignored
4. **Test variations** - Small changes can significantly impact CTR
5. **Update regularly** - Add current year, refresh messaging
6. **Check competitors** - See what's working in your SERP
