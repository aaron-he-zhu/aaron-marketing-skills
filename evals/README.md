# Skill Quality & Regression Cases
**Status**: lightweight simulated seed set
**Scope**: quality and regression review examples covering all 69 skills (16 SEO/GEO + 5 protocol + 16 influencer/IMPACT + 16 paid ads + 16 email) and the `/aaron-marketing:auto`/`/aaron-marketing:auto --deep` natural-language router
This directory stores small review cases that document expected skill behavior and known regressions. They are reviewed manually or with Claude during PR and code review. They are not automated benchmarks and do not prove production behavior. (The `/aaron-marketing:auto` scenario library is runtime routing data and now lives in `references/auto-routing-scenarios.md`, not here.)
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
The `/aaron-marketing:auto` routing scenarios live in `references/auto-routing-scenarios.md` (a runtime resource `commands/auto.md` consults) as a YAML `eval-case` bundle with real `target_skill` values plus `scenario_family`, `risk_gates`, `expected_route`, `blocking_inputs`, and `must_not`. For command-only scenarios, `target_skill` is the risk/state owner and `expected_route` is command truth. Update that file when you change routing in `commands/auto.md`.
## Evidence Rule
Cases may be simulated, but simulated cases are non-validating and do not prove real behavior. Promote a case to `status: real` only after it is tied to a real user report, audit artifact, or another project-local signal.
External research can create candidate cases, but external research is non-validating. A case based only on external research stays `status: simulated` until tied to a project-local artifact or real project signal.
## Running Cases
These cases are reviewed by reading them during PR or code review, or by asking Claude to evaluate a skill's output against the relevant `expected_behavior` and `failure_modes` for a given `target_skill` or case id. Passing a simulated case is useful regression evidence, but it is not acceptance evidence on its own — that still requires a project-local real signal.
