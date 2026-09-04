---
type: procedure
id: AMS-WIKI-OPS
title: Wiki ops cadence
status: active
generated: false
sources:
  - references/wiki/SCHEMA.md
  - CONTRIBUTING.md
  - docs/repo-family.md
stale_after: 2027-03-04
---

# Weekly / post-Accept wiki lint

Run after an Accept and at least weekly while the wiki is active.

```bash
python3 scripts/check-wiki.py
python3 scripts/check-local-links.py
```

`check-wiki.py` fails closed on:

- missing or invalid OKF-subset frontmatter
- `stale_after` in the past on `status: active` pages
- pages not listed from `index.md` (orphans)
- index links to missing pages
- wiki paths appearing in Skill `### Runtime Reads`, context modules, or
  distribution allowlists
- SCHEMA.md losing the sentence **Runtime must not inject wiki.**

## Human pass (same window)

- Contradictions between two `active` patterns (resolve or deprecate one)
- Claims that sound like campaign metrics without a source
- Entity pages that have started minting canonical facts
- Framework annotations that drifted into scoring language

## Out of scope for this cadence

Signpost / family sync (`scripts/sync-family.sh`, `docs/repo-family.md`)
and release tagging remain release-owner work. Do not fold them into the
weekly wiki lint unless a single doc cross-link is needed. This PR does
not retag `20.1.0` or refresh signpost repos.
