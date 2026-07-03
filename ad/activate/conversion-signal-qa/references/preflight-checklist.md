# Tracking Pre-Flight Checklist

Run before launching or scaling paid campaigns. Mark each item **pass / fail / needs-input** from the user's own GA4 exports and one manual test conversion. Never pass-by-default — a missing export makes the item **needs-input**, not pass. This checklist BUILDS/FIXES the signal; it does not score the ROAS `R1`/`R2` vetoes (that is [ad-account-auditor](../../ad-account-auditor/SKILL.md)).

## 1. Conversion-event firing

| Item | Pass when | Fail / needs-input |
|------|-----------|--------------------|
| Test conversion recorded | A manually-run test conversion appears in the GA4 Conversions export with correct event name | No test conversion run = **needs-input**; run but absent = **fail** |
| One canonical event per action | Each money action (purchase/lead/signup) maps to exactly one conversion event | Multiple events for the same action, or one event reused for several actions |
| Value + currency present | Purchase events carry a numeric value and a single currency | Missing value, mixed currencies, or hard-coded test value in production |
| Dedup parameter present | Each conversion carries a stable order/transaction ID | No ID to dedup on across platforms |

## 2. UTM hygiene

| Item | Pass when | Fail / needs-input |
|------|-----------|--------------------|
| All paid links tagged | Every paid landing URL carries source/medium/campaign | Untagged links land as `(direct)` or `referral` in Traffic-acquisition |
| Consistent casing/values | source/medium values match the spec exactly (lowercase, no synonyms) | `Google` vs `google`, `cpc` vs `ppc`, free-text campaign names |
| Auto-tagging vs manual not colliding | Platform auto-tagging (e.g. gclid) and manual UTMs don't overwrite each other | Both present and fighting, splitting one source into two rows |
| No PII in UTMs | UTM values contain no emails, names, or order data | PII embedded in campaign/content params |

## 3. Cross-platform dedup

> Pre-flight **gates** only — confirm the rule and routing *exist*. The actual order-ID matching, de-dup, and inflation math are the standing job of [attribution-reconciler](../../../scale/attribution-reconciler/SKILL.md).

| Item | Pass when | Fail / needs-input |
|------|-----------|--------------------|
| Single source of truth named | GA4/ecommerce order IDs are the truth set, not each platform's self-reported count | Platform counts trusted directly |
| Dedup method defined | A method to reconcile platform claims against the truth set is stated, owned by attribution-reconciler | No plan for resolving Meta/Google overlap |
| Overlap flagged & routed | Any obvious Meta+Google double-count is flagged and routed to attribution-reconciler | Overlap ignored (or quantified here instead of routed) |

## 4. Attribution-window alignment

| Item | Pass when | Fail / needs-input |
|------|-----------|--------------------|
| Windows stated & aligned | Each platform's click/view window is stated and a common comparison basis is chosen (the actual re-scoping runs in attribution-reconciler) | Windows unknown, or compared 7-day-click to 1-day-view as if equal |
| Currency/timezone aligned | Exports normalized to one currency and timezone before matching | Mixed timezones shifting conversions across days |

## 5. Offline + iOS-ATT modeled gaps (flags, not fails)

| Item | Flag when |
|------|-----------|
| Offline import gap | Offline/CRM conversions exist but aren't imported back; report the gap |
| iOS-ATT modeled share | Part of conversions are modeled/partial from iOS-ATT; flag the share. **Modeled data is a flag, not a fail** — it fires on nearly every modern account. Only *no verifiable data at all* is a fail. |

## Launch-readiness rule

State plainly: **launch-ready** (no fails; flags acknowledged) or **fix first** (list each fail/needs-input). Then hand to the auditor to score `R1`/`R2`.
