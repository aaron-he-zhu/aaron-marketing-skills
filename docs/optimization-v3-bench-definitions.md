# v3 benchmark definition reconciliation

Source baseline: `cac58547bc84ed2af865b68b90c5cfbb79b63978` (bundle 20.1.0).

The removed catalog `item_definitions` contained STAR 40 + ROAS 20 + SEND 20 = **80** manually repeated criteria. All 80 were compared before deletion. **63** differ only in case/final punctuation (STAR 40, ROAS 11, SEND 12); **17** have wording differences (ROAS 9, SEND 8). These are not 40 demonstrated semantic conflicts. The table below records every wording difference and its disposition. The delimited Markdown tables are now the sole authored criterion source; legacy optional schema/reader support and every `item_policies` entry remain.

| Item | Removed catalog wording | Previous Markdown wording | Disposition |
|---|---|---|---|
| ROAS-R1 | conversion instrumentation verified against an own-data truth set | Conversion instrumentation is verified against an own-data truth set. | Equivalent wording/grammar; existing Markdown preserves the obligation. |
| ROAS-R2 | cross-platform attribution deduplicated and windows/currency normalized | Cross-platform attribution is deduplicated; windows and currency are normalized. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| ROAS-R3 | incremental contribution or profit measured against the declared target/control | Incremental contribution or profit is measured against the declared target/control. | Equivalent wording/grammar; existing Markdown preserves the obligation. |
| ROAS-O3 | offer economics, eligibility, terms, and availability are explicit | Economics, eligibility, terms, and availability are explicit. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| ROAS-O5 | creative hook, format, accessibility, and fatigue state fit the placement | Hook, format, accessibility, and fatigue state fit the placement. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| ROAS-A1 | brand and placement safety verified from the placement evidence | Brand and placement safety are verified from placement evidence. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| ROAS-A4 | campaign/account structure supports the declared objective without avoidable overlap | Account structure supports the objective without avoidable overlap. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| ROAS-S1 | budget pacing stays within the declared plan and constraints | Budget pacing remains within the declared plan and constraints. | Equivalent wording/grammar; existing Markdown preserves the obligation. |
| ROAS-S3 | marginal CPC/CPM/CTR/CVR efficiency is compared on a normalized window | Marginal CPC/CPM/CTR/CVR efficiency uses a normalized window. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| SEND-S1 | SPF/DKIM/DMARC alignment verified from DNS and aggregate evidence | SPF/DKIM/DMARC alignment is verified from DNS and aggregate evidence. | Equivalent wording/grammar; existing Markdown preserves the obligation. |
| SEND-S3 | inbox placement is measured on a declared provider/seed panel | Inbox placement is measured on a declared provider or seed panel. | Equivalent wording/grammar; existing Markdown preserves the obligation. |
| SEND-E4 | send timing and frequency fit preference and capacity | Timing and frequency fit preferences and operating capacity. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| SEND-E5 | engagement decay and reactivation/sunset logic are measured | Engagement decay and reactivation/sunset behavior are measured. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| SEND-N3 | applicable lifecycle journeys exist for the declared program type | Journeys applicable to the declared program type exist and work. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| SEND-N5 | preference and frequency controls are available where applicable | Preference/frequency controls exist where recurring sends make them applicable. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| SEND-D2 | the declared outcome truth set is measured: revenue, pipeline, subscription, sponsorship, or another named outcome | The declared outcome truth set is measured. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |
| SEND-D3 | offer and CTA are clear for the declared program | Offer and CTA are clear for this program. | Restore the catalog scope explicitly in the Markdown criterion; grammar clarified without dropping either obligation. |

## Intentional human-anchor corrections

- CORE-EEAT A05: unobserved brand evidence becomes Unknown; verified absence in a declared adequate observation scope may Fail.
- CORE-EEAT C03: the exact target query is excluded from the variant count, removing the overlapping one-query Partial/Fail boundary.
- CORE-EEAT R01: exactly one meaningful precise data point is Partial; repeated numbers and irrelevant numeric padding do not count.
- CORE-EEAT R02: both citation density and source-type diversity must meet the same band; the lower band governs.
- CORE-EEAT O04: parallel-information organization governs; a lists-per-word quota is retired.
- CITE C01: freeze and cite the cohort-specific criterion before scoring; 500/50 are historical examples, not a universal verdict.

These are human-rubric interpretation changes, recorded as **2026-10-27-a** in each benchmark. Numerical score policies, all 320 qualified identities, 37 profiles, applicability and veto identity remain unchanged. Historical artifacts retain their original source digests. New boundary cases are authored, reviewable regression expectations, not results of a dual-blind study or business outcome calibration.

## Evidence and review work

Each benchmark describes its own reusable evidence batch and change-sensitive review path. Reusing a source does not count as independent corroboration; each item keeps its own judgment. Complete final observations still pass the original deterministic scorer and 100% applicable coverage. Collection counts, question counts, rater disagreement and business outcomes have **not been measured** in this implementation.

## First boundary batch and verification

The first batch covers **20** qualified items, preserving each item's separate construct:

| Framework | Items | Boundary focus |
|---|---|---|
| CORE-EEAT | A05, C03, R01, R02, O04 | Unknown versus absence; distinct secondary intents; one data point; density/diversity conjunction; organization rather than list quotas |
| CITE | C01 | Precommitted cohort criteria, including a small-domain Pass and unanchored large-domain Unknown |
| STAR | S2, S6, A3 | Verified fraud versus missing analytics; native creator integration rather than generic ad copy |
| ROAS | R3, R4, R5, A5, S4 | Incrementality versus attribution; own-data constraints; lag/uncertainty; saturation versus creative decay |
| SEND | E2, N1, D2 | MPP/proxy/N/A; effective suppression; different program outcome truth sets |
| RAMP | P6 | Collection, owned disposition/follow-up, verified abandonment and unavailable records |
| ECHO | C3 | Native adaptation versus remediable mismatch, blocking incompatibility and unverified folklore |
| TALE | A9 | Specificity versus generic messaging; truth/substantiation remain separate controls |

`tests/fixtures/benchmark-boundary-cases.json` fixes **70** structured examples: 21 Pass, 12 Partial, 19 Fail, 17 Unknown and 1 catalog-authorized N/A. They are expected item judgments for review, not a new production classifier. `test_benchmark_anchors.py` checks the documented facts/states against those fixed examples, independently computes the count/density boundary oracles, and sends all 70 resulting observations through the original scorer to check coverage, Unknown/N/A and veto behavior. Its negative controls deliberately change facts or restore Unknown→Fail and must be rejected. It cannot establish that a model will classify arbitrary unseen evidence correctly.

Of the 320 compiled criteria, **31** change text: the 20 boundary items above plus 11 other ROAS/SEND scope/wording reconciliations. The other **289** criterion strings match the baseline exactly; converting RAMP/ECHO/TALE paragraphs to delimited tables preserves those original item identities and text except the three explicitly revised P6/C3/A9 anchors. The detailed-note revision and each later runtime source digest identify the new interpretation; historical observations are not rewritten.

Focused verification performed on the working revision: `tests.test_rubric_score`, `tests.test_benchmark_anchors`, `tests.test_v3_compatibility` and `tests.test_auditor_runtime` passed (46 tests at this handoff), and the independent golden behavior guard passed all **37** profiles. The frozen v3 compatibility fixture was not modified. Final release regeneration/source checks remain part of the parent implementation's acceptance, rather than being inferred from these focused tests.
