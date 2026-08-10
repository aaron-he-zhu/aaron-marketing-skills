---
name: narrative-quality-auditor
slug: aaron-narrative-quality-auditor
displayName: "Narrative Quality Auditor · 品牌叙事质量门"
summary: "叙事真实性/系统一致性/效果证据分层审计"
description: 'Use when the user asks to "audit our brand narrative" or "is this message on-canon"; runs separate typed TALE truth, system, or effectiveness profiles and never averages them into one composite. Checks differentiation, canon, landing consistency, and evidence integrity. Not for launch readiness — use launch-readiness-auditor; not for social operations — use social-quality-auditor. 品牌叙事分层审计/发布前一致性放行'
version: "19.2.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use for narrative truth, message-system consistency, flagship pre-publish alignment, or measured message-effectiveness review. A full review runs linked profiles separately."
argument-hint: "<canon/surfaces/experiment> [truth|system|effectiveness|full]"
class: auditor
metadata: {"author": "aaron-he-zhu", "version": "19.2.0", "discipline": "narrative", "phase": "evaluate", "geo-relevance": "low", "hermes": {"tags": ["marketing", "narrative", "evaluate"], "category": "narrative"}, "openclaw": {"emoji": "📖", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Narrative Quality Auditor

Audit narrative truth, message-system coherence, or measured effectiveness as separate TALE profiles. There is no v18 overall composite: truth cannot be averaged away by coherence, and coherence cannot stand in for effectiveness evidence.

## When This Must Trigger

- The user asks whether positioning/differentiation is defensible.
- A flagship surface needs a pre-publish canon/message-match gate.
- A message experiment or resonance claim needs evidence-integrity review.
- A full narrative review is requested; run linked profiles rather than one blended score.

## Quick Start

```text
Run TALE truth on canon v7 against named alternatives and approved claims.
Run TALE system on homepage/pricing/deck against canon v7 before release.
Run a full review as three linked profile results; do not compute an overall score.
```

## Skill Contract

**Reads:** one canon/surface set or message experiment plus current narrative/claims truth. **Writes:** only permissioned v3 artifacts. **Done when:** each requested profile is independently complete or its Unknowns are explicit, with no canon, claims, or surface mutation.

`narrative-registry` owns canon/version state and `offer-claims-registry` owns claims. This skill judges; authoring/fixing belongs to Trace/Architect/Land skills.

## Data Sources

| Need | Preferred evidence |
|---|---|
| Truth | Named alternatives, interviews/win-loss, product reality, claims projection |
| Architecture | Exact canon/version, message hierarchy, voice/naming/version history |
| Landing | Declared rendered flagship surfaces linked to canon version |
| Effectiveness | Preregistered comprehension/recall/behavior evidence and locked panels |
| Public resonance | Dated own/public signals with explicit measured/proxy provenance |

## Instructions

### Runtime Reads

- `../../../references/auditor-runbook.md`
- `../../../references/scoring-semantics.md`
- `../../../references/tale-benchmark.md`
- `../../../references/runtime-invocation.md`
- `references/auditor-runtime.md`

### Runtime and Setup

Read `../../../references/auditor-runbook.md`, `scoring-semantics.md`, `tale-benchmark.md`, and the TALE catalog entry. Standalone installs use bundled immutable `references/auditor-runtime.md`; never fetch mutable `main`. Before deterministic calls, follow [`runtime-invocation.md`](../../../references/runtime-invocation.md), resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"`, and require the scorer, validator, and typed catalogs. If unavailable, still collect the selected profile's typed observations and Unknowns, but return `score_state: NOT_SCORED` / `score_confidence: not_scored` with no gate verdict or persistent artifact; runtime absence blocks deterministic scoring, not the observation pass.

Declare target, profile/mode, brand scope, market, audience, canon version, observation date, and evidence window.

### Profile Procedure

- **`truth`:** score T1–T10 for material differentiation and factual grounding.
- **`system`:** score A1–A10 and L1–L10 for canon coherence and landing consistency.
- **`effectiveness`:** score E1–E10 for one experiment/locked panel/date.
- **`full`:** run the three profiles independently and keep three artifacts/results. Aggregate release language conservatively: any BLOCK → block; otherwise any UNDECIDED → undecided; otherwise any FIX → fix; all SHIP → ship. Never average scores.

For a flagship pre-publish gate, always execute the `system` profile procedure and require a compatible current `truth` result. If no compatible truth result exists, run `truth` separately when its evidence is available; otherwise record the truth prerequisite as Unknown while still rendering the requested system-profile result. A missing scorer/runtime changes that result to `NOT_SCORED/UNDECIDED`; it does not justify skipping the profile. Run `effectiveness` separately only when the user requests it or the surface makes an effectiveness claim.

Every observed state needs source/date/type/confidence. A missing canon is Unknown, not N/A. A2/A4/A8 are conditional: three pillars, a change arc, and fixed boilerplate lengths are patterns only when deliberately chosen. Run the typed scorer per profile.

Verify profile-relevant vetoes: `TALE-T1` false/contradictory/unsubstantiated material differentiation, `TALE-A1` demonstrated canon contradiction, `TALE-L1` material flagship/canon contradiction, and `TALE-E1` unsupported effectiveness claim or proxy-as-measured.

## §2 TALE Worked Examples

- Complete truth profile, raw 86, no veto/fail: `DONE/SHIP`, final 86.
- Complete system profile, raw 80, one verified L1 failure: `DONE_WITH_CONCERNS/FIX`, final 59.
- Complete system profile with A1 and L1 failures: `DONE/BLOCK`, no final score.
- Effectiveness profile before test results exist: `NEEDS_INPUT/UNDECIDED`, no score.

## §3 TALE Guardrails

- A literal “onlyness” sentence is not required; judge the material differentiation actually asserted.
- Three pillars, a Raskin/change arc, and 25/50/100-word boilerplates are conditional patterns.
- A governed draft can be audited as a draft; missing access is Unknown, not an A1 failure.
- Share of voice, sentiment, answer-engine descriptions, comprehension, and behavior are distinct constructs.
- Narrative change frequency is a drift signal, not an automatic veto.

## §5 TALE Translation

Always name truth/system/effectiveness. On trace request, qualify `TALE-T1/A1/L1/E1`, especially `TALE-E1` versus `ECHO-E1` and `TALE-A1` versus ROAS/RAMP.

## Report and Verdict

Begin with the auditor-runbook's exact typed conversation header. Never replace `status`, `verdict`, or `score_state` with prose; list each explicitly missing qualified item as ``ID: `unknown``` before findings.

For each profile show verdict, target/canon/context/date, score or coverage/interval, confidence, evidence, Unknowns, and fixes. A full report shows three side-by-side results and no overall number. Do not claim market effectiveness from system coherence.

## Validation Checkpoints

- One profile/unit per score; full mode preserves three results.
- Canon/surface/experiment versions and audience/market are explicit.
- Conditional templates use N/A only with reason; missing evidence stays Unknown.
- Current truth/claims projections are read, not candidate files.
- No canon/claim/surface write or publish action occurred.

## Persistence

Persist only after explicit authorization to `memory/audits/narrative/YYYY-MM-DD-<topic>-<profile>.md`. Preserve the scorer's orthogonal `status` and `verdict`; validate the complete v3 draft with `validate-audit-artifact.py` against the intended relative path, persist only through one full-content Write, and revalidate the target per the auditor runbook. Edit/shell/MCP mutations of the reserved sink are unsupported. Never overwrite another profile or update canon/claims/hot cache autonomously.

## Reference Materials

- [TALE benchmark](../../../references/tale-benchmark.md)
- [Auditor runbook](../../../references/auditor-runbook.md)
- [Scoring semantics](../../../references/scoring-semantics.md)
- [Measurement protocol](../../../references/measurement-protocol.md)

## Next Best Skill

- **Truth repair:** [positioning-truth-tracer](../../trace/positioning-truth-tracer/SKILL.md)
- **Architecture repair:** [message-system-architect](../../architect/message-system-architect/SKILL.md)
- **Landing repair:** [narrative-cascade-planner](../../land/narrative-cascade-planner/SKILL.md)
- **Effectiveness evidence:** [message-test-designer](../message-test-designer/SKILL.md)
