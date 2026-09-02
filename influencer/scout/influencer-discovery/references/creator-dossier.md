# Creator Dossier — Method (Keyless, Tier 1)

A repeatable way to turn one creator's public profile or homepage into a
structured dossier you can hand to `fit-scorer`; it is not outreach-ready. Uses only
public pages, the creator's own posts, and inputs the user shares. No paid tools,
no API keys, no scraping that needs login. Where a `~~` connector would sharpen a
field, note it — but every field has a public-only fallback. The durable dossier
uses pseudonymous and opaque references; it is not a contact database.

## 1. When to build one

Build a dossier when discovery has surfaced a candidate worth a real read: a
priority `creator_ref`, a competitor partner you want to understand, or any creator the
user names directly. Skip it for bulk pool screening (that is step 3 of the main
skill). One dossier = one creator.

## 2. Inputs you need

- A stable opaque `creator_ref`, plus a handle or profile/homepage URL available
  transiently on at least one platform.
- The brand or niche context (so niche-fit and brand-safety reads have a target).
- Optional: any other handles the user already knows for this creator.

If you only have a name, search the name plus the niche on the open web to find
the primary profile before starting. Treat that name as transient lookup input;
convert the result to `creator_ref` plus verified handle/profile references
before saving or handing off.

Resolve identity in this order:

1. Reuse an explicitly carried opaque `creator_ref` from the current authorized
   discovery lineage, or a creator-registry aggregate ID only when its handle
   link is verified.
2. Otherwise generate `creator-<UUIDv4>` once and reuse it unchanged in the
   dossier, saved artifact, and every handoff derived from it.
3. Keep raw handles, names, profile URLs, emails, and provider IDs out of
   `creator_ref`. Do not hash any of those values to make an ID; low-entropy
   identity data remains guessable after hashing. Provider-specific identity
   evidence belongs in separate opaque handle/profile and `source_ref` fields.

An opaque `creator_ref` resolves only through the accompanying authorized
artifact's verified handle/profile evidence or an accepted creator-registry
identity link. If neither is available downstream, mark identity unresolved and
request the transient locator again; never reverse-derive or guess it.

## 3. The dossier fields

Fill each field from public data. Mark anything you could not confirm as
`unconfirmed` rather than guessing — an honest gap is more useful than a fake
fact. Each factual field also records `provider/tool`, `source_ref`,
`observed_at`, its window, and one evidence label (`Measured`, `Calculated`,
`Estimated`, `User-provided`, or `Proxy`).

| Field | What goes here | Provider/tool + source_ref | observed_at / window | Evidence label / freshness |
|-------|----------------|----------------------------|----------------------|----------------------------|
| **Creator ref** | Stable opaque `creator-<UUIDv4>` or verified registry aggregate ID; never a raw handle | upstream artifact/registry + opaque ref | date / N/A | User-provided or Measured / current-stale-unknown |
| **Verified handle refs** | Primary and linked-platform opaque refs; identity status | public page/provider + ref | date / N/A | label / current-stale-unknown |
| **Primary platform** | Where most output/audience sits | public page/provider + ref | date / declared window | label / current-stale-unknown |
| **Decision geography** | Country/region only when required by the campaign filter | public page/provider + ref | date / declared window | label / current-stale-unknown |
| **Niche** | One-line category, plus 2-3 recurring topics | recent-post sample + ref | date / sample window | label / current-stale-unknown |
| **Audience signal** | Follower band, visible engagement read, who shows up in comments | public counts/provider + ref | date / sample window | label / current-stale-unknown |
| **Recent outliers** | 1-3 posts that out-performed the creator's baseline | post refs | date / comparison window | label / current-stale-unknown |
| **Posting rhythm** | Rough cadence and last-active date | post refs | date / sample window | label / current-stale-unknown |
| **Brand-safety flags** | Observed controversy, off-brand content, disclosure or partnership signals | post refs | date / sample window | label / current-stale-unknown |
| **Past/competitor partners** | Observed partner refs, never inferred exclusivity | post/provider refs | date / observation window | label / current-stale-unknown |
| **Contact-path refs** | `recipient_ref`, `contact_source_ref`, `agency_ref`, eligible channel or Unknown | opaque refs only | date / N/A | label / current-stale-unknown |
| **Confidence** | High / Medium / Low on the dossier overall | evidence-row refs | date / current STAR window | Calculated / current-stale-unknown |

When providers disagree, keep parallel rows with their own evidence rather than
averaging or selecting by recency alone. Similar names or handles do not prove
identity; merge them only after a verified cross-link or explicit user
confirmation. Apply the current campaign's STAR `evidence_window` to volatile
fields: outside is `stale`; a missing date/window or missing STAR window is
`unknown`; both become `refresh_required` and remain Unknown for Fit until
refreshed. Never invent a global TTL.

## 4. How to read each field well

- **Audience signal, not vanity count.** A follower number alone says little.
  Sample several recent posts and judge whether comments look like real people
  talking versus emoji spam or pods. Note the pattern in plain words.
- **Outliers tell you what works.** A post that beat the creator's own baseline
  shows the format and topic their audience rewards — useful for briefs later.
  Compare a post to *that creator's* norm, never to other creators.
- **Brand-safety is evidence, not a verdict.** Record only the dated observation.
  Audience/authenticity facts may feed `fit-scorer`'s typed S1–S10 read and
  potential S2/S6 control evidence. Brand-safety/content-integrity observations
  are candidate `STAR-T3` evidence. `creator-content-auditor` alone applies the
  S2/S6/T3 gates, caps, and final verdict; neither discovery nor fit-scorer does.
- **Partners reveal positioning.** Repeated competitor posts can mean exclusivity
  or simple availability — flag it, hand the detail to `competitor-tracker`.

For platform-specific reading cues (what counts as a healthy engagement read on
X vs. TikTok vs. YouTube, where partnership labels show up), see
[platform-vetting.md](platform-vetting.md).

## 5. Contact-discovery waterfall

Work down this list and stop at the first method that yields a usable path.
Resolve a raw contact coordinate only transiently. Record which step succeeded
as `recipient_ref`, `contact_source_ref`, `agency_ref`, eligible channel, and
observation date so outreach knows how warm the channel is without copying the
address or a person's name.

1. **Public business email** in the bio, about page, or "contact" link.
2. **Link-in-bio / homepage** — many creators list a booking or business form there.
3. **Management or agency** named in the bio (e.g. "repped by …") — find the
   agency's public roster contact instead of the creator directly.
4. **Press/partnerships page** on a personal site, if they run one.
5. **Platform DM or business-inquiry button** as a documented fallback — note it
   is lower-signal and slower.
6. **No public path found** — record `unconfirmed` and flag that outreach must
   source a path another way. Do not guess an email address.

A `~~CRM` connector can check whether any of these contacts already exist as a
known partner before you reach out; without it, the user reviews possible
matches by hand. Neither path may merge identities without the verified
cross-link rule above.

## 6. Output and handoff

Return the dossier inline. Offer an exact WARM path alongside the discovery file
for the same topic and save only after authorization. In the handoff to
`fit-scorer`, carry `creator_ref`, verified handle refs, niche, audience signal,
brand-safety flags, field-level evidence, the current STAR `evidence_window`,
`freshness_status`, `refresh_required`, and pseudonymous contact-path refs so
Fit starts with the full read. Route selected Fit results to campaign planning;
outreach becomes eligible only after an approved plan and documented
contact/consent/channel readiness. The dossier never authorizes a send. Never include a raw name, email,
phone, postal address, named manager, credential, or geography more granular
than the declared campaign decision requires.
