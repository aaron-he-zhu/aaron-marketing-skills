---
name: memory-management
description: 'Use when the user asks to "remember project context"; manages the cross-discipline marketing memory lifecycle (SEO/GEO + influencer + paid ads + email) — hot-cache, active work, archive tiers, and privacy cleanup. Not for content or domain scoring — use the auditors. 项目记忆/跨会话'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when reviewing, archiving, or cleaning up campaign memory. Also when the user asks to check saved findings, manage hot cache, or archive old data."
argument-hint: "[review|archive|cleanup]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: protocol
  phase: protocol
  geo-relevance: "low"
---

# Memory Management
This skill implements a three-tier memory system (HOT/WARM/COLD) for all marketing disciplines (SEO/GEO, influencer, paid ads, and email). HOT memory (80 lines max) loads automatically every session via the SessionStart hook. WARM memory loads on demand per skill. COLD memory is archived data queried only when explicitly requested. The skill manages the full lifecycle: capture, promote, demote, and archive.

## What This Skill Does

Manages a three-tier memory lifecycle (HOT/WARM/COLD) with automatic promotion, demotion, and archival. Also maintains open-loop tracking and cross-skill aggregation.

## Quick Start

Start with one of these prompts. Finish with a hot-cache update plan and a handoff summary using the repository format in [Skill Contract](../../references/skill-contract.md).

### Initialize Memory Structure

```
Set up marketing memory for [project name]
```

```
Initialize memory structure for a new [industry] website optimization project
```

### Update After Analysis

```
Update memory after ranking check for [keyword group]
```

```
Refresh hot cache with latest competitor analysis findings
```

### Query Stored Context

```
What are our hero keywords?
```

```
Show me the last ranking update date for [keyword category]
```

```
Look up our primary competitors and their domain authority
```

### Promotion and Demotion

```
Promote [keyword] to hot cache
```

```
Archive stale data that hasn't been referenced in 30+ days
```

### Glossary Management

```
Add [term] to project glossary: [definition]
```

```
What does [internal jargon] mean in this project?
```

## Skill Contract

**Expected output**: a memory update plan, hot-cache changes, and a short handoff summary.

- **Reads**: current campaign facts, new findings from other skills, approved decisions, and the shared [State Model](../../references/state-model.md).
- **Writes**: updates to `memory/hot-cache.md`, `memory/open-loops.md`, `memory/decisions.md`, and related `memory/` folders. Manages WARM-to-COLD archival in `memory/archive/`. **Auditor handoff archiving** (v7.1.0+): when triggered by a direct user request or an auditor's explicit "Save these results?" yes-response, append a structured block to `memory/audits/YYYY-MM.md`. The Stop hook never initiates memory writes. See [Examples](references/examples.md) for the exact archive block format and rules.
- **Promotes**: durable strategy, blockers, terminology, entity candidates, and major deltas. Applies the temperature lifecycle by **observable** rules only: promote to HOT on an explicit user/skill request ("promote X" / pin); demote and archive by the file's `last_updated` date. Reference-frequency counters are NOT tracked by any hook, so the lifecycle never depends on them — see [State Model](../../references/state-model.md).
- **Done when**: the requested lifecycle action (capture/promote/demote/archive/query/purge) is applied, `memory/hot-cache.md` is within the 80-line / 25KB limit, and the affected memory paths are reported back to the user.
- **Primary next skill**: use the `Next Best Skill` below when the project memory baseline is ready for active work.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

### Temperature Lifecycle Rules

> See [Promotion & Demotion Rules](references/promotion-demotion-rules.md) for the full promotion/demotion table and action procedures.

### Hook Integration

This skill's behavior is reinforced by the library's `claude-hook.sh` hooks. What the hook **actually does** (do not document behavior it lacks):
- **SessionStart** (fires on startup, resume, clear, compact): injects a sanitized excerpt of `memory/hot-cache.md`, and when `memory/open-loops.md` has tracked items, appends a one-line pointer to review them for staleness. It does not compute dates or a "Quick Status" — surfacing which open loops are stale is the agent's job once pointed at the file.
- **PostToolUse**: warns when `memory/hot-cache.md` exceeds 80 lines / 25KB; enforces the auditor artifact-gate on `memory/audits/*.md` writes; offers an optional quality check after user-facing content edits.
- **Stop**: a no-op (exits without output). CLAUDE.md's "allow-only Stop check" is just this no-op; the hook never initiates memory writes.

## Data Sources

With tools: auto-populate from ~~SEO tool, ~~analytics, ~~search console. Without tools: ask user for keywords, competitors, metrics, campaigns, and terminology. See [CONNECTORS.md](../../CONNECTORS.md).

## Decision Gates

**Stop and ask the user when:**
- A purge (Art 17 / CCPA) is requested — present the matched files and the redaction-vs-delete choice, and only act on confirmed matches. Never auto-delete memory.
- A `memory/decisions.md` entry needed to answer a query has `approved_by: skill_inferred` or a missing field — surface it as ADVISORY and confirm before treating it as authoritative.
- A referenced term is not found in any memory layer — ask for clarification rather than guessing.

**Continue silently (never stop for):**
- Routine promotion/demotion that follows the temperature lifecycle rules.
- Hot-cache trimming suggestions when over the 80-line / 25KB limit (recommend, don't block).
- Missing optional tool data when auto-populating — record what is available and proceed.

## Instructions

When a user requests memory management (any discipline — SEO/GEO, influencer, paid ads, or email):

### 1. Initialize Memory Structure

For new projects, create the directory structure defined in the [State Model](../../references/state-model.md). Key directories: `memory/` (decisions, open-loops, glossary, entities, creators, claims, consent, research, content, audits, monitoring, influencer, paid-ads, email).

> **Templates**: [Hot Cache Template](references/hot-cache-template.md) · [Glossary Template](references/glossary-template.md)

### 2. Context Lookup Flow

When a user references something unclear, follow this lookup sequence:

**Step 1: Check `memory/hot-cache.md` (hot cache)**
- Is it in active keywords (SEO/GEO), tracked creators/niches (influencer), or live offers/ad accounts (paid)?
- Is it in primary competitors or tracked influencers?
- Is it in current priorities or campaigns?

**Step 2: Check memory/glossary.md**
- Is it defined as project terminology?
- Is it a custom segment or shorthand?

**Step 3: Check Cold Storage**
- Search `memory/archive/` first for dated `YYYY-MM-DD-` archived files.
- If the archive points to a source category, follow that trail back to `memory/research/`, `memory/audits/`, `memory/monitoring/`, `memory/influencer/`, `memory/paid-ads/`, or `memory/email/`.
- Treat COLD findings as historical unless refreshed by the current session.

**Step 4: Ask User**
- If not found in any layer, ask for clarification
- Log the new term in glossary if it's project-specific

- **Decision provenance (v8.0.1+)**: when loading `memory/decisions.md`, verify each entry has `approved_by: user`. Entries with `approved_by: skill_inferred` or missing field are treated as **ADVISORY** — surface to user before using as authoritative. Auditor-class gate skills (content-quality-auditor, domain-authority-auditor, content-reviewer, ad-account-auditor, email-quality-auditor) MUST ignore non-user-approved decisions when determining verdict. See [skill-contract.md §Promotion Rules](../../references/skill-contract.md).

Example lookup: User asks "Update rankings for our hero KWs" → Step 1 finds "Hero Keywords (Priority 1)" in hot-cache → extract the keyword list → run the ranking check → update `memory/hot-cache.md` and `memory/monitoring/rank-history/YYYY-MM-DD-ranks.csv`.

### 3. Promotion & Demotion Logic

> **Reference**: See [Promotion & Demotion Rules](references/promotion-demotion-rules.md) for detailed promotion/demotion triggers (keywords, competitors, metrics, campaigns) and the action procedures for each.

### 4. Update Triggers, Archive Management & Cross-Skill Integration

> **Reference**: See [Update Triggers & Integration](references/update-triggers-integration.md) for the complete update procedures after ranking checks, competitor analyses, audits, and reports; monthly/quarterly archive routines; and integration points with connected skills across all four disciplines — SEO/GEO (keyword-research, rank-tracker, competitor-analysis, content-gap-analysis, content-writer, content-quality-auditor, domain-authority-auditor), influencer (skills writing under `memory/influencer/<skill>/`, plus content-reviewer's gated artifacts and creator-registry candidate flow), paid ads (skills writing under `memory/paid-ads/<skill>/`, plus the ad-account-auditor and attribution-reconciler artifacts rolled into the monthly aggregate and the offer-claims-registry candidate flow), and email (skills writing under `memory/email/<skill>/`, plus email-quality-auditor's gated EQS artifacts rolled into the monthly aggregate and the consent-registry candidate flow).

### 5. Memory Hygiene Checks

When invoked for review or cleanup:

1. **Line count check**: Count lines in `memory/hot-cache.md`. If >80, list oldest entries for archival.
2. **Byte check**: If hot-cache exceeds 25KB, warn and recommend trimming long entries.
3. **Staleness scan**: List memory files whose frontmatter `last_updated` date (or file mtime) is older than 30 days; recommend archival for files older than 90 days. Age is computable from disk — reference-frequency is not tracked, so never gate on "unreferenced".
4. **Frontmatter audit**: Check that all memory files (except hot-cache.md) have `name`, `description`, and `type` in their frontmatter. Report any missing fields.

### 6. Save Results

Ask "Save these results for future sessions?" — if yes, write `YYYY-MM-DD-<topic>.md` to `memory/`. Add veto issues to `memory/hot-cache.md` only from auditor handoff or explicit user approval.

## GDPR / Privacy Compliance

`memory/` may store third-party personal data — entity names, founder bios, LinkedIn profiles, author/journalist names surfaced by `entity-optimizer` or research skills. Under GDPR Art 4(1) (applies to **processing of personal data of EU/EEA/UK residents** regardless of where the controller is located), these qualify as "personal data". The user is the data controller. Non-EU users without EU/EEA/UK data subjects may still face analogous obligations under CCPA/CPRA (California), PIPEDA (Canada), LGPD (Brazil), or other national regimes. **Not legal advice.**

### Retention policy
- WARM files: archive to `memory/archive/` after 90 days unreferenced (default lifecycle)
- COLD archive: never auto-deleted, but eligible for Art 17 erasure requests
- All files: user MUST honor Art 17 requests from data subjects (individuals named in memory)

### Deletion flow (Art 17 / CCPA §1798.105)
Invoke: `memory-management purge <entity-name-or-slug>`

This skill then:
1. Greps all files under `memory/` (including `memory/archive/`) for the entity name, slug, or domain — `grep -rF "<entity-name>" memory/` — and presents matches for confirmation.
2. On confirmation, deletes or anonymizes the matched lines/files across the working tree: `memory/hot-cache.md`, WARM notes, COLD/archive files, `memory/entities/<slug>.md`, `memory/entities/candidates.md`, audit aggregates, and open loops.
3. Appends a dated, subject-free entry to `memory/audits/gdpr-purges.md` per the [GDPR Purge Log Template](references/gdpr-purge-log-template.md) — required fields `date`, `redacted_label`, `legal_basis`, `action`, `scope`, `working_tree_only: true` — so there is a human-readable record of the request.

> **Honest limitation — this edits the working tree only.** If `memory/` is under version control (it usually is, in the user's project repo), the subject **still exists in git history**. Verify with `git log -S"<entity-name>" -- memory/`; true erasure from history requires `git filter-repo` / `git filter-branch` and is the user's responsibility — it is out of this skill's scope. Do not represent a working-tree redaction as a complete, audit-grade erasure. There is no salted-fingerprint or reingest-blocking mechanism: nothing in the hooks consults a tombstone before writing, so any such claim would be false.

### Lawful basis reminder
Before writing a third-party person to `memory/entities/`, the user must have one lawful basis per GDPR Art 6 (where GDPR applies — see scope note above): `consent`, `legitimate_interest`, `contract`, or equivalent. Advisory — this skill does not enforce, and does not substitute for legal review.

## Reference Materials

- [Examples](references/examples.md) — Worked examples, advanced features, practical limitations, and the auditor handoff archive block format & rules
- [Promotion & Demotion Rules](references/promotion-demotion-rules.md) — Full promotion/demotion table and action procedures
- [Update Triggers & Integration](references/update-triggers-integration.md) — Update procedures, archive routines, and cross-skill integration points
- [CORE-EEAT Content Benchmark](../../references/core-eeat-benchmark.md) — Content quality scoring stored in memory
- [CITE Domain Rating](../../references/cite-domain-rating.md) — Domain authority scoring stored in memory

## Next Best Skill

Primary: [keyword-research](../../research/keyword-research/SKILL.md) — seed or refresh campaign strategy with current demand signals.
