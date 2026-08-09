---
name: social-quality-auditor
slug: aaron-social-quality-auditor
displayName: "Social Quality Auditor · 社媒质量门"
summary: "社媒资产门/运营成熟度/六条红线"
description: 'Use when the user asks to "audit our social presence" or "is this batch safe to publish"; runs either the typed ECHO asset gate or a separate program-maturity profile, with channel-truth, claim, disclosure, manipulation, UGC-rights, and denominator checks. Not for creator deliverables — use creator-content-auditor; not for launch readiness — use launch-readiness-auditor. 社媒资产门/运营成熟度/发布前放行'
version: "19.2.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use for a pre-publish social asset/batch gate or a separate channel-program maturity audit. Never combine the asset and operating profiles into one score."
argument-hint: "<asset batch or channel portfolio> [asset-gate|community|b2c|founder]"
class: auditor
metadata: {"author": "aaron-he-zhu", "version": "19.2.0", "discipline": "social", "phase": "host", "geo-relevance": "low", "hermes": {"tags": ["marketing", "social", "host"], "category": "social"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Social Quality Auditor

Run one ECHO profile on one unit. The `asset-gate` audits a publish package and its governing records; program-maturity profiles audit a channel portfolio/window. Social outcomes remain measured metrics, not part of either rubric score.

## When This Must Trigger

- Before queued posts/assets publish or a paused queue resumes.
- When channel truth, claims, disclosure, engagement manipulation, UGC permission, or reported denominators are in doubt.
- When the user requests a community/B2C/founder program-maturity baseline or rerun.

## Quick Start

```text
Run ECHO asset-gate on this five-post batch against channel/claims/UGC records.
Audit the last 90 days with program-maturity-community; report outcomes separately.
```

## Skill Contract

**Reads:** one asset package or one channel portfolio/window, current governance projections, and dated evidence. **Writes:** only a permissioned v3 artifact. **Done when:** one profile is complete or its Unknowns are explicit, with no publication, queue, registry, or engagement side effect.

`channel-registry`, `offer-claims-registry`, and permission/consent state own truth. This skill judges frozen state and never manufactures permissions or updates canonical records.

## Data Sources

| Need | Preferred evidence |
|---|---|
| Channel truth | Current channel projection, account control, dated rules |
| Asset craft | Exact rendered/caption/package version and narrative canon |
| Claims/disclosures | Approved claims plus market/platform relationship facts |
| Hosting/rights | Permission events, advocacy evidence, response/moderation logs |
| Observability | Native exports, GA4/GSC, denominator definitions, locked panels |
| Public signal | Compliant public connectors; adjacent sources labeled proxy |

## Instructions

### Runtime Reads

- `../../../references/auditor-runbook.md`
- `../../../references/scoring-semantics.md`
- `../../../references/echo-benchmark.md`
- `../../../references/runtime-invocation.md`
- `references/auditor-runtime.md`

### Runtime and Setup

Read `../../../references/auditor-runbook.md`, `scoring-semantics.md`, `echo-benchmark.md`, and the ECHO catalog entry. Standalone installs use bundled immutable `references/auditor-runtime.md`; never fetch mutable `main`. Before deterministic calls, follow [`runtime-invocation.md`](../../../references/runtime-invocation.md), resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"`, and require the scorer, validator, and typed catalogs. If unavailable, return `score_state: NOT_SCORED` / `score_confidence: not_scored` with no gate verdict or persistent artifact.

Declare target, profile, `assessment_mode`, `program_archetype`, channels, market, window, and observation date. Use `assessment_mode: asset` plus `program_archetype: not-applicable` for `asset-gate`; use `assessment_mode: program` plus the exact `community|b2c|founder` archetype for a maturity profile. Profile and context must match.

### Profile Procedure

- **`asset-gate`:** score E1, C1–C10, H1/H2, and O1. An observed asset with no performance rate/metric claim passes O1; missing asset access is Unknown.
- **`program-maturity-community`:** score E/H/O with community weights.
- **`program-maturity-b2c`:** score E/H/O with feed-led weights.
- **`program-maturity-founder`:** score E/H/O with founder-led weights.

Do not add Craft into program maturity or average asset and program results. Every observed state needs source/date/type/confidence. Closed-platform data requires user export; missing private evidence is Unknown.

Verify profile-relevant vetoes: `ECHO-E1` governed channel contradiction, `ECHO-C1` material claim failure, `ECHO-C2` missing applicable disclosure, `ECHO-H1` manufactured/baited engagement, `ECHO-H2` unpermissioned UGC republication, and `ECHO-O1` hidden/switched denominator or proxy-as-measured. Run the typed scorer.

## §2 ECHO Worked Examples

- Complete asset gate, raw 88, no veto/fail: `DONE/SHIP`, final 88.
- Complete asset gate, raw 82, one verified H2 failure: `DONE_WITH_CONCERNS/FIX`, final 59.
- Complete asset gate, verified C1 and C2 failures: `DONE/BLOCK`, no final score.
- Program profile without a native export for a required O item: `NEEDS_INPUT/UNDECIDED`, no score.

## §3 ECHO Guardrails

- Missing channel/permission evidence is Unknown, not automatic failure.
- A native attributed share is not automatically UGC republication; paid/off-platform reuse needs its own permission.
- Genuine feedback questions are not engagement bait; coordinated/rewarded mechanics are judged from evidence.
- Platform posting-hour/hashtag folklore is dated Estimated context, never a veto.
- Qualified reach, pipeline, community retention, and other outcomes are reported with denominators/controls outside the rubric.

## §5 ECHO Translation

State `asset-gate` or exact maturity profile in every result. On trace request, qualify all ECHO IDs, especially `ECHO-O1` versus `ROAS-O1` and `ECHO-E1` versus `TALE-E1`.

## Report and Verdict

Begin with the auditor-runbook's exact typed conversation header. Never replace `status`, `verdict`, or `score_state` with prose; list each explicitly missing qualified item as ``ID: `unknown``` before findings.

Show verdict, unit/profile/context/date, score or coverage/interval, confidence, included-item detail, verified critical controls, Unknown inputs, and fixes. For asset batches, identify the exact asset/location. Never publish or unpause a queue based only on the audit; separate explicit approval is required.

## Validation Checkpoints

- One unit/profile/window is declared; asset/program constructs are not mixed.
- Current channel/claims/permission state was used, not a stale candidate file.
- Expected items have valid states and provenance.
- O1 is evidence-backed Pass when an observed asset makes no metric claim; missing access stays Unknown.
- Outcomes are not smuggled into a rubric score; no side effect occurred.

## Persistence

Persist only after explicit authorization to `memory/audits/social/YYYY-MM-DD-<topic>.md`. Preserve the scorer's orthogonal `status` and `verdict`; validate the complete v3 draft with `validate-audit-artifact.py` against the intended relative path, persist only through one full-content Write, and revalidate the target per the auditor runbook. Edit/shell/MCP mutations of the reserved sink are unsupported. Do not autonomously write channel state, permissions, claims, queues, or hot cache.

## Reference Materials

- [ECHO benchmark](../../../references/echo-benchmark.md)
- [Auditor runbook](../../../references/auditor-runbook.md)
- [Scoring semantics](../../../references/scoring-semantics.md)
- [Measurement protocol](../../../references/measurement-protocol.md)

## Next Best Skill

- **Channel truth:** [channel-registry](../../../protocol/channel-registry/SKILL.md)
- **Claims:** [offer-claims-registry](../../../protocol/offer-claims-registry/SKILL.md)
- **UGC/response:** [engagement-inbox-manager](../engagement-inbox-manager/SKILL.md)
- **Measurement:** [social-measurement-loop](../../observe/social-measurement-loop/SKILL.md)
