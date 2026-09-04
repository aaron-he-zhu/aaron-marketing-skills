---
type: proposal-template
id: AMS-WIKI-PROPOSAL
title: Skill evolution proposal checklist
status: active
generated: false
sources:
  - references/wiki/evolution-pipeline.md
  - references/wiki/SCHEMA.md
  - CONTRIBUTING.md
  - .github/PULL_REQUEST_TEMPLATE.md
stale_after: 2027-03-04
---

# Skill evolution proposal

Copy this checklist into a PR or issue. Path-safe: the existing 120 Skill
slugs and directories cannot change.

## Identity

- Proposal title:
- Pattern id cited (required): `AMS-P-`
- Atomic concern (one sentence):
- Trace / Run evidence (in-repo paths):

## Scope gate (must all be true)

- [ ] No Skill URL / path / directory / slug / `name` change
- [ ] No 121st Skill or new installable package
- [ ] Wiki is not being wired into runtime assembly or `### Runtime Reads`
- [ ] Seven-section skill contract unchanged
- [ ] Eight auditor gates and framework IDs unchanged
- [ ] One atomic diff
- [ ] Numbers are sourced; none invented

If any box is false, stop. Record the rejection in [log.md](log.md).

## Stage

- [ ] Wiki-only patch (pattern, annotation, log row, or example)
- [ ] Follow-up Skill body clarification that cites the pattern id
- [ ] Non-Skill `references/` annotation only

## Reviewer

- [ ] Sources resolve
- [ ] `scripts/check-wiki.py` clean
- [ ] `python3 scripts/check-local-links.py` clean
- [ ] Human maintainer reviewed

## Rejection record (if rejected)

- Date:
- Rule violated:
- Ledger row added to `log.md`: yes / no
