# Quality Review Aids — creator-content-auditor

Extra inputs for the **Quality Assessment** (step 5) and **Compliance / Platform-Specific** (step 4) sections. These do not change the STAR veto set.

## AI-slop / humanizer signals: Appeal evidence only

Run the content through the slop checklist in [humanizer-slop.md](../../../../references/humanizer-slop.md) only to collect specific observations for the applicable STAR **Appeal** items.

- Do not apply a fixed deduction, a hand-calculated subtotal, or a standalone pass/fail rule from a signal count.
- Do not let slop observations set `status`, `verdict`, `score_state`, raw/final score, or `cap_applied`; the typed scorer owns those fields.
- Slop is never a veto. The complete STAR veto set remains `STAR-S2`, `STAR-S6`, `STAR-T1`, `STAR-T2`, and `STAR-T3`.

Record each concrete signal with location/timecode and evidence ref, map it to the applicable Appeal item, and let the typed run determine its effect.

## Veto and final-result boundary

- `STAR-S2`: verified follower fraud / real-follower rate below the typed tier benchmark.
- `STAR-S6`: verified bought, coordinated, or pod-based engagement.
- `STAR-T1`: applicable market/platform disclosure failure when a material connection exists.
- `STAR-T2`: verified false or unsubstantiated material claim.
- `STAR-T3`: documented disqualifying brand-safety evidence under the declared policy/window.

Unknown or refused evidence never fires a veto. Copy the final `status`, `verdict`, `score_state`, `raw_overall_score`, `final_overall_score`, and `cap_applied` only from the typed scorer. Exactly one verified veto yields `DONE_WITH_CONCERNS/FIX`, `cap_applied: true`, and a final score capped at 59; two or more yield `DONE/BLOCK`, `cap_applied: false`, and no final score. Do not compute a legacy `/10` result or a second decision.

## Multi-persona review

For higher-stakes or ambiguous submissions, run the content past the persona set in [expert-panel.md](../../../../references/expert-panel.md). Each persona reviews from one lens (e.g. brand, compliance, audience, platform-native), then reconcile only their evidence observations into the typed STAR run. Persona votes or prose never create a parallel gate decision. Use this when a solo pass feels under-confident, not for every routine submission.

## Per-platform format & disclosure norms

Before filling the **Platform-Specific Requirements** and **Technical Specifications** tables, load the matching platform note for current format limits and disclosure conventions:

- [platforms/tiktok.md](../../../../references/platforms/tiktok.md)
- [platforms/youtube.md](../../../../references/platforms/youtube.md)
- [platforms/x.md](../../../../references/platforms/x.md)
- [platforms/linkedin.md](../../../../references/platforms/linkedin.md)
- [platforms/reddit.md](../../../../references/platforms/reddit.md)

Platform notes inform the checks only when their date and applicability match the declared platform/market. `STAR-T1` is evaluated from the applicable market/platform rule and material-connection facts; a platform note alone does not replace that evidence.
