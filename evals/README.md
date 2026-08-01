# Skill Quality & Regression Cases

**Status**: deterministic conformance suites plus provenance-bound semantic profiles

**Scope**: quality and regression review examples covering all 120 skills (16 SEO/GEO + 16 influencer + 16 paid ads + 16 email + 16 launch + 16 social + 16 narrative + 8 protocol) and the `/aaron-marketing:auto`/`/aaron-marketing:auto --deep` natural-language router

This directory stores review cases that document expected skill behavior and known regressions. The deterministic suite manifest executes the typed scorer, registry runtime, shared HTTP, hook, routing, permission, distribution supply-chain, and publisher release-safety boundaries offline. The strict semantic corpus contains **572 authored cases + 88 generated routing cases + 40 generated auditor-contract cases = 700 cases**. Passing a semantic case proves only the recorded host/model behavior under the bound request; it does not prove a business outcome. The authoritative `/aaron-marketing:auto` scenario source is `evals/auto-routing-scenarios.source.md`; generated runtime projections live under `references/auto-routing-scenarios.md` and `references/auto-routing/`.

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

Cases may be simulated, but simulated cases are non-validating and do not prove real behavior. Promote a case to `status: real` only after it is tied to a project-local signal and add both `evidence_ref` and the current `evidence_sha256`; the strict parser rejects a real label without that evidence binding. Case provenance is independent of execution provenance: a real model can execute a simulated case, and a real case does not become executed evidence until a real adapter result exists.
External research can create candidate cases, but external research is non-validating. A case based only on external research stays `status: simulated` until tied to a project-local artifact or real project signal.
## Running Cases

Run all deterministic behavior suites:

```bash
python3 scripts/run-behavior-evals.py
```

If a sync provider has materialized repository files with more than one hard
link, do not weaken the runtime's single-link checks. Run the exact current
working tree from a private, single-link snapshot instead:

```bash
python3 scripts/run-isolated-evals.py

# Or select one suite; arguments after -- go to run-behavior-evals.py.
python3 scripts/run-isolated-evals.py -- --suite context-efficiency
```

The launcher copies tracked files plus non-ignored untracked files (including
current edits), excludes ignored private evidence, initializes a clean temporary
Git snapshot, validates a single-link Python interpreter, and removes the stage
after the run. Use `--keep-stage` only when you need to inspect a failed stage.
It prints the retained path; that directory is not a release artifact.

The `context-efficiency` suite executes the live planner and resolver for all
120 skills in both direct and `/auto` routes against an empty project fixture.
It guards actual required/selected assembly bytes rather than summing a separate
approximation. Generate a complete review snapshot without converting bytes to
model tokens:

```bash
python3 scripts/check-context-efficiency.py --json --output /tmp/context-efficiency.json
```

[`context-efficiency-policy.json`](context-efficiency-policy.json) intentionally
separates current regression guardrails from optimization targets. Tighten a
guard only after a measured baseline and semantic/routing/safety non-inferiority
review; reaching a byte target by itself is never a release acceptance signal.

Runtime/provider observations use the strict
[`context-usage-v1.schema.json`](context-usage-v1.schema.json). Create a record
from a hash-bound, consumer-separated assembly when one is available, validate
it, and aggregate multiple records:

```bash
python3 scripts/context-usage.py from-assembly \
  --assembly /path/to/context-assembly.json \
  --record-id <run-id:turn-id> \
  --recorded-at 2026-08-01T00:00:00Z \
  --capability-profile governed \
  --output /tmp/context-usage.json

python3 scripts/context-usage.py validate /tmp/context-usage.json
python3 scripts/context-usage.py summarize /tmp/context-usage.json
```

`from-assembly` recomputes the `assembly_signature` SHA-256 integrity field and
validates consumer arithmetic before recording controller body bytes as
`control_plane`, model body bytes as `model_visible_static`, tool body bytes as
`tool_schemas`, and deferred/on-demand bytes as `references`. Despite the legacy
field name, `assembly_signature` is a plain integrity hash—not a cryptographic
signature, signer identity, or attestation. It leaves provider tokens null. If
only a resolver manifest exists, record the manifest-level baseline instead:

```bash
python3 scripts/context-usage.py from-manifest \
  --manifest /path/to/context-manifest.json \
  --record-id <run-id:turn-id> \
  --recorded-at 2026-08-01T00:00:00Z \
  --capability-profile governed \
  --host-profile claude-code \
  --output /tmp/context-usage-manifest.json
```

Provider usage fields stay `null` when unavailable. The tool never relabels the
resolver's UTF-8 byte counts as provider tokens. A manifest-only
record does not infer `model_visible_static`; that field is populated only from
the explicit consumer split in a validated assembly.
`from-manifest` first applies the resolver's complete manifest validator,
including embedded-request identity hashes, invocation/route/budget identity,
candidate coverage, selected-resource arithmetic, and `context_signature`
integrity. This is semantic validation of the captured document; live-source
re-resolution remains a separate operation. A `manual` provenance label is an
origin classification only and does not establish trust or attestation.
The same record has nullable paired-experiment identities/hashes and disclosure
recall/precision fields. Deterministic bytes can be compared without provider
usage; token-savings claims require complete provider-reported usage, and
cost-savings claims are unsupported by protocol v3.

Select semantic cases without making a model call:

```bash
# Fixed 24-case cross-layer safety/routing/gate smoke profile
python3 scripts/run-behavior-evals.py --adapter-only --profile smoke --list-cases

# Smoke plus cases impacted by explicit paths or --changed-from <git-ref>
python3 scripts/run-behavior-evals.py --adapter-only --profile change-aware \
  --changed-file social/host/social-quality-auditor/SKILL.md --list-cases

# Complete 700-case profile; intended for an operator-scheduled adapter run
python3 scripts/run-behavior-evals.py --adapter-only --profile nightly --list-cases
```

## Adapter protocols

An optional host/model adapter can evaluate the selected cases without becoming a CI dependency. The bundled Codex adapter is opt-in because it makes real model calls. The protocols have separate acceptance roles:

- **Protocol v2** is the current-source real-provider smoke used by the five-dimension engineering-maturity gate.
- **Protocol v3** performs blind route → selected-skill context → independent judge execution and is the paired evaluation path for `explicit` versus `balanced` or `lean`.

### Protocol v2: engineering-maturity smoke

```bash
python3 scripts/run-behavior-evals.py \
  --adapter-only \
  --adapter-protocol 2 \
  --profile smoke \
  --case derived-content-quality-auditor-missing-evidence \
  --adapter-batch-size 1 \
  --evidence-run-id <CANONICAL_UUID> \
  --adapter-implementation-ref scripts/adapters/codex-behavior-adapter.py \
  --adapter-command 'python3 scripts/adapters/codex-behavior-adapter.py --codex-bin <ABSOLUTE_CODEX_PATH> --codex-sha256 <CODEX_BINARY_SHA256> --model <SUT_MODEL_ID> --judge-model <DISTINCT_JUDGE_MODEL_ID> --workers 1'
```

Protocol v2 sends one hash-bound NDJSON request per case and requires one result conforming to [`behavior-adapter-v2.schema.json`](behavior-adapter-v2.schema.json). Results bind the request, SUT/judge model and adapter identity, exact adapter implementation, prompt/parameter hashes, timestamps, candidate/judge response hashes, complete expected/forbidden assertion coverage, and a closed behavior/inconclusive/host/adapter failure taxonomy. Real and simulated execution modes cannot be conflated; the v2 runner requires `execution_mode: real`. Missing, duplicate, unknown, malformed, simulated, or failed results fail closed. Raw prompts and responses are not result fields. Adapter commands are parsed into an argument vector and run without a shell. Existing adapter commands still default to protocol v1 for compatibility; select v2 explicitly and provide the project-relative `--adapter-implementation-ref` for model-backed profiles. The official adapter must initially be the Python script at `argv[1]` of the same resolved interpreter as the runner. The runner then copies the already-read adapter and both already-read output schemas into a private read-only staging tree and executes only that staged script as `<current-python> -I -S <staged-script>`. Its child environment is rebuilt from a six-key allowlist and contains no inherited `PYTHON*` variables, so `PYTHONPATH`, `sitecustomize`, user-site packages, and a source-schema swap after binding cannot intercept execution. The staged adapter and both staged schemas are re-hashed before and after every batch. `--adapter-timeout` applies per outer batch. The bundled adapter's `--workers 1..4` partitions that batch across isolated private runtimes while preserving input result order; use one worker for calibration, then a single full-profile batch with a bounded worker count after calibration passes.

Every protocol-v2 execution requires an evidence run UUID. The runner writes the exact requests, an immutable identity manifest, incremental hash-chained structured results, and a prefix-verifiable completion record under ignored `memory/runs/<uuid>/semantic-eval/`. The manifest persists the exact resolved logical adapter argv and its digest, the complete case-selection provenance and its digest, both source and staged identities for the adapter and its three schemas, the isolated interpreter flags and environment policy, runner implementation, and protocol schema. The current-source verifier re-hashes the exact project sources and current Python runtime, reconstructs the staged aggregate identity, recomputes the command and selection digests, and requires the `-I -S`/no-site/allowlist policy; changing or omitting any one invalidates the evidence. Prompt-profile certification additionally reconstructs the current filtered, change-aware, smoke, or nightly selection (including reasons), binds the manifest profile to the stored arm request, and requires the command's current Codex binary plus SUT/judge options to match that request. It fsyncs each validated batch before continuing; raw model prompts/outputs and real evidence bytes are never written there. If a later batch or host call fails, rerun the exact command with `--resume-evidence`: terminal cases are skipped, while prior host/adapter failures are retried. A changed profile, case set, adapter argv or identity, source hash, runner/schema version, adapter runtime schema, isolation policy, or execution mode refuses resume. The local hash chain is integrity and replay evidence for repository-held bytes, not independent provider or operator attestation. Where promotion policy requires externally trustworthy provenance, the provider identity/revision and release approval still need a trusted signature or attestation path outside this self-authenticating chain.

### Protocol v3: blind routing and compact-profile pairs

Run a non-deployable balanced ablation with the same staged adapter boundary:

```bash
python3 scripts/run-behavior-evals.py \
  --adapter-only \
  --adapter-protocol 3 \
  --profile smoke \
  --case routing-outreach-vs-contract-helper-outreach-manager-001 \
  --host-profile claude-code-plugin-host \
  --model-id <SUT_MODEL_ID> \
  --judge-model-id <DISTINCT_JUDGE_MODEL_ID> \
  --prompt-profile balanced \
  --evaluation-only \
  --evidence-run-id <CANONICAL_UUID> \
  --adapter-implementation-ref scripts/adapters/codex-behavior-adapter.py \
  --adapter-command 'python3 scripts/adapters/codex-behavior-adapter.py --codex-bin <ABSOLUTE_CODEX_PATH> --codex-sha256 <CODEX_BINARY_SHA256> --model <SUT_MODEL_ID> --judge-model <DISTINCT_JUDGE_MODEL_ID> --workers 1'
```

The routing candidate receives the request text and a target-neutral 120-skill discovery index, never the expected route, assertions, `must_not`, target-derived coverage metadata, or target-derived paths. Only after it selects a skill does the adapter consume the planner/resolver/assembly model-resource allowlist for that direct selected-Skill route and load its explicit, balanced, or lean representation. The `/auto` answer shard is discarded before this post-route assembly and cannot enter the candidate prompt or staged source directory. The independent judge receives the selected transcript and expected outcomes. Every v3 execution uses the same private staged adapter, immutable manifest, hash-chained result stream, and completion record as v2.

A deployable compact certification additionally requires canonical real cases; at least 40 cases, 3 repeats, and 8 verifier-derived coverage strata; a distinct, evidence-wide-unique protocol-v3 run UUID plus stored request/result provenance for every control/candidate arm; immutable SUT and judge revisions with evidence-wide consistency; and a genuinely independent judge (`judge_model_id != model_id`, with same-provider aliases forbidden from sharing one non-null immutable revision). It also requires exact host/toolset/adapter/assembly/source bindings. In particular, each post-route model-resource set must exactly equal the current host/distribution branch's full required and `explicit-runtime-read` closure; a self-consistent caller-supplied subset is rejected. The declared reduction floor is measured from the full paired `model_body_bytes` (not a Skill/capsule-only harness ratio); routing and quality must be non-inferior; both arms must satisfy absolute 95% routing and 90% quality floors; candidate safety failures and safety regressions must be zero; and the binding must be current and Governed. Coverage strata are evidence-only: auto-routing cases derive `auto:<canonical source scenario_family>`, while authored and derived-auditor cases derive `discipline:<current system-catalog discipline>`. Neither `coverage_stratum` nor `scenario_family` may enter the public candidate case, and post-route arm resources may not contain an `/auto` routing shard. Capture rebuilds the entire stored request through the current `build_v3_requests` path from the current canonical case and requires canonical equality across the public scenario/input, judge assertions/`must_not`, complete 120-skill routing index, selection, execution, and assembly binding. It then runs the complete v3 result validator—including assertion coverage, judge ledger, routing, failure taxonomy, real execution mode, and manifest-bound adapter hash—before quality or safety booleans are projected. Evidence timestamps must enclose every actual arm, age is measured from the latest arm end rather than a fresh wrapper timestamp, and the certificate binds the full arm-run-set hash. Supply prior certificates with repeated `--previous-certificate` arguments during promotion to reject an already-promoted or duplicate run set. Provider usage may be null for behavioral comparison. Complete provider telemetry alone is not proof of savings: protocol v3 keeps token-savings permission false until a positive paired input-token reduction gate and uncertainty treatment exist. Cost-savings claims are unsupported.

The current corpus contains 700 simulated cases, the bundled adapter reports both `model_revision: null` and `judge_model_revision: null`, and `references/prompt-profiles.json` contains zero certified bindings. Protocol-v3 compact runs are therefore evaluation-only, and `explicit` remains the deployment default. A package-local certificate and hashes alone are not a production trust anchor; non-empty compact bindings remain fail-closed until a signed release-attestation path can be revalidated. Before that path may enable bindings, the release policy must also add uncertainty-aware paired inference (for example confidence intervals plus an exact paired test such as McNemar) and 100% required-case gates for high-risk, auditor, and protocol subsets; the current aggregate floors do not claim those guarantees.

For protocol v2, the bundled Codex adapter runs the bound target contract as the system under test without showing it the assertions. For protocol v3, it first performs blind routing, then loads only the selected representation and runs the selected-skill task. Both protocols use a separate judge call over the hash-bound candidate response. Evaluation variants, authored case corpora, routing expectations, and real-case evidence bytes never enter candidate-visible context. Every model call runs from a private isolated workspace with only verified source bytes, a sanitized child environment, disabled optional tools, and a named read-only filesystem profile. The host executable must be an absolute, non-symlink path with an operator-supplied SHA-256; the adapter verifies and copies those exact bytes into its private runtime before copying authentication, so ambient `PATH` and executable replacement cannot redirect a run.

Judge recovery is deliberately narrow and bounded. The candidate runs exactly once. A judge response that fails strict JSON parsing or the local closed result validator may be regenerated once, for a hard maximum of two judge attempts; a valid `behavior-failed` or `inconclusive` result, a timeout, a host error, or a schema rejection is terminal and is not retried. The second attempt uses a new private judge project and output file and receives the original judge prompt plus only a closed diagnostic code, the rejected response SHA-256, and its byte length—the rejected raw response is never echoed into the repair prompt. Each result records an ordered `judge_attempts` ledger; successful judge outcomes require exactly one accepted entry and it must be last. `judge_response_sha256` binds the last attempt, while `response_sha256` binds the candidate digest and the complete ordered ledger. The runner rejects reordered, altered, overlong, multiply accepted, or otherwise inconsistent ledgers, and two protocol-rejected attempts terminate as non-retryable `ADAPTER_PROTOCOL`.

The eight auditor gates also have generated machine-readable prompt contracts under `references/prompt-contracts/`. They are derived from the topology and framework catalogs, bind every runtime source by SHA-256, and contribute five semantic variants per gate: complete, missing evidence, single veto, multi-veto, and persistence authority. After changing an auditor, framework catalog, system catalog, or bound runtime source, run:

```bash
python3 scripts/generate-auditor-prompt-contracts.py --write
python3 scripts/generate-auditor-prompt-contracts.py --check
```

Semantic cases may also be reviewed manually against `expected_behavior` and `failure_modes`. Passing a simulated case is useful regression evidence, not acceptance evidence; acceptance still requires a project-local real signal.
