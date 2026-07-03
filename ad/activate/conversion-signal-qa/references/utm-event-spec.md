# UTM / Event Spec Builder

Fill these two templates for the account, then save them with the pre-flight report. The spec is the contract every paid link and conversion event must follow so the GA4 Traffic-acquisition and Conversions exports stay clean and dedupable.

## UTM naming convention

One canonical value per field. Lowercase, no spaces, no synonyms, no PII.

| Field | Rule | Example |
|-------|------|---------|
| `utm_source` | the platform, one fixed token | `google`, `meta`, `linkedin` |
| `utm_medium` | the paid channel type, fixed vocabulary | `cpc`, `paid_social`, `display` |
| `utm_campaign` | `{goal}_{audience}_{yyyymm}` | `dr_prospecting_202606` |
| `utm_content` | ad/creative variant id | `video_a`, `carousel_b` |
| `utm_term` | keyword/theme (search only) | `running_shoes` |

Rules:
- Pick **one** value per source/medium and never vary case (`google`/`cpc`, never `Google`/`PPC`).
- Don't let platform auto-tagging (gclid/fbclid) and manual UTMs overwrite each other — choose one scheme per platform and document it.
- Never embed emails, names, or order IDs in any UTM field.

## Conversion-event spec

One row per money action. Each action maps to exactly one event with a stable dedup ID.

| Money action | Event name | Value param | Currency | Dedup ID | Fires on |
|--------------|-----------|-------------|----------|----------|----------|
| Purchase | `purchase` | order_total | single currency | `transaction_id` | order confirmation |
| Lead | `generate_lead` | lead_value (or none) | — | `lead_id` | form thank-you |
| Signup | `sign_up` | — | — | `user_id` | account-created |

Rules:
- The **dedup ID** is the single source of truth for cross-platform reconciliation — GA4/ecommerce order IDs win over any platform's self-reported count.
- State the **attribution window** chosen per platform and normalize all exports to one window, currency, and timezone before matching.
- Confirm one **manual test conversion** flows end-to-end into the GA4 Conversions export before launch.
