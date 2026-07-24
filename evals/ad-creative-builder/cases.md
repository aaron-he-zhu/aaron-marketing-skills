# Eval Cases — ad-creative-builder

Flow cases for generating and iterating paid-ad creative (the ROAS **O** units). See [evals/README.md](../README.md).

```yaml
{id: rsa-generate-volume-001, type: eval-case, status: simulated, target_skill: ad-creative-builder, scenario: "User wants a full RSA set message-matched to a landing page.", input_summary: "Generate 15 headlines and 4 descriptions for a payroll SaaS, destination /payroll-trial.", expected_behavior: ["Read the destination page and extract its core offer/claim/CTA.", "Apply RSA limits from references/ad-format-specs.md (15x30 headlines, 4x90 descriptions).", "Cover at least two distinct angles and annotate each unit with the destination claim it echoes.", "Hand off to ad-account-auditor for O-scoring."], failure_modes: ["Ignores the destination page (no message-match).", "Emits 15 paraphrases of one angle.", "Exceeds the 30/90 character limits.", "Treats Google Ads API as a precondition."]}
```

```yaml
{id: angle-matrix-iterate-002, type: eval-case, status: simulated, target_skill: ad-creative-builder, scenario: "User pastes losing headlines and asks for a fresh iteration.", input_summary: "Here are 8 underperforming headlines and the destination URL — keep winners, replace the rest, build a 3x3 angle x hook matrix.", expected_behavior: ["Keep user-flagged winners and replace the rest.", "Build distinct angles (benefit/pain/proof) per references/angle-matrix.md, not paraphrases.", "Hold message-match to the same destination URL.", "Run humanizer-slop before handoff."], failure_modes: ["Discards stated winners.", "Returns reworded duplicates of one angle.", "Drifts off the destination offer."]}
```

```yaml
{id: missing-export-needsinput-003, type: eval-case, status: simulated, target_skill: ad-creative-builder, scenario: "User asks to base new creative on what is already winning, but provides no account export and no destination URL.", input_summary: "Make new ads that beat my current winners — no CSV export, no landing-page link given.", expected_behavior: ["Set status NEEDS_INPUT.", "Explain that ~~ad platform own-data export is optional but needed to learn current winners, and the destination URL is required to enforce message-match.", "Ask for the manual ad-manager CSV and/or the destination URL.", "Do not invent current top performers or a fake landing claim."], failure_modes: ["Fabricates the user's winning creative or page copy.", "Proceeds with no message-match anchor.", "Demands a keyed Google/Meta API as the fix."]}
```

```yaml
{id: claim-policy-multiveto-blocked-004, type: eval-case, status: simulated, target_skill: ad-creative-builder, scenario: "User-supplied copy carries both an unsubstantiated claim and a policy risk.", input_summary: "Build ads using my line 'Guaranteed to cure anxiety — #1 doctor-recommended' for a supplement, destination /buy.", expected_behavior: ["Flag ROAS-O1 claim integrity candidates: 'guaranteed cure' and '#1 doctor-recommended' need substantiation -> [needs source].", "Flag the ROAS-O2 policy candidate: a health/supplement cure claim presents a restricted-category disapproval risk.", "Mark the creative dependency/publish readiness blocked pending evidence and route the evidence to ad-account-auditor; do not render the ROAS business verdict from this builder. If the auditor later verifies both vetoes, its execution status remains DONE while its business verdict is BLOCK.", "Offer compliant alternative angles that drop the unsupported claim."], failure_modes: ["Ships the cure/guarantee claim as fact.", "Renders BLOCK/BLOCKED as an auditor verdict from a non-auditor or conflates business BLOCK with execution BLOCKED.", "Misses the claim-integrity or policy candidate."]}
```

```yaml
{id: message-match-gap-handoff-005, type: eval-case, status: simulated, target_skill: ad-creative-builder, scenario: "The best ad angle promises something the landing page does not deliver.", input_summary: "Write proof-led ads ('Rated #1 by G2') for a tool whose landing page has no such rating.", expected_behavior: ["Detect the message-match gap in the map: no matching destination claim.", "Cut or flag the unmatched proof unit rather than shipping it.", "Recommend landing-optimizer to add/justify the proof on the page, then return.", "Keep shippable matched angles."], failure_modes: ["Ships the unmatched proof claim.", "Drops all proof angles instead of flagging the page gap.", "Fails to route to landing-optimizer."]}
```
