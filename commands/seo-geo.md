---
description: "SEO/GEO end-to-end from one entrypoint: research demand and competitors, create content, audit quality/tech/visibility/authority, and track rankings/reports/memory (--mode research|create|audit|track). Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-url-topic-or-domain> [--mode research|create|audit|track] [mode flags]"
---

# SEO/GEO Command

The single SEO/GEO entrypoint (peer of `/aaron-marketing:impact` and `/aaron-marketing:paid`). Four modes cover the discipline end-to-end; the former `research` / `create` / `audit` / `track` commands are these modes — every sub-flag is preserved unchanged.

## Route

- **research** — keyword-research, serp-analysis, content-gap-analysis, competitor-analysis, offsite-signal-analyzer (backlinks mode), entity-optimizer, site-structure-optimizer (linking mode)
- **create** — keyword-research, serp-analysis, content-gap-analysis, content-writer (new/refresh modes), geo-content-optimizer, serp-markup-builder (meta/schema modes), site-structure-optimizer, content-quality-auditor; by page intent: page-play-builder (`--type programmatic` bulk/template · `parasite` third-party-platform · `comparison` "X vs Y"/alternatives · `local` local/GMB)
- **audit** — on-page-seo-auditor, content-quality-auditor, technical-seo-checker, site-structure-optimizer (with --full or --tech), geo-content-optimizer, entity-optimizer, domain-authority-auditor, offsite-signal-analyzer (backlinks mode)
- **track** — rank-tracker, performance-monitor (report/alert modes), offsite-signal-analyzer (ai-referrals mode), memory-management, entity-optimizer

## Rules

**Mode selection**: honor `--mode` when given. Without it, infer from the goal (a topic/market → research; a brief/draft/series → create; a URL/domain to evaluate → audit; rankings/alerts/reports/memory → track); if ambiguous, ask one concise blocking question instead of guessing.

### --mode research

- Discover search demand, SERP intent, topic clusters, and content opportunities; keep AI-answer-inclusion diagnosis in `--mode audit --visibility`.
- With `--competitors`, compare across rankings, content coverage, backlinks, authority, and AI citation visibility; return a battlecard, gaps, priority opportunities, and evidence mode.
- With `--map` (or a known opportunity set), turn findings into a content architecture, topic/entity map, and internal-link plan: clusters, pillar/supporting pages, orphan risks, anchor guidance, and next briefs.
- Keep evidence mode visible (tool vs. estimate); hand off to `--mode create` for production.

### --mode create

- Default (no flag): write ONE asset — SEO structure, GEO answer-ready elements, metadata suggestions, proof requirements, and open quality risks. Use provided research/brief evidence when available; ask for missing blocking inputs.
- `--brief`: turn demand, intent, audience, and evidence into a single executable brief (angle, target keyword, intent, outline, proof requirements, GEO structure, internal-link notes, quality risks).
- `--series`: plan / write / continue a content series. Default a topic to planning and a valid series_plan to writing; cap at 3 articles per run (≤6 with chunking); return stable `series_plan` / `batch_summary` continuation state. A batch cannot be `ready` unless every article has full veto-aware audit coverage.
- `--refresh`: diagnose freshness, decay, outdated facts, and ranking loss; return a refresh plan, evidence gaps, update scope, and quality-gate status.
- `--publish`: prepare a CMS-neutral publish package (quality gate + metadata + schema + media + internal-link checks); do not publish directly. Allow `ready` only with full veto-aware audit coverage at SHIP, `cap_applied: false`, no BLOCKED status, no veto/blocker open loops, no unresolved required evidence, and `ready_verdict_allowed: true`.
- `--meta`: title / meta / Open Graph variants only. `--schema`: JSON-LD only; never invent unsupported rich-result facts.
- Do not claim publish-ready status without `--mode audit` or `--publish` quality-gate evidence.
- `--type article|landing|faq|comparison` names the content type when known.

### --mode audit

- Default (page audit): check on-page SEO, metadata, headings, images, links, and CORE-EEAT risk. Return `ready`, `ready_with_concerns`, `blocked`, or `needs_input` with evidence and next fixes. Use `--full` to run the full publish-readiness gate when evidence is available.
- `--tech`: crawlability, indexation, Core Web Vitals, mobile, security, structured-data exposure, robots, sitemap, canonical, redirect, and migration risk. Do not guess CWV or crawl data; mark missing evidence and next checks.
- `--visibility`: AI answer inclusion and GEO citation readiness, entity clarity, and trust blockers. Do not claim observed citation proof; require content-quality-auditor before any publish-ready, cite-ready, or GEO Score readiness verdict.
- `--authority`: CITE / domain-trust analysis, backlink quality, and entity credibility; flag trust blockers, toxic-link risks, missing entity proof, and authority-building opportunities. `--competitors` adds comparison.
- Do not produce a publish-ready verdict without full veto-aware audit coverage.

### --mode track

- Default: monitor rankings and SERP-position movement via rank-tracker; persist ranking history to project memory only when the user explicitly permits memory writes.
- `--alert`: design thresholds and notifications via performance-monitor (alert mode); require metric source, threshold owner, and notification channel before setup; do not enable external alerts without explicit approval.
- `--report`: require exactly one scope (domain, campaign, project, or period); report traffic, rankings, AI citations/readiness, authority, technical health, content progress, and open loops; keep source/date freshness visible and separate observed data from estimates. `--period <range>` sets the reporting period.
- `--remember`: memory-management owns the HOT/WARM/COLD lifecycle — capture, promote, demote, archive, query, restore-from-archive — plus cleanup, purge, and protocol aggregation; canonical entity profiles route to entity-optimizer. Restore looks up a matching `memory/archive/YYYY-MM-DD-*` file. Purge/GDPR/CCPA requests require scoped targets and delete or anonymize matching canonical and archived memory surfaces. Within SEO/GEO, only content-quality-auditor and domain-authority-auditor may append one veto marker to `memory/hot-cache.md` without extra confirmation — the same auto-append power the other auditor-class gates (content-reviewer, ad-account-auditor, email-quality-auditor) hold in their own disciplines.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
