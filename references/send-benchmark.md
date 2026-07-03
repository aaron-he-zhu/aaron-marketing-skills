# SEND Benchmark — Email Marketing Evaluation Standard

The fifth framework in this library, alongside [CORE-EEAT](core-eeat-benchmark.md) (content quality), [CITE](cite-domain-rating.md) (domain authority), [C³](c3-benchmark.md) (influencer), and [ROAS](roas-benchmark.md) (paid ads). SEND scores an **email marketing program** — named for the verb the whole channel turns on — across four goal-weighted levers whose initials spell the name. It is deliberately **use-case-agnostic**: the same four dimensions score B2C lifecycle/ecommerce, B2B cold outbound, and newsletter/creator programs; the *goal-weight column* encodes which one you are running.

**Keyless by design**: every input comes from the user's **own account, manually exported** — ESP campaign/flow export (opens/clicks/revenue), the DMARC aggregate (RUA) report, a seed-list/inbox-placement test, and the GA4/ecommerce export. Keyed ESP APIs (Klaviyo, Mailchimp, HubSpot, Customer.io) are an optional Tier-2/3 MCP convenience, **never a Tier-1 precondition**.

## The four dimensions (S · E · N · D)

| Letter | Dimension | What it measures |
|--------|-----------|------------------|
| **S** | **Sender-integrity / Deliverability** | Authentication (SPF/DKIM/DMARC/BIMI), domain/IP reputation, inbox placement vs spam, bounce & spam-complaint rates, list hygiene, **+ list consent integrity** (vs consent-registry) |
| **E** | **Engagement** | Open / click / CTOR vs benchmark, subject-line + preheader quality, personalization, send-time & frequency fit, engagement-decay & sunset hygiene |
| **N** | **Nurture / Lifecycle** | Automation-flow design (welcome, abandoned-cart, post-purchase, win-back), trigger timing & cadence, segmentation relevance, goal progression, **+ unsubscribe / preference-center integrity** |
| **D** | **Direct-response / Conversion** | Revenue-per-send & per-recipient, conversion vs target, offer & CTA strength, email↔landing message-match, **+ claim & disclosure compliance** (vs the claims ledger) |

Mnemonic for the levers: **will it land (S) → will they open it (E) → does the program sustain them (N) → what comes back (D)**. The same four letters also frame the lifecycle as the **SEND loop**: Setup → Engage → Nurture → Deliver — the phase directories under `email/`.

## Scoring chassis

| | |
|---|---|
| Per sub-item | Pass = 10 · Partial = 5 · Fail = 0 |
| Dimension score | mean of sub-items × 10 → 0–100 |
| Rollup | **arithmetic goal-weighted mean** (same chassis as CITE / ROAS), floor-rounded — **not** C³'s geometric CVI |
| Rating bands | 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor |
| Veto-cap | delegated to [auditor-runbook.md](auditor-runbook.md) §2 — single veto caps the weighted overall at `min(raw, 60)`; 2+ veto fails → `status: BLOCKED` |

**Email Quality Score (EQS, 0–100)** = `floor(weighted({S, E, N, D}, goal-weights))`. ⚠ The EQS (a 0–100 quality score) is **not** any single email KPI (open rate, inbox-placement %, revenue/recipient); those KPIs are *inputs* to the dimensions.

### Sub-items (Pass / Partial / Fail each)

- **S** — SPF + DKIM + DMARC aligned & passing · sending-domain/IP reputation acceptable · inbox-placement ≥ threshold (vs spam/promotions) · hard-bounce rate < benchmark · spam-complaint rate < 0.1% · list acquired with recorded consent.
- **E** — open rate vs benchmark · click / CTOR vs benchmark · subject-line + preheader quality · send-time & frequency appropriate · engagement-decay managed (a re-engagement / sunset path exists).
- **N** — core lifecycle flows present (welcome, cart, post-purchase, win-back) · trigger timing & cadence sound · segmentation relevance · goal-progression logic · preference-center / frequency options offered.
- **D** — revenue / conversion vs target · offer clarity & CTA strength · email → landing message-match · urgency / social-proof used honestly · claims substantiated & policy-compliant.

### Goal-weight columns (each sums to 1.0)

| Goal | S | E | N | D |
|------|---|---|---|---|
| **Promotional / DR** | 0.20 | 0.20 | 0.15 | 0.45 |
| **Retention / Newsletter** | 0.20 | 0.35 | 0.30 | 0.15 |
| **Cold outbound / Acquisition** | 0.45 | 0.25 | 0.15 | 0.15 |

- Promotional weights: `EQS_promo = S×0.20 + E×0.20 + N×0.15 + D×0.45`
- Retention weights: `EQS_reten = S×0.20 + E×0.35 + N×0.30 + D×0.15`
- Cold-outbound weights: `EQS_cold = S×0.45 + E×0.25 + N×0.15 + D×0.15`

*Rationale:* a promotional blast lives or dies on conversion (D heaviest). Retention/newsletter is an engagement-and-lifecycle game (E + N = 0.65). Cold outbound is deliverability-first — if you land in spam, nothing downstream matters (S heaviest).

### Worked examples (golden-math fixture)

Kept here so `scripts/golden-auditor-math.py` can assert the arithmetic deterministically. Input vector `S=80 E=75 N=70 D=78`:

- **Promotional / DR goal** → 16 + 15 + 10.5 + 35.1 = `floor(76.6) = 76`.
- **Retention / Newsletter goal** (same vector) → 16 + 26.25 + 21 + 11.7 = `floor(74.95) = 74`. (Weighting toward Engagement + Nurture *lowers* a retention read on a conversion-tilted account — the weights encode the goal.)
- **Cold outbound / Acquisition goal** (same vector) → 36 + 18.75 + 10.5 + 11.7 = `floor(76.95) = 76`.
- **Veto-capped** — if S1 (authentication broken) fails on the Promotional example, the weighted overall is capped: `min(76, 60) = 60`, `cap_applied: true`.

## Veto items (red lines — stable IDs, distributed S:2 / N:1 / D:1)

| ID | Dimension | Trigger |
|----|-----------|---------|
| **S1** | Sender-integrity | Email authentication broken / unverifiable — SPF, DKIM, or DMARC failing or unaligned. *No DMARC record at all* = veto. A young program at **DMARC `p=none` but SPF/DKIM aligned and passing** = Partial/flag, **not** an auto-veto (mirrors ROAS's iOS-ATT modeled-data carve-out). |
| **S2** | Sender-integrity | List consent integrity — purchased / scraped / non-opt-in list with no lawful basis on record (checked against consent-registry). *No consent record on file* = **NEEDS_INPUT**, not pass-by-default. |
| **N1** | Nurture | Unsubscribe / opt-out broken or absent — a functioning opt-out not honored (CAN-SPAM / GDPR / CASL red line), or the one-click `List-Unsubscribe` header missing for Gmail/Yahoo bulk senders (RFC 8058 — a mailbox-provider requirement, not a statute). Checked against consent-registry's suppression/opt-out history. |
| **D1** | Direct-response | Claim integrity — false / unsubstantiated claim or missing required disclosure (checked against `memory/claims/claims-ledger.md`, same red line as ROAS O1). |

**Over-frequency / list fatigue** (sending past the point of engagement decay) is a high-severity **guardrail/flag under E**, *not* a veto — it wastes reputation and suppresses future engagement, but it does not by itself make the EQS untrustworthy (mirrors ROAS's premature-scaling guardrail under S).

## Data contract (keyless export columns)

| Need | Source export (own data) |
|------|--------------------------|
| E / opens / clicks / CTOR / send-time | ESP campaign report (own data) |
| N / flow performance / cadence | ESP flow/automation export |
| S / bounce & complaint / reputation | ESP deliverability report + sending-domain reputation (Postmaster/SNDS) |
| S1 (authentication) | **DMARC aggregate (RUA) report** + a DNS check of SPF/DKIM/DMARC/BIMI records (else NEEDS_INPUT) |
| S / inbox placement | seed-list / inbox-placement test (else NEEDS_INPUT) |
| S2 (consent) | consent record — opt-in timestamp + lawful basis from consent-registry (`memory/consent/`); **no record = NEEDS_INPUT** |
| N1 (unsubscribe integrity) | list-unsubscribe / one-click opt-out present & functional (ESP send config + message headers), **and** opt-outs honored — checked against the suppression / opt-out history in consent-registry (`memory/consent/`) |
| D (revenue / conversion) | GA4 / ecommerce export (own data) — order-ID truth set, **not** the ESP's self-reported attributed revenue |
| D1 (claim integrity) | approved wording + required disclosures from `memory/claims/claims-ledger.md` |

Reuse the existing `~~web analytics` (GA4) and `~~ecommerce` connector categories plus the new `~~email platform` (ESP, own-data manual export) — see [CONNECTORS.md](../CONNECTORS.md). Do **not** invent a `~~deliverability` category; SPF/DKIM/DMARC come from DNS + the DMARC RUA report, both keyless.

## Naming disambiguation

SEND's **S** (Sender-integrity) collides textually with ROAS's **S** (Spend-efficiency), and its **D** (Direct-response) with the ROAS/CITE letter pools. Each framework's letters and veto IDs are independent — SEND's `S1/S2/N1/D1` have no relationship to ROAS's `R1/R2/O1/O2/A1` or the S-guardrail. In any shared document (e.g. [auditor-runbook.md](auditor-runbook.md) §2/§5) always qualify the letter with the framework name (`SEND-S` vs `ROAS-S`). The runbook lists SEND vetoes under an Email sub-heading.

## Where it is used

The email skills apply SEND across the **SEND loop** — Setup → Engage → Nurture → Deliver (directories under `email/<phase>/`). Only [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) computes the goal-weighted EQS and runs the four vetoes; every other skill operates on a single lever and hands off.

- **Setup (S/E)** — [deliverability-qa](../email/setup/deliverability-qa/SKILL.md) scores **S** (auth, reputation, inbox-placement, spam-content, list hygiene — the S1 pre-flight); [list-segment-builder](../email/setup/list-segment-builder/SKILL.md) turns the user's own list/CRM/GA4 export into behavioral + lifecycle-stage segments and suppression rules (**E** targeting); [list-growth-designer](../email/setup/list-growth-designer/SKILL.md) plans compliant acquisition + the opt-in capture-flow spec (the upstream of `S2`, feeding `N` lifecycle entry). Consent/suppression facts come from [consent-registry](../protocol/consent-registry/SKILL.md).
- **Engage (E/D)** — [email-creative-builder](../email/engage/email-creative-builder/SKILL.md) produces the pre-click **E/D** unit (subject, preheader, body, CTA; message-matched to the landing page, claims-ledger-aware). Reuse: [audience-mapper](../discover/audience-mapper/SKILL.md) for persona/lifecycle-stage definition.
- **Nurture (N/D)** — [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md) designs lifecycle/automation flows + frequency governance (**N**); [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md) plans paid-sub / sponsorship / referral economics (**D** for owned-audience programs). Reuse: [landing-optimizer](../measure/landing-optimizer/SKILL.md) for the post-click page.
- **Deliver (S·E·N·D gate)** — [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) is the auditor-class gate: it scores EQS, enforces S1/S2/N1/D1, and emits the [auditor-runbook](auditor-runbook.md) handoff schema to `memory/audits/email/`. [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md) owns A/B / multivariate + send-time / hold-out design and the significance read (promote/kill). Reuse: [roi-calculator](../measure/roi-calculator/SKILL.md) (revenue-per-send / list-value), [report-generator](../measure/report-generator/SKILL.md), [performance-analyzer](../measure/performance-analyzer/SKILL.md).

> **Provisional**: SEND is a new framework. Treat its bands as provisional until calibrated against ~30 real manually-exported program audits in `memory/audits/email/`, per the runbook's calibration discipline.
