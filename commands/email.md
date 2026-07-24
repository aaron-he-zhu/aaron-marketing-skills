---
description: "Run an email-marketing (SEND) workflow: deliverability/consent setup, segmentation, email creative, lifecycle flows, newsletter monetization, send-testing, and the email-quality audit gate. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-list> [--phase setup|engage|nurture|deliver]"
---

# Email Command

Run the email-marketing lifecycle along the **SEND loop** (Setup → Engage → Nurture → Deliver). Skills score on the [SEND framework](../references/send-benchmark.md) and operate from the user's **own-account manual export** — keyed ESP APIs (Klaviyo, Mailchimp, HubSpot, Customer.io) are never required. The discipline is use-case-agnostic: the same skills serve B2C lifecycle/ecommerce, B2B cold outbound, and newsletter/creator programs; the goal you name selects the SEND typed profile.

## Route

Infer the SEND-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Setup** — deliverability-qa (SPF/DKIM/DMARC/BIMI auth, reputation, inbox-placement, spam-content — the S1 pre-flight), list-segment-builder (behavioral + lifecycle-stage segments + suppression), list-growth-designer (acquisition strategy + compliant opt-in capture-flow spec), list-hygiene-monitor (scheduled list-health / decay watch); consult consent-registry's per-subject records (`memory/consent/`) for lawful basis and suppression before building or sending
- **Engage** — email-creative-builder (subject/preheader/body/CTA, message-matched to the landing page), subject-line-lab (subject variants + pre-score + truncation/spam check), email-render-builder (responsive HTML + dark-mode + cross-client QA), dynamic-content-personalizer (merge tags + conditional blocks per segment); read approved wording from the claims projection and submit `[needs source]` items as claims proposals; reuse audience-mapper for persona / lifecycle-stage definition
- **Nurture** — email-sequence-designer (welcome / cart / post-purchase / win-back flows + frequency governance), newsletter-monetization-planner (paid-sub / sponsorship / referral economics), preference-frequency-manager (preference center + frequency opt-down ladder), reactivation-specialist (win-back + re-permission + list sunset); reuse landing-optimizer for the post-click page
- **Deliver** — send-experiment-designer (A/B / send-time / hold-out design + significance read), inbox-placement-monitor (post-send seed-list inbox-vs-spam trend), cold-outbound-sequencer (B2B cold sequence + reply-triage branching + domain warmup), then email-quality-auditor (the EQS gate + pre-send go/no-go; S2/N1 judged against consent-registry, D1 against offer-claims-registry); reuse roi-calculator / report-generator / performance-analyzer

For a pre-send safety question, use the explicit ordered route
`/aaron-marketing:email --phase deliver`: run `deliverability-qa` first so S1
authentication evidence is trustworthy, then run `email-quality-auditor` for
the EQS gate and pre-send verdict. Missing ESP/GA4 exports, DMARC/auth records,
consent evidence, or claims evidence maps to the affected control's
`NEEDS_INPUT`; it never shortens or reorders this gate.

## Rules

- `email-quality-auditor` is the pre-send gate: score EQS and enforce the four vetoes (S1/S2/N1/D1) before any send or scale; run deliverability-qa first so S1 can be trusted, and resolve unregistered claims via offer-claims-registry before the D1 check.
- `memory/events/consent.ndjson` is the consent/suppression history. Ordinary skills submit proposals; `consent-registry` owns canonical changes. Suppress/erase events apply directly, and send eligibility must use replay-safe `is-suppressed`; missing consent evidence remains Unknown/NEEDS_INPUT, never pass-by-default.
- Keyless Tier 1 — score from native ESP / GA4 / ecommerce exports plus the DMARC aggregate (RUA) report and a seed-list/inbox-placement test the user provides; keyed ESP APIs are opt-in Tier-2/3 MCP only.
- Only `email-quality-auditor` computes the profile-weighted EQS; every other skill works one SEND lever and hands off. Over-frequency / list fatigue is a guardrail under E, not a veto.
- Label every metric Measured / User-provided / Estimated; never invent open/click/deliverability figures. Compliance checks (CAN-SPAM / GDPR / CASL) are guidance, not legal advice.
- **Scope edge — list acquisition**: [list-growth-designer](../email/setup/list-growth-designer/SKILL.md) owns the acquisition *strategy* + the compliant opt-in capture-flow *spec*; the signup form / popup *UX* is a landing/CRO job ([landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)), the *confirmation* flow is [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), the opt-in *record* is [consent-registry](../protocol/consent-registry/SKILL.md), and referral growth-loop *economics* are [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md).

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
