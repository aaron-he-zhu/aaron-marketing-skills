---
name: audit-page
description: Run a comprehensive on-page SEO + CORE-EEAT content quality audit for a given URL or content
argument-hint: "<URL or paste content>"
allowed-tools: ["WebFetch"]
parameters:
  - name: source
    type: string
    required: true
    description: URL to audit or pasted content
  - name: keyword
    type: string
    required: false
    description: Target keyword for relevance scoring
---

# Audit Page Command

> Content quality scoring based on [CORE-EEAT Content Benchmark](https://github.com/aaron-he-zhu/core-eeat-content-benchmark). Full reference: [references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)

A combined **on-page SEO** + **CORE-EEAT content quality** audit. For full site-wide technical SEO, use `/seo:check-technical`.

## Usage

```
/seo:audit-page https://example.com/blog-post
/seo:audit-page [paste content here] targeting "keyword"
/seo:audit-page https://example.com/landing-page keyword="primary keyword"
```

**Arguments:**
- URL or pasted content (required)
- `keyword="target keyword"` (optional but recommended for relevance scoring)

## Workflow

1. **Run On-Page SEO Audit** -- Invoke `on-page-seo-auditor` with the URL/content and target keyword. Scores 8 areas (Title, Meta Description, Headers, Content, Keywords, Links, Images, Technical).
2. **Run CORE-EEAT Content Quality Audit** -- Invoke `content-quality-auditor`. Veto check first, then score all 80 items across 8 dimensions. Calculate GEO Score (CORE) and SEO Score (EEAT).
3. **Compile Output** -- Merge both results into the format below. Generate priority-ranked action list by severity (Critical / Important / Minor).

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ON-PAGE SEO AUDIT: [Page Title or URL]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OVERALL SCORE: XX/100

[████████████████████░░░░░░░░░░░░░░░░░░░░] XX%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION SCORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[8 area scores with bar charts]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIORITY ACTION LIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL / IMPORTANT / MINOR items with specific fixes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE ACTION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] [Action items]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE-EEAT CONTENT QUALITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Content Type: [type]
Veto Status: Pass / Fail [item]
Weighted Score: XX/100 ([rating])

GEO Score (CORE): XX/100    SEO Score (EEAT): XX/100

Dimension Scores:
Contextual Clarity   [████████░░] XX/100
Organization         [████████░░] XX/100
Referenceability     [████████░░] XX/100
Exclusivity          [████████░░] XX/100
Experience           [████████░░] XX/100
Expertise            [████████░░] XX/100
Authority            [████████░░] XX/100
Trust                [████████░░] XX/100

Top 5 Content Quality Improvements:
1. [Issue in plain language] -- [specific action]
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DETAILED FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Section-by-section breakdown in plain language. Internal item IDs
 (CORE-EEAT benchmark identifiers) are emitted only in the YAML handoff
 artifact at `memory/audits/` with `class: auditor-output` frontmatter —
 never in this user-facing view, per Runbook §5 translation layer.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTE: For technical SEO (speed, crawl, HTTPS), run: /seo:check-technical
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Tips

- Provide target keyword for accurate relevance scoring
- Use alongside `/seo:check-technical` for full technical + content picture
- Some EEAT items (A01, A05, A07) require site-level data; mark "N/A" if not observable
- Run audits monthly for key pages and compare scores over time

## Related Skills

- [on-page-seo-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/on-page-seo-auditor/SKILL.md) -- Detailed on-page SEO analysis
- [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) -- Full CORE-EEAT 80-item content quality audit
