---
name: ad-account-auditor
slug: aaron-ad-account-auditor
displayName: "Ad Account Auditor · 付费广告账户审计"
summary: "付费广告账户审计/ROAS评分"
description: 'Use when auditing a paid ad account for incremental contribution, wasted spend, or measurement integrity before scaling; runs a typed 20-item ROAS profile with verified vetoes and a SHIP/FIX/BLOCK/UNDECIDED gate on own exported data. Not for campaign structure design — use campaign-architect; not for creative production — use ad-creative-builder. 付费广告账户审计/ROAS评分'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when checking whether a paid account or portfolio is safe to launch or scale. Requires normalized own-data outcomes, attribution windows, currency, conversion lag, and business constraints."
argument-hint: "<campaign + outcome exports> <currency/window/lag> [profile]"
allowed-tools: WebFetch
class: auditor
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "ad", "phase": "activate", "geo-relevance": "medium", "hermes": {"tags": ["marketing", "ad", "activate"], "category": "ad"}, "openclaw": {"emoji": "🎯", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Ad Account Auditor

Audit one paid-media account or portfolio for incremental contribution and operating quality under declared constraints. Platform-reported ROAS is one input, never the objective or truth set by itself.

## When This Must Trigger

- Before launching, materially increasing spend, or changing a risky bid/targeting strategy.
- When tracking, attribution inflation, unsafe placements, claims, or wasted spend are in doubt.
- When the user requests a ROAS/RQS account audit from their exports.

## Quick Start

```text
Audit this USD account for direct response using 7-day click, 3-day lag, and $120 CAC ceiling.
Run the incremental-profit profile against the holdout and order-ID exports.
```

## Skill Contract

**Reads:** one normalized account/portfolio evidence set. **Writes:** only a permissioned v3 artifact. **Done when:** required context and all 20 states are explicit, vetoes use verified evidence, and scorer output is reported without executing spend changes.

This skill judges. `conversion-signal-qa`, `attribution-reconciler`, `campaign-architect`, `ad-creative-builder`, and `budget-pacing-monitor` build/fix the inputs. Never enable campaigns, change bids, upload audiences, or scale budgets without separate explicit approval.

## Data Sources

| Need | Preferred evidence |
|---|---|
| Delivery/spend | Campaign, query, placement, audience, and change-history exports |
| Outcome truth | Deduplicated order/lead IDs from ecommerce, analytics, or CRM |
| Economics | Currency, margin/contribution, CAC/payback constraint |
| Attribution | Platform + own-data timestamps/IDs, normalized windows and lag |
| Safety/claims | Placement report, rendered ad/landing, approved claim/disclosure state from [offer-claims-registry](../../../protocol/offer-claims-registry/SKILL.md) (the paid claims SSOT) |
| Incrementality | Holdout/geo split/causal test, otherwise explicitly labeled proxy |

## Instructions

### Runtime and Setup

Read `../../../references/auditor-runbook.md`, `scoring-semantics.md`, `roas-benchmark.md`, and the ROAS catalog entry. Standalone installs use bundled immutable `references/auditor-runtime.md`; never fetch mutable `main`. Before deterministic calls, follow [`runtime-invocation.md`](../../../references/runtime-invocation.md), resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"`, and require the scorer, validator, and typed catalogs. If unavailable, return `score_state: NOT_SCORED` / `score_confidence: not_scored` with no gate verdict or persistent artifact.

Declare profile (`direct-response|prospecting|incremental-profit`), target, currency, attribution window, conversion lag, business constraint, goal, and observation date. If any required context is missing, return `NEEDS_INPUT/UNDECIDED`.

### Evidence and Scoring

1. Normalize currency, windows, IDs, lag, and portfolio scope before comparing metrics.
2. Score all 20 `R1..S5` criteria from the benchmark with source/date/type/confidence.
3. Use Unknown for missing own-data truth, placement exports, or reconciliation. No data is not a veto and cannot be N/A merely because access is inconvenient.
4. Verify vetoes:
   - `ROAS-R1`: instrumentation demonstrably fails the named own-data truth set.
   - `ROAS-R2`: material double-counting/inflation is demonstrated.
   - `ROAS-O1`: material claim/disclosure failure against the `offer-claims-registry` approved state.
   - `ROAS-O2`: applicable platform/restricted-category violation.
   - `ROAS-A1`: placement evidence demonstrates a material safety breach.
5. Run the typed scorer. Report estimated/proxy incrementality as such; do not call platform attribution causal.

## §2 ROAS Worked Examples

- Complete direct-response profile, raw 78, no veto/fail: `DONE/SHIP`, final 78.
- Complete profile, raw 78, one verified R1 failure: `DONE_WITH_CONCERNS/FIX`, final 59.
- Complete profile, verified R1 and R2 failures: `DONE/BLOCK`, raw retained, no final score.
- Missing placement report: A1 Unknown, `NEEDS_INPUT/UNDECIDED`, no overall score.

## §3 ROAS Guardrails

- High reported ROAS can reflect under-spend, branded-demand capture, or attribution inflation.
- Learning-phase disruption is an S2 finding, not an automatic veto.
- ATT/modeled data may reduce confidence; it does not automatically fail R1.
- Frequency, creative fatigue, and audience saturation require separate evidence.
- Never compare cross-platform returns before normalizing currency/window/lag and deduplicating outcomes.

## §5 ROAS Translation

Lead with business impact and evidence. On trace request, qualify `ROAS-R1/R2/O1/O2/A1`; do not expose bare IDs that collide with RAMP/ECHO/TALE.

## Report and Verdict

Begin with the auditor-runbook's exact typed conversation header. Never replace `status`, `verdict`, or `score_state` with prose; list each explicitly missing qualified item as ``ID: `unknown``` before findings.

Show verdict, profile/context, score or coverage/interval, confidence, R/O/A/S detail, reconciliation table, verified critical controls, Unknown evidence, and prioritized fix/owner/rerun condition. The scorer owns status/verdict and the 59 ceiling.

## Validation Checkpoints

- Scope/currency/window/lag/constraint/goal are explicit.
- Own-data outcome truth is separated from platform self-report.
- All 20 items have valid states and provenance; Unknown is not renormalized.
- Veto failures are positively verified.
- No spend/account mutation occurred without separate approval.

## Persistence

Persist only after explicit authorization to `memory/audits/ad/YYYY-MM-DD-<topic>.md`. Assemble and validate the complete v3 draft with `validate-audit-artifact.py` against that intended `--relative-path`, persist only through one full-content Write, then revalidate the target as required by the auditor runbook. Edit/shell/MCP mutations of the reserved sink are unsupported. Do not autonomously write hot cache, claims, candidates, or account state.

## Reference Materials

- [ROAS benchmark](../../../references/roas-benchmark.md)
- [Measurement protocol](../../../references/measurement-protocol.md)
- [Auditor runbook](../../../references/auditor-runbook.md)
- [Scoring semantics](../../../references/scoring-semantics.md)

## Next Best Skill

- **Tracking:** [conversion-signal-qa](../conversion-signal-qa/SKILL.md)
- **Claims/disclosures:** [offer-claims-registry](../../../protocol/offer-claims-registry/SKILL.md) — the approved claim/disclosure state behind `ROAS-O1`
- **Attribution:** [attribution-reconciler](../../scale/attribution-reconciler/SKILL.md)
- **Structure/audience:** [campaign-architect](../../research/campaign-architect/SKILL.md)
- **Pacing:** [budget-pacing-monitor](../../scale/budget-pacing-monitor/SKILL.md)
