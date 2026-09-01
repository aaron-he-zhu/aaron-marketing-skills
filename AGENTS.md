# AGENTS.md

Guidelines for AI agents working in this repository. For full runtime context, see [CLAUDE.md](CLAUDE.md).

## Repository Overview

- **Name**: aaron-marketing-skills — 120 skills (16 × 7 disciplines + 8 protocol), 7 disciplines + a protocol layer, 8 commands, shared references
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **Current bundle**: 20.1.0
<!-- GENERATED:END release-surface:current-bundle -->
- **Repository**: https://github.com/aaron-he-zhu/aaron-marketing-skills
- **Author**: Aaron He Zhu | **License**: Apache 2.0
- **Specs**: [Agent Skills](https://agentskills.io/specification.md)
- **Cross-agent compatibility**: all 120 skills install on the 70+ SKILL.md hosts served by `npx skills` (which reads the skill declarations from `.claude-plugin/plugin.json` — no mirror directory needed, never add one). Per-agent matrix + degradation rules: [docs/agent-compatibility.md](docs/agent-compatibility.md); CI enforces the discovery count. New/renamed skills must also be added to a grouping in the repo-root `skills.sh.json` (lays out the [skills.sh page](https://skills.sh/aaron-he-zhu/aaron-marketing-skills); CI-enforced coverage).
- **Agent Plugins v1**: the repository root is the authoring SSOT, not a standard install root. Release automation generates a separate Portable Lite archive with flat `skills/<name>/` paths, 120/120 strict Agent Skills, and no `mcp.json`, commands, hooks, connectors, or repository runtime. Never add or commit a generated root `skills/` mirror. Existing Claude, `npx skills`, registry, and host-extension layers remain canonical for their clients. See [docs/agent-plugins-v1.md](docs/agent-plugins-v1.md).
Content-first repository: skills and commands are Markdown; Claude Code hooks use a small Bash runner; zero-dependency Python-stdlib code provides connectors, typed scoring, deterministic context manifests, canonical registry events, non-authoritative operational run events, artifact validation, and CI guards (no pip dependencies). Network mutations are limited to dry-run-by-default `resend.py` and `indexpush.py`, both requiring `--live`. The authoritative topology is [`references/system-catalog.json`](references/system-catalog.json); its generated human view is [`docs/system-architecture.md`](docs/system-architecture.md).

Install instructions live in [README.md](README.md). Keep this file focused on authoring and maintenance rules.

### The system — a four-layer marketing operating system

The bundle is told as a **four-layer marketing operating system**, not a chronological list of peer disciplines. Seven disciplines, four altitudes — a system, not a pile. Canonical logical ordering: **Narrative → SEO/GEO · Social · Email · Paid · Influencer → Launch → Protocol**.

| Layer | Adopt | Disciplines | Cadence |
|-------|-------|-------------|---------|
| **L1 · Strategy** — what we say / who we are | crawl | **Narrative** · TALE | always-on |
| **L2 · Channels** — always-on engines that express the strategy (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · STAR | always-on (influencer episodic-leaning) |
| **L3 · Orchestration** — the time-boxed moment across channels | run | **Product Launch** · RAMP | episodic |
| **L4 · Protocol** — the shared system of record | — | 7 truth registries + working memory · 8 auditor gates · one skill contract | — |

Narrative is the message; the channels are the mediums that express it — remove any one channel and the record is intact; remove Narrative and every channel speaks an unsourced, ungoverned message. Each discipline's 4-phase loop lives inside its layer (Narrative = Trace → Architect → Land → Evaluate).

The strata are the system; the 4×4 shape is how each workflow is drawn. Each discipline is exactly **4 phases × 4 skills = 16** (112 discipline + 8 protocol = **120**). Do not maintain another hand-written inventory here: update the typed system catalog, then run `python3 scripts/generate-system-docs.py --write`. CI checks every path, phase, count, owner, and generated view.

## Skill Format Specifications

### Required Frontmatter

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | 1-64 chars, lowercase a-z, numbers, hyphens. Must match directory name. Lowercase slug `^[a-z0-9][a-z0-9-]*$`. |
| `version` | Yes | Semver string. Must match `metadata.version` and the row in `VERSIONS.md`. |
| `description` | Yes | 1-1024 chars. Include: what it does, trigger phrases, scope boundaries. Optimized for `npx skills find`. |

### Canonical-source Repo-Required / Spec-Optional Frontmatter

The fields below belong in the canonical discipline/phase source and its
existing compatibility channels. The generated Agent Plugins v1 Portable Lite
copy keeps only the pinned Agent Skills field set and normalizes `metadata` to a
string-to-string map; do not weaken the canonical source to imitate that strict
projection.

| Field | Purpose |
|-------|---------|
| `license` | License name (default: Apache-2.0) |
| `compatibility` | Platform list |
| `allowed-tools` | Pre-approved tools (e.g., `WebFetch`) |
| `metadata` | **Single-line strict-JSON object** — OpenClaw's parser reads single-line keys only; the validator fails a YAML block map. `metadata.version` must match top-level `version`. |
| `metadata.author/geo-relevance` | Discovery and categorization. |
| `metadata.discipline` + `metadata.phase` | On every skill (120/120): `discipline` = narrative/seo-geo/influencer/ad/email/launch/social/protocol (`ad` is the Paid Ads/ROAS discipline value); `phase` = lifecycle phase. Uniform routing/clustering tags. |
| `metadata.hermes` | Hermes Agent extension: `{"tags": ["marketing", <discipline>, <phase>], "category": <discipline>}` for `hermes skills browse` filtering. |
| `metadata.openclaw` | OpenClaw extension: `{"emoji": <discipline emoji>, "homepage": <repo URL>}` for the macOS UI. |
| `slug` | SkillHub.cn publishing identity — must match the frontmatter value registered on the platform: prefer `<skill-name>` when owned, otherwise `aaron-<skill-name>` as the conflict fallback (validator-enforced). |
| `displayName` + `summary` | SkillHub.cn listing card: bilingual display name + Chinese one-liner. |
| `when_to_use` | Trigger scenarios for auto-invocation (underscores, not hyphens) |
| `argument-hint` | Argument format hint in command picker |

### Description Best Practices

Start with `Use when the user asks to "..."`, then one sentence on function, then scope boundaries linking related skills.

## Quality Frameworks

See [CLAUDE.md § Quality Frameworks](CLAUDE.md) for details. Summary:
- **CORE-EEAT** (80 items, 8 dimensions): content quality. [Full reference](references/core-eeat-benchmark.md)
- **CITE** (40 items, 4 dimensions): domain authority. [Full reference](references/cite-domain-rating.md)
- **STAR** (S Suitability / T Trust / A Appeal / R Return, SQS arithmetic profile-weighted-mean rollup like ROAS/SEND): influencer marketing. [Full reference](references/star-benchmark.md)
- **ROAS** (R Return / O Offer / A Audience / S Spend-efficiency, RQS arithmetic weighted-mean rollup like CITE): paid ads. [Full reference](references/roas-benchmark.md)
- **SEND** (S Sender-integrity/deliverability / E Engagement / N Nurture-lifecycle / D Direct-response; profile-weighted EQS): email marketing. [Full reference](references/send-benchmark.md)
- **RAMP** (40 stable IDs across R Readiness / A Assets / M Momentum / P Proof; separate preflight/execution/outcome profiles): product launch. [Full reference](references/ramp-benchmark.md)
- **ECHO** (40 stable IDs across E Embeddedness / C Craft / H Hosting / O Observability; separate asset/program profiles): organic social. [Full reference](references/echo-benchmark.md)
- **TALE** (T Truth / A Architecture / L Landing / E Evidence; separate truth/system/effectiveness profiles): brand narrative & messaging. [Full reference](references/tale-benchmark.md)
- Veto items: CORE-EEAT (T04, C01, R10) · CITE (T03, T05, T09) · STAR (STAR-S2/S6, STAR-T1/T2/T3 — always qualify with the framework name) · ROAS (R1/R2/O1/O2/A1) · SEND (S1/S2/N1/D1) · RAMP (R1/A1/M1/P1 — IDs collide with ROAS, always qualify with the framework name) · ECHO (E1/C1/C2/H1/H2/O1 — always qualify with the framework name; ECHO O1 vs ROAS O1, ECHO C1 vs CORE C01) · TALE (T1/A1/L1/E1 — always qualify with the framework name)

## Tool Connector Pattern

Skills use `~~category` placeholders. See [CONNECTORS.md](CONNECTORS.md). Every skill works at Tier 1 (no tools). MCP adds Tier 2/3.

## Inter-Skill Handoff

See [CLAUDE.md § Inter-Skill Handoff](CLAUDE.md). Key fields (per skill-contract §Handoff Summary Format): status, objective, key findings, evidence, assumptions, open loops, recommended next skill — plus `cap_applied` / `raw_overall_score` / `final_overall_score` for the 8 auditor-class gates.

Auditor-class gates: `content-quality-auditor` (CORE-EEAT publish gate), `domain-authority-auditor` (CITE citation-trust gate), `creator-content-auditor` (STAR gate → `memory/audits/influencer/`), `ad-account-auditor` (ROAS gate → `memory/audits/ad/`), `email-quality-auditor` (SEND gate → `memory/audits/email/`), `launch-readiness-auditor` (RAMP lifecycle-profile gate → `memory/audits/launch/`), `social-quality-auditor` (ECHO asset/program gate → `memory/audits/social/`), and `narrative-quality-auditor` (TALE profile gate → `memory/audits/narrative/`). New cross-cutting reference protocols: `humanizer-slop`, the `measurement-protocol` decision protocol, and `platforms/`.

## Git Workflow

- **Branch naming**: `feature/skill-name`, `fix/skill-name`, `docs/description`
- **Conventional Commits**: `feat:`, `fix:`, `docs:`
- **After skill changes**: update the authoritative **10 tracking surfaces** in [CONTRIBUTING.md §6](CONTRIBUTING.md). For release bumps, also sync localized README badges. `scripts/check-versions.sh` (CI) fails on any drift — run it locally after syncing.
- **Adding a connector**: follow [docs/connector-playbook.md](docs/connector-playbook.md) end to end — qualify (category / connector-vs-recipe / safety class), verify against primary docs + a live call, implement to house style, offline-test the pure builders, wire skills by the differentiation rule, hit the six doc touchpoints, track, regress, record.
- **Use `references/` for detail** — keep `SKILL.md` focused. Auditor-class skills `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT) and keep only their framework-specific §2 worked examples, §3 guardrails, and §5 translation inline.
- **Validate**: `./scripts/validate-skill.sh <category>/<skill-name>` before release PRs. CI guards: `golden-math` (8 frameworks), strict 734-case `check-evals` plus credential-free smoke/change-aware/nightly profile planning, generated auditor prompt-contract drift, typed route/run/audit-loop tests for event-first recovery, selected-ancestry closure, bounded convergence, and terminal-slot preservation, `check-local-links`, `check-pii`, `check-stdlib-only` (incl. the Paid-Ads keyed-API red line), `check-context-budget` (SKILL.md/auditor-activation/recursive-reference and assembled `/auto` byte budgets), `check-routing` (trigger uniqueness, boundary clauses, bare-name handoff resolution), plus the `check-architecture.py` symmetry contract (conform-or-declared; stale deviations fail).

## Writing Style

- Direct, instructional, second person
- Bold key terms on first use
- Code blocks for commands/templates; tables for structured data
- One skill per file; put extras in `references/`
