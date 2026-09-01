---
name: contract-helper
slug: contract-helper
displayName: "Contract Helper · 合作合同助手"
summary: "红人合作协议要点:交付物、授权、独家与披露条款清单及谈判要点"
description: 'Use when the user asks to "draft an influencer contract", "review these agreement terms", or "build a partnership template"; produces a full influencer agreement framework (scope, compensation, usage rights, exclusivity, FTC disclosure), a clause-by-clause review with red flags, and a negotiation cheat sheet. Not for outreach negotiation before a deal exists — use outreach-manager. 达人合同/合作协议条款审查'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when drafting a new influencer or creator agreement, reviewing an incoming contract or agency paper, negotiating terms such as usage rights or exclusivity, explaining standard clauses, or building a reusable partnership template. Auto-activate once a partnership is agreed in principle and the deal needs paperwork."
argument-hint: "<deliverables and compensation> [platform] | review <pasted terms>"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "activate", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "activate"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Contract Helper

Create and review influencer partnership agreements. Clear contracts protect both brand and creator and set expectations for the collaboration.

⚠️ This skill provides general guidance and templates. Always have contracts reviewed by legal counsel before execution.

## Quick Start

```
Draft an influencer agreement for [deliverables] with [compensation terms]
```
```
Review these contract terms from an influencer agency: [paste terms]
```

## Skill Contract

- **Reads**: campaign brief, agreed deliverables, compensation figure, platform list, usage-rights and exclusivity needs, any pasted incoming agreement, and stable `party_ref`, `contact_ref`, `address_ref`, and `signature_ref` values when available. Raw legal names, entity identifiers, emails, phones, postal addresses, payment details, and signatures are transient execution inputs only. If `memory-management` is active, prior outreach terms and budget caps load from the hot cache. For a rostered creator, resolve the carried opaque `creator_ref` through its authorized artifact or verified registry link, then read `memory/creators/<aggregate-id>.md` — the [creator-registry](../../../protocol/creator-registry/SKILL.md) projection — for existing exclusivity windows, contract status, usage-rights history, and standard-range anchors before drafting or reviewing. Never derive the path from a raw handle.
- **Writes**: return the drafted agreement or review memo inline by default. With exact WARM-save authorization, `memory/influencer/contract-helper/YYYY-MM-DD-<topic>.md` stores only `party_ref`, `contact_ref`, `address_ref`, `signature_ref`, and a non-PII terms summary; it never stores raw party/contact/address/signature values, payment details, or the executable/signed document bytes. The e-sign execution copy remains in the authorized external document/e-sign system. Each signed-term update requires a separate exact authorization for an `operation: propose` request through `registry-events.py` to `memory/events/creators.ndjson`; only `creator-registry` writes canonical roster records.
- **Promotes**: only with separate exact authorization, promote durable signed terms (usage-rights window, exclusivity scope, payment schedule) to `memory/hot-cache.md`.
- **Done when**:
  - Every required term is filled or explicitly marked TBD (parties, deliverables, compensation, payment timeline, usage rights, exclusivity, termination).
  - Red flags are listed for any review, and a legal-counsel review note is attached before execution.
  - A negotiation cheat sheet maps each open term only to a user-supplied target or a source-dated, jurisdiction/market-compatible anchor; otherwise the counter remains `TBD/NEEDS_INPUT`.
  - Any WARM record is reference-only, and any signature request is either not sent or has its own exact authorization bound to the final recipient, document bytes, and channel.
- **Primary next skill**: [brief-generator](../../target/brief-generator/SKILL.md) — after signature, create or finalize the creator-ready brief, then let the creator fulfill it. A signature alone is never enough to route to amplification.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). The skill works by asking you for the inputs directly: parties, deliverables, compensation, platform, and any incoming terms to review. Paste an agency's draft and it reviews against the checklist with zero setup.

Optional connectors that COULD speed up specific steps:

- `~~CRM` / deal record — pull agreed scope and rate so you don't re-type them.
- `~~influencer database` — resolve legal-name/entity inputs transiently from authorized party refs for the external execution copy; retain only opaque refs in WARM.
- `~~e-signature` — hold the full execution copy outside WARM and route it only after the independent signature-send authorization below.

See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category. None are required.

## Instructions

When a user requests contract help:

1. **Gather contract parameters** — capture `party_ref`, `contact_ref`, `address_ref`, and `signature_ref` plus partnership details (campaign, duration, deliverables, compensation) and additional terms (usage rights, exclusivity, approval, platforms). Raw identity/contact/address/signature inputs stay transient. Use the gathering form in [references/templates.md §1](references/templates.md).
2. **Draft the agreement** — fill the 11-section framework (scope, compensation, usage rights, exclusivity, approval, compliance/FTC, warranties, confidentiality, indemnification, termination, miscellaneous + signatures). The reference-safe WARM summary and the external-only execution-copy template are separated in [references/templates.md §2](references/templates.md). Scale sections to deal size — drop whitelisting/broad-exclusivity blocks for small deals.
3. **Explain key clauses** — for each material clause give what it covers, why it matters, and what to watch for. Clause guide in [references/templates.md §3](references/templates.md).
4. **Review and flag** — for any incoming paper, run the checklist: essential terms present, red flags, and per-clause counters. Never use a built-in duration, revision count, turnaround time, or payment term as a default. A numerical counter must be user-supplied or tied to a source-dated, jurisdiction/market-compatible anchor; otherwise mark it `TBD/NEEDS_INPUT`. Checklist + tables in [references/templates.md §4-5](references/templates.md).
5. **Prepare and authorize e-sign execution** — keep the full executable agreement in the external e-sign/document system, compute the SHA-256 over the exact final document bytes, and show the exact `recipient_ref`, document hash, and delivery channel. Sending for signature is an external mutation and requires an independent exact authorization bound to that tuple; drafting, legal review, WARM save, HOT promotion, or a prior send approval does not cover it. Resolve the raw recipient/contact/address only inside the authorized provider call. If any document byte, recipient, or channel changes, discard the approval and request a new one. Do not upload, route, or send when the tuple or authorization is missing.
6. **Route after signature** — if no final creator-ready brief exists, hand off to [brief-generator](../../target/brief-generator/SKILL.md). If the brief already exists, proceed with creator fulfillment; when a submission arrives, hand its frozen version to [creator-content-auditor](../creator-content-auditor/SKILL.md) for revision/approval. Route an auditor-approved frozen asset to [content-amplifier](../content-amplifier/SKILL.md) only when active rights cover the intended use; Spark/boost paths additionally require the matching live post, while a dark-post path does not. Do not skip fulfillment or the content gate merely because the agreement is signed.

Return the drafted agreement or review memo inline. Offer a reference-only terms summary at the exact WARM save path; never place the e-sign execution copy there. Ask separately before any HOT promotion. Once terms are signed, offer another exact authorization for a one-line `operation: propose` update (usage-rights window, exclusivity scope, final rate) through `registry-events.py` to `memory/events/creators.ndjson` for [creator-registry](../../../protocol/creator-registry/SKILL.md) to reconcile. Drafting, signing, saving, and signature delivery are four distinct authorization surfaces; none authorizes another.

If an authorized lightweight campaign tracker already exists, offer to record `stage: contracted` with the signed agreement in `evidence_refs`; that WARM update needs its own exact save authorization and is not canonical. If the brief is already final, do not invoke another planning skill merely to extend the chain: hand the contracted brief to the creator for fulfillment, record later submissions when authorized, and invoke the auditor only after content is submitted.

## Example

**User**: "Draft a simple agreement for 2 Instagram posts at $500, Net 30 after acceptance, two revision rounds, non-exclusive 12-month owned-channel rights in the US, draft due 15 Sep and go-live 22 Sep."

**Output**: a simplified agreement scoped to those supplied terms — 2 IG posts, $500 Net 30, two revision rounds, non-exclusive 12-month US owned-channel rights, the supplied dates, and #ad disclosure. Heavier sections outside the deal are omitted or marked TBD, not invented. Any authorized WARM save is the reference-only term summary; the executable agreement stays in the external e-sign system and is not sent without the separately approved `recipient_ref` + document SHA-256 + channel tuple. See [references/templates.md §7](references/templates.md) for the worked walkthrough.

## Reference Materials

- [references/templates.md](references/templates.md) — gathering form, full 11-section agreement template, clause explanations, review checklist, negotiation tables, tips, worked example.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path convention.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless connector recipes per category.
- Sibling skills: [outreach-manager](../outreach-manager/SKILL.md) (negotiate before contract), [creator-content-auditor](../creator-content-auditor/SKILL.md) (execute the approval clause), [budget-optimizer](../../target/budget-optimizer/SKILL.md) (set compensation), [brief-generator](../../target/brief-generator/SKILL.md) (attach the brief as an exhibit).

## Next Best Skill

**Primary**: [brief-generator](../../target/brief-generator/SKILL.md) — create or finalize the creator-ready brief after signature.

**Conditional next steps**:
- **Brief already final**: proceed with creator fulfillment; when content is submitted, use [creator-content-auditor](../creator-content-auditor/SKILL.md) to run the approval workflow the contract defines.
- **Asset approved for reuse**: use [content-amplifier](../content-amplifier/SKILL.md) only after confirming the frozen asset is auditor-approved and covered by active rights for the intended use; require a matching live post only for Spark/boost or another existing-post method.
- [outreach-manager](../outreach-manager/SKILL.md) — if terms stall, return to negotiation before re-drafting.

**Termination**: keep a visited-set for this session. If a skill above has already been invoked, stop and report chain-complete rather than re-running it. Max chain depth is 3 hops; once reached, summarize and hand back to the user.

## Related Skills

- [outreach-manager](../outreach-manager/SKILL.md) - Negotiate before contract
- [brief-generator](../../target/brief-generator/SKILL.md) - Attach brief as exhibit
- [creator-content-auditor](../creator-content-auditor/SKILL.md) - Execute approval process
- [budget-optimizer](../../target/budget-optimizer/SKILL.md) - Set compensation terms
