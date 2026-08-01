<!-- Generated routing projection; do not edit directly. -->
# Auto Routing Shard: Narrative routing scenarios (TALE)

Primary routing cases for `/aaron-marketing:narrative`. This projection contains 6 cases. Read the [routing boundary contract](../aaron-product-api-contract.md) before execution.

## Runtime routing records

Each record is generated from the authoritative eval case and contains only route selection, blocking-input, risk-gate, and must-not fields.

```json
- {"id":"narrative-preship-gate-001","target_skill":"narrative-quality-auditor","scenario_family":"narrative_ship_gate","risk_gates":["narrative_truth_substantiation","message_readiness","claim_integrity"],"expected_route":"/aaron-marketing:narrative --phase evaluate (truth prerequisite -> system profile)","blocking_inputs":["narrative/message draft","claim evidence","audience","canon version"],"must_not":["blend truth/system/effectiveness","substantiate by assertion"]}
- {"id":"narrative-strategy-001","target_skill":"strategic-narrative-designer","scenario_family":"narrative_strategy","risk_gates":["narrative_truth_substantiation","data_insufficient"],"expected_route":"/aaron-marketing:narrative --phase trace -> architect (strategic-narrative-designer -> message-system-architect)","blocking_inputs":["current messaging","audience/beliefs","proof points","category context"],"must_not":["invent audience beliefs or category facts","skip the trace phase"]}
- {"id":"narrative-message-house-001","target_skill":"message-system-architect","scenario_family":"message_system","risk_gates":["claim_integrity","message_readiness","data_insufficient"],"expected_route":"/aaron-marketing:narrative --phase architect -> narrative-registry -> narrative-quality-auditor","blocking_inputs":["positioning","proof points","audience","tone/voice"],"must_not":["assert pillars without proof","skip evaluate profiles"]}
- {"id":"narrative-pitch-001","target_skill":"pitch-narrative-builder","scenario_family":"pitch_narrative","risk_gates":["narrative_truth_substantiation","claim_integrity","data_insufficient"],"expected_route":"/aaron-marketing:narrative --phase land (pitch-narrative-builder -> proof-point-packager) -> narrative-quality-auditor","blocking_inputs":["audience (investor/buyer)","traction evidence","proof points","ask"],"must_not":["fabricate traction or market size","present estimates as measured"]}
- {"id":"narrative-baseline-001","target_skill":"narrative-baseline-mapper","scenario_family":"narrative_baseline","risk_gates":["data_insufficient"],"expected_route":"/aaron-marketing:narrative --phase trace","blocking_inputs":["current assets/messaging","channels","claim inventory","time window"],"must_not":["claim complete coverage","issue gate verdict from trace"]}
- {"id":"narrative-drift-001","target_skill":"narrative-drift-monitor","scenario_family":"narrative_drift","risk_gates":["data_insufficient","memory_or_entity_write"],"expected_route":"/aaron-marketing:narrative --phase evaluate (narrative-drift-monitor) -> stop for inputs -> narrative-resonance-monitor -> message-test-designer -> stop for write permission","blocking_inputs":["narrative canon","in-market samples","period","test hypothesis","exact registry-write authorization"],"must_not":["overclaim causation","write memory without exact authorization"]}
```
