# AGENTS.md

Guidelines for AI agents working in this repository. For full runtime context, see [CLAUDE.md](CLAUDE.md).

## Repository Overview

- **Name**: seo-geo-claude-skills — 20 SEO/GEO skills, 20 commands, shared references
- **Repository**: https://github.com/aaron-he-zhu/seo-geo-claude-skills
- **Author**: Aaron He Zhu | **License**: Apache 2.0
- **Specs**: [Agent Skills](https://agentskills.io/specification.md) · [Codex Plugins](https://developers.openai.com/codex/plugins/build) · [ClawHub](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md) · [Vercel Labs](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md)
Content-first repository: skills and commands are Markdown; Claude Code hooks use a small Bash runner. Primary directories: `research/`, `build/`, `optimize/`, `monitor/`, `cross-cutting/`, `commands/`, `references/`.

Install instructions live in [README.md](README.md). Marketplace and agent-host integration details live in [marketplaces/README.md](marketplaces/README.md). Keep this file focused on authoring and maintenance rules.

## Skill Format Specifications

### Required Frontmatter

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | 1-64 chars, lowercase a-z, numbers, hyphens. Must match directory name. Satisfies ClawHub slug `^[a-z0-9][a-z0-9-]*$`. |
| `version` | Yes | Semver string. Must match `metadata.version` and the row in `VERSIONS.md`. |
| `description` | Yes | 1-1024 chars. Include: what it does, trigger phrases, scope boundaries. Optimized for `npx skills find`. |

### Repo-Required / Spec-Optional Frontmatter

| Field | Purpose |
|-------|---------|
| `license` | License name (default: Apache-2.0) |
| `compatibility` | Platform list |
| `allowed-tools` | Pre-approved tools (e.g., `WebFetch`) |
| `metadata.author/version/geo-relevance/tags/triggers` | Discovery and categorization. `metadata.version` must match top-level `version`. |
| `metadata.openclaw` | ClawHub runtime declarations (only if hard dependency exists) |
| `when_to_use` | Trigger scenarios for auto-invocation (underscores, not hyphens) |
| `argument-hint` | Argument format hint in command picker |

### Description Best Practices

Start with `Use when the user asks to "..."`, then one sentence on function, then scope boundaries linking related skills.

## Quality Frameworks

See [CLAUDE.md § Quality Frameworks](CLAUDE.md) for details. Summary:
- **CORE-EEAT** (80 items, 8 dimensions): content quality. [Full reference](references/core-eeat-benchmark.md)
- **CITE** (40 items, 4 dimensions): domain authority. [Full reference](references/cite-domain-rating.md)
- Veto items: CORE-EEAT (T04, C01, R10) · CITE (T03, T05, T09)

## Tool Connector Pattern

Skills use `~~category` placeholders. See [CONNECTORS.md](CONNECTORS.md). Every skill works at Tier 1 (no tools). MCP adds Tier 2/3.

## Inter-Skill Handoff

See [CLAUDE.md § Inter-Skill Handoff](CLAUDE.md). Key fields: objective, findings, evidence, open loops, keyword, content type, scores (CORE-EEAT/CITE), priority items, URL.

## Git Workflow

- **Branch naming**: `feature/skill-name`, `fix/skill-name`, `docs/description`
- **Conventional Commits**: `feat:`, `fix:`, `docs:`
- **After skill changes**: update tracking files (VERSIONS.md, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, marketplace.json, README.md, CLAUDE.md). For release bumps, also sync CITATION, localized README badges, Gemini/Qwen/CodeBuddy manifests, marketplace mirrors, and the [marketplace module](marketplaces/README.md) when platform-facing behavior changes.
- **Keep regular SKILL.md under 350 lines** — use `references/` for detail. Auditor-class skills with `runbook-sync` markers may inline the protocol runbook up to ~750 lines.
- **Validate**: `./scripts/validate-skill.sh <category>/<skill-name>` and `./scripts/validate-slimming-guardrails.sh` before release/slimming PRs.

## Writing Style

- Direct, instructional, second person
- Bold key terms on first use
- Code blocks for commands/templates; tables for structured data
- One skill per file, under 350 lines; extras in `references/`
