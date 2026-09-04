<div align="center">

# Aaron Marketing Skills

**120 marketing skills, 7 disciplines, one contract — your AI marketing staff, installable as a plugin, portable skills, or an 8-bot team.**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
<!-- GENERATED:BEGIN release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-20.1.0-orange" alt="Version"></a>
<!-- GENERATED:END release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
  <a href="https://claudeskills.info/skills/aaron-he-zhu/aaron-marketing-skills/"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/claudeskills.json" alt="ClaudeSkills"></a>
</p>

**English** | [Deutsch](docs/README.de.md) | [Español](docs/README.es.md) | [Français](docs/README.fr.md) | [Italiano](docs/README.it.md) | [日本語](docs/README.ja.md) | [한국어](docs/README.ko.md) | [Português](docs/README.pt.md) | [简体中文](docs/README.zh.md) | [繁體中文](docs/README.zh-Hant.md)

</div>

An **AI marketing staff you install, not prompt** — 120 agent skills as one plugin, as portable skills on 70+ hosts, or as an **8-bot AI Staff** on Grok Bot and Hermes Bot Mode. Skills and commands are **plain Markdown**; small Bash/Python-stdlib runtimes provide hooks, validation, scoring, registry events, connectors, and CI (no `pip`). **Every skill runs at Tier 1** with data you provide.

| Layer | Skills | Lifecycle (phase directories) | Framework → gate | Entrypoint |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](references/tale-benchmark.md) truth / system / effectiveness profiles | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Social** | 16 | explore → craft → host → observe | [ECHO](references/echo-benchmark.md) asset / program-maturity profiles | `/aaron-marketing:social` |
| **Email** | 16 | setup → engage → nurture → deliver | [SEND](references/send-benchmark.md) → `email-quality-auditor` (EQS) | `/aaron-marketing:email` |
| **Paid ads** | 16 | research → orchestrate → activate → scale | [ROAS](references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:ad` |
| **Influencer** | 16 | scout → target → activate → report | [STAR](references/star-benchmark.md) → `creator-content-auditor` (SQS); `fit-scorer` produces the Suitability (S) read | `/aaron-marketing:influencer` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](references/ramp-benchmark.md) preflight / execution / outcome profiles | `/aaron-marketing:launch` |
| **Protocol layer** | 8 | — (shared machinery, outside the phase flows) | 7 truth registries (entity · creator · offer/claims · consent · launch · channel · narrative) + HOT/WARM/COLD memory | — |

`/aaron-marketing:auto` routes any natural-language goal. Typed topology: [`references/system-catalog.json`](references/system-catalog.json). Readable map: [system architecture](docs/system-architecture.md). Long-form narrative/SEO: [aaronmarketing.ai docs hub](https://aaronmarketing.ai/docs/) (placeholder hub root). In-repo vs hub: [docs/README.md](docs/README.md).

> Signpost repos point here — [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) (tag `v9.9.12`) and [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills) (tag `standalone-final`). Sibling policy: [docs/repo-family.md](docs/repo-family.md).

---

## Contents

- [Install](#install)
  - [AI Staff](#ai-staff--8-named-bots)
- [First run](#first-run)
- [Skill catalog](#skill-catalog)
- [Commands](#commands)
- [More](#more)
- [Contributing](#contributing--project-docs)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Install

| Host | Install |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` then `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ hosts](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **Agent Plugins v1 clients · Portable Lite** | Download `aaron-marketing-skills-20.1.0-agent-plugin-v1-lite.tar.gz` from the [v20.1.0 release](https://github.com/aaron-he-zhu/aaron-marketing-skills/releases/tag/v20.1.0), unpack it, and install the extracted plugin directory |
| **Grok Bot · Hermes Bot Mode (AI Staff)** | Generate, then install: Hermes = `profile install`; Grok = semi-manual cards. See [AI Staff](#ai-staff--8-named-bots) |
| **[SkillHub.cn](https://skillhub.cn) (中文社区)** | `skillhub install <frontmatter-slug>` |
| **Any host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

Claude Code: `marketplace add` only registers the catalog — run `/plugin install aaron-marketing@aaron` to enable skills and commands. Single skill: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`. Per-agent quirks: [docs/agent-compatibility.md](docs/agent-compatibility.md) (verified 120/120 installable, 2026-07).

The plugin adds **nothing** to `/mcp` — [`docs/mcp-catalog.json`](docs/mcp-catalog.json) is a copy-paste reference only. The repo root is the authoring SSOT, **not** an Agent Plugins v1 install root. Use the Portable Lite release asset ([boundary](docs/agent-plugins-v1.md)).

### AI Staff — 8 named bots

On **Grok Bot** and **Hermes Bot Mode** this bundle installs as staff: seven specialists (`aaron-narrative`, `aaron-seo-geo`, `aaron-social`, `aaron-email`, `aaron-ad`, `aaron-influencer`, `aaron-launch`) plus **`aaron-chief`** (protocol + routing). Same 120 skills, covered exactly once. No Web UI, Usage Gateway, or cloud hosting in this OSS surface.

```bash
python3 scripts/generate-bot-projections.py --output /private/path/aaron-bot-roster
```

| Path | What you do |
|------|-------------|
| **Hermes** | Each `hermes/<bot>/` is a profile distribution. Publish that directory as a git repo, then `hermes profile install <url> --alias`. |
| **Grok** | Semi-manual: create bots from `grok/bot-cards.md`, enable `grok/enable-lists.md`, follow `grok/setup-checklist.md`. No bulk import. |

Bundles are **Tier-1 static**. Auditors return `NOT_SCORED`. Registries are propose-only. On Grok, every bot on an account shares one cloud computer — names are not security boundaries. Full steps, output layout, and smoke: **[docs/ai-staff-install.md](docs/ai-staff-install.md)**. Host matrix + owner-run backlog: [agent-compatibility.md](docs/agent-compatibility.md#named-bot-roster-deployment-grok-bot--hermes-bot-mode). Long-form: [docs hub / AI Staff](https://aaronmarketing.ai/docs/ai-staff) (placeholder path).

Offline check: `python3 scripts/smoke-bot-projections.py`.

---

## First run

If the host routes skills automatically, describe the goal:

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

Or use a slash command — `/auto` to route, or a discipline entrypoint:

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

Every skill works with pasted data. Optional tools: [CONNECTORS.md](CONNECTORS.md).

---

## Skill catalog

Skill links open each `SKILL.md`. One-line purpose and plays live in each **Discipline guide**. Catalog order follows the four-layer strata — Narrative first, then the five channels, Launch, then Protocol.

### Narrative — TALE (16)  ·  📖 [Discipline guide](narrative/README.md)

| Phase | Skills |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](narrative/evaluate/narrative-drift-monitor/SKILL.md) |

### SEO/GEO — SITE (16)  ·  📖 [Discipline guide](seo-geo/README.md)

| Phase | Skills |
|-------|--------|
| **Survey** | [keyword-research](seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement** | [content-writer](seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune** | ⛩ [content-quality-auditor](seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate** | ⛩ [domain-authority-auditor](seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

### Social — ECHO (16)  ·  📖 [Discipline guide](social/README.md)

No posting, engagement, or DM automation.

| Phase | Skills |
|-------|--------|
| **Explore** | [channel-portfolio-planner](social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](social/craft/social-creative-builder/SKILL.md), [short-video-scripter](social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](social/host/social-selling-planner/SKILL.md), [crisis-response-planner](social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](social/observe/social-measurement-loop/SKILL.md) |

### Email — SEND (16)  ·  📖 [Discipline guide](email/README.md)

| Phase | Skills |
|-------|--------|
| **Setup** | [deliverability-qa](email/setup/deliverability-qa/SKILL.md), [list-segment-builder](email/setup/list-segment-builder/SKILL.md), [list-growth-designer](email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](email/engage/email-creative-builder/SKILL.md), [subject-line-lab](email/engage/subject-line-lab/SKILL.md), [email-render-builder](email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](email/deliver/cold-outbound-sequencer/SKILL.md) |

### Paid Ads — ROAS (16)  ·  📖 [Discipline guide](ad/README.md)

| Phase | Skills |
|-------|--------|
| **Research** | [campaign-architect](ad/research/campaign-architect/SKILL.md), [audience-segment-builder](ad/research/audience-segment-builder/SKILL.md), [search-term-miner](ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](ad/scale/fatigue-frequency-manager/SKILL.md) |

### Influencer — STAR (16)  ·  📖 [Discipline guide](influencer/README.md)

| Phase | Skills |
|-------|--------|
| **Scout** | [audience-mapper](influencer/scout/audience-mapper/SKILL.md), [trend-spotter](influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](influencer/scout/fit-scorer/SKILL.md) |
| **Target** | [competitor-tracker](influencer/target/competitor-tracker/SKILL.md), [campaign-planner](influencer/target/campaign-planner/SKILL.md), [brief-generator](influencer/target/brief-generator/SKILL.md), [budget-optimizer](influencer/target/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](influencer/activate/contract-helper/SKILL.md), [content-amplifier](influencer/activate/content-amplifier/SKILL.md) |
| **Report** | [landing-optimizer](influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](influencer/report/performance-analyzer/SKILL.md), [roi-calculator](influencer/report/roi-calculator/SKILL.md), [report-generator](influencer/report/report-generator/SKILL.md) |

### Launch — RAMP (16)  ·  📖 [Discipline guide](launch/README.md)

| Phase | Skills |
|-------|--------|
| **Research** | [positioning-mapper](launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](launch/research/launch-window-planner/SKILL.md), [early-access-designer](launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](launch/prove/momentum-planner/SKILL.md) |

### Protocol layer (8)

| Group | Skills |
|-------|--------|
| **Protocol** | [entity-registry](protocol/entity-registry/SKILL.md), [creator-registry](protocol/creator-registry/SKILL.md), [offer-claims-registry](protocol/offer-claims-registry/SKILL.md), [consent-registry](protocol/consent-registry/SKILL.md), [launch-registry](protocol/launch-registry/SKILL.md), [channel-registry](protocol/channel-registry/SKILL.md), [narrative-registry](protocol/narrative-registry/SKILL.md), [memory-management](protocol/memory-management/SKILL.md) |

---

## Commands

Eight commands. Source: [commands/](commands).

| Command | Use it for | Narrowing |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Any goal — smallest useful workflow | `--deep` |
| `/aaron-marketing:narrative` | Brand narrative (TALE) | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO (SITE) | `--phase survey\|implement\|tune\|evaluate` |
| `/aaron-marketing:social` | Organic social (ECHO) | `--phase explore\|craft\|host\|observe` |
| `/aaron-marketing:email` | Email (SEND) | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:ad` | Paid ads (ROAS) | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:influencer` | Influencer (STAR) | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:launch` | Product launch (RAMP) | `--phase research\|assemble\|mobilize\|prove` |

---

## More

Short pointers only. Long-form essays belong on the [docs hub](https://aaronmarketing.ai/docs/) (placeholder). Maintainer contracts stay in-repo.

- **Architecture** — L1 Narrative → L2 channels → L3 Launch → L4 Protocol. Shared contract: [skill-contract.md](references/skill-contract.md). Four-layer map: [system-architecture.md](docs/system-architecture.md).
- **Quality** — eight frameworks, eight auditor gates (`SHIP` / `FIX` / `BLOCK` / `UNDECIDED`). Runbook: [auditor-runbook.md](references/auditor-runbook.md).
- **Capability profiles** — fresh projects run **Lite**. Pro / Governed add connectors or stateful writes; they never drop consent, claims, or audit integrity. Details: [capability-profiles.md](references/capability-profiles.md).
  **v19 validation status:** this is an **engineering-validated** release. CI, package checks, and real-provider runs over simulated fixtures are not real-project outcome evidence; **real-project outcomes remain unvalidated**. **Lite remains** the fresh-project **default**. Governed availability does not validate Governed outcomes or Governed-by-default. That promotion needs the post-release cohort of **14** pilots + **70** paired Lite/Governed projects + **28** shadow projects.
- **Connectors** — `~~category` placeholders; Tier 1 is keyless. Recipes: [CONNECTORS.md](CONNECTORS.md). Add one: [connector-playbook.md](docs/connector-playbook.md).
- **Workflows** — `/aaron-marketing:auto` for cross-channel goals; each discipline guide lists its 4-phase loop.
- **Design** — skills are content; keyless first; surgical/MECE; no invented numbers; compliance is guidance, not law.
- **Hooks** (Claude Code plugin): `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, and `Stop`. The **Artifact Gate** is framework-agnostic.
- **Layout** — discipline/phase trees, `commands/`, `references/`, `hooks/`, `scripts/`, `memory/`, `docs/`. `references/wiki/` is maintainer knowledge, not a Skill and not a runtime default.
- **CI** — `validate-skill.sh`, golden math, evals, routing, `check-wiki.py` (wiki stays out of assembly), PII, stdlib-only, versions, and `python3 scripts/smoke-bot-projections.py` for the AI Staff roster. Full guard list: [CONTRIBUTING.md](CONTRIBUTING.md).

Distributions are allowlisted by [`references/distribution-files.json`](references/distribution-files.json). Maintenance scripts named here (`check-wiki.py` and friends) stay in `MAINTENANCE_EXACT` and do **not** enter the plugin payload.

---

## Contributing & project docs

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — authoring rules, the 10 tracking surfaces, and team conventions.
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](VERSIONS.md)** — per-skill versions + changelog (current bundle: `20.1.0`).
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](SECURITY.md)** · **[PRIVACY.md](PRIVACY.md)** · **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**
- **[CLAUDE.md](CLAUDE.md)** / **[AGENTS.md](AGENTS.md)** — agent-facing context.
- **[docs/README.md](docs/README.md)** — which docs are in-repo SSOT vs site-hub destined.

Maintainer knowledge lives in [`references/wiki/`](references/wiki/index.md) (schema: [`SCHEMA.md`](references/wiki/SCHEMA.md)). It is not a 121st Skill and is **not** injected into runtime context assembly. Skill path/slug/`name` changes stay forbidden.

---

## Disclaimer

These skills assist brand-narrative, SEO/GEO, influencer-marketing, paid-ads, email-marketing, product-launch, and organic-social workflows but do **not** guarantee rankings, AI citations, traffic, engagement, conversions, ROAS, deliverability, or business outcomes. Influencer-, ad-, email-, and social-compliance checks (FTC disclosure, claim integrity, platform policy, consent/opt-in, material-connection disclosure) are guidance, not legal advice. Verify recommendations with qualified professionals before relying on them for major strategy, financial, or legal decisions.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left&sealed_token=ejNFyk10Yua2s8a5BomKSd5kCPTp6s9p5WfLLK7z_xHjBbBXuZ2-m7dowGHvGzCJi4zhs-PUv4m4v77ZIsuYunVBnwWGIZRF5zGe6bl3Dob3Pwlm9VUelpwpKOAtf4V9s8crOVP2h4hAEfMV4TgrzuLW-K2Tx5Lv870ovKJuWC-urh-yG2E-9_c25uVl" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left&sealed_token=ejNFyk10Yua2s8a5BomKSd5kCPTp6s9p5WfLLK7z_xHjBbBXuZ2-m7dowGHvGzCJi4zhs-PUv4m4v77ZIsuYunVBnwWGIZRF5zGe6bl3Dob3Pwlm9VUelpwpKOAtf4V9s8crOVP2h4hAEfMV4TgrzuLW-K2Tx5Lv870ovKJuWC-urh-yG2E-9_c25uVl" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left&sealed_token=ejNFyk10Yua2s8a5BomKSd5kCPTp6s9p5WfLLK7z_xHjBbBXuZ2-m7dowGHvGzCJi4zhs-PUv4m4v77ZIsuYunVBnwWGIZRF5zGe6bl3Dob3Pwlm9VUelpwpKOAtf4V9s8crOVP2h4hAEfMV4TgrzuLW-K2Tx5Lv870ovKJuWC-urh-yG2E-9_c25uVl" />
 </picture>
</a>
