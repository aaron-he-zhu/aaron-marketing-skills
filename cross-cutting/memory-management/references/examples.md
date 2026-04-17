# Memory Management Examples

Detailed examples showing memory management in action.

---

## Example 1: Update Rankings for Hero Keywords

**User**: "Update rankings for our hero keywords"

**Assistant**:

```markdown
I'll update rankings for your hero keywords. Let me check the hot cache for the list.

[Reads memory/hot-cache.md, finds Hero Keywords section:]
- keyword research tools (currently #15, target #5)
- best seo software (currently #23, target #10)
- free backlink checker (currently #8, target #3)
- content optimization guide (currently #12, target #5)
- technical seo audit (currently #18, target #8)

[If ~~SEO tool connected: runs automated ranking check]
[If manual: asks user for current rankings]

---

## Ranking Update - December 15, 2024

| Keyword | Previous | Current | Change | Target | Status |
|---------|----------|---------|--------|--------|--------|
| keyword research tools | #15 | #12 | up 3 | #5 | Improving |
| best seo software | #23 | #24 | down 1 | #10 | Stable |
| free backlink checker | #8 | #6 | up 2 | #3 | Near target |
| content optimization guide | #12 | #11 | up 1 | #5 | Improving |
| technical seo audit | #18 | #16 | up 2 | #8 | Improving |

### Notable Changes
- **free backlink checker** moved to #6 (only 3 positions from target!)
- **keyword research tools** gained 3 positions (strong movement)
- All other keywords showing stable or positive movement

### Updated Files
1. memory/hot-cache.md -> Hero Keywords table updated with current ranks
2. memory/monitoring/rank-history/2024-12-15-ranks.csv -> New row added:
   `2024-12-15,keyword research tools,12,best seo software,24,free backlink checker,6,...`

### Recommendations
1. Push additional content/backlinks to "free backlink checker" pages to hit #3 target
2. Investigate why "keyword research tools" suddenly gained 3 positions (replicate success)
3. Monitor "best seo software" for any negative trends

Hot cache refreshed. Next ranking check recommended: December 22, 2024.
```

---

## Example 2: Glossary Lookup

**User**: "What does 'quick wins' mean in our project?"

**Assistant**:

```markdown
Let me look that up in the project memory.

[Step 1: Check memory/hot-cache.md -> not found]
[Step 2: Check memory/glossary.md -> found!]

From your project glossary:

**Quick Wins**
- **Definition**: Low-difficulty, high-value target keywords
- **Keyword Count**: 25 keywords
- **Context**: This segment includes keywords where you can achieve page 1 rankings within 30-60 days due to low competition, despite having decent search volume

According to your memory files, your current quick wins are stored in:
`memory/research/keywords/long-tail-keywords.md` (tagged with "quick-win" label)

Would you like me to show you the current list of quick win keywords?
```

---

## Example 3: Initialize Memory for New Project

**User**: "Set up memory for a new e-commerce site selling outdoor gear"

**Assistant**:

```markdown
I'll set up the two-layer memory system for your outdoor gear e-commerce site.

## Creating Directory Structure

[Creates: memory/glossary.md, memory/research/, memory/content/, memory/monitoring/, etc.]

## `memory/hot-cache.md` (hot cache) - Initial Setup

I'll need some information to populate the hot cache:

1. **Target Keywords**: What are your top 10 hero keywords?
   (e.g., "hiking backpacks", "camping tents", "outdoor clothing")

2. **Primary Competitors**: Who are your top 3-5 competitors?
   (e.g., rei.com, backcountry.com, moosejaw.com)

3. **Current Metrics** (if available):
   - Domain authority?
   - Current organic traffic?
   - Any existing rankings?

4. **Active Initiatives**:
   - Are you launching a new category?
   - Running a content campaign?
   - Focusing on any specific product line?

5. **Project Terminology**:
   - Any internal product names or abbreviations?
   - How do you segment your keyword strategy?

Please provide what you have, and I'll create your initial `memory/hot-cache.md` and glossary. We can start with basics and enrich as we gather more data.

---

Once you provide this information, I'll generate:
- memory/hot-cache.md with your initial hot cache
- memory/glossary.md with project terminology
- memory/research/keywords/ structure with placeholder files
- memory/research/competitors/ with initial competitor list
- memory/content/calendar/active-calendar.md for Q1 2025

After setup, you can use commands like:
- "Update rankings for hero keywords"
- "Add new competitor [domain]"
- "Promote [keyword] to hot cache"
- "Archive campaigns from Q3 2024"
```

---

## Advanced Features

- **Smart Context Loading**: `Load full context for [campaign name]` — retrieves hot cache + all cold storage files for a campaign
- **Memory Health Check**: `Run memory health check` — finds orphaned files, missing timestamps, stale items, broken references
- **Bulk Promotion/Demotion**: `Promote all keywords ranking in top 10 to hot cache` / `Demote all completed campaigns from Q3`
- **Memory Snapshot**: `Create memory snapshot for [date/milestone]` — point-in-time copy for major milestones
- **Cross-Project Memory**: `Compare memory with [other project]` — keyword overlaps, competitor intersections across projects
- **Wiki Lint**: `/seo:wiki-lint [--fix] [--project name] [--retire-preview]` — contradictions, orphans, stale claims, hash mismatches. See [commands/wiki-lint.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/commands/wiki-lint.md)

---

## Practical Limitations

- **Concurrent access**: Use timestamped filenames to avoid overwrites from parallel sessions.
- **Cold storage retrieval**: WARM/COLD files only load on demand. Hot cache is the primary cross-session mechanism.
- **Data freshness**: Stale data (>90 days) should be flagged for refresh. Wiki index `mtime` field helps detect staleness.
- **Wiki compilation**: Index is best-effort for summaries; precise fields (score, status, mtime) are deterministic. Delete `memory/wiki/` anytime to revert.

---

## Auditor Handoff Archive Block Format

Append to the end of the monthly file (`memory/audits/YYYY-MM.md`), newest entries at bottom:

```markdown
## YYYY-MM-DD · <target> · <framework>

- runbook_version: 1.1
- status: DONE | DONE_WITH_CONCERNS | BLOCKED
- framework: CORE-EEAT | CITE
- vetos_failed: [T04, R10]    # empty list [] if none
- veto_count: 2
- raw_overall: 78
- final_overall: 60            # or "n/a" if BLOCKED
- cap_applied: true
- audit_gap_types: [missing, shallow]  # derived from key_findings[].gap_type (string tag; distinct from entity-geo-handoff-schema.md's gap_type enum — see ownership note at bottom of this file); [] if none
- false_positive: false        # user annotation; default false; set true only on explicit user "this was wrong" feedback
- audit_source: content-quality-auditor | domain-authority-auditor
```

**Rules**:
- One block per audit. Do not overwrite existing blocks.
- `target` is the URL or domain audited.
- `runbook_version` is copied from the current runbook header — this is how `/seo:p2-review` identifies cross-version reruns.
- `audit_gap_types` is derived from `key_findings[].gap_type` string tags (deferred to P2; until then, leave as `[]`). **Namespace note**: this field is distinct from the `gap_type` enum defined in [references/entity-geo-handoff-schema.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/entity-geo-handoff-schema.md) which classifies entity-level recognition gaps. The auditor archive stores audit-finding gap tags (e.g., `missing`, `shallow`), whereas the entity schema enumerates entity-level gaps (e.g., `knowledge_graph`, `ai_recognition`). Keep both namespaces separate.
- `false_positive` is the ONLY field that can be added/flipped after initial write, via explicit user annotation.
- If the monthly file does not exist, create it with a single `# Audit Archive — YYYY-MM` header at top.
