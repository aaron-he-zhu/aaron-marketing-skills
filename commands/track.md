---
name: track
description: "Track and remember over time: rankings, alerts, performance reports, and project memory. Not sure? Use /aaron-seo-geo:auto."
argument-hint: "<domain-campaign-or-memory-request> [--alert|--report|--remember] [--period <range>]"
parameters:
  - name: target
    type: string
    required: true
    description: "Domain, keyword set, campaign, reporting scope, or memory request"
  - name: mode
    type: string
    required: false
    description: "alert, report, or remember (default: rank tracking)"
  - name: period
    type: string
    required: false
    description: "Reporting period (with --report)"
---

# Track Command

Track and remember over time — ranking monitoring, alerts, performance reporting, and project memory.

## Route

- rank-tracker
- alert-manager
- performance-reporter
- memory-management
- entity-optimizer

## Rules

- Default: monitor rankings and SERP-position movement via rank-tracker; persist ranking history to project memory only when the user explicitly permits memory writes.
- `--alert`: design thresholds and notifications via alert-manager; require metric source, threshold owner, and notification channel before setup; do not enable external alerts without explicit approval.
- `--report`: require exactly one scope (domain, campaign, project, or period); report traffic, rankings, AI citations/readiness, authority, technical health, content progress, and open loops; keep source/date freshness visible and separate observed data from estimates.
- `--remember`: memory-management owns the HOT/WARM/COLD lifecycle — capture, promote, demote, archive, query, restore-from-archive — plus cleanup, purge, and protocol aggregation; canonical entity profiles route to entity-optimizer. Restore looks up a matching `memory/archive/YYYY-MM-DD-*` file. Purge/GDPR/CCPA requests require scoped targets and delete or anonymize matching canonical and archived memory surfaces. Only content-quality-auditor and domain-authority-auditor may append one veto marker to `memory/hot-cache.md` without extra confirmation.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
