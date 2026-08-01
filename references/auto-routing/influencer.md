<!-- Generated routing projection; do not edit directly. -->
# Auto Routing Shard: Influencer

Primary routing cases for `/aaron-marketing:influencer`. This projection contains 4 cases. Read the [routing boundary contract](../aaron-product-api-contract.md) before execution.

## Runtime routing records

Each record is generated from the authoritative eval case and contains only route selection, blocking-input, risk-gate, and must-not fields.

```json
- {"id":"influencer-creator-discovery-001","target_skill":"influencer-discovery","scenario_family":"creator_shortlist","risk_gates":["brand_safety","engagement_authenticity","data_insufficient"],"expected_route":"/aaron-marketing:influencer --phase scout (influencer-discovery) -> stop for criteria; resume influencer-discovery -> fit-scorer","blocking_inputs":["brand/campaign goal","audience definition","budget/follower tier","engagement floor","location/language","exclusions","creator evidence"],"must_not":["recommend creators without required criteria","claim downstream steps already ran","score partial STAR coverage","render a gate verdict from discovery"]}
- {"id":"influencer-content-review-gate-001","target_skill":"creator-content-auditor","scenario_family":"sponsored_content_gate","risk_gates":["ftc_disclosure","claim_integrity","data_insufficient","external_side_effect","memory_or_entity_write"],"expected_route":"/aaron-marketing:influencer --phase activate (creator-content-auditor) -> stop for evidence or publish/write permission","blocking_inputs":["disclosure status","claim evidence","brief"],"must_not":["approve without observed disclosure and claim evidence","convert Unknown into a veto or score","write an unvalidated or unauthorized audit artifact"]}
- {"id":"influencer-roi-readout-001","target_skill":"roi-calculator","scenario_family":"campaign_roi","risk_gates":["attribution","data_insufficient"],"expected_route":"/aaron-marketing:influencer --phase report (performance-analyzer -> roi-calculator)","blocking_inputs":["spend","conversions","baseline/control"],"must_not":["claim ROI without a control"]}
- {"id":"influencer-outreach-side-effect-001","target_skill":"outreach-manager","scenario_family":"creator_outreach","risk_gates":["external_side_effect","data_insufficient"],"expected_route":"/aaron-marketing:influencer --phase activate (outreach-manager) -> stop for approval","blocking_inputs":["target list","message owner","explicit send approval"],"must_not":["send outreach automatically"]}
```
