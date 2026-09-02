# Landing Optimizer — Templates & Worked Examples

Fill-in templates, ASCII layouts, HTML snippets, and a full worked example for the [landing-optimizer](../SKILL.md) skill. The numbered headings map to the Instructions steps in `SKILL.md`.

**Creator-reuse precondition**: do not copy, propose, publish, or test a creator name, quote, message excerpt, video, image, thumbnail, embed, screenshot, badge, testimonial, creator-specific path, or creator-linked tracking token unless the exact frozen version has a matching `creator-content-auditor` approval ref and an `active`, dated/evidenced, unexpired rights row covering the exact channel, territory, format, duration, and `paid | organic | both` use for the full test/flight. Missing, stale, expired-during-test, revoked, disputed, unknown, or out-of-scope evidence returns `NEEDS_INPUT`; leave an opaque placeholder and do not copy, publish, or test the reuse. Saved artifacts/handoffs retain only `creator_ref`, `page_ref`, `snapshot_ref`, frozen asset/approval refs, and opaque rights/evidence refs—never a raw creator handle/name, profile/content/page URL, provider ID, embedded media, or copied creator quote.

---

## Step 1 — Current-State Audit

```markdown
### Landing Page Audit

**Campaign**: [name]
**Transient page locator (never save)**: [URL used only for current inspection]
**Saved page/snapshot refs**: [opaque page_ref] · [opaque snapshot_ref]
**Traffic Source**: [creator_ref values]
**Current Conversion Rate**: [%]
**Goal**: [what counts as conversion]

### Traffic Context

| Factor | Details |
|--------|---------|
| Creator Ref(s) | [creator_ref values] |
| Platform(s) | [platforms] |
| Content Type | [type] |
| Key Message | [approved_asset_ref + approval_ref + approved message ref, or NEEDS_INPUT] |
| Promo Code | [code if applicable] |
| Audience | [demographics] |
```

---

## Step 2 — Message Match Analysis

```markdown
## Message Match Analysis

### Frozen Approved Creator Asset → Landing Page

| Element | Approved Creator Asset Shows | Landing Page Shows | Match? |
|---------|-----------------|--------------------|----|
| Primary message | [approved message ref; quote only when reuse gate passes] | "[page headline from snapshot_ref]" | ✅/⚠️/❌/Unknown |
| Value prop | "[benefit]" | "[benefit shown]" | ✅/⚠️/❌ |
| Offer | "[discount/deal]" | "[offer displayed]" | ✅/⚠️/❌ |
| Product | [shown/mentioned] | [featured] | ✅/⚠️/❌ |
| Tone | [style] | [page tone] | ✅/⚠️/❌ |

### Message Match Score: [X/10]

**Issues Found**:
- [Issue 1]: [how to fix]
- [Issue 2]: [how to fix]

**Why This Matters**:
Record mismatch as a test hypothesis, not a causal result. If the creator-side approval or scoped rights are missing, keep that side `Unknown/NEEDS_INPUT` and do not reproduce its wording.
```

---

## Step 3 — Page Structure Recommendations

### Recommended Layout for Influencer Traffic

```
┌─────────────────────────────────────────────┐
│                   HEADER                     │
│  Logo | Nav (minimal) | Cart/CTA            │
├─────────────────────────────────────────────┤
│                   HERO                       │
│  Headline matching influencer message       │
│  Subheadline with value prop                │
│  Primary CTA button                         │
│  [creator_ref slot; populate only after gate] │
├─────────────────────────────────────────────┤
│              SOCIAL PROOF                   │
│  [approved name/asset/quote refs after gate] │
│  OR: UGC gallery                           │
├─────────────────────────────────────────────┤
│              PRODUCT INFO                   │
│  Key features (3-5 max)                    │
│  Product images/video                      │
│  Price + promo code application            │
├─────────────────────────────────────────────┤
│           MORE SOCIAL PROOF                 │
│  Reviews, testimonials, other creators     │
├─────────────────────────────────────────────┤
│               FAQ/OBJECTIONS                │
│  Answer common concerns                    │
├─────────────────────────────────────────────┤
│              FINAL CTA                      │
│  Repeat offer + strong CTA                 │
├─────────────────────────────────────────────┤
│                  FOOTER                     │
│  Trust badges, policies, support           │
└─────────────────────────────────────────────┘
```

### Section-by-Section Optimization

#### Hero Section

**Current**: [describe current state]

**Recommended**:
- Headline: [specific recommendation]
- Subheadline: [specific recommendation]
- CTA: [specific button text]
- Image/Video: [recommendation]

**Example**:
```
Headline: "[Approved message wording, or generic campaign wording if NEEDS_INPUT]"
Subheadline: "Use code [CODE] for [X]% off"
CTA: "Shop Now" or "Get [X]% Off"
```

#### Social Proof Section

**Recommendation**:
- Use the driving creator's permitted display name only after the exact reuse gate passes
- Embed or screenshot only the exact frozen approved asset when rights cover that format, destination, territory, duration, and use class
- Include only the approved verbatim quote when quote/name attribution is explicitly covered

**Example**:
```
[creator display name resolved at publication only if rights cover it]
[approved_asset_ref embed/screenshot/quote-card format covered by rights]
[approved_quote_ref resolved at publication] — [creator_ref attribution]
```

#### Product Section

**Recommendation**:
- Show exact product(s) influencer featured
- Highlight features they mentioned
- Make promo code pre-applied or prominent

---

## Step 4 — Social Proof Integration

```markdown
## Social Proof Strategy

### Influencer Integration

| Element | Placement | Implementation |
|---------|-----------|----------------|
| Creator video | Hero or below | [approved_asset_ref] embed/thumbnail only when exact format is covered |
| Pull quote | Hero area | [approved_quote_ref] quote card only when exact quote/name format is covered |
| Creator badge | Near CTA | [creator_ref; display name resolved only at publication when covered] |
| UGC gallery | Mid-page | Frozen approved asset refs whose individual scopes cover the gallery |

### Social Proof Hierarchy

**Tier 1: Primary Creator Ref**
- Most prominent placement
- Their gated approved_asset_ref / approved_quote_ref
- Their audience = this traffic

**Tier 2: Other Creator Refs**
- Separately gated supporting testimonials
- Adds credibility depth

**Tier 3: Customer Reviews**
- Star ratings
- Written reviews
- Review count

**Tier 4: Trust Indicators**
- Customer count ("Join 10,000+ customers")
- Press mentions
- Awards/certifications
```

### Implementation Examples

**Creator Badge**:
```html
<div class="creator-badge">
  <img src="[approved_asset_ref resolved at publication]" alt="[approved alt text]">
  <span>[approved creator display copy resolved at publication]</span>
</div>
```

**UGC Quote**:
```html
<blockquote class="ugc-quote">
  <p>"[approved_quote_ref resolved at publication]"</p>
  <cite>[creator display name resolved at publication only when covered], [Platform]</cite>
</blockquote>
```

---

## Step 5 — Conversion Optimization

```markdown
## Conversion Optimization

### CTA Optimization

| Element | Current | Recommended | Why |
|---------|---------|-------------|-----|
| Button text | [current] | [new] | [reason] |
| Button color | [current] | [new] | [reason] |
| Button size | [current] | [new] | [reason] |
| Placement | [current] | [new] | [reason] |
| Quantity | [#] | [#] | [reason] |

**CTA Best Practices for Influencer Traffic**:
- Reference the promo code in button ("Get 20% Off with CODE")
- Create urgency if applicable ("Limited Time")
- Use action-oriented language ("Shop," "Get," "Claim")
- Make code visible and easy to copy

### Promo Code Experience

**Current**: [describe current promo code experience]

**Recommended**:
- [ ] Auto-apply code via URL parameter
- [ ] Display code prominently at top
- [ ] Show savings amount
- [ ] Make code easy to copy
- [ ] Confirm code applied in cart

**Implementation**:
```
Page: resolve [page_ref] to the implementation URL transiently; save only [page_ref] and [promo_code_ref]

On page load:
1. Detect the approved promo-code parameter
2. Apply to cart automatically
3. Display only the supplied, approved offer terms
```

### Friction Reduction

| Friction Point | Impact | Solution |
|----------------|--------|----------|
| [Point 1] | High/Med/Low | [Solution] |
| [Point 2] | High/Med/Low | [Solution] |
| [Point 3] | High/Med/Low | [Solution] |

**Quick Wins**:
- Remove unnecessary form fields
- Add guest checkout option
- Show shipping costs early
- Display trust badges near CTAs
- Add live chat/support option

### Mobile Optimization

**Critical for influencer traffic** (majority mobile):

| Element | Mobile Check | Status |
|---------|--------------|--------|
| Page load speed | <3 seconds | ✅/❌ |
| CTA button size | Thumb-friendly | ✅/❌ |
| Form fields | Easy to tap | ✅/❌ |
| Images | Optimized | ✅/❌ |
| Scroll depth | Key info visible | ✅/❌ |
```

---

## Step 6 — A/B Testing Plan

```markdown
## A/B Testing Recommendations

Any variant containing a creator name, quote, asset, embed, screenshot, badge, or creator-specific path stays `NEEDS_INPUT — DO NOT START` unless the exact frozen approval and active scoped rights cover the full planned test and publication duration.

### Test Priority Matrix

| Test | Impact | Effort | Priority |
|------|--------|--------|----------|
| Headline copy | High | Low | 1 |
| CTA button text | High | Low | 2 |
| Hero image/video | High | Medium | 3 |
| Social proof placement | Medium | Low | 4 |
| Page length | Medium | Medium | 5 |

### Test 1: Headline

**Hypothesis**: [If we change X, then Y because Z]

| Variant | Headline | Expected Impact |
|---------|----------|-----------------|
| Control | "[Current headline]" | Baseline |
| Test A | "[Alternative 1]" | [expected change] |
| Test B | "[Alternative 2]" | [expected change] |

**Sample Size**: [calculated minimum]
**Duration**: [minimum days to reach significance]
**Success Metric**: Conversion rate

### Test 2: CTA

**Hypothesis**: [statement]

| Variant | Button | Expected Impact |
|---------|--------|-----------------|
| Control | "[Current]" | Baseline |
| Test A | "[Alternative]" | [expected change] |

### Testing Best Practices

- Test one element at a time
- Run until statistical significance
- Document all tests and results
- Implement winners quickly
- Test continuously
```

---

## Step 7 — Influencer-Specific Pages

```markdown
## Influencer-Specific Landing Pages

### When to Create Dedicated Pages

✅ Create dedicated page when:
- Influencer has unique offer/code
- High-volume partnership
- Different product focus
- Long-term ambassador
- Need attribution clarity

❌ Use general page when:
- Small one-off partnership
- Same offer as general campaigns
- Resource constraints

### Dedicated Page Template

**Saved page identity**: [opaque page_ref]. Resolve any public creator-name slug only at publication and only when the reuse gate explicitly covers name/path use; otherwise use a generic campaign path.

**Page Elements**:
```
┌──────────────────────────────────────┐
│  [approved creator display copy]    │
│  [approved_asset_ref]               │
│  Their exclusive offer: [OFFER]     │
├──────────────────────────────────────┤
│  Product(s) they featured           │
│  [Images matching their content]    │
│  [Their specific talking points]    │
├──────────────────────────────────────┤
│  [approved_quote_ref/testimonial]   │
│  [Additional social proof]          │
├──────────────────────────────────────┤
│  Shop + Promo Code Application      │
└──────────────────────────────────────┘
```

### Personalization Options

| Element | Personalization Level |
|---------|----------------------|
| Public path | [creator-name slug only if rights cover name/path; otherwise campaign path] |
| Headline | [approved creator name/message reuse or generic campaign copy] |
| Hero image | [exact frozen approved asset ref with matching image format rights] |
| Offer | Their unique code |
| Products | What they featured |
| Testimonial | [approved verbatim quote ref with matching quote/name rights] |
```

---

## Step 8 — Performance Tracking

```markdown
## Landing Page Analytics

### Key Metrics to Track

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Page load time | <3s | [X]s | ✅/❌ |
| Bounce rate | <40% | [X]% | ✅/❌ |
| Conversion rate | [X]% | [X]% | ✅/❌ |
| Add to cart rate | [X]% | [X]% | ✅/❌ |
| Average order value | $[X] | $[X] | ✅/❌ |

### Tracking Setup

**UTM Parameters**:
```
?utm_source=[platform]
&utm_medium=influencer
&utm_campaign=[campaign-name]
&utm_content=[opaque creator_ref or campaign-content ref]
&utm_term=[content-type]
```

**Events to Track**:
- Page view
- Scroll depth (25%, 50%, 75%, 100%)
- CTA clicks
- Promo code applied
- Add to cart
- Purchase

### Attribution

| Method | Use Case |
|--------|----------|
| UTM parameters | Source tracking |
| Promo codes | Direct attribution |
| Opaque page refs / approved public paths | Creator-specific tracking without persisting raw URLs |
| Pixel tracking | Conversion attribution |
```

---

## Worked Example — Opaque Creator-Ref Campaign

**User**: "Use `creator_ref: creator-042`, `page_ref: page-017`, `snapshot_ref: snap-009`, and frozen `approved_asset_ref: asset-v7` with its matching creator-content-auditor `approval_ref`. The supplied rights row is `active`, observed today with an opaque evidence ref, and covers US landing-page name attribution, exact quote, video embed, and screenshot formats for both paid and organic traffic through the full six-week test/flight. Our dated analytics export reports 1.2% CR versus a source-dated 2–3% target. The approved asset emphasizes 'smooth texture'; the snapshot leads with 'high protein content,' omits the asset, does not auto-apply the promo, and places the mobile CTA below the fold. Build the plan without persisting raw names or URLs."

**Output**:

```markdown
## Landing Page Optimization: creator-042 Campaign

**Creator reuse preflight**: exact frozen approval matched; rights `active`; status date/evidence present; US web name/quote/embed/screenshot formats and paid+organic six-week duration covered.

### Diagnosis

**Current CR**: 1.2% — user-provided from the dated export
**Comparable target**: 2–3% — user-provided and source-dated; not independently validated here

### Supplied Page Observations

1. **Message Mismatch**: `approved_message_ref` and the headline in `snapshot_ref: snap-009` differ; resolve exact wording only inline or at implementation, not in the saved plan
2. **Creator Asset Omitted**: the supplied snapshot does not feature `approved_asset_ref: asset-v7`
3. **Promo Code Friction Hypothesis**: the supplied snapshot says code `ANNA20` is not auto-applied
4. **Mobile CTA Hypothesis**: the supplied snapshot places the CTA below the fold on mobile

### Priority Fixes

| Fix | Hypothesis to test | Effort |
|-----|--------------------|--------|
| Add the frozen approved video to hero | May improve message continuity; lift is Unknown | [NEEDS_INPUT] |
| Auto-apply promo code | May reduce entry friction; lift is Unknown | [NEEDS_INPUT] |
| Match headline to approved messaging | May reduce mismatch; lift is Unknown | [NEEDS_INPUT] |
| Move CTA above fold on mobile | May make the next action easier to find; lift is Unknown | [NEEDS_INPUT] |

**Expected lift**: `NEEDS_INPUT` — no experiment or comparable lift evidence was supplied. Do not add hypothetical per-fix lifts or sum them into a forecast.

### Implementation

**New Headline**: `[headline using only the approved smooth-texture language]`

**Add to Hero**:
\`\`\`html
<div class="creator-feature">
  <video src="[approved_asset_ref resolved transiently at publication]"></video>
  <p>"[approved_quote_ref resolved transiently at publication]" — [permitted creator display name resolved transiently]</p>
</div>
\`\`\`

**Auto-Apply Code**:
Page: `[page_ref; implementation URL resolved transiently]` with `[approved promo_code_ref]`
Display: `[approved offer copy; NEEDS_INPUT if discount terms were not supplied]`

### Test Plan

- Baseline: 1.2% CR from the supplied dated export
- Control: current page snapshot
- Variant: one approved change at a time, or a declared bundled treatment
- Creator-asset gate: approval and rights must remain active and cover the entire six-week test/flight; otherwise `NEEDS_INPUT — DO NOT START`
- Primary outcome: conversion rate
- Sample size, run length, guardrails, and precommitted decision rule: `NEEDS_INPUT`
- Report only observed results after the experiment; do not claim additive or causal lift from the hypotheses above
```

---

## Tips for Better Landing Pages

1. **Match the message** — Continuity from content to page
2. **Gate creator proof** — Approval and exact scoped rights come before reuse
3. **Check mobile from supplied data** — Do not assume the traffic mix
4. **Treat friction as a hypothesis** — Measure the declared change
5. **Test with a decision rule** — Report observed results only
