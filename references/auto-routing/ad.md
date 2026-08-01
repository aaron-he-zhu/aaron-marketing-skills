<!-- Generated routing projection; do not edit directly. -->
# Auto Routing Shard: Paid routing scenarios (ROAS)

Primary routing cases for `/aaron-marketing:ad`. This projection contains 6 cases. Read the [routing boundary contract](../aaron-product-api-contract.md) before execution.

## Runtime routing records

Each record is generated from the authoritative eval case and contains only route selection, blocking-input, risk-gate, and must-not fields.

```json
- {"id":"paid-prelaunch-account-audit-001","target_skill":"ad-account-auditor","scenario_family":"paid_launch_gate","risk_gates":["launch_readiness","conversion_signal_integrity","data_insufficient"],"expected_route":"/aaron-marketing:ad --phase activate (conversion-signal-qa -> ad-account-auditor) -> stop on veto","blocking_inputs":["account export","conversion tracking evidence","goal target"],"must_not":["approve launch with an open R1/R2/O1/O2/A1 veto","invent ROAS/CPA figures"]}
- {"id":"paid-roas-drop-reconcile-001","target_skill":"attribution-reconciler","scenario_family":"roas_discrepancy","risk_gates":["attribution","data_insufficient"],"expected_route":"/aaron-marketing:ad --phase scale (attribution-reconciler -> paid-measurement-loop)","blocking_inputs":["platform export","GA4/ecommerce export","attribution windows","date range"],"must_not":["treat platform-reported ROAS as ground truth","change budgets before reconciliation"]}
- {"id":"paid-creative-test-design-001","target_skill":"ad-test-designer","scenario_family":"ad_experiment_design","risk_gates":["claim_substantiation","external_side_effect","data_insufficient"],"expected_route":"/aaron-marketing:ad --phase orchestrate (ad-test-designer -> ad-creative-builder) -> stop for launch approval","blocking_inputs":["test objective","baseline metric","budget/duration","claim evidence"],"must_not":["launch the test automatically","use unsubstantiated claims in creative"]}
- {"id":"paid-audience-segments-001","target_skill":"audience-segment-builder","scenario_family":"paid_campaign_research","risk_gates":["data_insufficient"],"expected_route":"/aaron-marketing:ad --phase research (audience-segment-builder -> campaign-architect)","blocking_inputs":["product/offer","goal metric","platforms/geography","budget tier"],"must_not":["invent audience sizes or benchmark CPMs"]}
- {"id":"paid-creative-fatigue-001","target_skill":"fatigue-frequency-manager","scenario_family":"creative_fatigue","risk_gates":["data_insufficient"],"expected_route":"/aaron-marketing:ad --phase scale (fatigue-frequency-manager)","blocking_inputs":["frequency + CTR-over-time export","audience size","creative flight dates"],"must_not":["diagnose fatigue without frequency/decay evidence","invent benchmark CTRs"]}
- {"id":"paid-value-mapping-001","target_skill":"conversion-value-mapper","scenario_family":"value_based_bidding","risk_gates":["conversion_signal_integrity","data_insufficient"],"expected_route":"/aaron-marketing:ad --phase activate (conversion-value-mapper -> conversion-signal-qa)","blocking_inputs":["unit economics / margins","purchase-value signal","conversion tracking evidence"],"must_not":["send unverified conversion values to the platform","invent margins"]}
```
