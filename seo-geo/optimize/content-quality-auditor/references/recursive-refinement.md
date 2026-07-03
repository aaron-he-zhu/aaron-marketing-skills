# Recursive Refinement Loop (CORE-EEAT)

A capped loop for pushing a draft toward its CORE-EEAT target band. Score, find the
weakest dimensions, revise, rescore. Stop early when the band is met. **Never more than 3
rounds.** This loop tunes scores; it does not change how vetoes work.

## Hard rule — a veto stays terminal

If any veto item fails (T04, C01, R10), the page is **BLOCKED**. The loop does not soften,
average away, or override that. A veto-failed page exits the loop immediately with
`status: BLOCKED` regardless of how many rounds are left. Run the loop only on pages that
pass all three veto checks. If a veto appears mid-loop (e.g. a revision introduces a
mismatched claim), stop the loop and mark BLOCKED. See
[auditor-runbook.md §2](../../../../references/auditor-runbook.md) for cap and
veto handling.

## Target band

Pick the band before round 1 and state it. Default target is the **Good** band (75–89) on
the content-type weighted total. If the user names a different floor, use that. The loop ends
the moment `final_overall_score` lands in or above the band.

## The loop

```
round = 0
if any veto fails:           → status: BLOCKED, exit (no rounds)
score the draft (full 80-item pass) → final_overall_score

while final_overall_score < target_band_floor AND round < 3:
    round += 1
    1. List the top-3 weakest dimensions (lowest weighted contribution first:
       dimension_score × content_type_weight, ascending)
    2. Revise the draft to lift those 3 dimensions only — leave passing
       dimensions alone (surgical edits, no full rewrite)
    3. Re-run the full 80-item score → new final_overall_score
    4. If any veto now fails → status: BLOCKED, exit immediately

stop when: band met  OR  round == 3  (whichever comes first)
```

Pick weakest dimensions by **weighted contribution**, not raw score — a low score in a
high-weight dimension costs more than a low score in a low-weight one. Use the content-type
weight table in
[core-eeat-benchmark.md](../../../../references/core-eeat-benchmark.md).

## Stop conditions (any one ends the loop)

| Condition | Outcome |
|---|---|
| `final_overall_score` ≥ target band floor | DONE — report the passing score |
| 3 rounds completed, still below band | DONE_WITH_CONCERNS — report best score + remaining weak dimensions in `open_loops` |
| A veto fails at any point | BLOCKED — terminal, overrides every round |
| A round produces no score gain | Stop early; report and note the plateau in `open_loops` |

## What each round reports

Keep a short per-round line so the trail is auditable:

```
Round 1: overall 64 → weakest [Ept .05=3.0, A .05=3.5, R .15=10.5] → revised → 71
Round 2: overall 71 → weakest [R .15=11.0, E .20=14.0, Exp .20=14.5] → revised → 78  (band met, stop)
```

After the loop, emit the standard auditor handoff with the final round's
`cap_applied`, `raw_overall_score`, and `final_overall_score`. Add a `refinement_rounds`
count to `open_loops` context so a later re-audit knows how much tuning already happened.

## Deferred — learned-rejection memory

Pre-deducting points for patterns that were rejected in past audits ("learned rejection")
is **not implemented and not part of this loop.** No corpus of past rejections exists yet,
so there is nothing to learn from. If it is ever added, it stays **project-local memory**
(under the user's `memory/` tree) — it is never a committed file in this repo, because the
patterns are specific to one project's content history, not shared skill logic.
