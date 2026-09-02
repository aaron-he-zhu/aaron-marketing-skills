# Outreach Manager — Templates

Fill-in templates for each Instructions step in [../SKILL.md](../SKILL.md). Copy the block you need and replace the bracketed placeholders. Apply the hard copy rules in [cold-copy-rules.md](cold-copy-rules.md) before sending. Drafts may retain explicit placeholders; no message may send or schedule until the eligibility, approval, and live-suppression gates below pass. Resolve a raw handle, profile/content URL, email, phone, or recipient name only transiently for research or the exact send gate. Reuse an explicitly carried opaque `creator_ref`, or a creator-registry aggregate ID only when its identity link is verified; otherwise generate one random `creator-<UUIDv4>` once for this lineage. Never derive that ref from a raw locator or deterministic hash. Before saving a template or handoff, replace direct identifiers and raw URLs throughout—including evidence, headings, subject lines, pipeline rows, signatures, and notes—with the stable `creator_ref`, resolvable opaque `handle_ref` / `recipient_ref` / `contact_source_ref` / `source_ref`, or dispatch-time placeholders. If no authorized artifact or verified registry link resolves those opaque refs, record `identity_status: unresolved`, persist no hidden locator mapping, set `cross_session_locator_required: true`, and request the raw locator again at dispatch.

## Step 1 — Outreach Parameters

```markdown
### Outreach Parameters

**Campaign Context**:
- Brand: [name]
- Campaign: [description]
- Product: [product]
- Value proposition for influencer: [why they should care]

**Transient lookup inputs (never save)**:
- Raw handle/profile URL: [resolve only for research or the exact dispatch]
- Raw content URL: [resolve only for evidence review; never persist as `source_ref`]

**Saved target identity**:
- Creator ref: [explicit upstream opaque ref / verified registry aggregate ID / random creator-<UUIDv4>]
- Identity status: [resolved/unresolved/conflict]
- Handle ref: [resolvable opaque handle_ref or unknown]
- Recipient ref: [resolvable opaque recipient_ref or unresolved]
- Contact source ref: [resolvable opaque contact_source_ref or unknown]
- Cross-session locator required: [true/false]
- Platform: [platform]
- Followers: [count]
- Niche: [category]

**Contact Eligibility (required before send/schedule)**:
- Pseudonymous subject ID: [non-PII subject-id used by consent-registry]
- Recipient ref: [resolvable opaque exact creator/management recipient; not a segment or placeholder]
- Jurisdiction: [region code or Unknown]
- Intended channel: [email/DM/etc.]
- Contact source ref: [opaque reference to where the contact path came from]
- Lawful basis: [basis or Unknown]
- Basis/evidence reference: [opaque source_ref; never a raw URL/handle]
- Contact eligibility: [Eligible/Ineligible/Unknown]
- Eligibility evidence: [opaque source_ref] · observed_at: [YYYY-MM-DD or ISO 8601]
- Negative signal on file: [none/scoped decline/stop-contact/unsubscribe/verified spam-provider complaint/consent withdrawal + opaque source_ref]
- Live suppression result: [PENDING until immediately before dispatch; result + query time]
- Exact approval for the single currently due touch: [recipient_ref + channel + final message + concrete ISO-8601 dispatch_at/timezone if scheduled + approval_ref]
- Later cadence touches: [DRAFT — NOT SCHEDULED; each requires fresh approval and checks when due]

**Outreach Details**:
- Compensation type: [ad/gifted/affiliate]
- Budget per influencer: $[X] or [product value]
- Deliverables: [what you're asking for]
- Timeline: [urgency level]
```

## Step 2 — Personalized Outreach

```markdown
## Outreach Message for [creator_ref]

**Dispatch identity:** [resolvable opaque recipient_ref / unresolved until dispatch]

**Status:** DRAFT — NOT SENT

### Personalization Research

Before crafting the message, note these personalization points:

| Element | Verifiable detail | source_ref | observed_at | Use In Message |
|---------|-------------------|------------|-------------|----------------|
| Recent content | [specific asset and observable detail] | [resolvable opaque evidence ref] | [date/ISO 8601] | Reference as ice-breaker |
| Content style | [observable format or pattern] | [opaque evidence/export refs] | [date/ISO 8601] | Explain the campaign criterion match |
| Audience | [measured demographic fact, if supplied] | [opaque analytics/export ref] | [date/ISO 8601] | Connect to campaign |
| Values | [explicit statement, not inference] | [opaque evidence ref] | [date/ISO 8601] | Align with an approved brand criterion |
| Past partnerships | [verified brand refs] | [opaque evidence/portfolio ref] | [date/ISO 8601] | Mention only when relevant |

If either `source_ref` or `observed_at` is missing, omit the fact or leave a bracketed placeholder. Do not convert an inference into a creator belief, and do not invent first-person viewing, purchasing, product-use, or relationship history for the sender.

### Primary Outreach Message

**Subject Line Options**:
1. "[Evidence-backed content topic] — a [Brand] collaboration idea"
2. "[Approved campaign name] — proposed [deliverable]"
3. "A collaboration question from [Brand]"

---

**Message:**

[Recipient name], your [specific asset] [verifiable observation supported by opaque source_ref].

I'm [sender resolved at dispatch] at [Brand]; [approved one-sentence offer naming the campaign, deliverable, and compensation].

Open to the brief?

[Approved sender signature resolved transiently at dispatch]

---

### Message Variations

**Shorter Version (DM-friendly):**

[Recipient name], your [specific asset] [verifiable observation supported by opaque source_ref].

[Brand] is proposing [approved compensation] for [approved deliverable] in [campaign].

Open to the brief?

---

**More Formal Version (Email/Management):**

[Recipient/management name resolved transiently at dispatch], [creator display name resolved transiently at dispatch]'s [specific asset] [verifiable observation supported by opaque source_ref], matching [named campaign criterion].

[Brand] proposes [approved compensation] for [approved deliverable] in [campaign].

Would reviewing the brief be useful?

[Approved sender signature resolved transiently at dispatch]
```

## Step 3 — Follow-Up Sequence

```markdown
## Follow-Up Sequence

**Status:** DRAFT — NOT SENT

### Timing Strategy

| Touch | Draft window | Exact `dispatch_at` + timezone | Channel | Purpose |
|-------|--------------|------------------------------------------------------------|---------|---------|
| Initial | Day 0 | [fill only when this is the single due touch; otherwise unresolved] | [Email/DM] | First outreach |
| Follow-up 1 | Day 3-4 | [fill only when this is the single due touch; otherwise unresolved] | Same channel | Add one approved detail |
| Follow-up 2 | Day 7-8 | [fill only when this is the single due touch; otherwise unresolved] | Same approved eligible channel | Add a different approved detail |
| Follow-up 3 | Day 14 | [fill only when this is the single due touch; otherwise unresolved] | Original channel | Close the loop |
| Archive | Day 21 | N/A — not a dispatch | - | Archive the draft cadence |

Never fill or approve multiple future timestamps as a batch. All touches except the single currently due one remain `DRAFT — NOT SCHEDULED`.

### Follow-Up Messages

**Follow-Up #1 (Day 3-4):**

Subject: [Campaign] — one additional detail

[Recipient name], following up on [campaign] with one detail not included in the first note.

[Approved new detail supported by claims-or-brief ref].

Worth a look?

[Approved sender signature resolved transiently at dispatch]

---

**Follow-Up #2 (Day 7-8):**

Subject: [Campaign] — [approved new value detail]

[Recipient name], one more relevant detail for [campaign]: [approved new value or scope detail].

[Approved compensation/deliverable remains unchanged, or state the exact approved change].

Open to the brief, or should I close this offer?

[Approved sender signature resolved transiently at dispatch]

---

**Follow-Up #3 (Day 14 - Final):**

Subject: Closing the loop on [campaign]

[Recipient name], closing the loop on [campaign] with [final approved useful detail].

I won't send another message about this exact offer unless you reopen it.

If you want the brief later, reply here.

[Approved sender signature resolved transiently at dispatch]

---

### Follow-Up Best Practices

**Do:**
- Add new value in each follow-up
- Keep the note neutral; never assume their inbox volume, schedule, interest, or reaction
- Make it easy to say no
- Stay on the approved eligible channel; treat any new channel as a new eligibility and approval decision
- Keep messages shorter each time
- Stop the current offer cadence on a clear offer decline and record its exact campaign/offer/category scope, `observed_at`, and opaque `source_ref` inline; persist it only with separate exact authorization. A later cadence inside that scope needs newer cited reopening evidence. Do not globally suppress a scoped decline or commercial objection
- Map explicit consent signals exactly: stop-contact → `user-request`; unsubscribe → `unsubscribe`; verified channel/provider spam complaint → `complaint`; consent withdrawal → `withdrawal`
- Before every actual dispatch, re-resolve and verify the root runtime/schema and re-run live consent-registry `is-suppressed` inside the delivery job; never rely on the Day 0 result for later touches
- Keep every future touch unscheduled and approve/check/dispatch only the single currently due touch, regardless of provider features

**Don't:**
- Follow up more than 3-4 times
- Sound desperate or pushy
- Send identical messages
- Follow up daily
- Guilt trip for not responding
- Treat `not suppressed` as proof of lawful basis or permission to contact
```

## Step 4 — Negotiation Guide

```markdown
## Negotiation Guide

### Current Situation

| Factor | Details |
|--------|---------|
| Creator ref | [creator_ref] |
| Recipient | [recipient_ref] |
| Their ask | $[X] |
| Our budget | $[Y] |
| Gap | $[Z] |
| Deliverables | [what they'd provide] |

### Negotiation Strategies

**Strategy 1: Value Exchange**

Instead of increasing cash, offer additional value:

| Offer | Value | Script |
|-------|-------|--------|
| Extended usage rights | [$X value supported by source_ref] | "Would separately documented whitelisting rights for [exact channels/duration/territory] at $[X] help bridge the gap? No rights activate until contract-helper records the agreement." |
| Additional product | [$X value supported by source_ref] | "We can include [approved additional products] with a documented value of $[X]." |
| Affiliate commission | [approved %] | "Would an approved [X%] commission on attributed sales through the agreed tracking method help?" |
| Long-term commitment | [future value] | "If this goes well, we'd be open to discussing an ambassador plan with [X] potential partnerships per year; any commitment would be agreed separately in writing." |

---

**Strategy 2: Scope Adjustment**

Modify deliverables to fit budget:

| Original Ask | Modified Scope | Budget Fit |
|--------------|----------------|------------|
| 1 Reel + 3 Stories | 1 Reel only | Reduces cost [%] |
| Dedicated video | Integration mention | Reduces cost [%] |
| Exclusive content | Non-exclusive | Reduces cost [%] |

**Script**: "Your quoted $[X] is above the approved $[Y] budget for this campaign. Would you be open to [modified scope] for $[Y]?"

---

**Strategy 3: Future Value**

Describe future discussion as conditional, not promised value:

**Script**: "We can't meet $[X] for this campaign. We can offer $[Y] for the stated scope and evaluate the measured results afterward; any future campaign or budget would require a separate written agreement. Would that work?"

---

### Negotiation Scripts

**Their ask is too high:**

"Thank you for sharing the $[X] rate. The approved budget for this campaign is $[Y]. Is there flexibility, or should we compare a reduced scope and any separately priced rights?"

**They want more deliverables:**

"We'd be happy to discuss adding [deliverable]. For the additional content, we could offer an extra $[X], bringing the total to $[Y]. Does that work for you?"

**They're hesitant about the brand:**

"That makes sense. The approved brand evidence available for review is [opaque claims/testimonial/campaign ref; omit if not supplied]. Would the evidence pack or campaign brief answer the immediate question?"

**They want exclusivity:**

"Exclusivity is definitely something we can discuss. For [duration] exclusivity in [category], we could increase the compensation to $[X]. Would that work?"

---

### Common Objections & Responses

| Objection | Response |
|-----------|----------|
| "Your rate is too low" | [Value exchange or scope adjustment] |
| "I don't do sponsored content" | "Understood — thanks for letting me know. I won't follow up about sponsored work." Stop the sponsored cadence and record a scoped creator preference; suppress consent only for a separate explicit stop-contact (`user-request`), unsubscribe (`unsubscribe`), verified spam/provider complaint (`complaint`), or consent withdrawal (`withdrawal`). |
| "I've never heard of your brand" | "The approved brand evidence available is [opaque claims/testimonial/campaign ref; omit if absent]. Would the evidence pack be useful?" |
| "Bad timing right now" | "Understood. Should I close this offer, or is there one exact date on which you authorize a single follow-up?" Do not invent a cooling period or schedule without the reply. |
| "I need to check with my manager" | "Of course. Share the preferred management contact path; we'll retain only its pseudonymous contact-source reference and resolve the raw address at dispatch." |
| "I only work with my agency" | "Understood. Share the agency contact path; we'll retain only its pseudonymous contact-source reference and resolve the raw address at dispatch." |
```

## Step 5 — Outreach Pipeline Tracker

```markdown
## Outreach Pipeline Tracker

### Pipeline Overview

| Stage | Count | Conversion Rate |
|-------|-------|-----------------|
| Identified | [#] | - |
| Contacted | [#] | [%] from identified |
| Responded | [#] | [%] from contacted |
| Negotiating | [#] | [%] from responded |
| Confirmed | [#] | [%] from negotiating |
| Declined/No Contact/No Response | [#] | - |

### Detailed Pipeline

| Creator ref | Identity status | Recipient ref | Platform | Status | Last Contact | Next Action | Due | Notes |
|-------------|-----------------|---------------|----------|--------|--------------|-------------|-----|-------|
| [creator_ref-1] | [resolved/unresolved] | [recipient_ref/unknown] | [platform] | Negotiating | [date] | Send revised offer | [date] | Ask: $[X] |
| [creator_ref-2] | [resolved/unresolved] | [recipient_ref/unknown] | [platform] | Awaiting Response | [date] | Prepare Follow-up #2 draft; do not schedule | [draft window] | No response observed |
| [creator_ref-3] | resolved | [recipient_ref] | [platform] | Confirmed | [date] | Handoff to contract-helper | [date] | Agreed terms ref: [opaque ref] |
| [creator_ref-4] | [resolved/unresolved] | [recipient_ref/unknown] | [platform] | Declined — scoped offer preference | [date] | None | - | Scope: [campaign/offer/category]; source_ref: [opaque ref]; newer reopening evidence: [opaque ref/none]; no global suppression |
| [creator_ref-5] | [resolved/unresolved] | [recipient_ref/unknown] | [platform] | No contact — global suppression [recorded/pending] | [date] | None | - | Exact signal/reason code: [stop-contact/user-request | unsubscribe/unsubscribe | verified spam-provider complaint/complaint | consent withdrawal/withdrawal]; event/handoff: [opaque ref] |

### Today's Actions

| Priority | Creator ref | Recipient ref | Action | Notes |
|----------|-------------|---------------|--------|-------|
| 🔴 High | [creator_ref] | [recipient_ref/unknown] | [action] | [notes] |
| 🟡 Medium | [creator_ref] | [recipient_ref/unknown] | [action] | [notes] |
| 🟢 Low | [creator_ref] | [recipient_ref/unknown] | [action] | [notes] |

### Pipeline Health

- **Response rate**: [% or Unknown] ([Measured from supplied campaign/CRM data] or [Estimated source-dated comparator + source_ref/window])
- **Confirmation rate**: [% or Unknown] ([Measured from supplied campaign/CRM data] or [Estimated source-dated comparator + source_ref/window])
- **Average time to confirm**: [X days]
- **Top objection**: [most common reason for decline]
```

## Worked Example — evidence-bound placeholders

**User**: "Write outreach for `creator_ref: creator-042`. Evidence supplied: transient content locator `[raw URL—do not save]`, `source_ref: [opaque authorized artifact ref]`, `observed_at: [ISO 8601]`, and `observable_detail: [exact visible detail]`. Approved campaign, product, deliverable, and compensation wording is in `[claims-or-brief-ref]`."

**Output**:

```markdown
## Outreach for `creator_ref: creator-042`

### Personalization Points
- Content item: `[content title or format supported by evidence]` · source_ref: `[opaque authorized artifact ref]` · observed_at: `[ISO 8601]`
- Observable detail: `[exact visible detail from supplied evidence]` · source_ref: `[same opaque authorized artifact ref]` · observed_at: `[ISO 8601]`
- Past partners: not supplied — omit rather than infer

### Primary Message

Subject: `[evidence-backed content topic]` — collaboration idea from `[Brand]`

[Recipient name resolved transiently at dispatch], your `[content item]` `[observable detail supported by opaque source_ref]`.

I'm `[sender resolved transiently at dispatch]` at `[Brand]`; `[approved one-sentence offer naming campaign, deliverable, and compensation]`.

Open to the brief?

[Approved sender signature resolved transiently at dispatch]
```

## Tips for Successful Outreach

1. **Do your research** — use a specific observation backed by an opaque authorized evidence ref.
2. **Lead with value** — what's in it for them?
3. **Be concise** — busy creators skim.
4. **Be professional but human** — not corporate-speak.
5. **Make responding easy** — clear ask, simple yes/no.
6. **Respect their time** — don't over-follow-up.
