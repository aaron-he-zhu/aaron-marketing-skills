# Claims Ledger Schema

Authoritative field definitions and file templates for `memory/claims/`. `offer-claims-registry` is the sole writer of `claims-ledger.md` and `offers.md`; every consumer (`ad-account-auditor`, `content-reviewer`, `ad-creative-builder`, `brief-generator`, `landing-optimizer`, `content-writer`, `page-play-builder`) reads these fields as-is. Do not rename or omit fields.

## Provenance labels

One label per claim row. The label states what evidence is on file — it is never a verdict.

| Label | Meaning | Who can set it |
|-------|---------|----------------|
| `verified-document` | The user named a specific substantiation document (study, test report, certification, warranty terms, own customer data) with a date | Only the user, by naming the document |
| `user-attested` | The user asserts the claim is true but has named no document | Registry, from user statements |
| `none-on-file` | Claim is registered but no evidence was provided | Registry default for unresolved `[needs source]` flags |
| `expired` | Evidence or the underlying offer has passed its review/expiry date | Registry, on expiry sweep |

Rules: never upgrade a label without new user input; downgrades to `expired` happen automatically on sweep. `none-on-file` is a factual state, not a failure — converting it into an O1/T2 failure is the gates' job.

## `memory/claims/claims-ledger.md` template

```markdown
---
type: claims
tier: WARM
updated: YYYY-MM-DD
---

# Claims Ledger

| # | Claim (exact text) | Evidence source + date | Provenance | Approved wording variants | Claim-level disclaimers / policy flags | Used in | Review/expiry |
|---|--------------------|------------------------|------------|---------------------------|----------------------------------------|---------|---------------|
| C-001 | "Cuts reporting time by 40%" | Internal timing study, 2026-03 (User-provided) | user-attested | "save 40% of reporting time"; "40% faster reports" | none / — | ads, landing /pricing | 2026-09-01 |
| C-002 | "Earn up to $500/mo" | — | none-on-file | — | earnings disclaimer required; policy flag: earnings | creator briefs | 2026-07-15 |
```

Field notes:

- **Claim (exact text)** — verbatim, in quotes. The dedupe key is the meaning, not the string: rewordings join the variants list of the existing row.
- **Evidence source + date** — recorded exactly as the user gave it, labeled Measured / User-provided / Estimated per the skill contract. Never invented.
- **Approved wording variants** — the only phrasings builders may pull. `ad-creative-builder` and `brief-generator` copy from this column, never paraphrase beyond it.
- **Claim-level disclaimers / policy flags** — disclaimers tied to this claim ("results not typical", finance/health text) plus sensitivity flags (health, finance, earnings, before/after). Sponsorship-disclosure format (#ad, "Paid partnership") is NOT recorded here — it belongs to briefs (T1).
- **Used in** — ads / landing pages / creator briefs / comparison pages, with URLs or asset names when known.
- **Review/expiry** — evidence age limit, offer end date, or default 6-month review.

## `memory/claims/offers.md` template

```markdown
---
type: claims
tier: WARM
updated: YYYY-MM-DD
---

# Live Offers

| # | Offer terms | Promo code | Start | End | Landing URL | Status | Linked claims |
|---|-------------|-----------|-------|-----|-------------|--------|---------------|
| O-001 | 50% off first 3 months, annual plans | SAVE50 | 2026-07-01 | 2026-07-31 | /promo/summer | live | C-003 |
```

Status values: `upcoming` / `live` / `ended`. Any ad or page claim that depends on an offer (price, discount, "free shipping") links to its offer row; when the offer flips to `ended`, the linked claims go into the expiry sweep.

## `memory/claims/candidates.md` (written by other skills)

The only `memory/claims/` file other skills may write. Exact mirror of the `memory/entities/candidates.md` pattern — when 3+ candidates accumulate, recommend `offer-claims-registry`.

```markdown
- [ ] "Rated #1 by TechRadar" — from: ad-creative-builder [needs source], 2026-07-02, asset: RSA draft v3
- [ ] "Ships in 24h" — from: page-play-builder, 2026-07-01, page: /vs/acme
```

The registry consumes candidates top-down, registers or merges each, and deletes processed lines.

## Frontmatter rule

All three files carry ordinary WARM frontmatter (`type: claims`, `tier: WARM`) — never `class: auditor-output`. The PostToolUse Artifact Gate validates only `memory/audits/`; registry files must not imitate auditor artifacts.

## Consumer query patterns

- **Gate check** (`ad-account-auditor` O1/O2, `content-reviewer` T2): look up the exact claim; absent row or provenance `none-on-file`/`expired` is the gate's evidence — the ledger itself renders no verdict.
- **Builder pull** (`ad-creative-builder`, `brief-generator`, `content-writer`, `page-play-builder`): fetch approved wording variants + required disclaimers for a claim; unresolved `[needs source]` flags route to `candidates.md`.
- **Message match** (`landing-optimizer`): compare page copy against registered claims and the offers table (code, terms, dates, URL).
