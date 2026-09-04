---
type: pattern
id: AMS-P-001
title: Status is not verdict
status: active
generated: false
sources:
  - references/auditor-runbook.md
  - references/skill-contract.md
stale_after: 2027-03-04
---

# AMS-P-001 · Status is not verdict

**Lesson (compiled, not invented):** execution status and business gate
verdict are orthogonal. `DONE` does not mean `SHIP`. `BLOCKED` does not mean
the gate said no.

## In-repo source

`references/auditor-runbook.md` §4 “Status Is Not Verdict” already states the
pairing:

| Situation | `status` | `verdict` |
|---|---|---|
| Clean enough to ship | `DONE` | `SHIP` |
| Remediation needed | `DONE_WITH_CONCERNS` | `FIX` |
| Two or more verified vetoes | `DONE` | `BLOCK` |
| Missing applicable evidence | `NEEDS_INPUT` | `UNDECIDED` |
| Technical/security stop | `BLOCKED` | `UNDECIDED` |

The shared contract repeats the same split: `status` reports execution, not
business quality.

## When this pattern applies

- Writing or reviewing an auditor handoff
- Explaining why an audit completed but must not publish
- Rejecting a Skill-body change that collapses status into verdict

## Must not

- Re-score or change veto IDs
- Treat this page as a ninth gate
- Inject this page through `### Runtime Reads`
