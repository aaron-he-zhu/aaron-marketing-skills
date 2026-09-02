# Content Amplifier — Templates, Specs & Worked Examples

Fill-in templates for both modes of [content-amplifier](../SKILL.md). Anchors are mode-prefixed: `paid-*` for the paid-amplification workflow, `repurpose-*` for the UGC-reuse workflow. Links back to repo root use `../../../`.

**Example precondition**: every row or branch that recommends a new activation, edit, or destination is valid only for the exact frozen version approved by `creator-content-auditor` and a current `active`, dated, evidenced, unexpired grant whose channel, territory, format, and use scope covers that action. Paid selection additionally requires dated evidence for organic performance and separate Hook/Message/Quality/CTA observations. If any of those five components or its evidence is missing, the asset is `NOT_SCORED/NEEDS_INPUT`: preserve supplied observations, but emit no `/25`, rank, tier, or spend and never substitute `Estimated`. Replace any missing approval, rights field, quote, or decision threshold with `NEEDS_INPUT`/`Unknown`; do not treat placeholders or illustrative structures as observed facts. Saved artifacts use stable opaque `creator_ref` plus opaque asset/approval/evidence/rights refs only, never a raw handle, creator name, profile/content URL, email, provider ID, or deterministic identity hash.

---

# Mode: paid

Templates for extending the reach of organic creator content with paid spend.

## paid-1: Content Inventory (Step 1)

```markdown
### Content Inventory for Amplification

**Campaign**: [name]
**Total Content Pieces**: [#]
**Amplification Budget**: $[X]

### Approval, Rights, and Performance Overview

| Creator Ref | Frozen Asset Ref | Auditor Approval | Rights Preflight | Platform | Content Type | Organic Reach | ER | Views | Organic Evidence |
|-------------|------------------|------------------|------------------|----------|--------------|---------------|----|-------|------------------|
| [creator_ref-1] | [approved_asset_ref] | `approved` | `active`; [scope]; [observed time + evidence ref] | [platform] | [type] | [provided/Measured reach or Unknown] | [provided/Measured % or Unknown] | [provided/Measured views or Unknown] | [opaque source_ref + observed_at or gap] |
| [creator_ref-2] | [approved_asset_ref] | `approved` | `active`; [scope]; [observed time + evidence ref] | [platform] | [type] | [provided/Measured reach or Unknown] | [provided/Measured % or Unknown] | [provided/Measured views or Unknown] | [opaque source_ref + observed_at or gap] |
| [creator_ref-3] | [approved_asset_ref] | `approved` | `active`; [scope]; [observed time + evidence ref] | [platform] | [type] | [provided/Measured reach or Unknown] | [provided/Measured % or Unknown] | [provided/Measured views or Unknown] | [opaque source_ref + observed_at or gap] |
```

Populate selection and allocation only from frozen versions approved by `creator-content-auditor` whose current, dated rights evidence is `active`, unexpired, and scoped to the exact channel, territory, format, and paid use. Otherwise return `NEEDS_INPUT` for that asset. Organic reach/ER/views require a dated opaque evidence ref; missing organic evidence is `Unknown` and makes paid selection `NOT_SCORED/NEEDS_INPUT`, never Estimated.

## paid-2: Content Selection (Step 2)

```markdown
## Content Selection for Amplification

### Selection Criteria

| Criterion | Required observation | Evidence requirement |
|-----------|----------------------|----------------------|
| Organic performance | [1-5 or Unknown] | Dated reach/ER/views evidence and declared scoring rule |
| Hook | [1-5 or Unknown] | Dated observation against the declared hook criterion |
| Message | [1-5 or Unknown] | Dated observation against the declared message criterion |
| Quality | [1-5 or Unknown] | Dated observation against the declared production criterion |
| CTA | [1-5 or Unknown] | Dated observation against the declared CTA criterion |

### Content Scoring

| Creator Ref / Asset | Organic | Hook | Message | Quality | CTA | Score State | Total | Rank |
|---------------------|---------|------|---------|---------|-----|-------------|-------|------|
| [creator_ref-1 / asset_ref] | [1-5 + source_ref/date] | [1-5 + source_ref/date] | [1-5 + source_ref/date] | [1-5 + source_ref/date] | [1-5 + source_ref/date] | [SCORED only at complete coverage] | [X/25 only if SCORED] | [rank only if SCORED] |
| [creator_ref-2 / asset_ref] | [value/gap] | [value/gap] | [value/gap] | [value/gap] | [value/gap] | `NOT_SCORED/NEEDS_INPUT` if any gap | — | — |

Do not estimate a missing component, force `/25`, normalize over observed items, or prorate a partial score. An incomplete asset cannot enter a tier or receive spend.

### Top Picks for Amplification

Only list assets that passed the frozen-approval and active scoped-rights preflight and have complete evidence across all five selection components. A high content score never overrides a missing approval or rights gap; an incomplete score never becomes a tier.

**Tier 1: Must Amplify**

| Content | Reason | Recommended Spend |
|---------|--------|-------------------|
| [creator_ref-1 / asset_ref] | [evidence-bound reason] | $[X] ([%] of budget) |
| [creator_ref-2 / asset_ref] | [evidence-bound reason] | $[X] ([%] of budget) |

**Tier 2: Consider If Budget Allows**

| Content | Reason | Recommended Spend |
|---------|--------|-------------------|
| [creator_ref-3 / asset_ref] | [evidence-bound reason] | $[X] ([%] of budget) |

**Do Not Amplify**

| Content | Reason |
|---------|--------|
| [creator_ref-4 / asset_ref] | [evidence-bound reason, rights block, or NOT_SCORED gap] |
```

## paid-3: Amplification Strategy (Step 3 + method detail)

```markdown
## Amplification Strategy

### Strategy Overview

**Objective**: [awareness/traffic/conversions]
**Total Budget**: $[X]
**Duration**: [timeframe]
**Platforms**: [platforms]

### Amplification Methods

#### Option 1: Whitelisting / Spark Ads

**What it is**: Running ads through the creator's account

| Platform | Format | Identity / delivery path | Requirements |
|----------|--------|--------------------------|--------------|
| Meta | Partnership Ads | Creator identity | Matching frozen approval, active scoped paid rights, and current creator/platform authorization |
| TikTok | Spark Ads | Existing creator post identity | Matching frozen approval, active scoped paid rights, live post, and current authorization code |
| YouTube | Supported creator-linked format | Platform-specific identity | Matching frozen approval, active scoped paid rights, and current platform authorization |

**Setup**: [ ] frozen asset version matches auditor approval · [ ] rights status is evidenced `active` and scope covers this exact use · [ ] creator/platform access or authorization is current · [ ] proper disclosure maintained.

#### Option 2: Brand Account Boosting

**What it is**: Delivering a licensed creator asset under the brand account identity.
**Requirements**: matching frozen approval, active scoped paid rights, brand ad-account access, and any separately required creator attribution/disclosure.

#### Option 3: Dark Posts

**What it is**: Ads using creator content that do not appear as organic posts.
**Requirements**: matching frozen approval and active scoped paid rights for every variation, placement, territory, format, and flight.

No method receives a directional engagement, credibility, authenticity, or performance claim by default. Use the user's declared operational constraint or a predeclared comparative test to choose among methods.

### Recommended Strategy Mix

| Method | % of Budget | Amount | Rationale |
|--------|-------------|--------|-----------|
| Whitelisting | [%] | $[X] | [reason] |
| Brand-Account Ads | [%] | $[X] | [reason] |
| Dark Posts | [%] | $[X] | [reason] |
```

## paid-4: Audience Targeting (Step 4)

```markdown
## Audience Targeting Strategy

### Primary Audience: Lookalike/Similar

**Source**: [creator's audience / engaged users / converters]
**Similarity**: [1-10% / narrow-broad]
- Lookalike of creator's engaged followers
- Interest overlap with creator's niche
- Demographics matching creator's audience

### Secondary Audience: Expansion

**For Awareness Campaigns**:
| Audience Segment | Size | Targeting Details |
|------------------|------|-------------------|
| Interest-based | [size] | [interests] |
| Behavioral | [size] | [behaviors] |
| Demographic | [size] | [demographics] |

**For Conversion Campaigns**:
| Audience Segment | Size | Targeting Details |
|------------------|------|-------------------|
| Retargeting | [size] | Website visitors, engagers |
| Custom | [size] | Email lists, customers |
| Lookalike | [size] | Purchase lookalikes |

### Targeting by Platform

#### Meta (Instagram/Facebook)
| Ad Set | Audience | Targeting | Budget |
|--------|----------|-----------|--------|
| [Ad Set 1] | [description] | [details] | $[X] |
| [Ad Set 2] | [description] | [details] | $[X] |

#### TikTok
| Ad Group | Audience | Targeting | Budget |
|----------|----------|-----------|--------|
| [Ad Group 1] | [description] | [details] | $[X] |

### Exclusions
- Existing customers (if not retargeting)
- Previous purchasers (if awareness)
- [Other exclusions]
```

## paid-5: Budget Allocation (Step 5)

```markdown
## Budget Allocation

### Total Amplification Budget: $[X]

### By Content
| Content | Platform | Spend | % | Rationale |
|---------|----------|-------|---|-----------|
| [creator_ref-1 / asset_ref] | TikTok | $[X] | [%] | [complete-score evidence and declared objective] |
| [creator_ref-2 / asset_ref] | Instagram | $[X] | [%] | [complete-score evidence and declared objective] |
| [creator_ref-3 / asset_ref] | Instagram | $[X] | [%] | [complete-score evidence and declared objective] |
| Testing pool | Various | $[X] | [%] | A/B testing new content |

### By Objective
| Objective | Budget | % | Expected Result |
|-----------|--------|---|-----------------|
| Awareness/Reach | $[X] | [%] | [impressions] |
| Traffic | $[X] | [%] | [clicks] |
| Conversions | $[X] | [%] | [conversions] |

### By Platform
| Platform | Budget | % | CPM Estimate | Expected Reach |
|----------|--------|---|--------------|----------------|
| TikTok | $[X] | [%] | $[X] | [reach] |
| Instagram | $[X] | [%] | $[X] | [reach] |
| Facebook | $[X] | [%] | $[X] | [reach] |

### Pacing
| Period | Daily Budget | Purpose |
|--------|--------------|---------|
| Days 1-3 | $[X]/day | Learning phase |
| Days 4-7 | $[X]/day | Optimization |
| Days 8+ | $[X]/day | Scaling winners |
```

> All allocations must sum to the stated budget. A CPM/reach figure may be Estimated only when its calculation inputs and assumptions were supplied or explicitly approved; show that basis. Otherwise use `Unknown`/`NEEDS_INPUT` rather than an example value.

> Allocate only among assets that passed the frozen-approval and active scoped-rights preflight and have `score_state: SCORED` at complete Organic/Hook/Message/Quality/CTA coverage. If no such asset remains, return `NOT_SCORED/NEEDS_INPUT` rather than a hypothetical allocation.

## paid-6: Optimization Playbook (Step 6)

```markdown
## Optimization Playbook

### KPIs to Monitor
| Metric | Target | Action If Below | Action If Above |
|--------|--------|-----------------|-----------------|
| CPM | $[X] | Adjust targeting | Scale budget |
| CTR | [%] | Test new creatives | Scale spend |
| CPC | $[X] | Optimize audience | Increase bid |
| CVR | [%] | Review landing page | Scale budget |
| ROAS | [X]:1 | Pause or adjust | Significantly scale |

### Optimization Schedule
| Day | Action |
|-----|--------|
| [learning window] | Let campaigns run and collect the agreed minimum evidence |
| [first review date] | Apply the supplied scale/pause decision rule |
| [refinement date] | Test a declared audience hypothesis |
| [reallocation date] | Reallocate only when the supplied rule is met and action is authorized |
| [review cadence] | Repeat the approved optimization cycle |

### A/B Testing Plan
| Test | Variable A | Variable B | Success Metric |
|------|------------|------------|----------------|
| [Test 1] | [version A] | [version B] | [metric] |

### When to Scale
Scale up when: [user-supplied target, observation window, minimum sample, guardrails, and decision rule; otherwise NEEDS_INPUT].
Method: [user-approved budget increment and cadence]; expand audiences or duplicate ad sets only as an explicitly authorized test.

### When to Pause
Pause when: [user-supplied stop threshold, observation window, minimum sample, and guardrails; otherwise NEEDS_INPUT].

### Creative Refresh
Refresh when frequency reaches [X]+, engagement declines week-over-week, or CTR drops below [%]. Options: new creator content, different cuts/edits, new hooks, different CTAs.
```

## paid-7: Platform-Specific Setup (Step 7)

```markdown
## Platform Setup Guides

### Rights and Existing-Placement Preflight

| Content ID | Frozen Asset Ref | Auditor Approval | Rights Status | `status_observed_at` | `status_evidence_ref` | Intended Use | Scope Check |
|------------|------------------|------------------|---------------|----------------------|-----------------------|--------------|-------------|
| [asset] | [approved_asset_ref or NEEDS_INPUT] | [approved or NEEDS_INPUT] | [allowed status] | [ISO-8601 time] | [contract/addendum/notice ref or explicit gap ref] | [platform/territory/format/paid use] | [covered/out-of-scope/unknown] |

Only the exact frozen version with auditor status `approved`, plus `active` rights with dated evidence and a matching, unexpired scope, may proceed to setup. Missing approval, `expired`, `revoked`, `disputed`, `unknown`, missing evidence, and out-of-scope grants fail closed for new use with `NEEDS_INPUT`. If a blocked asset already has live placements, copy those placements into the manual removal queue in repurpose step 7; this table does not authorize a pause, deletion, unpublish, or other platform write.

### Meta (Instagram/Facebook) — Partnership Ads
1. Creator authorization: Instagram Settings > Business > Branded Content > add your brand as approved partner (or share a post code for specific content).
2. Create campaign: Ads Manager > Create Campaign > select objective > at ad level pick "Use existing post" > enter branded content ad code > set targeting + budget.
Best practices: use the creator's caption (edited if needed); maintain disclosure; test multiple placements.

### TikTok — Spark Ads
1. Creator authorization: video > ... > Ad settings > turn on "Ad authorization" > copy the authorization code (valid 7-365 days).
2. Create campaign: TikTok Ads Manager > create campaign with chosen objective > at ad level pick "Spark Ads" > enter authorization code > configure targeting.
Implementation note: follow the current documented placement/disclosure requirements and treat placement or comment settings as declared test variables, not default performance levers.

### YouTube — Video Ads
1. Get content rights or have the creator upload to the brand channel.
2. Create a Video campaign in Google Ads > select ad format (skippable, non-skippable, etc.) > configure targeting.
Implementation note: use the supplied or current documented format requirements; any hook, brand-timing, or companion-banner choice remains a declared test unless evidence is supplied.
```

## Worked Example — paid

**User**: "Use five frozen, auditor-approved TikTok assets mapped to stable `creator_ref` values. A dated organic export supplies views/ER plus its opaque evidence ref, and a separate dated evidence matrix supplies Organic/Hook/Message/Quality/CTA observations for every asset: creator-ref-01 = 5/5/4/4/3; creator-ref-02 = 3/3/4/4/4; creator-ref-03 = 4/4/4/3/3; creator-ref-04 = 4/4/3/3/2; creator-ref-05 = 2/2/3/4/2. Every component has `source_ref` and `observed_at`. The supplied asset manifest has a frozen approval reference for each version, and the rights manifest records each grant as active, dated, evidenced, unexpired, and scoped to the requested US TikTok Spark Ads and Instagram Partnership Ads flight. Allocate our $5,000 budget."

```markdown
## Amplification Recommendation

**Evidence basis**: organic metrics, all five selection observations, frozen approval refs, and rights status/scope are user-provided with opaque evidence refs and observation dates. No paid-performance result is Measured by this skill.

| Creator Ref | O/H/M/Q/CTA (provided) | Score State / Total | Approval / rights preflight | Plan Status | Budget |
|-------------|-------------------------|---------------------|-----------------------------|-------------|--------|
| creator-ref-01 | 5/5/4/4/3 | SCORED · 21/25 | frozen approved; `active`; scope covered | Include in declared test | $2,000 |
| creator-ref-02 | 3/3/4/4/4 | SCORED · 18/25 | frozen approved; `active`; scope covered | Include in declared test | $1,000 |
| creator-ref-03 | 4/4/4/3/3 | SCORED · 18/25 | frozen approved; `active`; scope covered | Include in declared test | $1,000 |
| creator-ref-04 | 4/4/3/3/2 | SCORED · 16/25 | frozen approved; `active`; scope covered | Include in declared test | $800 |
| creator-ref-05 | 2/2/3/4/2 | SCORED · 13/25 | frozen approved; `active`; scope covered | No initial spend | $0 |

Recommended strategy ($5,000):
1. creator-ref-01 ($2,000) — highest supplied complete total in this set.
2. creator-ref-02 ($1,000) — tied supplied complete total; retain as a separately measured variation.
3. creator-ref-03 ($1,000) — tied supplied complete total; retain as a separately measured variation.
4. creator-ref-04 ($800) — lower supplied complete total; use the smaller declared test cell.
5. Testing reserve ($200) — A/B test variations.

Setup priority: obtain any separate platform authorization still required > launch only the frozen approved versions within the evidenced scope > apply the user-approved scale/pause rule. If that rule or its thresholds were not supplied, mark them `NEEDS_INPUT`; do not invent a three-day result or an automatic scale decision.
```

If the original terse request were the only input, the correct response would be `NOT_SCORED/NEEDS_INPUT`: request each asset's dated organic metrics/evidence, Hook/Message/Quality/CTA observations/evidence, frozen approval reference, and current rights observation/evidence/scope. Do not emit `/25`, rank, tier, or allocation until every selection component and rights gate is complete.

## Tips — paid

1. Score only evidence-complete assets — missing selection evidence stays `NOT_SCORED`.
2. Treat organic results as a test input, not a guarantee of paid performance.
3. Preserve creator context — test whitelisting against brand reposts instead of assuming either will win.
4. Test before scaling — small tests before big budgets.
5. Optimize continuously — paid requires active management.

---

# Mode: repurpose

Templates for reusing one approved asset across paid, website, email, and social.

## repurpose-1: Content Inventory (Step 1)

```markdown
### Content Inventory

**Campaign**: [name]
**Total Content Pieces**: [#]
**Content Types**: [videos, images, reviews, etc.]

| ID | Creator Ref | Frozen Asset Ref | Opaque Source Ref | Auditor Approval | Platform | Type | Duration/Format | Rights Level / Expiry | Rights Status | `status_observed_at` | `status_evidence_ref` |
|----|-------------|------------------|-------------------|------------------|----------|------|-----------------|-----------------------|---------------|----------------------|-----------------------|
| 001 | [creator_ref] | [approved_asset_ref] | [opaque authorized source_ref] | `approved` | TikTok | Video | [provided duration] | [grant / future date] | `active` | [ISO-8601 time] | [signed grant ref] |
| 002 | [creator_ref] | [approved_asset_ref or NEEDS_INPUT] | [opaque source_ref or NEEDS_INPUT] | [approved or NEEDS_INPUT] | Instagram | Reel | [provided duration] | [grant / expired date] | `expired` | [ISO-8601 time] | [grant ref + expiry] |
| 003 | [creator_ref] | [approved_asset_ref or NEEDS_INPUT] | [opaque source_ref or NEEDS_INPUT] | [approved or NEEDS_INPUT] | Instagram | Carousel | [provided image count] | [unknown] | `unknown` | [ISO-8601 time] | [gap ref: current grant not supplied] |

### Rights Summary

| Rights Type | Content Count | Expiration |
|-------------|---------------|------------|
| Perpetual | [#] | Never |
| 12 months | [#] | [date] |
| Campaign only | [#] | [date] |
| Organic only | [#] | N/A - no paid use |
```

## repurpose-2: Repurposing Opportunity Map (Step 2)

```markdown
## Repurposing Opportunity Map

### Original Content: [creator_ref / approved_asset_ref] TikTok Video
**Persistent source identity**: [creator_ref + exact approved_asset_ref + opaque authorized source_ref; raw handle/content URL forbidden]
**Frozen approved asset ref**: [approved_asset_ref or NEEDS_INPUT]
**Auditor approval**: [approved or NEEDS_INPUT]
**Original**: [provided duration and content description]
**Rights preflight**: [`active` + observed time + evidence ref + unexpired destination scope, or NEEDS_INPUT]

### Repurposing Options

| New Format | Channel | Modifications Needed | Effort |
|------------|---------|---------------------|--------|
| Spark Ad | TikTok Ads | None (native) | Low |
| Instagram Reel | Instagram | Aspect ratio adjust | Low |
| Facebook Ad | Facebook | Caption + CTA overlay | Medium |
| YouTube Short | YouTube | Minor edits | Low |
| Website testimonial | Website | Extract quote + thumbnail | Medium |
| Email GIF | Email | Convert to GIF, 5-10s | Medium |
| Still images | Multiple | Screenshot key moments | Low |
| Quote cards | Social | Pull text, design graphic | Medium |
| Landing page | Website | Embed or screenshot | Low |
| Sales deck | Presentations | Screenshots + stats | Medium |

### Content Multiplication — 1 Original Video → 10+ Assets

Original: 45s TikTok Video
 ├─ Paid Ads: Spark Ad · FB Video · IG Reel
 ├─ Social: Stories Clips · Quote Cards
 └─ Website/Email: Website Banner · Email Hero
```

The tree is a format illustration, not permission. Populate it only with destinations covered by the supplied active grant for the exact frozen approved version; replace every uncovered or unevidenced branch with `NEEDS_INPUT`.

## repurpose-3: Repurposing Plan (Step 3)

```markdown
## Content Repurposing Plan

### Priority Content
| Rank | Content | Original Performance | Repurpose Priority |
|------|---------|---------------------|-------------------|
| 1 | [creator_ref-1 / asset_ref] video | [provided/observed metrics or Unknown] | [only if frozen approved + active scope covered] |
| 2 | [creator_ref-2 / asset_ref] reel | [provided/observed metrics or Unknown] | [only if frozen approved + active scope covered] |
| 3 | [creator_ref-3 / asset_ref] post | [provided/observed metrics or Unknown] | [NEEDS_INPUT when approval or scope is missing] |

### Channel Distribution Plan

#### Paid Advertising
| Platform | Content to Use | Format | Timeline |
|----------|---------------|--------|----------|
| TikTok Ads | [content IDs] | Spark Ads | Immediate |
| Meta Ads | [content IDs] | Video/Carousel | Week 1 |
| YouTube | [content IDs] | Shorts/Pre-roll | Week 2 |

#### Owned Channels
| Channel | Content to Use | Format | Timeline |
|---------|---------------|--------|----------|
| Website | [content IDs] | Embedded/Screenshots | Week 1 |
| Email | [content IDs] | GIF/Images | Week 2 |
| Blog | [content IDs] | Embedded + quotes | Week 3 |

#### Social Media
| Platform | Content to Use | Format | Timeline |
|----------|---------------|--------|----------|
| Instagram | [content IDs] | Repost/Stories | Ongoing |
| TikTok | [content IDs] | Stitch/Duet | Ongoing |
| Twitter | [content IDs] | Quote + link | Ongoing |

#### Sales & Marketing
| Use Case | Content to Use | Format | Timeline |
|----------|---------------|--------|----------|
| Sales deck | [content IDs] | Screenshots | Week 1 |
| Case study | [content IDs] | Quotes + metrics | Month 2 |
| Trade show | [content IDs] | Loop video | As needed |
```

## repurpose-4: Format Transformation Specs (Step 4)

```markdown
## Format Transformation Specifications

### Video to Multiple Formats — Full Video Variations
| Target | Aspect Ratio | Duration | Modifications |
|--------|--------------|----------|---------------|
| TikTok/Reels | 9:16 | 15-60s | Native or trim |
| Instagram Feed | 1:1 or 4:5 | 15-60s | Crop/letterbox |
| Facebook Feed | 1:1 or 16:9 | 15-60s | CTA overlay |
| YouTube Shorts | 9:16 | <60s | YouTube branding |
| YouTube Pre-roll | 16:9 | 15-30s | Front-load message |
| Stories | 9:16 | 15s max | Split into segments |

### Video to Static
| Asset Type | Source | Specifications |
|------------|--------|----------------|
| Thumbnail | Key frame | 1080x1080 or 1080x1920 |
| Quote card | Pull text | Brand template |
| Product shot | Frame grab | High-res moment |
| GIF | 5-10s clip | <5MB, loop |

### Quote/Review Transformations
| Format | Specifications | Use Case |
|--------|----------------|----------|
| Website testimonial | Photo + quote + name | Product pages |
| Social quote card | Designed graphic | Organic posts |
| Email testimonial | Quote + thumbnail | Campaigns |
| Ad copy | Pull key phrases | Ad headlines |

### Image Transformations
| From | To | Specifications |
|------|----|----------------|
| Carousel | Individual posts | Separate each image |
| High-res image | Multiple crops | 1:1, 4:5, 9:16 |
| Photo | Ad creative | Add copy overlay |
| Photo | Website banner | Crop to banner ratio |
```

## repurpose-5: Channel-Specific Guidelines (Step 5)

```markdown
## Channel Repurposing Guidelines

### Website Usage
- Product pages: within the exact active scope, embed approved video refs, use approved quote refs, and resolve any permitted creator display name only at publication.
- Homepage: UGC carousel/gallery; video testimonial section; social proof counter.
- Landing pages: hero video from top creator; testimonial quotes throughout; creator endorsement badges.

Implementation:
<div class="ugc-testimonial">
  <video src="[approved_asset_ref resolved at publication]" controls></video>
  <p class="quote">"[approved_quote_ref resolved at publication]"</p>
  <p class="attribution">[creator display name resolved at publication only when rights cover name attribution], [platform]</p>
</div>

### Email Marketing
Best practices: use GIFs (<5MB) for video; include a static fallback; pull compelling quotes; link to full content.
| Email Type | UGC Usage |
|------------|-----------|
| Welcome series | Testimonial quote |
| Promotional | Product demo GIF |
| Newsletter | "What creators say" section |
| Abandoned cart | Social proof quote |

### Paid Advertising — Creative Variations
For each video create: original (no changes); hook variation (different first 3s); CTA variation (different end card); length variations (15s, 30s, full); text-overlay variation.

Testing Matrix:
| Version | Hook | Body | CTA | Overlay |
|---------|------|------|-----|---------|
| A | Original | Original | Original | None |
| B | New hook | Original | Original | None |
| C | Original | Trimmed | Strong CTA | Brand |
| D | New hook | Trimmed | Strong CTA | Brand |

### Social Media Organic
Reposting: always credit the creator; ask permission even if contractual; add brand commentary; use platform repost features when available.
| Day | Content Type | Source |
|-----|--------------|--------|
| Mon | Original brand content | Brand |
| Tue | UGC repost | [creator_ref-1 / asset_ref] |
| Wed | Original brand content | Brand |
| Thu | UGC Stories | [creator_ref-2 / asset_ref] |
| Fri | UGC repost | [creator_ref-3 / asset_ref] |
```

## repurpose-6: Content Library Structure (Step 6)

```markdown
## UGC Content Library Structure

### Folder Organization
/ugc-library/
├── /raw/ (/videos/ /images/ /audio/)
├── /processed/ (/ads/ [/tiktok/ /meta/ /youtube/] /website/ /email/ /social/)
├── /creators/ (/creator_ref-1/ /creator_ref-2/ /creator_ref-3/)
└── /campaigns/ (/campaign-name-1/ /campaign-name-2/)

### Asset Naming Convention
`[campaign]_[creator_ref]_[platform]_[type]_[variation]_[date]`
Illustrative placeholders:
- [campaign]_[creator_ref]_tiktok_video_[frozen-version]_[YYYYMMDD]
- [campaign]_[creator_ref]_tiktok_video_15s_[YYYYMMDD]
- [campaign]_[creator_ref]_ig_thumbnail_01_[YYYYMMDD]

### Metadata Tracking
| Field | Description | Required value/source |
|-------|-------------|-----------------------|
| Asset ID | Unique identifier | [asset ID] |
| Frozen Asset Ref | Exact version approved by the auditor | [approved_asset_ref or NEEDS_INPUT] |
| Auditor Approval | Approval status for that exact version | [approved or NEEDS_INPUT] |
| Creator Ref | Stable opaque identity | [creator_ref; never raw handle/name/URL/provider ID] |
| Original Platform | Where created | [provided platform] |
| Content Type | Format | [provided format] |
| Duration | Length | [provided duration or Unknown] |
| Usage Rights | License type | [from cited grant or NEEDS_INPUT] |
| Rights Expiration | If applicable | [future date/perpetual from cited grant or NEEDS_INPUT] |
| Approved Uses | Exact channel/territory/format/use scope | [from cited grant or NEEDS_INPUT] |
| Rights Status Evidence | Current state | [`active` + observed time + evidence ref, or NEEDS_INPUT] |
| Performance | Original metrics | [provided/observed values with provenance, or Unknown] |
| Tags | Searchable keywords | [provided/derived non-factual labels] |
```

## repurpose-7: Usage Rights Tracker (Step 7)

```markdown
## Usage Rights Tracker

### Rights by Content
| Content ID | Creator Ref | Frozen Asset Ref | Auditor Approval | Rights Level / Exact Scope | Paid Use | Website | Email | Expires | Rights Status | `status_observed_at` | `status_evidence_ref` |
|------------|-------------|------------------|------------------|----------------------------|----------|---------|-------|---------|---------------|----------------------|-----------------------|
| UGC-[id] | [creator_ref-1] | [approved_asset_ref] | `approved` | [cited channel/territory/format/use] | [Yes if cited] | [Yes if cited] | [Yes if cited] | [future date/perpetual] | `active` | [ISO-8601 time] | [signed grant ref] |
| UGC-[id] | [creator_ref-2] | [approved_asset_ref or NEEDS_INPUT] | [approved or NEEDS_INPUT] | [cited limited scope] | [from grant] | [from grant] | [from grant] | [expired date] | `expired` | [ISO-8601 time] | [grant ref + expiry] |
| UGC-[id] | [creator_ref-3] | [approved_asset_ref] | `approved` | Organic only; [territory/format] | No | No | No | [from grant] | `active` | [ISO-8601 time] | [signed grant ref] |

Allowed rights status values are deliberately small: `active | expired | revoked | disputed | unknown`. Status describes the currently observed grant state; it does not broaden scope. `active` still requires a matching channel, territory, format, use, and unexpired term. Every status needs `status_observed_at` plus a source or explicit evidence-gap reference.

### Expiring Rights Alert
| Content | Creator Ref | Rights Expire | Action Needed |
|---------|-------------|---------------|---------------|
| [asset] | [creator_ref] | [date from cited grant] | Renew or remove |
| [asset] | [creator_ref] | [date from cited grant] | Renew or remove |

### Manual Removal Queue — Existing Placements Only

Derive one row per current placement whose rights are `expired`, `revoked`, `disputed`, `unknown`, or out of scope. This is a manual follow-up view, not an execution queue.

| Content ID | Trigger Status / Evidence | Destination | Owner | `due_at` | `completion_ref` |
|------------|---------------------------|-------------|-------|----------|------------------|
| [asset] | [`revoked`; notice ref] | [opaque live-placement ref] | [human role/ref] | [ISO-8601 time] | null |

Leave `completion_ref: null` until separately authorized human/platform action has completed and supplied evidence. Never infer completion from `due_at`, mark a row complete, pause an ad, delete a post, unpublish a page, or write to a platform from this tracker.

### Rights Expansion Opportunities
| Content | Current Rights | Potential Upgrade | Est. Cost |
|---------|----------------|-------------------|-----------|
| UGC-003 | Organic only | Add paid rights | $[X] |
| UGC-002 | 12 months | Perpetual | $[X] |
```

> Never recommend new use unless rights status is evidenced `active` and the grant covers that exact destination. `expired`, `revoked`, `disputed`, and `unknown` fail closed. A newly observed status change may be offered—with separate exact authorization—to the existing creator-registry proposal workflow; this tracker neither writes the proposal nor creates a new registry.

## Worked Example — repurpose (3 TikTok videos)

**User**: "Use these three supplied frozen, auditor-approved assets mapped to `creator_ref-1`, `creator_ref-2`, and `creator_ref-3`. Their supplied rights records are `active`, dated, evidenced, unexpired, and cover the requested derivative edits and US paid, website, email, organic-social, and YouTube destinations for the full 30-day flight. Build the reuse plan without persisting raw creator locators."

```markdown
## Repurposing Plan: 3 TikTok Videos

**Evidence basis**: asset descriptions and rank are user-provided; each destination below is limited to the supplied frozen approval and active scoped-rights records.

### Content Overview
1. creator_ref-1: 45s product demo (user-provided rank 1)
2. creator_ref-2: 30s before/after
3. creator_ref-3: 60s day-in-the-life

### Immediate Actions (Week 1) — From creator_ref-1 video (45s demo):
- TikTok Spark Ad (original)
- Instagram Reel (repost)
- Website product page embed
- 3 still images for ads/social
- 15s cut for Stories
Total: 1 video → 6 assets

### 30-Day Repurposing Calendar
| Week | Channel | Content | Asset Type |
|------|---------|---------|------------|
| 1 | TikTok Ads | creator_ref-1 / asset_ref | Spark Ad |
| 1 | Instagram | creator_ref-2 / asset_ref | Reel repost |
| 1 | Website | creator_ref-1 / asset_ref | Embed |
| 2 | Meta Ads | creator_ref-1 / asset_ref | Video ad |
| 2 | Email | creator_ref-3 / asset_ref | GIF + quote |
| 3 | YouTube | creator_ref-2 / asset_ref | Short |
| 4 | Landing page | All | Testimonials |

### Asset Checklist
- [ ] Create 15s cuts from all 3
- [ ] Pull 2 quote cards from creator_ref-3 / approved_asset_ref
- [ ] Design 3 thumbnail images
- [ ] Convert creator_ref-2 / approved_asset_ref to GIF for email
- [ ] Add CTA overlay to creator_ref-1 / approved_asset_ref for Meta
```

If the original terse request were the only input, return `NEEDS_INPUT` for the three frozen approval refs and current rights observation/evidence/scope. Do not create cuts, quote cards, a calendar, or destination recommendations until those inputs are supplied.

## Tips — repurpose

1. Plan repurposing before shooting — capture with multiple uses in mind.
2. Negotiate rights upfront — cheaper than adding later.
3. Create a system — organize for easy access.
4. Track everything — know what you can use where.
5. Refresh regularly — don't overuse the same content.
