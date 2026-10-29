# Benchmark boundary examples

These 70 frozen examples support reviewer calibration and regression testing.
Open only the relevant framework when a concrete boundary needs clarification.
The framework item anchors, applicability and evidence rules remain execution requirements; these examples do not add a new scoring engine, replace the scorer, or establish human reliability/business validity.

## CORE-EEAT

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| brand-unobserved | A05 | `{"adequate_observation":false}` | unknown |
| brand-observed-absent | A05 | `{"adequate_observation":true,"recognition_signal":"none"}` | fail |
| brand-scoped-demand | A05 | `{"adequate_observation":true,"recognition_signal":"branded-search-demand"}` | pass |
| query-exact-only | C03 | `{"artifact_observed":true,"primary_answered":true,"secondary_intents":0}` | fail |
| query-one-variant | C03 | `{"artifact_observed":true,"secondary_intents":1}` | partial |
| query-two-variants | C03 | `{"artifact_observed":true,"secondary_intents":2}` | partial |
| query-three-variants | C03 | `{"artifact_observed":true,"secondary_intents":3}` | pass |
| precision-none | R01 | `{"artifact_observed":true,"distinct_relevant_measurements":0}` | fail |
| precision-one-repeated | R01 | `{"artifact_observed":true,"distinct_relevant_measurements":1,"numeric_tokens":6}` | partial |
| precision-four | R01 | `{"artifact_observed":true,"distinct_relevant_measurements":4}` | partial |
| precision-five | R01 | `{"artifact_observed":true,"distinct_relevant_measurements":5}` | pass |
| citation-one-type | R02 | `{"claim_linked_citations":10,"source_types":1,"words":1000}` | fail |
| citation-two-types | R02 | `{"claim_linked_citations":2,"source_types":2,"words":1000}` | partial |
| citation-pass | R02 | `{"claim_linked_citations":3,"source_types":3,"words":1500}` | pass |
| citation-low-density | R02 | `{"claim_linked_citations":3,"source_types":3,"words":4000}` | fail |
| citation-count-unobserved | R02 | `{"claim_linked_citations":3,"source_types":3,"words":null}` | unknown |
| lists-organized | O04 | `{"artifact_observed":true,"parallel_items":"all-grouped"}` | pass |
| lists-mixed | O04 | `{"artifact_observed":true,"parallel_items":"some-buried"}` | partial |
| lists-runon | O04 | `{"artifact_observed":true,"parallel_items":"obscured-runon"}` | fail |
| lists-unneeded | O04 | `{"artifact_observed":true,"form":"appropriate-continuous-prose","parallel_items":"none"}` | pass |

## CITE

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| cohort-small-pass | C01 | `{"frozen_cohort":true,"partial_minimum":10,"pass_minimum":20,"referring_domains":30}` | pass |
| cohort-intermediate | C01 | `{"frozen_cohort":true,"partial_minimum":10,"pass_minimum":20,"referring_domains":15}` | partial |
| cohort-below-minimum | C01 | `{"frozen_cohort":true,"partial_minimum":10,"pass_minimum":20,"referring_domains":5}` | fail |
| cohort-large-unanchored | C01 | `{"frozen_cohort":false,"referring_domains":600}` | unknown |

## STAR

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| followers-audited-pass | S2 | `{"audit_verified":true,"cohort_minimum":90,"real_follower_rate":95}` | pass |
| followers-verified-fail | S2 | `{"audit_verified":true,"cohort_minimum":90,"real_follower_rate":85}` | fail |
| followers-missing | S2 | `{"audit_verified":false,"cohort_minimum":90,"real_follower_rate":null}` | unknown |
| engagement-verified-bought | S6 | `{"bought_engagement_verified":true}` | fail |
| engagement-rate-only | S6 | `{"authenticity_observation":false,"unusual_rate":true}` | unknown |
| engagement-authentic | S6 | `{"authenticity_observation":true,"bought_engagement_verified":false,"coordinated_activity":false}` | pass |
| integration-native | A3 | `{"asset_observed":true,"creator_reference_observed":true,"integration":"native-and-understandable"}` | pass |
| integration-awkward | A3 | `{"asset_observed":true,"creator_reference_observed":true,"integration":"awkward-but-connected"}` | partial |
| integration-disconnected | A3 | `{"asset_observed":true,"creator_reference_observed":true,"integration":"unrelated-bolted-on-copy"}` | fail |
| integration-unobserved | A3 | `{"asset_observed":false}` | unknown |

## ROAS

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| incremental-controlled | R3 | `{"declared_target_met":true,"design":"holdout","own_profit_observed":true}` | pass |
| incremental-platform-ratio | R3 | `{"design":"none","own_incrementality_observed":false,"platform_roas":12}` | unknown |
| incremental-limited-proxy | R3 | `{"design":"justified-labeled-proxy","limitations_declared":true,"own_outcomes_observed":true}` | partial |
| constraint-at-ceiling | R4 | `{"cac":20,"cac_ceiling":20,"own_outcomes_verified":true,"payback_ceiling":6,"payback_months":4}` | pass |
| constraint-breached | R4 | `{"cac":25,"cac_ceiling":20,"own_outcomes_verified":true,"payback_ceiling":6,"payback_months":4}` | fail |
| constraint-undefined | R4 | `{"cac":20,"cac_ceiling":null}` | unknown |
| marginal-immature | R5 | `{"average_roas":8,"declared_lag_complete":false}` | unknown |
| marginal-negative | R5 | `{"declared_lag_complete":true,"marginal_profit":"verified-negative","uncertainty":"target-excluded"}` | fail |
| marginal-uncertain | R5 | `{"declared_lag_complete":true,"marginal_profit":"estimated-positive","uncertainty":"target-straddled"}` | partial |
| saturation-frequency-only | A5 | `{"audience_reach_overlap_observed":false,"frequency":12}` | unknown |
| saturation-observed | A5 | `{"audience_reach_overlap_observed":true,"overlap":"above-declared-maximum","qualified_new_reach":"below-declared-minimum"}` | fail |
| saturation-within-bounds | A5 | `{"audience_reach_overlap_observed":true,"overlap":"within-declared-bounds","qualified_new_reach":"within-declared-bounds"}` | pass |
| fatigue-frequency-only | S4 | `{"creative_cohort_breakdown":false,"frequency":12}` | unknown |
| fatigue-stable | S4 | `{"audience_held_stable":true,"creative_cohort_breakdown":true,"creative_performance":"stable"}` | pass |
| fatigue-observed | S4 | `{"audience_held_stable":true,"creative_cohort_breakdown":true,"creative_performance":"verified-decline"}` | fail |

## SEND

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| opens-unused | E2 | `{"ctor_used":false,"opens_used":false,"reason":"Program uses verified clicks/downstream actions; no open-derived metric is assessed."}` | na |
| opens-unsegmented | E2 | `{"mpp_segmentation_observed":false,"opens_used":true}` | unknown |
| opens-proxy-honest | E2 | `{"mpp_segmentation_observed":true,"opens_used":true,"proxy_caveat":true}` | pass |
| opens-false-human-claim | E2 | `{"claim":"raw-opens-are-measured-human-engagement","mpp_preload_verified":true,"opens_used":true}` | fail |
| suppression-violated | N1 | `{"delivery_verified":true,"suppression_effective_before_send":true}` | fail |
| suppression-unobserved | N1 | `{"delivery_logs_observed":false}` | unknown |
| suppression-honored | N1 | `{"required_optout_tested":true,"subsequent_delivery":false,"suppression_effective_before_send":true}` | pass |
| newsletter-own-outcome | D2 | `{"program":"paid-newsletter","truth_set":"verified-subscriptions-and-net-revenue"}` | pass |
| outbound-opens-only | D2 | `{"program":"cold-outbound","truth_set":"provider-opens-only"}` | unknown |
| commerce-own-outcome | D2 | `{"program":"ecommerce","truth_set":"deduplicated-orders-and-contribution"}` | pass |

## RAMP

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| feedback-collected | P6 | `{"disposition_recorded":false,"feedback_observed":true}` | partial |
| feedback-closed | P6 | `{"feedback_observed":true,"owned_disposition":true,"reporter_followup_recorded":true}` | pass |
| feedback-abandoned | P6 | `{"abandonment_verified":true,"feedback_observed":true}` | fail |
| feedback-unobserved | P6 | `{"feedback_records_observed":false}` | unknown |

## ECHO

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| platform-native | C3 | `{"asset_observed":true,"execution":"native","requirements":"documented-or-observed"}` | pass |
| platform-remediable | C3 | `{"asset_observed":true,"execution":"remediable-format-mismatch","requirements":"documented-or-observed"}` | partial |
| platform-incompatible | C3 | `{"asset_observed":true,"execution":"verified-blocking-incompatibility","requirements":"documented"}` | fail |
| platform-folklore-only | C3 | `{"adaptation_observed":false,"requirements":"unverified-folklore-only"}` | unknown |

## TALE

These frozen factual examples make the revised boundaries reviewable. They are not a general machine classifier, a dual-blind reliability result, or business outcome evidence. Each state is an item judgment; the original scorer still owns coverage, vetoes and the final profile result.

| Case | Item | Observed facts (JSON) | Expected state |
|---|---|---|---|
| message-concrete | A9 | `{"audience":"named","canon_observed":true,"problem":"identifiable","value":"specific"}` | pass |
| message-generic | A9 | `{"audience":"indeterminate","canon_observed":true,"problem":"indeterminate","value":"empty-generic-claim"}` | fail |
| message-unobserved | A9 | `{"canon_observed":false}` | unknown |
