# Cold Outreach Copy Rules

Hard rules for cold creator outreach (first-touch DM or email to someone who has never heard from you). Apply to every message in every follow-up sequence. These are stricter than the warm-pitch templates in `SKILL.md` — use them when the relationship is cold and deliverability matters.

---

## First-Line Bans

Never open the first message with any of these — they read as a template and get skipped:

- "I" — e.g., "I came across your profile..."
- "We" — e.g., "We help creators like you..."
- "Our team" / "Our brand" as the first words
- "I wanted to" / "I'm reaching out because..."
- "Hope this finds you well" or any version of it
- "My name is..." — save for a later step if needed, never step 1

Always open with one of these instead:

- The creator's name plus a cited thing they made — "[Name], your [specific asset from source_ref]..."
- A specific sourced observation — "Your [three cited reels] use an educational step-by-step format..."
- A source-dated niche development — "[Cited niche development] may make [campaign angle] timely..."

The first line earns the second. If it does not make the creator think "this is about me," the message is dead.

## Evidence-Backed Personalization

Every factual personalization point must carry both:

- `source_ref` — a resolvable opaque reference to an authorized artifact, analytics export, or other checkable source. A raw post/profile URL or handle may be used transiently but never becomes the persisted ref.
- `observed_at` — the date or ISO 8601 time the source was observed.

Use only what the source actually supports. A content pattern is an inference unless multiple cited examples establish it; a creator's value or audience attribute needs an explicit statement or measured source. If either evidence field is missing, omit the fact, generalize the opener, or keep a bracketed placeholder in a `DRAFT — NOT SENT` message. Do not substitute generic praise or assumptions such as "perfect fit," "authentic style," "impressed by your content," "this will resonate," or "your inbox must be busy."

Never invent first-person history for the sender. Do not claim to have watched for months, bought an item, added a product to a cart, used a product, met the creator, or followed their work unless the user supplies that fact and its evidence.

---

## Per-Step Sentence Caps

| Step | Max sentences | What it does |
|------|--------------|--------------|
| Step 1 (first touch) | 3 sentences | Personal opener, the offer, one soft CTA. Nothing else. |
| Steps 2-3 (follow-up) | 3-5 sentences | Add a new angle or a new piece of value, never a repeat. |
| Bump (short nudge) | 1-2 sentences | "Still a fit?" style. Short. |
| Breakup (final) | 2-3 sentences | Leave value, keep the door open. |

If a step runs longer than its cap, cut it.

---

## Verifiable Observation, Not Invented Experience

Ground the opener in something visible in the cited source, not an invented reaction or an unsupported marketing claim.

- Good (verifiable observation): "Your 12 August routine reel demonstrates all three steps in one take." (`source_ref: [post-id]`, `observed_at: [date]`)
- Bad (invented experience): "I watched your reel and immediately bought everything you used."
- Bad (unsupported result): "Most creators see saves spike with this format."

Measured statistics may be used only when their source and observation window are supplied and the wording preserves their limits. Do not disguise an estimate as an observation.

Never fabricate: client names, follower or sales numbers, past-campaign results, or content references unless they are real and verifiable. If you cannot verify it, generalize it.

---

## Soft CTA List

Use a low-commitment ask in step 1. Preferred soft CTAs:

- "Worth a look?"
- "Want the full brief?"
- "Open to hearing more?"
- "Is this the kind of thing you take on?"
- "Happy to send details — useful?"

Avoid hard asks in step 1 — they presume interest from a stranger:

- "Book a call with me"
- "Are you free Thursday?"
- "Let's hop on a call"

Use a hard ask only at step 3+ after the creator has replied or signaled interest, and even then soften it.

---

## No Link in Step 1

- Step 1: no links at all. Links in a first cold message hurt deliverability and read as spray-and-pray.
- Steps 2-3: at most one link, only if it adds real value (a brief, a lookbook, a past-collab example).
- Breakup: one real, genuinely useful link is fine.
- Never link to a form or landing page in steps 1-2.
- Never invent a URL. Every link must point to a real, checked page before sending.

## Send and Stop Gate

These copy rules do not authorize delivery. Before sending or scheduling, require the exact recipient, channel, and final message for the single currently due touch; when scheduling that one touch, also require one concrete ISO-8601 `dispatch_at` and timezone. Draft windows are not exact approval, and every later touch remains `DRAFT — NOT SCHEDULED` until it separately becomes due. Record jurisdiction, channel, lawful-basis evidence, and contact eligibility. The host must supply the verified absolute user-project root; never infer it from the bundle, current directory, event data, or outreach copy. Inside every actual delivery job, resolve `AARON_SKILLS_ROOT` from `CLAUDE_PLUGIN_ROOT` or the Git top level, verify the plugin/runtime, `registry-event.schema.json`, system/catalog profile files, and project root as specified in [runtime-invocation.md](../../../../references/runtime-invocation.md), then run live consent-registry `is-suppressed` for the pseudonymous subject immediately before the provider call. Suppressed, Unknown, inaccessible, or errored state fails closed. A `not suppressed` result is not proof of lawful basis.

Never approve or schedule the whole cadence, regardless of provider features. Approve/check/dispatch only one currently due touch; after it completes, leave every later touch as an unscheduled draft. Before saving any outreach artifact or handoff, reuse an explicitly carried opaque `creator_ref` or verified creator-registry aggregate ID; otherwise generate one random `creator-<UUIDv4>` once for the lineage. Never derive it from a raw locator or deterministic hash. Replace raw handles, names, profile/content URLs, recipient identities, and direct contact data with resolvable opaque `handle_ref` / `recipient_ref` / `contact_source_ref` / `source_ref` values or dispatch-time placeholders. When no authorized artifact or verified registry link resolves them, mark identity unresolved, save no hidden mapping, and require the transient locator again at dispatch.

Any offer decline ends that cadence immediately: void every remaining draft touch, do not relabel the offer or switch channels, and record only the exact campaign/offer/category scope, date, and opaque evidence ref inline. Persisting that preference needs separate exact authorization, and a later cadence inside its scope requires newer cited reopening evidence; unknown scope fails closed without an invented cooldown. Do not invoke global suppression for the decline or a commercial objection alone. Saying "I don't do sponsored content" is not automatically a global unsubscribe. Invoke the consent-registry direct suppression path (or its exact `immediate-suppress-handoff` when the verified runtime is unavailable) only with the exact typed mapping: explicit stop-contact → `user-request`; unsubscribe → `unsubscribe`; verified channel/provider spam complaint → `complaint`; consent withdrawal → `withdrawal`.

---

## Tone

Peer-to-peer, not brand-to-creator. Curious, not desperate. Specific, not generic. Short, not comprehensive. If a message sounds like marketing copy, rewrite it until it reads like a note from a knowledgeable peer.
