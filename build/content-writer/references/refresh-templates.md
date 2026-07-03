# Content Refresh Templates

Templates for content-refresher steps 2-9. Referenced from [SKILL.md](../SKILL.md).

## Steps 2-3: Find And Diagnose Refresh Candidates

```markdown
## Content Refresh Analysis

| Content | Published | Last Updated | Traffic Trend | Ranking Trend | Priority | Decision |
|---------|-----------|--------------|---------------|---------------|----------|----------|
| [Title] | [date] | [date/Never] | [down/up X%] | [lost/gained X positions] | H/M/L | [refresh/merge/redirect/retire] |

| Traffic Potential | Decline Severity | Decision |
|-------------------|------------------|----------|
| High | High | Refresh immediately |
| High | Low | Schedule refresh |
| Low | High | Evaluate refresh, merge, redirect, or retire |
| Low | Low | Low priority |

## Individual Page Diagnosis: [Title]
**URL**: [URL] | **Published**: [date] | **Last Updated**: [date] | **Word Count**: [X]

| Metric | 6 Mo Ago | Current | Change | Source |
|--------|----------|---------|--------|--------|
| Organic traffic / impressions / CTR / avg position | [values] | [values] | [+/-] | [analytics/GSC/rank tracker] |

| Keyword | Old Position | Current Position | SERP / Intent Change | Refresh Angle |
|---------|--------------|------------------|----------------------|---------------|
| [kw] | [X] | [X] | [AI Overview/PAA/new intent] | [angle] |
```

## Steps 4-5: Define Updates And Plan The Rewrite

```markdown
## Refresh Requirements

| Area | Evidence | Update Needed | Priority |
|------|----------|---------------|----------|
| Year references | "[old year]" | Update only if substance changes | M |
| Statistics | "[old stat]" | Replace with current sourced stat | H |
| Tools/products | "[old tool]" | Add/remove current options | H |
| Broken links | [X broken] | Fix, replace, or remove | H |
| Missing topics | [competitor/PAA evidence] | Add source-backed section | H |
| Images | [old/missing alt/large file] | Replace, compress, add useful alt | M |

### Required SEO/GEO Updates
- [ ] Refresh title/meta only if intent changed
- [ ] Add or update H2s for missing topics
- [ ] Update internal links to newer relevant pages
- [ ] Add FAQ only when questions match real demand
- [ ] Add 40-60 word definition near the start when useful
- [ ] Include quotable statistics with source and publication date
- [ ] Use recent sources, normally from the last 2 years unless canonical

## Refresh Plan
**Current title**: [title]
**Refreshed title**: [title with updated hook if justified]
**New word count target**: [X] words (+/-[Y])

| Section / Asset | Keep / Update / Add / Remove | Current | After Refresh | Source / Reason |
|-----------------|------------------------------|---------|---------------|-----------------|
| Introduction | Update | [issue] | [target] | [reason] |
| [Section] | Keep | [still valid] | [unchanged] | [reason] |
| [New Section] | Add | 0 | [X words] | [competitor/PAA gap] |
| Statistic / Link / Image | Update | [old] | [new] | [source/date or alt/format reason] |
```

## Steps 6-7: Write And GEO-Optimize

```markdown
## Refreshed Content Sections

### Updated Introduction
[Updated hook, primary keyword in first 100 words, fresh source-backed context.]

### New Section: [Title]
[Cover competitor/PAA gap with direct answer, examples, and source-backed facts.]

### Updated Statistics
**Replace**: "[old claim]"
**With**: "[current claim] ([Source], [publication year/date])"

### FAQ
#### [Question matching PAA/common query]?
[Direct 40-60 word answer optimized for snippets and AI citations.]

## GEO Enhancement Checklist
| Element | Requirement |
|---------|-------------|
| Definition | 40-60 words, clear, quotable |
| Quotable statistic | Source + date + standalone wording |
| Q&A | Direct answer first, context second |
| Citations | Recent, authoritative, dated |
| Factual statements | Understandable out of context |
```

## Step 8: Republishing Strategy

```markdown
## Republishing Strategy

| Refresh Level | New Content Share | Date Treatment | Notes |
|---------------|-------------------|----------------|-------|
| Major overhaul | 50%+ | Update published date | Use only when structure/substance materially changed |
| Moderate update | 20-50% | Add or update "Last Updated" date | Most refreshes fit here |
| Minor update | <20% | Keep original date | Fixes or light factual updates only |

**Recommendation**: [Option] because [evidence].

### Technical Implementation
- [ ] Update `dateModified` in schema
- [ ] Update sitemap `lastmod`
- [ ] Clear cache after publishing
- [ ] Resubmit in Search Console when material changes shipped
- [ ] Monitor rankings, traffic, and CTR for 4-6 weeks

### Promotion
- [ ] Share as "updated for [current year]" only for substantial updates
- [ ] Notify email/social audiences when the update changes user value
- [ ] Add fresh internal links from related pages
```

## Step 9: Refresh Report

```markdown
# Content Refresh Report
**Content**: [Title] | **Refresh Date**: [Date] | **Refresh Level**: Major / Moderate / Minor

| Element | Before | After | Evidence |
|---------|--------|-------|----------|
| Word count / sections | [values] | [values] | [delta] |
| Statistics / sources | [outdated] | [current] | [sources + dates] |
| Internal links / FAQ / images | [values] | [values] | [source or rationale] |

| Metric | Current | 30-Day Target | 90-Day Target |
|--------|---------|---------------|---------------|
| Avg position | [X] | [Y] | [Z] |
| Organic traffic | [X]/mo | [Y]/mo | [Z]/mo |

**Next review**: [Date - 6 months from now]
```
