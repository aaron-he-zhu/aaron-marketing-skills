---
description: "SEO/GEO end-to-end along the SITE loop: survey demand and competitors, implement content, tune quality/tech/on-page, and evaluate authority/rankings/reports/memory (--phase survey|implement|tune|evaluate). Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-url-topic-or-domain> [--phase survey|implement|tune|evaluate] [phase flags]"
---

# SEO/GEO Command

Run the SEO/GEO lifecycle along the **SITE loop** (Survey → Implement → Tune → Evaluate) — the single SEO/GEO entrypoint (peer of `/aaron-marketing:influencer` and `/aaron-marketing:ad`). Skills score on [CORE-EEAT](../references/core-eeat-benchmark.md) (content) and [CITE](../references/cite-domain-rating.md) (domain authority).

## Route

Infer the SITE-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Survey** — keyword-research, serp-analysis, content-gap-analysis, competitor-analysis, offsite-signal-analyzer (backlinks mode), entity-registry, site-structure-optimizer (linking mode)
- **Implement** — content-writer (new/refresh modes), geo-content-optimizer, serp-markup-builder (meta/schema modes), site-structure-optimizer, content-quality-auditor (pre-publish gate); by page intent: page-play-builder (`--type programmatic` bulk/template · `parasite` third-party-platform · `comparison` "X vs Y"/alternatives · `local` local/GMB)
- **Tune** — on-page-seo-checker, content-quality-auditor, technical-seo-checker, site-structure-optimizer (with --full or --tech), geo-content-optimizer
- **Evaluate** — domain-authority-auditor (CITE citation-trust gate), rank-tracker, performance-monitor (report/alert modes), offsite-signal-analyzer (ai-referrals mode), memory-management, entity-registry

## Rules

**Phase selection**: honor `--phase` when given. Without it, infer from the goal (a topic/market → survey; a brief/draft/series → implement; a URL/domain to evaluate → tune; authority/rankings/alerts/reports/memory → evaluate); if ambiguous, ask one concise blocking question instead of guessing.

### --phase survey

- Discover search demand, SERP intent, topic clusters, and content opportunities; keep AI-answer-inclusion diagnosis in `--phase tune --visibility`.
- With `--competitors`, compare across rankings, content coverage, backlinks, authority, and AI citation visibility; return a battlecard, gaps, priority opportunities, and evidence mode.
- For the `competitor_gap` scenario (`--competitors`), explicitly run both `data_insufficient` and `geo_visibility_claim`; require competitors, market, and domain as blocking inputs. AI citation visibility is not an optional metric that may be estimated: without observed query, market/locale, engine, date, and citation evidence, keep the AI gap Unknown/`NEEDS_INPUT` and do not claim it.
- With `--map` (or a known opportunity set), turn findings into a content architecture, topic/entity map, and internal-link plan: clusters, pillar/supporting pages, orphan risks, anchor guidance, and next briefs.
- Keep evidence mode visible (tool vs. estimate); hand off to `--phase implement` for production.

### --phase implement

- Default (no flag): write ONE asset — SEO structure, GEO answer-ready elements, metadata suggestions, proof requirements, and open quality risks. Use provided survey/brief evidence when available; ask for missing blocking inputs.
- `--brief`: turn demand, intent, audience, and evidence into a single executable brief (angle, target keyword, intent, outline, proof requirements, GEO structure, internal-link notes, quality risks).
- `--series`: plan / write / continue a content series. Default a topic to planning and a valid series_plan to writing; cap at 3 articles per run (≤6 with chunking); return stable `series_plan` / `batch_summary` continuation state. A batch cannot be `ready` unless every article has full veto-aware audit coverage.
- `--refresh`: diagnose freshness, decay, outdated facts, and ranking loss; return a refresh plan, evidence gaps, update scope, and quality-gate status.
- `--publish`: prepare a CMS-neutral publish package (quality gate + metadata + schema + media + internal-link checks); do not publish directly. Allow `ready` only with full veto-aware audit coverage at SHIP, `cap_applied: false`, no BLOCKED status, no veto/blocker open loops, no unresolved required evidence, and `ready_verdict_allowed: true`.
- `--meta`: title / meta / Open Graph variants only. `--schema`: JSON-LD only; never invent unsupported rich-result facts.
- Do not claim publish-ready status without `--phase tune` or `--publish` quality-gate evidence.
- `--type article|landing|faq|comparison` names the content type when known.

### --phase tune

- Default (page audit): check on-page SEO, metadata, headings, images, links, and CORE-EEAT risk. Return `ready`, `ready_with_concerns`, `blocked`, or `needs_input` with evidence and next fixes. Use `--full` to run the full publish-readiness gate when evidence is available.
- `--tech`: crawlability, indexation, Core Web Vitals, mobile, security, structured-data exposure, robots, sitemap, canonical, redirect, and migration risk. Do not guess CWV or crawl data; mark missing evidence and next checks.
- `--visibility`: AI answer inclusion and GEO citation readiness, entity clarity, and trust blockers. Do not claim observed citation proof; require content-quality-auditor before any publish-ready, cite-ready, or GEO Score readiness verdict.
- Do not produce a publish-ready verdict without full veto-aware audit coverage.

### --phase evaluate

- Default: monitor rankings and SERP-position movement via rank-tracker; persist ranking history to project memory only when the user explicitly permits memory writes.
- `--authority`: CITE / domain-trust analysis, backlink quality, and entity credibility via domain-authority-auditor; flag trust blockers, toxic-link risks, missing entity proof, and authority-building opportunities. `--competitors` adds comparison.
- `--alert`: design thresholds and notifications via performance-monitor (alert mode); require metric source, threshold owner, and notification channel before setup; do not enable external alerts without explicit approval.
- `--report`: require exactly one scope (domain, campaign, project, or period); report traffic, rankings, AI citations/readiness, authority, technical health, content progress, and open loops; keep source/date freshness visible and separate observed data from estimates. `--period <range>` sets the reporting period.
- `--remember`: memory-management owns the HOT/WARM/COLD lifecycle — capture, promote, demote, archive, query, restore-from-archive — plus cleanup, purge, and protocol aggregation; canonical entity profiles route to entity-registry. Restore looks up a matching `memory/archive/YYYY-MM-DD-*` file. Purge/GDPR/CCPA requests require scoped targets and delete or anonymize matching canonical and archived memory surfaces. Within SEO/GEO, a gate veto from content-quality-auditor or domain-authority-auditor becomes a HOT **promotion candidate** that memory-management applies only with the standard memory-write permission — auditor-class gates hold no automatic hot-cache append power, here or in any other discipline (see the promotion rules under `protocol/memory-management`).

- **Scope edge — organic search vs neighbors**: durable message canon and voice live with narrative ([message-system-architect](../narrative/architect/message-system-architect/SKILL.md) et al.) — content here *expresses* that canon; machine-facing entity facts are [entity-registry](../protocol/entity-registry/SKILL.md) (consulted, never redefined); paid search/PMax structure is [campaign-architect](../ad/research/campaign-architect/SKILL.md); post-click CRO on landing pages is [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md); repurposing/boosting a published asset starts at [content-amplifier](../influencer/activate/content-amplifier/SKILL.md); launch-window go-live tech items stay with this discipline's [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md) / [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md) but are *scheduled* by launch's asset packager.
## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
