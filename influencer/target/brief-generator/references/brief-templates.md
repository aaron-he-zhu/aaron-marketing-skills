# Brief Generator — Templates & Variations

Full templates and worked variations for the brief-generator skill. The skill's Instructions step 2 ("Generate Professional Brief") fills the master template below; steps for content-type and campaign-type tuning use the variation tables.

Back to the skill: [SKILL.md](../SKILL.md)

**Persistence and delivery boundary**: a saved brief or handoff uses `creator_ref`, `brand_ref`, `page_ref`, `shipping_ref`, `contact_ref`, and `voice_source_ref` for creator/brand identity, page destination, shipping destination, contact path, and voice provenance. Never persist the corresponding raw name, handle, profile/page/source URL, postal address, email, phone, provider ID, or a hidden mapping. The creator-facing render may resolve those values only transiently inside an authorized dispatch. A `Send` label, finished brief, or WARM-save approval is not delivery permission: route the single final render through `outreach-manager`'s independent exact send gate and fresh suppression/eligibility preflight.

**Platform-spec boundary**: use a dated official platform source for every format limit, duration, frame count, or placement rule. If the applicable current spec is unavailable, write `TBD/NEEDS_INPUT`; do not fill a remembered “optimal” or “typical” number.

---

## Brief Input Capture

Gather these before generating (Instructions step 1):

```markdown
### Brief Requirements

**Reference-safe identity and routing**:
- Creator: [creator_ref]
- Brand: [brand_ref]
- Landing destination: [page_ref or not applicable]
- Shipping destination: [shipping_ref or not applicable]
- Contact path: [contact_ref]
- Voice provenance: [voice_source_ref or not applicable]

**Campaign Information**:
- Campaign Name: [name]
- Brand display value: [resolve from brand_ref only in transient creator-facing render]
- Product/Service: [description]

**Deliverables**:
- Platform(s): [platforms]
- Content Type: [types]
- Quantity: [number of posts]

**Key Details**:
- Key message: [main point to convey]
- CTA: [what action should viewers take]
- Timeline: [key dates]
- Budget/Compensation: [terms]
```

---

## Master Brief Template

```markdown
---

# Influencer Campaign Brief

## Campaign: [Campaign Name]

**Creator**: [creator_ref] · **Brand**: [brand_ref] · **Page**: [page_ref] · **Shipping**: [shipping_ref] · **Contact**: [contact_ref] · **Voice source**: [voice_source_ref]

---

## 📋 Overview

### Brand
**[brand display name resolved transiently from brand_ref at dispatch]** - [One-line brand description]

[2-3 sentences about the brand, its values, and what makes it unique]

### Product/Service
**[Product Name]**

[Product description including:
- What it is
- Key features/benefits
- Price point
- Where to buy]

### Campaign Goal
[Clear statement of what this campaign aims to achieve]

### Why You
[Evidence-backed personalization for creator_ref; raw creator display name is inserted only in the transient dispatch render]

---

## 🎯 Key Messages

### Primary Message
> "[The one thing viewers should take away]"

### Supporting Messages (choose 1-2 to incorporate naturally)
- [Message 1]
- [Message 2]
- [Message 3]

### Talking Points
- [Point 1]
- [Point 2]
- [Point 3]

### What NOT to Say
- [Avoid 1]
- [Avoid 2]

---

## 📱 Deliverables

### Content Requirements

| Platform | Format | Quantity | Specs |
|----------|--------|----------|-------|
| [Platform 1] | [Format] | [#] | [Specs] |
| [Platform 2] | [Format] | [#] | [Specs] |

### Platform-Specific Details

#### [Platform 1] Requirements

**Format**: [Format type]
**Quantity**: [Number]
**Duration**: [If video: length]

**Technical Specs**:
- Aspect ratio: [ratio]
- Resolution: [minimum]
- File format: [formats]

**Caption Requirements**:
- Include: [brand_ref mention requirement, hashtag_ref values, disclosure_ref]
- Character limit: [value from dated official platform_spec_ref or TBD/NEEDS_INPUT]
- Destination/placement: [page_ref + placement from dated platform_spec_ref, or TBD/NEEDS_INPUT]

**Additional Elements**:
- [ ] [Element 1]
- [ ] [Element 2]

---

## 🎨 Creative Direction

### Creative Concept
[Describe the overall creative vision for this campaign]

### Tone & Style
- Tone: [e.g., fun and energetic / authentic and relatable / premium and aspirational]
- Style: [e.g., lifestyle integration / tutorial / review / day-in-the-life]
- Visual: [e.g., bright and colorful / moody and cinematic / minimal and clean]

### Content Structure Suggestion

**Hook window**: [user-approved timing or source-dated performance/platform rule; otherwise `TBD/NEEDS_INPUT`]
[Evidence-backed opening suggestion]

**Body**:
[What the main content should cover]

**CTA** (end):
[What viewers should do next]

### Creative Freedom
[Statement about how much creative freedom the influencer has]

> 💡 **Note**: We love your creative voice! These are guidelines, not scripts. Feel free to make this your own while hitting the key messages.

### Inspiration

**Reference Examples**:
- [voice_source_ref or other opaque approved source ref + description]
- [voice_source_ref or other opaque approved source ref + description]

**What we love about these**:
- [What makes them effective]

### Do's and Don'ts

#### ✅ Do
- [Do 1]
- [Do 2]
- [Do 3]
- [Do 4]

#### ❌ Don't
- [Don't 1]
- [Don't 2]
- [Don't 3]
- [Don't 4]

---

## 📦 Product Details

### What You'll Receive
- [Product 1] - [description/variant]
- [Product 2] - [description/variant]

**Shipping Timeline**: [Expected delivery date]
**Shipping Destination**: [shipping_ref; raw address resolves only in the authorized fulfillment/dispatch system]

### Product Key Features

| Feature | Benefit | How to Show |
|---------|---------|-------------|
| [Feature 1] | [Benefit] | [Demo suggestion] |
| [Feature 2] | [Benefit] | [Demo suggestion] |
| [Feature 3] | [Benefit] | [Demo suggestion] |

### Product USPs to Highlight
1. [USP 1]
2. [USP 2]
3. [USP 3]

---

## 🔗 Campaign Assets

### Required Elements

| Element | Details |
|---------|---------|
| Brand identity/mention | [brand_ref; raw display name/handle resolves only in transient dispatch render] |
| Campaign Hashtag | [hashtag_ref; raw hashtag resolves only in transient dispatch render] |
| Branded Hashtag | [hashtag_ref; raw hashtag resolves only in transient dispatch render] |
| Landing Page | [page_ref; raw URL resolves only in transient dispatch render] |
| Promo Code | [promo_code_ref; approved code/terms resolve only in transient dispatch render] |
| UTM destination | [page_ref; approved tracking parameters resolve only at dispatch] |

### Brand Assets (if needed)
[brand_asset_ref values; raw asset-folder URLs resolve only in the transient dispatch render]

---

## 📅 Timeline & Deadlines

| Milestone | Date | Notes |
|-----------|------|-------|
| Brief Received | [date] | Today |
| Product Delivery | [date] | |
| Concept/Script Due | [date] | Optional - for approval |
| Draft Content Due | [date] | For review before posting |
| Feedback Provided | [date] | |
| Revisions Due | [date] | If needed |
| Final Approval | [date] | |
| Content Goes Live | [date] | [time window if specific] |
| Insights/Analytics Due | [user-supplied or source-dated due date; otherwise `TBD/NEEDS_INPUT`] | [source/basis] |

**Posting Window**: [specific dates/times if applicable]

---

## ✅ Approval Process

### What to Submit for Review

1. **Before filming/creating**:
   - [ ] Concept outline OR script (optional)
   - [ ] Any questions or concerns

2. **For content approval**:
   - [ ] Draft content (unlisted/private)
   - [ ] Draft caption with all required elements

3. **After posting**:
   - [ ] Opaque live placement/page ref (raw link remains transient)
   - [ ] Screenshots of insights at the user-supplied/source-dated due time

### Submission Method
[contact_ref + approved channel; raw email/account resolves only in the independently authorized dispatch]

### Review Timeline
- Initial review: [X] business days
- Revision feedback: [X] business days

### Revision Policy
[Number of revisions included, what constitutes a revision]

---

## ⚖️ Legal & Compliance

### Disclosure Requirements

**Required disclosure**: All sponsored content MUST include clear disclosure.

**Acceptable disclosures**:
- #ad (required)
- #sponsored
- "Paid partnership with [brand display name resolved transiently from brand_ref]" (only when required by the dated applicable rule)
- Verbal disclosure using [brand_ref resolved transiently] when required by the dated applicable rule

**Placement**: Disclosure must be:
- Visible without clicking "more"
- At the beginning of caption
- Clear and unambiguous

### Content Restrictions

- [ ] No competitor mentions
- [ ] No false claims about product
- [ ] No before/after claims (unless approved)
- [ ] No pricing comparisons
- [ ] [Industry-specific restrictions]

### Usage Rights

**[brand_ref; display name resolved transiently] is granted the following rights**:
- [ ] Repost on brand social channels
- [ ] Use in paid advertising
- [ ] Use on website
- [ ] Use in email marketing
- [ ] Use in presentations/sales materials

**Duration**: [user-supplied contractual duration or `TBD/NEEDS_INPUT`]
**Territories**: [user-supplied contractual territory or `TBD/NEEDS_INPUT`]

---

## 💰 Compensation

### Payment Terms

| Item | Amount |
|------|--------|
| Base Fee | $[X] |
| [Additional deliverable] | $[X] |
| **Total** | **$[X]** |

**Payment Method**: [method]
**Payment Timeline**: [user-supplied contract term or `TBD/NEEDS_INPUT`]
**Invoice Requirements**: [what to include]

### Additional Compensation
- Affiliate commission: [% on sales with code]
- Product to keep: [Yes/No - value]
- Performance bonus: [if applicable]

---

## 📞 Contact Information

### Your Point of Contact

**Contact Ref**: [contact_ref]
**Role**: [non-identifying role]
**Delivery details**: [resolve raw name/email/phone transiently only inside the authorized dispatch]
**Response Time**: [expected response time]

### Escalation Contact
[secondary contact_ref; raw details resolve transiently only at dispatch]

---

## ❓ FAQ

**Q: Can I share the product with friends/family in the content?**
A: [Answer]

**Q: What if I need more time?**
A: [Answer]

**Q: Can I repurpose this content for other platforms?**
A: [Answer]

**Q: What happens if I'm not happy with the product?**
A: [Answer]

---

## ✍️ Brief Acknowledgment

By proceeding with this collaboration, you confirm:

- [ ] I have read and understood this brief
- [ ] I agree to the deliverables and timeline
- [ ] I will comply with disclosure requirements
- [ ] I understand the usage rights granted

**Please confirm receipt and understanding by [date].**

---

*Thank you for partnering with [brand display name resolved transiently from brand_ref]! We're excited to work with you. Don't hesitate to reach out through [contact_ref resolved transiently at dispatch].*

---
```

---

## Brief Variations by Content Type

For different content types, adjust:

```markdown
## Brief Variations

### TikTok Video Brief
- Emphasize: Hook importance, trending sounds, native feel
- Include: Sound/music options, trending formats to consider
- Duration/format: [dated official TikTok spec ref; otherwise `TBD/NEEDS_INPUT`]

### Instagram Reels Brief
- Emphasize: Visual quality, cover image, carousel option
- Include: Reel vs. Feed placement, Stories cross-posting
- Duration/format: [dated official Instagram Reels spec ref; otherwise `TBD/NEEDS_INPUT`]

### Instagram Feed Post Brief
- Emphasize: High-quality imagery, detailed caption
- Include: Carousel considerations, aesthetic fit
- Format: Square/Portrait/Landscape options

### Instagram Stories Brief
- Emphasize: Authenticity, multiple frames, swipe-up/link
- Include: Story frames breakdown, poll/questions use
- Frame count/format: [dated official Instagram Stories spec ref; otherwise `TBD/NEEDS_INPUT`]

### YouTube Video Brief
- Emphasize: Integration style (dedicated vs. mention), SEO
- Include: Video description requirements, end screen
- Duration: Varies by integration type

### YouTube Shorts Brief
- Similar to TikTok with YouTube-specific features
- Include: YouTube algorithm considerations
```

---

## Brief Templates by Campaign Type

- **Product Launch Brief** — Focus: introduction, key features, availability. Content: unboxing, first impressions, demo.
- **Review/Testimonial Brief** — Focus: honest experience, specific benefits. Content: in-depth review, before/after (if applicable).
- **Event/Activation Brief** — Focus: experience, atmosphere, brand interaction. Content: real-time posting, event highlights.
- **Always-On/Ambassador Brief** — Focus: ongoing integration, long-term relationship. Content: regular organic mentions, lifestyle integration.
- **Giveaway Brief** — Focus: entry mechanics, rules, excitement. Content: prize showcase, entry CTA.

---

## How to Invoke (extended)

### Create a Campaign Brief

```
Create an influencer brief for [campaign] with [deliverables] for [product]
```

```
Generate a brief for [influencer type] promoting [product] on [platform]
```

### Specific Content Types

```
Create a TikTok brief for a product review video
```

```
Generate an Instagram Stories brief for a brand takeover
```

---

## Tips for Great Briefs

1. **Be clear, not controlling** — guidelines, not scripts.
2. **Show inspiration** — visual examples help.
3. **Respect their voice** — that's why you hired them.
4. **Make it scannable** — use formatting, headers, bullets.
5. **Include everything** — don't make them ask questions.
6. **Be realistic** — don't ask for too much in one post.
