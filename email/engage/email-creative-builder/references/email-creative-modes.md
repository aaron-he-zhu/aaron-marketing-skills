# Email Creative Modes (SEND-E/D)

Three use-case pattern sets for `email-creative-builder`. Pick the mode that matches the program; the skill stays use-case-agnostic and the mode only changes the pattern, not the contract. All three end at the same **message-match map** so [email-quality-auditor](../../../deliver/email-quality-auditor/SKILL.md) can score the E/D unit and run the D1 claim veto.

## Mode A — Promotional / lifecycle (B2C)

- **Goal**: one action (buy, redeem, book). Single dominant CTA.
- **Structure**: hook → value/offer → proof (review, stat, guarantee) → CTA → urgency (honest deadline/stock only).
- **Offer**: pull terms + promo code + expiry from the live-offers table ([offer-claims-registry](../../../../protocol/offer-claims-registry/SKILL.md), `memory/claims/offers.md`) — never invent them.
- **Claims**: every product/benefit claim traces to an approved row in `memory/claims/claims-ledger.md`; unregistered → `[needs source]` → `memory/claims/candidates.md`.

## Mode B — Cold outbound (B2B)

- **Goal**: a reply, not a click. One low-friction ask (interest-check / soft CTA).
- **Structure**: relevance line (why them, now) → one concrete value point → light social proof → single soft ask. Keep it short; plain-text feel.
- **Personalization**: one genuine, verifiable personalization token per message; no fabricated "I saw you…" specifics.
- **Compliance**: physical mailing address + a functioning opt-out honored within 10 business days (CAN-SPAM); the one-click `List-Unsubscribe` header is a Gmail/Yahoo bulk-sender rule (RFC 8058), not a CAN-SPAM statute. Consent/lawful-basis per recipient from [consent-registry](../../../../protocol/consent-registry/SKILL.md). Spintax/variants must not degrade into misleading claims.

## Mode C — Newsletter / creator

- **Goal**: sustained engagement + (where relevant) monetization. CTA may be read/forward/refer, not buy.
- **Structure**: subject promise → lead → 1–3 sections → clearly-labeled sponsorship (if any) → forward/refer ask.
- **Sponsorship = ad**: any paid placement gets an explicit disclosure; the offer/claim still routes through the claims ledger (D1). Monetization economics belong to [newsletter-monetization-planner](../../../nurture/newsletter-monetization-planner/SKILL.md).

## Message-match map (all modes — required output)

For each CTA, record the row so the auditor can verify email↔landing consistency:

| Email element | Says | Landing page must show | Match? |
|---|---|---|---|
| Subject/hook | <promise> | <same promise above the fold> | ✓ / ✗ |
| Offer | <terms/code> | <identical terms/code> | ✓ / ✗ |
| CTA label | <verb + object> | <same next step> | ✓ / ✗ |

A mismatch is a message-match failure (SEND-`D` sub-item) — flag it; the post-click fix is [landing-optimizer](../../../../influencer/measure/landing-optimizer/SKILL.md).
