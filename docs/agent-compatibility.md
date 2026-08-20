# Agent Compatibility — 70+ SKILL.md Hosts

All 120 skills follow the [Agent Skills](https://agentskills.io) open standard (`SKILL.md` + YAML frontmatter), so they run on every host that reads the format — natively or via the [`npx skills` installer](https://github.com/vercel-labs/skills). This page is the per-agent reference: how to install, what each host reads, and what degrades outside the Claude Code plugin. For getting *listed* on marketplaces, directories, and awesome-lists, see [registry-submissions.md](registry-submissions.md).

**Verified 2026-07** (end-to-end): `npx skills add` discovers and installs **120/120** skills from both a local clone and the GitHub remote. The installer reads the skill declarations straight from `.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json` — an official installer feature for Claude Code plugin repos — so the discipline-folder layout (`seo-geo/<phase>/<skill>/`) needs no mirror directory.

**Agent Plugins v1 baseline reviewed 2026-08-10** (offline package contract):
the release-only Portable Lite projection validates **120/120 strict Agent
Skills** under the pinned Agent Plugins 1.0.0 and Agent Skills baselines. This
is not a claim that every client has completed an install/UI smoke test. The
client checks below are a non-blocking client-verification backlog: a `Pending`
row does not block publishing the schema- and repository-validator-conformant
archive, but it does block any claim that the named client is verified until
the required evidence is recorded. See the exact [package structure,
provenance, and capability boundary](agent-plugins-v1.md).

## Install

| Route | Command | Serves |
|-------|---------|--------|
| **Claude Code plugin** (full suite) | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` → `/plugin install aaron-marketing@aaron` | skills + commands + hooks + memory + connectors + shared references |
| **Any other agent** (project) | `npx skills add aaron-he-zhu/aaron-marketing-skills` | skills, installed to `.agents/skills/` + your agent's own dir |
| **Any other agent** (global) | `npx skills add aaron-he-zhu/aaron-marketing-skills -g` | same, user-wide |
| **Single skill** | `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research` | one skill folder |
| **Force one agent** | `… -a codex` / `-a cursor` / `-a opencode` … | one host only |
| **Agent Plugins v1 · Portable Lite** | Download `aaron-marketing-skills-20.0.0-agent-plugin-v1-lite.tar.gz` from the [v20.0.0 release](https://github.com/aaron-he-zhu/aaron-marketing-skills/releases/tag/v20.0.0), unpack it, and select the extracted plugin directory in the client | 120 strict static Skills; no `mcp.json`, commands, hooks, connectors, or repository runtime |

`npx skills` auto-detects which agents are installed and symlinks each skill into the right directories (canonical copy in `.agents/skills/`, per-agent symlinks). Use `--copy` where symlinks are unsupported, `npx skills update` to pull new versions, `npx skills remove` to uninstall.

The repository root is the authoring SSOT, **not** an Agent Plugins v1 install
root: its canonical Skills live under discipline/phase paths and retain the
existing client-specific metadata. Install the extracted release asset instead;
its immediate `skills/<name>/` children are the strict portable projection. The
existing Claude, `npx skills`, SkillHub, ClawHub, OpenClaw, and Hermes routes are
unchanged.

### Agent Plugins v1 client-verification backlog

As of 2026-08-10, the upstream [Agent Plugins compatible-client
list](https://agent-plugins.org/compatible-clients) names the seven clients
below. Repository validation proves package shape, strict Skill frontmatter,
contained links, forbidden runtime surfaces, and file/projection hashes; it
does not substitute for a client smoke test.

| Client listed upstream | Client-verification status | Required evidence before marking verified |
|---|---|---|
| VS Code | Pending | Import the extracted directory; confirm all 120 Skills are discoverable; invoke one static Skill; confirm no MCP server is registered. |
| Cursor | Pending | Import the extracted directory; confirm all 120 Skills are discoverable; invoke one static Skill; confirm no MCP server is registered. |
| GitHub Copilot | Pending | Import the extracted directory; confirm all 120 Skills are discoverable; invoke one static Skill; confirm no MCP server is registered. |
| ChatGPT / Codex | Pending | Import the extracted directory; confirm all 120 Skills are discoverable; invoke one static Skill; confirm no MCP server is registered. |
| Kiro | Pending | Import the extracted directory; confirm all 120 Skills are discoverable; invoke one static Skill; confirm no MCP server is registered. |
| Hermes Agent | Pending | Import the extracted directory; confirm all 120 Skills are discoverable; invoke one static Skill; confirm no MCP server is registered. |
| OpenClaw | Pending | Import the extracted directory; confirm all 120 Skills are discoverable; invoke one static Skill; confirm no MCP server is registered. |

Record the client version, OS, archive SHA-256, discovery count, invocation
result, and MCP-registration observation when each smoke is run. Until then,
describe Portable Lite as schema- and repository-validator-conformant, not as
client-verified. A `Pending` row is therefore an explicit claim boundary, not a
silent release gate.

## skills.sh registry

[skills.sh](https://skills.sh) is the public registry + leaderboard behind the `npx skills` CLI. This bundle's live page: **<https://skills.sh/aaron-he-zhu/aaron-marketing-skills>**.

- **Listing is automatic**: skills appear and rank via the CLI's anonymous install telemetry (skill name, files, timestamp — nothing personal; opt out with `DISABLE_TELEMETRY=1`). There is no submission step — being installable *is* being listed, which is what CI's discovery-count guard protects.
- **Page layout is ours to define**: the repo-root [`skills.sh.json`](../skills.sh.json) ([official schema](https://skills.sh/schemas/skills.sh.schema.json)) groups the 120 skills into the eight discipline sections. Registry entries for pre-v12 skill names that were merged away (e.g. `seo-content-writer`, `meta-tags-optimizer`) persist from historical installs and cannot be deleted — `notGrouped: "bottom"` sinks them below the current catalog. CI asserts the groupings cover exactly the manifest-declared skill set, so a new skill can't ship ungrouped.
- **Search**: `npx skills find <query>` and `GET /api/v1/skills/search` match on name + description — every skill's `description` frontmatter is written with trigger phrases for this (see AGENTS.md authoring rules). The wider API (`/api/v1/…`, leaderboard/detail/audit endpoints) requires a Vercel OIDC token.
- **Well-known hosting** (`/.well-known/agent-skills/index.json`, RFC 8615) is the registry's alternative to GitHub sources for skills served from your own domain — not applicable to this GitHub-hosted repo.

## ClawHub (OpenClaw's registry)

[ClawHub](https://clawhub.ai) is publish-based — it does not crawl GitHub, so the bundle appears there only when its owner pushes versions. This repo ships the tooling:

```bash
npm i -g clawhub && clawhub login          # one-time; GitHub account required
bash scripts/publish-clawhub.sh --dry-run  # preview all 120 (verified: 120/120 resolve)
bash scripts/publish-clawhub.sh --i-accept-mit0   # publish, real versions from VERSIONS.md
```

The script walks the plugin.json skill list (same set every other host installs) and passes each skill's real frontmatter version, so ClawHub versions track this repo's per-skill versioning. Consumers then run `openclaw skills install @<handle>/<skill>` — or find the skills from Hermes via `--source clawhub`. Published skills undergo ClawHub's automated security scanning.

> ⚠️ **License gate**: ClawHub relicenses everything published there as **MIT-0** (free use/modify/redistribute, no attribution) — broader than this repo's Apache-2.0. The script refuses real publishes without an explicit `--i-accept-mit0`, and publishing is intentionally left as an owner decision, not CI automation.

OpenClaw also installs without ClawHub: `npx skills add aaron-he-zhu/aaron-marketing-skills -a openclaw` (project `skills/` dir), since OpenClaw reads `<workspace>/skills/` and `.agents/skills/` natively.

## Hermes Agent install routes

Hermes pulls from multiple hubs; four routes work for this bundle, in order of preference:

1. **skills.sh source** (works today, full skill folders): `hermes skills install skills-sh/aaron-he-zhu/aaron-marketing-skills/<skill-name>` — e.g. `…/keyword-research`; browse with `hermes skills search seo --source skills-sh`.
2. **ClawHub source** (after the owner publishes, see above): `hermes skills search marketing --source clawhub`.
3. **Pinned direct URL** (single file, no `references/` bundled — prefer routes 1–2): `hermes skills install https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/<release-tag>/<discipline>/<phase>/<skill>/SKILL.md`. Pin a release tag; do not use a mutable branch for an execution contract.
4. **Local bulk via `skills.external_dirs`** (all 120, no hub): unpack the Portable Lite release archive anywhere local and point `skills.external_dirs` in the Hermes config at its `skills/` directory — Hermes discovers the 120 flat `skills/<name>/` folders with their bundled reference closure. External dirs sit at the lowest skill-precedence tier, so project and profile skills shadow them cleanly.

**Tap caveat**: `hermes skills tap add` takes a GitHub repository source and assumes one `skills/` root per repo (one `path` override in `~/.hermes/.hub/taps.json`) — it accepts neither local paths nor this multi-discipline layout. Use the skills.sh source (same folders) or route 4 for local bulk installs; a downstream mirror repository with a flat `skills/` root would enable `tap add`, but that mirror is an optional owner-published artifact and is never committed here. Installed skills surface as slash commands (`/keyword-research …`) and are security-scanned at `community` trust on install. Every skill's `metadata.hermes` carries `tags`/`category` so `hermes skills browse` filters cleanly.

## SkillHub.cn (中文 Skills 社区)

[skillhub.cn](https://skillhub.cn) is the Chinese-market skills community (Tencent-hosted, TRACE-scored, human + automated review). Like ClawHub it is publish-based, with its **own frontmatter contract** on top of Agent Skills — every SKILL.md in this repo carries both, so the folders publish as-is:

| SkillHub field | Repo convention |
|----------------|-----------------|
| `slug` (required, globally unique) | unprefixed `<skill-name>` preferred, `aaron-<skill-name>` as the collision fallback — e.g. `keyword-research` (validator-enforced) |
| `displayName` (required) | bilingual: `"Keyword Research · 关键词研究"` |
| `summary` (recommended) | Chinese one-liner for the listing card |
| `version` / `license` / `homepage` | shared with the Agent Skills fields |

Publish flow (owner-run; machine spec at <https://skillhub.cn/ai/release.md>):

```bash
curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only   # one-time
skillhub login --key "$SKILLHUB_KEY" --host https://api.skillhub.cn         # key: 个人中心 → API keys
bash scripts/publish-skillhub.sh --dry-run     # local pre-check, all 120 (verified: 120/120 pass)
bash scripts/publish-skillhub.sh               # publish all → platform review (pending_review)
```

Notes: publishing requires the account to have completed 实名认证 (real-name verification — a `403` means finish it in the browser first); each publish enters platform review before listing; consumers install with the SKILL.md frontmatter slug (`skillhub install <frontmatter-slug>`). Keep the API key in the environment (`$SKILLHUB_KEY`) — never in the repo.

## Per-agent matrix

Paths below are each host's **native** skill directories (docs verified 2026-07; ✦ = also reads the cross-agent `.agents/skills/` convention, which is where `npx skills` installs).

| Agent | Project dir | Global dir | Notes |
|-------|-------------|------------|-------|
| **Claude Code** | `.claude/skills/` (+ plugin skills) | `~/.claude/skills/` | Prefer the plugin — it adds the 8 commands, hooks, memory, connectors. Does **not** read `.agents/skills/`; `npx skills` handles the mapping. |
| **OpenAI Codex** ✦ | `.agents/skills/` (CWD → repo root) | `~/.agents/skills/`, `/etc/codex/skills` | `AGENTS.md` context file supported. Launch-era `~/.codex/skills` no longer in current docs. |
| **Google Antigravity** ✦ | `.agents/skills/` | `~/.gemini/config/skills/` (CLI: `~/.gemini/antigravity-cli/skills/`) | `description` drives activation; global `~/.agents/skills` **not** read. |
| **OpenCode** ✦ | `.opencode/skills/`, `.claude/skills/` | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | Unknown frontmatter ignored; per-skill permissions in `opencode.json`. |
| **Cursor** ✦ | `.cursor/skills/` | `~/.cursor/skills/`, `~/.agents/skills/` | Rules/commands converge on skills (`/migrate-to-skills`). |
| **OpenClaw** ✦ | `<ws>/skills/`, `<ws>/.agents/skills/` | `~/.agents/skills/`, `~/.openclaw/skills/` | Parser reads single-line keys only — every skill's `metadata` is therefore a single-line JSON object (fully parsed, incl. `metadata.openclaw` emoji/homepage). Registry: [ClawHub](#clawhub-openclaws-registry). |
| **Hermes Agent** | — (config `skills.external_dirs`) | `~/.hermes/skills/` | Four install routes — [see below](#hermes-agent-install-routes). `metadata.hermes` carries tags/category for `hermes skills browse`. Skills double as slash commands (`/keyword-research`). Recommends ≤60-char descriptions; ours are longer by design (trigger-phrase routing) and load fine. Named-bot deployment (one profile per bot): [see below](#named-bot-roster-deployment-grok-bot--hermes-bot-mode). |
| **Grok Build** ✦ (docs 2026-08) | `.grok/skills/` | `~/.grok/skills/`, `~/.agents/skills/` | xAI's coding agent. Reads `SKILL.md` natively; unknown frontmatter keys are ignored, so the extended metadata is inert. The global `npx skills add … -g` route serves it via `~/.agents/skills/`. |
| **Grok Bot** (docs 2026-08) | — (no filesystem install surface) | — | xAI's managed named bots on a shared cloud computer. Skills arrive per bot via Settings → Plugins or by saving written instructions in chat — [see below](#named-bot-roster-deployment-grok-bot--hermes-bot-mode). Not a `npx skills` target. |
| **Gemini CLI** ✦ | `.gemini/skills/` | `~/.gemini/skills/`, `~/.agents/skills/` | `.agents/` outranks `.gemini/` at the same tier; `/skills list\|enable\|disable`. |
| **GitHub Copilot CLI** ✦ | `.github/skills/`, `.claude/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` | Same skills work in Copilot cloud agent + code review; `gh skill` adds provenance frontmatter. |
| **Amp** ✦ | `.claude/skills/` | `~/.agents/skills/`, `~/.claude/skills/`, `~/.config/amp/skills/` | — |
| **Goose** ✦ | `.goose/skills/`, `.claude/skills/` | `~/.agents/skills/`, `~/.claude/skills/` | Needs v1.25.0+ (Summon extension). |
| **Windsurf** ✦ | `.windsurf/skills/`, `.claude/skills/` | `~/.codeium/windsurf/skills/`, `~/.agents/skills/` | Docs now under docs.devin.ai (Cognition). |
| **Cline** | `.cline/skills/`, `.clinerules/skills/`, `.claude/skills/` | `~/.cline/skills/` | Docs don't list `.agents/skills/` — use `-a cline` so the installer places the agent dir. |
| **Roo Code** ✦ | `.roo/skills/` | `~/.roo/skills/`, `~/.agents/skills/` | Per-mode variants (`skills-<mode>/`); `.roo/` outranks `.agents/`. |
| **50+ more** ✦ | see [installer table](https://github.com/vercel-labs/skills#supported-agents) | | Cline-likes, Warp, Zed, Kilo, Kiro, Trae, Qoder, OpenHands, Droid, Junie, … |

## Named-bot roster deployment (Grok Bot / Hermes Bot Mode)

Hosts with **named, persistent bots** (xAI's Grok Bot; Hermes Agent's Bot
Mode, where a bot is an isolated profile) deploy this bundle as an
**8-bot roster** instead of one flat skill pile: seven discipline specialists
(`aaron-narrative`, `aaron-seo-geo`, `aaron-social`, `aaron-email`,
`aaron-ad`, `aaron-influencer`, `aaron-launch`) plus `aaron-chief`,
which routes cross-discipline goals and owns the 8 protocol skills. Together
the bots cover the 120 canonical skills exactly once; the roster derives
entirely from [`references/system-catalog.json`](../references/system-catalog.json) —
there is no second hand-maintained inventory.

```bash
python3 scripts/generate-bot-projections.py --output /private/path/aaron-bot-roster
```

The generator writes, into a private directory **outside the repository**
(outputs are release/deployment artifacts and are never committed):

- `hermes/<bot>/` — one installable [Hermes profile distribution](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions)
  per bot: `distribution.yaml`, a generated `SOUL.md` (persona, phase-grouped
  skill index, handoff protocol, inlined non-reducible red lines),
  `skills/<name>/` folders projected with the same link-rewriting and
  static-reference closure as Portable Lite, the bundled
  `references/policy-kernel.md`, and a hash-bound `distribution-manifest.json`.
  Publish a bundle as a git repository and `hermes profile install <url> --alias`.
- `grok/` — `bot-cards.md` (name/title/description per bot; the description
  doubles as Grok's cross-bot routing signal), `enable-lists.md` (exact
  per-bot skill enablement), and `setup-checklist.md`. Grok Bot has no bulk
  import: bots are created manually from the cards, and skills install via
  Settings → Plugins or the officially supported fallback of saving a skill
  from written instructions pasted in chat.

Deployment boundaries, in both hosts:

- Links to a skill owned by another bot are redirected to the bundle's
  `PORTABILITY.md` boundary; cross-bot work is handed off **by name**
  (`@aaron-chief` first) with a visited set and at most three
  automatic handoffs.
- Bundles are Tier-1 and static: no connectors, `mcp.json`, cron, hooks, or
  deterministic runtimes. Auditors return `NOT_SCORED` instead of
  hand-calculating verdicts; registry and durable-memory work is
  propose-only, with canonical acceptance remaining an owner-run step.
- Grok Bot specifics: bots on one account share **one persistent cloud
  computer** — files, browser sessions, and logins are visible to every bot,
  so bot names are not security boundaries. Grok Bot runs on macOS, Windows,
  and iOS at launch (no Linux desktop, Android, or iPad).
- The matching typed host profiles (`hermes-bot-host`, `grok-bot-host`) live
  in the dedicated **roster-projection-only** catalog
  [`references/bot-roster-profiles.json`](../references/bot-roster-profiles.json)
  (schema-locked to `routing_surface: named-bot-roster`,
  `compatible_distributions: ["bot-roster"]`, `context_assembly: excluded`).
  They are deliberately kept out of
  [`references/host-capability-profiles.json`](../references/host-capability-profiles.json),
  so the certified context/prompt assembly chain and its hash-pinned host
  catalog stay untouched; each generated bundle manifest binds the selected
  profile definition by SHA-256.

### Named-bot / Grok smoke backlog (owner-run)

Same contract as the Agent Plugins backlog above: a `Pending` row blocks only
the *verified* claim, never the generated artifact, and only the owner flips a
row after recording the evidence.

| Surface | Status | Required evidence before marking verified |
|---|---|---|
| Grok Build (filesystem skills) | Pending | Client version + OS; skills placed in `.grok/skills/` or `~/.agents/skills/`; discovery confirmed; one skill invoked; unknown frontmatter keys ignored without error. |
| Grok Bot (managed bots) | Pending | App version + platform; one bot created from `bot-cards.md`; one skill saved from written instructions; per-bot enable list applied; a send/publish dry-run stopped at the approval boundary. |
| Hermes Bot Mode (profile distributions) | Pending | `hermes --version` + OS; one generated bundle installed via `hermes profile install`; bundle SHA-256 recorded; bundled skill count discovered (16, or 8 for `aaron-chief`); one skill invoked as a slash command; no MCP server registered. |
| Hermes `skills.external_dirs` (local bulk) | Pending | `hermes --version` + OS; unpacked Portable Lite SHA-256; 120/120 discovery from the external dir; one skill invoked; profile-over-external shadowing observed as documented. |

## Frontmatter portability

Every `SKILL.md` carries `name` (matches its directory, spec rule), `description` (≤1024 chars, spec limit), `license`, `compatibility`, `metadata`, plus the Claude Code extensions `when_to_use` and `argument-hint`. The agentskills.io integration guide instructs hosts to ignore unknown fields, and no researched host hard-fails on extras — the extensions are inert elsewhere.

`metadata` is always a **single-line strict-JSON object** (valid YAML flow mapping, so every spec parser reads it identically). This is deliberate: OpenClaw's frontmatter parser reads single-line keys only — a YAML block map under `metadata:` is invisible to it. The object carries the repo's own keys (`author`, `version`, `discipline`, `phase`, `geo-relevance`) plus two documented host extensions on every skill: `metadata.hermes` (`tags`/`category` for Hermes browse/filter) and `metadata.openclaw` (`emoji`/`homepage` for the OpenClaw macOS UI). The validator fails block-map metadata, so the guarantee holds for future skills.

One hard rule the ecosystem enforces silently: frontmatter must be **valid YAML**. In single-quoted scalars an apostrophe must be doubled (`designer''s`) — one unescaped apostrophe made a skill invisible to every spec parser until v12.7.0. `scripts/validate-skill.sh` now checks for this class, and CI asserts the installer still discovers the full declared count.

Portable Lite is a generated strict projection, not a copy of that extended
frontmatter. It keeps only fields accepted by the pinned Agent Skills baseline,
normalizes generic `metadata` to a string-to-string map, and omits source
`compatibility`, `allowed-tools`, registry/client card fields, and the
Hermes/OpenClaw metadata objects. The canonical source keeps those declarations
for the compatibility channels that use them; Portable Lite grants no host-tool
preapproval.

## What degrades outside the Claude Code plugin

### Generic shared-root router sidecar

A host adapter that installs the complete shared-root payload but cannot expose
Claude-style slash commands can request the typed
`generic-shared-root-host` projection:

```bash
python3 scripts/build-distribution.py \
  --plugin --profile lite \
  --host-profile generic-shared-root-host \
  --output /private/path/aaron-generic-host
```

That payload keeps the 120 business skills unchanged and adds eight generated
`class: router` facades under `router-facades/`, described by
`router-facades/sidecar-manifest.json`. A generic host registers those eight
sidecar entries as its discipline-level discovery surface; after one facade
selects a target, the host invokes the target business Skill itself. The
facade never executes the target workflow and never grants permission. All 120
targets appear exactly once across Narrative, SEO/GEO, Social, Email, Paid Ads,
Influencer, Launch, and Protocol. The normal `npx skills add` route still reads
the canonical 120 entries directly from `.claude-plugin/plugin.json`; generated
facades do not appear in registries or inflate the public Skill count.

All complete plugin/shared-root host projections include the typed host,
prompt, and context-module catalogs, their resolver, and the compact portable
policy kernel. These files select a representation; they are not executable
authority and are not additional Skills. A standalone one-folder install keeps
the full Skill as its embedded explicit-policy representation and does not
claim the missing root resolver, kernel, or capsule runtime.

The Governed physical profile also includes the generated
`references/skill-capsules/` index and 120 per-skill capsule JSON records for
typed lean context assembly. Balanced assembly keeps the complete selected
Skill and replaces only shared policy with the kernel. Its `context-assembly.py` runtime and
schema keep controller, model, tool, and deferred resources separate instead
of treating manifest capacity as model-visible prompt. Capsule records contain
no `SKILL.md`, are not plugin or registry declarations, and therefore never
expand the canonical 120-Skill surface. Explicit and balanced execution still
select the complete Skill; Lite, Pro, and standalone payloads do not ship the
capsule tree or assembly runtime.

A standalone install bundles **only each skill's folder** (its `SKILL.md` + own `references/`). Everything below ships with the plugin (or a full `git clone`) instead:

| Shared resource | Standalone behavior |
|-----------------|---------------------|
| Repo-root `references/` (auditor runbook, typed catalogs, benchmarks, skill contract, state model) | Relative root links are unavailable, but every auditor folder includes a generated immutable `references/auditor-runtime.md` containing all item identities and human benchmark anchors plus the selected framework's typed profiles, applicability, veto, missingness, and observation vocabulary. The root runbook, full schemas, and benchmark remain repository/plugin maintenance sources and are not falsely presented as separate standalone files. The fallback never fetches a mutable branch, guesses missing policy, calculates a score, or claims a gate verdict. Non-gate skills inline their essential rules. |
| Deterministic repo-root runtimes (`rubric-score.py`, `validate-audit-artifact.py`, `context-resolver.py`, `registry-events.py`, `run-events.py`, `audit-loop.py`, `audit-trends.py`) | Not bundled. In a Claude Code plugin install, commands resolve them through `${CLAUDE_PLUGIN_ROOT}`; in a full clone they fall back to the Git repository root, following the [root runtime invocation contract](../references/runtime-invocation.md). In **every** form, agent sessions are limited to `propose`/`suppress` and preparing owner request files — canonical acceptance (`owner-append`/`safety-append`) is an owner-run terminal step outside agent sessions, per the [Owner Ritual](../references/registry-event-protocol.md); once canonical events exist, agent sessions read the owner-installed projections rather than replaying. Run evidence, context manifests, and audit-loop steps are separate non-authoritative metadata and cannot widen that boundary; loop owner approval advances bookkeeping only and is never external-mutation authority. The runtime, not prose or a host-supplied field, derives selected-ancestry loop closure: event-first missing-step recovery requires the same original request, sibling loops stay isolated, successful closure is strict, and a failed/aborted unresolved closure preserves failure evidence without claiming convergence. A standalone one-folder install must fail closed: auditors return `NOT_SCORED` instead of hand-calculating or claiming a gate verdict, registry skills may prepare a proposal but cannot append/project/claim canonical truth, and a host cannot claim a resolver-verified context manifest, session tree, save point, envelope, or converged loop without the corresponding runtime. Install the plugin or use a full clone for those operations. Semantic eval profiles, generated prompt contracts, and the opt-in real Codex adapter are repository-maintenance assets and are intentionally absent from user distributions. |
| `scripts/connectors/*.py` (keyless data helpers) | Not bundled. Every skill is designed Tier-1: it runs on user-provided data with no connector. Clone the repo to use the connectors. |
| The 8 `/aaron-marketing:*` commands | Claude Code plugin only. Ordinary per-Skill installs route from the 120 descriptions. A complete generic shared-root build may instead register the generated eight-facade sidecar described above; standalone one-folder installs remain direct-skill. |
| Hooks (bounded working-memory/run-resume context, Artifact Gate) | Claude Code plugin only, and hook **enforcement requires `python3` on PATH**. Run tracing is off unless `AARON_ACTIVE_RUN_ID` is explicit and stable lifecycle IDs are available; traces contain metadata/hashes, not payloads. Without python3 the hooks degrade instead of refusing everything: non-memory tool calls pass through, and only identifiable memory-namespace / reserved-sink calls are refused until python3 is installed. A standalone host has no machine-enforced audit write interception; without the deterministic validator, an auditor may collect typed inputs but must return `NOT_SCORED` and must not claim `SHIP`, `FIX`, or a persisted valid artifact. |
| Cross-skill handoffs (`../<skill>/SKILL.md` links) | Literal paths may break, but handoffs reference skills **by name** — any host with the sibling skill installed routes fine. Install the full bundle rather than single skills to keep chains intact. |

**Positioning in one line**: Claude Code plugin = the operated product (gates checked by deterministic runtimes plus bounded lifecycle hooks, memory persisted, connectors wired, registry proposals flowing into the owner-run acceptance ritual); any other host = the same 120 authored procedures, with deterministic scoring, registry runtime access, hooks, and connectors degraded exactly as listed above. Canonical registry acceptance is owner-run in every form — no install grants an agent session that authority.

## The write-before validation contract (hookless hosts)

The Claude Code Artifact Gate is a hook; hosts without a PreToolUse equivalent enforce nothing at write time. The gate's *logic* is host-agnostic, though — `scripts/validate-audit-artifact.py` is a stdlib CLI. Any host (or a human operator) can hold the same contract by validating **before** the write lands:

```bash
AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
# 1. Assemble the complete artifact content; stage it as a draft file.
# 2. Validate the draft against its intended sink path (structure + reserved path):
python3 "$AARON_SKILLS_ROOT/scripts/validate-audit-artifact.py" \
  /path/to/draft.md --relative-path memory/audits/<class>/<file>.md
# 3. Only on exit 0, pass the exact validated bytes to the host's full-content writer.
# 4. Revalidate the landed target before claiming it was saved:
python3 "$AARON_SKILLS_ROOT/scripts/validate-audit-artifact.py" \
  memory/audits/<class>/<file>.md --relative-path memory/audits/<class>/<file>.md
```

Rules that make this equivalent to the hook gate:

- Validate **content**, not intent: the bytes validated in step 2 must be the bytes written in step 3 — no post-validation edits, appends, or template re-renders.
- Exit code is the verdict: non-zero means do not write. A prose summary of validation errors is not permission to proceed.
- Validation is structure, not authorization: a passing draft still needs the user's write permission (`references/auditor-runbook.md` §3), and the multi-veto BLOCK / NOT_SCORED semantics in `references/skill-contract.md` are unchanged.
- Sweep form for batch/audit reviews: `--scan-root memory/audits` validates every artifact in the reserved sink (what the Stop hook runs on Claude Code).
- Hosts with their own hook/pretool systems (OpenClaw, Hermes, Cursor, …) can call the same two commands from their extension point; the CLI is network-free and stdlib-only.

## For contributors

- Never mirror skills into `.agents/skills/` or `.claude/skills/` inside this repo — manifest-driven discovery already covers every host, and committed symlinks would not survive iCloud/Windows checkouts.
- Adding a skill? Its `plugin.json` + `marketplace.json` entries make it installable everywhere; CI's discovery-count guard fails if the installer and the manifest disagree.
- Keep `name` == directory name, `description` ≤1024 chars, apostrophes in single-quoted YAML doubled, and `metadata` a single-line JSON object (with the `hermes` + `openclaw` extension keys). `bash scripts/validate-skill.sh <skill-dir>` checks all of it.
- Publishing to ClawHub is an owner-only, license-acknowledged action (`scripts/publish-clawhub.sh`) — never automate it in CI.
