---
name: p2-review
description: Evaluate v7.1.0 P2 observation items against trigger conditions. Auto-closes unmet items on 2026-07-10; proposes met items for v7.3.
argument-hint: "[--verbose] [--since <date>]"
parameters:
  - name: verbose
    type: boolean
    required: false
    description: Show per-item reasoning and counts, not just the summary.
  - name: since
    type: string
    required: false
    description: Scan memory/audits/ from this date forward (YYYY-MM-DD). Default is v7.1.0 release date (2026-04-11).
---

# P2 Review

> Evaluates v7.1.0 **P2 observation items** against their binary trigger conditions, reports status, and makes a recommendation for v7.3.0. Part of the [SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills).

**Ownership**: this command is the designated runner for the 2026-07-10 tombstone review tied to [ADR-001](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/decisions/2026-04-adr-001-inline-auditor-runbook.md). Without it, "auto-close" is aspirational.

**Scheduled trigger**: the SessionStart hook in `hooks/hooks.json` reminds the user to run this command if the current date is ≥ 2026-07-10 AND `memory/p2-review-2026-07.md` does not yet exist.

---

## What It Checks

Scans `memory/audits/YYYY-MM*.md` files for evidence that each P2 observation item's trigger has been met. Produces a recommendation per item.

### P2 observation items (v7.1.0)

| Item | Binary trigger | Data source |
|---|---|---|
| **Gap Typology field** | 3+ handoffs in `memory/audits/` with explicit `audit_gap_types: [missing, ...]` annotation from a downstream writer/refresher skill (per [examples.md §Auditor Handoff Archive Block Format](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/references/examples.md)) | `memory/audits/*.md` |
| **40-tier cap number** | 30+ audits in `memory/audits/` with 2+ veto fails (BLOCKED status) | `memory/audits/*.md` |
| **Failure Modes Catalog** (single shared file) | 5+ audits in `memory/audits/` with `false_positive: true` user annotation | `memory/audits/*.md` |
| **Adversarial Pass** (alternative to removed Blind Pass) | Named user feedback: "audits feel mechanical" or equivalent | feedback channel, manual |
| **wiki-lint aggregation extension** | Any of the above 2+ items pass (derived trigger) | derived from above |

---

## Evaluation Procedure

For each P2 item:

1. Read `memory/audits/` files matching the item's data source
2. Count records matching the trigger pattern
3. Compare count to threshold
4. Determine status:
   - `MET` — threshold reached; propose for v7.3.0
   - `PARTIAL` — count > 0 but below threshold; keep observing
   - `UNMET` — count == 0 after 90+ days since v7.1.0 ship; propose tombstone
5. Emit per-item recommendation

### Tombstone rule

An item with UNMET status at ≥ 2026-07-10 is proposed for **deletion** from the project, not silent persistence. This is enforced by writing the recommendation to `references/decisions/2026-07-adr-002-p2-tombstone.md` (or next ADR number) so the closure is visible and reviewable.

---

## Usage

```
/seo:p2-review                         # evaluate current state
/seo:p2-review --verbose               # show per-item counts and reasoning
/seo:p2-review --since 2026-05-01      # only count audits after May 2026
```

---

## Output

Report written to `memory/p2-review-YYYY-MM.md` (runtime location, survives across sessions). Summary also presented to the user in a table.

### Report format

```markdown
# P2 Review — 2026-07-10

**Scanned**: memory/audits/*.md (since 2026-04-11, v7.1.0 release)
**Audits counted**: N total

## Per-item status

| Item | Threshold | Actual | Status | Recommendation |
|---|---|---|---|---|
| Gap Typology field | 3 handoffs | 0 | UNMET | Propose tombstone in ADR-002 |
| 40-tier cap | 30 multi-veto | 2 | PARTIAL | Continue observing |
| Failure Modes Catalog | 5 false positives | 0 | UNMET | Propose tombstone in ADR-002 |
| Adversarial Pass | user feedback | none | UNMET | Propose tombstone in ADR-002 |
| wiki-lint aggregation | derived | derived | UNMET | Closes automatically with parents |

## Recommendations

- **Propose tombstone**: 4 items (see above)
- **Continue observing**: 1 item (40-tier cap, 2/30 evidence)

## Next steps

1. If recommendation is "Propose tombstone": create ADR-002 in `references/decisions/` and open a PR to remove the deferred references from `references/auditor-runbook.md` §2, `references/contract-fail-caps.md`, and `references/decisions/2026-04-adr-001-inline-auditor-runbook.md`.
2. If recommendation is "Continue observing": re-run this command in 90 days.
3. If recommendation is "Propose for v7.3.0": create a new ADR + implementation ticket for the v7.3.0 work.
```

---

## Not included

- No automatic tombstone execution. The command surfaces recommendations; actual removal requires a human-authored ADR and PR.
- No external data sources. Only reads `memory/audits/` (runtime data written by auditors per the v7.2.0 memory-management archiving rule) and the project's own reference files.
- No forecast of when UNMET items might become MET. Observation continues at whatever cadence the user runs this command.

---

## Related

- [ADR-001: Inline Auditor Runbook](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/decisions/2026-04-adr-001-inline-auditor-runbook.md) — defines the P2 items and tombstone rule
- [references/auditor-runbook.md §2](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/auditor-runbook.md) — 2+ veto BLOCKED behavior pending 40-tier calibration
- [references/contract-fail-caps.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/contract-fail-caps.md) — sunset clause for the 40-tier number
- [cross-cutting/memory-management/SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md) — archives handoffs to `memory/audits/` enabling this review's data source
