---
name: contract-helper
slug: contract-helper
displayName: "Contract Helper · 合作合同助手"
summary: "红人合作协议要点:交付物、授权、独家与披露条款清单及谈判要点"
description: 'Use when the user asks to "draft an influencer contract", "review these agreement terms", or "build a partnership template"; produces a full influencer agreement framework (scope, compensation, usage rights, exclusivity, FTC disclosure), a clause-by-clause review with red flags, and a negotiation cheat sheet. Not for outreach negotiation before a deal exists — use outreach-manager. 达人合同/合作协议条款审查'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when drafting a new influencer or creator agreement, reviewing an incoming contract or agency paper, negotiating terms such as usage rights or exclusivity, explaining standard clauses, or building a reusable partnership template. Auto-activate once a partnership is agreed in principle and the deal needs paperwork."
argument-hint: "<deliverables and compensation> [platform] | review <pasted terms>"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "activate", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "activate"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
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

- **Reads**: campaign brief, agreed deliverables, compensation figure, platform list, usage-rights and exclusivity needs, any pasted incoming agreement. If `memory-management` is active, prior outreach terms and budget caps load from the hot cache. For rostered creators, read `memory/creators/<handle-slug>.md` — the [creator-registry](../../../protocol/creator-registry/SKILL.md) roster record — for existing exclusivity windows, contract status, usage-rights history, and standard-range anchors before drafting or reviewing.
- **Writes**: drafted agreement or review memo to `memory/influencer/contract-helper/YYYY-MM-DD-<topic>.md`. Signed terms (usage-rights window, exclusivity scope, final rate) also go as a one-line update to `memory/events/creators.ndjson` via an authorized `operation: propose` request to `registry-events.py` — only `creator-registry` writes canonical roster records.
- **Promotes**: durable facts (signed terms, usage-rights window, exclusivity scope, payment schedule) to `memory/hot-cache.md`.
- **Done when**:
  - Every required term is filled or explicitly marked TBD (parties, deliverables, compensation, payment timeline, usage rights, exclusivity, termination).
  - Red flags are listed for any review, and a legal-counsel review note is attached before execution.
  - A negotiation cheat sheet maps each open term to a standard range.
- **Primary next skill**: [content-amplifier](../content-amplifier/SKILL.md) — once the contract is signed, amplify the licensed content.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). The skill works by asking you for the inputs directly: parties, deliverables, compensation, platform, and any incoming terms to review. Paste an agency's draft and it reviews against the checklist with zero setup.

Optional connectors that COULD speed up specific steps:

- `~~CRM` / deal record — pull agreed scope and rate so you don't re-type them.
- `~~influencer database` — confirm the creator's legal name, entity, and audience-authenticity signals for the warranties section.
- `~~e-signature` — route the finished agreement for signing.

See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category. None are required.

## Instructions

When a user requests contract help:

1. **Gather contract parameters** — parties, partnership details (campaign, duration, deliverables, compensation), and additional terms (usage rights, exclusivity, approval, platforms). Use the gathering form in [references/templates.md §1](references/templates.md).
2. **Draft the agreement** — fill the 11-section framework (scope, compensation, usage rights, exclusivity, approval, compliance/FTC, warranties, confidentiality, indemnification, termination, miscellaneous + signatures). Full template in [references/templates.md §2](references/templates.md). Scale sections to deal size — drop whitelisting/broad-exclusivity blocks for small deals.
3. **Explain key clauses** — for each material clause give what it covers, why it matters, and what to watch for. Clause guide in [references/templates.md §3](references/templates.md).
4. **Review and flag** — for any incoming paper, run the checklist: essential terms present, red flags, and per-clause negotiation ranges. Checklist + tables in [references/templates.md §4-5](references/templates.md).

Save the drafted agreement or review memo to `memory/influencer/contract-helper/YYYY-MM-DD-<topic>.md`, and promote durable signed terms to the hot cache. Once terms are signed, also submit them (usage-rights window, exclusivity scope, final rate) as a one-line update to `memory/events/creators.ndjson` via an authorized `operation: propose` request to `registry-events.py` for [creator-registry](../../../protocol/creator-registry/SKILL.md) to reconcile into the roster record.

## Example

**User**: "Draft a simple agreement for a micro-influencer to create 2 Instagram posts for $500"

**Output**: a simplified agreement scoped to the deal — 2 IG posts, $500 with a payment schedule, non-exclusive 12-month usage on owned channels, #ad disclosure, and a short timeline. Heavier sections (whitelisting, broad exclusivity, multi-round approval) are dropped. See [references/templates.md §7](references/templates.md) for the worked walkthrough.

## Reference Materials

- [references/templates.md](references/templates.md) — gathering form, full 11-section agreement template, clause explanations, review checklist, negotiation tables, tips, worked example.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path convention.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless connector recipes per category.
- Sibling skills: [outreach-manager](../outreach-manager/SKILL.md) (negotiate before contract), [creator-content-auditor](../creator-content-auditor/SKILL.md) (execute the approval clause), [budget-optimizer](../../target/budget-optimizer/SKILL.md) (set compensation), [brief-generator](../../target/brief-generator/SKILL.md) (attach the brief as an exhibit).

## Next Best Skill

**Primary**: [content-amplifier](../content-amplifier/SKILL.md) — once the agreement is signed and usage rights are locked, amplify the licensed content into paid and owned channels.

**Alternates (same Activate family)**:
- [creator-content-auditor](../creator-content-auditor/SKILL.md) — run the approval workflow the contract defines.
- [outreach-manager](../outreach-manager/SKILL.md) — if terms stall, return to negotiation before re-drafting.

**Termination**: keep a visited-set for this session. If a skill above has already been invoked, stop and report chain-complete rather than re-running it. Max chain depth is 3 hops; once reached, summarize and hand back to the user.

## Related Skills

- [outreach-manager](../outreach-manager/SKILL.md) - Negotiate before contract
- [brief-generator](../../target/brief-generator/SKILL.md) - Attach brief as exhibit
- [creator-content-auditor](../creator-content-auditor/SKILL.md) - Execute approval process
- [budget-optimizer](../../target/budget-optimizer/SKILL.md) - Set compensation terms
