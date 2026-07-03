---
description: "Run a paid-ads (ROAS) workflow: audience segments, account structure, ad creative, experiment design, pre-launch signal QA + the account-audit gate, measurement, and attribution. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-account> [--phase research|orchestrate|activate|scale]"
---

# Paid Command

Run the paid-ads lifecycle along the **ROAS loop** (Research → Orchestrate → Activate → Scale). Skills score on the [ROAS framework](../references/roas-benchmark.md) and operate from the user's **own-account manual export** — keyed ad-platform APIs are never required.

## Route

Infer the ROAS-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Research** — campaign-architect (structure + search-term mining), audience-segment-builder; reuse budget-optimizer for spend; consult offer-claims-registry's live-offers table (`memory/claims/offers.md`) when structuring promo campaigns
- **Orchestrate** — ad-creative-builder, ad-test-designer; reuse landing-optimizer for the post-click page; pull approved claim wording from offer-claims-registry's ledger (`memory/claims/claims-ledger.md`) and route `[needs source]` flags to `memory/claims/candidates.md`
- **Activate** — conversion-signal-qa (build/verify tracking), then ad-account-auditor (the RQS gate + launch go/no-go; O1/O2 judged against offer-claims-registry's ledger)
- **Scale** — paid-measurement-loop, attribution-reconciler; reuse roi-calculator / report-generator / performance-analyzer

## Rules

- `ad-account-auditor` is the launch gate: score RQS and enforce the five vetoes (R1/R2/O1/O2/A1) before any budget increase; run conversion-signal-qa first so R1/R2 can be trusted, and resolve unregistered claims via offer-claims-registry before the O1/O2 checks.
- `offer-claims-registry` is the claims/offers SSOT: only it writes `memory/claims/claims-ledger.md` and `memory/claims/offers.md`; other skills drop claim candidates in `memory/claims/candidates.md` only.
- Keyless Tier 1 — score from native ad-manager / GA4 / ecommerce exports the user provides; keyed Google Ads / Meta APIs are opt-in Tier-2/3 MCP only.
- Only `ad-account-auditor` computes the goal-weighted RQS; every other skill works one lever and hands off. Bid-pacing and search-term mining are modes of budget-optimizer / campaign-architect, not separate skills.
- Label every metric Measured / User-provided / Estimated; never invent ROAS/CPA figures.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
