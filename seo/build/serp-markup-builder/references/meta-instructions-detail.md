# Meta Tags Optimizer — Detailed Instructions

Compact workflow, formula set, alignment checks, and example output for the Meta Tags Optimizer skill.

## Step 1: Gather Page Information

```markdown
### Page Analysis

**Page URL**: [URL]
**Page Type**: [blog/product/landing/service/homepage]
**Primary Keyword**: [keyword]
**Secondary Keywords**: [keywords]
**Target Audience**: [audience]
**Primary CTA**: [desired action]
**Unique Value Prop**: [what makes this page special]
```

## Step 2: Create Optimized Title Tag

Requirements:
- 50-60 characters when possible
- Primary keyword near the front
- Clear intent match
- Brand only when it adds value

Use one of these formulas:
1. `Keyword | Benefit | Brand`
2. `Number + Keyword + Promise`
3. `How to [Keyword]: [Benefit]`
4. `What is [Keyword]? [Hook]`
5. `[Keyword] in [Year]: [Update]`

Deliver three options with length, power words, and keyword position.

## Step 3: Write Meta Description

Requirements:
- 150-160 characters when possible
- Primary keyword used naturally
- Specific benefit + CTA
- Accurate preview of the page

Preferred formula:

`[What the page offers] + [Benefit] + [CTA]`

Deliver three options with length, CTA, and emotional trigger.

## Step 4: Create Social and Supporting Tags

Generate:
- Open Graph (`og:type`, `og:url`, `og:title`, `og:description`, `og:image`)
- Twitter Card tags
- Canonical URL
- Robots / viewport
- Author and article tags where relevant

> **Reference**: See [references/meta-tag-code-templates.md](meta-tag-code-templates.md) for HTML templates and the complete combined block.

## Step 5: CORE-EEAT Alignment Check

| Check | Status | Notes |
|-------|--------|-------|
| **C01 Intent Alignment** | Pass/Warn/Fail | Does the title promise match the content? |
| **C02 Direct Answer** | Pass/Warn/Fail | Does the description reflect the answer available near the top of the page? |

If C01 fails, rewrite the title. If C02 fails, either restructure the content or rewrite the description.

## Step 6: CTR Optimization Tips

```markdown
## CTR Optimization Analysis

### CTR Boosting Elements
| Element | Present | Expected Impact |
|---------|---------|-----------------|
| Numbers | Yes/No | +20-30% |
| Current Year | Yes/No | +15-20% |
| Power Words | Yes/No | +10-15% |
| Question Format | Yes/No | +10-15% |
| Brackets | Yes/No | +10% |

### A/B Test Suggestions
- **Version A**: [current title + description]
- **Version B**: [alternative]
- **Hypothesis**: [why it may outperform]
```

## Example

**User**: "Create meta tags for a blog post about 'how to start a podcast in [current year]'"

**Output**:

```markdown
## Meta Tags: How to Start a Podcast ([current year])

### Title Tag
<title>How to Start a Podcast in [current year]: Complete Beginner's Guide</title>

### Meta Description
<meta name="description" content="Learn how to start a podcast in [current year] with our step-by-step guide. Covers equipment, hosting, recording, and launching your first episode.">
```

_Use the code templates file for the full OG / Twitter / Article block._

## Tips for Success

Front-load the keyword, match search intent, keep the promise specific, and test small variations over time.
