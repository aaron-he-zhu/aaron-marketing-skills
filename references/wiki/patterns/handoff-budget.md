---
type: pattern
id: AMS-P-005
title: Handoff budget
status: active
generated: false
sources:
  - references/skill-contract.md
  - CLAUDE.md
stale_after: 2027-03-04
---

# AMS-P-005 · Handoff budget

**Lesson (compiled, not invented):** emit status, objective, evidence-backed
findings, assumptions, open loops, and at most one next Skill. Carry a
visited set. Stop after three automatic handoffs.

## In-repo source

Skill contract “Termination rules for Next Best Skill chains” and the
handoff summary format. CLAUDE.md restates the same cap.

## When this pattern applies

- Writing `recommended_next_skill`
- Reviewing a Skill that lists a menu of peers as if they all run next
- A proposal that turns a phase into an automatic 16-Skill crawl

## Must not

- Auto-run an auditor because a handoff named it
- Replay a visited Skill in the same chain
- Replace an exhausted budget with a silent extra hop
