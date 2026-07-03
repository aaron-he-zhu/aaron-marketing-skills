---
description: "Run an email-marketing (SEND) workflow: deliverability/consent setup, segmentation, email creative, lifecycle flows, newsletter monetization, send-testing, and the email-quality audit gate. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-list> [--phase setup|engage|nurture|deliver]"
---

# Email Command

Run the email-marketing lifecycle along the **SEND loop** (Setup → Engage → Nurture → Deliver). Skills score on the [SEND framework](../references/send-benchmark.md) and operate from the user's **own-account manual export** — keyed ESP APIs (Klaviyo, Mailchimp, HubSpot, Customer.io) are never required. The discipline is use-case-agnostic: the same skills serve B2C lifecycle/ecommerce, B2B cold outbound, and newsletter/creator programs; the goal you name selects the SEND goal-weight column.

## Route

Infer the SEND-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Setup** — deliverability-qa (SPF/DKIM/DMARC/BIMI auth, reputation, inbox-placement, spam-content, list hygiene — the S1 pre-flight), list-segment-builder (behavioral + lifecycle-stage segments + suppression), list-growth-designer (acquisition strategy + compliant opt-in capture-flow spec); consult consent-registry's per-subject records (`memory/consent/`) for lawful basis and suppression before building or sending
- **Engage** — email-creative-builder (subject/preheader/body/CTA, message-matched to the landing page); pull approved claim wording from offer-claims-registry's ledger (`memory/claims/claims-ledger.md`) and route `[needs source]` flags to `memory/claims/candidates.md`; reuse audience-mapper for persona / lifecycle-stage definition
- **Nurture** — email-sequence-designer (welcome / cart / post-purchase / win-back flows + frequency governance), newsletter-monetization-planner (paid-sub / sponsorship / referral economics); reuse landing-optimizer for the post-click page
- **Deliver** — send-experiment-designer (A/B / send-time / hold-out design + significance read), then email-quality-auditor (the EQS gate + pre-send go/no-go; S2/N1 judged against consent-registry, D1 against offer-claims-registry); reuse roi-calculator / report-generator / performance-analyzer

## Rules

- `email-quality-auditor` is the pre-send gate: score EQS and enforce the four vetoes (S1/S2/N1/D1) before any send or scale; run deliverability-qa first so S1 can be trusted, and resolve unregistered claims via offer-claims-registry before the D1 check.
- `consent-registry` is the consent/suppression SSOT: only it writes `memory/consent/`; other skills drop consent candidates in `memory/consent/candidates.md` only. No consent record on file = NEEDS_INPUT (not pass-by-default) — the S2 red line.
- Keyless Tier 1 — score from native ESP / GA4 / ecommerce exports plus the DMARC aggregate (RUA) report and a seed-list/inbox-placement test the user provides; keyed ESP APIs are opt-in Tier-2/3 MCP only.
- Only `email-quality-auditor` computes the goal-weighted EQS; every other skill works one SEND lever and hands off. Over-frequency / list fatigue is a guardrail under E, not a veto.
- Label every metric Measured / User-provided / Estimated; never invent open/click/deliverability figures. Compliance checks (CAN-SPAM / GDPR / CASL) are guidance, not legal advice.
- **Scope edge — list acquisition**: [list-growth-designer](../email/setup/list-growth-designer/SKILL.md) owns the acquisition *strategy* + the compliant opt-in capture-flow *spec*; the signup form / popup *UX* is a landing/CRO job ([landing-optimizer](../measure/landing-optimizer/SKILL.md)), the *confirmation* flow is [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), the opt-in *record* is [consent-registry](../protocol/consent-registry/SKILL.md), and referral growth-loop *economics* are [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md).

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
