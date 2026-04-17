# Content Refresh Templates

Detailed output templates for content-refresher steps 2-9. Referenced from [SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/SKILL.md).

---

## Step 2: Identify Content Refresh Candidates

```markdown
## Content Refresh Analysis

### Refresh Candidate Identification

**Criteria for Content Refresh**:
- Published more than 6 months ago
- Contains dated information (years, statistics)
- Declining traffic trend
- Lost keyword rankings
- Outdated references or broken links
- Missing topics competitors now cover
- No GEO optimization

### Content Audit Results

| Content | Published | Last Updated | Traffic Trend | Priority |
|---------|-----------|--------------|---------------|----------|
| [Title 1] | [date] | [date] | ↓ -45% | 🔴 High |
| [Title 2] | [date] | Never | ↓ -30% | 🔴 High |
| [Title 3] | [date] | [date] | ↓ -20% | 🟡 Medium |
| [Title 4] | [date] | [date] | → 0% | 🟡 Medium |

### Refresh Prioritization Matrix

```
High Traffic + High Decline = 🔴 Refresh Immediately
High Traffic + Low Decline = 🟡 Schedule Refresh
Low Traffic + High Decline = 🟡 Evaluate & Decide
Low Traffic + Low Decline = 🟢 Low Priority
```
```

---

## Step 3: Analyze Individual Content for Refresh

```markdown
## Content Refresh Analysis: [Title]

**URL**: [URL]
**Published**: [date]
**Last Updated**: [date]
**Word Count**: [X]

### Performance Metrics

| Metric | 6 Mo Ago | Current | Change |
|--------|----------|---------|--------|
| Organic Traffic | [X]/mo | [X]/mo | [+/-X]% |
| Avg Position | [X] | [X] | [+/-X] |
| Impressions | [X] | [X] | [+/-X]% |
| CTR | [X]% | [X]% | [+/-X]% |

### Keywords Analysis

| Keyword | Old Position | Current Position | Change |
|---------|--------------|------------------|--------|
| [kw 1] | [X] | [X] | ↓ [X] |
| [kw 2] | [X] | [X] | ↓ [X] |
| [kw 3] | [X] | [X] | ↓ [X] |

### Why This Content Needs Refresh

1. **Outdated information**: [specific examples]
2. **Competitive gap**: [what competitors added]
3. **Missing topics**: [new subtopics to cover]
4. **SEO issues**: [current optimization problems]
5. **GEO potential**: [AI citation opportunities]
```

---

## Step 4: Identify Specific Updates Needed

```markdown
## Refresh Requirements

### Outdated Elements

| Element | Current | Update Needed |
|---------|---------|---------------|
| Year references | "[old year]" | Update to [current year] |
| Statistics | "[old stat]" | Find current data |
| Tool mentions | "[old tool]" | Add newer tools |
| Links | [X] broken | Fix or replace |
| Screenshots | Outdated UI | Recapture |

### Missing Information

**Topics competitors now cover that you don't**:

| Topic | Competitor Coverage | Words Needed | Priority |
|-------|---------------------|--------------|----------|
| [Topic 1] | 3/5 competitors | ~300 words | High |
| [Topic 2] | 2/5 competitors | ~200 words | Medium |
| [Topic 3] | 4/5 competitors | ~400 words | High |

### SEO Updates Needed

- [ ] Update title tag with current year
- [ ] Refresh meta description
- [ ] Add new H2 sections for [topics]
- [ ] Update internal links to newer content
- [ ] Add FAQ section for featured snippets
- [ ] Refresh images and add new alt text

### GEO Updates Needed

- [ ] Add clear definition at start
- [ ] Include quotable statistics with sources
- [ ] Add Q&A formatted sections
- [ ] Update sources with current citations
- [ ] Create standalone factual statements
```

---

## Step 5: Create Refresh Plan

```markdown
## Content Refresh Plan

### Title/URL
**Current**: [current title]
**Refreshed**: [updated title with year/hook]

### Structural Changes

**Keep As-Is**:
- [Section 1] - Still relevant and accurate
- [Section 2] - Still relevant and accurate

**Update/Expand**:
- [Section 3] - Update statistics, add [X] words
- [Section 4] - Add new examples from [current year]

**Add New Sections**:
- [New Section 1] - [description, ~X words]
- [New Section 2] - [description, ~X words]
- FAQ Section - [X questions for featured snippets]

**Remove/Consolidate**:
- [Section 5] - Outdated, remove or redirect topic

### Content Additions

**New Word Count Target**: [X] words (+[Y] from current)

| Section | Current | After Refresh | Notes |
|---------|---------|---------------|-------|
| Introduction | [X] | [X] | Add hook, update context |
| [Section 1] | [X] | [X] | Keep |
| [Section 2] | [X] | [X] | Update stats |
| [New Section] | 0 | [X] | Add entirely |
| FAQ | 0 | [X] | Add for GEO |
| Conclusion | [X] | [X] | Update CTA |

### Specific Updates

**Statistics to Update**:

| Old Statistic | New Statistic | Source |
|---------------|---------------|--------|
| "[old stat]" | "[find current]" | [source] |
| "[old stat]" | "[find current]" | [source] |

**Links to Update**:

| Anchor Text | Old URL | New URL | Reason |
|-------------|---------|---------|--------|
| "[anchor]" | [old] | [new] | Broken |
| "[anchor]" | [old] | [new] | Better resource |

**Images to Update**:

| Image | Action | New Alt Text |
|-------|--------|--------------|
| [img 1] | Replace | "[keyword-rich alt]" |
| [img 2] | Keep | Update alt text |
```

---

## Step 6: Write Refresh Content

```markdown
## Refreshed Content Sections

### Updated Introduction

[Write new introduction with:]
- Updated hook for current year
- Fresh statistics
- Clear value proposition
- Primary keyword in first 100 words

### New Section: [Title]

[Write new section covering:]
- [Topic competitors now cover]
- Current information and examples
- GEO-optimized with quotable statements

### Updated Statistics Section

**Replace**:
> "[Old statement with outdated stat]"

**With**:
> "[New statement with current stat] (Source, [current year])"

### New FAQ Section

## Frequently Asked Questions

### [Question matching PAA/common query]?

[Direct answer in 40-60 words, optimized for featured snippets]

### [Question 2]?

[Direct answer]

### [Question 3]?

[Direct answer]
```

---

## Step 7: Optimize for GEO During Refresh

```markdown
## GEO Enhancement Opportunities

### Add Clear Definitions

**Add at start of article**:
> **[Topic]** is [clear, quotable definition in 40-60 words that
> AI systems can cite directly].

### Add Quotable Statements

**Transform**:
> "Email marketing is effective for businesses."

**Into**:
> "Email marketing delivers an average ROI of $42 for every $1
> invested, making it the highest-ROI digital marketing channel
> according to the Data & Marketing Association ([current year])."

### Add Q&A Sections

Structure content with questions AI might answer:
- What is [topic]?
- How does [topic] work?
- Why is [topic] important?
- What are the benefits of [topic]?

### Update Citations

- Add sources for all statistics
- Link to authoritative references
- Include publication dates
- Use recent sources (last 2 years)
```

---

## Step 8: Generate Republishing Strategy

```markdown
## Republishing Strategy

### Date Strategy

**Options**:

1. **Update Published Date**
   - Use when: Major overhaul (50%+ new content)
   - Pros: Signals freshness to Google
   - Cons: Loses "original" authority

2. **Add "Last Updated" Date**
   - Use when: Moderate updates (20-50% new)
   - Pros: Shows both original and fresh
   - Cons: Original date visible

3. **Keep Original Date**
   - Use when: Minor updates (<20% new)
   - Pros: Maintains authority
   - Cons: Doesn't signal update

**Recommendation**: [Option X] because [reason]

### Technical Implementation

- [ ] Update `dateModified` in schema
- [ ] Update sitemap lastmod
- [ ] Clear cache after publishing
- [ ] Resubmit to ~~search console

### Promotion Strategy

**Immediately after refresh**:
- [ ] Share on social media as "updated for [current year]"
- [ ] Send to email list if significant update
- [ ] Update internal links with fresh anchors
- [ ] Reach out for new backlinks

**Track Results**:
- [ ] Monitor rankings for 4-6 weeks
- [ ] Track traffic changes
- [ ] Watch for featured snippet capture
- [ ] Check AI citation improvements
```

---

## Step 9: Create Refresh Report

```markdown
# Content Refresh Report

## Summary

**Content**: [Title]
**Refresh Date**: [Date]
**Refresh Level**: [Major/Moderate/Minor]

## Changes Made

| Element | Before | After |
|---------|--------|-------|
| Word count | [X] | [Y] (+[Z]%) |
| Sections | [X] | [Y] |
| Statistics | [X] outdated | [Y] current |
| Internal links | [X] | [Y] |
| Images | [X] | [Y] |
| FAQ questions | 0 | [X] |

## Updates Completed

- [x] Updated title with current year
- [x] Refreshed meta description
- [x] Added [X] new sections
- [x] Updated [X] statistics with sources
- [x] Fixed [X] broken links
- [x] Added FAQ section for GEO
- [x] Implemented FAQ schema
- [x] Updated images and alt text

## Expected Outcomes

| Metric | Current | 30-Day Target | 90-Day Target |
|--------|---------|---------------|---------------|
| Avg Position | [X] | [Y] | [Z] |
| Organic Traffic | [X]/mo | [Y]/mo | [Z]/mo |
| Featured Snippets | 0 | 1+ | 2+ |

## Next Review

Schedule next refresh review: [Date - 6 months from now]
```
