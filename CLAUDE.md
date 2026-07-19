# Aaron Marketing Skills — Claude Code Context

This plugin provides **120 skills and 8 commands** across Narrative, SEO/GEO, Organic Social, Email, Paid Ads, Influencer, and Product Launch, plus a shared protocol layer. All 120 skills follow one contract and are auto-loaded by context; commands use `/aaron-marketing:`. Current bundle version: `18.0.0` (see [VERSIONS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md)). The typed topology is [`references/system-catalog.json`](references/system-catalog.json); [`docs/system-architecture.md`](docs/system-architecture.md) is its generated human view.

> Umbrella repo, renamed from `seo-geo-claude-skills` (stars/forks/issues/history carried over by the GitHub rename). This repo is the **SSOT for the whole repo family** — 8 benchmark mirrors and 7 discipline signpost repos are declared in [docs/repo-family.md](docs/repo-family.md). The SEO/GEO and influencer former standalones preserve their final lines at tags `v9.9.12` / `standalone-final`. Release sync is owner-run via `scripts/sync-family.sh` (dry-run default); `family-drift.yml` is read-only. **No family repo is created or synced outside that registry.**

> Cross-agent: beyond the Claude Code plugin, all 120 skills install standalone on the 70+ SKILL.md hosts served by `npx skills` (Codex, Cursor, OpenCode, Antigravity, Gemini CLI, Copilot CLI, OpenClaw, Hermes, …) — the installer reads the skill declarations from `.claude-plugin/plugin.json`, so **no mirror skills directory may be added to this repo**. Per-agent matrix, frontmatter portability rules (YAML single-quote escaping!), and standalone degradation: [docs/agent-compatibility.md](docs/agent-compatibility.md). CI's discovery-count guard asserts all declared skills stay installer-visible. The bundle's [skills.sh registry page](https://skills.sh/aaron-he-zhu/aaron-marketing-skills) is laid out by the repo-root `skills.sh.json` groupings — every new/renamed skill must be added to a grouping (CI-enforced). OpenClaw's ClawHub registry is publish-based: `scripts/publish-clawhub.sh` (owner-run, MIT-0 relicensing acknowledgement required, never CI-automated); Hermes installs via its skills.sh source (`hermes skills install skills-sh/aaron-he-zhu/aaron-marketing-skills/<skill>`). SkillHub.cn (中文社区) is likewise publish-based via `scripts/publish-skillhub.sh` — its frontmatter contract (`slug` — unprefixed `<name>` preferred, `aaron-<name>` as the collision fallback — plus `displayName` + `summary`) lives in every SKILL.md and is validator-enforced; the API key stays in `$SKILLHUB_KEY`, never in the repo.

## Skills by Phase

> **The system — a four-layer marketing operating system.** One brand voice, expressed through five always-on channels, concentrated into launch moments, all reading and writing a shared system of record. Seven disciplines, four altitudes — a system, not a pile.
>
> | Layer | Adopt | Disciplines | Cadence |
> |-------|-------|-------------|---------|
> | **L1 · Strategy** — what we say / who we are | crawl | **Narrative** · TALE | always-on |
> | **L2 · Channels** — always-on engines that express the strategy (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · STAR | always-on (influencer episodic-leaning) |
> | **L3 · Orchestration** — the time-boxed moment across channels | run | **Product Launch** · RAMP | episodic |
> | **L4 · Protocol** — the shared system of record | — | 7 truth registries + working memory · 8 auditor gates · one skill contract | — |
>
> Narrative is the message; the channels are the mediums that express it. Each core builder records the exact narrative canon/version and claims projection offset it used. Each discipline's 4-phase loop lives inside its layer (Narrative = Trace → Architect → Land → Evaluate).

The per-discipline catalogs below follow the catalog order: Narrative → SEO/GEO → Social → Email → Paid → Influencer → Launch → Protocol. Note: "Activate" means creator outreach for influencer but account-gating for paid ads — same word, discipline-specific scope.

**Narrative — TALE (16):** phase directories under `narrative/` follow the TALE loop (Trace → Architect → Land → Evaluate). The Strategy (L1) layer — one brand voice every channel inherits; claims-ledger-aware throughout. `positioning-mapper` stays physically in `launch/` but reads logically as the front of TALE Trace.

| Phase | Skills |
|-------|--------|
| **Trace** | `narrative-baseline-mapper`, `category-narrative-mapper`, `audience-belief-mapper`, `positioning-truth-tracer` |
| **Architect** | `strategic-narrative-designer`, `message-system-architect`, `brand-language-codifier`, `story-bank-builder` |
| **Land** | `narrative-cascade-planner`, `pitch-narrative-builder`, `narrative-enablement-kit`, `proof-point-packager` |
| **Evaluate** | `narrative-quality-auditor` (separate truth/system/effectiveness gates), `message-test-designer`, `narrative-resonance-monitor`, `narrative-drift-monitor` |

Reused cross-discipline (counted in their home phases, not duplicated): `positioning-mapper` (Dunford canvas, launch home), `message-house-builder` (message spine, launch home), `audience-mapper` (persona/belief), `share-of-voice-tracker` (social home — resonance vs competitors). No new connector: narrative resonance reuses `bluesky.py`/`gdelt.py`/`tavily.py`/`wayback.py`. The narrative truth registry `narrative-registry` lives in the protocol layer.

**SEO/GEO — SITE (16):** phase directories under `seo-geo/` follow the SITE loop (Survey → Implement → Tune → Evaluate). Quality frameworks stay CORE-EEAT (content) + CITE (domain) — the loop brand and the benchmark names are separate.

| Phase | Skills |
|-------|--------|
| **Survey** | `keyword-research`, `competitor-analysis`, `serp-analysis`, `content-gap-analysis` |
| **Implement** | `content-writer`, `geo-content-optimizer`, `serp-markup-builder`, `page-play-builder` |
| **Tune** | `content-quality-auditor`, `technical-seo-checker`, `on-page-seo-checker`, `site-structure-optimizer` |
| **Evaluate** | `domain-authority-auditor`, `rank-tracker`, `performance-monitor`, `offsite-signal-analyzer` |

**Social — ECHO (16):** phase directories under `social/` follow the ECHO loop (Explore → Craft → Host → Observe). The asset gate and program-maturity profiles are separate constructs. Ships **no** posting/engagement/DM automation of any kind.

| Phase | Skills |
|-------|--------|
| **Explore** | `channel-portfolio-planner` (channel mix + fit), `voice-dossier-builder` (brand voice/persona canon), `platform-norm-profiler` (per-platform norms + rule guardrails), `participation-warmup-planner` (earn-your-presence ramp) |
| **Craft** | `social-calendar-builder` (cadence + pillars, capacity-governed), `social-creative-builder` (post/thread/carousel, claims-ledger-aware), `short-video-scripter` (short-form video scripts), `advocacy-program-designer` (employee/creator advocacy spec) |
| **Host** | `social-quality-auditor` (asset/program profile gate + pre-publish mode), `engagement-inbox-manager` (reply/mention triage), `social-selling-planner` (founder-led/social-selling motion), `crisis-response-planner` (escalation ladder + holding statements) |
| **Observe** | `social-pulse-monitor` (mentions + sentiment pulse), `share-of-voice-tracker` (SOV vs competitors), `dark-social-attributor` (unattributable-referral inference), `social-measurement-loop` (period-stable rollup back to memory) |

Reused cross-discipline (counted in their home phases, not duplicated): `trend-spotter` (cultural timing), `audience-mapper` (persona), `content-amplifier` ("boost this" repurposing), `outreach-manager` (creator/partner DMs), `competitor-tracker` (rival watch), `landing-optimizer` (post-click), `performance-analyzer`, `roi-calculator`, `report-generator`, `offer-claims-registry` (ECHO C1 claim compliance), `community-launch-runner` (launch-day community posts), `creator-registry`, `page-play-builder`, `memory-management`. The social truth registry `channel-registry` lives in the protocol layer.

**Email — SEND (16):** phase directories under `email/` follow the SEND loop (Setup → Engage → Nurture → Deliver). The auditor selects a declared promotional, retention, cold-outbound, or newsletter profile.

| Phase | Skills |
|-------|--------|
| **Setup** | `deliverability-qa` (SEND-S, the S1 auth pre-flight), `list-segment-builder` (segments + suppression), `list-growth-designer` (acquisition strategy + compliant capture-flow spec), `list-hygiene-monitor` |
| **Engage** | `email-creative-builder` (subject/preheader/body/CTA, message-matched, claims-ledger-aware), `subject-line-lab`, `email-render-builder`, `dynamic-content-personalizer` |
| **Nurture** | `email-sequence-designer` (lifecycle flows + frequency governance), `newsletter-monetization-planner` (paid-sub/sponsorship/referral economics), `preference-frequency-manager`, `reactivation-specialist` |
| **Deliver** | `email-quality-auditor` (EQS gate + pre-send go/no-go mode), `send-experiment-designer` (A/B + send-time + hold-out design; renamed from send-test-designer), `inbox-placement-monitor`, `cold-outbound-sequencer` |

Reused cross-discipline (counted in their home phases, not duplicated): `audience-mapper` (persona/lifecycle-stage), `landing-optimizer` (post-click), `roi-calculator` (revenue-per-send), `report-generator`, `performance-analyzer`, `offer-claims-registry` (D1 claim compliance). The email truth registry `consent-registry` lives in the protocol layer.

*Scope edge:* `list-growth-designer` (setup) owns the acquisition **strategy** + the compliant opt-in capture-flow **spec**; the signup-form/popup **UX** stays with `landing-optimizer`, the opt-in **record** with `consent-registry`, the confirmation **flow** with `email-sequence-designer`, and referral growth-loop **economics** with `newsletter-monetization-planner`. (`early-access-designer` in launch owns only the stage-ladder **design** + referral **mechanic spec** — same seams apply.)

**Paid Ads — ROAS (16):** phase directories under `ad/` follow the ROAS loop (Research → Orchestrate → Activate → Scale).

| Phase | Skills |
|-------|--------|
| **Research** | `campaign-architect`, `audience-segment-builder`, `search-term-miner`, `product-feed-optimizer` |
| **Orchestrate** | `ad-creative-builder`, `ad-test-designer`, `bid-strategy-planner`, `landing-experience-checker` |
| **Activate** | `ad-account-auditor` (RQS gate + launch go/no-go mode), `conversion-signal-qa`, `placement-exclusion-manager`, `conversion-value-mapper` |
| **Scale** | `paid-measurement-loop`, `attribution-reconciler`, `budget-pacing-monitor`, `fatigue-frequency-manager` |

Reused cross-discipline (counted in their home phases, not duplicated): `budget-optimizer` (spend allocation), `landing-optimizer` (post-click), `roi-calculator` (return math), `report-generator`, `performance-analyzer`.

**Influencer — STAR (16):** phase directories under `influencer/` follow the STAR loop (Scout → Target → Activate → Report). Loop and quality framework now share the name STAR (**S**uitability · **T**rust · **A**ppeal · **R**eturn), symmetric with ROAS/SEND/ECHO/RAMP/TALE.

| Phase | Skills |
|-------|--------|
| **Scout** | `audience-mapper`, `trend-spotter`, `influencer-discovery`, `fit-scorer` |
| **Target** | `competitor-tracker`, `campaign-planner`, `brief-generator`, `budget-optimizer` |
| **Activate** | `outreach-manager`, `creator-content-auditor`, `contract-helper`, `content-amplifier` |
| **Report** | `landing-optimizer`, `performance-analyzer`, `roi-calculator`, `report-generator` |

**Launch — RAMP (16):** phase directories under `launch/` follow the RAMP loop (Research → Assemble → Mobilize → Prove). Preflight, execution, and outcome are separate lifecycle profiles and are never averaged.

| Phase | Skills |
|-------|--------|
| **Research** | `positioning-mapper` (Dunford canvas: alternatives/attributes/beachhead), `launch-tier-planner` (tier + type + risk register + kill criteria), `launch-window-planner` (dates, competitor calendar, embargo windows), `early-access-designer` (waitlist→GA stage ladder + graduation criteria) |
| **Assemble** | `message-house-builder` (tagline/pillars/PR-FAQ spine, claims-ledger-aware), `launch-asset-packager` (tier-scoped manifest: press kit + store listing specs + technical go-live), `pricing-packaging-planner` (tiers/launch offers/guarantees), `sales-enablement-kit` (battle cards + talk track, sales-led only) |
| **Mobilize** | `launch-readiness-auditor` (typed lifecycle gate + T-1 go/no-go mode), `launch-day-conductor` (hour-blocked runbook, requires SHIP), `community-launch-runner` (PH/HN/directory/regional incl. 中文 channels, platform-rule guardrails), `press-media-relations` (media tiers + embargo pitch sequence + press release) |
| **Prove** | `launch-monitor` (T-0→T+30 telemetry, spike-vs-sustain), `launch-feedback-synthesizer` (theme triage + status loop + compliant social proof), `launch-retro-analyzer` (D1/W1/M1 actual-vs-target + 5-Whys), `momentum-planner` (anti second-week cliff, changelog-as-GTM, next moment) |

Reused cross-discipline (counted in their home phases, not duplicated): `audience-mapper` (ICP/persona), `trend-spotter` (cultural timing), `budget-optimizer`, `landing-optimizer` (launch page UX), `campaign-planner` (creator lane — "launch with creators" starts there), `outreach-manager` (pitch/follow-up mechanics for media + hunters), `content-amplifier` (repurposing + paid-amplification calendar), `email-creative-builder`/`email-sequence-designer`/`cold-outbound-sequencer` (email lanes), `campaign-architect`/`ad-creative-builder` (paid lane), `page-play-builder`/`content-writer` (pages/posts), `technical-seo-checker`/`serp-markup-builder` (go-live tech), `performance-monitor` (post-window monitoring), `roi-calculator`, `performance-analyzer`, `report-generator`, `offer-claims-registry` (A1 claim compliance). The launch truth registry `launch-registry` lives in the protocol layer.

**Protocol layer — cross-cutting (8):** shared truth & memory machinery outside the discipline phase-flows — 7 discipline-anchored truth registries (`entity-registry` → SEO/GEO, `creator-registry` → influencer, `offer-claims-registry` → paid, `consent-registry` → email, `launch-registry` → launch, `channel-registry` → social, `narrative-registry` → narrative) plus the cross-discipline `memory-management`. Counted separately. The auditor-class **gate role** spans 8 skills, all discipline-resident and counted there: `content-quality-auditor` (seo-geo/tune/), `domain-authority-auditor` (seo-geo/evaluate/), `creator-content-auditor` (influencer/activate/), `ad-account-auditor` (ad/activate/), `email-quality-auditor` (email/deliver/), `launch-readiness-auditor` (launch/mobilize/), `social-quality-auditor` (social/host/), `narrative-quality-auditor` (narrative/evaluate/).

| Group | Skills |
|-------|--------|
| **Protocol** | `entity-registry`, `creator-registry`, `offer-claims-registry`, `consent-registry`, `launch-registry`, `channel-registry`, `narrative-registry`, `memory-management` |

## One-Shot Commands

**Eight commands.** `/aaron-marketing:auto` infers intent across all disciplines; each discipline has one explicit entrypoint. Not sure? Use `/aaron-marketing:auto`:

```
/aaron-marketing:auto      — Infer marketing intent across all disciplines and run the smallest useful workflow (add --deep for exhaustive/stress-test)
/aaron-marketing:seo-geo   — SEO/GEO end-to-end (SITE loop: --phase survey|implement|tune|evaluate; per-phase flags preserved: --competitors/--map, --brief/--series/--refresh/--publish/--meta/--schema/--type, --full/--tech/--visibility, --authority/--alert/--report/--remember/--period)
/aaron-marketing:influencer    — Influencer (STAR loop): scout / target / activate / report (--phase to force a stage)
/aaron-marketing:ad      — Paid ads (ROAS loop): research / orchestrate / activate / scale (--phase to force a stage)
/aaron-marketing:email     — Email (SEND loop): setup / engage / nurture / deliver (--phase to force a stage)
/aaron-marketing:launch    — Product launch (RAMP loop): research / assemble / mobilize / prove (--phase to force a stage; "launch with creators" routes to campaign-planner instead)
/aaron-marketing:social    — Organic social (ECHO loop): explore / craft / host / observe (--phase to force a stage; "boost this" routes to content-amplifier, launch-day community posts to community-launch-runner)
/aaron-marketing:narrative — Brand narrative (TALE loop): trace / architect / land / evaluate (--phase to force a stage)
```

## Quality Frameworks

- **CORE-EEAT** ([references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/core-eeat-benchmark.md)): 80-item content quality framework (8 dimensions). GEO Score = CORE avg; SEO Score = EEAT avg. Three veto items: T04, C01, R10.
- **CITE** ([references/cite-domain-rating.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/cite-domain-rating.md)): 40-item domain authority framework (4 dimensions). Three veto items: T03, T05, T09.
- **STAR** ([references/star-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/star-benchmark.md)): influencer-marketing framework — **S**uitability · **T**rust · **A**ppeal · **R**eturn (4 dimensions × 10 items = 40). SQS = floor(profile-weighted arithmetic mean), the same rollup family as ROAS (RQS) and SEND (EQS). Veto items: STAR-S2/S6 (audience authenticity) and STAR-T1/T2/T3 (disclosure/claims/brand-safety) — IDs collide textually with SEND/ROAS/RAMP/TALE/CITE/CORE-EEAT, always qualify with the framework name.
- **ROAS** ([references/roas-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/roas-benchmark.md)): paid ads framework — R (Return), O (Offer), A (Audience), S (Spend-efficiency). RQS = arithmetic weighted-mean rollup (like CITE). Veto items: R1/R2/O1/O2/A1.
- **SEND** ([references/send-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/send-benchmark.md)): email marketing framework — S (Sender-integrity/deliverability), E (Engagement), N (Nurture/lifecycle), D (Direct-response/conversion). EQS = arithmetic profile-weighted-mean rollup (like ROAS). Veto items: S1/S2/N1/D1.
- **RAMP** ([references/ramp-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/ramp-benchmark.md)): product-launch framework — R (Readiness), A (Assets), M (Momentum), P (Proof); 40 stable IDs selected into separate preflight, execution, or outcome profiles. Never average lifecycle reads. Veto items: RAMP R1/A1/M1/P1 (IDs collide textually with ROAS R1/A1 — always qualify with the framework name).
- **ECHO** ([references/echo-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/echo-benchmark.md)): organic-social framework — E (Embeddedness), C (Craft), H (Hosting), O (Observability). Run either the asset gate or one program-maturity profile; never combine them. Veto items: ECHO E1/C1/C2/H1/H2/O1 (IDs collide textually with ROAS O1/O2 — always qualify with the framework name).
- **TALE** ([references/tale-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/tale-benchmark.md)): brand-narrative framework — T (Truth), A (Architecture), L (Landing), E (Evidence). Truth, system, and effectiveness profiles remain separate; full review links three results without an overall number. Veto items: TALE T1/A1/L1/E1 (IDs collide textually with other frameworks — always qualify with the framework name).

## Operating Contract

- Shared contract reference: [references/skill-contract.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/skill-contract.md)
- Shared state model: [references/state-model.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/state-model.md)
- Protocol roles (role assignments — the `protocol/` directory itself is 8 skills; the 8 gates live in their home disciplines; `creator-content-auditor`/`ad-account-auditor`/`email-quality-auditor`/`launch-readiness-auditor`/`social-quality-auditor`/`narrative-quality-auditor` play gate roles but are counted under their home disciplines):
  - `content-quality-auditor` = publish readiness gate
  - `domain-authority-auditor` = citation trust gate
  - `creator-content-auditor` = STAR gate (emits SQS)
  - `ad-account-auditor` = ROAS gate
  - `email-quality-auditor` = SEND gate
  - `launch-readiness-auditor` = RAMP gate
  - `social-quality-auditor` = ECHO asset/program profile gate
  - `narrative-quality-auditor` = TALE truth/system/effectiveness profile gate
  - `entity-registry` = canonical entity profile
  - `creator-registry` = canonical creator roster/dossier (influencer truth SSOT)
  - `offer-claims-registry` = offer & claim-substantiation record (paid truth SSOT)
  - `consent-registry` = per-subject consent/suppression record (email truth SSOT)
  - `launch-registry` = canonical launch event owner and dossier/calendar projector (T-0 proposals resolve individually in offset order)
  - `channel-registry` = canonical channel roster/dossier (social truth SSOT)
  - `narrative-registry` = canonical brand-narrative canon/dossier (narrative truth SSOT)
  - `memory-management` = campaign memory loop
- Hook automation: `hooks/hooks.json` — seven command-backed events: SessionStart combined-budget memory/integrity context plus opt-in active-run resume, UserPromptSubmit, PreToolUse exact-path privacy preflight, PostToolUse and PostToolUseFailure post-state checks, PostToolBatch bounded namespace/sink sweep, and a first-Stop sweep with the required active-stop loop guard. Run lifecycle emission requires `AARON_ACTIVE_RUN_ID` plus stable host IDs and stores only hashed identity/typed metadata.
- Temperature memory: HOT (`memory/hot-cache.md`, 80 lines, auto-loaded) / WARM (`memory/` subdirs) / COLD (`memory/archive/`)
- Dual truncation: HOT tier limited to 80 lines AND 25KB (whichever triggers first)

## Inter-Skill Handoff

When a skill recommends running another, pass the standard shape from `references/skill-contract.md` §Handoff Summary Format: status (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_INPUT), objective, key findings/output, evidence (each labeled Measured/User-provided/Calculated/Estimated/Proxy), assumptions, open loops, and the recommended next skill. The 8 auditor-class gates additionally emit `cap_applied`, `raw_overall_score`, and `final_overall_score` per `references/auditor-runbook.md` §5.

If `memory-management` is active, prior audit results load automatically from the hot cache.

## Tool Connector Pattern

Skills use `~~category` placeholders (e.g., `~~SEO tool`, `~~analytics`). Every skill works without any integrations (Tier 1). [CONNECTORS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/CONNECTORS.md) documents a verified **free/keyless data recipe for each category** — Google Search Console & GA4 (own data), PageSpeed/CrUX, Wikidata SPARQL, Common Crawl, Wayback CDX, Open PageRank, advertools, plus **Resend** for `~~email platform` (free-tier key; `scripts/connectors/resend.py` — domain-auth status, seed-test sends, suppression sync, broadcasts; mutating subcommands dry-run by default, `--live` to execute) and two **keyless hosted fetchers** — **Firecrawl** for `~~web crawler`/`~~SEO tool` (`scripts/connectors/firecrawl.py` — live SERP + JS-rendered scrape + site map, ~1,000 free credits/mo) and **Tavily** for `~~AI monitor`(proxy)/`~~SEO tool`/`~~trend database` (`scripts/connectors/tavily.py` — scored search, `--answer` AI-citation probe, news pulse, URL extract), both with a local robots.txt pre-flight and `--own-site` override — plus three **keyless public-API connectors** — `doh.py` (DNS-over-HTTPS email-auth records — the any-ESP SEND-S1 record pull), `pageviews.py` (Wikipedia attention series), `gdelt.py` (GDELT global news mentions, `~~brand monitor`; ≥5s between calls) — plus `youtube.py` (free-key YouTube Data API creator metrics, shortlist-vetting scope) and the mutation-class `indexpush.py` (IndexNow + 百度普通收录 index push; dry-run default, `--live` to submit) — plus three **launch-telemetry connectors** for `~~launch platform`/`~~app store data`: `hn.py` (keyless — Algolia HN Search 10k req/hr/IP + official Firebase v0; brand mentions, live rank polling, the comments>points ratio fact; numeric filters auto-route to `search_by_date`), `producthunt.py` (free developer token, GraphQL v2, 6,250 complexity/15 min; **non-commercial ToS — business use needs hello@producthunt.com, attribution required**; daily top-N / post / topic), and `appstore.py` (keyless documented endpoints only — iTunes Search/lookup at ~20 calls/min official guidance + charts via `rss.marketingtools.apple.com`; customerreviews RSS is a zombie → manual recipe; private-header endpoints rejected) — plus three **keyless social connectors** for `~~social platform`: `bluesky.py` (Bluesky/AT-Proto public app-view — profile/posts/search), `fediverse.py` (Mastodon/Fediverse public timelines + hashtag search), and `discourse.py` (public Discourse-forum JSON — topics/posts/activity), joined by a `youtube.py --rss` extension (keyless channel-feed pull, no API key) — while `threads.py` stays recipe-only for now (free-key but Meta developer-app setup hurdle) and Reddit degrades to the `.rss` recipe (keyless `.json` returns 403); the discipline ships **no** posting/engagement/DM automation of any kind — so skills can pull real data with zero paid-tool dependency. The narrative discipline adds **no new connector** — its resonance/drift monitors reuse the existing `bluesky.py`/`gdelt.py`/`tavily.py`/`wayback` recipes. MCP servers catalogued in `docs/mcp-catalog.json` (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, the self-hosted free **OpenSEO** suite, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack, Resend, the keyless Firecrawl and Tavily) are an **opt-in** Tier 2/3 automation layer — the catalog is kept outside the plugin-root `.mcp.json` path that Claude Code auto-registers (and `plugin.json` carries no `mcpServers` key), so installing the plugin adds nothing to the user's `/mcp` list; users copy the entries they want into their own MCP config.

## Contribution Rules

- All `SKILL.md` files must include: `name`, `version`, `description`, `license`, `compatibility`, `metadata` frontmatter. `metadata` must be a **single-line strict-JSON object** (OpenClaw's parser reads single-line keys only; the validator fails block maps) carrying `author`/`version`/`discipline`/`phase` plus the `hermes` (tags/category) and `openclaw` (emoji/homepage) host extensions. Recommended: `when_to_use` (underscores, not hyphens) and `argument-hint`.
- `plugin.json` must include: `name` (the spec-required identifier) and `description` at top level, plus `id` (the marketplace identity key downstream tooling references). Commands are auto-discovered from `./commands/`; skills are listed as directory paths.
- Keep each `SKILL.md` focused — move long detail into `references/` subdirectories. The eight auditor-class gate skills (`content-quality-auditor`, `domain-authority-auditor`, `creator-content-auditor`, `ad-account-auditor`, `email-quality-auditor`, `launch-readiness-auditor`, `social-quality-auditor`, `narrative-quality-auditor` — discipline-resident, not protocol-layer) `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT: handoff schema, cap method, Artifact Gate, translation format) via a plugin-relative path, and keep only their **framework-specific** §2 worked examples, §3 guardrails, and §5 translation inline (CORE-EEAT / CITE / STAR / ROAS / SEND / RAMP / ECHO / TALE diverge and must not be byte-identical). All intra-repo links in `SKILL.md`/`references/` are plugin-relative paths, never `blob/main` GitHub URLs — the validator enforces this.
- High-volume `references/` packs should prefer compact starter templates, step matrices, and checklists over long worked outlines. Keep canonical examples only where they materially improve execution quality.
- After updating a skill, keep the **authoritative 10 tracking surfaces** in step as listed in [CONTRIBUTING.md §6](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/CONTRIBUTING.md).
- Design philosophy: skills are content (Markdown). All code is **zero-dependency Python-stdlib/bash** under `scripts/`, in three classes: (1) validators & generators (`validate-skill.sh`, `check-*.py`/`.sh`, `generate-*.py`), (2) deterministic runtimes invoked per `references/runtime-invocation.md` (`rubric-score.py`, `context-resolver.py`, `registry-events.py`, `run-events.py`, `audit-loop.py`, `audit-trends.py`, `validate-audit-artifact.py`), (3) connector helpers under `scripts/connectors/` that pull public/own data locally so skills don't need external tools (see [CONNECTORS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/CONNECTORS.md)). No third-party / `pip` dependencies.
- Keep the shared contract and state-model language consistent with `references/skill-contract.md` and `references/state-model.md`.
- Branch naming: `feature/skill-name`, `fix/skill-name`, `docs/description`

## CLI Tools

System PATH in Claude Code sessions is minimal (`/usr/bin:/bin:/usr/sbin:/sbin`). Tools installed via Homebrew or npm are NOT on PATH by default. Always use absolute paths:

- **gh** (GitHub CLI): `/opt/homebrew/bin/gh`
- **node**: `/usr/local/bin/node`
- **bun**: `~/.bun/bin/bun`

Or prepend PATH at start of command: `export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"; gh ...`

### GitHub Release

```bash
/opt/homebrew/bin/gh release create vX.Y.Z --title "title" --notes "body"
```

> [AGENTS.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/AGENTS.md) · [README.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/README.md)
