# Spam-Trigger Checklist (subject + preheader, pre-test)

Keyless heuristic patterns `subject-line-lab` flags on a subject line and its preheader **before** a test. These are pattern flags labeled **Estimated** — a clean pass here is *not* an inbox-placement guarantee. The full spam-content + SPF/DKIM/DMARC scan under SEND-**S** is [deliverability-qa](../../../setup/deliverability-qa/SKILL.md); the goal-weighted EQS and the S1/S2/N1/D1 vetoes are [email-quality-auditor](../../../deliver/email-quality-auditor/SKILL.md). This bench only pre-flags subject-level patterns.

## Pattern flags (each is a rank-down or a cut, stated out loud)

| Pattern | Flag when | Why it hurts |
|---|---|---|
| **ALL-CAPS run** | 3+ consecutive all-caps words, or a fully-caps subject | reads as shouting; classic spam signal |
| **Exclamation stacking** | `!!!`, or 2+ `!` in one subject | high spam-word correlation, low trust |
| **Deceptive prefix** | `RE:` / `FWD:` with no prior thread | fakes familiarity; a CAN-SPAM deception risk (downstream N1/D1) |
| **False scarcity** | "only 2 left", "expires in 1 hour" with no substantiated basis | unsubstantiated urgency → a D1 claim risk the auditor vetoes |
| **Spam-word density** | 2+ of: free, guaranteed, act now, risk-free, cash, winner, congratulations, 100%, click here | filter keyword clustering |
| **Symbol stacking** | multiple `$`, `%`, or `★`/`✅` glyphs used as decoration | promotional-tab / spam-folder signal |
| **Misleading personalization** | an unresolved `{token}` or a personalization claim the data cannot fill | renders broken; erodes trust |

## Emoji rule (scored separately as its own heuristic)

- **> 1 emoji** → flag (dilutes; risks tofu/□ render on some clients).
- **Any emoji in cold-outbound (B2B) mode** → flag.
- **One on-brand emoji in promo/newsletter** → pass with a note.

## What this checklist does NOT do

- No mailbox-provider filter verdict (Gmail/Outlook scoring is opaque) — heuristic only.
- No authentication check (SPF/DKIM/DMARC) — that is SEND-S, [deliverability-qa](../../../setup/deliverability-qa/SKILL.md).
- No body-copy spam scan — this covers subject + preheader only; the body is [email-creative-builder](../../email-creative-builder/SKILL.md), gated by [email-quality-auditor](../../../deliver/email-quality-auditor/SKILL.md).
- No claim substantiation — a flagged false-scarcity or superlative gets `[needs source]`; [offer-claims-registry](../../../../protocol/offer-claims-registry/SKILL.md) resolves it.
