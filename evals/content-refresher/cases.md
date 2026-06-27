```yaml
{id: routing-command-refresh-decay-001, type: eval-case, status: simulated, target_skill: content-refresher, scenario: "User asks to update stale ranking content.", input_summary: "Refresh our 2024 Kubernetes cost guide that lost traffic.", expected_behavior: ["Route /aaron-seo-geo:create --refresh to content refresh and decay recovery.", "Check freshness, source dates, search intent drift, and schema freshness.", "Do not rewrite from scratch unless needed."], failure_modes: ["Routes to new content writing.", "Skips freshness evidence.", "Ignores ranking decay context."]}
```
