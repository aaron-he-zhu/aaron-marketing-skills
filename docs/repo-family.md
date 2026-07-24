# Repo Family — Registry & Sync Policy

This repository (`aaron-marketing-skills`) is the **single source of truth (SSOT)** for all marketing skills, frameworks, commands, and docs. Every sibling repo under the same account that carries related content is a **downstream family repo** with an explicit tier, policy, and sync mode recorded here.

**The rule: no family repo is created, revived, or synced outside this table.** Every live mirror is a permanent sync liability — adding one means adding a row here first, with a sync mode the tooling can enforce.

## Registry

| Repo | Tier | Policy | Sync mode | Source of truth |
|------|------|--------|-----------|-----------------|
| [aaron-marketing-skills](https://github.com/aaron-he-zhu/aaron-marketing-skills) | **SSOT** | active development | — | — |
| [core-eeat-content-benchmark](https://github.com/aaron-he-zhu/core-eeat-content-benchmark) | published standard | live mirror | `ids` | `references/core-eeat-benchmark.md` |
| [cite-domain-rating](https://github.com/aaron-he-zhu/cite-domain-rating) | published standard | live mirror | `ids` | `references/cite-domain-rating.md` |
| [influencer-marketing-star-benchmark](https://github.com/aaron-he-zhu/influencer-marketing-star-benchmark) | published standard | live mirror | `ids` | `references/star-benchmark.md` (v18 STAR reframe replaced the C3 split; **owner must rename the GitHub mirror from `influencer-marketing-c3-benchmark` before the next sync**) |
| [paid-ads-roas-benchmark](https://github.com/aaron-he-zhu/paid-ads-roas-benchmark) | published standard | live mirror | `body` | `references/roas-benchmark.md` |
| [email-marketing-send-benchmark](https://github.com/aaron-he-zhu/email-marketing-send-benchmark) | published standard | live mirror | `body` | `references/send-benchmark.md` |
| [launch-marketing-ramp-benchmark](https://github.com/aaron-he-zhu/launch-marketing-ramp-benchmark) | published standard | live mirror | `body` | `references/ramp-benchmark.md` |
| [social-marketing-echo-benchmark](https://github.com/aaron-he-zhu/social-marketing-echo-benchmark) | published standard | live mirror | `body` | `references/echo-benchmark.md` |
| [narrative-marketing-tale-benchmark](https://github.com/aaron-he-zhu/narrative-marketing-tale-benchmark) | published standard | live mirror | `body` | `references/tale-benchmark.md` |
| [paid-ads-agent-skills](https://github.com/aaron-he-zhu/paid-ads-agent-skills) | signpost | live mirror | `list` | `.claude-plugin/plugin.json` (`ad/` skills) |
| [email-marketing-agent-skills](https://github.com/aaron-he-zhu/email-marketing-agent-skills) | signpost | live mirror | `list` | `.claude-plugin/plugin.json` (`email/` skills) |
| [product-launch-agent-skills](https://github.com/aaron-he-zhu/product-launch-agent-skills) | signpost | live mirror | `list` | `.claude-plugin/plugin.json` (`launch/` skills) |
| [social-media-agent-skills](https://github.com/aaron-he-zhu/social-media-agent-skills) | signpost | live mirror | `list` | `.claude-plugin/plugin.json` (`social/` skills) |
| [brand-narrative-agent-skills](https://github.com/aaron-he-zhu/brand-narrative-agent-skills) | signpost | live mirror | `list` | `.claude-plugin/plugin.json` (`narrative/` skills) |
| [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) | signpost | live mirror | `list` | `.claude-plugin/plugin.json` (`seo-geo/` skills) · final standalone line at tag `v9.9.12` |
| [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills) | signpost | live mirror | `list` | `.claude-plugin/plugin.json` (`influencer/` skills) · final standalone line at tag `standalone-final` |

Freshness is self-documenting: every `body`/`list` mirror carries its synced umbrella version in its `SYNC:BEGIN` marker line, and the drift sentinel (below) is the authoritative staleness signal — this table records *policy*, not *state*.

## Tiers

- **SSOT** — the only place development happens. Downstream repos never receive content that doesn't exist here first.
- **Published standard** — the eight benchmark frameworks' citable public homes (CORE-EEAT, CITE, STAR, ROAS, SEND, RAMP, ECHO, TALE). Content is the product; each carries a provenance note pointing at its working copy in `references/`.
- **Signpost** — README-only discovery surfaces, one per discipline. Banner + current skill list + install pointer to the umbrella; **no skill content, no `plugin.json`** — deliberately non-installable so nobody installs a stale snapshot. The two pre-merge standalones (seo-geo, influencer) keep their final full lines under git tags (`v9.9.12` / `standalone-final`), linked from their banners, with old→new mapping tables for returning users; already-installed copies of those lines keep working offline.

## Sync modes

- **`body`** — the mirror README's framework body between `<!-- SYNC:BEGIN -->` / `<!-- SYNC:END -->` markers is regenerated verbatim from the source file, with relative `references/` links rewritten to absolute umbrella URLs. Full-fidelity mirror.
- **`ids`** — every framework item ID the source file references (bold or table-row, e.g. `T04`, `A2`) must exist in the published standard's ID set; the repo keeps its own standalone packaging and prose (these three predate this policy, and the umbrella file may be a compact summary of the full standard). ID drift is *reported* for manual reconciliation, never auto-pushed.
- **`list`** — the skill list between SYNC markers is regenerated from `plugin.json`.

## How sync runs

1. **At release time** (CONTRIBUTING §6): run `bash scripts/sync-family.sh` — dry-run by default, reports per-repo drift with diffs and exits non-zero on any. Then `bash scripts/sync-family.sh --live` to clone, apply, and push the `body`/`list` targets. The live run validates the canonical GitHub origin and clean, pushed HEAD once, exports that commit privately, and generates every body/list/ID comparison from the export; it never reopens worktree `plugin.json` or `references/` inputs after the gate. Owner-run, never CI-automated — same convention as `publish-clawhub.sh` (pushes to public repos get a human glance).
2. **Between releases**: [`.github/workflows/family-drift.yml`](../.github/workflows/family-drift.yml) runs the same script weekly (read-only, keyless — raw.githubusercontent fetches only) and fails red on drift. It deliberately does **not** run on PRs: drift while `references/` evolves on main ahead of a release is expected, not an error.

## Banner templates

Every family repo README opens with the same recognizable block. Three variants — parameterize, don't improvise:

### A. Signpost (paid / email / launch / social / narrative agent-skills)

```markdown
> [!IMPORTANT]
> **This is a signpost repo — the skills live in [aaron-marketing-skills](https://github.com/aaron-he-zhu/aaron-marketing-skills).**
> The 16 <discipline> skills listed below are actively developed there, as one of 7 disciplines in a 120-skill bundle
> sharing one contract, eight benchmark-driven gates, and keyless data connectors. This repo carries no skill content —
> it exists so you can find the discipline; the bundle is where you install it.
```

### B. Signpost with history (former standalones: seo-geo-claude-skills, influencer-marketing-agent-skills)

Variant A plus a preserved-line pointer in the banner, and an old→new `<details>` mapping table after the skill list:

```markdown
> … This repo's former standalone <N>-skill line is preserved, unchanged, at tag [`<tag>`](…/tree/<tag>) and receives
> no updates — already-installed copies keep working; new installs come from the bundle.
```

### C. Provenance note (the eight benchmark repos)

```markdown
> **Working copy:** this standard is maintained in [aaron-marketing-skills — `references/<file>.md`](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/<file>.md)
> and published here as its citable home. Framework changes land there first, then sync here (`scripts/sync-family.sh`).
```
