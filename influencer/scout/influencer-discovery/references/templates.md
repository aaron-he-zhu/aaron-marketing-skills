# Influencer Discovery — Templates

Fill-in scaffolds for each step of [SKILL.md](../SKILL.md): the search-criteria
form, the search-strategy checklist, the screening table, the per-influencer
profile, the compiled discovery report, and the insights block. Copy the matching
block and replace the bracketed cells. For platform-specific reading cues see
[platform-vetting.md](platform-vetting.md); for a deep single-creator read see
[creator-dossier.md](creator-dossier.md).

---

## Step 1 — Discovery Parameters

```markdown
### Discovery Parameters

**Brand/Product**: [name]
**Campaign Goal**: [awareness/consideration/conversion]
**Budget Range**: [budget implications for influencer tier]

**Search Criteria**:

| Parameter | Requirement | Priority |
|-----------|-------------|----------|
| Niche/Category | [niche] | Required |
| Platform(s) | [platforms] | Required |
| Follower Range | [min-max] | Required |
| Engagement Rate | [minimum %] | Required |
| Geography | [minimum country/region granularity needed for this decision] | [Required/Preferred] |
| Language | [languages] | [Required/Preferred] |
| Content Type | [video/photo/etc.] | Preferred |
| Posting Frequency | [minimum] | Preferred |
| Audience Demographics | [age/gender/interests] | Preferred |
| Brand Safety | [requirements] | Required |

**Nice-to-Have**:
- [Additional preference 1]
- [Additional preference 2]

**Exclusions**:
- [Competitor partnerships]
- [Content types to avoid]
- [Other exclusions]
```

---

## Step 2 — Search Strategy

```markdown
## Search Strategy

### Transient Lookup Block — DO NOT SAVE OR HAND OFF

Raw handles/profile URLs may appear only in this block while the current session performs lookup. Delete the block before producing any saved artifact, handoff, checkpoint, or registry proposal.

| Lookup slot | Raw handle/profile URL | Platform hint | Lookup purpose |
|-------------|------------------------|---------------|----------------|
| lookup-01 | [raw locator supplied/returned this session] | [platform] | [search/verification purpose] |

### Primary Search Methods

1. **Hashtag Research**
   - Core hashtags: #[hashtag1], #[hashtag2]
   - Niche hashtags: #[hashtag3], #[hashtag4]
   - Brand-adjacent: #[hashtag5]

2. **Similar Accounts**
   - Starting from: [lookup slot from the transient block]
   - Platform suggestions: "Similar to" features

3. **Competitor Mentions**
   - Check tagged posts on [competitor accounts]
   - Monitor #[competitor hashtags]

4. **Platform-Specific Discovery**
   - TikTok: Creator Marketplace, trending sounds
   - Instagram: Explore page, Reels
   - YouTube: Related channels, collaboration networks

5. **Saved-Safe Tool Queries / Import Batches** (when records are available)

| Batch | creator_ref | identity_status | handle_ref | Provider/tool | Query or purpose | source_ref | observed_at | Window | Evidence label |
|-------|-------------|-----------------|------------|---------------|------------------|------------|-------------|--------|----------------|
| batch-01 | [creator-<UUIDv4>] | [resolved/unresolved/conflict] | [opaque authorized ref or unknown] | [provider/tool or user-export] | [query/import purpose] | [opaque ref] | [date/ISO 8601] | [measurement window/not-supplied] | [Measured/Calculated/Estimated/User-provided/Proxy] |

Keep no credential or raw contact coordinate in this log. A provider name does
not label every returned field automatically; apply the evidence label to each
field in the profile below. Save an opaque `handle_ref`/`source_ref` only when an
authorized artifact or verified registry link can resolve it. Otherwise do not
create a hidden raw-handle mapping: set `identity_status: unresolved`, set
`handle_ref: unknown`, and record `cross_session_locator_required: true` so a
later session asks the user for the transient locator again.
```

### Partial Checkpoint — Two Raw Locators, Missing Inputs

When the only candidates are exactly two transient raw locators and required criteria or dated evidence are missing, do not produce or save a vetted shortlist. Return `NEEDS_INPUT` inline. Only after a separate exact authorization to save a partial checkpoint may you copy this block:

```markdown
## Partial Discovery Checkpoint

- `status`: `NEEDS_INPUT`
- `checkpoint_state`: `PARTIAL`
- `artifact_kind`: `partial_discovery_checkpoint`
- `candidate_count`: 2
- `shortlist_status`: `NOT_VETTED`
- `ranking_status`: `NOT_RANKED`
- `tiering_status`: `NOT_TIERED`
- `criteria_gaps`: [[missing required criterion], ...]
- `evidence_gaps`: [[missing dated evidence/source], ...]

| creator_ref | identity_status | handle_ref | source_ref | cross_session_locator_required |
|-------------|-----------------|------------|------------|--------------------------------|
| [creator-<UUIDv4>] | [unresolved/resolved] | [opaque authorized ref or unknown] | [opaque authorized ref or unknown] | [true/false] |
| [creator-<UUIDv4>] | [unresolved/resolved] | [opaque authorized ref or unknown] | [opaque authorized ref or unknown] | [true/false] |

Raw locators are omitted. If no authorized resolver exists, do not preserve a hidden mapping; the next session must request each locator again. Do not add discovery signals, tiers, ranks, “top” language, or a fit-scorer handoff until criteria and evidence are complete.
```

---

## Step 3 — Initial Screening

```markdown
## Initial Candidate Pool

**Total Candidates Found**: [number]
**After Initial Screening**: [number]

### Screening Criteria Applied

| Criterion | Filter | Eliminated |
|-----------|--------|------------|
| Follower range | [range] | [#] |
| Engagement rate | >[%] | [#] |
| Recent activity | <[days] | [#] |
| Content relevance | [criteria] | [#] |
| Brand safety | [criteria] | [#] |

### Red Flags Identified

- [#] accounts with suspected fake followers
- [#] accounts with controversial content
- [#] accounts with competitor exclusivity
- [#] accounts inactive >30 days
```

---

## Step 4 — Influencer Profile

For each qualified influencer:

Apply this identity-reference rule before filling the block:

- Reuse an explicitly carried opaque `creator_ref`, or a creator-registry
  aggregate ID only after its handle link is verified.
- Otherwise generate one random `creator-<UUIDv4>` and reuse it unchanged across
  the report, any authorized save, and every downstream handoff/tracker.
- A raw handle, display name, profile URL, email, provider ID, or deterministic
  hash of any of them is never a valid `creator_ref`. Keep provider identity
  evidence in separate opaque `handle_ref` and `source_ref` fields.
- Resolve the ref only through the accompanying authorized artifact's verified
  handle evidence or an accepted registry identity link. If neither is
  available, set `identity_status: unresolved`, persist no `handle_ref`,
  `source_ref`, or hidden raw-locator mapping, and set
  `cross_session_locator_required: true`. A later session must ask the user for
  the transient locator again; do not guess or merge.

```markdown
---

## Influencer #[X]: [creator-<UUIDv4>]

**Identity status**: [resolved/unresolved/conflict]
**Verified cross-link ref**: [source_ref or none]
**Cross-session locator required**: [true/false]
**Current STAR evidence_window**: [start/end or not-supplied]

### Basic Information

| Field | Value/ref | Provider/tool | source_ref | observed_at | Window | Evidence label | Freshness |
|-------|-----------|---------------|------------|-------------|--------|----------------|-----------|
| **Creator ref** | [creator-<UUIDv4> or verified registry aggregate ID] | [upstream artifact/registry] | [opaque ref] | [date] | [N/A] | [User-provided/Measured] | [current/stale/unknown] |
| **Primary handle ref** | [opaque public-handle/profile ref] | [provider/tool] | [opaque ref] | [date] | [N/A] | [label] | [current/stale/unknown] |
| **Other handle refs** | [opaque refs] | [provider/tool] | [opaque ref] | [date] | [N/A] | [label] | [current/stale/unknown] |
| **Platform** | [primary platform] | [provider/tool] | [opaque ref] | [date] | [N/A] | [label] | [current/stale/unknown] |
| **Geography** | [only the country/region required by the filter] | [provider/tool] | [opaque ref] | [date] | [window/not-supplied] | [label] | [current/stale/unknown] |
| **Language** | [primary language] | [provider/tool] | [opaque ref] | [date] | [window/not-supplied] | [label] | [current/stale/unknown] |
| **Niche** | [category] | [provider/tool] | [opaque ref] | [date] | [window/not-supplied] | [label] | [current/stale/unknown] |

### Metrics

Use one row per field and observation. When two providers disagree about the
same field, retain both rows with their own dates/windows; do not average them or
let the newest row overwrite the other automatically.

| Field | Platform | Value | Provider/tool | source_ref | observed_at | Window | Evidence label | Freshness |
|-------|----------|-------|---------------|------------|-------------|--------|----------------|-----------|
| Followers | [platform] | [count] | [provider/tool] | [opaque ref] | [date] | [point-in-time] | [label] | [current/stale/unknown] |
| Engagement rate | [platform] | [%] | [provider/tool] | [opaque ref] | [date] | [posts/date range + denominator] | [label] | [current/stale/unknown] |
| Average views | [platform] | [views] | [provider/tool] | [opaque ref] | [date] | [posts/date range] | [label] | [current/stale/unknown] |
| Growth trend | [platform] | [growing/stable/declining + %] | [provider/tool] | [opaque ref] | [date] | [e.g. trailing 90 days] | [label] | [current/stale/unknown] |

### Audience Analysis

| Field | Value | Provider/tool | source_ref | observed_at | Window | Evidence label | Freshness |
|-------|-------|---------------|------------|-------------|--------|----------------|-----------|
| Gender mix | [%F / %M] | [provider/tool] | [opaque ref] | [date] | [audience/export window] | [label] | [current/stale/unknown] |
| Age | [primary age range] | [provider/tool] | [opaque ref] | [date] | [window] | [label] | [current/stale/unknown] |
| Geography | [country/region-level breakdown only] | [provider/tool] | [opaque ref] | [date] | [window] | [label] | [current/stale/unknown] |
| Interests | [categories] | [provider/tool] | [opaque ref] | [date] | [window] | [label] | [current/stale/unknown] |
| Real-follower estimate | [%] | [provider/model] | [opaque ref] | [date] | [window] | Estimated | [current/stale/unknown] |
| Audience-brand overlap | [High/Medium/Low] | [provider/method] | [opaque ref] | [date] | [window] | [Estimated/Calculated/Proxy] | [current/stale/unknown] |

### Content Analysis

| Field | Observation | Provider/tool | source_ref | observed_at | Window | Evidence label | Freshness |
|-------|-------------|---------------|------------|-------------|--------|----------------|-----------|
| Primary format | [format] | [provider/tool] | [opaque ref] | [date] | [post sample] | [label] | [current/stale/unknown] |
| Posting frequency | [X posts/week] | [provider/tool] | [opaque ref] | [date] | [post sample] | [label] | [current/stale/unknown] |
| Aesthetic/tone | [description] | [method] | [post refs] | [date] | [post sample] | [Calculated/Estimated] | [current/stale/unknown] |
| Top content | [content ref + supported engagement] | [provider/tool] | [opaque ref] | [date] | [metric window] | [label] | [current/stale/unknown] |

**Discovery Relevance Observations — NOT_EVALUATED by Fit**:

| Dimension | Read | Evidence-row refs | Evidence label |
|-----------|------|-------------------|----------------|
| Visual-content overlap | [Observed/Not observed/Unknown] | [refs] | [Calculated/Estimated] |
| Value-topic overlap | [Observed/Not observed/Unknown] | [refs] | [Calculated/Estimated] |
| Audience-evidence overlap | [Observed/Not observed/Unknown] | [refs] | [Calculated/Estimated] |

These observations support the Fit evidence package only. Do not translate
them into a Fit score, recommendation, priority, or creator-selection decision.

### Partnership History

**Past Brand Partnerships**:
| Brand ref | Date/window | Content Type | Performance | Provider/tool | source_ref | observed_at | Evidence label | Freshness |
|-----------|-------------|--------------|-------------|---------------|------------|-------------|----------------|-----------|
| [brand ref 1] | [date/window] | [type] | [performance] | [provider/tool] | [opaque ref] | [date] | [label] | [current/stale/unknown] |
| [brand ref 2] | [date/window] | [type] | [performance] | [provider/tool] | [opaque ref] | [date] | [label] | [current/stale/unknown] |

**Competitor Partnerships**: [Yes/No/Unknown + evidence-row refs]

### Contact-path References

- **Creator ref**: [creator-<UUIDv4> or verified registry aggregate ID; never a raw handle]
- **Recipient ref**: [pseudonymous recipient_ref or unknown]
- **Contact source ref**: [opaque contact_source_ref or unknown]
- **Agency ref**: [opaque agency_ref or not-applicable]
- **Eligible channel**: [email/DM/form/unknown; eligibility is checked by outreach-manager]
- **Observed at**: [date/ISO 8601 or unknown]

Resolve any raw email, phone, postal address, public name, or named manager only
transiently when needed. Never copy it into this profile, a saved discovery
artifact, a handoff, or a registry proposal.

### Discovery-to-Fit Freshness

- `STAR evidence_window`: [start/end or not-supplied]
- `freshness_status`: [current/stale/unknown]
- `refresh_required`: [field list or none]

`current` means every required volatile input falls inside the supplied STAR
window. A field outside it is `stale`; a missing observation date/window or an
absent STAR window is `unknown`. Keep stale/unknown evidence visible for
provenance, but hand that field to `fit-scorer` as Unknown until refreshed. The
profile-level status is `stale` if any required field is stale, otherwise
`unknown` if any required field is unknown, and `current` only when all required
fields are current. Do not create a global TTL.

### Unresolved Evidence / Identity Conflicts

| Field or identity | Observation A ref | Observation B ref | Status / next check |
|-------------------|-------------------|-------------------|---------------------|
| [field/identity] | [source/date/window] | [source/date/window] | [unresolved/verified cross-link needed] |

Do not average conflicting values, select by recency alone, or merge identities
from similar names/handles. Only a verified cross-link or explicit user
confirmation permits one `creator_ref`.

### Discovery Evidence Completeness

| Required input group | Coverage | Freshness | Evidence-row refs | Gap / next query |
|----------------------|----------|-----------|-------------------|------------------|
| Declared follower/platform/geography filters | [complete/gap] | [current/stale/unknown] | [refs] | [gap/query or none] |
| Engagement and recency observations | [complete/gap] | [current/stale/unknown] | [refs] | [gap/query or none] |
| Audience evidence | [complete/gap] | [current/stale/unknown] | [refs] | [gap/query or none] |
| Content/relevance evidence | [complete/gap] | [current/stale/unknown] | [refs] | [gap/query or none] |
| Authenticity and brand-safety observations | [complete/gap] | [current/stale/unknown] | [refs] | [gap/query or none] |
| Identity resolution | [resolved/unresolved/conflict] | [current/stale/unknown] | [refs] | [gap/query or none] |

- `triage_state`: [READY_FOR_FIT / NEEDS_REFRESH / INELIGIBLE]
- `ranking_status`: `NOT_RANKED`
- `fit_status`: `NOT_EVALUATED`
- `refresh_required`: [field list or none]
- `declared_filter_result`: [pass / fail + exact criterion / unknown]

`READY_FOR_FIT` requires complete current required evidence and no unresolved
identity/evidence conflict. Any stale or unknown required field forces
`NEEDS_REFRESH`, `NOT_RANKED`, and `NEEDS_INPUT`. `INELIGIBLE` requires dated
evidence that fails an explicit discovery filter; it is not a STAR veto or Fit
verdict.

---
```

> Discovery emits evidence completeness and declared-filter status only. It
> never emits a Fit score, recommendation tier, outreach priority, or action
> rank. [fit-scorer](../../fit-scorer/SKILL.md) owns typed comparison.

---

## Step 5 — Compiled Discovery Report

Use this block only after the required criteria and real candidate records exist. A `PARTIAL` checkpoint is not eligible for a `READY_FOR_FIT` queue or fit-scorer handoff. Discovery never action-ranks candidates; stale/unknown required evidence remains `NEEDS_REFRESH/NOT_RANKED/NEEDS_INPUT`.

```markdown
# Influencer Discovery Results

**Search Date**: [date]
**Brand/Campaign**: [name]
**Criteria Used**: [summary]

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Candidates Reviewed | [#] |
| Passed Declared Discovery Filters | [#] |
| READY_FOR_FIT | [#] |
| NEEDS_REFRESH / NOT_RANKED | [#] |
| INELIGIBLE by Declared Filter | [#] |

### By Platform

| Platform | Count | Current complete | Needs refresh |
|----------|-------|------------------|---------------|
| Instagram | [#] | [#] | [#] |
| TikTok | [#] | [#] | [#] |
| YouTube | [#] | [#] | [#] |

Calculate summaries only from comparable field/window observations selected
with an explicit rationale. Do not average unresolved provider conflicts.

### Descriptive Follower-Band Distribution

Use only the user-declared or source-dated taxonomy. A follower band is not a
quality or action tier.

| Declared band | Follower range | Count | Taxonomy source/date |
|---------------|----------------|-------|----------------------|
| [band] | [range] | [#] | [user/source ref + date] |

## Candidate Evidence Queue — No Action Ranking

### READY_FOR_FIT

| Creator ref | Platform | Declared-filter result | Evidence completeness | Freshness | Fit status | Ranking status |
|-------------|----------|------------------------|-----------------------|-----------|------------|----------------|
| [creator-<UUIDv4>] | [platform] | [pass + refs] | complete | current | NOT_EVALUATED | NOT_RANKED |

### NEEDS_REFRESH / NEEDS_INPUT

| Creator ref | Platform | Stale/unknown required fields | Refresh query | Fit status | Ranking status |
|-------------|----------|-------------------------------|---------------|------------|----------------|
| [creator-<UUIDv4>] | [platform] | [fields] | [exact query/fields] | NOT_EVALUATED | NOT_RANKED |

### INELIGIBLE BY DECLARED FILTER

| Creator ref | Failed criterion | Evidence refs | Fit status | Ranking status |
|-------------|------------------|---------------|------------|----------------|
| [creator-<UUIDv4>] | [exact declared filter] | [dated refs] | NOT_EVALUATED | NOT_RANKED |

Do not recommend a creator mix or budget split from discovery. After typed Fit,
`campaign-planner` owns selected mix, objectives, deliverables, and budget.

## Next Steps

1. Send current-evidence candidates to [fit-scorer](../../fit-scorer/SKILL.md) for the typed Suitability read; stale/unknown rows remain `NEEDS_INPUT` and are not action-ranked.
2. Send selected Fit results to [campaign-planner](../../../target/campaign-planner/SKILL.md) to approve objectives, deliverables, rights, measurement, and decision rules.
3. Use [outreach-manager](../../../activate/outreach-manager/SKILL.md) only after the plan is approved and creator selection plus contact/consent/channel readiness are documented. This handoff never authorizes a send.

## Export Options

- [ ] Export pseudonymous refs and evidence pointers to CSV for CRM import
- [ ] Export Fit handoff package
- [ ] Export campaign-planning inputs after Fit

Exports and saved artifacts omit raw names, emails, phones, postal addresses,
named managers, and credentials. Resolve a contact coordinate only transiently
at outreach's exact send gate.
```

---

## Step 6 — Discovery Insights

```markdown
## Discovery Insights

### Niche Observations

**Content Trends**:
- Most successful content type: [type]
- Trending topics: [topics]
- Underutilized angles: [opportunities]

**Competitive Picture**:
- Brands most active: [brands]
- Influencers oversaturated: [who to avoid]
- Untapped opportunities: [gaps]

### Recommendations for Future Searches

- Consider expanding to: [adjacent niches]
- Platform opportunity: [underutilized platform]
- Timing: [when to search again]
```

---

## Worked Example — Sustainable Fashion Micro-Influencers

**User**: "Find 15 micro-influencers (10K-100K followers) in the sustainable
fashion space for a new eco-friendly clothing brand."

**Output** (illustrative; assumes a dated export supplied the evidence rows):

```markdown
# Influencer Discovery: Sustainable Fashion Micro-Influencers

## Candidate Evidence Queue — NOT RANKED

### creator-7f3c2f84-7f1e-47e8-a726-f0d620bb0d91
- **Identity evidence**: public-handle-ref-01 (opaque, verified cross-link)
- **Platform**: Instagram (47K) + TikTok (23K)
- **Engagement**: 5.2% IG, 8.1% TikTok
- **Geography**: US (the required decision granularity)
- **Content**: Outfit styling, brand reviews, thrift hauls
- **Audience**: 78% F, 25-34 primary, US-based
- **Evidence**: the full profile retains one export/provider ref, observation date, window, evidence label, and freshness state per factual field (abridged here)
- **Triage state**: READY_FOR_FIT only if every required field above is current
- **Fit status**: NOT_EVALUATED
- **Ranking status**: NOT_RANKED

**Declared-filter result**: [pass/fail/unknown from the cited rows only]. Do not
translate these observations into a Fit claim or outreach priority.

**Past Partnerships**: brand-ref-01, brand-ref-02, brand-ref-03 (each backed by a dated post/export row in the full profile)

### creator-e2e582d4-655f-4bbd-97f2-c34945b2547a
- **Identity evidence**: public-handle-ref-02 (opaque, verified cross-link)
[... continue with the supplied candidate records, without numbering or rank ...]

## Summary

Report only counts derived from the supplied export: reviewed, passed declared
filters, `READY_FOR_FIT`, `NEEDS_REFRESH`, and `INELIGIBLE`. Do not invent a
threshold, recommended mix, priority tier, or “rising star” label.

**Next Steps**: Run current-evidence candidates through fit-scorer, then approve the campaign plan. Prepare outreach only after selection and contact/consent/channel readiness; do not send from discovery.
```

---

## Tips for Success

1. **Evidence over volume** — prefer evidence-complete candidates to a larger pool with stale or unknown required fields.
2. **Verify authenticity** — check for fake followers and engagement pods.
3. **Review recent content** — confirm consistent quality and brand safety.
4. **Consider past partnerships** — learn from their collaboration history.
5. **Look beyond followers** — engagement quality matters more.
6. **Check all platforms** — multi-platform creators offer more value.
7. **Save for later** — build a pipeline, not just one campaign's list.

---

## What This Skill Does

1. **Multi-Platform Search**: finds influencers across Instagram, TikTok, YouTube, Twitter, and more.
2. **Criteria Matching**: filters by niche, follower count, engagement, location.
3. **Audience Analysis**: evaluates whether their audience matches your target.
4. **Content Assessment**: reviews content quality and style fit.
5. **Authenticity Screening**: identifies potential red flags.
6. **Evidence Queue Building**: compiles organized, non-ranked candidate queues for typed Fit.

## When to Use This Skill

- Building an influencer roster from scratch.
- Expanding into new platforms or niches.
- Finding replacements for churned influencer partners.
- Discovering micro and nano influencers at scale.
- Identifying competitors' influencer partners.
- Building an always-on influencer pipeline.
