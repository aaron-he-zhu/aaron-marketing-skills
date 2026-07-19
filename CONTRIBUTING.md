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
- **behavior conformance** — orchestrates rubric, registry, HTTP, hook, permission, and routing suites offline; an optional NDJSON adapter can evaluate semantic cases without becoming a CI dependency.
- **runtime protocol** — verifies operational run idempotency, event trees/hash chains, immutable snapshots/save points/envelopes, concurrency, bounded resume, Git-ignore/path defenses, and the non-authority boundary.
- **architecture conformance** — checks `references/system-catalog.json` against all 120 paths/frontmatters, plugin order, framework/auditor/registry ownership, transition graphs, L1 dependencies, distribution contracts, and the **symmetry contract** (SYM-01..17: loop/acronym derivation, command selector, registry/gate naming and topology, score surfaces, grouping titles, Scope edges, metadata key set — every violation must be licensed by a `symmetry.deviations` entry, and stale deviations fail).

Build the same minimal payload users receive and run its boundary tests:

```bash
python3 scripts/build-distribution.py --output /tmp/aaron-marketing-dist --plugin
python3 -m unittest tests.test_distribution_builder
```

The allowlist in `references/distribution-files.json` is authoritative. Runtime additions must be declared there; tests, evals, CI, generators, and repository-maintenance documentation must not leak into the plugin payload. Standalone one-folder auditor bundles stay compact and fail closed; regenerate them with `python3 scripts/generate-auditor-runtime.py --write` after changing any bound source. Auto-routing cases are maintained only in `evals/auto-routing-scenarios.source.md`; regenerate the runtime index/eight shards with `python3 scripts/generate-auto-routing-shards.py --write` and never hand-edit the generated views.
- **check-evals** — structural lint over all eval fixtures and auto-routing targets (phase directories and command selectors derive from the system catalog).
- **check-context-budget** — the progressive-disclosure budget as a hard gate: SKILL.md line caps, auditor activation-chain byte budgets, recursive per-reference byte budgets, the largest valid command + index + three-shard `/auto` assembly, and the HOT template's runtime 80-line/25 KB limit.
- **check-routing** — description-routing health as a hard gate: quoted trigger phrases are uniquely owned across all 120 skills, every description carries a `Not for X — use Y` boundary clause, and bare-name handoffs in Next Best Skill blocks resolve to real skills.
- **check-local-links** — every repo-local Markdown link target must resolve inside the repo.
- **check-pii** — scans for committed PII. Enable the repository pre-commit hook once
  per clone with `git config core.hooksPath .githooks`; CI independently scans every
  tracked index blob with `python3 scripts/check-pii.py --tracked`.
- **check-stdlib-only** — enforces the zero-dependency Python-stdlib rule for connector helpers, including the Paid-Ads keyed-API red line (no keyed paid-ad API calls baked into skills).

### 6. Update tracking files

After adding or updating a skill, keep these **10 tracking surfaces** in sync. **This list is authoritative** — `CLAUDE.md` and `AGENTS.md` point here instead of restating it, so update this list if the set changes.
- `references/system-catalog.json` — canonical layer/order/phase/path/auditor/registry/distribution topology; regenerate `docs/system-architecture.md`
- `VERSIONS.md` — version and date
- `.claude-plugin/plugin.json` — skills array + version
- `marketplace.json` (repo root) — must match plugin.json
- `.claude-plugin/marketplace.json` — **byte-identical mirror** of the root `marketplace.json` (copy it after editing the root)
- `README.md` — skills table + version badge
- `CLAUDE.md` — category table + version
- `AGENTS.md` — name/count line + framework item/dimension counts (CORE-EEAT / CITE / STAR / ROAS / SEND / RAMP / ECHO / TALE)
- `docs/README.zh.md` — Chinese README: the 120 · 16 / 16 / 16 / 16 / 16 / 16 / 16 / 8 counts (skills / SEO-GEO / influencer / paid ads / email / launch / social / narrative / protocol) + 8 commands + version badge. The 8 additional localized READMEs (`docs/README.{de,es,fr,it,ja,ko,pt,zh-Hant}.md`) are now version-locked too — `check-versions.sh` asserts each carries the current `version-<bundle>-orange` badge (the bundle value is read from `plugin.json`, so this never goes stale on a bump).
- `.github/repo-about.json` — the GitHub repo **About** SSOT (sidebar description + topics). The About is *not* read by GitHub directly and *not* editable by the CI token, so it silently drifted on the v13/v14 discipline bumps. Edit the count/disciplines/gates here, then project it onto GitHub with `bash scripts/sync-about.sh --live` (owner-run, needs admin auth). `check-versions.sh` asserts its skill count matches the tree; the weekly `about-drift.yml` sentinel fails red if GitHub drifts from it.

For release bumps, also sync README badges and localized README badges.

**Adding or renaming a skill?** Also add its slug to a grouping in the repo-root `skills.sh.json` — the [skills.sh registry page](https://skills.sh/aaron-he-zhu/aaron-marketing-skills) renders those sections, and CI fails when the groupings don't cover exactly the plugin.json skill set (an ungrouped skill would render below the legacy names at the bottom of the page).

**Cutting a release?** Also (a) sync the downstream repo family: `bash scripts/sync-family.sh` (dry-run drift report), then `bash scripts/sync-family.sh --live` to push the live mirrors — registry, tiers, and banner templates in [docs/repo-family.md](docs/repo-family.md); (b) project the GitHub About: `bash scripts/sync-about.sh` (dry-run), then `bash scripts/sync-about.sh --live`; and (c) distribute to the registries — `bash scripts/registry-status.sh` to see per-skill drift across ClawHub + SkillHub, then `bash scripts/publish-registries.sh --live` (publishes only the behind-set) and `bash scripts/publish-package.sh --live` (the OpenClaw bundle-plugin). Full runbook: [docs/distribution.md](docs/distribution.md). All owner-run (editing external/GitHub/registry state needs auth the CI token lacks). Between releases, the weekly `family-drift.yml` and `about-drift.yml` sentinels fail red if either surface drifts.

**CI enforces this list**: `scripts/check-versions.sh` fails when the bundle version drifts across the system catalog, plugin/marketplace/OpenClaw manifests, root/localized README badges, AGENTS.md, CLAUDE.md, or VERSIONS.md; when any SKILL.md version disagrees with its row; or when `.github/repo-about.json`'s skill count disagrees with the tree. Run it locally before pushing: `bash scripts/check-versions.sh`.

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
