<!-- Generated routing projection; do not edit directly. -->
# Auto Routing Shard: Cross-discipline disambiguation

Boundary disambiguation only; load it when the goal genuinely spans disciplines. This projection contains 5 cases. Read the [routing boundary contract](../aaron-product-api-contract.md) before execution.

## Runtime routing records

Each record is generated from the authoritative eval case and contains only route selection, blocking-input, risk-gate, and must-not fields.

```json
- {"id":"cross-creator-whitelisting-001","target_skill":"content-amplifier","scenario_family":"whitelisting_disambiguation","risk_gates":["ftc_disclosure","claim_integrity","launch_readiness","external_side_effect"],"expected_route":"/aaron-marketing:influencer --phase activate (content-amplifier) -> /aaron-marketing:ad --phase activate (ad-account-auditor) -> stop for spend approval","blocking_inputs":["usage rights/contract","disclosure status","ad account","budget"],"must_not":["run creator content as ads without usage rights","skip the STAR gate because spend is paid-side"]}
- {"id":"cross-ads-landing-page-001","target_skill":"landing-optimizer","scenario_family":"post_click_disambiguation","risk_gates":["claim_substantiation","data_insufficient"],"expected_route":"/aaron-marketing:ad --phase orchestrate (landing-optimizer reuse)","blocking_inputs":["landing URL","ad creative/offer","conversion metric"],"must_not":["claim conversion lift without data","rewrite as SEO content when the goal is paid post-click"]}
- {"id":"cross-email-list-custom-audience-001","target_skill":"list-segment-builder","scenario_family":"email_to_paid_audience_disambiguation","risk_gates":["consent_lawful_basis","external_side_effect","data_insufficient"],"expected_route":"/aaron-marketing:email (consent-registry -> list-segment-builder) -> /aaron-marketing:ad --phase research (audience-segment-builder) -> stop for upload approval","blocking_inputs":["consent basis for data sharing","list export","target platform","match key"],"must_not":["share a non-consented list with an ad platform","skip consent because the destination is paid"]}
- {"id":"cross-launch-campaign-sense-001","target_skill":"email-creative-builder","scenario_family":"launch_word_sense","risk_gates":["data_insufficient"],"expected_route":"/aaron-marketing:email (email-creative-builder) | /aaron-marketing:launch | /aaron-marketing:ad --phase activate","blocking_inputs":["what 'launch' refers to (broadcast / GTM moment / ads)"],"must_not":["force a product-launch loop onto an email broadcast","assume campaign = paid ads"]}
- {"id":"cross-boost-this-sense-001","target_skill":"content-amplifier","scenario_family":"boost_this_sense","risk_gates":["external_side_effect","data_insufficient"],"expected_route":"/aaron-marketing:influencer --phase activate (content-amplifier) -> /aaron-marketing:ad --phase activate","blocking_inputs":["asset to boost","organic repurpose vs paid spend","usage rights if creator content"],"must_not":["treat 'boost this' as a net-new calendar post","put spend behind an asset without rights/gate"]}
```
