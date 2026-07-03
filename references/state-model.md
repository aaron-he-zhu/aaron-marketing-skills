# State Model

Plan C standardizes where reusable project state belongs. All state follows a three-tier temperature model with automatic lifecycle management.

## Temperature Tiers

### HOT — `memory/hot-cache.md`

- Capacity: 80 lines max
- Loaded automatically by SessionStart hook every session
- Content: project goals, hero keywords (max 10), primary competitors (max 5), active veto items, unresolved open loops from `memory/open-loops.md`
- Promotion: **explicit** — the user or a skill pins a finding to HOT ("promote X" / auto-promote of veto items and blockers). No hook counts references, so promotion is never frequency-based.
- Demotion: when the HOT entry's `last_updated` date is older than 30 days — move it out of hot-cache.md; the content remains in its WARM file

### WARM — `memory/<category>/<skill>/`

- Capacity: 200 lines per file
- Loaded on demand when a skill matches the topic
- Paths follow the Durable State definitions below
- Promotion: when the user/skill decides a conclusion is durable, extract it (max 3 lines) to HOT — an explicit action, not a reference counter
- Demotion: when the file's `last_updated` date is older than 90 days — move it to `memory/archive/` with date prefix `YYYY-MM-DD-`

### COLD — `memory/archive/`

- No capacity limit
- Queried only when `memory-management` is explicitly invoked
- Never auto-deleted, only archived
- Filename format: `YYYY-MM-DD-original-filename.md`

### Lifecycle Rules (observable only)

Nothing in the hooks records read/reference counts, so the lifecycle uses only what an agent can
check on disk: an **explicit pin** or a **`last_updated` date**.

```
explicit "promote X" / pin           → WARM promotes to HOT (extract ≤3 lines)
HOT entry last_updated > 30 days      → HOT demotes to WARM
WARM file last_updated > 90 days      → WARM demotes to COLD (archive with YYYY-MM-DD- prefix)
```

### Dual Truncation Rule

HOT tier is limited to 80 lines AND 25KB (whichever triggers first). A cache within both limits is injected in full; the SessionStart hook applies the 80-line cap at a newline boundary and the 25KB cap at the byte limit, so an over-limit cache may be cut mid-line. If exceeded after Claude Write/Edit, the PostToolUse hook warns the user.

### Staleness Protocol

| Age | Treatment |
|-----|-----------|
| ≤7 days | Current — use without caveat |
| 8–30 days | Point-in-time — verify against current state before asserting as fact |
| 31–90 days | Stale — surfaced for review when `memory-management` runs its staleness scan (by `last_updated` date) |
| >90 days | Archive candidate — recommend archival via memory-management |

## Memory File Frontmatter

Every file in `memory/` SHOULD include YAML frontmatter. Two shapes are valid:

**WARM files** — subject matter state (audits, research, decisions, entities, etc.):

```yaml
---
name: campaign-q2-seo
description: Q2 SEO campaign targeting 50 keywords across 3 verticals
type: project
last_updated: 2026-06-10
---
```

Valid `type` values: `project`, `reference`, `decision`, `entity`, `glossary`, `open-loops`, `entity-candidates`

The `description` field enables future semantic search across memory files. **`last_updated`** (a date) is what the demotion/archival rules and `memory-management`'s staleness scan read — write it whenever you create or modify a WARM file. Absent it, fall back to the file's mtime.

**HOT file** (`memory/hot-cache.md`) — session scope declaration:

```yaml
---
tier: hot
project: acme-q2     # null for global scope; set to a project slug to scope memory reads
---
```

When `project` is non-null, the SessionStart hook and `memory-management` preferentially load memory scoped to that project. Switching projects between sessions = swap this field.

## Durable State

### `memory/decisions.md`

Store:

- major strategic choices
- accepted tradeoffs
- abandoned directions worth remembering

### `memory/open-loops.md`

Store:

- unresolved blockers
- missing evidence
- follow-up tasks
- risks that should not be forgotten

### `memory/glossary.md`

Store:

- project terminology
- internal acronyms
- shorthand labels
- segment definitions
- historical naming context

### `memory/entities/`

Store:

- canonical names
- sameAs and profile links
- entity type
- topic associations
- disambiguation notes
- knowledge-base status

Only `entity-optimizer` should write canonical records here. Other skills should keep raw entity leads in their own category notes until canonicalization is needed.

### `memory/creators/`

Store (one file per creator, `<handle-slug>.md`, slug = canonical primary-platform handle):

- verified cross-platform handles with confirmed/unconfirmed status
- audience stats with as-of dates and Measured/User-provided/Estimated provenance
- rate card and negotiation history
- past-campaign performance baselines
- dated disclosure/FTC compliance events citing content-reviewer verdict IDs
- exclusivity windows, contract status, and the confirmed contact path

Only `creator-registry` writes canonical records here. Other skills submit updates to `memory/creators/candidates.md` only.

**Lifecycle exemption**: canonical creator records are roster state, not dated run artifacts — no `YYYY-MM-DD` filename, and they are exempt from the 90-day WARM demotion (like `memory/entities/`). Demotion happens only when the user drops a creator from the roster, and `memory-management` remains the sole executor of that archival.

### `memory/claims/`

Store (standing ledger files, not per-run artifacts):

- `claims-ledger.md` — one row per marketing claim: claim text → substantiation evidence (source, date, provenance label) → approved wording + required disclosures → where used (ads / landing pages / briefs) → review/expiry date
- `offers.md` — live offers: terms, promo codes, dates, landing URLs
- `candidates.md` — intake from other skills (mirror of the entity/creator pattern)

Only `offer-claims-registry` writes canonical records here. Other skills submit updates to `memory/claims/candidates.md` only.

**Lifecycle exemption**: ledger files are standing state, not dated run artifacts — exempt from the 90-day WARM demotion (like `memory/entities/` and `memory/creators/`); rows retire via their review/expiry date, and `memory-management` remains the sole executor of archival.

### `memory/consent/`

Store (one record per subscriber/prospect subject — the email consent & suppression SSOT):

- subscription status and source
- opt-in timestamp + **lawful basis** (consent / legitimate-interest / contract) and double-opt-in proof
- append-only unsubscribe / bounce / spam-complaint history with dates
- suppression flags the S2 veto and N1 unsubscribe-honoring are judged against

Only `consent-registry` writes canonical records here. Other skills submit updates to `memory/consent/candidates.md` only.

**GDPR posture**: subscribers are natural persons — inherit `creator-registry`'s lawful-basis gate and data-minimization posture; store the minimum needed to prove consent and honor suppression, never raw personal data beyond that.

**Lifecycle exemption**: consent/suppression records are standing state, not dated run artifacts — exempt from the 90-day WARM demotion (like `memory/creators/` and `memory/claims/`); records retire on consent withdrawal / suppression, and `memory-management` remains the sole executor of archival.

### `memory/research/`

Common subfolders:

- `keywords/`
- `competitors/`
- `serp/`
- `content-gaps/`

Store:

- keyword opportunities
- competitor findings
- SERP notes
- content gap summaries

### `memory/content/`

Common subfolders:

- `briefs/`
- `calendar/`
- `published/`

Store:

- content briefs
- approved angles
- meta tag decisions
- schema notes
- refresh plans

### `memory/audits/`

Common subfolders:

- `content/` (content-quality-auditor — CORE-EEAT)
- `domain/` (domain-authority-auditor — CITE)
- `<skill>/` (other Optimize skills, per-skill — e.g. `technical-seo-checker/`, `site-structure-optimizer/`)
- `influencer/` (content-reviewer — C³ ART gate artifacts)
- `paid/` (ad-account-auditor — ROAS gate artifacts)
- `email/` (email-quality-auditor — SEND gate artifacts)

Store:

- audit summaries
- veto items
- prioritized fixes
- pass/fail gate decisions (all gated artifacts carry `class: auditor-output` + the cap schema per [auditor-runbook.md](auditor-runbook.md))

### `memory/monitoring/`

Common subfolders:

- `rank-history/`
- `reports/`
- `alerts/`
- `snapshots/`

Store:

- ranking deltas
- alert history
- backlink changes
- stakeholder reporting summaries
- dated supporting CSV or export files when helpful

### `memory/influencer/`

Per-skill subfolders, one per influencer-marketing (IMPACT) skill: `memory/influencer/<skill>/` (e.g. `audience-mapper/`, `fit-scorer/`, `roi-calculator/`). Scored on the [C³ framework](c3-benchmark.md).

Store:

- audience profiles, niche dossiers, trend reports (discover)
- creator shortlists, fit scores (ACE), competitor partner maps (discover)
- campaign plans, briefs, budget allocations (plan)
- outreach threads, content reviews (ART), contract drafts (activate)
- amplification plans, repurposed UGC, landing-page optimizations (activate)
- performance analyses, ROI/CVI calculations, reports (measure)

Same WARM lifecycle as the other categories: dated files `YYYY-MM-DD-<topic>.md`, demoted to `memory/archive/` after 90 days by `last_updated`. (content-reviewer's **gated** ART verdict is an auditor artifact and lives in `memory/audits/influencer/`, not here.)

### `memory/paid-ads/`

Per-skill subfolders, one per Paid Ads skill: `memory/paid-ads/<skill>/` (e.g. `campaign-architect/`, `ad-creative-builder/`, `paid-measurement-loop/`). Scored on the [ROAS framework](roas-benchmark.md).

Store:

- account/campaign structure plans, targeting + negative lists, cannibalization audits (research)
- ad-creative sets and angle matrices (orchestrate)
- ROAS/CPA readback snapshots vs control (scale)

Same WARM lifecycle (dated files, demoted to `memory/archive/` after 90 days). ad-account-auditor's **gated** RQS verdict is an auditor artifact and lives in `memory/audits/paid/`.

### `memory/email/`

Per-skill subfolders, one per email-marketing skill: `memory/email/<skill>/` (e.g. `deliverability-qa/`, `email-creative-builder/`, `email-sequence-designer/`). Scored on the [SEND framework](send-benchmark.md).

Store:

- deliverability pre-flight results (auth/reputation/inbox-placement), segment maps + suppression lists (setup)
- email creative sets, subject-line variants (engage)
- lifecycle-flow designs, cadence/frequency plans, newsletter monetization models (nurture)
- send-test designs and significance reads (deliver)

Same WARM lifecycle (dated files, demoted to `memory/archive/` after 90 days). email-quality-auditor's **gated** EQS verdict is an auditor artifact and lives in `memory/audits/email/`. Consent/suppression facts live in `memory/consent/` (consent-registry's SSOT), not here.

## Writing Guidance

When a skill describes state updates, it should:

- prefer summaries over raw dumps
- distinguish facts from assumptions
- note missing data explicitly
- avoid inventing data when tools are unavailable
- keep raw exports beside the dated summary they support

## Ownership

- `memory-management` is the sole executor of WARM → COLD archival operations
- `entity-optimizer` is the sole writer of canonical records in `memory/entities/<name>.md`
- Other skills write entity candidates to `memory/entities/candidates.md` only
- `creator-registry` is the sole writer of canonical records in `memory/creators/<handle-slug>.md`; other skills write to `memory/creators/candidates.md` only
- `offer-claims-registry` is the sole writer of canonical records in `memory/claims/`; other skills write to `memory/claims/candidates.md` only
- `consent-registry` is the sole writer of canonical records in `memory/consent/`; other skills write to `memory/consent/candidates.md` only
- `content-quality-auditor` owns publish-readiness state in `memory/audits/content/`
- `domain-authority-auditor` owns citation-trust state in `memory/audits/domain/`
- `content-reviewer` owns the C³ ART gate state in `memory/audits/influencer/`
- `ad-account-auditor` owns the ROAS gate state in `memory/audits/paid/`
- `email-quality-auditor` owns the SEND gate state in `memory/audits/email/`

See [skill-contract.md](skill-contract.md) for the full protocol-layer vs execution-layer behavior matrix.
