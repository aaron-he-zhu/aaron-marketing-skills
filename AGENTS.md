# AGENTS.md

Guidelines for AI agents working in this repository.

## Repository Overview

- **Name**: seo-geo-claude-skills
- **Repository**: https://github.com/aaron-he-zhu/seo-geo-claude-skills
- **Author**: Aaron He Zhu
- **License**: Apache 2.0
- **Skills Specification**: [Agent Skills](https://agentskills.io/specification.md)

This is a content-only repository (no executable code). It contains 20 SEO and GEO skills, 15 one-shot commands, and shared reference documents for AI coding agents.

## Repository Structure

```
seo-geo-claude-skills/
├── research/                         # Phase 1: Market Research (4 skills)
│   ├── keyword-research/SKILL.md
│   ├── competitor-analysis/SKILL.md
│   ├── serp-analysis/SKILL.md
│   └── content-gap-analysis/SKILL.md
├── build/                            # Phase 2: Content Creation (4 skills)
│   ├── seo-content-writer/SKILL.md
│   ├── geo-content-optimizer/SKILL.md
│   ├── meta-tags-optimizer/SKILL.md
│   └── schema-markup-generator/SKILL.md
├── optimize/                         # Phase 3: Improvement (4 skills)
│   ├── on-page-seo-auditor/SKILL.md
│   ├── technical-seo-checker/SKILL.md
│   ├── internal-linking-optimizer/SKILL.md
│   └── content-refresher/SKILL.md
├── monitor/                          # Phase 4: Tracking (4 skills)
│   ├── rank-tracker/SKILL.md
│   ├── backlink-analyzer/SKILL.md
│   ├── performance-reporter/SKILL.md
│   └── alert-manager/SKILL.md
├── cross-cutting/                    # Protocol layer across all phases (4 skills)
│   ├── content-quality-auditor/SKILL.md
│   ├── domain-authority-auditor/SKILL.md
│   ├── entity-optimizer/SKILL.md
│   └── memory-management/SKILL.md
├── commands/                         # 15 one-shot command files
├── references/                       # Shared reference documents
│   ├── core-eeat-benchmark.md        # 80-item content quality framework
│   ├── cite-domain-rating.md         # 40-item domain authority framework
│   ├── skill-contract.md             # Shared skill contract and handoff format
│   └── state-model.md                # Shared memory layout and ownership rules
├── scripts/                          # Developer utilities
│   └── validate-skill.sh             # Validate SKILL.md spec compliance
├── .claude-plugin/                   # Claude Code plugin manifest
│   └── plugin.json
├── marketplace.json                  # skills.sh marketplace manifest
├── .mcp.json                         # Pre-configured MCP servers
├── CLAUDE.md                         # Claude Code auto-loaded agent context
├── AGENTS.md                         # This file (skills.sh convention)
├── CONNECTORS.md                     # Tool placeholder mappings
├── CONTRIBUTING.md                   # Contribution guide
├── VERSIONS.md                       # Version tracking for all skills
├── README.md                         # Main documentation
└── LICENSE                           # Apache 2.0
```

Each skill directory contains a `SKILL.md` and optionally a `references/` subdirectory with skill-specific templates, rubrics, and checklists.

## Skill Categories

| Category | Directory | Purpose | Skills |
|----------|-----------|---------|--------|
| Research | `research/` | Market analysis before content creation | keyword-research, competitor-analysis, serp-analysis, content-gap-analysis |
| Build | `build/` | Content creation optimized for search and AI | seo-content-writer, geo-content-optimizer, meta-tags-optimizer, schema-markup-generator |
| Optimize | `optimize/` | Improve existing content and technical health | on-page-seo-auditor, technical-seo-checker, internal-linking-optimizer, content-refresher |
| Monitor | `monitor/` | Track performance and catch issues | rank-tracker, backlink-analyzer, performance-reporter, alert-manager |
| Cross-cutting | `cross-cutting/` | Protocol layer across all phases | content-quality-auditor, domain-authority-auditor, entity-optimizer, memory-management |

## Hooks & Automation

This library uses prompt-based hooks to automate cross-skill coordination. All hooks are prompt instructions in `hooks/hooks.json` — no shell scripts, no executables.

| Event | Matcher | Behavior |
|-------|---------|----------|
| SessionStart | startup | Load `memory/hot-cache.md` as project context; remind open loops older than 7 days |
| UserPromptSubmit | all | Keep hot-cache priorities in mind silently |
| PostToolUse | Write, Edit | Recommend content-quality-auditor after content writing |
| Stop | all | Prompt to save findings to `memory/`; auto-save veto issues to hot-cache |
| FileChanged | hot-cache.md | Warn if hot-cache exceeds 80 lines or 25KB |

### Hook Design Principles

- **Prompt-based only** — no shell scripts, no executables, no dependencies
- **Transparent** — user can see and override any hook behavior
- **Non-blocking** — hooks suggest actions, they never force them

### Temperature Memory Model

The library uses a three-tier memory model. See [references/state-model.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) for full specification.

| Tier | Location | Capacity | Lifecycle |
|------|----------|----------|-----------|
| HOT | `memory/hot-cache.md` | 80 lines | Auto-loaded every session; demotes after 30 days unreferenced |
| WARM | `memory/<category>/` | 200 lines/file | On-demand loading; promotes to HOT on high frequency; demotes after 90 days |
| COLD | `memory/archive/` | Unlimited | Query-only via memory-management; never auto-deleted |

## Skill Format Specifications

All skills are compatible with three skill ecosystems:

| Ecosystem | Spec | Install |
|-----------|------|---------|
| **ClawHub** | [openclaw/clawhub skill-format.md](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md) | `clawhub install aaron-he-zhu/<skill-name>` — [browse all 20](https://clawhub.ai/u/aaron-he-zhu) |
| **Agent Skills** | [agentskills.io/specification.md](https://agentskills.io/specification.md) | `npx skills add aaron-he-zhu/seo-geo-claude-skills` |
| **Vercel Labs skills** | [vercel-labs/skills find-skills](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md) | `npx skills find seo` |

### Required Frontmatter

Every `SKILL.md` must have YAML frontmatter with:

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | 1-64 chars, lowercase a-z, numbers, hyphens only. Must match directory name exactly. Cannot start/end with hyphen. No consecutive hyphens. Also satisfies ClawHub slug pattern `^[a-z0-9][a-z0-9-]*$`. |
| `description` | Yes | 1-1024 chars. Must include: what it does, when to use it (trigger phrases), and scope boundaries (related skills). Optimized for `npx skills find` (Vercel Labs) discovery. |

### Optional Frontmatter

| Field | Purpose | Ecosystem |
|-------|---------|-----------|
| `license` | License name (default: Apache-2.0) | All |
| `compatibility` | Platform list: Claude Code, skills.sh, ClawHub, Vercel Labs | All |
| `allowed-tools` | Space-delimited pre-approved tools (e.g., `WebFetch`) | Agent Skills |
| `metadata.author` | Skill author | All |
| `metadata.version` | Semantic version | All |
| `metadata.geo-relevance` | GEO optimization relevance (high/medium/low) | This library |
| `metadata.tags` | Searchable keywords | All |
| `metadata.triggers` | Trigger phrases that activate the skill | Agent Skills |
| `metadata.openclaw` | ClawHub runtime declarations (`requires.env`, `requires.bins`) | ClawHub |
| `when_to_use` | Detailed trigger scenarios for auto-invocation (underscores, not hyphens) | Claude Code |
| `argument-hint` | Argument format hint in command picker | All |

### ClawHub Runtime Declaration

Skills declare runtime requirements under `metadata.openclaw` only when they have a hard dependency or a `primaryEnv` signal. Skills with no hard dependencies omit the `openclaw` block entirely.

If a skill requires a specific API key to function at all, declare it:
```yaml
metadata:
  openclaw:
    primaryEnv: AHREFS_API_KEY
    requires:
      env:
        - AHREFS_API_KEY
```

### Description Field Best Practices

The `description` field drives discovery across all three ecosystems (skills.sh, ClawHub search, `npx skills find`). It must include:

1. **When to use** — Start with `Use when the user asks to "..."` followed by trigger phrases
2. **What it does** — One sentence describing the skill's function
3. **Scope boundaries** — `For X, see [other-skill]. For Y, see [another-skill].`

Example:
```yaml
description: 'Use when the user asks to "find keywords", "keyword research", "what should I write about". Discovers high-value keywords with search intent analysis and difficulty assessment. For competitor keywords specifically, see competitor-analysis.'
```

## Quality Frameworks

Two proprietary frameworks power this library's auditing skills:

### CORE-EEAT (80 items, 8 dimensions)
- **C**ontextual Clarity (10 items) — intent alignment, audience targeting
- **O**rganization (10 items) — structure, navigation, readability
- **R**eferenceability (10 items) — quotability, data presentation
- **E**xclusivity (10 items) — original research, unique insights
- **Exp**erience (10 items) — first-hand knowledge, practical advice
- **Exp**ertise (10 items) — depth, accuracy, technical competence
- **A**uthority (10 items) — credentials, recognition, citations
- **T**rust (10 items) — transparency, disclosures, accuracy

Used by: content-quality-auditor, seo-content-writer, geo-content-optimizer, content-refresher, on-page-seo-auditor

Full reference: [references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)

### CITE (40 items, 4 dimensions)
- **C**itation (10 items) — backlink profiles, media mentions
- **I**mpact (10 items) — publishing record, brand recognition
- **T**rust (10 items) — legal compliance, security, policies
- **E**ntity (10 items) — Knowledge Graph presence, consistency

Used by: domain-authority-auditor, backlink-analyzer, competitor-analysis, performance-reporter

Full reference: [references/cite-domain-rating.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/cite-domain-rating.md)

### Veto System
Both frameworks include critical items that can override the overall score:
- CORE-EEAT: T04 (Disclosures), C01 (Intent Alignment), R10 (Content Consistency)
- CITE: T03 (Security), T05 (Policies), T09 (Review Authenticity)

## Tool Connector Pattern

Skills use `~~category` placeholders instead of specific tool names. See [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md) for the full mapping.

### Progressive Enhancement
| Tier | Integration | Experience |
|------|-------------|------------|
| Tier 1 | None | User pastes data manually. Full analysis frameworks still apply. |
| Tier 2 | Basic MCP | Automated data retrieval via connected tools. |
| Tier 3 | Full | Fully automated workflows with multiple tool integrations. |

Every skill works at Tier 1. Tool integration enhances but never gates functionality.

## Installation

| Your tool | Install command |
|-----------|----------------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` |
| **OpenClaw** | `clawhub install aaron-he-zhu/<skill>` · [bundle](https://clawhub.ai/plugins/aaron-seo-geo) |
| **Gemini CLI** | `gemini extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| **Qwen Code** | `qwen extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| **Amp** | `amp skill add aaron-he-zhu/seo-geo-claude-skills` |
| **Kimi Code CLI** | `kimi plugin install https://github.com/aaron-he-zhu/seo-geo-claude-skills.git` |
| **CodeBuddy** | in-app: `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` then `/plugin install aaron-seo-geo` |
| **Cursor / Codex / opencode / Windsurf / Cline / Copilot / [35+ more](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/seo-geo-claude-skills` |

**Git Submodule** (version-pinned):
```bash
git submodule add https://github.com/aaron-he-zhu/seo-geo-claude-skills.git .claude/skills/seo-geo
```

## Checking for Updates

Once per session, agents should check for updates:

1. Fetch `https://raw.githubusercontent.com/aaron-he-zhu/seo-geo-claude-skills/main/VERSIONS.md`
2. Compare remote versions against locally installed skill metadata versions
3. If 2+ skills have updates OR any skill has a major version bump, notify the user:

```
SEO & GEO Skills update available: [list updated skills with old → new versions]
- OpenClaw: clawhub install aaron-he-zhu/<skill-name>  (for each updated skill)
- Other agents: npx skills add aaron-he-zhu/seo-geo-claude-skills
```

4. Do not block the user's workflow for update checks. Notify non-intrusively.

## Inter-Skill Handoff Protocol

When one skill points to its `Next Best Skill`, preserve this context:

| Context | How to Pass |
|---------|------------|
| Objective | State what was analyzed, created, or fixed |
| Key findings / output | Carry forward the highest-signal result |
| Evidence | Include URLs, datasets, or sections reviewed |
| Open loops | Note blockers, missing inputs, or unresolved risks |
| Target keyword | Include in the skill invocation |
| Content type | State explicitly |
| CORE-EEAT scores | Summarize dimension scores (e.g., C:75 O:60 R:80 E:45) |
| CITE scores | Summarize dimension + veto status |
| Priority items | List specific item IDs |
| Content URL | Include for fetch-capable skills |

If `memory-management` is active, prior audit results are automatically available via the hot cache in [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md).

## Git Workflow

When contributing to this repository:

- **Branch naming**: `feature/skill-name`, `fix/skill-name`, `docs/description`
- **Conventional Commits**: `feat: add skill-name skill`, `fix: correct scoring in on-page-seo-auditor`, `docs: update VERSIONS.md`
- **After adding or updating a skill**: Update all 5 tracking files: `VERSIONS.md`, `.claude-plugin/plugin.json` skills array, `marketplace.json` (repo root) skills array (must match plugin.json exactly), `README.md` skills table, `CLAUDE.md` category table
- **If shared behavior changes**: Keep `references/skill-contract.md`, `references/state-model.md`, `AGENTS.md`, `README.md`, and `CLAUDE.md` aligned
- **Keep SKILL.md under 350 lines** (~4000 tokens) — use `references/` subdirectories for detailed documentation
- **Validate before submitting**: Run `./scripts/validate-skill.sh <category>/<skill-name>`

## Writing Style

- Direct, instructional tone — second person ("you", "your")
- Bold key terms on first use
- Use code blocks for commands, templates, and examples
- Use tables for structured data
- Keep SKILL.md focused — one skill per file, under 350 lines
- Additional documentation goes in `references/` subdirectories
