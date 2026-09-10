# Skill Dashboard

This is a local optional tool that projects **your own** skill-run artifacts
into HTML, Markdown, and JSON. The generator and view schema ship in the
Claude plugin / governed **install surface**. It is **not** a 121st Skill,
**not** a hosted Web product, and **not** a Gateway. Generated
`skill-dashboard.html` is a user-local output, never a committed install
artifact.

Use it when you want an intuitive local view of what ran, what changed, what
is still open, and whether business outcomes are actually bound to a
measurement contract.

## Boundaries

- Product name: **Skill Dashboard** only. Do not call it a usage board.
- Reads existing files. It does not invent metrics, mutate registries, or
  authorize sends/publishes/spend.
- Outcomes numeric before/after appear **only** when a `measurement-contract`
  exists, with supporting `evidence-observation`, `action-receipt`, or
  `cycle-retro` as available. Otherwise the Outcomes module uses a fixed
  empty state: business results are unvalidated/unbound.
- No billing, hosted multi-tenant UI, or social-signal monitoring.
- `scripts/skill-dashboard.py` and `references/skill-dashboard.schema.json`
  ship in the plugin / governed allowlist. This guide, `check-skill-dashboard.py`,
  fixtures, and issue templates stay out. Portable Lite still ships no
  executable repository runtime. Generated HTML/MD/JSON stay on the machine
  that ran the command.

## Conventional discovery paths

Point `--root` at the **project** that holds working memory, not at a plugin
install. When nothing is found, the view stays honest and empty.

```
<project>/
  memory/runs/<run-id>/envelopes/*.json
  memory/runs/<run-id>/save-points/*.json
  memory/runs/<run-id>/events.ndjson          # optional Timeline
  memory/runs/<run-id>/artifacts/*.json       # control artifacts if stored per run
  memory/audits/<discipline>/*.md
  memory/control/*.json                       # measurement-contract and friends
  memory/control/values/*.json                # optional numeric value files
  memory/open-loops.md
  memory/decisions.md
  memory/session-checkpoint.md
  memory/staff/bot-roster.json                # optional 8-bot roster
  memory/staff/handoffs/*.json                # optional Staff chain
  references/system-catalog.json              # else the skills-repo catalog
```

Numeric outcome values are resolved only from project-path `value_ref`
bindings on evidence fields (a local JSON object with a numeric `value`).
Opaque refs stay referenced, not invented. Run-envelope `metrics` are
operational counters and never become Outcomes numbers.

## Run

After a Claude plugin / governed install, or from a clone of this repository:

```bash
python3 scripts/skill-dashboard.py --root .
python3 scripts/skill-dashboard.py --root /path/to/project --out skill-dashboard.html --json --md
```

- `--root` — project directory to scan (default: `.`)
- `--out` — HTML path; default `skill-dashboard.html`. A directory writes
  `skill-dashboard.html` inside it.
- `--json` — also write `skill-dashboard.json`
- `--md` — also write `skill-dashboard.md`

Open the HTML locally. Do not publish it as a hosted product.

## Information architecture

1. **Next** — `next_action`, open loops, blockers
2. **Usage** — run header, `visited_skills` chain, status
3. **Delta** — work artifacts before/after; quality before/after
   (`SHIP` / `FIX` / `BLOCK` / `UNDECIDED` / `NOT_SCORED`)
4. **Outcomes** — measurement-contract gated before/after; unbound empty
   state otherwise
5. **Decisions** — propose / Accept queues and decision gates
6. **Trust** — evidence gaps, conflicts, confidence
7. **Coverage** — visited skills vs `references/system-catalog.json`
8. **Staff** — 8-bot handoff/chain when present; graceful empty state
   otherwise
9. **Timeline** — optional; hidden unless `events.ndjson` exists

The view schema is [`references/skill-dashboard.schema.json`](../references/skill-dashboard.schema.json).
It is a projection, not a second system of record.

## Empty states

| Module | Empty state |
|--------|-------------|
| Next | No next action, open loop, or blocker is recorded. |
| Usage | No run envelopes were found under `memory/runs/`. |
| Delta | No artifact or audit before/after pair is available. |
| Outcomes | Business results are unvalidated/unbound. No invented numbers. |
| Decisions | No propose or Accept decision items were found. |
| Trust | No evidence gaps, conflicts, or confidence notes were found. |
| Coverage | No visited skills and no catalog coverage to project. |
| Staff | No AI Staff handoff chain was found. |
| Timeline | Omitted when run events are absent. |

## Optional Claude Code hooks

A local `Stop` or `SessionStart` hook **may** regenerate Skill Dashboard after
a run. Hooks are **not** required for CI, are **not** shipped as part of this
tool, and must never create write authority on their own. Keep any hook
outside the governed plugin payload.

## Feedback

Use the Skill Dashboard issue template if a projection is wrong, an empty
state is dishonest, or a file leaked into an install package.
