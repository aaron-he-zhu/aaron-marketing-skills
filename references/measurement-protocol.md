# Measurement & Attribution Protocol

> The honest answer to "how do we know a change worked?" — and, just as important, to
> "which questions can we answer in minutes, and which take weeks and a control group?"
> Without this discipline, every version is guesswork. This file is the SSOT for what is
> testable, how fast, and what each signal does and does NOT prove.

**Scope**: the layered latency model below (proxy vs outcome) is **SEO/GEO-specific**. The cross-discipline design and decision protocol applies to every discipline. Other disciplines use their own unit, outcome truth set, latency, and guardrails; they do not inherit the crawler/citation layers.

## The problem this exists to fix

SEO/GEO outcomes are **delayed** (a page change surfaces in an AI answer or a ranking only
after the engine re-crawls and re-indexes) and **confounded** (your number also moves because
the engine changed, a competitor changed, or the category shifted). So a raw before/after on
the final outcome is rarely attributable to your edit. The fix is not "measure faster" — some
things genuinely cannot be measured fast — it is to **separate the fast proxy from the slow
outcome, label which is which, and attribute the slow ones against a control.**

## The core distinction: proxy vs outcome, four latency layers

The single most common mistake (we made it ourselves) is collapsing two opposite-latency things
into one claim like "GEO is minute-level testable". It is not. It splits cleanly:

| Layer | What it measures | Latency | Proxy or outcome | How you test it | Tool |
|---|---|---|---|---|---|
| **1. Crawler access** | Can the AI/search bots even fetch and parse the page? | **Instant** | Precondition (neither) | Fetch-as-bot + robots eval + your server logs | `robots.py` (exists), `botlog.py` *(proposed)* |
| **2. Citability** | *Given the page is retrieved*, is it extractable / quotable / answer-shaped? | **Minutes** | **Proxy** for GEO | Hand the URL/content to a live-fetch engine, ask the target question, score the answer | `citations.py probe` *(proposed)* + `ledger.py` |
| **3. Surfacing** | Does an engine cite you for a bare query, *unprompted*? | **Days–weeks** | **Outcome** (GEO) | Ask a fixed query panel WITHOUT giving the URL; record citations over time vs a control | `citations.py surface` *(proposed)* + `ledger.py` |
| **4. Rankings / clicks** | Search position, impressions, CTR | **Weeks–months** | **Outcome** (SEO) | GSC / rank data snapshotted over time vs a control | `gsc.py` *(proposed)* + `ledger.py` |

> **⚠️ The error this table prevents:** never read a missing citation (layer 3) as "my content
> is bad" until layer 1 says the bot actually fetched a 200. "Not crawled yet" and "crawled but
> not chosen" look identical in the answer box and have completely different fixes. Check access
> first.

## Layer 1 — Crawler access (instant, fully in your control)

The cheapest, fastest signal, and a **precondition** for everything below: if the bot can't
fetch or render the page, no amount of content quality matters.

- **Test:** request the page as each relevant bot UA and confirm a `200` with the content present
  in the raw HTML (not JS-injected). Evaluate robots.txt for each UA group. Parse your own access
  logs for actual bot hits per URL.
- **Bots to check** (UA tokens drift — verify current values, do not hard-code blindly): training
  crawlers (GPTBot, ClaudeBot, PerplexityBot), live/user fetchers (ChatGPT-User, Claude-User,
  Perplexity-User), search-index crawlers (OAI-SearchBot, Claude-SearchBot), and Google
  (Googlebot powers AI Overviews; **Google-Extended is an opt-out *token*, not a separate crawler**,
  and does not change crawl timing).
- **What green here proves:** only that you are reachable. It is insurance against wasting two
  weeks discovering ClaudeBot was being 403'd — **not** evidence you will be cited.
- **robots caveat:** the live/user fetchers do not all obey robots.txt — `Perplexity-User`, in
  particular, behaves like a real-time browser and may fetch even when `PerplexityBot` (its
  background indexing crawler) is disallowed. So a robots.txt block reduces *surfacing* (L3, the
  index path) without necessarily stopping an explicit-URL *probe* (L2). Test access per UA, not in
  aggregate.

## Layer 2 — Citability: the fast loop (minutes, but a proxy)

**Why it *can* be fast — and the exception that bites:** when you hand the engine a **specific
URL**, a live-fetch path does a real HTTP GET at query time, so it sees the version you just
deployed and you bypass the crawl/index lag. This holds for **Perplexity-User** and **Claude's
`web_fetch`** (Claude-User UA). It does **not** hold universally: **ChatGPT, even with web access
on, preferentially answers from its own cached index rather than re-fetching**, and Claude's
`web_search` (as opposed to `web_fetch`) reads a search index, not your live page. So the
minutes-fast property belongs to the **explicit-URL live-fetch path**, not to "browsing" in
general — verify per engine, do not assume a universal bypass.

**What it actually measures:** extractability, quotable self-contained chunks, a direct answer
near the top, schema/structure the model can parse — i.e. **exactly what the build-phase GEO work
(`geo-content-optimizer`, schema, Q&A blocks) changes.** This is why iterating on those changes
*can* be fast.

**What it does NOT measure — state this every time:** whether the engine will *retrieve* you
unprompted. It tests "if retrieved, is it good," not "will it be retrieved." It is a **proxy** for
GEO, never the outcome.

**Method (probe):**
1. Define a fixed **prompt panel** of target questions (the queries you want to be cited for).
2. Run each prompt while supplying the URL/content — but **only trust the result as a test of your
   current page if a live fetch actually happened.** Confirm it: your access log should show the
   `Perplexity-User` / `Claude-User` hit during the probe. If no hit appears (ChatGPT cache,
   Claude `web_search`, any index path), you scored a *cached* copy — label it as such, do not call
   it a fresh-content test.
3. Score each answer: was the page cited? was a claim quoted verbatim? was the answer correct and
   attributable to your content? (binary per dimension is fine).
4. Because model output is **stochastic, sample** — run each prompt N times and record the **rate**,
   not a single yes/no. Snapshot the rates to `ledger.py` so successive content edits show a delta.

**Honest friction:** there is no clean, free API that reports "who did ChatGPT cite." Use the
Perplexity API where it exists; otherwise this layer is **semi-manual** (run the panel through each
engine's own interface/API). `ledger.py` structures the results; it does not automate the asking.

## Layer 3 — Surfacing: the slow loop (days–weeks, the real GEO outcome)

The thing users actually want — "does ChatGPT/AIO/Perplexity recommend me when someone asks" — is
**gated by each engine's own crawl + index refresh, which you cannot force.** There is no
"recrawl now" button for the AI-specific bots. Google's Search Console URL Inspection → Request
Indexing nudges *Google's* index only (rate-limited, no guarantee), and AI Overview inclusion is
decided separately on top of that. So surfacing is **as slow and confounded as SEO ranking.**

**Method (surface):**
1. Ask the fixed query panel **without supplying the URL**.
2. Record, per engine, whether your domain is cited / linked / named, and in what position.
3. Snapshot to `ledger.py` on a schedule (e.g. weekly).

**Attribution requires a control — this is non-negotiable for layers 3–4.** Your citation rate
moves for reasons that are not your edit (the engine retrained, a competitor published, the SERP
feature changed). So measure a **holdout in parallel**: an unchanged page of yours, a sibling URL,
or a competitor, run through the same panel. **Report delta-vs-control, not raw delta.** A raw
"+15% citations" means nothing if the whole category rose 15%.

**Horizon:** fix the measurement window *before* you start (e.g. 2–6 weeks) and do not react to
day-to-day noise inside it. Reading surfacing daily is reading noise.

## Layer 4 — SEO outcomes (weeks–months, same discipline)

Impressions / position / clicks via GSC (`gsc.py`, proposed) snapshotted to `ledger.py`, read
against a control and a horizon, accounting for seasonality. Mechanically identical to layer 3 —
just a different data source and a longer window.

## The loop (applies to layers 2–4)

1. **Baseline** — `ledger.py record` the relevant signal *before* the change.
2. **One attributable change** — make a single change, or a clearly labeled batch. Two changes at
   once destroy attribution.
3. **Wait the layer's latency** — minutes (L2), the fixed horizon (L3/L4). Re-snapshot.
4. **`ledger.py diff` / `trend` against the control**, not against zero.
5. **Label every number** — `Measured` / `Estimated` / `Proxy-for-<outcome>`. Never render a
   layer-2 proxy as if it were a layer-3 outcome. (This is the same labeling rule the skills already
   carry, applied to time-series.)

## What this protocol does NOT give you (read before trusting a number)

- **No certainty.** A proxy (L2) can improve while the outcome (L3) does not, and vice-versa.
  Citability is necessary, not sufficient, for surfacing.
- **No fast surfacing.** Layers 3–4 stay slow. Any claim of a minute-level "will I be cited /
  ranked" loop is false — we made that claim once and it was wrong.
- **No attribution without a control.** A raw before/after on a confounded outcome is a story,
  not evidence.
- **Single runs are noise.** L2 is stochastic; sample and report rates.
- **Collection is semi-manual.** The tools structure and diff the data; they do not, for the AI
  engines, automate the asking.

## Cross-Discipline Decision Protocol

Every monitored change is judged on a fixed schedule against a defensible counterfactual, then promoted, kept testing, rolled back, or marked unproven by the named decision owner. Statistical software supplies evidence; it does not own the business verdict.

### Register Before Exposure

Record the unit of randomization/analysis, population and exclusions, control and candidate, primary metric, guardrails, metric direction, outcome truth source, attribution rule, conversion lag, hypothesis, minimum practically important effect, alpha/confidence, power/precision target, sample plan, multiplicity or sequential-testing correction, start/stop/read dates, and decision owner. A plan written after looking at outcomes is exploratory, not confirmatory.

**Readback windows** (set before the change; do not react inside the window):

| Change type | Readbacks |
|---|---|
| Content refresh (existing page) | 7 / 14 / 28 / 56 days |
| New content / new asset | 14 / 28 / 56 / 90 days |
| Technical fix | daily ×7, then 28 |
| AEO/GEO surfacing | weekly |
| Influencer activation | per post + 7 / 30 days |
| Paid campaign change | exit learning phase first, then 7 / 14 days |

**Required readback fields**: experiment/change ID · preregistration version · owner · target/population · control and candidate windows · sample/exclusions · sources and provenance · primary metric and guardrails · attribution/lag · effect and uncertainty · statistical method · data-quality incidents · decision · rationale · next patch · next readback date.

### Typed Measurement Contract and Cycle Retro

When a workflow needs a machine-verifiable cross-discipline loop, encode the preregistration as `kind: measurement-contract` under [`control-artifact.schema.json`](control-artifact.schema.json). Bind the exact measured target, candidate, and control bytes; population/scope; analysis unit; primary metric and guardrails; truth source; attribution and conversion-lag references; locked/start/stop/read times; decision rule; and decision owner. `locked_at` must be no later than exposure, and confirmatory designs require a control. `none-exploratory` is explicitly exploratory and cannot be reported as confirmatory evidence.

Close a readback with `kind: cycle-retro`. It binds the exact measurement-contract digest, the contract's exact target as the non-forked current head, selected ancestry, evidence bindings, decision owner, decision time, coded limitations, and any next read. A new hypothesis may be carried forward only with `hypothesis_evidence_weight: 0`; it is a proposed next test, never evidence for the completed cycle.

The protocol deliberately does not define a universal decision enum. Each discipline supplies a safe `decision_code` and an immutable `decision_taxonomy_ref`: for example Social, Narrative, Launch, Email, Paid, and Influencer may use different domain decisions without changing the shared schema. The validator checks identity, digest, owner, current-head, and time relationships; the discipline checks whether the code is allowed and what action it implies.

An action receipt may be cited as readback evidence only when its exact digest and scope match the registered unit/window. A successful receipt proves that a separate executor reported the bounded operation; it does not prove business impact, transfer permission, or replace the declared outcome truth source.

### Method-Appropriate Evidence

- **Binary rates**: use a prespecified two-proportion method, effect estimate/interval, and practical-effect bar. `experiment.py proportion` returns a two-sided pooled z-test, per-arm Wilson intervals, an absolute-lift interval, and separate statistical/practical flags.
- **Continuous/skewed metrics**: report sample sizes, robust summaries, a rank test where its assumptions match the estimand, and a bootstrap effect interval. A Mann-Whitney test is not a test of mean difference and must not be described as one.
- **Time series or non-randomized changes**: use a defensible matched control, interrupted-series, difference-in-differences, or other stated design. A generic A/B p-value does not repair confounding.
- **Small or dependent samples**: remain exploratory unless the chosen exact, clustered, paired, or hierarchical method supports the design.

`alpha=0.05`, `power=0.80`, and a 15% relative practical-lift reference are defaults only when no better domain-specific policy exists. They are not universal truths. Declare any default before exposure and report sensitivity. For a zero control rate, relative lift is undefined; use a preregistered absolute effect.

Use [`scripts/connectors/experiment.py`](../scripts/connectors/experiment.py) for stdlib deterministic calculations. Inputs are user-provided observations; p-values, intervals, power, and effect estimates are **Calculated**. The helper deliberately emits no `promote`, `rollback`, or winner verdict.

### Decision Ownership

**Promote** only when the precommitted primary evidence and practical-effect bar are met, guardrails are acceptable, attribution/data quality is intact, and the decision owner accepts the operational tradeoff. **Keep testing** only under a registered continuation/sequential rule. **Rollback** may be immediate for a safety, legal, reliability, or material business guardrail even before efficacy is resolved. Otherwise record **Unproven**; absence of significance is not proof of equivalence.

Do not promote when sample/precision is inadequate, attribution is dirty, exclusions changed post hoc, seasonality or interference explains the move, collection failed mid-window, repeated peeking/multiplicity is unhandled, or only a proxy improved while the declared outcome did not.

## Per-discipline latency notes

- **SEO/GEO** — the four-layer model above (crawler access → citability → surfacing → rankings). Proxy (L2) is minutes; outcomes (L3/L4) are weeks. Always read against a control.
- **Influencer** — content has a short head (first 24–48h decides most reach) then a long tail; judge a post on its own platform analytics vs the creator's recent median, not vs another creator. Return rolls up into the SQS per the [STAR framework](star-benchmark.md).
- **Paid ads** — auction feedback is near-instant, so the latency problem inverts vs GEO: the slow parts are **conversion lag** (a click today converts days later) and **attribution windows** (Meta 7-day-click vs Google last-click are not comparable — normalize before diffing), plus **learning-phase noise** (editing a campaign still in learning resets it; do not read or change it until it exits). Never compare cross-platform ROAS without normalizing window + currency. Scores roll up per the ROAS framework (`references/roas-benchmark.md`, added in the Paid Ads wave).

## Frequency ceiling by objective

Read against the **early-flight baseline**, not a raw last-day dip (per the paid latency note above). Frequency is impressions ÷ reach over a stated window — a 7-day rolling window unless the export says otherwise. The bands below are **Estimated** starting points, not measured thresholds: they say *where to start looking for decay*, not a hard cutoff. Confirm the actual breach by reading the CTR/CVR slope, and let the observed decay — not the number alone — call fatigue vs saturation. There is no universal "frequency 3" rule.

| Objective | Frequency ceiling (7-day) | Read | Confidence |
|---|---|---|---|
| **Prospecting / cold** (Awareness, top-funnel) | ~1.5–2.5 | Cold audiences fatigue fast; CTR decay past this band usually reads as creative fatigue while reach is still growing | Estimated |
| **Warm retargeting** (site visitors, cart, engagers) | ~4–7 | A warm, invested pool tolerates more exposures before CTR/CVR fall; a plateau in reach *with* a rising frequency reads as saturation, not fatigue | Estimated |
| **Retention / existing customers** (short-window winback) | ~6–10 | The most tolerant band, but the pool is smallest, so saturation arrives on a shorter calendar even if the per-user ceiling is high | Estimated |

Notes on reading the band:
- **Prospecting < warm < retention** is the ordering that holds; the exact numbers are platform- and vertical-dependent, so treat them as Estimated and state the ceiling you used.
- A number inside the band with **falling CTR** still signals fatigue — the ceiling is a prompt to check the slope, not a pass.
- A number above the band with **flat CTR/CVR** is not yet a problem; do not rotate on the frequency figure alone.
- Longer windows (28-day) inflate frequency mechanically; do not compare a 28-day frequency against a 7-day band.

## Tooling map

| Tool | Status | Layer(s) | Role |
|---|---|---|---|
| `scripts/connectors/ledger.py` | **exists** | 2–4 | snapshot / diff / trend spine; per-target time series with collision guard |
| `scripts/connectors/experiment.py` | **exists** | cross-discipline | statistical/effect-size decision inputs on user-provided observations; no business verdict |
| `scripts/rubric-score.py` | **exists** | framework audits | deterministic advisory rubric scoring, coverage, confidence, veto, and verdict semantics |
| `scripts/golden-auditor-math.py` | **exists** | — | guards the *internal* consistency of the scoring math (not external validity) |
| `scripts/connectors/robots.py` | **exists** | 1 | robots.txt + AI-bot access check |
| `scripts/connectors/botlog.py` | *proposed* | 1 | parse server logs → per-URL AI-bot hit counts |
| `scripts/connectors/citations.py` | *proposed* | 2, 3 | `probe` (fast citability) + `surface` (slow unprompted-citation) modes, both → ledger |
| `scripts/connectors/gsc.py` | *proposed* | 4 | Google Search Console impressions/position/clicks |

## Relationship to the Eight Frameworks

CORE-EEAT, CITE, STAR, ROAS, SEND, RAMP, ECHO, and TALE scores are advisory quality-control summaries. Deterministic math guards internal consistency; it does not establish reliability or external validity. Outcome calibration must follow the preregistered, version-locked study in [`scoring-semantics.md`](scoring-semantics.md). Until that study succeeds for a named profile/population/outcome, present scores as structured audit evidence, not outcome predictors.

See also: [CONNECTORS.md](../CONNECTORS.md) (the data recipes and the measurement-loop note),
[scripts/connectors/README.md](../scripts/connectors/README.md) (helper reference),
[state-model.md](state-model.md) (where snapshots live in `memory/`).
