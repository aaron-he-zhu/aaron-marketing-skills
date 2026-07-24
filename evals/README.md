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

Select semantic cases without making a model call:

```bash
# Fixed 24-case cross-layer safety/routing/gate smoke profile
python3 scripts/run-behavior-evals.py --adapter-only --profile smoke --list-cases

# Smoke plus cases impacted by explicit paths or --changed-from <git-ref>
python3 scripts/run-behavior-evals.py --adapter-only --profile change-aware \
  --changed-file social/host/social-quality-auditor/SKILL.md --list-cases

# Complete 700-case profile; intended for a trusted scheduled adapter run
python3 scripts/run-behavior-evals.py --adapter-only --profile nightly --list-cases
```

An optional host/model adapter can evaluate the selected cases without becoming a CI dependency. The bundled Codex adapter is opt-in because it makes real model calls:

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

Every protocol-v2 execution requires an evidence run UUID. The runner writes the exact requests, an immutable identity manifest, incremental hash-chained structured results, and a prefix-verifiable completion record under ignored `memory/runs/<uuid>/semantic-eval/`. The manifest binds both source and staged identities for the adapter and its two schemas, the isolated interpreter flags and environment policy, the logical adapter command, runner implementation, and protocol schema. The current-source verifier re-hashes the exact project sources and current Python runtime, reconstructs the staged aggregate identity, and requires the `-I -S`/no-site/allowlist policy; changing or omitting any one invalidates the evidence. It fsyncs each validated batch before continuing; raw model prompts/outputs and real evidence bytes are never written there. If a later batch or host call fails, rerun the exact command with `--resume-evidence`: terminal cases are skipped, while prior host/adapter failures are retried. A changed profile, case set, adapter identity, source hash, runner/schema version, adapter runtime schema, isolation policy, or execution mode refuses resume.

The bundled Codex adapter first runs the target contract as the system under test without showing it the assertions, then starts a separate judge call over the hash-bound candidate response. Each SUT request consumes the current generated skill machine contract, target skill, shared execution contract, catalog, and hash-bound bundle references; an auto-routing case also receives `commands/auto.md`, the selected discipline command, and the product routing boundary. Evaluation variants, authored case corpora, and routing shards that contain expected assertions never enter the SUT-visible source set. Every model call runs from a private isolated workspace with only verified source bytes, a sanitized child environment, disabled optional tools, and a named read-only filesystem profile. It never uses the source repository as the model working directory and never sends real-case evidence bytes to the model. The host executable must be an absolute, non-symlink path with an operator-supplied SHA-256; the adapter verifies and copies those exact bytes into its private runtime before copying authentication, so ambient `PATH` and executable replacement cannot redirect a run.

Judge recovery is deliberately narrow and bounded. The candidate runs exactly once. A judge response that fails strict JSON parsing or the local closed result validator may be regenerated once, for a hard maximum of two judge attempts; a valid `behavior-failed` or `inconclusive` result, a timeout, a host error, or a schema rejection is terminal and is not retried. The second attempt uses a new private judge project and output file and receives the original judge prompt plus only a closed diagnostic code, the rejected response SHA-256, and its byte length—the rejected raw response is never echoed into the repair prompt. Each result records an ordered `judge_attempts` ledger; successful judge outcomes require exactly one accepted entry and it must be last. `judge_response_sha256` binds the last attempt, while `response_sha256` binds the candidate digest and the complete ordered ledger. The runner rejects reordered, altered, overlong, multiply accepted, or otherwise inconsistent ledgers, and two protocol-rejected attempts terminate as non-retryable `ADAPTER_PROTOCOL`.

The eight auditor gates also have generated machine-readable prompt contracts under `references/prompt-contracts/`. They are derived from the topology and framework catalogs, bind every runtime source by SHA-256, and contribute five semantic variants per gate: complete, missing evidence, single veto, multi-veto, and persistence authority. After changing an auditor, framework catalog, system catalog, or bound runtime source, run:

```bash
python3 scripts/generate-auditor-prompt-contracts.py --write
python3 scripts/generate-auditor-prompt-contracts.py --check
```

Semantic cases may also be reviewed manually against `expected_behavior` and `failure_modes`. Passing a simulated case is useful regression evidence, not acceptance evidence; acceptance still requires a project-local real signal.
