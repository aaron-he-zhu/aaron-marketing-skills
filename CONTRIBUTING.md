# Contributing

Thanks for your interest in contributing! This guide covers adding skills, improving existing ones, and submitting changes.

## Requesting a Skill

[Open a Skill Request issue](https://github.com/aaron-he-zhu/aaron-marketing-skills/issues/new?template=skill-request.yml) if you have an idea but don't want to build it yourself.

## Adding a New Skill

### 1. Choose the correct category

| Category | Directory | Use when the skill... |
|----------|-----------|----------------------|
| Narrative | `narrative/<phase>/` | Traces, architects, lands, and proves brand narrative & messaging (TALE loop: trace/architect/land/evaluate) |
| SEO/GEO | `seo-geo/<phase>/` | Surveys demand, implements content/markup, tunes quality/tech, evaluates authority & rankings (SITE loop: survey/implement/tune/evaluate) |
| Social | `social/<phase>/` | Plans, crafts, hosts, and measures organic social (ECHO loop: explore/craft/host/observe) |
| Email | `email/<phase>/` | Grows, sends, and audits email programs (SEND loop: setup/engage/nurture/deliver) |
| Paid Ads | `ad/<phase>/` | Builds, audits, and scales paid-ad campaigns (ROAS loop: research/orchestrate/activate/scale) |
| Influencer | `influencer/<phase>/` | Scouts audiences/creators, targets campaigns, activates outreach & the STAR gate, reports ROI (STAR loop: scout/target/activate/report) |
| Launch | `launch/<phase>/` | Plans, gates, executes, and proves product launches (RAMP loop: research/assemble/mobilize/prove) |
| Protocol | `protocol/` | Cross-cutting layer (7 truth registries: entity/creator/claims/consent/launch/channel/narrative + memory) — shared across disciplines |

### 2. Create the skill directory

```bash
mkdir -p <category>/<skill-name>
```

Directory name: 1-64 chars, lowercase `a-z`, numbers, hyphens only. No leading/trailing/consecutive hyphens.

### 3. Create `SKILL.md` with required frontmatter

```yaml
---
name: your-skill-name
slug: aaron-your-skill-name
displayName: "Your Skill Name · 中文名"
summary: "一句话中文简介(SkillHub.cn 列表卡片)"
version: "1.0.0"
description: 'Use when the user asks to "[trigger]". [What it does]. For [related task], see [other-skill].'
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "[One line on when this skill applies — underscores in the key, not hyphens]"
argument-hint: "<main-input> [--optional-flag]"
metadata: {"author": "your-github-username", "version": "1.0.0", "discipline": "seo-geo", "phase": "survey", "geo-relevance": "high|medium|low", "hermes": {"tags": ["marketing", "seo-geo", "survey"], "category": "seo-geo"}, "openclaw": {"emoji": "🔍", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---
```

All eleven keys above (plus top-level `homepage`) appear on every shipped skill. The only sanctioned *extra* top-level keys are `class: auditor` (the 8 gate skills only) and `allowed-tools` (skills that fetch URLs, e.g. `WebFetch`). The `metadata` key set is fixed: `author` / `version` / `discipline` / `phase` / `geo-relevance` / `hermes` / `openclaw` — no other keys.

The `name` field must match the directory name exactly. `metadata` must be a **single-line strict-JSON object** (valid YAML flow mapping) — OpenClaw's frontmatter parser reads single-line keys only, and the validator fails a YAML block map. In single-quoted scalars, double any literal apostrophe (`designer''s`). Keep the `hermes` (tags/category) and `openclaw` (emoji/homepage) host extensions in step with the skill's discipline. The `slug`/`displayName`/`summary` trio is the [SkillHub.cn](https://skillhub.cn) publishing contract — `slug` must be the platform-owned frontmatter slug (`<skill-name>` when available, otherwise `aaron-<skill-name>` as the conflict fallback; validator-enforced), `displayName` bilingual, `summary` a Chinese one-liner.

### 4. Write effective instructions

Use the compact shared skeleton from `references/skill-contract.md`: `Quick Start`, `Skill Contract`, `Handoff Summary`, `Data Sources`, `Instructions`, `Reference Materials`, and `Next Best Skill`. Optional sections such as `What This Skill Does`, `Example`, `Tips for Success`, `Save Results`, and `Validation Checkpoints` are welcome when they improve execution quality. Put detailed references in the skill's `references/` subdirectory.

Auditor-class skills are the exception: repository mode reads the root typed runtime; each auditor also ships a generated immutable `references/auditor-runtime.md` for standalone installs. Keep only framework-specific examples, guardrails, and veto translations inline. Eight skills are auditor-class gate consumers, each scored against one framework and writing to its own audit sink:

| Auditor-class skill | Framework | Audit sink |
|---------------------|-----------|------------|
| `content-quality-auditor` | CORE-EEAT (publish readiness) | `memory/audits/content/` |
| `domain-authority-auditor` | CITE (citation trust) | `memory/audits/domain/` |
| `creator-content-auditor` | STAR SQS (influencer content gate) | `memory/audits/influencer/` |
| `ad-account-auditor` | ROAS RQS (paid-ads gate) | `memory/audits/ad/` |
| `email-quality-auditor` | SEND EQS (email SEND gate) | `memory/audits/email/` |
| `launch-readiness-auditor` | RAMP lifecycle-profile gate | `memory/audits/launch/` |
| `social-quality-auditor` | ECHO asset/program-profile gate | `memory/audits/social/` |
| `narrative-quality-auditor` | TALE truth/system/effectiveness gate | `memory/audits/narrative/` |

Cross-cutting reference protocols apply across disciplines: the humanizer-slop protocol, the measurement-protocol decision protocol, and the per-channel `platforms/` reference packs. These stay references (not skills) by design — each is consumed as a pre-handoff sub-step inside discipline skills, so promoting one to a standalone skill would duplicate that step.

### 5. Validate

```bash
./scripts/validate-skill.sh <category>/<skill-name>
```

CI runs additional guards beyond the per-skill validator:
- **golden behavior** — runs every typed profile through the real catalog/scorer, including Unknown, one-veto, multi-veto, cap, and STAR rollup boundaries; it never regex-scrapes Markdown formulas.
- **behavior conformance** — orchestrates rubric, registry, HTTP, hook, permission, and routing suites offline; strict smoke/change-aware/nightly profiles select 24 to 700 provenance-bound semantic cases, while optional protocol-v2 adapters remain outside credential-free CI.
- **runtime protocol** — verifies operational run idempotency, event trees/hash chains, immutable snapshots/save points/envelopes, concurrency, bounded resume, Git-ignore/path defenses, and the non-authority boundary.
- **audit outer loop** — verifies event-first v2 anchors and same-request step recovery, verification-only public binding, selected-ancestry/sibling-isolated closure, a reserved terminal event slot, strict success versus bounded failed/aborted escape, exact active-loop coverage for waiting/needs-input/blocked, lease fencing, monotonic time, optimistic concurrency, separate retry/cycle/byte/deadline budgets, audit identity and observation-time provenance, strict convergence, exact-byte deduplication, graph-wide exact-hash linkage, and control-escaped terminal output without executing interventions.
- **architecture conformance** — checks `references/system-catalog.json` against all 120 paths/frontmatters, plugin order, framework/auditor/registry ownership, transition graphs, L1 dependencies, distribution contracts, and the **symmetry contract** (SYM-01..17: loop/acronym derivation, command selector, registry/gate naming and topology, score surfaces, grouping titles, Scope edges, metadata key set — every violation must be licensed by a `symmetry.deviations` entry, and stale deviations fail).
- **five-engineering maturity** — validates the closed 100-control Prompt/Context/Harness/Loop/Graph rubric and report contract. Before release, run `python3 scripts/check-engineering-maturity.py --semantic-evidence-run-id <uuid>` against a complete current-source real-provider smoke run; every dimension must reach 95/100 and pass its hard gates.

Build the three physical plugin ceilings users receive and run their boundary
tests. A fresh project resolves to Lite in every archive; the archive controls
only the maximum available capability:

```bash
python3 scripts/build-release-assets.py \
  --source-repo /path/to/aaron-marketing-skills \
  --source-repository aaron-he-zhu/aaron-marketing-skills \
  --source-commit <exact-40-hex-release-commit> \
  --version 19.0.0 \
  --output /private/path/v19.0.0-release-assets
python3 -m unittest tests.test_distribution_builder tests.test_release_assets tests.test_publish_release tests.test_publish_state
```

The allowlist in `references/distribution-files.json` is authoritative. Runtime additions must be declared there; tests, evals, CI, generators, and repository-maintenance documentation must not leak into the plugin payload. The builder rejects symlinks, special files, and multiply linked files and emits a complete SHA-256 manifest with its physical profile ceiling. To meet the Governed hard budget, the builder deterministically replaces the expanded `references/skill-contracts/` tree with `references/skill-contracts.pack.json.gz`; the resolver accepts that derived pack only after bounded decompression and exact record/aggregate hash checks. Keep the expanded generated tree in source control for review and CI, and never hand-edit the pack. Bare `--plugin` is a deprecated Governed-ceiling alias through v20; contributor and release commands must name `--profile`. The release-asset builder privately exports one exact Git commit, builds Lite/Pro/Governed independently, emits canonical fixed-root tarballs plus `SHA256SUMS` and `release-assets.json`, safely unpacks them, and verifies each profile/provenance-bound manifest against a fresh build of that same commit. Run it twice into new directories and require all five outputs to be byte-identical before release. Every live release publisher/projector accepts only a clean commit reachable from successfully refreshed `origin/main`; per-skill and built-package publishers package a private Git export of that pinned commit and verify repository/commit-bound manifests before upload. Dry-runs do not apply the live clean-tree gate. Standalone one-folder auditor bundles stay compact and fail closed; regenerate them with `python3 scripts/generate-auditor-runtime.py --write` after changing any bound source. Auto-routing cases are maintained only in `evals/auto-routing-scenarios.source.md`; regenerate the runtime index/eight shards with `python3 scripts/generate-auto-routing-shards.py --write` and never hand-edit the generated views. Auditor prompt contracts are maintenance/evaluation artifacts derived from the system/framework catalogs and bound sources; regenerate them with `python3 scripts/generate-auditor-prompt-contracts.py --write` and never hand-edit `references/prompt-contracts/`.
- **check-evals** — strict case parsing plus structural lint over all 700 authored/generated semantic fixtures and their real-evidence bindings (phase directories and command selectors derive from the system catalog).
- **check-context-budget** — the progressive-disclosure budget as a hard gate: SKILL.md line caps, auditor activation-chain byte budgets, recursive per-reference byte budgets, the largest valid command + index + three-shard `/auto` assembly, and the HOT template's runtime 80-line/25 KB limit.
- **check-routing** — description-routing health as a hard gate: quoted trigger phrases are uniquely owned across all 120 skills, every description carries a `Not for X — use Y` boundary clause, and bare-name handoffs in Next Best Skill blocks resolve to real skills.
- **check-local-links** — every repo-local Markdown link target must resolve inside the repo.
- **check-pii** — scans for committed PII. Enable the repository pre-commit hook once
  per clone with `git config core.hooksPath .githooks`; CI independently scans every
  tracked index blob with `python3 scripts/check-pii.py --tracked`.
- **check-stdlib-only** — enforces the zero-dependency Python-stdlib rule for connector helpers, including the Paid-Ads keyed-API red line (no keyed paid-ad API calls baked into skills).

### 6. Update tracking files

After adding or updating a skill, keep these **10 tracking surfaces** in sync. **This list is authoritative** — `CLAUDE.md` and `AGENTS.md` point here instead of restating it, so update this list if the set changes.

- `references/system-catalog.json` — canonical layer/order/phase/path/auditor/registry/distribution topology and release version; regenerate `docs/system-architecture.md`
- `VERSIONS.md` — version and date
- `references/publication-metadata.json` — editable public identity, marketplace, About, skills.sh grouping, locale, and marker-template metadata
- `.claude-plugin/plugin.json` — generated skills array + version
- `marketplace.json` and `.claude-plugin/marketplace.json` — generated byte-identical marketplace projections
- `openclaw.plugin.json` — generated OpenClaw identity/version projection
- `README.md` — authored content plus generated version/current-bundle marker regions
- `CLAUDE.md`, `AGENTS.md`, and `SECURITY.md` — authored policy plus generated current-release marker regions
- `docs/README.{zh,de,es,fr,it,ja,ko,pt,zh-Hant}.md` — authored localized content plus generated version/current-bundle marker regions
- `.github/repo-about.json` and `skills.sh.json` — generated About and grouped-discovery projections; project About to GitHub with `bash scripts/sync-about.sh --live`

Do not hand-edit a generated JSON projection or marker body. After changing the
catalog/publication sources, run
`python3 scripts/generate-release-surfaces.py --write`, then `--check`. For a
coordinated release, use the dry-run-by-default
`python3 scripts/bump-release.py --to X.Y.Z --date YYYY-MM-DD --align-all-skills`
transaction before its `--write` form; this updates only current product
bindings and leaves historical/schema/protocol versions intact.

**Adding or renaming a skill?** Also add its slug to a grouping in the repo-root `skills.sh.json` — the [skills.sh registry page](https://skills.sh/aaron-he-zhu/aaron-marketing-skills) renders those sections, and CI fails when the groupings don't cover exactly the plugin.json skill set (an ungrouped skill would render below the legacy names at the bottom of the page).

**Cutting a release?** The profile release gate additionally requires private,
pseudonymous real-project evidence bound to the exact RC commit: at least 14
pilot, 70 randomized paired Lite/Governed, and 28 shadow projects, distributed
2/10/4 per discipline. Two blind reviewers assess every project; simulated
evals are not eligible. Keep all evidence outside Git and run
`python3 scripts/verify-profile-outcomes.py /private/path/evidence.json
--source-commit "$RC_COMMIT" --release-candidate 19.0.0-rc.N
--evidence-manifest /private/path/manifest.json --receipt
/private/path/receipt.json --json`. The verifier refuses duplicated project,
brief, or evidence identities, requires balanced randomized order, and checks
the attested private-manifest digest. Keep the project-data-free receipt private
and pass its path as `AARON_RELEASE_RECEIPT` to live publishers.
No evidence or a failed threshold means no tag and no live publisher. Then (a)
run `python3 scripts/create-github-release.py` as a network-free preview and its
`--live --receipt <private-receipt> --asset-dir <verified-assets>` form to create
or read-only verify the immutable tag/release; (b) sync the downstream
repo family with `sync-family.sh`; (c) project GitHub About with
`sync-about.sh`; and (d) publish the Governed-ceiling/Lite-default bundle and
per-skill registry records. Full gate, rollback, and distribution order:
[docs/distribution.md](docs/distribution.md). All external mutations are
owner-run. Between releases, the weekly `family-drift.yml` and
`about-drift.yml` sentinels fail red if either surface drifts.

**CI enforces this list**: the release-surface generator detects projection
drift, and `scripts/check-versions.sh` validates product-version bindings and
each skill row. A coordinated cut additionally runs
`bash scripts/check-versions.sh --release-all-current`, which requires exactly
120/120 skills on the same bundle version/date. Run both locally before pushing.

**Adding a connector?** Follow [docs/connector-playbook.md](docs/connector-playbook.md) — the end-to-end pipeline (qualify → verify → implement → test → wire → document → track → regress → record) with the safety-class gate table and the connector-vs-recipe decision rule.

## Improving Existing Skills

Keep changes focused. Bump both top-level `version` and `metadata.version` together. Update `VERSIONS.md`. Put new reference docs in the skill's `references/` subdirectory.

## Craft Checklist

Beyond the mechanical checks, every skill should pass the senior self-test from [skill-contract.md §Skill Authoring Discipline](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/skill-contract.md):

- [ ] **Simplicity** — would a senior engineer call this skill overcomplicated? Every section traces to the user's task.
- [ ] **Boundary** — the `description` ends with a `Not for X — use Y` clause so it doesn't compete with a sibling skill.
- [ ] **Verifiable** — the Skill Contract states a `Done when:` with checkable conditions.
- [ ] **Honest data** — Instructions tell the model to label Measured / User-provided / Estimated and never invent numbers.
- [ ] **Surgical handoff** — Next Best Skill points to exactly one primary move.

## Quality Checklist (mechanical)

Before submitting a PR:

- [ ] `name` matches directory name (lowercase slug `^[a-z0-9][a-z0-9-]*$`)
- [ ] Top-level `version` is present and matches `metadata.version` plus `VERSIONS.md`
- [ ] `description` includes trigger phrases AND scope boundaries (≤1024 chars)
- [ ] Shared compact section contract present (`validate-skill.sh` checks this)
- [ ] Validator passes: `./scripts/validate-skill.sh <category>/<skill-name>`
- [ ] Uses `~~placeholder` pattern for tool references
- [ ] `allowed-tools: WebFetch` added if skill fetches live URLs
- [ ] Includes validation checkpoints and at least one example
- [ ] All tracking and release files updated; plugin.json and marketplace.json arrays identical
- [ ] `.claude-plugin/marketplace.json` byte-identical to repo-root copy

## Submitting

- Fork, create a `feature/your-skill-name` branch, and submit a PR.

## Code of Conduct

Be respectful, constructive, and focused on making the library better for everyone.
