---
name: launch-readiness-auditor
slug: aaron-launch-readiness-auditor
displayName: "Launch Readiness Auditor · 发布就绪审计"
summary: "发布就绪审计/RAMP分阶段评估/发布前放行"
description: 'Use when the user asks to "audit our launch plan", "are we ready to launch", or evaluate launch execution/outcomes; runs one typed RAMP preflight, execution, or outcome profile without mixing time horizons. Not for recording launch state — use launch-registry; not for running launch day — use launch-day-conductor. 发布就绪审计/RAMP分阶段评估/发布前放行'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use for launch-eve readiness, an observed launch-window execution audit, or a post-lag outcome review. Each run uses one lifecycle profile and never averages plans, execution, and outcomes."
argument-hint: "<launch slug/plan/evidence> [preflight|execution|outcome]"
allowed-tools: WebFetch
class: auditor
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "launch", "phase": "mobilize", "geo-relevance": "low", "hermes": {"tags": ["marketing", "launch", "mobilize"], "category": "launch"}, "openclaw": {"emoji": "🚀", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Launch Readiness Auditor

Audit one launch at one lifecycle read. Preflight evaluates readiness/assets plus planned policy and instrumentation red lines; execution evaluates observed launch-window operation; outcome evaluates post-lag proof. There is no cross-time composite.

## When This Must Trigger

- Before a committed launch/announcement when go/no-go evidence is needed.
- During/after the launch window when execution quality must be assessed.
- After the declared lag when actual outcomes and learnings are reviewed.

## Quick Start

```text
Run RAMP preflight for launch alpha against the registry stage, canon, claims, rules, and event QA.
Run the outcome profile at day 30; keep it separate from the preflight result.
```

## Skill Contract

**Reads:** one launch, one lifecycle read, registry/canon/claims state, and profile-specific evidence. **Writes:** only a permissioned v3 artifact. **Done when:** the selected profile is complete or its exact Unknowns are reported, with no launch execution or registry mutation.

`launch-registry` owns stage/date/embargo facts. `launch-day-conductor` executes the runbook. This auditor only judges the frozen evidence.

## Data Sources

| Need | Preferred evidence |
|---|---|
| Stage/access | Projected launch record plus direct access/eligibility check |
| Narrative/claims | Canon version, claims projection, rendered assets |
| Operations/rules | Launch plan, commitments, dated official platform rules |
| Instrumentation | Verified events/UTMs and destination truth checks |
| Execution | Timestamped action/incident/response evidence |
| Outcomes | Own analytics/CRM/store truth after declared lag |

## Instructions

### Runtime and Setup

Read `../../../references/auditor-runbook.md`, `scoring-semantics.md`, `ramp-benchmark.md`, and the RAMP catalog entry. Standalone installs use bundled immutable `references/auditor-runtime.md`; never fetch mutable `main`. Before deterministic calls, follow [`runtime-invocation.md`](../../../references/runtime-invocation.md), resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"`, and require the scorer, validator, and typed catalogs. If unavailable, return `score_state: NOT_SCORED` / `score_confidence: not_scored` with no gate verdict or persistent artifact.

Declare profile/lifecycle read (`preflight|execution|outcome`), target launch, launch type, market, access model, observation date, and evidence window.

### Profile Procedure

- **Preflight:** score R1–R10, A1–A10, planned M1, and P1. A public pricing page is required only when the declared access model promises public paid availability.
- **Execution:** score observed M1–M10; do not substitute planned runbook quality for actual execution.
- **Outcome:** score P2–P10 after the declared lag; do not backfill forecast targets as actuals.

Every observed state needs source/date/type/confidence. Missing applicable evidence is Unknown; catalog-authorized conditional items may be N/A with reason. Run `python3 "$AARON_SKILLS_ROOT/scripts/rubric-score.py" score <run.json>` on the selected typed profile.

Verify profile-relevant vetoes: `RAMP-R1` stage/access contradiction, `RAMP-A1` material claim/disclosure failure, `RAMP-M1` planned or observed manipulation/embargo/platform violation, and `RAMP-P1` demonstrably broken instrumentation on participating surfaces.

## §2 RAMP Worked Examples

- Complete preflight, raw 80, no veto/fail: `DONE/SHIP`, final 80.
- Complete preflight, raw 76, one verified A1 failure: `DONE_WITH_CONCERNS/FIX`, final 59.
- Complete preflight, verified R1 and M1 failures: `DONE/BLOCK`, no final score.
- Outcome read before conversion lag or without own-data actuals: `NEEDS_INPUT/UNDECIDED`, no score.

## §3 RAMP Guardrails

- Stage truth follows promised access/eligibility; a pricing page is not universal evidence of GA.
- A genuine feedback request is not vote solicitation.
- Privacy-limited modeled measurement may be Partial; broken required instrumentation is P1 Fail.
- Launch stacking/capacity is an M10 finding, not an automatic veto.
- Never average preflight, execution, and outcome profiles or compare their scores as the same construct.

## §5 RAMP Translation

State lifecycle read with every result. On trace request, qualify `RAMP-R1/A1/M1/P1`, especially against colliding ROAS IDs.

## Report and Verdict

Begin with the auditor-runbook's exact typed conversation header. Never replace `status`, `verdict`, or `score_state` with prose; list each explicitly missing qualified item as ``ID: `unknown``` before findings. Use the stable catalog ID verbatim (for example, `RAMP-R1`); never substitute an evidence-subcheck label or synthesize a suffixed ID such as `RAMP-R1d`.

Lead with lifecycle-specific verdict, target/context/date, score or coverage/interval, confidence, profile detail, linked prior reads, critical evidence, Unknowns, and fix/rerun owner. A preflight SHIP authorizes no external launch action by itself; explicit execution approval remains required.

## Validation Checkpoints

- One launch and one lifecycle profile are declared.
- Plan, execution, and outcome evidence were not mixed.
- Expected items only are scored; Unknown/N/A semantics are correct.
- Stage/access, policy, claims, and instrumentation vetoes are positively verified.
- No launch, submission, registry, or campaign side effect occurred.

## Persistence

Persist only after explicit authorization to `memory/audits/launch/YYYY-MM-DD-<topic>.md`. Preserve the scorer's orthogonal `status` and `verdict`; validate the complete v3 draft with `validate-audit-artifact.py` against the intended relative path, persist only through one full-content Write, and revalidate the target per the auditor runbook. Edit/shell/MCP mutations of the reserved sink are unsupported. Create separate files for separate lifecycle reads and link them by launch ID rather than overwriting.

## Reference Materials

- [RAMP benchmark](../../../references/ramp-benchmark.md)
- [Auditor runbook](../../../references/auditor-runbook.md)
- [Scoring semantics](../../../references/scoring-semantics.md)
- [Measurement protocol](../../../references/measurement-protocol.md)

## Next Best Skill

- **Stage/commitment facts:** [launch-registry](../../../protocol/launch-registry/SKILL.md)
- **Asset/technical fixes:** [launch-asset-packager](../../assemble/launch-asset-packager/SKILL.md)
- **Execute approved plan:** [launch-day-conductor](../launch-day-conductor/SKILL.md)
- **Outcome monitoring:** [launch-monitor](../../prove/launch-monitor/SKILL.md)
