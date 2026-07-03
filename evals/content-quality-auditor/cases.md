Simulated seed cases for CORE-EEAT veto behavior, cap arithmetic, `BLOCKED`, handoff, and artifact gates.
```yaml
{id: content-quality-auditor-sim-001, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "Affiliate links appear before disclosure.", input_summary: "Best hosting article has comparison tables and affiliate buttons; disclosure is in footer.", expected_behavior: ["Flag the relevant veto.", "Apply cap arithmetic.", "Explain the issue clearly."], failure_modes: ["Treats disclosure as minor.", "Averages away the veto.", "Omits cap_applied or final_overall_score."]}
```
```yaml
{id: content-quality-auditor-sim-002, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "User asks for a full score without page content or URL.", input_summary: "Score my Kubernetes autoscaling article; no article is provided.", expected_behavior: ["Return NEEDS_INPUT or BLOCKED.", "State needed evidence.", "Do not fabricate scores."], failure_modes: ["Guesses from topic.", "Emits full artifact without evidence.", "Marks audit complete despite missing data."]}
```
```yaml
{id: content-quality-auditor-sim-003, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "Raw score passes but one veto fails.", input_summary: "Expertise and structure are strong, but a veto item fails.", expected_behavior: ["Keep raw and final capped scores separate.", "Use math.floor rounding.", "Set cap_applied: true."], failure_modes: ["Rounds 77.5 to 78.", "Caps only a dimension.", "Drops raw_overall_score."]}
```
```yaml
{id: content-quality-auditor-sim-004, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "Audit has fixable issues and downstream work.", input_summary: "Outdated stats, missing credentials, and weak source freshness.", expected_behavior: ["Emit DONE_WITH_CONCERNS or DONE with priorities.", "Preserve open loops.", "Recommend the right downstream skill."], failure_modes: ["Drops actionable handoff.", "Uses internal jargon.", "Creates recursive routing."]}
```
```yaml
{id: content-quality-auditor-sim-005, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "Title promises definitive medical proof but body has generic opinions.", input_summary: "'Best Diabetes Supplements Proven by Doctors' has no named doctors, citations, or proof.", expected_behavior: ["Flag C01 or equivalent title-mismatch veto.", "Treat as veto-level publish risk.", "Preserve required remediation."], failure_modes: ["Only rewrites title.", "Treats as low-priority CTR issue.", "Scores as publish-ready."]}
```
```yaml
{id: content-quality-auditor-sim-006, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "Article cites conflicting current statistics for one claim.", input_summary: "Market is listed as $4B and $14B in different sections.", expected_behavior: ["Flag R10 or equivalent contradictory-data veto.", "Require source/date reconciliation.", "Do not average the contradiction away."], failure_modes: ["Marks as minor fact-check note.", "Keeps high final score.", "Fails to ask for source/date evidence."]}
```
```yaml
{id: content-quality-auditor-sim-007, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "Two or more veto items fail.", input_summary: "YMYL affiliate review lacks disclosure, has contradictory safety data, and unsupported expert claims.", expected_behavior: ["Set BLOCKED by runbook rules.", "Do not emit final_overall_score when BLOCKED.", "List vetoes and unblock actions."], failure_modes: ["Applies single-veto cap only.", "Publishes final score despite BLOCKED.", "Hides a veto in general recommendations."]}
```
```yaml
{id: content-quality-auditor-sim-008, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "Audit output misses required scoring artifact fields.", input_summary: "Narrative recommendations omit cap_applied, raw_overall_score, and final_overall_score while claiming DONE.", expected_behavior: ["Fail artifact gate or return DONE_WITH_CONCERNS.", "Require score fields when allowed.", "Explain blocked, capped, or publish-ready state."], failure_modes: ["Accepts narrative-only output.", "Claims DONE without score artifacts.", "Does not distinguish capped, blocked, and uncapped states."]}
```
```yaml
{id: routing-content-quality-auditor-sim-001, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "User asks whether content is ready to publish.", input_summary: "Can we publish this affiliate review after the rewrite?", expected_behavior: ["Route content-quality-auditor as the publish-readiness gate.", "Use on-page-seo-auditor only for page SEO issues after quality risk is assessed.", "Preserve veto and BLOCKED handling."], failure_modes: ["Routes only to content-writer.", "Skips publish gate.", "Treats disclosure risk as ordinary SEO."]}
```
```yaml
{id: routing-content-quality-auditor-sim-002, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "User asks for page audit with YMYL claims.", input_summary: "Audit this medical supplement page for SEO and whether claims are safe.", expected_behavior: ["Route content-quality-auditor as required protocol gate.", "Allow on-page-seo-auditor as downstream or paired skill.", "Return NEEDS_INPUT if page content or URL is missing."], failure_modes: ["Runs only on-page SEO.", "Ignores YMYL claim substantiation.", "Fabricates scores without evidence."]}
```
```yaml
{id: routing-content-quality-auditor-sim-003, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "User wants title/meta help for an unsupported claim.", input_summary: "Make a title tag saying our product is proven best, but the page has no proof.", expected_behavior: ["Route title accuracy risk to content-quality-auditor before serp-markup-builder.", "Flag claim-substantiation issue.", "Handoff to serp-markup-builder only after claim language is safe."], failure_modes: ["Optimizes the title without quality gate.", "Treats claim support as CTR copywriting.", "Skips veto-level risk."]}
```
```yaml
{id: routing-command-publish-gate-001, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "User asks for a CMS-neutral publish package.", input_summary: "Prepare this article for publishing with metadata, schema, links, and final gate.", expected_behavior: ["Route /aaron-marketing:seo-geo --mode create --publish through content-quality-auditor before any ready verdict.", "Require page_full or per_article_full audit evidence for ready.", "Include audit_ref, gate_verdict, veto_state, score cap, blockers, and ready_verdict_allowed."], failure_modes: ["Marks ready from rollup-only audit.", "Omits veto evidence.", "Skips internal-linking handoff."]}
```
```yaml
{id: routing-command-audit-quality-001, type: eval-case, status: simulated, target_skill: content-quality-auditor, scenario: "User asks for content quality and publish readiness audit.", input_summary: "Audit this article for EEAT and tell me if it can ship.", expected_behavior: ["Route /aaron-marketing:seo-geo --mode audit to page or domain audit and use CORE-EEAT gate for content.", "Return ready_with_concerns or blocked when evidence is incomplete.", "Do not fabricate scores."], failure_modes: ["Uses on-page SEO only.", "Marks ready without full audit.", "Ignores vetoes."]}
```
