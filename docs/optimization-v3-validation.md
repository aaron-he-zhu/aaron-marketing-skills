# v3 implementation and validation

User authorization: “分阶段全部实施”, 2026-10-27. Scope: both repositories,
implementation and tests in the task's managed **cloud** environment
(`provider: cloud`, observed phase `running`), under `/workspace`.
No changes were written or synced to the user's omarchy computer.
At the pre-PR implementation acceptance point, no commit, remote push, PR,
merge, deployment or external permission/credential change had been performed.
“Local” means the cloud checkout. The user subsequently authorized commits,
pushes and draft PRs: “推送pr，但是不合并。” Merge, deployment and external
permission/credential changes remain outside that authorization.

The approved [plan](optimization-v3.zh.md) is the execution baseline.

| Repository | Initial commit | Initial tracked changes |
|---|---|---|
| aaron-marketing-skills | cac58547bc84ed2af865b68b90c5cfbb79b63978 | None |
| aaronmarketing-site | fe778e70a48f9441066052786ef2045eae0be542 | None |

Both repositories use `feature/v3-simplification`. Core working sources are
**20.2.0, unreleased**; the website deliberately pins released core 20.1.0 at
the original exact commit. No unpublished core content is passed off as a
published source. The plan and validation are tracked deliverables rather than
only ignored `docs/plans/` material.

## Plan coverage

| Stage | Implemented changes | Preserved boundaries / evidence |
|---|---|---|
| A | Retire nine Pi PoC files and its 96-package research graph; remove directory-specific scanner exceptions. Deduplicate the three full CI paths through one actual isolated unittest discovery plus uncovered conformance. Correct authored/generated maintenance instructions. | Generic dependency/privacy/source/publishing negative controls retained; S0/S1 baseline retained. Required-status identity temporarily retained as a stdlib compatibility job. |
| B | Remove six compulsory run/workflow cache writes and their commit-then-cache-failure branches. Keep explicit export. Waiting survives observation. Start resolves once; resume uses one verified event prefix/savepoint view. Retire compact production selection/certification/ablation and 121 capsule files. | Immutable events/plans/snapshots/savepoints, selected ancestry, nonce/receipt single consumption, lease/fencing, budgets, authorization and hashes retained. Explicit host/controller/model/tool separation retained; v2 provider protocol remains 2.0. |
| C | Source snapshots feed Astro directly; remove body/Quick Start/Python generation chain and dead renderer. Derive catalog membership/ordering/counts. Merge peer publication properties and matrix presentation. Share four authoring catalog traversals, generate fixed runtime ceilings and 13 current Portable-install version surfaces, and add one thin refresh command. | 120 route/path/slug identities and standalone installation preserved. Offline builds and independent pinned-source comparison retained. Fixed ceilings cannot be relaxed by package self-report. No generic task/DSL engine added. |
| D | Remove 80 manually duplicated criterion copies after reconciliation; compile exactly one authoritative table block per framework. Generate shared auditor activation/report rules, 37 profile policy views and runbook veto table. Clarify 20 item boundaries with 70 fixed facts/state cases. Embed the six-step improvement method in the existing shared contract. | 320 qualified items/37 profiles, numerical policies, applicability, coverage, Unknown/N/A, vetoes and rounding match the independent frozen baseline. Professional criterion changes are versioned and distinct from structural equivalence; no new scoring engine or evidence store. |

The [definition reconciliation](optimization-v3-bench-definitions.md) records all
17 wording differences among the retired copies (63 others were formatting),
20 revised items and 70 boundary cases. The examples are lookup-only material; required item anchors/evidence rules stay in each benchmark. Legacy optional catalog definition
fields remain readable. Item policies are preserved. Eight original auditor
SKILL paths and all eight standalone fallbacks remain.

The frozen compatibility fixture records original skill paths, marketplace
slugs and public URLs, 320 qualified IDs, 37 profiles and numerical/conditional
policy hashes. Independent tests compare complete identity sets, not just counts.
Arithmetic goldens remain independent of the generators.

## Validation state

Final aggregate core validation: **passed**. `python3 scripts/run-behavior-evals.py --with-unittest-discovery` ran **1141 tests in 322.164 seconds, zero skipped**, then passed all **36** declared conformance suites. Twenty-two suites reused the proven same test IDs and source hashes from that actual discovery; independent oracles still executed. This run used the final implementation sources, not only the earlier focused revisions.

Already passed on the integrated sources:

- `python3 scripts/maintain.py --write` followed by `--check`: all projections
  current; 120 machine contracts and eight prompt contracts / 40 variants.
- `bash scripts/check-versions.sh`: core 20.2.0, all 120 skills, all tracking,
  release instructions and locale surfaces aligned.
- Python compilation, shell syntax and `git diff --check`.
- All 120 canonical Skills individually validated; status/version checks and the current working-tree PII/secret scan passed.
- Architecture, local links (6,241), routing, context budget, wiki exclusion and
  734-case structural eval lint.
- Bench and auditor targeted suite: 61 tests; later profile/parser/mode additions
  also passed. Independent golden behavior covers all 37 profiles.
- Recovery targeted suites: 154 tests; explicit context/distribution/provider
  fixtures: 191 tests; CI/workflow/maintenance targeted suites: 42 tests.
  These sets overlap and are not summed as a unique total.
- Publishing/receipt integration regression: 37 tests after correcting fixture
  copying and current-version expectations.
- Website final run: 39 tests (8 client, 19 install proof, 12 skills/source),
  export assertion, Astro check 0 errors/0 warnings/one existing deprecation
  hint, offline build 257 HTML / 255 sitemap URLs / 120 skill URLs.

Initial aggregate discovery ran 1,141 tests and exposed 29 fixture errors from
cross-filesystem hard links plus one outdated supported-version expectation.
The fixture now copies independent inodes instead of linking the real checkout;
release history assertions include 20.2.0. No production guard was relaxed.
The affected 37 tests passed. A subsequent aggregate passed every unit but exposed the unchanged 150,000-byte selected-context guard. All 70 examples were retained in `references/benchmark-boundary-examples.md` as optional lookup material; the duplicate 4,439-byte connector command table was removed from CONNECTORS while all 28 advertised helpers, their arguments/credentials and safety controls remained in the existing unchanged helper guide. No policy or evidence threshold was raised. The final complete aggregate then passed.

Website page comparison: 238 normalized DOMs identical after pin normalization;
17 skill pages correct fence-heading/truncation descriptions, with two showing
additional complete original list items/references. Staff/chief pages correct
the registry count. All original preformatted and inline code remains, sitemap
XML is identical, and other navigation/SEO/JSON-LD is unchanged. Detailed site
evidence is in `aaronmarketing-site/docs/engineering/v3-validation.md`.

## Intentional compatibility and rollback limits

- Historical blind protocol 3.0 is not relabeled as 3.1. It requires the pinned
  historical runtime. Current catalogs/modules use 2.0 and explicit-only
  deployment; current blind protocol is 3.1 with gold-standard isolation and
  independently bound sources/judge. Standalone explicit evaluation remains
  `deployment_eligible: false`.
- Existing neutral output fields remain `null`, empty or zero where old
  consumers still need the shape; no compact certification/fallback path
  survives behind those fields.
- Project/repair flags remain explicit exports. Old plans and event bytes are
  not rewritten. In the exercised rollback fixture, the pinned old workflow
  runtime verified new records after matching projection export; this does not
  establish compatibility for every new artifact. The old run reducer still wrongly wakes
  waiting on observation, so that runtime cannot safely take over such runs.
  Pause writers, fix the head and validate verify/resume/idempotency on an
  isolated snapshot before rollback. If safe takeover fails, retain facts and
  stop progression. Code rollback cannot undo external effects.
- The GitHub integration's GET of
  `repos/aaron-he-zhu/aaron-marketing-skills/branches/main/protection/required_status_checks`
  was rejected with **403: Resource not accessible by integration**. The read
  did not succeed; external settings were not changed and the action was not
  retried. The old Pi workflow/check identity therefore remains as a lightweight
  stdlib regression entry until a repository owner can verify required-status
  bindings. This exception does not retain the Node probe or its dependencies.
- At pre-PR acceptance, remote Actions were **not run**; their later results
  belong to the PR checks. Real provider/model executions, human blind-rater
  reliability studies, business outcome calibration and deployment were **not run**.
  Fixture fields saying `execution_mode: real` are exercised protocol fields,
  not proof of actual provider calls. Release evidence/permission gates remain
  closed until their separate requirements are met.

## Actual simplification

- Six default cache writes become zero; exports are deliberate.
- Production context selection keeps one representation, explicit.
- 121 capsule JSON files (1,032,169 bytes), four research schemas, four research
  scripts and two research tests are removed; nine old Pi files are also removed.
- Eight common auditor activation/report texts and 37 profile tables are
  projections, not additional manually maintained rules.
- Eighty duplicate criterion copies become zero; all 320 items remain.
- Four catalog walkers share one authoring implementation. Fixed ceilings and
  Portable-release version strings have one authored source.
- Full S2/S3 static reachable top-level check calls decrease 72 → 37; the only
  retired independent oracle is the non-deployable capsule check, while the
  Claude discovery check is added. This is not a timing or model-quality claim.
- Website removes 1,218,526 bytes of committed body/Quick Start intermediates.
  Before its final validation note, all site authoring inputs net -1,217,184
  bytes / -1,336 lines, with file count +1. Final totals below include evidence documents; file counts and payload size are reported separately.

## Final guard measurements

The original context-efficiency policy remains unchanged. All 240 assemblies
pass: direct selected p50 **144,668 B**, auto selected p50 **149,611 B**, below
the 150,000 B guard. These are resolver allocation bytes, not provider token
usage or browser downloads. Normal model cost/quality savings are not claimed.

Core catalog display labels Content/Research retain their compatibility names;
the fixed C/R IDs map to the human Contextual Clarity/Referenceability sections.
There is no extra dimension or changed weighting. FAQ/applicability redesign,
empirical rater calibration and downstream standards publication require their
own evidence; they were not silently introduced as part of this structural cut.

## Final source totals

Source bytes count Git baseline files and current non-ignored files, including
new tests/evidence documents and deleted generated data. They exclude Git
objects, node_modules, dist and caches. These numbers describe authoring inputs,
not browser transfer size or runtime performance.

| Repository | Baseline files / bytes | Current files / bytes | Net files / bytes |
|---|---|---|---|
| Core | 1,089 / 14,197,402 | 961 / 12,965,680 | -128 / -1,231,722 |
| Site | 338 / 5,269,506 | 340 / 4,056,346 | 2 / -1,213,160 |

All four planned stages are implemented and their local acceptance checks pass.
No implementation blocker remains. External required-status access, real
provider/outcome studies and publication/deployment remain explicitly outside
this completed cloud implementation.

## Post-review fixes (2026-10-28)

An independent review of the draft PR, plus a rerun of the engineering
maturity checker against main, led to these follow-up changes:

- The S1 `Changed-surface contracts` CI step still called the deleted
  `scripts/generate-skill-capsules.py`, so every S1 PR would have failed the
  protected `validate` check. That line is removed; full tiers never ran it.
- The v3 rename of `test_projection_failure_recovers_and_tampering_fails_closed`
  dropped the token that maturity fact L15 scans for, which lowered the loop
  score below main and would fail the owner-run release gate. The original
  test name is restored; the loop score is back to 10.0, as on main.
- `verify_distribution_manifest` again requires the explicit prompt catalog
  for current-schema (1.2) plugins; older manifests are checked only when they
  still ship one. Context-module catalog errors now surface as
  `DistributionError` instead of an uncaught traceback.
- `workflow verify` reports a projection-read failure as itself instead of as
  a run-coordinator lock failure; it still fails closed.
- `pi-agent-poc.yml` no longer has a paths filter. The old filter matched only
  the retired `evals/pi-agent-poc/**` tree, so the retained `probe` would
  otherwise run only when the workflow file itself changes.

Re-run: `python3 scripts/run-behavior-evals.py --with-unittest-discovery` ran
**1143 tests**. The only failure was
`test_inaccessible_suppression_path_fails_closed_in_cli`, which also fails on
the unmodified branch in this container because it runs as root (a `chmod 0`
directory stays readable to root); CI runs as a normal user. The maturity
checker matches main on every fact; P19/P20/H20 need a semantic evidence run
and fail the same way on main.
