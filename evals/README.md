# Skill Quality & Regression Cases
**Status**: deterministic conformance suites plus simulated semantic seed cases
**Scope**: quality and regression review examples covering all 120 skills (16 SEO/GEO + 16 influencer + 16 paid ads + 16 email + 16 launch + 16 social + 16 narrative + 8 protocol) and the `/aaron-marketing:auto`/`/aaron-marketing:auto --deep` natural-language router
This directory stores small review cases that document expected skill behavior and known regressions. The deterministic suite manifest executes the typed scorer, registry runtime, shared HTTP, hook, routing, and permission boundaries offline. Semantic Markdown cases remain review/evaluation seeds; passing them does not prove business outcomes. The authoritative `/aaron-marketing:auto` scenario source is `evals/auto-routing-scenarios.source.md`; generated runtime projections live under `references/auto-routing-scenarios.md` and `references/auto-routing/`.
## Layout
```text
evals/<skill-name>/cases.md
```
Each YAML case uses:
```yaml
id: geo-content-optimizer-sim-001
type: eval-case
status: simulated | real
target_skill: geo-content-optimizer
scenario: "Short situation"
input_summary: "Request or failure signal"
expected_behavior: ["Expected behavior"]
failure_modes: ["Regression"]
```
Routing cases use the same schema and live in the target skill's `cases.md`. Use `id: routing-...`, keep `target_skill` as a real skill slug, and encode route order, required gates, handoffs, `NEEDS_INPUT`, or `BLOCKED` behavior in `expected_behavior`.
The `/aaron-marketing:auto` routing scenarios are maintained in `evals/auto-routing-scenarios.source.md` as a YAML `eval-case` bundle with real `target_skill` values plus `scenario_family`, `risk_gates`, `expected_route`, `blocking_inputs`, and `must_not`. For command-only scenarios, `target_skill` is the risk/state owner and `expected_route` is command truth. After changing that source, run `python3 scripts/generate-auto-routing-shards.py --write`; never hand-edit the generated runtime index or shards.
## Evidence Rule
Cases may be simulated, but simulated cases are non-validating and do not prove real behavior. Promote a case to `status: real` only after it is tied to a real user report, audit artifact, or another project-local signal.
External research can create candidate cases, but external research is non-validating. A case based only on external research stays `status: simulated` until tied to a project-local artifact or real project signal.
## Running Cases

Run all deterministic behavior suites:

```bash
python3 scripts/run-behavior-evals.py
```

An optional host/model adapter can evaluate the semantic seed cases without becoming a CI dependency:

```bash
python3 scripts/run-behavior-evals.py \
  --adapter-command "<adapter executable and arguments>" \
  --case content-quality-auditor
```

The runner sends one NDJSON object per case on stdin. The adapter returns one NDJSON object per case conforming to `behavior-adapter.schema.json`: `id`, boolean `passed`, and non-empty `evidence` are required. Output IDs must match input IDs exactly; missing, duplicate, unknown, malformed, or failed results fail closed. The adapter command is executed directly as an argument vector, never through a shell.

Semantic cases may also be reviewed manually against `expected_behavior` and `failure_modes`. Passing a simulated case is useful regression evidence, not acceptance evidence; acceptance still requires a project-local real signal.
