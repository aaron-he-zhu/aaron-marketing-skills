# Ad Test Design Guide

Detail pack for [ad-test-designer](../SKILL.md). Significance methods here are **documented procedures only** — walk them by hand, never run scipy or any code.

## Variant matrix template

| Variant | One changed variable | What's held constant | Destination |
|---------|---------------------|----------------------|-------------|
| A (control) | — (baseline) | everything | current LP/URL |
| B | the single test change | all else = control | same or split URL |
| C, D (A/B/n, ≤ 4 total) | a different single change each | all else = control | same |

Rules: one variable per variant; keep a control/holdout; cap A/B/n at 4 variants so traffic isn't split too thin; same audience + budget logic across arms.

### Test structures

- **Creative A/B** — vary one creative element (headline / hook / image). Primary metric usually CTR or CVR.
- **Landing-page A/B / split-URL** — vary one page element (hero, CTA, proof). Primary metric CVR; guardrail bounce.
- **Incrementality (geo / holdout)** — a treated group gets the change, a matched holdout does not. Measures lift over the counterfactual, not just relative variant performance. Needs a clean, comparable holdout (geo split or audience holdout) and a longer window.

## Sample-size lookup (per variant, two-sided α = 0.05, power = 0.80)

Approximate exposures **per variant** to detect a relative lift on a binary metric (CVR/CTR). Interpolate; for A/B/n add ~20–30% headroom for multiple comparisons.

| Baseline rate | 10% lift | 20% lift | 50% lift |
|---------------|----------|----------|----------|
| 1% | ~150k | ~39k | ~6k |
| 3% | ~47k | ~12k | ~2k |
| 5% | ~27k | ~7k | ~1.2k |
| 10% | ~12k | ~3k | ~550 |

**Duration** = (per-variant sample × number of variants) ÷ (traffic/day reaching the test). Floor at one full business cycle (≥ 1–2 weeks) to absorb day-of-week effects. Pre-commit to the sample size; **do not peek and stop early** — early stopping inflates false positives.

**Power note**: power (1−β) is the chance of detecting a true effect of the stated size. The table is built at 0.80; if the user wants 0.90, sizes rise ~30%. State the assumed baseline, minimum detectable effect, α, and power in the design.

## Significance methods (documented procedures — no code)

### Two-proportion z-test (CVR / CTR)

For control rate p₁ = x₁/n₁ and variant rate p₂ = x₂/n₂:

1. Pooled rate `p = (x₁ + x₂) / (n₁ + n₂)`.
2. Standard error `SE = sqrt( p·(1−p)·(1/n₁ + 1/n₂) )`.
3. `z = (p₂ − p₁) / SE`.
4. Significant at 95% when `|z| ≥ 1.96` (two-sided), i.e. p < 0.05.

Report p₁, p₂, the relative lift `(p₂−p₁)/p₁`, and the z value with its inputs shown.

### Mann-Whitney U (non-normal continuous metrics)

Use for revenue-per-user, order value, time-on-page where the distribution is skewed and the z-test's normality assumption fails. Rank all observations across both arms, sum the ranks per arm, derive U, and compare to the critical value (or its normal approximation) at α = 0.05. Document the rank sums and the U you computed; do not run a library.

### Bootstrap confidence interval (CI on the lift)

When you want a CI on the lift rather than only a p-value: resample each arm with replacement many times, recompute the lift each time, and take the 2.5th/97.5th percentiles as the 95% CI. The test is "significant" when the CI excludes 0 (or excludes the min-practical-lift threshold). Describe the procedure and the resulting interval; do not execute it.

## The decision gate

Apply **both** conditions, not just statistical significance:

```
significant  = p < 0.05 (or 95% CI excludes 0)
worth_it     = observed lift ≥ minimum practical lift (set at design time, e.g. 10–15%)
```

| Result | Decision |
|--------|----------|
| significant AND worth_it | **Promote** the winner |
| significant loser | **Kill** the variant, keep control, note why |
| not significant at full sample | **Kill / inconclusive** — bolder test or more traffic |
| significant but below min practical lift | **Keep control** — real but not worth the cost/risk |
| guardrail breach (spend, refund, bounce worse) | **Kill** regardless of primary metric |
| mixed across segments | **Segment** and decide per segment, or retest |

A statistically significant 0.4% lift on a metric where you set a 10% practical floor is a **keep-control**, not a promote — significance without practical lift does not clear the gate.
