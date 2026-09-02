# Contract Helper — Templates and Reference Packs

Moved out of `SKILL.md` to keep the skill lean. This file holds the full agreement template, parameter-gathering form, clause explanations, the review checklist, and negotiation tables. Links back to repo root use `../../../`.

⚠️ This skill provides general guidance and templates. Always have contracts reviewed by legal counsel before execution.

**Identity and execution boundary**: a saved WARM record is a reference-only contract summary. Its identity/contact fields are limited to `party_ref`, `contact_ref`, `address_ref`, and `signature_ref`, followed by the supplied term summary; never place raw legal names, entity IDs, emails, phones, postal addresses, payment details, signatures, or executable/signed document bytes in WARM. The full execution copy belongs only in the authorized external document/e-sign system. A draft, review, WARM save, or legal approval is not permission to upload or send it. Every signature request needs its own exact authorization bound to the final `recipient_ref`, SHA-256 of the exact document bytes, and delivery channel; any change to one of those values requires new approval.

---

## 1. Contract Parameters (gathering form)

```markdown
### Contract Parameters

**Parties**:
- Brand/Company party ref: [party_ref or TBD]
- Creator party ref: [party_ref or TBD]
- Delivery contact refs: [contact_ref values or TBD]
- Notice address refs: [address_ref values or TBD]
- Signature refs: [signature_ref values or TBD]

**Partnership Details**:
- Campaign: [name/description]
- Duration: [start-end dates]
- Deliverables: [what influencer will create]
- Compensation: [payment terms]

**Additional Terms**:
- Usage rights: [requirements]
- Exclusivity: [yes/no, scope]
- Approval process: [requirements]
- Platform(s): [where content will be posted]
```

---

### WARM Contract Summary (Persistable)

```yaml
party_refs: [brand-party-ref, creator-party-ref]
contact_refs: [brand-contact-ref, creator-contact-ref]
address_refs: [brand-address-ref, creator-address-ref]
signature_refs: [brand-signature-ref-or-pending, creator-signature-ref-or-pending]
term_summary:
  deliverables: [supplied scope or TBD]
  compensation: [supplied amount/schedule or TBD]
  usage_rights: [channel/territory/format/duration/use scope or TBD]
  exclusivity: [supplied scope/window or TBD]
  revisions: [supplied count/process or TBD]
  effective_and_delivery_dates: [supplied dates or TBD]
  governing_law_and_dispute_process: [supplied terms or TBD]
  execution_status: [draft | routed | partially-signed | executed]
```

Do not add raw values or the document bytes/hash to this WARM block. The e-sign provider retains its execution copy and provider audit trail outside WARM.

### E-sign Dispatch Authorization (Transient External Action)

```yaml
recipient_ref: [exact intended signer/recipient ref]
document_sha256: [SHA-256 of the exact final execution bytes]
channel: [exact e-sign/email delivery channel]
exact_authorization: [approval ref for this tuple or NEEDS_INPUT]
dispatch_state: [DRAFT_NOT_SENT | AUTHORIZED_PENDING_PROVIDER | SENT_WITH_PROVIDER_EVIDENCE]
```

Resolve the raw recipient and any legal/address values only inside the authorized provider job. Do not save this dispatch manifest as the WARM contract summary. A different recipient, document byte, or channel invalidates the authorization.

---

## 2. Full Agreement Template

**External execution copy only — never save this rendered copy to WARM.** Keep the reference-safe WARM summary above locally; resolve legal names, addresses, notices, and signature fields transiently inside the separately authorized external document/e-sign workflow.

```markdown
# INFLUENCER PARTNERSHIP AGREEMENT

---

**This Agreement** is entered into as of [DATE] ("Effective Date") by and between:

**Company**: [legal entity resolved transiently from Brand `party_ref`], a [jurisdiction/entity type from approved terms] with offices at [address resolved transiently from Brand `address_ref`] ("Brand")

and

**Creator**: [legal party resolved transiently from Creator `party_ref`], [approved entity/person description] residing/registered at [address resolved transiently from Creator `address_ref`] ("Influencer")

Collectively referred to as the "Parties."

---

## 1. SCOPE OF WORK

### 1.1 Campaign Description

Influencer agrees to create and publish content promoting Brand's [PRODUCT/SERVICE/CAMPAIGN] (the "Campaign") as detailed below.

### 1.2 Deliverables

| Platform | Content Type | Quantity | Specifications |
|----------|--------------|----------|----------------|
| [Platform] | [Type] | [#] | [Details] |
| [Platform] | [Type] | [#] | [Details] |

**Total Deliverables**: [#] content pieces

### 1.3 Content Requirements

All content must:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]
- Comply with all applicable laws and platform terms of service
- Include proper sponsorship disclosures as required by FTC guidelines

### 1.4 Timeline

| Milestone | Date |
|-----------|------|
| Agreement Execution | [Date] |
| Product Shipment | [Date] |
| Content Submission for Review | [Date] |
| Content Approval/Feedback | [Date] |
| Content Publication | [Date/Window] |
| Campaign Conclusion | [Date] |

---

## 2. COMPENSATION

### 2.1 Payment Terms

Brand agrees to compensate Influencer as follows:

| Item | Amount |
|------|--------|
| Base Fee | $[AMOUNT] |
| [Additional Item] | $[AMOUNT] |
| **Total Compensation** | **$[TOTAL]** |

### 2.2 Payment Schedule

- [PERCENTAGE]% ($[AMOUNT]) upon execution of this Agreement
- [PERCENTAGE]% ($[AMOUNT]) upon content publication

OR

- Full payment within [NUMBER] days of content publication

### 2.3 Payment Method

Payment will be made via [PAYMENT METHOD] to:

[Payment details remain in the authorized payment/provider system; the WARM summary stores no account data]

### 2.4 Taxes

Influencer is responsible for all applicable taxes. Brand will issue a 1099 form if required by law.

### 2.5 Additional Compensation (if applicable)

**Affiliate Commission**: Influencer will receive [PERCENTAGE]% commission on verified sales generated through the approved tracking reference: [opaque tracking_ref; rendered link/code only in the execution/delivery surface]

**Performance Bonus**: [If applicable, describe bonus structure]

---

## 3. CONTENT OWNERSHIP AND USAGE RIGHTS

### 3.1 Ownership

Influencer retains ownership of all original content created under this Agreement ("Content").

### 3.2 License Grant

Influencer grants Brand a [EXCLUSIVE/NON-EXCLUSIVE], [ROYALTY-FREE/PAID], [WORLDWIDE/TERRITORY-LIMITED] license to:

- [ ] Repost Content on Brand's owned social media channels
- [ ] Use Content in paid social media advertising
- [ ] Use Content on Brand's website
- [ ] Use Content in email marketing
- [ ] Use Content in presentations and sales materials
- [ ] Use Content in out-of-home advertising
- [ ] Use Content in print materials
- [ ] Create derivative works from Content
- [ ] Sublicense Content to authorized partners

### 3.3 License Duration

This license shall remain in effect for:

- [ ] The duration of this Agreement
- [ ] [NUMBER] months from content publication
- [ ] [NUMBER] years from content publication
- [ ] In perpetuity

### 3.4 Whitelisting/Paid Amplification Rights

Brand [IS/IS NOT] authorized to run paid advertisements using Influencer's identity through:

- [ ] Meta Branded Content Ads
- [ ] TikTok Spark Ads
- [ ] YouTube BrandConnect
- [ ] Other: [SPECIFY]

Duration of whitelisting rights: [DURATION]
Additional compensation for whitelisting: [IF APPLICABLE]

### 3.5 Content Modifications

Brand [MAY/MAY NOT] modify Content. Any modifications require [written approval from Influencer / no approval].

---

## 4. EXCLUSIVITY

### 4.1 Exclusivity Period

During the period from [START DATE] to [END DATE], Influencer agrees not to:

- [ ] Promote competing products/services in the [CATEGORY] category
- [ ] Enter into sponsorship agreements with the following competitors: [LIST]
- [ ] Create negative content about Brand or its products

### 4.2 Competing Brands

For purposes of this Agreement, competing brands include but are not limited to:
- [Competitor 1]
- [Competitor 2]
- [Competitor 3]

### 4.3 Exclusivity Compensation

Exclusivity compensation is [INCLUDED in base fee / an additional $AMOUNT].

---

## 5. CONTENT APPROVAL

### 5.1 Review Process

1. Influencer will submit draft content to Brand by [DATE/DEADLINE]
2. Brand will provide feedback within [NUMBER] business days
3. Influencer will make requested revisions within [NUMBER] business days
4. Brand will provide final approval within [NUMBER] business days

### 5.2 Revisions

This Agreement includes up to [NUMBER] rounds of revisions at no additional cost. Additional revisions will be billed at $[AMOUNT] per round.

### 5.3 Approval Standards

Brand may request revisions for:
- Factual inaccuracies
- Brand guideline violations
- Compliance issues
- Quality concerns

Brand may NOT request revisions that fundamentally change Influencer's creative voice.

### 5.4 Failure to Approve

If Brand fails to respond within the stated timeline, content will be deemed [APPROVED / NOT APPROVED].

---

## 6. COMPLIANCE AND DISCLOSURE

### 6.1 FTC Compliance

Influencer agrees to comply with all Federal Trade Commission (FTC) guidelines regarding endorsements and testimonials, including but not limited to clear and conspicuous disclosure of the material relationship with Brand.

### 6.2 Required Disclosures

All Content must include:
- [ ] #ad or #sponsored hashtag
- [ ] Platform branded content tools where available
- [ ] Verbal disclosure in video content
- [ ] Clear written disclosure in caption

### 6.3 Platform Terms

Influencer agrees to comply with all terms of service and community guidelines of each platform where Content is published.

### 6.4 Industry-Specific Compliance

[Include any industry-specific requirements - e.g., FDA, alcohol, financial services, etc.]

---

## 7. REPRESENTATIONS AND WARRANTIES

### 7.1 Influencer Represents and Warrants

- They have full authority to enter into this Agreement
- They own or have rights to all Content created
- Content will be original and not infringe on third-party rights
- They will provide honest opinions about products/services
- All claims made are truthful and substantiated
- They have disclosed any material relationships that might affect their endorsement
- Their follower base is authentic (no purchased followers or engagement)

### 7.2 Brand Represents and Warrants

- They have full authority to enter into this Agreement
- Products/services are as described
- They own or have rights to provide any materials given to Influencer
- Payment will be made as agreed

---

## 8. CONFIDENTIALITY

### 8.1 Confidential Information

Both Parties agree to keep confidential all non-public information related to this Agreement, including but not limited to:
- Financial terms
- Campaign strategy
- Unreleased products or information
- Business practices

### 8.2 Duration

Confidentiality obligations survive termination for [NUMBER] years.

### 8.3 Exceptions

Information is not confidential if it:
- Is publicly available
- Was known prior to disclosure
- Is required by law to be disclosed

---

## 9. INDEMNIFICATION

### 9.1 Influencer Indemnification

Influencer agrees to indemnify and hold harmless Brand from any claims arising from:
- Influencer's breach of this Agreement
- Influencer's negligence or misconduct
- Third-party claims related to Content

### 9.2 Brand Indemnification

Brand agrees to indemnify and hold harmless Influencer from any claims arising from:
- Brand's breach of this Agreement
- Brand's products or services
- Brand's use of Content beyond licensed scope

---

## 10. TERMINATION

### 10.1 Termination for Convenience

Either Party may terminate this Agreement with [NUMBER] days written notice.

### 10.2 Termination for Cause

Either Party may terminate immediately if the other Party:
- Materially breaches this Agreement
- Engages in illegal or unethical conduct
- Files for bankruptcy

### 10.3 Effect of Termination

Upon termination:
- Influencer will be compensated for work completed
- All Content licenses remain in effect as specified
- Confidentiality obligations survive
- Influencer will remove unpublished Content if requested

### 10.4 Morality Clause

Brand may terminate immediately if Influencer engages in conduct that damages Brand's reputation or is inconsistent with Brand's values, including but not limited to:
- Criminal activity
- Discriminatory behavior
- Controversial public statements

---

## 11. MISCELLANEOUS

### 11.1 Independent Contractor

Influencer is an independent contractor and not an employee of Brand.

### 11.2 Assignment

Neither Party may assign this Agreement without written consent.

### 11.3 Entire Agreement

This Agreement constitutes the entire agreement between the Parties.

### 11.4 Amendments

Amendments must be in writing and signed by both Parties.

### 11.5 Governing Law

This Agreement is governed by the laws of [STATE].

### 11.6 Dispute Resolution

Any disputes will be resolved through [mediation/arbitration/litigation] in [LOCATION].

### 11.7 Severability

If any provision is unenforceable, remaining provisions remain in effect.

### 11.8 Notices

All notices shall be sent to:

**Brand**: [notice destination resolved transiently from Brand `contact_ref` / `address_ref`]
**Influencer**: [notice destination resolved transiently from Creator `contact_ref` / `address_ref`]

---

## SIGNATURES

**BRAND**

Signature: [external e-sign field bound to Brand `signature_ref`]
Name: [legal signer display resolved transiently from Brand `party_ref`]
Title: [TITLE]
Date: _____________

**INFLUENCER**

Signature: [external e-sign field bound to Creator `signature_ref`]
Name: [legal signer display resolved transiently from Creator `party_ref`]
Date: _____________

---
```

---

## 3. Key Clauses Explained

```markdown
## Key Contract Clauses Explained

### Deliverables
**What it covers**: Specific content to be created
**Why it matters**: Clarity prevents disputes
**Watch for**: Vague terms, unlimited revisions

### Compensation
**What it covers**: Payment amounts and timing
**Why it matters**: Ensures fair payment
**Watch for**: Delayed payments, unclear terms

### Usage Rights
**What it covers**: How brand can use content
**Why it matters**: Protects creator's work
**Watch for**: Perpetual rights, unlimited usage without extra pay

### Exclusivity
**What it covers**: Restrictions on competitor work
**Why it matters**: Significant impact on creator income
**Watch for**: Broad category definitions, extended periods

### Approval Process
**What it covers**: How content is reviewed
**Why it matters**: Prevents delays and disputes
**Watch for**: Unlimited revisions, vague standards

### Morality Clause
**What it covers**: Termination for conduct issues
**Why it matters**: Protects brand reputation
**Watch for**: Overly broad definitions
```

---

## 4. Contract Review Checklist

```markdown
## Contract Review Checklist

### Essential Terms ✅

- [ ] Parties clearly identified
- [ ] Deliverables specifically defined
- [ ] Compensation clearly stated
- [ ] Payment timeline specified
- [ ] Usage rights defined and limited
- [ ] Exclusivity terms reasonable
- [ ] Approval process clear
- [ ] Termination terms fair

### Red Flags 🚩

- [ ] Perpetual usage rights without additional compensation
- [ ] Unlimited revisions
- [ ] Vague deliverable requirements
- [ ] Payment contingent on subjective approval
- [ ] Overly broad exclusivity
- [ ] One-sided termination rights
- [ ] Missing confidentiality protections
- [ ] No dispute resolution process

### Negotiation Points 💡

| Clause | Counter anchor | Source / status | Negotiate If |
|--------|----------------|-----------------|--------------|
| Usage rights | [user-supplied target or sourced range] | [dated jurisdiction/market-compatible source ref or `TBD/NEEDS_INPUT`] | Requested scope exceeds the evidenced target |
| Exclusivity | [user-supplied target or sourced range] | [dated jurisdiction/market-compatible source ref or `TBD/NEEDS_INPUT`] | Requested scope exceeds the evidenced target |
| Revisions | [user-supplied count/process or sourced anchor] | [dated compatible source ref or `TBD/NEEDS_INPUT`] | Paper is broader than the evidenced target |
| Payment | [user-supplied timing or sourced anchor] | [dated compatible source ref or `TBD/NEEDS_INPUT`] | Paper differs from the evidenced target |
| Whitelisting | [user-supplied fee/terms or sourced anchor] | [dated compatible source ref or `TBD/NEEDS_INPUT`] | Paper differs from the evidenced target |
```

Do not label an unsourced range “standard.” If no compatible anchor is supplied, explain the risk dimension and request the user's target or research source without proposing a number.

---

## 5. Common Negotiation Points (creator vs brand)

| Term | Creator position | Brand position | Evidence-bound counter |
|------|------------------|----------------|------------------------|
| Usage rights | [quoted/user-supplied] | [quoted/user-supplied] | [user target or dated compatible anchor; otherwise `TBD/NEEDS_INPUT`] |
| Exclusivity | [quoted/user-supplied] | [quoted/user-supplied] | [user target or dated compatible anchor; otherwise `TBD/NEEDS_INPUT`] |
| Revisions | [quoted/user-supplied] | [quoted/user-supplied] | [user target or dated compatible anchor; otherwise `TBD/NEEDS_INPUT`] |
| Approval | [quoted/user-supplied] | [quoted/user-supplied] | [user target or dated compatible anchor; otherwise `TBD/NEEDS_INPUT`] |
| Payment | [quoted/user-supplied] | [quoted/user-supplied] | [user target or dated compatible anchor; otherwise `TBD/NEEDS_INPUT`] |

---

## 6. Tips for Better Contracts

1. **Be specific** — vague terms cause disputes.
2. **Be fair** — one-sided contracts damage relationships.
3. **Plan for problems** — include what happens if things go wrong.
4. **Keep it readable** — complex language creates confusion.
5. **Get legal review** — always for significant partnerships.

---

## 7. Worked Example (simplified scope)

**User**: "Draft a simple agreement for a micro-influencer to create 2 Instagram posts for $500"

**Output**: Simplified agreement containing only the supplied deliverables and fee. Usage duration, channels/territory, revisions, payment timing, approval turnaround, governing law, disclosure rule, and every other omitted term remain `TBD/NEEDS_INPUT` unless the user supplies them or a source-dated jurisdiction/market-compatible anchor. If the user authorizes a WARM save, write only `party_ref`/`contact_ref`/`address_ref`/`signature_ref` plus the term summary above. Keep the executable agreement in the external e-sign system. Before routing it for signature, show the exact `recipient_ref`, SHA-256 of the final document bytes, and channel and obtain a separate exact authorization for that immutable tuple.
