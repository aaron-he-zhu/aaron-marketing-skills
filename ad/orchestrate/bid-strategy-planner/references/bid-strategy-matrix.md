# Bid Strategy Matrix

Decision matrix and formulas for the [bid-strategy-planner](../SKILL.md) skill: pick a strategy from goal + data-volume + funnel-stage, derive the starting target, group the portfolio, and plan the learning-phase entry. Sets the ROAS **S (Spend-efficiency)** bidding lever — see [roas-benchmark.md](../../../../references/roas-benchmark.md).

All numeric thresholds below are **Estimated** rules of thumb, not platform guarantees. Read the account's own history first; the account's real numbers override any figure here.

## 1. Strategy-selection matrix

Read left to right: the first row whose goal + volume + funnel-stage all match wins. "Volume" = conversions in the trailing 30 days for the campaign or its bid portfolio.

| Goal | Funnel stage | Data volume (trailing 30d) | → Bid strategy | Why |
|------|-------------|-----------------------------|----------------|-----|
| Revenue / ROAS target | Mid–bottom (DR) | Adequate value signal (see §1a) | **tROAS** | Optimizes to revenue, not just count |
| Fixed-CPA / lead target | Mid–bottom (DR) | Adequate conversion volume | **tCPA** | Holds a cost-per-action ceiling |
| Grow conversion count | Any DR | Thin / below tCPA threshold | **max-conversions** (no target) | Learns volume first; add a target later |
| Grow revenue, value known | Any DR | Thin count but value data present | **max-conv-value** (no target) | Value-learning entry before tROAS |
| Prospecting / awareness | Top | Little-to-no conversion signal | **max-conversions** or **manual CPC** | Bid to reach/clicks, not to a conversion target the funnel can't feed |
| Any | Any | Sparse data **or** tight manual constraint (e.g. hard bid cap, brand terms) | **manual CPC** (or enhanced CPC) | Human control when automation can't learn |

### 1a. Volume thresholds (Estimated rule of thumb)

The load-bearing rule: **an automated target strategy needs roughly 30+ conversions per 30 days per campaign (or bid portfolio) before you set a target.** All figures Estimated:

| Trailing-30d conversions | Fit |
|--------------------------|-----|
| **< 15 / mo** | Too thin for any target — start **max-conversions** (no target) or **manual CPC** |
| **15–30 / mo** | Borderline — **max-conversions** now; revisit for tCPA once it clears ~30 |
| **≥ 30 / mo** | Adequate — **tCPA** eligible |
| **≥ 30 / mo with value data** | **tROAS** eligible (revenue goal) |
| **≥ 50 / mo** | Comfortable headroom for a target strategy to learn without stalling |

If the account gives you a real conversions/mo figure, use it and label it Measured; if you are applying the threshold to a guessed count, label the count Estimated and say so.

## 2. Target-derivation formulas

Set the target off the achievable number, not the aspirational one. A target the account has never hit throttles delivery.

- **tCPA starting target** = trailing achievable CPA (median of recent weeks, not the best single week). Start **at or slightly above** it; tighten later.
  - `starting_tCPA ≈ trailing_CPA × 1.0–1.1`
- **tROAS starting target** = trailing achievable ROAS.
  - `starting_tROAS ≈ trailing_ROAS × 0.9–1.0` (set at or just below what the account already earns, then raise)
- **Toward an aspirational goal** — step, don't jump. Move the target ≤ ~15% per adjustment, and only after the current setting clears the learning phase and stabilizes. A larger jump can reset learning (§4).

Show the math and label every input **Measured** (connector/own-data export), **User-provided** (stated by the user), or **Estimated** (benchmark). If a figure the derivation needs is missing, mark it `[needs export]` and ask — never invent a CPA/ROAS/count.

## 3. Portfolio grouping {#portfolio-grouping}

Group campaigns into one bid portfolio only when they share **both** a goal **and** a comparable target. A portfolio pools conversion signal — helpful for thin campaigns, harmful if you mix incompatible economics.

**Do group** when all hold:

- [ ] Same goal type (all tCPA, or all tROAS — never mix)
- [ ] Comparable target range (CPAs/ROAS within a similar band)
- [ ] Same funnel stage (all DR, or all prospecting)
- [ ] Pooling helps a thin campaign borrow signal from a fuller one

**Keep separate** when any hold:

- [ ] Prospecting vs DR (different intent, different target math)
- [ ] Very different CPA/ROAS economics (a $10-CPA and a $120-CPA campaign)
- [ ] A campaign that must hold its own hard cap or brand-term bid

### Grouping map template

| Portfolio | Strategy | Shared target | Campaigns | Funnel stage |
|-----------|----------|---------------|-----------|--------------|
| DR-Core | tCPA | $[Measured] | camp-A, camp-B | DR |
| Value-Ecom | tROAS | [x] ROAS | camp-C | DR |
| Prospecting | max-conversions | (no target) | camp-D | Top |

State one assumption line for any non-obvious grouping and proceed (per the skill's Decision Gate).

## 4. Learning-phase entry checklist

Plan the entry, not the in-flight pacing (that is [budget-pacing-monitor](../../../scale/budget-pacing-monitor/SKILL.md)).

- [ ] **Estimate conversions-to-exit** — Estimated rule of thumb: a strategy typically exits learning after **~15–30 conversions accrue over ~5–7 days** at a stable target/budget. Label it Estimated.
- [ ] **Set the do-not-touch window** — no target or budget changes during learning (roughly the first 5–7 days, or until conversions-to-exit is reached). Name the calendar window.
- [ ] **Name what resets learning** — a target change beyond ~15–20%, a budget change beyond ~20%, structure edits (adding/removing ad groups, changing conversion actions), or a bid-strategy switch. Any of these restarts the clock and wastes spend.
- [ ] **Set a review date** — the first date it is safe to adjust the target, after exit.

### When to switch strategy

| Situation | Move |
|-----------|------|
| max-conversions campaign clears ~30 conv/mo and holds a stable CPA | Switch to **tCPA** at the achieved CPA |
| max-conv-value campaign accrues stable value data | Switch to **tROAS** at the achieved ROAS |
| tCPA/tROAS chronically throttles delivery at target | Loosen the target first (≤15% step); switch to max-conversions only if loosening fails |
| Conversion tracking breaks or volume collapses | Drop to **manual CPC** until signal returns |

A switch **resets the learning phase** — treat it as a fresh entry and re-run this checklist. If a planned target/budget move is large enough to reset learning, flag it as a premature-scaling risk for the auditor's **S** guardrail rather than shipping it silently.
