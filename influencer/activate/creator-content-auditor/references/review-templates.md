# Content Reviewer — Templates, Worked Example & Checklists

Fill-in templates for each review step, a worked example, the quick checklist, and review tips. Referenced from [../SKILL.md](../SKILL.md). The numbered steps below match the Instructions section there.

**Persistence boundary**: every block except **Step 8 — Feedback Message for Creator** may be used to assemble a durable audit only after raw identities and locators are removed. Creator, reviewer, and governing-brief identity fields persist only as `creator_ref`, `reviewer_ref`, and `brief_ref`; use opaque approved-asset/evidence refs where the typed audit needs evidence. Never persist a raw handle, name, email, profile/content URL, brief URL, or recipient locator. Step 8 is a transient creator-facing render only: never copy it into the v3 artifact, WARM memory, HOT, or a handoff. Generating, reviewing, approving, or saving it is not send authorization; delivery must use `outreach-manager`'s independently approved single-touch send gate.

## Step 1 — Establish Review Criteria

```markdown
### Review Framework

**Brief**: [brief_ref]
**Creator**: [creator_ref]
**Platform**: [platform]
**Content Type**: [format]
**Reviewer**: [reviewer_ref]

### Typed STAR Evidence Plan

| Dimension | Catalog items | Evidence refs / gaps |
|-----------|---------------|----------------------|
| Suitability | `STAR-S1..S10` from the supplied fit-scorer read | [opaque refs or `unknown`] |
| Trust | `STAR-T1..T10` from the frozen deliverable and governing records | [opaque refs or `unknown`] |
| Appeal | `STAR-A1..A10` from the frozen deliverable | [opaque refs or `unknown`] |
| Return | `STAR-R1..R10` under the declared `assessment_time` | [opaque refs, catalog-authorized `na`, or `unknown`] |

These tables collect evidence only. Do not invent category weights, thresholds, `/10` rollups, or a parallel verdict. The final result copies `status`, `verdict`, `score_state`, raw/final score, and `cap_applied` only from the typed scorer.
```

## Step 2 — Brand Alignment Review

```markdown
## Brand Alignment Review

### Visual Brand Check

| Element | Guideline | Content | Status |
|---------|-----------|---------|--------|
| Tone | [expected] | [observed] | ✅/⚠️/❌ |
| Aesthetic | [expected] | [observed] | ✅/⚠️/❌ |
| Quality level | [expected] | [observed] | ✅/⚠️/❌ |
| Brand representation | [expected] | [observed] | ✅/⚠️/❌ |

### Brand Safety Check

| Risk Area | Check | Status | Notes |
|-----------|-------|--------|-------|
| Controversial topics | [details] | ✅/❌ | [notes] |
| Competitor mentions | [details] | ✅/❌ | [notes] |
| Inappropriate content | [details] | ✅/❌ | [notes] |
| Sensitive contexts | [details] | ✅/❌ | [notes] |
| Background elements | [details] | ✅/❌ | [notes] |

### Value Alignment

| Brand Value | Reflected in Content? | Notes |
|-------------|-----------------------|-------|
| [Value 1] | ✅/⚠️/❌ | [how/why not] |
| [Value 2] | ✅/⚠️/❌ | [how/why not] |

**Mapped STAR item evidence**: [qualified item IDs + dated evidence refs]
**Notes**: [observations only; no manual subtotal or gate]
```

## Step 3 — Message Accuracy Review

```markdown
## Message Accuracy Review

### Key Message Check

| Required Message | Present? | How Communicated | Accuracy |
|------------------|----------|------------------|----------|
| [Message 1] | ✅/❌ | [how] | ✅/⚠️/❌ |
| [Message 2] | ✅/❌ | [how] | ✅/⚠️/❌ |
| [Message 3] | ✅/❌ | [how] | ✅/⚠️/❌ |

### Talking Points Check

| Talking Point | Included | Notes |
|---------------|----------|-------|
| [Point 1] | ✅/❌ | [notes] |
| [Point 2] | ✅/❌ | [notes] |
| [Point 3] | ✅/❌ | [notes] |

### Prohibited Claims Check

| Prohibited Content | Present? | Issue |
|--------------------|----------|-------|
| False claims | ✅/❌ | [if present] |
| Competitor disparagement | ✅/❌ | [if present] |
| Unsubstantiated claims | ✅/❌ | [if present] |
| [Industry-specific] | ✅/❌ | [if present] |

### Call-to-Action Check

| CTA Requirement | Status | Notes |
|-----------------|--------|-------|
| CTA present | ✅/❌ | |
| Correct CTA | ✅/❌ | Expected: [X], Actual: [Y] |
| Clear and compelling | ✅/⚠️/❌ | |

**Mapped STAR item evidence**: [qualified item IDs + dated evidence refs]
```

## Step 4 — Compliance Review

The complete STAR veto set is `STAR-S2`, `STAR-S6`, `STAR-T1`, `STAR-T2`, and `STAR-T3`. Record only verified `fail` states as vetoes; missing or refused evidence is `unknown`, never a veto. The typed scorer alone applies the outcome rule: exactly one verified veto → `DONE_WITH_CONCERNS/FIX`, `cap_applied: true`, and `final_overall_score = min(raw_overall_score, 59)`; two or more → `DONE/BLOCK`, `cap_applied: false`, and no final score. Never turn a single veto directly into Reject/Hold or hand-calculate a cap.

```markdown
## Compliance Review

### Disclosure Check

| Requirement | Status | Details |
|-------------|--------|---------|
| Disclosure present | ✅/❌ | [type used] |
| Disclosure visible | ✅/❌ | [placement] |
| Disclosure clear | ✅/❌ | [assessment] |
| Disclosure early | ✅/❌ | [timing/placement] |

**Acceptable Disclosures Used**:
- [ ] #ad
- [ ] #sponsored
- [ ] "Paid partnership" feature
- [ ] Verbal disclosure
- [ ] Other: [specify]

**Disclosure Issues** (if any):
- [Issue 1]
- [Issue 2]

### Platform-Specific Requirements

| Platform Rule | Status | Notes |
|---------------|--------|-------|
| [Rule 1] | ✅/❌ | [notes] |
| [Rule 2] | ✅/❌ | [notes] |

### Legal/Regulatory Check

| Requirement | Status | Notes |
|-------------|--------|-------|
| Applicable market disclosure rule | ✅/❌/Unknown | [dated official source + market] |
| Industry regulations | ✅/❌ | [specific] |
| Age restrictions | ✅/❌ | [if applicable] |
| Claims substantiation | ✅/❌ | |
| Copyright/licensing | ✅/❌ | Music, images, etc. |

### Required Elements Check

| Element | Required | Present | Status |
|---------|----------|---------|--------|
| Brand mention | ✅ | ✅/❌ | ✅/❌ |
| Required account tag from `brief_ref` | ✅/❌ | [present/absent; raw tag remains transient] | ✅/❌ |
| #[hashtag] | ✅ | ✅/❌ | ✅/❌ |
| Required destination from `brief_ref` | ✅/❌ | [present/absent; raw URL remains transient] | ✅/❌ |
| Promo code | ✅/❌ | ✅/❌ | ✅/❌ |

**Mapped STAR item evidence**: [`STAR-T1`, `STAR-T2`, `STAR-T3`, other qualified IDs + dated refs]
```

## Step 5 — Quality Assessment

```markdown
## Quality Assessment

### Production Quality Evidence

| Element | Observation | STAR item / evidence ref |
|---------|-------------|--------------------------|
| Video/Image quality | [observed / unknown] | [qualified Appeal item + dated ref] |
| Audio quality (if applicable) | [observed / catalog-authorized na / unknown] | [qualified Appeal item + dated ref] |
| Lighting | [observed / unknown] | [qualified Appeal item + dated ref] |
| Framing/Composition | [observed / unknown] | [qualified Appeal item + dated ref] |
| Editing | [observed / unknown] | [qualified Appeal item + dated ref] |

### Content Effectiveness

| Element | Observation | STAR item / evidence ref |
|---------|-------------|--------------------------|
| Hook strength | [observed / unknown] | [qualified Appeal item + dated ref] |
| Engagement potential | [observed / unknown] | [qualified Appeal item + dated ref] |
| Authenticity | [observed / unknown] | [qualified Appeal item + dated ref] |
| Storytelling | [observed / unknown] | [qualified Appeal item + dated ref] |
| Persuasiveness | [observed / unknown] | [qualified Appeal item + dated ref] |

### Platform Optimization

| Element | Observation | Notes |
|---------|-------------|-------|
| Format for platform | [observed / unknown] | [dated official spec ref] |
| Length within current platform rule | [observed / unknown] | [actual vs. dated official spec] |
| Native feel | [observed / unknown] | [Appeal evidence only] |
| Trend relevance | [observed / unknown] | [dated source where material] |

### Creative Assessment

| Factor | Observation / evidence ref |
|--------|----------------------------|
| Originality | [observation + qualified Appeal item] |
| Brand integration naturalness | [observation + qualified Appeal item] |
| Memorability | [observation + qualified Appeal item] |
| Share-worthiness | [observation + qualified Appeal item] |

AI-slop/humanizer signals are observations for the applicable **Appeal** items only. They never create a veto, a fixed penalty, or a verdict outside the typed scorer.
```

## Step 6 — Technical Specifications Check

```markdown
## Technical Specifications Check

### Platform Requirements

| Spec | Required | Actual | Status |
|------|----------|--------|--------|
| Aspect ratio | [ratio] | [ratio] | ✅/❌ |
| Resolution | [min] | [actual] | ✅/❌ |
| Duration | [range] | [actual] | ✅/❌ |
| File format | [formats] | [format] | ✅/❌ |
| File size | [max] | [actual] | ✅/❌ |

### Caption Check

| Element | Requirement | Actual | Status |
|---------|-------------|--------|--------|
| Length | [max chars] | [chars] | ✅/❌ |
| Hashtags | [requirements] | [actual] | ✅/❌ |
| Tags | [requirements] | [actual] | ✅/❌ |
| Links | [requirements] | [actual] | ✅/❌ |

**Mapped STAR item evidence**: [qualified item IDs + dated official-spec refs; no manual gate]
```

## Step 7 — Final Review

```markdown
# Content Review Summary

## Submission Details

| Field | Value |
|-------|-------|
| Governing brief | [brief_ref] |
| Creator | [creator_ref] |
| Content Type | [type] |
| Submission Date | [date] |
| Reviewer | [reviewer_ref] |
| Review Date | [date] |

## Typed Scorer Result

| Field | Value |
|-------|-------|
| `status` | [`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_INPUT` / `BLOCKED`] |
| `verdict` | [`SHIP` / `FIX` / `BLOCK` / `UNDECIDED`] |
| `score_state` | [`SCORED` / `NOT_SCORED`] |
| `raw_overall_score` | [typed scorer value or omitted] |
| `final_overall_score` | [typed scorer value or omitted] |
| `cap_applied` | [typed scorer boolean] |
| `veto_count` | [typed scorer value] |

Copy these fields from the deterministic scorer without recomputing or translating them into a second gate. Creator-facing translation may follow: `SHIP` → Approved, `FIX` → Revisions Required, `BLOCK` → Reject/Hold this version, `UNDECIDED` → Needs Evidence. Exactly one verified veto is `FIX` with a 59 ceiling; only two or more verified vetoes produce `BLOCK`.

## Evidence-Bound Changes

- Must fix: [qualified item, exact evidence, correction, owner, resubmission condition]
- Should fix: [qualified item, exact evidence, correction, owner, resubmission condition]
- Optional: [non-gating observation]

## Durable Feedback Summary

[Evidence-bound requested changes and resubmission conditions only. Keep the creator-facing message transient; see Step 8.]
```

## Step 8 — Feedback Message for Creator (Transient Only)

Do not save or hand off this rendered copy. Resolve display names, the reply path, and any recipient locator only inside the independently authorized delivery job. Before any email/DM provider call, hand off to `outreach-manager` and require exact approval for the one currently due message bound to `recipient_ref`, channel, final rendered message, and a concrete ISO-8601 `dispatch_at` plus timezone when scheduled; then run its fresh eligibility and live-suppression checks. Any changed recipient, channel, message, or schedule requires new exact approval.

```markdown
## Feedback Message for Creator — TRANSIENT, NOT PERSISTABLE

---

Hi [creator display name resolved transiently at dispatch]!

Thanks for submitting your content for [campaign display name resolved transiently from brief_ref]. We've reviewed it and have some feedback.

### What We Love ❤️

- [Positive point 1]
- [Positive point 2]
- [Positive point 3]

### Changes Needed 📝

Before we can approve, we need a few adjustments:

**1. [Issue]**
- What we see: [current state]
- What we need: [required state]
- Why: [brief explanation]

**2. [Issue]**
- What we see: [current state]
- What we need: [required state]

### Suggestions (Optional)

These aren't required, but might make the content even stronger:
- [Suggestion 1]
- [Suggestion 2]

### Timeline

Please send the revised content by [date] so we can hit our posting window.

Let me know if you have any questions! Happy to hop on a quick call if that's easier.

Thanks again for your creativity!

Best,
[reviewer display signature resolved transiently from reviewer_ref at dispatch]

---
```

**Dispatch state**: `DRAFT — NOT SENT` until the independent outreach exact-send authorization and fresh preflight both pass.

## Worked Example

**User**: "Review this TikTok video submission for our protein powder campaign"

**Output**:

```markdown
# Content Review: creator_ref / approved_asset_ref / TikTok

## Typed Scorer Result

| Field | Value |
|-------|-------|
| `status` | `DONE_WITH_CONCERNS` |
| `verdict` | `FIX` |
| `score_state` | `SCORED` |
| `raw_overall_score` | `82` |
| `final_overall_score` | `59` |
| `cap_applied` | `true` |
| `veto_count` | `1` |

**Creator-facing translation**: Revisions Required. One verified `STAR-T1` veto triggers `FIX` and the typed 59 ceiling; it does not become `BLOCK`/Reject.

## Issues Found

### Verified veto — requires revision and rerun
1. **`STAR-T1` disclosure failure** — the required disclosure was not observed at the evidenced location.
   - Fix: apply the market/platform-compatible disclosure specified by `brief_ref`, cite the revised asset evidence, and rerun the typed gate.

2. **Required offer element absent** — `brief_ref` requires `promo_code_ref`, but the frozen asset evidence does not contain it.
   - Fix: add the approved offer element exactly as governed by the brief and claim records.

### Should Fix (Messaging)
1. **Required key message absent** — the approved claim ref in `brief_ref` is not represented in the frozen asset.
   - Fix: add only the approved wording and retain the claim evidence ref.

## What's Great
- Authentic workout integration
- High production quality
- Engaging hook
- Great product showcase

## Feedback Message
[Transient creator-facing render from Step 8; excluded from the durable artifact]
```

## Quick Review Checklist

```markdown
## Quick Review Checklist

### Must-Pass Items
- [ ] `STAR-S2` follower-authenticity evidence verified or explicitly `unknown`
- [ ] `STAR-S6` coordinated/bought-engagement evidence verified or explicitly `unknown`
- [ ] `STAR-T1` market/platform disclosure evidence verified or explicitly `unknown`
- [ ] `STAR-T2` material-claim integrity evidence verified or explicitly `unknown`
- [ ] `STAR-T3` documented brand-safety policy/window evidence verified or explicitly `unknown`
- [ ] Brand mentioned correctly
- [ ] Required hashtags included
- [ ] No competitor mentions
- [ ] Content is brand-safe

### Quality Check
- [ ] Hook observation mapped to the applicable Appeal item
- [ ] Audio/video quality acceptable
- [ ] Key messages communicated
- [ ] CTA is clear
- [ ] Authentic feel maintained
- [ ] Slop/humanizer findings recorded only as Appeal evidence, never a veto or standalone penalty

### Technical
- [ ] Correct format/dimensions
- [ ] Appropriate length
- [ ] Caption complete
- [ ] Links/codes correct
```

## Tips for Effective Reviews

1. **Be constructive** - Focus on solutions, not just problems
2. **Lead with positives** - Acknowledge what works
3. **Be specific** - "Add #ad to caption" not "fix disclosure"
4. **Explain why** - Help them understand the reasoning
5. **Respect creativity** - Don't over-edit their voice
6. **Be timely** - Quick reviews keep campaigns on track
