# AGENTS.md

Guidelines for AI agents working in this repository. For full runtime context, see [CLAUDE.md](CLAUDE.md).

## Repository Overview

- **Name**: aaron-marketing-skills — 69 skills (16 SEO/GEO + 16 influencer + 16 paid + 16 email + 5 protocol), 4 disciplines + a protocol layer, 5 commands, shared references
- **Repository**: https://github.com/aaron-he-zhu/aaron-marketing-skills
- **Author**: Aaron He Zhu | **License**: Apache 2.0
- **Specs**: [Agent Skills](https://agentskills.io/specification.md)
Content-first repository: skills and commands are Markdown; Claude Code hooks use a small Bash runner; `scripts/connectors/` holds zero-dependency Python-stdlib data helpers (no pip deps). Primary directories: SEO/GEO `research/`, `build/`, `optimize/`, `monitor/`; protocol layer `protocol/`; influencer/IMPACT `discover/`, `plan/`, `activate/`, `measure/`; paid ads `paid/research`, `paid/orchestrate`, `paid/activate`, `paid/scale`; email `email/setup`, `email/engage`, `email/nurture`, `email/deliver`; plus `commands/`, `references/`, `scripts/connectors/`.

Install instructions live in [README.md](README.md). Keep this file focused on authoring and maintenance rules.

### New skills (v12.0.0) — 4×4 symmetry refactor

The bundle is now four disciplines of exactly **4 phases × 4 skills = 16** each (64 discipline + 5 protocol = **69**). No capability was deleted — reductions are mode-preserving merges. Full per-phase listings are in [CLAUDE.md § Skills by Phase](CLAUDE.md).

**SEO/GEO (16)** — merges: `content-writer` (seo-content-writer + content-refresher) · `serp-markup-builder` (meta-tags-optimizer + schema-markup-generator) · `page-play-builder` (programmatic + parasite + comparison + local SEO, 4 modes) · `site-structure-optimizer` (internal-linking-optimizer + site-architecture) · `performance-monitor` (performance-reporter + alert-manager) · `offsite-signal-analyzer` (backlink-analyzer + ai-traffic).

**Influencer/IMPACT (16)** — 6 phases → 4 (insight + map → **discover**, activate + convert → **activate**, track → **measure**). Merges: `audience-mapper` (audience-analyzer + niche-researcher) · `content-amplifier` (content-amplifier + ugc-repurposer). Moves: `competitor-tracker` (map → plan) · `landing-optimizer` (convert → measure).

**Paid/ROAS (16)** — new: `search-term-miner`, `product-feed-optimizer` (research) · `bid-strategy-planner`, `landing-experience-checker` (orchestrate) · `placement-exclusion-manager`, `conversion-value-mapper` (activate) · `budget-pacing-monitor`, `fatigue-frequency-manager` (scale).

**Email/SEND (16)** — new: `list-hygiene-monitor` (setup) · `subject-line-lab`, `email-render-builder`, `dynamic-content-personalizer` (engage) · `preference-frequency-manager`, `reactivation-specialist` (nurture) · `inbox-placement-monitor`, `cold-outbound-sequencer` (deliver). Renamed: `send-experiment-designer` (was send-test-designer).

### New skills (v11.0.0)

Sixteen skills added across the 38 → 54 expansion (six SEO/GEO + four paid in v11, then four more paid in the Balanced paid-ads expansion, plus the two protocol truth registries). Full per-phase listings are in [CLAUDE.md § Skills by Phase](CLAUDE.md). Paid phases are directories under `paid/` following the ROAS loop (paid/research, paid/orchestrate, paid/activate, paid/scale).

| Discipline | Phase | Skill |
|------------|-------|-------|
| SEO/GEO | Build | `programmatic-seo` |
| SEO/GEO | Build | `parasite-seo` |
| SEO/GEO | Build | `comparison-page-builder` |
| SEO/GEO | Build | `local-seo` |
| SEO/GEO | Optimize | `site-architecture` |
| SEO/GEO | Monitor | `ai-traffic` |
| Paid Ads | Research (structure + search-term mining) | `campaign-architect` |
| Paid Ads | Research (audiences) | `audience-segment-builder` |
| Paid Ads | Orchestrate (creative) | `ad-creative-builder` |
| Paid Ads | Orchestrate (experiment design) | `ad-test-designer` |
| Paid Ads | Activate (auditor-class gate; ROAS RQS + launch go/no-go) | `ad-account-auditor` |
| Paid Ads | Activate (conversion-signal QA) | `conversion-signal-qa` |
| Paid Ads | Scale (readback) | `paid-measurement-loop` |
| Paid Ads | Scale (attribution de-dup / incrementality) | `attribution-reconciler` |
| Protocol | Truth registry (canonical creator roster/dossier — influencer SSOT) | `creator-registry` |
| Protocol | Truth registry (offer & claim-substantiation record — paid SSOT) | `offer-claims-registry` |

## Skill Format Specifications

### Required Frontmatter

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | 1-64 chars, lowercase a-z, numbers, hyphens. Must match directory name. Lowercase slug `^[a-z0-9][a-z0-9-]*$`. |
| `version` | Yes | Semver string. Must match `metadata.version` and the row in `VERSIONS.md`. |
| `description` | Yes | 1-1024 chars. Include: what it does, trigger phrases, scope boundaries. Optimized for `npx skills find`. |

### Repo-Required / Spec-Optional Frontmatter

| Field | Purpose |
|-------|---------|
| `license` | License name (default: Apache-2.0) |
| `compatibility` | Platform list |
| `allowed-tools` | Pre-approved tools (e.g., `WebFetch`) |
| `metadata.author/version/geo-relevance/tags/triggers` | Discovery and categorization. `metadata.version` must match top-level `version`. |
| `metadata.discipline` + `metadata.phase` | On every skill (69/69): `discipline` = seo-geo/influencer/paid/email/protocol; `phase` = lifecycle phase. Uniform routing/clustering tags. |
| `when_to_use` | Trigger scenarios for auto-invocation (underscores, not hyphens) |
| `argument-hint` | Argument format hint in command picker |

### Description Best Practices

Start with `Use when the user asks to "..."`, then one sentence on function, then scope boundaries linking related skills.

## Quality Frameworks

See [CLAUDE.md § Quality Frameworks](CLAUDE.md) for details. Summary:
- **CORE-EEAT** (80 items, 8 dimensions): content quality. [Full reference](references/core-eeat-benchmark.md)
- **CITE** (40 items, 4 dimensions): domain authority. [Full reference](references/cite-domain-rating.md)
- **C³** (9 dimensions, Creator/Content/Campaign on ACE/ART/ROI, CVI geometric rollup): influencer marketing. [Full reference](references/c3-benchmark.md)
- **ROAS** (R Return / O Offer / A Audience / S Spend-efficiency, RQS arithmetic weighted-mean rollup like CITE): paid ads. [Full reference](references/roas-benchmark.md)
- **SEND** (S Sender-integrity/deliverability / E Engagement / N Nurture-lifecycle / D Direct-response, EQS arithmetic goal-weighted-mean rollup like ROAS): email marketing. [Full reference](references/send-benchmark.md)
- Veto items: CORE-EEAT (T04, C01, R10) · CITE (T03, T05, T09) · C³ (ACE A2/C1/E2, ART T1/T2) · ROAS (R1/R2/O1/O2/A1) · SEND (S1/S2/N1/D1)

## Tool Connector Pattern

Skills use `~~category` placeholders. See [CONNECTORS.md](CONNECTORS.md). Every skill works at Tier 1 (no tools). MCP adds Tier 2/3.

## Inter-Skill Handoff

See [CLAUDE.md § Inter-Skill Handoff](CLAUDE.md). Key fields (per skill-contract §Handoff Summary Format): status, objective, key findings, evidence, assumptions, open loops, recommended next skill — plus `cap_applied` / `raw_overall_score` / `final_overall_score` for the 5 auditor-class gates.

Auditor-class gates: `content-quality-auditor` (CORE-EEAT publish gate), `domain-authority-auditor` (CITE citation-trust gate), `content-reviewer` (C³ ART gate → `memory/audits/influencer/`), `ad-account-auditor` (ROAS gate → `memory/audits/paid/`), and `email-quality-auditor` (SEND gate → `memory/audits/email/`). New cross-cutting reference protocols: `humanizer-slop`, the `measurement-protocol` decision protocol, and `platforms/`.

## Git Workflow

- **Branch naming**: `feature/skill-name`, `fix/skill-name`, `docs/description`
- **Conventional Commits**: `feat:`, `fix:`, `docs:`
- **After skill changes**: update the tracking files — the authoritative 8-file list is in [CONTRIBUTING.md §6](CONTRIBUTING.md) (VERSIONS.md, `.claude-plugin/plugin.json`, root `marketplace.json` + its `.claude-plugin/marketplace.json` mirror, README.md, CLAUDE.md, AGENTS.md, docs/README.zh.md). For release bumps, also sync localized README badges.
- **Use `references/` for detail** — keep `SKILL.md` focused. Auditor-class skills `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT) and keep only their framework-specific §2 worked examples, §3 guardrails, and §5 veto-ID rows inline.
- **Validate**: `./scripts/validate-skill.sh <category>/<skill-name>` before release PRs. CI guards: `golden-math` (5 frameworks), `check-evals`, `check-pii`, `check-stdlib-only` (incl. the Paid-Ads keyed-API red line).

## Writing Style

- Direct, instructional, second person
- Bold key terms on first use
- Code blocks for commands/templates; tables for structured data
- One skill per file; put extras in `references/`
