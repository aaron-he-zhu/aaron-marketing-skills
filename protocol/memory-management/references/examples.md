# Memory Management Examples

---

## Example 1: Update Rankings for Hero Keywords

**User**: "Update rankings for our hero keywords"

```markdown
I'll update rankings for your hero keywords.
[Reads memory/hot-cache.md -> Hero Keywords section]
[If ~~SEO tool connected: runs automated ranking check]
[If manual: asks user for current rankings]

## Ranking Update - December 15, 2024

| Keyword | Previous | Current | Change | Target | Status |
|---------|----------|---------|--------|--------|--------|
| keyword research tools | #15 | #12 | up 3 | #5 | Improving |
| best seo software | #23 | #24 | down 1 | #10 | Stable |
| free backlink checker | #8 | #6 | up 2 | #3 | Near target |

### Updated Files
1. memory/hot-cache.md -> Hero Keywords table updated
2. memory/monitoring/rank-history/2024-12-15-ranks.csv -> New row added

### Recommendations
1. Push additional content/backlinks to "free backlink checker" to hit #3
2. Investigate "keyword research tools" +3 gain (replicate success)
3. Monitor "best seo software" for negative trends

Hot cache refreshed. Next ranking check: December 22, 2024.
```

---

## Example 2: Glossary Lookup

**User**: "What does 'quick wins' mean in our project?"

```markdown
[Check memory/hot-cache.md -> not found]
[Check memory/glossary.md -> found!]

**Quick Wins**
- **Definition**: Low-difficulty, high-value target keywords
- **Keyword Count**: 25
- **Context**: Keywords achievable for page 1 within 30-60 days due to low competition

Current list stored in: `memory/research/keywords/long-tail-keywords.md` (tagged "quick-win")
```

---

## Example 3: Initialize Memory for New Project

**User**: "Set up memory for a new e-commerce site selling outdoor gear"

```markdown
I'll set up the two-layer memory system.
[Creates: memory/glossary.md, memory/research/, memory/content/, memory/monitoring/, etc.]

To populate hot cache, I need:
1. **Target Keywords**: Top 10 hero keywords
2. **Primary Competitors**: Top 3-5 competitors
3. **Current Metrics**: DA, organic traffic, existing rankings
4. **Active Initiatives**: New categories, content campaigns, product focus
5. **Project Terminology**: Internal names, abbreviations, keyword segmentation

Once provided, I'll generate:
- memory/hot-cache.md, memory/glossary.md
- memory/research/keywords/ and memory/research/competitors/ structures
- memory/content/calendar/active-calendar.md
```

---

## Advanced Features

- **Smart Context Loading**: `Load full context for [campaign name]`
- **Memory Health Check**: `Run memory health check` — orphaned files, missing timestamps, stale items
- **Bulk Promotion/Demotion**: `Promote all keywords ranking in top 10 to hot cache`
- **Memory Snapshot**: `Create memory snapshot for [date/milestone]`
- **Cross-Project Memory**: `Compare memory with [other project]`

---

## Practical Limitations

- **Concurrent access**: Use timestamped filenames to avoid overwrites from parallel sessions.
- **Cold storage retrieval**: WARM/COLD files only load on demand. Hot cache is primary cross-session mechanism.
- **Data freshness**: Stale data (>90 days) should be flagged for refresh.

---

## Auditor Handoff Archive Block Format

Append to monthly file (`memory/audits/YYYY-MM.md`), newest at bottom:

```markdown
## YYYY-MM-DD · <target> · <framework>
- runbook_version: 1.1
- status: DONE | DONE_WITH_CONCERNS | BLOCKED
- framework: CORE-EEAT | CITE | ROAS
- vetos_failed: [T04, R10]    # empty list [] if none
- veto_count: 2
- raw_overall: 78
- final_overall: 60            # or "n/a" if BLOCKED
- cap_applied: true
- audit_gap_types: [missing, shallow]  # distinct from entity-geo-handoff-schema.md's gap_type enum
- false_positive: false        # set true only on explicit user feedback
- audit_source: content-quality-auditor | domain-authority-auditor | ad-account-auditor
```

**Rules**:
- One block per audit. Do not overwrite existing blocks.
- `target` is the URL or domain audited (for ROAS blocks, the ad account or campaign).
- `runbook_version` copied from current runbook header.
- Paid artifacts roll in too: ROAS blocks come from ad-account-auditor's gated artifacts under `memory/audits/ad/`; attribution-reconciler's standing workbooks under `memory/ad/attribution-reconciler/` are folded into the same monthly pass (a one-line pointer per workbook is enough — do not copy tables).
- `false_positive` is the ONLY field that can be flipped after initial write.
- GDPR/CCPA erasure is the exception: replace subject identifiers with a stable redacted label while preserving scores, status, and timestamps. (Working-tree redaction only — no salted fingerprint or reingest tombstone; see [memory-management SKILL.md §GDPR](../SKILL.md) and [GDPR Purge Log Template](gdpr-purge-log-template.md).)
- If monthly file doesn't exist, create with `# Audit Archive — YYYY-MM` header.
