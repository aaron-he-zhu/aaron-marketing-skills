# Medium and GitHub as AI-Citation Surfaces

Two high-authority third-party surfaces that LLMs cite often. These are not standalone skills — they are extra real estate for content the canonical site already owns. Use them to widen citation coverage, then point them back to the original. Everything here is manual / keyless: you work with the user's own accounts and public pages.

## Why these two get cited

| Surface | Why LLMs pull from it | What to publish there |
|---------|----------------------|-----------------------|
| Medium | High domain authority; indexes fast (articles can surface in days, not months); frequently appears in AI answers | Republished articles, explainers, opinion pieces |
| GitHub | High DA + crawled constantly; very high AI-citation rate for technical / how-to / "list of" queries | READMEs, GitHub Pages docs, gists, Awesome-style lists |

Note: "ranks in days" and "cited often" are patterns reported by the source skill, not guaranteed outcomes. Treat them as plausible, not promised.

## Medium: canonical setup (do this first)

Republishing the same article on Medium and the user's own domain creates duplicate content. The fix is the canonical tag, which tells search engines the user's site is the original.

- In Medium's story settings, set the canonical link to the original URL on the user's site.
- Publish on the user's own domain **first**, let it get indexed, then republish on Medium with the canonical pointing home.
- This protects the user's own page from being outranked by its own Medium copy and credits the site as source.
- Medium's canonical only affects search engines. It does not stop an LLM from quoting the Medium copy — which is fine, because the article still links back to the site.

## Medium: content and links

| Element | Guidance |
|---------|----------|
| Title | Keyword-led, matches the search/question intent of the topic |
| Body quality | Same bar as the user's own site — no thin reposts |
| Internal links | Link to 1–2 relevant pages on the user's site, in-context |
| CTA | One clear path back to the site; do not over-promote |

## GitHub surfaces: profile vs repository

These behave differently. Do not optimize them the same way.

| Surface | What it is | Optimize for |
|---------|-----------|--------------|
| Profile README | A repo named `username/username`; its root `README.md` renders on the profile page | Identity + navigation, ~15–40 rendered lines |
| Pinned | Up to 6 repos/gists shown on the profile | Flagship projects that match the canonical-entity story |
| Repo README | Root `README.md` on a project's Code tab | Product landing: what it does, install, proof, CTA |
| GitHub Pages | Static site at `username.github.io` (user site) or `username.github.io/repo/` (project site) | Long-form docs, FAQ, changelog — more indexable pages |
| Gists | Small snippets / micro-content | Long-tail topics; link back to the main repo or site |

A normal repo's README does not change the profile banner — only the `username/username` repo does.

## What gets a GitHub repo surfaced

Rough ranking weight reported by the source: repo name and About description carry the most, Topics high, README high.

- **Repo name** — descriptive and keyword-bearing, hyphen-separated (`markdown-editor`, not `my-project`).
- **About description** — 350-char hard limit; aim ~128 chars. Lead with the primary keyword, say what it does and who it's for. Keep it consistent with the README's first paragraph.
- **Topics** — 6–20 (6–10 is plenty), lowercase with hyphens. Mix technology, purpose, and category tags. Underused, so a cheap discovery win.
- **Website field** (repo Settings / About) — point it at the one canonical site or docs URL that the README's main CTA also uses.

## README for AI citation

| Practice | Why it helps extraction |
|----------|------------------------|
| Answer-first | Direct answer in the first 1–2 sentences (~40–60 words) so an LLM can quote it cleanly |
| Short paragraphs | 2–3 sentences max; easier to lift verbatim |
| Question-style H2/H3 | On project repos, phrase headings as the questions users ask |
| Include data | Numbers and concrete specifics; the source reports cited content skews data-heavy |
| Freshness | Keep it updated; the source reports much cited content was edited recently. Add a "last updated" line |

Profile README is the exception: compress to one punchy tagline under the H1, a few `###` blocks (What I do · Open source · Find me), and a single deduplicated link cluster. Do not paste a full product README there.

## Pointing surfaces back to canonical

The whole point is to funnel authority and clicks home, and to keep entity signals aligned.

- Lead the profile README's opening line with the canonical site URL; mirror it in Pinned and the About field.
- Each Medium republish carries its canonical tag plus in-body links to the site.
- Repo About + Website field + README CTA should all point at the same canonical URL — one destination, repeated consistently, not three competing ones.

## Common mistakes

- Republishing on Medium with **no canonical** → the user's own page competes with itself.
- Treating the profile README like a product README (install steps, screenshots, Contributing) → use the short profile pattern instead.
- Link sprawl: the same site/social/email repeated in badges, tables, and prose → consolidate to one line.
- Generic repo names and empty Topics → kills discoverability and topic-page matches.
- Stale repos → inactivity reads as low credibility and weakens freshness signals.

## Related

- `../../../protocol/entity-optimizer/SKILL.md` — keep site ↔ Medium ↔ GitHub entity identity consistent
- `../../../monitor/domain-authority-auditor/SKILL.md` — citation-trust gate (CITE)
- `../SKILL.md` — geo-content-optimizer (the parent skill)
