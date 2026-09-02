# Trend Spotter — Templates & Worked Detail

Fill-in templates for each Instructions step in [../SKILL.md](../SKILL.md), plus an extended example and execution tips. The SKILL.md keeps the numbered method; the long tables and report scaffolds live here.

## Current-evidence gate

Every named current trend, hashtag, sound, format, cultural conversation,
competitor adoption, count, growth rate, or lifecycle call needs a source ref,
`observed_at`/retrieval date, measurement window, platform, geography, metric
definition, current value, and comparable prior value. RSS/feed-title overlap
alone belongs in a separate `Proxy candidate` queue with
`score_state: NOT_SCORED` and `decision: NEEDS_INPUT`; it never fills a
lifecycle, brand-fit, watch/avoid, or act-now field. If those records are
absent, copy the query-plan block in the extended example, leave current
sections `TBD`, and return `NEEDS_INPUT`. Never fill an example row from memory
or relabel an unsupported number `Estimated`.

## Step 1 — Trend Analysis Parameters

```markdown
### Trend Analysis Parameters

**Brand/Industry**: [name]
**Target Platforms**: [platforms]
**Target Audience**: [audience description]
**Geographic Focus**: [regions]
**Time Horizon**: [immediate/this month/this quarter]
**Content Categories**: [relevant categories]
```

## Step 2 — Current Trends

```markdown
## Current Trends

### Trending Topics

| Topic ref | Platform/geo | Current value | Comparable prior value | Metric definition | Lifecycle | Source refs | Observed at / window | Evidence label |
|-----------|--------------|---------------|------------------------|-------------------|-----------|-------------|----------------------|----------------|
| [topic ref] | [exact scope] | [value] | [value] | [unit/denominator] | [rising/peak/declining] | [opaque refs] | [dates/window] | [Measured/User-provided + Calculated lifecycle] |

Only scope-matched dated momentum observations may enter this table. A Proxy or model estimate cannot fill `Current value`, `Comparable prior value`, or `Lifecycle`.

### Proxy Candidate Queue — Not Scored

| Candidate ref | Proxy sources | Observed at | Score state | Decision | Required platform/geo/window query |
|---------------|---------------|-------------|-------------|----------|------------------------------------|
| [candidate ref] | [opaque refs] | [dates] | NOT_SCORED | NEEDS_INPUT | [exact query and fields] |

### Trending Hashtags

| Hashtag ref | Platform/geo | Posts | Growth | Source ref | Observed at / window |
|-------------|--------------|-------|--------|------------|----------------------|
| [hashtag ref] | [scope] | [volume] | [%] | [ref] | [date/window] |

### Trending Audio/Sounds

| Sound ref | Platform/geo | Uses | Origin ref | Source ref | Observed at / window | Safety status |
|-----------|--------------|------|------------|------------|----------------------|---------------|
| [sound ref] | [scope] | [count] | [ref] | [ref] | [date/window] | [supported/unknown] |

### Trending Challenges

| Challenge ref | Platform/geo | Participation | Source ref | Observed at / window | Risk evidence |
|---------------|--------------|---------------|------------|----------------------|---------------|
| [candidate ref] | [scope] | [value] | [ref] | [date/window] | [supported/unknown] |
```

## Step 3 — Trending Content Formats

```markdown
## Trending Content Formats

### Video Formats

| Format | Platform/geo | Performance | Source ref | Observed at / window | Adoption |
|--------|--------------|-------------|------------|----------------------|----------|
| [Format] | [scope] | [metric] | [ref] | [date/window] | Rising/Peak/Declining |

**Hot Formats Right Now**:

1. **[Format Name]**
   - What it is: [description]
   - Observed association: [what the cited comparison shows]
   - Hypothesis: [untested explanation, clearly labeled]
   - Best for: [use cases]
   - How to adapt: [brand approach]
   - Example: [link or description]

2. **[Format Name]**
   - What it is: [description]
   - Observed association / hypothesis: [cite or label]
   - Best for: [use cases]
   - How to adapt: [brand approach]

### Emerging Formats to Watch

| Format | Platform | Status | Source ref + observed window | Decision window |
|--------|----------|--------|------------------------------|-----------------|
| [format] | [platform] | [status] | [ref/date/window] | [supported window] |

### Declining Formats to Avoid

| Format | Platform | Why Declining | Alternative |
|--------|----------|---------------|-------------|
| [format] | [platform] | [reason] | [alternative] |
```

## Step 4 — Cultural Calendar & Moments

```markdown
## Cultural Calendar & Moments

### Upcoming Cultural Moments

| Event/Moment | Date | Relevance | Lead Time | Opportunity |
|--------------|------|-----------|-----------|-------------|
| [Event 1] | [date] | ⭐⭐⭐⭐⭐ | [weeks needed] | [opportunity description] |
| [Event 2] | [date] | ⭐⭐⭐⭐ | [weeks needed] | [opportunity description] |
| [Event 3] | [date] | ⭐⭐⭐ | [weeks needed] | [opportunity description] |

### Cultural Conversations

**Active Conversations to Join**:

| Conversation | Platforms | Sentiment | Brand Angle |
|--------------|-----------|-----------|-------------|
| [topic] | [platforms] | Positive/Mixed/Negative | [how to participate] |

**Conversations to Avoid**:

| Topic | Risk Level | Why Avoid |
|-------|------------|-----------|
| [topic] | High | [reason] |

### Seasonal Opportunities

| Season/Period | Themes | Content Ideas | Influencer Angle |
|---------------|--------|---------------|------------------|
| [period] | [themes] | [ideas] | [approach] |
```

## Step 5 — Trend Relevance Assessment

```markdown
## Trend Relevance Assessment

### Trend: [Name]

**Overview**:
- What: [description]
- Origin: [where it started]
- Current Status: [rising/peaking/declining]
- Platform: [primary platforms]
- Audience: [who's participating]

**Brand Fit Analysis**:

| Factor | Score | Notes |
|--------|-------|-------|
| Audience alignment | [1-5] | [explanation] |
| Brand value fit | [1-5] | [explanation] |
| Content adaptability | [1-5] | [explanation] |
| Risk level | [1-5] | [explanation] |
| Timing window | [1-5] | [explanation] |
| **Total Score** | [X/25] | |

**Recommendation**: ✅ Participate / ⚠️ Proceed with caution / ❌ Skip

**If Participating**:
- Best approach: [how to adapt]
- Timing: [when to post]
- Influencer type: [who should create]
- Risk mitigation: [how to stay safe]

**If Skipping**:
- Reason: [why not]
- Alternative: [what to do instead]
```

## Step 6 — Competitor Trend Activity

```markdown
## Competitor Trend Activity

### Competitor Trend Adoption

| Competitor | Recent trends adopted | Observed performance | Source ref + observed window | Learning/hypothesis |
|------------|-----------------------|----------------------|------------------------------|---------------------|
| [Comp] | [evidenced trend] | [result or Unknown] | [ref/date/window] | [observation or labeled hypothesis] |

### Gap Analysis

**Trends competitors are missing**:
- [Trend 1]: [opportunity for you]
- [Trend 2]: [opportunity for you]

**Trends competitors are overusing**:
- [Trend 1]: [saturation level]

### Best Practices from Competitors

| Competitor | What They Did Well | How to Apply |
|------------|-------------------|--------------|
| [comp] | [execution] | [your approach] |
```

## Step 7 — Trend Report

```markdown
# Trend Report: [Brand/Industry]

**Report Date**: [date]
**Time Horizon**: [period covered]

## Executive Summary

Fill Top 3, watch, avoid, and action blocks only when every included candidate
has complete current evidence for the exact platform/geography/window under the
gate above. Otherwise set the block to `TBD`, return `NEEDS_INPUT`, and attach
the exact collection plan; Proxy candidates never enter these blocks.

**Top 3 Trends to Act On Now** (fill only when every selected row passes the current-evidence gate; otherwise `TBD/NEEDS_INPUT`):
1. [Trend 1]: [why and how]
2. [Trend 2]: [why and how]
3. [Trend 3]: [why and how]

**Trends to Watch**:
- [Trend]: [when it might peak]

**Trends to Avoid**:
- [Trend]: [why]

## Priority Action Items

### Immediate (This Week)

1. **[Trend/Opportunity]**
   - Action: [specific action]
   - Influencer approach: [type of creator]
   - Content format: [format]
   - Hashtags: [relevant hashtags]

### Short-term (This Month)

1. **[Trend/Opportunity]**
   - Action: [specific action]
   - Timeline: [when to execute]

### Plan Ahead (This Quarter)

| Opportunity | Timing | Prep Needed | Budget Consideration |
|-------------|--------|-------------|---------------------|
| [opportunity] | [date] | [weeks] | [notes] |

## Content Format Recommendations

| Platform | Hot Formats | Content Ideas |
|----------|-------------|---------------|
| TikTok | [formats] | [ideas] |
| Instagram | [formats] | [ideas] |
| YouTube | [formats] | [ideas] |

## Hashtag Strategy

**Trending to use**:
- #[hashtag] - [context]
- #[hashtag] - [context]

**Brand + Trend combinations**:
- #[brand] + #[trend] = [combination]

## Risk Assessment

| Trend | Risk Level | Mitigation |
|-------|------------|------------|
| [trend] | [level] | [how to stay safe] |

## Next Steps

1. Brief influencers on [top trend]
2. Create content calendar incorporating [cultural moments]
3. Monitor [emerging trends] for right timing
4. Review trend report again on [date]
```

## Extended Example — TikTok fitness trends

**User**: "What TikTok trends should a fitness brand run right now?"

**Output**:

```markdown
# TikTok Fitness Trend Evidence Request

**Status**: NEEDS_INPUT

The prompt contains brand/platform context but no dated current-trend evidence.
Do not name or score a trend, report a view count, call a lifecycle state, select
a hashtag/format, or recommend this-week execution.

## Exact query / collection plan

| Query or export | Required fields |
|-----------------|-----------------|
| TikTok fitness topic/hashtag trend results for the requested US window | candidate ref, volume definition/value, growth calculation, source_ref, observed_at, measurement window |
| Current fitness sounds and format samples | sound/format ref, usage/performance metric, source_ref, observed_at, comparison window |
| Safety/context read for each candidate | dated source refs, origin/context, rights constraints, observed risk signals |
| Named competitor adoption, if requested | competitor ref, dated post/campaign ref, observed result and window |

After the records arrive, score only the evidenced candidates. Until then all
trend tables are `TBD`, brand fit is `NOT_SCORED`, and no discovery handoff is
made.
```

## Scope & Execution Tips

This skill identifies emerging trends across platforms, assesses each one's fit for your brand, determines the optimal moment to act, surfaces trending content formats, tracks cultural moments and conversations, and monitors competitor trend adoption.

Use it when planning campaign timing and themes, identifying trending content formats to incorporate, finding viral moments to capitalize on, discovering emerging hashtags and challenges, understanding cultural conversations relevant to your brand, or staying ahead of competitor trend adoption.

Tips:
1. **Act fast but thoughtfully** — trends move quickly, but brand safety matters.
2. **Adapt, don't copy** — put your brand's spin on trends.
3. **Consider timing** — early is better, but not too early.
4. **Monitor continuously** — set up regular trend reviews.
5. **Know when to skip** — not every trend is for every brand.
