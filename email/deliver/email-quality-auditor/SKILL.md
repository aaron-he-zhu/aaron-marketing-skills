---
name: email-quality-auditor
slug: aaron-email-quality-auditor
displayName: "Email Quality Auditor · 邮件质量审计"
summary: "邮件质量审计/EQS评分/发送前放行"
description: 'Use when the user asks to "audit an email program" or "is this campaign safe to send"; runs a typed 20-item SEND profile with authentication, consent, opt-out, and claim veto checks on own evidence. Not for building deliverability setup — use deliverability-qa; not for designing lifecycle flows — use email-sequence-designer. 邮件质量审计/EQS评分/发送前放行'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when checking an email program or send before release, or when authentication, consent, suppression, engagement quality, lifecycle fit, claims, or outcome attribution are in doubt."
argument-hint: "<ESP/DMARC/outcome evidence> [promotional|retention|cold-outbound|newsletter]"
allowed-tools: WebFetch
class: auditor
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "email", "phase": "deliver", "geo-relevance": "low", "hermes": {"tags": ["marketing", "email", "deliver"], "category": "email"}, "openclaw": {"emoji": "✉️", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Email Quality Auditor

Audit one email program/profile and observation window with SEND. Open rate is MPP-sensitive proxy evidence; direct action and the program's declared outcome truth set carry the outcome read.

## When This Must Trigger

- Before a material broadcast/sequence release when channel safety is uncertain.
- When authentication, consent, suppression, complaints, frequency, claims, or attribution need a gate.
- When the user requests an EQS/SEND baseline or rerun.

## Quick Start

```text
Audit this newsletter using the last 90 days, provider split, MPP share, and subscription truth set.
Check this promotional send against DMARC, consent events, live suppressions, claims, and order IDs.
```

## Skill Contract

**Reads:** one program/profile, normalized window, provider evidence, live consent/suppression state, rendered messages, and outcome truth. **Writes:** only a permissioned v3 artifact. **Done when:** all expected SEND states are explicit and the scorer result is reported without sending email or changing provider settings.

Use `deliverability-qa` to repair authentication, `consent-registry` for lawful-basis/suppression facts, `email-sequence-designer` for journeys, and `send-experiment-designer` for preregistered tests.

## Data Sources

| Need | Preferred evidence |
|---|---|
| Authentication | DNS, message headers, DMARC aggregate evidence |
| Consent/suppression | Append-only consent events plus current live projection |
| Placement/reputation | Provider/seed panel and dated ESP/provider reports |
| Engagement | Cohort/provider/MPP-segmented ESP export |
| Lifecycle | Trigger/flow configuration and event export |
| Outcome | Ecommerce, CRM, subscription, sponsorship, or named equivalent truth set |
| Content | Rendered message/destination and approved claim/disclosure state |

## Instructions

### Runtime and Setup

Read `../../../references/auditor-runbook.md`, `scoring-semantics.md`, `send-benchmark.md`, and the SEND catalog entry. Standalone installs use bundled immutable `references/auditor-runtime.md`; never fetch mutable `main`. Before deterministic calls, follow [`runtime-invocation.md`](../../../references/runtime-invocation.md), resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"`, and require the scorer, validator, and typed catalogs. If unavailable, return `score_state: NOT_SCORED` / `score_confidence: not_scored` with no gate verdict or persistent artifact.

Declare profile (`promotional|retention|cold-outbound|newsletter`), target/program, provider, market, normalized window, list age, MPP share, and observation date.

### Evidence and Scoring

1. Freeze evidence and reconcile provider cohorts/windows before comparing rates.
2. Score all 20 `S1..D5` criteria. Every observed state requires source/date/type/confidence.
3. `E2` is N/A with reason when opens/CTOR are not used. `N3/N5` are conditional by program design. Missing records or exports are Unknown, not N/A.
4. Verify vetoes:
   - `SEND-S1`: required authentication is demonstrably broken/unaligned.
   - `SEND-S2`: a purchased/scraped/unlawful list is verified; missing provenance is Unknown.
   - `SEND-N1`: opt-out is broken/absent or a recorded suppression is not honored.
   - `SEND-D1`: material claim/disclosure/offer term fails approved evidence.
5. Run the typed scorer. Use clicks/replies/downstream actions as primary engagement evidence where available; opens/CTOR remain caveated proxy evidence.

For a send-only review without enough program evidence, report the verified red-line checks and exact gaps but return `NOT_SCORED/UNDECIDED`; “no blocker observed in supplied evidence” is not a full SEND SHIP verdict.

## §2 SEND Worked Examples

- Complete newsletter profile, raw 81, no veto/fail: `DONE/SHIP`, final 81.
- Complete promotional profile, raw 76, one verified S1 failure: `DONE_WITH_CONCERNS/FIX`, final 59.
- Complete profile, verified S2 and N1 failures: `DONE/BLOCK`, no final score.
- Consent provenance absent: S2 Unknown, `NEEDS_INPUT/UNDECIDED`, no score.

## §3 SEND Guardrails

- DMARC `p=none` with aligned SPF/DKIM and active monitoring is not automatically an S1 failure.
- Provider one-click-unsubscribe policy and statutory duties must be named separately.
- Opens and CTOR require MPP segmentation/proxy caveat; they cannot establish human attention alone.
- A newsletter need not have cart/post-purchase flows; score only journeys applicable to its declared program.
- Over-frequency is a serious E4/E5 finding, not an automatic veto.

## §5 SEND Translation

Explain channel and recipient risk in plain language. On trace request, qualify `SEND-S1/S2/N1/D1` and show the underlying DNS/event/rendered evidence.

## Report and Verdict

Begin with the auditor-runbook's exact typed conversation header. Never replace `status`, `verdict`, or `score_state` with prose; list each explicitly missing qualified item as ``ID: `unknown``` before findings.

Show verdict, profile/context, score or coverage/interval, confidence, S/E/N/D detail, outcome truth set, verified critical controls, Unknown inputs, and fix owners. Do not claim deliverability/inbox placement from DNS alone and do not execute a send.

## Validation Checkpoints

- Program/profile/provider/window/list age/market/MPP share are declared.
- Live suppression state was verified by replay, not a stale projection or pending proposal.
- All 20 states are valid; conditional N/A has a reason.
- Provider metrics and reconciled outcome truth are separated.
- No email/provider mutation occurred without separate explicit approval.

## Persistence

Persist only after explicit authorization to `memory/audits/email/YYYY-MM-DD-<topic>.md`. Preserve the scorer's orthogonal `status` and `verdict`; validate the complete v3 draft with `validate-audit-artifact.py` against the intended `--relative-path`, persist only through one full-content Write, and revalidate the target per the auditor runbook. Edit/shell/MCP mutations of the reserved sink are unsupported. Do not autonomously modify consent, claims, provider settings, or hot cache.

## Reference Materials

- [SEND benchmark](../../../references/send-benchmark.md)
- [Measurement protocol](../../../references/measurement-protocol.md)
- [Auditor runbook](../../../references/auditor-runbook.md)
- [Scoring semantics](../../../references/scoring-semantics.md)

## Next Best Skill

- **Authentication/placement:** [deliverability-qa](../../setup/deliverability-qa/SKILL.md)
- **Consent/suppression:** [consent-registry](../../../protocol/consent-registry/SKILL.md)
- **Lifecycle:** [email-sequence-designer](../../nurture/email-sequence-designer/SKILL.md)
- **Experiment:** [send-experiment-designer](../send-experiment-designer/SKILL.md)
