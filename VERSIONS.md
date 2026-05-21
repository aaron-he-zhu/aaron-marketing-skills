# SEO & GEO Skills Library - Versions

Current versions for the plugin and all 20 skills. Agents can fetch this file from `https://raw.githubusercontent.com/aaron-he-zhu/seo-geo-claude-skills/main/VERSIONS.md` once per session.

**Current release**: `9.9.9` (2026-05-14). Skill `version`, `metadata.version`, plugin manifests, marketplace files, badges, and `CITATION.cff` are aligned to the same public version.

## Skills

| Skill | Category | Version | Last Updated |
|-------|----------|---------|--------------|
| keyword-research | research | 9.9.9 | 2026-05-14 |
| competitor-analysis | research | 9.9.9 | 2026-05-14 |
| serp-analysis | research | 9.9.9 | 2026-05-14 |
| content-gap-analysis | research | 9.9.9 | 2026-05-14 |
| seo-content-writer | build | 9.9.9 | 2026-05-14 |
| geo-content-optimizer | build | 9.9.9 | 2026-05-14 |
| meta-tags-optimizer | build | 9.9.9 | 2026-05-14 |
| schema-markup-generator | build | 9.9.9 | 2026-05-14 |
| on-page-seo-auditor | optimize | 9.9.9 | 2026-05-14 |
| technical-seo-checker | optimize | 9.9.9 | 2026-05-14 |
| internal-linking-optimizer | optimize | 9.9.9 | 2026-05-14 |
| content-refresher | optimize | 9.9.9 | 2026-05-14 |
| rank-tracker | monitor | 9.9.9 | 2026-05-14 |
| backlink-analyzer | monitor | 9.9.9 | 2026-05-14 |
| performance-reporter | monitor | 9.9.9 | 2026-05-14 |
| alert-manager | monitor | 9.9.9 | 2026-05-14 |
| content-quality-auditor | cross-cutting | 9.9.9 | 2026-05-14 |
| domain-authority-auditor | cross-cutting | 9.9.9 | 2026-05-14 |
| entity-optimizer | cross-cutting | 9.9.9 | 2026-05-14 |
| memory-management | cross-cutting | 9.9.9 | 2026-05-14 |

## Changelog

### v9.9.9 — Consolidated 9.x final (2026-05-14)

Final 9.x release consolidating the entire post-v9.0.0 development line into a single coherent shipment. Previous interim tags (v9.5.0, v9.9.0, v9.9.5) and the entire v10.x exploratory line have been retired and folded into this release. Anyone tracking the 9.x line should upgrade directly from v9.0.0 to v9.9.9.

**Added**:
- **Aaron command architecture**: public command API renamed from `/seo:*` to `/aaron:*`; 20 commands total (17 user + 3 governance). New commands: `/aaron:auto`, `/aaron:max`, `/aaron:discover`, `/aaron:compete`, `/aaron:map`, `/aaron:brief`, `/aaron:series`, `/aaron:refresh`, `/aaron:publish`, `/aaron:visibility`, `/aaron:remember`. Consolidated validation under `/aaron:guard`, controlled evolution under `/aaron:evolve`, proposal review under `/aaron:skillify`. Old `/seo:*` commands are not runtime aliases — paste into `/aaron:auto` for recovery routing.
- **Wiki Knowledge Layer (Phase 1 → 3)**: full multi-session memory layer with auto-refreshed index (Phase 1), compiled pages with source SHA-256 hashes and conversational `(a)/(b)/(s)/(i)` contradiction reconciliation (Phase 2), and user-initiated WARM retirement with `originally_at` reverse link for full rollback recovery (Phase 3). New auxiliary files: `memory/wiki/log.md`, `.unresolved.md`, `.drift-log`, `.retire-day-log`. Recovery script `scripts/recover-retired-warm.sh` + Phase 3 rollback validator `scripts/validate-phase3-rollback.sh` (4 fixture variants).
- **Severity-tier routing for auditor outputs (B3)**: `content-quality-auditor` and `domain-authority-auditor` now route findings by severity tier (Critical / High / Medium / Low) instead of flat lists.
- **`/aaron:remember` slash command**: non-technical-user recovery path with trigger phrases (`recover wiki` / `恢复wiki` / `undo last retire`). memory-management runs recovery scripts on the user's behalf rather than telling them to "Run scripts/recover-retired-warm.sh".
- **Bulk + force retire flows**: `/aaron:guard --wiki --retire-preview --bulk-confirmed` retires all `safe`-marked candidates in one operation; `force-retire <path>` bypasses C5 (frontmatter-coverage) only. Day-cap (20/UTC-day) still enforced.
- **Multi-project guardrail**: pre-compile prompt when ≥2 distinct project slugs in hot-cache history.
- **PII compile guardrail**: heuristic detection of natural-person entities (title-case names / LinkedIn / `entity_type: person`); surfaces GDPR Art 5(1)(c) data-minimization warning before compile.
- **GDPR purge schema**: canonical template at `cross-cutting/memory-management/references/gdpr-purge-log-template.md` with auditor-verifiable structure (purge_id, fingerprint, scope, action, legal_basis, grep-count proof, audit_signature). Never raw subject data.
- **`/aaron:series` command**: plan / write / continue / publish-handoff modes for content series workflows.
- **Multi-agent compatibility**: Codex, Gemini, Qwen, Amp, Kimi, CodeBuddy manifest support.
- **31 eval cases** under `evals/memory-management/` (was 6 pre-9.5.0) covering retirement, recovery, contradiction reconciliation, GDPR, multi-project, PII, force-retire.

**Fixed (security)**:
- (R1) Symlink-pivot path-injection bypass in `scripts/recover-retired-warm.sh` — `verify_destination_under_memory()` helper uses `pwd -P` resolution + symlink-ancestor walk to stop planted symlinks chasing outside the repo.
- (R2) SessionStart hook prompt-injection — `.unresolved.md` and archive `originally_at:` text now treated as data, sanitized for newlines / control-bytes / backticks before display.
- (Sec #2) Predictable-PID DoS in validator — `/tmp/INJECTION_*_$$` sentinels replaced with `mktemp -d` inside per-test `$TMPDIR`.

**Fixed (code quality)**:
- `set -e` swallowed by `||` chain in `run_fixture` — switched to explicit `if !` chains.
- awk pattern drift between recovery + validator — shared-invariant comment block in both scripts.
- `set -euEo pipefail` + ERR trap with `$LINENO`/`$BASH_COMMAND` for CI debuggability.
- `sed`-based `extract_originally_at()` (was `awk '{print $2}'` — truncated paths with spaces).
- Explicit `mkdir -p` error handling.

**Fixed (CI + UX)**:
- `.github/workflows/validate-skill.yml` sets `actions/checkout@v4 with: fetch-depth: 2`. Without this, `changed_paths_match` in `validate-slimming-guardrails.sh` silently skipped on shallow checkouts.
- `changed_paths_match` emits `info:` stderr line when HEAD~1 is unavailable (skip is now observable).
- Audit-log post-condition mandated for every wiki write — `wiki-runbook §3` log table extended with `restore` + `resolve` operations.

**Changed**:
- Public command API: `/seo:*` → `/aaron:*` (breaking).
- Skill `version` and `metadata.version` fields unified across all 20 skills.
- Marketplace mirrors (`marketplace.json` ↔ `.claude-plugin/marketplace.json`) kept byte-identical via `.github/scripts/sync-skills.js`; Codex manifest uses `skills: "./"` so Codex can recursively discover nested skill directories; the same script keeps that root setting in place.

**Protected**: all 20 skills and 20 commands remain. No skill directories renamed, moved, or deleted. Existing skill GitHub URLs are stable.

- 20 skills (4 research + 4 build + 4 optimize + 4 monitor + 4 cross-cutting).
- CORE-EEAT 80-item content quality framework with three veto items (T04, C01, R10).
- CITE 40-item domain authority framework with three veto items (T03, T05, T09).

**Line budget**:
- Counted lines: ~23555 (over 20000 baseline). Active waiver: WLB-2026-05-002, expiry 2026-08-12, baseline 24000. CI exports `AARON_COMMAND_LINE_BUDGET_WAIVER=1`.

### v9.0.0 — Quality pass + multi-agent compatibility (2026-04-17)

Combined quality/compliance hardening, executable playbooks, Gemini/Qwen/Amp/Kimi/CodeBuddy support, `/seo:geo-drift-check`, compact references, handoff coverage, memory scaffolding, and markdown-command maintenance. No breaking changes to skill I/O contracts.

### Earlier releases

Earlier versions are documented in [GitHub Releases](https://github.com/aaron-he-zhu/seo-geo-claude-skills/releases).
