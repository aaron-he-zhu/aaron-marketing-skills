# Registry Submissions — listing playbook

Operational dossier for getting the bundle listed on every skills marketplace, directory, and awesome-list. Status matrix + per-platform routes below; reusable submission copy first. Companion doc: [agent-compatibility.md](agent-compatibility.md) (how the skills *run* everywhere; this file is about being *found* everywhere).

**Rule**: submissions and registry publishes are owner-run actions — prepare everything here, submit manually. Never automate registry publishing in CI.

## Submission kit (copy-paste)

**Repo**: <https://github.com/aaron-he-zhu/aaron-marketing-skills> · Apache-2.0 · v19.0.0 · 120 skills + 8 commands
**Install (universal)**: `npx skills add aaron-he-zhu/aaron-marketing-skills` — 70+ hosts (Codex, Cursor, OpenCode, Antigravity, Gemini CLI, Copilot CLI, OpenClaw, Hermes, …)
**Install (Claude Code plugin, full suite)**: `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` → `/plugin install aaron-marketing@aaron`
**Live registry pages**: [skills.sh](https://skills.sh/aaron-he-zhu/aaron-marketing-skills) · ClawHub (`@aaron-he-zhu/<skill>`) · SkillHub.cn (frontmatter slugs: `<skill>` when owned, otherwise `aaron-<skill>`)
**Topics/tags**: marketing, seo, geo, influencer-marketing, paid-ads, email-marketing, organic-social, product-launch, go-to-market, brand-narrative, brand-messaging, agent-skills, claude-code, skill-md

**One-liner (EN, ~120 chars)**
> 120 marketing skills as one four-layer operating system — narrative, SEO/GEO, social, email, paid, influencer, launch — with 8 auditor gates and keyless connectors.

**One-liner (中文, ~60 字)**
> 120 个营销技能构成四层营销操作系统:品牌叙事、SEO/GEO、自然社媒、邮件、付费广告、红人、产品发布,内置 8 个审计门与免密钥连接器。

**Short blurb (EN, ~350 chars)**
> A four-layer marketing operating system for AI agents: 120 SKILL.md skills across seven disciplines — brand narrative (TALE), SEO/GEO (CORE-EEAT + CITE), organic social (ECHO), email (SEND), paid ads (ROAS), influencer (STAR) and product launch (RAMP) — sharing one contract (trigger, quick start, handoff, next-best-skill). Eight benchmark-driven auditor gates emit machine-checkable verdicts. Every skill runs Tier-1 on pasted data; zero-dependency Python connectors pull free/own data. Works on Claude Code (full plugin) and 70+ SKILL.md hosts.

**Short blurb (中文, ~200 字)**
> 把聊天 Agent 变成营销操作员的四层营销操作系统:120 个 SKILL.md 技能覆盖七大学科——品牌叙事(TALE)、SEO/GEO(CORE-EEAT + CITE)、自然社媒(ECHO)、邮件营销(SEND)、付费广告(ROAS)、红人营销(STAR)、产品发布(RAMP)——共享同一套契约(触发→快速开始→交棒→下一技能)。八套基准驱动八个审计门,产出可机器校验的判定。每个技能都能仅凭粘贴的数据运行;零依赖 Python 连接器可拉取免费/自有数据。支持 Claude Code 完整插件与 70+ SKILL.md 宿主。

**Example use cases (EN — for submission forms asking "Example 1/2/…")**
```text
Example 1: "Research keywords for my SaaS product targeting small teams" — the keyword-research skill turns pasted or connected data into a prioritized keyword and topic-cluster plan.
Example 2: "Audit this article for E-E-A-T and publish readiness" — content-quality-auditor scores it against the 80-item CORE-EEAT benchmark and returns a SHIP / FIX / BLOCK verdict with a prioritized fix plan.
Example 3: "Find TikTok creators for a skincare launch and score their fit" — influencer-discovery builds a vetted candidate pool, then fit-scorer ranks it with go/pass verdicts.
Example 4: "Audit my Google Ads account before I scale spend — exports attached" — ad-account-auditor runs the ROAS gate (RQS score + veto checks) on your own-account export, no ad-platform API keys needed.
Example 5: "Review our message house against TALE before the launch" — narrative-quality-auditor runs separate truth, system, and effectiveness profiles on the versioned narrative canon; it never averages them into one composite and returns machine-checkable SHIP / FIX / BLOCK / UNDECIDED results.
Example 6: "/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub" — the auto command infers intent and chains the smallest useful workflow across the 120 skills.
```

**Reviewer/test notes (EN — for "submission details" fields)**
> Validated with `claude plugin validate` (passes). 120 skills + 8 commands across seven disciplines; CI enforces frontmatter validity, 10-surface version-sync, and install-discovery guards on every commit. Latest release: v19.0.0.

**Awesome-list entry line (EN, generic)**
```markdown
- [Aaron Marketing Skills](https://github.com/aaron-he-zhu/aaron-marketing-skills) - 120 marketing skills as a four-layer operating system (narrative, SEO/GEO, social, email, paid ads, influencer, launch) on one shared contract, with 8 benchmark-driven auditor gates and keyless data connectors.
```

**Awesome-list entry line (中文, generic)**
```markdown
- [Aaron Marketing Skills](https://github.com/aaron-he-zhu/aaron-marketing-skills) - 120 个营销技能构成四层营销操作系统(品牌叙事、SEO/GEO、自然社媒、邮件、付费广告、红人、产品发布),同一套运行契约 + 8 个审计门 + 免密钥数据连接器。
```

## Status matrix

> Legend — ✅ live · 🟢 submitted, awaiting listing · 🟡 prepared, owner action pending · 🔴 blocked upstream (route below) · ⬜ not applicable / not worth it

| # | Platform | Type | Status |
|---|----------|------|--------|
| 1 | [skills.sh](https://skills.sh/aaron-he-zhu/aaron-marketing-skills) | registry (telemetry) | ✅ live — `skills.sh.json` groupings shipped |
| 2 | [SkillHub.cn](https://skillhub.cn) | registry (publish) | ✅ live — local release target is bundle 19.0.0; verify remote drift before publishing. Check with `bash scripts/registry-status.sh`; publish only the behind-set with `bash scripts/publish-registries.sh --live skillhub` (see [distribution.md](distribution.md)) |
| 3 | [ClawHub](https://clawhub.ai) | registry (publish) | ✅ live — 120 skills current **and** the whole plugin as the `aaron-marketing` **bundle-plugin** package (`bash scripts/publish-package.sh --from-build --live`). Verify the canonical set with `registry-status.sh --require-current`; publish skills with `publish-registries.sh --live clawhub` |
| 4 | [Anthropic community marketplace](https://github.com/anthropics/claude-plugins-community) | curated directory | 🟢 **submitted 2026-07-04, pending review** (Console form; surfaces: Claude Code + Cowork; watch the [community catalog](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json) for `aaron-marketing`) |
| 5 | [Skills Directory](https://www.skillsdirectory.com) | directory + security scan | 🟢 **submitted 2026-07-04** (owner, via /submit) |
| 6 | [askill.sh](https://askill.sh) | registry | 🟡 CLI route times out from CN network (`askill login`/`submit` both) — use the **web form** askill.sh/submit instead; API token saved by owner |
| 7 | [SkillsMP](https://skillsmp.com) | auto-crawl | 🟡 indexed but **stale (38/120 pre-v12)** — nudge maintainer (Reddit/X) to re-crawl |
| 8 | [LobeHub Skills](https://lobehub.com/skills) | auto-crawl (topics) | ✅ crawl conditions met (topics verified) |
| 9 | [agentskill.sh](https://agentskill.sh) / [skill0.io](https://skill0.io) / [crossaitools](https://crossaitools.com) | auto-crawl | ✅ passive — no lever beyond topics/stars |
| 10 | `gh skill` (GitHub CLI) | decentralized channel | 🔴 layout unsupported — upstream FR drafted below |
| 11 | [Qoder Community](https://qoder.com/marketplace) | catalog repo (PR) | 🟢 **PR submitted**: [qoder-community#73](https://github.com/Qoder-AI/qoder-community/pull/73) (EN + zh entries, marketing category) |
| 12 | [AgentUse / Zerone Skill Market](https://www.zerone.market) | catalog repo (PR, bilingual) | 🟢 **PR submitted**: [agent-use-skills#7](https://github.com/zerone-agent/agent-use-skills/pull/7) (bilingual intro + 6 platform guides) |
| 13 | [Skillstore](https://skillstore.io) | form + security audit | 🟢 **submitted 2026-07-04** (owner, via /submit) |
| 14 | [Agent Skills Me](https://agentskills.me) | editor-curated aggregator | 🟡 login flow flagged as risky by owner's browser — **email fallback**: hi@evergreenai.cn (draft in this doc's kit) |
| 15 | [虾评Skill](https://xiaping.coze.com) | ZIP upload + points economy | ⬜ poor fit — per-skill ZIP repack + 虾米 quota grind; revisit only on demand |
| 16 | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) + siblings | awesome lists (PR) | 🟢 **PR submitted**: [awesome-agent-skills#755](https://github.com/VoltAgent/awesome-agent-skills/pull/755) (Community Skills → Marketing); siblings still open |
| 17 | [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | awesome list (PR) | ⬜ gated on full ClawHub publish first |
| 18 | Personal collections (anthropics, vercel-labs, antfu, obra, steipete, baoyu, …) | collections | ⬜ not venues |

## Per-platform playbooks

*(each entry: URL · operator · listing mechanism · exact submission route · prepared content · caveats)*

### English-language directories & registries (researched 2026-07)

**Concrete submission targets (owner-run, in value order):**

1. **Anthropic official plugin directory** — [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (curated; third-party plugins in `/external_plugins`; installs as `/plugin install <name>@claude-plugins-official`). **Submission form: <https://clau.de/plugin-directory-submission>** — "external plugins must meet quality and security standards." We are a spec-compliant plugin with CI guards, evals, and security docs — the strongest single listing available. Use the EN short blurb from the kit.
2. **Skills Directory** — <https://www.skillsdirectory.com> (~97k skills scanned, 50-rule security scan, grade badges). **Submit at <https://www.skillsdirectory.com/submit>** (GitHub sign-in → submit repo → automated scan). Whether one submission covers all 120 nested skills is undocumented — check after sign-in.
3. **askill.sh** — <https://askill.sh> ("The Agent Skills Registry", 261k+ entries, 40+ agents). GitHub-sourced **plus explicit submit page <https://askill.sh/submit>**.

**Auto-crawl (passive — no submission exists; discovery levers below):** [SkillsMP](https://skillsmp.com) (2M+ skills, ~2-star minimum), [LobeHub Skills](https://lobehub.com/skills) (169k+, scrapes GitHub topics `claude-skills`/`agent-skills` + SKILL.md code search), [agentskill.sh](https://agentskill.sh) (`ags` CLI, 100k+ indexed, security-vetted), [skill0.io](https://skill0.io) (small curated crawl, no submit lever), [crossaitools.com](https://crossaitools.com) (ex-claudemarketplaces.com; ranked by installs/stars/votes). **Discovery levers, all already satisfied**: GitHub topics (`agent-skills`, `claude-skills`, `ai-skills`, `claude-code` — verified present, 20-topic cap reached), public SKILL.md files, stars/install velocity.

**GitHub `gh skill` CLI — the one hard gap (verified 2026-07):** `gh skill install aaron-he-zhu/aaron-marketing-skills` fails with "no skills found" — the preview CLI only discovers `skills/*/SKILL.md`, `skills/{scope}/*/SKILL.md`, `{prefix}/skills/*/SKILL.md`, `*/SKILL.md`, or `plugins/*/skills/*/SKILL.md`, and (unlike `npx skills`) does **not** read `.claude-plugin/plugin.json` manifests. It also serves the latest semver tag, not `main` — cut releases to keep any future gh-skill content fresh. Prepared actions: (a) upstream feature request to [cli/cli](https://github.com/cli/cli/issues) asking for Claude-plugin-manifest discovery (precedent: vercel-labs/skills reads it, quote their plugin-manifest support); (b) fallback option, only if the user wants it: a flat auto-generated mirror repo (`skills/<name>/` layout, synced by Actions) — real maintenance cost, splits identity; not recommended while (a) is open.

**Not targetable now:** Smithery skills (no publish route documented), Agensi (paid/monetized marketplace, creator-contact onboarding — only if we want a commercial listing), ClaudeSkills.info / MCP Market / claudecodemarketplace.net / mcpservers.org (minor reach, mechanisms unverified).

<details><summary>Ready-to-paste: cli/cli feature-request draft (gh skill manifest discovery)</summary>

> **Title**: `gh skill`: discover skills declared in Claude Code plugin manifests (`.claude-plugin/plugin.json`)
>
> `gh skill install <owner>/<repo>` currently discovers only fixed layouts (`skills/*/SKILL.md`, `{prefix}/skills/*/SKILL.md`, `*/SKILL.md`, …). Repos organized as Claude Code plugins declare their skill directories in `.claude-plugin/plugin.json` (`"skills": ["./<path>", …]`) and often use domain-oriented trees that don't match those globs. The `npx skills` installer (vercel-labs/skills) already reads these manifests for exactly this reason, so the same repos install fine there but fail under `gh skill` with "no skills found … may be a curated list rather than a skills publisher".
>
> Example: `gh skill install aaron-he-zhu/aaron-marketing-skills` → 0 found, while the manifest declares 120 skills, each a spec-compliant `<dir>/SKILL.md`.
>
> Request: when the fixed globs find nothing (or additionally), read `.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json` skill declarations, mirroring vercel-labs/skills' `plugin-manifest` support.

</details>

### Chinese-language platforms (researched 2026-07)

1. **Qoder Community** — [qoder.com/marketplace](https://qoder.com/marketplace), catalog repo [`Qoder-AI/qoder-community`](https://github.com/Qoder-AI/qoder-community) (Alibaba's Qoder; entries reference external GitHub repos; review = build + schema check). **PR-ready entry** — add `src/content/skills/aaron-marketing-skills.md` (+ optional `src/content/skills-zh/` mirror with the kit's Chinese blurb):
   ```yaml
   ---
   name: aaron-marketing-skills
   title: Aaron Marketing Skills
   description: 120 marketing skills as a four-layer operating system — narrative, SEO/GEO, social, email, paid ads, influencer, launch — with 8 auditor gates and keyless data connectors.
   source: community
   author: aaron-he-zhu
   githubUrl: https://github.com/aaron-he-zhu/aaron-marketing-skills
   docsUrl: https://github.com/aaron-he-zhu/aaron-marketing-skills#readme
   category: marketing
   tags: [seo, geo, influencer, paid-ads, email-marketing, organic-social, product-launch, brand-narrative]
   roles: [marketer, growth, seo-specialist]
   date: <PR date>
   installCommand: npx skills add aaron-he-zhu/aaron-marketing-skills
   ---
   ```
   (Confirm exact schema against their `CONTRIBUTING.md` at PR time — field set verified 2026-07.) Qoder the IDE already installs us via skills.sh: `npx skills add aaron-he-zhu/aaron-marketing-skills -a qoder` works today.
2. **AgentUse / Zerone Skill Market** — [zerone.market](https://www.zerone.market), catalog repo [`Zerone-Agent/agent-use-skills`](https://github.com/Zerone-Agent/agent-use-skills). Two routes: *fast-track* — tell any agent 「请使用 `agentuse-share` 技能, 根据以下仓库链接完成贡献: https://github.com/aaron-he-zhu/aaron-marketing-skills」 and it generates the files; *manual* — fork + add `awesome-skills/introductions/{zh,en}/aaron-marketing-skills.md` (use both kit blurbs) + per-platform `INSTALL-*.md` guides. **Bilingual zh+en mandatory**; must be verified on ≥1 mainstream framework (we have several).
3. **Skillstore** — [skillstore.io/submit](https://skillstore.io/submit) (sign-in; accepts a repo URL **or a specific directory**; they run a security audit then open their own review PR). Repo root has no SKILL.md, so submit **flagship skill directory URLs** with a note about the plugin structure. Suggested flagship set (the 8 auditor gates, one per framework, spanning all seven disciplines): `narrative/evaluate/narrative-quality-auditor` (TALE), `seo-geo/tune/content-quality-auditor` (CORE-EEAT), `seo-geo/evaluate/domain-authority-auditor` (CITE), `social/host/social-quality-auditor` (ECHO), `email/deliver/email-quality-auditor` (SEND), `ad/activate/ad-account-auditor` (ROAS), `influencer/activate/creator-content-auditor` (STAR), `launch/mobilize/launch-readiness-auditor` (RAMP).
4. **Agent Skills Me** — [agentskills.me](https://agentskills.me) (EvergreenAI/Jimmy Lv; editor-curated aggregator of known GitHub skill repos). Register (GitHub login) → `/submit`; fallback email hi@evergreenai.cn with the kit's Chinese blurb asking to add the repo to indexed sources.
5. **SkillsMP** — [skillsmp.com](https://skillsmp.com) auto-crawl; **already indexed but stale**: `skillsmp.com/creators/aaron-he-zhu/aaron-marketing-skills` shows 38 pre-v12 skills (old names like `performance-reporter`) against the current 120, and the old `seo-geo-claude-skills` repo is indexed separately. No submit route — nudge the maintainer (Reddit/X, solo dev) for a re-crawl; pushing the current branch + a fresh release is the strongest re-crawl signal.
6. **虾评Skill** — [xiaping.coze.com](https://xiaping.coze.com) (Coze-hosted; per-skill ZIP ≤10MB with Chinese 50–300-char descriptions via agent API; upload quota gated by 虾米 points — A1 level = 0 uploads; promotion to 正式版 needs 5 reviews ≥4分). **Poor fit** for a 120-skill bundle — revisit only if the user specifically wants presence there.

### Open-source lists & collections (researched 2026-07)

**PR targets — curated link lists (submit the repo as one entry):**

1. **VoltAgent/awesome-agent-skills** (~27k★) — *top target*. Links-only curated list with an existing **Community Skills → Marketing** subcategory (marketing precedent: Corey Haines' skills already listed). Requirements per its CONTRIBUTING: public repo, working skill, SKILL.md docs, ≤10-word description, and *demonstrated community adoption* (brand-new repos get declined — our star count and skills.sh installs are the evidence). PR-ready entry (title `Add skill: aaron-he-zhu/aaron-marketing-skills`):
   ```markdown
   - **[aaron-he-zhu/aaron-marketing-skills](https://github.com/aaron-he-zhu/aaron-marketing-skills)** - 120 marketing skills: narrative, SEO/GEO, social, email, paid, influencer, launch
   ```
2. **Sibling awesome lists** (same entry line, adjust format to each list's style): `travisvn/awesome-claude-skills`, `heilcheng/awesome-agent-skills`, `kodustech/awesome-agent-skills`, `ComposioHQ/awesome-claude-skills`, and the Chinese-maintained `libukai/awesome-agent-skills`, `JackyST0/awesome-agent-skills`.
3. **VoltAgent/awesome-openclaw-skills** (5,400+ entries) — hard gate: entry must link `clawhub.ai/<author>/<skill>` for skills **already on ClawHub** with clean scan + adoption. Second wave after `scripts/publish-clawhub.sh` runs for real. Entry format: `- [skill-name](https://clawhub.ai/aaron-he-zhu/<skill>) - <≤10-word description>.`

**Not venues (watch-and-learn only):** `anthropics/skills` (1st-party showcase + the spec's authoring `template/`), `vercel-labs/agent-skills` (Vercel-authored only), `antfu/skills` (personal prefs), `obra/superpowers` ("we don't generally accept new skills"), `steipete/agent-scripts`, `JimLiu/baoyu-skills` (personal, no contribution path), `jinghan23/codex-export` + `alchaincyf/nuwa-skill` (single-skill repos), `titanwings/colleague-skill` (persona-skill gallery only — wrong domain).

**Optional upstreaming (content donation, not listing):** `affaan-m/everything-claude-code` (~212k★, accepts skills into its bundle — worth donating 1–2 flagship skills with a backlink if we want that audience); `ZhanlinCui/Ultimate-Agent-Skills-Collection` (166★, copies implementations in-tree — low value).

**Resolved (2026-07)**: the "skills (悟鸣)" card is [chujianyun/skills](https://github.com/chujianyun/skills) — WuMing's personal collection (669★, prompt/config-advisor/P7-P9/mermaid skills, CC-BY-NC-SA, no CONTRIBUTING) → same "not a venue" category as the other personal collections.

**Source directory**: the screenshot's catalog is [xia345.com](https://xia345.com) ("AI Agent 生态导航", 7,000+ skills/tools tracked) — no public submission route found; it curates editorially, so presence on the platforms above is the way in.
