# Creator Dossier — Method (Keyless, Tier 1)

A repeatable way to turn one creator's public profile or homepage into a
structured dossier you can hand to `fit-scorer` or `outreach-manager`. Uses only
public pages, the creator's own posts, and inputs the user shares. No paid tools,
no API keys, no scraping that needs login. Where a `~~` connector would sharpen a
field, note it — but every field has a public-only fallback.

## 1. When to build one

Build a dossier when discovery has surfaced a candidate worth a real read: a
top-tier handle, a competitor partner you want to understand, or any creator the
user names directly. Skip it for bulk pool screening (that is step 3 of the main
skill). One dossier = one creator.

## 2. Inputs you need

- A handle or a profile/homepage URL on at least one platform.
- The brand or niche context (so niche-fit and brand-safety reads have a target).
- Optional: any other handles the user already knows for this creator.

If you only have a name, search the name plus the niche on the open web to find
the primary profile before starting.

## 3. The dossier fields

Fill each field from public data. Mark anything you could not confirm as
`unconfirmed` rather than guessing — an honest gap is more useful than a fake fact.

| Field | What goes here | Public source |
|-------|----------------|---------------|
| **Handle** | Canonical @handle on the primary platform | Profile URL |
| **Real name** | If publicly stated | Bio, about page, link-in-bio |
| **Platforms** | Every platform + handle they link to | Bio links, link-in-bio page, cross-posts |
| **Primary platform** | Where most output/audience sits | Compare post cadence and visible counts |
| **Niche** | One-line category, plus 2-3 recurring topics | Last 10-15 public posts |
| **Audience signal** | Follower band, visible engagement read, who shows up in comments | Public counts; sample 5+ recent posts for likes/comments-to-follower feel |
| **Recent outliers** | 1-3 posts that clearly out-performed their baseline, with what made them land | Scan recent grid/feed for spikes vs. the creator's own norm |
| **Posting rhythm** | Rough cadence (e.g. 3-4/week) and last-active date | Timestamps on recent posts |
| **Brand-safety flags** | Controversy, off-brand content, undisclosed ads, conflicting partnerships | Read recent posts + pinned content; note tone and any flags |
| **Past/competitor partners** | Brands they have posted for, especially competitors | `#ad`/`#sponsored` posts, tagged brands, paid-partnership labels |
| **Contact path** | Best way to reach them (see §5 waterfall) | Bio, about, business links |
| **Confidence** | High / Medium / Low on the dossier overall | Your own read of source quality |

## 4. How to read each field well

- **Audience signal, not vanity count.** A follower number alone says little.
  Sample several recent posts and judge whether comments look like real people
  talking versus emoji spam or pods. Note the pattern in plain words.
- **Outliers tell you what works.** A post that beat the creator's own baseline
  shows the format and topic their audience rewards — useful for briefs later.
  Compare a post to *that creator's* norm, never to other creators.
- **Brand-safety is a read, not a verdict.** Record what you saw (e.g. "two
  recent posts with strong political stance") and let `fit-scorer` weigh it.
- **Partners reveal positioning.** Repeated competitor posts can mean exclusivity
  or simple availability — flag it, hand the detail to `competitor-tracker`.

For platform-specific reading cues (what counts as a healthy engagement read on
X vs. TikTok vs. YouTube, where partnership labels show up), see
[platform-vetting.md](platform-vetting.md).

## 5. Contact-discovery waterfall

Work down this list and stop at the first method that yields a usable path.
Record which step succeeded so outreach knows how warm the channel is.

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
known partner before you reach out; without it, the user dedupes by hand.

## 6. Output and handoff

Save the dossier alongside the discovery file for the same topic. In the
handoff to `fit-scorer`, carry the handle, niche, audience signal, brand-safety
flags, and contact-path step so scoring and outreach start with the full read.
