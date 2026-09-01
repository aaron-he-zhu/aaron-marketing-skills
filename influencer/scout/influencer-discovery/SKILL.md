---
name: influencer-discovery
slug: influencer-discovery
displayName: "Influencer Discovery · 红人发现"
summary: "多平台红人挖掘:候选池、证据画像、真实性红旗筛查与 Fit 就绪队列"
description: 'Use when the user asks to "find influencers", "build an influencer list", or "discover creators in [niche]"; produces a multi-platform candidate pool, per-influencer evidence profiles, authenticity red-flag screening, and a Fit-readiness queue without action ranking. Not for STAR scoring or ranking a known shortlist — use fit-scorer. 达人挖掘/找达人/创作者名单'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when building an influencer roster from scratch, expanding into a new platform or niche, replacing churned partners, finding micro and nano creators at scale, identifying which influencers a competitor partners with, or standing up an always-on discovery pipeline. The user names a niche, platform, follower band, or brand and wants a list of candidate creators to evaluate."
argument-hint: "<brand or niche> [platform] [follower-range]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "scout", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "scout"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Influencer Discovery

Find evidence-backed creator candidates across platforms, screen them against declared discovery filters, and build a non-ranked readiness queue for typed Fit evaluation.

## Quick Start

```
Find 20 influencers in [niche] for [brand/product]
```

```
Find influencers in [niche] with 50K-200K followers on TikTok and Instagram,
based in [location], engagement above 4%, who have worked with brands like [brand]
```

## Skill Contract

- **Reads**: brand/product, niche or category, target platforms, follower range, engagement floor, decision-relevant geography/language, audience demographics, exclusions; dated candidate records from a user export, public source, roster, or live connector; the current campaign's STAR `evidence_window` when supplied; prior `entity-registry` brand profile and any `audience-mapper` output if present in memory; existing roster records under `memory/creators/` (dedupe only through verified identity links against creators already rostered by [creator-registry](../../../protocol/creator-registry/SKILL.md)).
- **Writes**: return discovery results inline by default; only with separate exact authorization, save them to `memory/influencer/influencer-discovery/YYYY-MM-DD-<topic>.md`. A saved artifact uses a stable opaque `creator_ref` plus pseudonymous `recipient_ref`, `contact_source_ref`, and `agency_ref`, keeps raw handles, profile URLs, and contact coordinates transient-only, and retains geography only at the granularity required by the declared filter. Save an opaque `handle_ref`/`source_ref` identity resolver only when the authorized source artifact or verified creator-registry link can resolve it. Without one, keep `identity_status: unresolved`, save no hidden raw-locator mapping, and set `cross_session_locator_required: true`. Reuse a verified creator-registry aggregate ID when one exists; otherwise generate `creator-<UUIDv4>` once for the candidate lineage. Never set `creator_ref` to a raw handle, name, URL, email, provider ID, or a deterministic hash of any of them. Each roster-worthy creator update requires another exact authorization for an `operation: propose` request through `registry-events.py` to `memory/events/creators.ndjson`; only `creator-registry` writes canonical records under `memory/creators/`.
- **Promotes**: only with separate exact authorization, durable facts (verified creator/handle refs, confirmed niche/platform coverage, competitor-saturated creators) to `memory/hot-cache.md`; discovery readiness or queue position is not a durable ranking fact.
- **Done when**:
  - The required search criteria are present; otherwise stop with `NEEDS_INPUT` and name the missing criteria without fabricating candidates.
  - Exactly two raw locators without complete criteria/evidence remain `NEEDS_INPUT`, not a vetted shortlist. A separately authorized partial checkpoint is labeled `PARTIAL`, lists every gap, and contains no tier or rank.
  - A candidate pool exists with at least the requested count screened past follower, engagement, and brand-safety filters.
  - Each candidate has a field-level evidence trail (`provider/tool`, `source_ref`, `observed_at`, window, evidence label), an audience read, and an evidence-completeness triage state (`READY_FOR_FIT | NEEDS_REFRESH | INELIGIBLE`) that is neither a score nor a STAR Suitability verdict.
  - Every candidate keeps one stable opaque `creator_ref` across the report and handoff; raw identity locators remain transient and are never copied into `creator_ref`.
  - Conflicting observations remain separate, identity merges have a verified cross-link, and the Fit handoff marks each volatile field `current`, `stale`, or `unknown` against the current STAR `evidence_window` with any `refresh_required` fields named.
  - A non-ranked Fit-readiness queue is compiled with next-step pointers; every stale/unknown required field produces `NEEDS_REFRESH`, `NOT_RANKED`, and `NEEDS_INPUT` until refreshed.
- **Primary next skill**: [fit-scorer](../fit-scorer/SKILL.md) — score and rank the discovered candidates with weighted criteria.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

Planning and screening need no live integration (Tier 1), but a real creator list still needs candidate records: public handles/links or an export supplied by the user, existing roster records, or a live search connector. Search criteria alone are not evidence that any specific creator or metric exists. If no candidate source is available, return a query/collection plan and `NEEDS_INPUT`; never invent handles, profiles, counts, or audience data.

Normalize evidence only in the report template, not through a new ingestion layer. For every factual field retain `provider/tool`, `source_ref`, `observed_at`, the measurement window (or `not-supplied`), and one label: `Measured`, `Calculated`, `Estimated`, `User-provided`, or `Proxy`. Keep conflicting values for the same field as parallel observations; do not average them, prefer the newest automatically, or merge identities from names/handles alone. A cross-provider identity becomes one creator only after a verified cross-link or explicit user confirmation.

Where a tool *could* sharpen results, use `~~` connector placeholders:

- `~~influencer database` — bulk discovery, follower/engagement metrics, audience demographics.
- `~~social platform analytics` — native creator-marketplace data, trending sounds, related accounts.
- `~~CRM` — surface possible existing-partner matches for verified identity-link review; never auto-merge records.
- `~~audience overlap` — estimate creator-audience vs. brand-audience match.

**Keyless candidate-card metadata (oEmbed)**: YouTube (`https://www.youtube.com/oembed?url=<video-url>&format=json`), TikTok (`https://www.tiktok.com/oembed?url=<post-url>`), and X (`https://publish.twitter.com/oembed?url=<post-url>`) return a post's title, author name/handle, and thumbnail with **no key** — enough to resolve a candidate transiently and retain an opaque verified-handle evidence ref instead of hand-copying identity data. A handle ref remains separate from `creator_ref`: only an explicitly carried upstream `creator_ref` or a verified creator-registry identity link may resolve the aggregate; otherwise create a fresh random opaque ref and preserve the identity gap. Metadata only: no follower or engagement metrics, so those stay `~~influencer database` or manual export — **except YouTube**, below.

**Measured YouTube metrics (free key)**: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" channel @handle` returns the real displayed subscriber count, total views, and video count, and `youtube.py videos @handle --limit 10` adds per-video views/likes/comments — upgrading a YouTube candidate's profile row from Estimated to **Measured**. Free `YOUTUBE_API_KEY` (10,000 units/day; one channel check ≈ 1–3 units). ToS boundary: vet a **named shortlist**, don't build a bulk creator database — quota extensions are refused for competitive harvesting. See [scripts/connectors/README.md](../../../scripts/connectors/README.md).

See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category and the opt-in MCP layer. None are required — every step degrades to user-supplied inputs.

## Instructions

Each step has a fill-in block in [references/templates.md](references/templates.md) — copy the matching block. This skill does *not* compute a per-influencer score, STAR Suitability verdict, outreach priority, or action rank. It records evidence completeness and declared-filter results; [fit-scorer](../fit-scorer/SKILL.md) owns typed comparison and ranking downstream.

1. **Define search criteria.** Capture brand, goal, audience definition, budget/follower tier, platforms, engagement floor, location/language, exclusions, and the required/preferred parameter table. If any required criterion is missing, stop with `NEEDS_INPUT`; offer [audience-mapper](../audience-mapper/SKILL.md) only when the user wants help defining the audience. Step 1 template.
2. **Conduct the search.** Work hashtags, similar-accounts, competitor mentions, and platform-native discovery. Raw handles/profile URLs may appear only in Step 2's transient lookup block and must be removed before any save or handoff. Log the saved-safe batch with `creator_ref`, identity status, opaque `handle_ref`/`source_ref` when resolvable, provider/tool, query purpose, `observed_at`, window, and evidence label. If no public handles/links, user export, roster records, or live search connector can supply candidate records, produce the exact query pack and collection template, return `NEEDS_INPUT`, and stop before naming creators. Step 2 template.
3. **Initial screening.** Filter the pool on follower range, engagement, recency, relevance, and brand safety; tally red flags (suspected fake followers, controversy, competitor exclusivity, inactivity). These are discovery signals, not verified STAR failures or vetoes; unsupported applicable evidence remains Unknown for downstream scoring. Per-platform reading cues: [references/platform-vetting.md](references/platform-vetting.md). Step 3 template.
4. **Build influencer profiles.** For each qualified creator, first reuse an explicitly carried opaque `creator_ref` or a creator-registry aggregate ID whose handle link is verified. If neither exists, generate one random `creator-<UUIDv4>` and reuse it unchanged throughout this report lineage. Never derive it from a handle or other identity data. Save an opaque handle/evidence ref only when an authorized artifact or verified registry link resolves it; otherwise keep `identity_status: unresolved`, create no hidden locator map, and require the raw locator again in a later session. Then fill the profile (pseudonymous identity refs, field-level metrics and audience evidence, content, partnership history, contact-path refs, and evidence-completeness triage state). Preserve conflicts as parallel rows and merge provider identities only after a verified cross-link. Compare each volatile observation with the current campaign's STAR `evidence_window`: within it is `current`; outside it is `stale`; a missing window/date or absent STAR window is `unknown`. A stale or unknown required field stays visible, becomes `refresh_required`, and forces `triage_state: NEEDS_REFRESH`, `ranking_status: NOT_RANKED`, and `NEEDS_INPUT`; never invent a global TTL. Do not emit a score, recommendation tier, or STAR Suitability verdict. For a deep single-creator read with a contact waterfall, use [references/creator-dossier.md](references/creator-dossier.md). Step 4 template.
5. **Compile the discovery report.** Roll profiles into summary stats, descriptive platform/follower-band breakdowns, and three non-ranked evidence queues: `READY_FOR_FIT`, `NEEDS_REFRESH`, and `INELIGIBLE` under the declared filters. Do not recommend a creator mix, label anyone Priority/Highly Recommended, or action-rank candidates before typed Fit. If the input is only two raw locators and criteria/evidence are incomplete, return `NEEDS_INPUT` and do not save a vetted pool. A partial checkpoint requires separate exact save authorization, must say `PARTIAL`/`NOT_VETTED`, list criteria/evidence gaps, and contain no rank, score, “top” label, or fit-scorer handoff. Step 5 template.
6. **Add insights.** Note niche content trends, the competitive picture, and recommendations for future searches. Step 6 template.

Return the discovery report inline. Saving the report, caching the shortlist, and submitting each roster-worthy creator through `registry-events.py` as `operation: propose` are three separate operations and each requires exact authorization; without it, offer the eligible path and write nothing. After a vetted shortlist exists, hand [fit-scorer](../fit-scorer/SKILL.md) the field-level evidence plus the STAR `evidence_window`, `freshness_status`, and `refresh_required` list; if no current STAR window exists, mark freshness `unknown` rather than inventing one. `fit-scorer` records the S1-S10 evidence read; [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) alone determines verified STAR vetoes and renders the gate verdict.

## Compact Example

**User**: "Find 15 micro-influencers (10K-100K followers) in sustainable fashion for a new eco clothing brand."

**Illustrative output when a dated export or live connector returned candidate records**: create one field-level evidence profile per opaque `creator_ref`, then place each row in `READY_FOR_FIT`, `NEEDS_REFRESH`, or `INELIGIBLE` under the declared filters. All rows remain `NOT_RANKED`; stale/unknown required fields are `NEEDS_INPUT`, and only the current complete rows hand off to `fit-scorer`. Without candidate records, return only the query/collection plan and `NEEDS_INPUT`. The report is returned inline, then save, promotion, and registry-proposal permissions are offered separately. Full walkthrough in [references/templates.md](references/templates.md#worked-example--sustainable-fashion-micro-influencers).

## Reference Materials

- [references/templates.md](references/templates.md) — all step fill-in blocks (criteria, search, screening, profile, report, insights), the worked example, tips, and the "what/when" overview.
- [references/platform-vetting.md](references/platform-vetting.md) — per-platform creator playbooks (X/LinkedIn/TikTok/YouTube/Reddit) feeding screening and profiling in steps 3-4.
- [references/creator-dossier.md](references/creator-dossier.md) — structured per-creator dossier from public data, with a contact-discovery waterfall.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipes and opt-in MCP layer.
- STAR benchmark at [references/star-benchmark.md](../../../references/star-benchmark.md) — scoring framework that fit-scorer applies downstream.
- Siblings in the scout phase: [fit-scorer](../fit-scorer/SKILL.md), [audience-mapper](../audience-mapper/SKILL.md), [trend-spotter](../trend-spotter/SKILL.md).

## Next Best Skill

**Primary**: [fit-scorer](../fit-scorer/SKILL.md) — score and rank the discovered candidates with weighted criteria before outreach.

**Alternates (same influencer family)**:
- [competitor-tracker](../../target/competitor-tracker/SKILL.md) — when discovery surfaced competitor-saturated creators and you want to map the competitive field first.
- [audience-mapper](../audience-mapper/SKILL.md) — when the target audience is still fuzzy and criteria need sharpening before a re-search.

**Termination**: Maintain a visited-set. If a skill has already been invoked this session, stop and report chain-complete rather than re-invoking it. Max chain depth is 3 hops from the originating request; stop and summarize when reached.

## Related Skills

- [audience-mapper](../audience-mapper/SKILL.md) - Define who to reach
- [fit-scorer](../fit-scorer/SKILL.md) - Score and rank discovered influencers
- [competitor-tracker](../../target/competitor-tracker/SKILL.md) - Find competitor influencers
- [outreach-manager](../../activate/outreach-manager/SKILL.md) - Contact discovered influencers
