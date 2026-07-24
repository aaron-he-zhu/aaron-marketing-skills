# Engineering Maturity Acceptance Contract

This contract defines the repository-owned acceptance bar for **Prompt**, **Context**, **Harness**, **Loop**, and **Graph** engineering. It is an engineering release gate, not a market-wide benchmark and not a substitute for production outcome data.

## Score semantics

Each dimension has 20 independently reported controls worth 5 points each. The score is the sum of passing controls:

```text
dimension_score = passing_controls * 5
maturity_rating = dimension_score / 10
```

The target is **at least 95/100 (9.5/10) in every dimension**. An aggregate average cannot compensate for a weak dimension.

A control passes only when its declared repository evidence is current and reproducible. Documentation, schemas, implementation, tests, CI wiring, and operational evidence are separate controls; one cannot stand in for another. Simulated semantic cases are deterministic regression evidence, not real-provider evidence.

## Hard-gate rule

Every dimension has hard gates. If any hard gate fails, that dimension is capped at 90 even if 19 or 20 controls otherwise pass. The executable scorecard reports both the raw score and the capped score.

| Dimension | Hard gates |
|---|---|
| Prompt | 120/120 hash-bound machine contracts; runtime consumption; strict drift check; current real-provider semantic evidence |
| Context | complete first-party candidate planning; deterministic resolution; route → plan → resolve → snapshot integration; fail-closed missingness/authority behavior |
| Harness | supported end-to-end controller; verifiable run recovery/envelopes; release provenance and filesystem safety; current real-provider evidence gate |
| Loop | typed generic loop policy; verifier-based convergence; bounded cycles/time/budget; deterministic recovery and terminal preservation |
| Graph | authoritative typed edges; full node coverage and graph validation; executable planning; a tested fan-out/join workflow with explicit partial-failure policy |

## Evidence classes

- **S — structure:** strict schema, catalog coverage, hashes, and generated-artifact drift checks.
- **D — deterministic behavior:** offline unit, integration, and adversarial tests.
- **E — end-to-end behavior:** the supported controller composes the actual repository runtimes rather than test doubles alone.
- **R — real-provider evidence:** protocol-v2 model execution with bound adapter/model/source identity and a complete passing evidence record.
- **O — operational safety:** publishing, permissions, recovery, observability, and cross-host degradation are enforced at the mutation boundary.

The scorecard records the exact evidence class and failure reason for every control. Real-provider evidence may remain under ignored private run storage; only its bounded completion/provenance metadata is inspected. Raw prompts, model responses, credentials, and project evidence are never copied into the score report.

The machine-readable contracts are:

- `engineering-maturity-rubric.json` — the authoritative five-by-twenty control inventory;
- `engineering-maturity-rubric.schema.json` — the closed rubric shape;
- `engineering-maturity-report.schema.json` — the closed bounded evidence report.

Run the full acceptance gate with the UUID of a completed private semantic smoke run:

```bash
python3 scripts/check-engineering-maturity.py \
  --semantic-evidence-run-id <uuid> \
  --output memory/engineering-maturity-report.json
```

The command exits successfully only when all five dimensions reach at least 95 and every hard gate passes. `--json` also emits the bounded report to stdout. `--skip-dynamic` is diagnostic only: execution-backed controls fail rather than being assumed.

## Freshness and reproducibility

- Generated contracts and graphs must match their authoritative sources byte-for-byte under `--check`.
- Deterministic tests must pass at the current worktree.
- Real-provider evidence must bind the current semantic runner; source and
  private-staged identities for the project adapter and both candidate/judge
  output schemas; the current interpreter's `-I -S` no-site bootstrap and
  environment allowlist; selected cases; prompt templates; model identity; and
  source hashes. Only the staged adapter/schema bytes may execute. Its default
  maximum age is 30 days.
- A score report identifies the repository commit when available, branch, worktree state, checker/rubric hashes, evidence run ID, evidence completion hash, and evaluation timestamp. Reports written with `--output` are atomically installed with mode `0600`.
- A dirty worktree may be assessed during development, but release readiness requires a clean, pushed commit and reruns all current-source checks.

## Required iteration

Run the scorecard after each implementation phase. Any dimension below 95, any hard-gate failure, or any stale evidence creates a new remediation item. Work is complete only when all five final scores are at least 95 and the repository's full validation suite remains green.
