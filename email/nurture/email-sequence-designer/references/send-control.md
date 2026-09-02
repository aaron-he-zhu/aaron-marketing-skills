# Email Send Control

Use this control whenever an email artifact could move from design into an ESP. It specializes the shared evidence, authorization, and receipt rules for email; it does not replace the consent registry or grant permission to send.

## Identity and privacy

- Use a host-issued opaque `subject_ref` for a person across segmentation, consent checks, suppression checks, and delivery receipts. Do not derive it with an unsalted hash of an email address.
- Raw email addresses may exist only transiently at the connector boundary needed for the requested operation. Never persist them in WARM artifacts, handoffs, logs, eval output, or measurement reports.
- Tier 1 outputs segment rules and aggregate counts. If stable opaque subject references are unavailable, do not emit a member-level manifest.

## Immutable send inputs

A sendable cohort is bound by `segment_ref`, `definition_version`, `definition_hash`, `evaluated_at`, `consent_snapshot_ref`, `suppression_snapshot_ref`, and aggregate eligible/excluded counts. A creative is bound by `creative_ref`, `creative_version`, `creative_hash`, and, after rendering, `html_hash` plus `plain_text_hash`. Any change creates a new version; it does not silently mutate the approved input.

The consent and suppression snapshots are observations, not permanent clearance. Re-read the current registry state immediately before every live send and exclude any newly suppressed subject. A stale or missing snapshot fails closed.

## Create is not send

Keep these states distinct:

1. **Plan/draft** — local flow, segment, creative, or HTML only.
2. **ESP create** — the provider accepted a draft/broadcast object. Its create result is not evidence of delivery or scheduling.
3. **Send intent** — exact ESP object, segment-definition version, payload hashes, sender, schedule, and limits awaiting operation-specific authorization.
4. **Send receipt** — provider or connector evidence returned after the authorized live send attempt.

A preview, dry run, command text, saved file, SHIP verdict, create response, or test design is never a send receipt. Authorization for create does not authorize send, and authorization for one payload/version/segment/schedule cannot be reused after any of them changes.

## Receipt and partial semantics

A real send receipt binds `intent_ref`, provider operation reference, attempted/completed times, accepted/rejected/deferred counts, status (`succeeded | partial | failed | unknown`), and evidence reference. `partial` is not success: report the rejected/deferred cohort and leave remediation open. If the connector cannot return provider evidence, report `receipt: unavailable`; never synthesize one from the plan.

Post-send monitoring and experiments bind their results to the send receipt, measurement contract, segment-definition version, and creative/HTML hashes. A result export with no matching receipt is usable as user-provided evidence only, with the binding gap explicit.
