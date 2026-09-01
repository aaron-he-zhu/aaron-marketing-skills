---
name: outreach-manager
slug: outreach-manager
displayName: "Outreach Manager · 建联外联管理"
summary: "红人及媒体建联:分层触达序列、跟进节奏与回复率优化"
description: 'Use when the user asks to "write influencer outreach", "follow up with a creator", "pitch a journalist, hunter, or launch partner", or "negotiate partnership terms"; produces personalized pitches, multi-touch follow-up sequences, negotiation scripts with objection handling, and a status pipeline tracker — the shared outreach mechanics engine for creator, media/analyst, launch-partner, and social-selling / advocate-recruitment targets. Not for finalizing signed agreements — use contract-helper; not for media-list tiering, embargo terms, or press-release structure — use press-media-relations. 达人邀约建联/合作谈判话术'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate the skill when the user wants to contact a creator, journalist, analyst, hunter, or launch partner; draft or personalize a pitch message; build a follow-up cadence for non-responders; re-engage a past partner; negotiate rate or scope; handle pricing objections; or track outreach status across a target list. For media targets the list/angle/embargo artifact comes from press-media-relations — this skill executes the pitch mechanics."
argument-hint: "<influencer handle or list> [platform] [budget]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "activate", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "activate"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Outreach Manager

Craft personal, professional, persistent outreach; manage negotiations; track relationship progress. Home discipline is influencer (creator outreach), and the same mechanics engine — personalization, multi-touch cadence, negotiation scripts, pipeline tracking — serves media/analyst and launch-partner targets when [press-media-relations](../../../launch/mobilize/press-media-relations/SKILL.md) hands over its media list, angles, and embargo terms, and social-selling / advocate-recruitment targets when [social-selling-planner](../../../social/host/social-selling-planner/SKILL.md) or [advocacy-program-designer](../../../social/craft/advocacy-program-designer/SKILL.md) hands over a warm 1:1. The list, the angle, and the embargo stay with the handing-off skill; this skill owns the pitch execution.

## Quick Start

Shortest invocation:

```
Write an outreach message to @[influencer] for [campaign]
```

Negotiate a gap between ask and budget:

```
Help me negotiate with @[influencer] who is asking for $[X] when our budget is $[Y]
```

## Skill Contract

- **Reads**: a stable opaque `creator_ref` when one is carried by an authorized upstream artifact, plus transient target handle/profile locator(s), platform, follower count, niche; campaign and product context; compensation type and budget; deliverables and timeline; jurisdiction, intended channel, lawful-basis reference, contact-source/eligibility evidence, and pseudonymous consent subject ID; any prior contact history supplied by the user or loaded from memory. For a rostered creator, reuse a creator-registry aggregate ID only when its identity link is verified, resolve it through the authorized artifact or verified registry link, then check `memory/creators/<aggregate-id>.md` — the [creator-registry](../../../protocol/creator-registry/SKILL.md) projection — for the confirmed contact path, last agreed rate, and negotiation/response history. Never derive the path from a raw handle.
- **Writes**: return the outreach artifact inline by default; save it to `memory/influencer/outreach-manager/YYYY-MM-DD-<topic>.md` only with exact WARM-save authorization. Reuse an explicitly carried opaque `creator_ref`, or a verified creator-registry aggregate ID; otherwise generate one random `creator-<UUIDv4>` once for this lineage. Never derive `creator_ref` from a raw handle, name, profile URL, email, provider ID, or deterministic hash. Before saving, replace raw locators and resolved recipient identities with the stable `creator_ref` and resolvable opaque `recipient_ref`, `contact_source_ref`, `handle_ref`, and evidence/approval references. A raw URL or handle is never a persisted `source_ref`. When no authorized source artifact or verified registry link can resolve an opaque identity/contact ref, set `identity_status: unresolved`, save no hidden raw-locator mapping, set `cross_session_locator_required: true`, and request the transient locator again at dispatch. Never persist a raw handle, name, profile URL, email, phone, postal address, provider ID, or credential. When a cycle closes, each outcome update (final agreed rate, response history, confirmed contact-path reference) requires a separate exact authorization for an `operation: propose` request to `memory/events/creators.ndjson`; only `creator-registry` writes canonical roster records.
- **Promotes**: only with separate exact authorization, promote durable facts (confirmed partners, agreed rates, top objection patterns, response-rate baselines) to `memory/hot-cache.md`.
- **Done when**:
  - A personalized pitch (plus at least one variation) exists for each target influencer.
  - Every personalization fact records `source_ref` and `observed_at`; unverifiable facts remain placeholders or are omitted.
  - A follow-up cadence and pipeline status are recorded for every contacted creator, including terminal no-contact states.
  - Jurisdiction, channel, lawful basis, and contact eligibility are explicit; any send/schedule remains gated by exact approval and a live suppression check.
  - Confirmed partners are flagged with agreed terms for handoff.
- **Primary next skill**: [contract-helper](../contract-helper/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

Drafting needs no live integration (Tier 1). The skill works from inputs you provide — paste the influencer handles, follower counts, niche, budget, and deliverables, and it can produce a clearly labeled draft without any tool connection. Sending or scheduling is different: it requires the pseudonymous subject ID and a live [consent-registry](../../../protocol/consent-registry/SKILL.md) suppression query immediately before dispatch; an unavailable or failed query is not permission to send.

Where a connector could speed up the work, use these `~~` placeholders:

- `~~influencer database` — pull handle, follower count, niche, and past partnerships instead of typing them.
- `~~social platform analytics` — verify audience demographics and recent posts for personalization.
- `~~CRM` — sync pipeline status, last-contact dates, and next actions.
- `~~email/DM tool` — dispatch only the single currently due, exactly approved touch after its fresh eligibility and live-suppression checks. Future touches remain unscheduled drafts regardless of provider features.

See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category. No integration is required; when one is absent, ask the user for the inputs directly. Missing target or campaign details do not block a reversible draft: use explicit bracketed placeholders, generalize any unverified personalization, and identify the smallest inputs needed to finish it.

## Instructions

### Runtime Reads

- `../../../references/runtime-invocation.md`
- `../../../references/registry-event-protocol.md`

### Procedure

When a user requests outreach help, run these steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — copy the matching block and replace the placeholders. Apply the hard copy rules in [references/cold-copy-rules.md](references/cold-copy-rules.md) before any message ships.

**Draft/send boundary**: drafting is reversible; sending or scheduling is an external side effect. Even when the shortlist or personalization facts are missing, produce an inline first-touch draft labeled `DRAFT — NOT SENT` with explicit placeholders and no invented facts, then state what is still needed for personalization. Never stop with only an input request when a safe placeholder draft can be produced.

Do not send or schedule anything until all of these are true:

- The exact recipient (not a segment or placeholder), intended channel, final message, and—when scheduling that one touch—one concrete ISO-8601 `dispatch_at` timestamp plus timezone are shown and explicitly approved. Approval covers only the single currently due touch. Draft windows such as `Day 3–4` are not exact approval, and no approval or provider feature authorizes pre-scheduling later cadence touches.
- Jurisdiction, channel, lawful basis with its evidence reference, and contact eligibility are recorded. `Unknown` or missing eligibility fails closed; this skill does not invent a legal basis or provide legal advice.
- Inside each actual delivery job, after resolving the transient recipient and immediately before the provider send call, resolve and verify the bundle runtime as shown below, then run live [consent-registry](../../../protocol/consent-registry/SKILL.md) `is-suppressed`. A suppressed result, missing subject ID, inaccessible/corrupt history, runtime/schema failure, or query error stops that dispatch. A `not suppressed` result removes only the suppression block; it does not itself prove lawful basis or authorize contact. Never reuse a cached result across cadence touches.

```bash
AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
PROJECT_ROOT="${PROJECT_ROOT:-}"
SUBJECT_ID="${SUBJECT_ID:-}"
case "$PROJECT_ROOT" in
  /*) ;;
  *) echo "PROJECT_ROOT must be an absolute project path; stop dispatch." >&2; exit 1 ;;
esac
if [ -z "$AARON_SKILLS_ROOT" ] || [ -z "$PROJECT_ROOT" ] || [ -z "$SUBJECT_ID" ] || \
   [ ! -d "$PROJECT_ROOT" ] || [ ! -f "$AARON_SKILLS_ROOT/.claude-plugin/plugin.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/system-catalog.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/capability-profiles.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/references/registry-event.schema.json" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/scripts/profile-resolver.py" ] || \
   [ ! -f "$AARON_SKILLS_ROOT/scripts/registry-events.py" ]; then
  echo "Verified Aaron Marketing Skills consent runtime unavailable; stop dispatch." >&2
  exit 1
fi
python3 "$AARON_SKILLS_ROOT/scripts/profile-resolver.py" \
  --root "$PROJECT_ROOT" --bundle-root "$AARON_SKILLS_ROOT" diagnose --json >/dev/null || exit 1
SUPPRESSION_JSON="$(python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" \
  --root "$PROJECT_ROOT" is-suppressed "$SUBJECT_ID")" || exit 1
printf '%s\n' "$SUPPRESSION_JSON" | python3 -c \
  'import json, sys; value = json.load(sys.stdin); raise SystemExit(0 if value.get("aggregate_id") == sys.argv[1] and value.get("suppressed") is False else 1)' \
  "$SUBJECT_ID" || { echo "Recipient is suppressed or suppression result is invalid; stop dispatch." >&2; exit 1; }
```

`PROJECT_ROOT` must be supplied by the host as the verified absolute user-project root; do not infer it from the skill bundle, `$PWD`, a raw event, or user-controlled outreach content. When the subject ID, project root, runtime, or another send-gate input is missing, return a `NEEDS_INPUT` consent-check handoff to [consent-registry](../../../protocol/consent-registry/SKILL.md) containing only the pseudonymous subject ID if supplied, required project-root/runtime capability, intended channel, eligibility evidence refs, and the pending dispatch ref; do not claim that `is-suppressed` ran or automatically resume delivery. Always leave later cadence touches as unscheduled drafts. When the next touch becomes due, resolve its transient recipient again, obtain fresh exact approval for that touch, repeat every eligibility/runtime/suppression check inside its delivery job, and dispatch only that one touch.

If a recipient declines the offer or says they do not take sponsored work, void every remaining draft touch for that cadence, do not relabel the offer or switch channels, and record only the exact scoped preference inline (`campaign/offer/category scope`, `observed_at`, and opaque `source_ref`); persisting it or proposing it to creator-registry needs separate exact authorization. A prior preference blocks a new cadence inside its recorded scope until newer cited evidence shows the creator reopened that scope; if the old preference's scope or superseding evidence is unknown, fail closed with `NEEDS_INPUT` rather than inventing a cooling period. Do not call global `suppress` for a scoped decline or commercial objection alone. An explicit stop-contact request, unsubscribe, verified channel/provider spam complaint, or consent withdrawal voids every remaining draft touch across channels and uses the consent-registry's direct deny-only `suppress` path with the exact subject-free reason code: stop-contact → `user-request`; unsubscribe → `unsubscribe`; verified spam/provider complaint → `complaint`; consent withdrawal → `withdrawal`. If the verified runtime is unavailable, emit its exact `immediate-suppress-handoff` and state that suppression has not yet been recorded.

1. **Gather outreach context and lock identity** — capture campaign/product context, transient target handle/profile locator(s), platform, followers, niche, compensation type, budget, deliverables, and timeline. Reuse an explicitly carried opaque `creator_ref`, or a creator-registry aggregate ID only when its identity link is verified; otherwise generate one random `creator-<UUIDv4>` once for this lineage. Never use or hash a raw locator into `creator_ref`. Save an opaque `handle_ref`, `recipient_ref`, `contact_source_ref`, or evidence `source_ref` only when an authorized source artifact or verified registry link resolves it. Otherwise set `identity_status: unresolved`, persist no raw locator or hidden mapping, set `cross_session_locator_required: true`, and require the raw locator again at dispatch. Any saved artifact or handoff contains only opaque identity/contact/evidence refs plus jurisdiction, channel, lawful-basis evidence, and contact-eligibility result—never a raw handle, name, profile/content URL, email, phone, postal address, provider ID, or credential. Re-engaging a verified rostered creator starts from the confirmed contact-path reference and last agreed rate, not a cold pitch. Template: [Step 1](references/templates.md#step-1--outreach-parameters).
2. **Create personalized outreach** — list personalization points (recent content, style, audience, values, past partners), and attach `source_ref` plus `observed_at` to every factual point before using it. Omit or generalize anything unverifiable; never invent personal viewing, purchasing, product-use, or relationship history. Then write the primary message plus a DM-friendly short version and a formal email/management version. Template: [Step 2](references/templates.md#step-2--personalized-outreach). *Media/analyst/hunter targets*: personalize on beat and recent coverage, lead with the story angle (not a compensation offer), carry the embargo terms verbatim from the press-media-relations artifact, and never invent quotes or data — claims come from the approved message house.
3. **Create follow-up sequence** — draft a 4-touch strategy window (Day 0 / 3-4 / 7-8 / 14, then archive at Day 21), each touch adding new evidence-backed or approved value and getting shorter. These ranges are planning guidance only. Always leave future touches unscheduled; when one becomes due, approve/check/dispatch only that touch with one concrete ISO-8601 `dispatch_at` plus timezone if scheduled. Cap at 3-4 follow-ups only while there is no blocking scoped preference or other negative signal, make it easy to say no, and use only the approved eligible channel. A new channel needs its own eligibility evidence and exact approval. A campaign/offer decline terminates that cadence and records the scoped preference inline; persisting it needs separate exact authorization. A later cadence within that scope requires newer reopening evidence. An explicit stop-contact (`user-request`), unsubscribe (`unsubscribe`), verified spam/provider complaint (`complaint`), or consent withdrawal (`withdrawal`) additionally triggers the suppression path above. Template: [Step 3](references/templates.md#step-3--follow-up-sequence).
4. **Provide negotiation support** — map the ask/budget gap, then apply value-exchange, scope-adjustment, or future-value strategies with ready scripts and an objection/response table. Template: [Step 4](references/templates.md#step-4--negotiation-guide).
5. **Track outreach pipeline** — record stage counts and conversion rates, a per-creator detailed pipeline, today's prioritized actions, and pipeline health (response rate, confirmation rate, time-to-confirm, top objection). Record offer declines as terminal for that cadence with a scoped preference. Record explicit stop-contact (`user-request`), unsubscribe (`unsubscribe`), verified channel/provider spam complaint (`complaint`), or consent withdrawal (`withdrawal`) as terminal no-contact states with the suppression event/handoff reference. Never leave a follow-up action on either row. Template: [Step 5](references/templates.md#step-5--outreach-pipeline-tracker). Active-cycle tracking lives here; when a cycle closes (confirmed or archived), offer the closed outcome as a one-line `operation: propose` update for separate exact authorization so [creator-registry](../../../protocol/creator-registry/SKILL.md) can reconcile it.

## Example

**User**: "Write outreach for `creator_ref: creator-042`. I supplied a transient content locator plus `source_ref: [opaque authorized evidence ref]`, `observed_at: [ISO 8601]`, and `observable_detail: [exact visible detail]`; use only the approved campaign, offer, and product wording in `[claims-or-brief-ref]`."

**Output** (abridged):

```markdown
## Outreach for `creator_ref: creator-042`

### Personalization Points
- Content item: `[content title or format supported by content_ref]`
- Observable detail: `[exact visible detail from supplied evidence]`
- Evidence: `source_ref: [opaque authorized evidence ref]`  •  `observed_at: [ISO 8601]`

### Primary Message
Subject: `[evidence-backed content topic]` — collaboration idea from `[Brand]`

`[Recipient name resolved transiently at dispatch]`, your `[content item]` `[observable detail supported by content_ref]`. I'm `[Sender]` from `[Brand]`. `[Approved campaign/product sentence from claims-or-brief-ref]` We're offering `[approved compensation]` for `[approved deliverable]`. Open to hearing more?
```

Full multi-version output, follow-up cadence, negotiation guide, and pipeline tracker live in [references/templates.md](references/templates.md).

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in templates for all five steps, the full worked example, and outreach tips.
- [references/cold-copy-rules.md](references/cold-copy-rules.md) — hard cold-outreach copy rules: first-line bans, per-step sentence caps, soft CTAs, observation framing, no link in step 1.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [runtime-invocation.md](../../../references/runtime-invocation.md) — safe bundle-root resolution and feature-runtime verification before live suppression queries.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipe per connector category.
- STAR benchmark scoring at [references/star-benchmark.md](../../../references/star-benchmark.md) — quality scoring reference for downstream review.
- [expert-panel.md](../../../references/expert-panel.md) — multi-persona review method for pressure-testing outreach copy before sending.
- Sibling skills: [influencer-discovery](../../scout/influencer-discovery/SKILL.md), [fit-scorer](../../scout/fit-scorer/SKILL.md), [brief-generator](../../target/brief-generator/SKILL.md), [contract-helper](../contract-helper/SKILL.md), [creator-content-auditor](../creator-content-auditor/SKILL.md).

## Next Best Skill

- **Primary**: [contract-helper](../contract-helper/SKILL.md) — once a partner is confirmed, turn the agreed commercial terms and rights into the agreement before content production.
- **Alternate**: [creator-content-auditor](../creator-content-auditor/SKILL.md) — only after the agreement/brief exists and the creator has produced draft content, review that content before it ships.
- **Alternate**: [brief-generator](../../target/brief-generator/SKILL.md) — send a full campaign brief to a creator who asked for more detail.

Termination note: keep a visited-set. If a skill in this chain was already invoked this session, stop and report chain-complete rather than re-running it. Max handoff depth is 3.

## Related Skills

- [influencer-discovery](../../scout/influencer-discovery/SKILL.md) - Find influencers to reach out to
- [fit-scorer](../../scout/fit-scorer/SKILL.md) - Prioritize who to contact first
- [brief-generator](../../target/brief-generator/SKILL.md) - Send briefs to confirmed partners
- [contract-helper](../contract-helper/SKILL.md) - Finalize agreements
