#!/usr/bin/env python3
"""experiment.py — statistical facts for marketing experiments (keyless, stdlib-only).

The missing closing loop: the discipline's *-test-designer skills (ad-test-designer,
send-experiment-designer, message-test-designer) DESIGN experiments and the
*-measurement-loop skills roll results up, but nothing computes
whether an observed difference clears precommitted statistical and practical bars.
This helper computes facts from the USER'S OWN experiment data; it never decides
whether the business should promote, roll back, or continue a test.

Everything is exact stdlib math (math + statistics + random). No numpy/scipy.

Subcommands (all print JSON; import the functions for the pure math):
  proportion  — two-variant conversion / rate test (the common marketing A/B):
                two-proportion z-test (two-sided), effect interval, Wilson score
                intervals, and practical-lift flag.
      python3 experiment.py proportion --control 100 1000 --variant 130 1000
  continuous  — two-variant continuous metric (revenue/user, time-on-page, …):
                Mann-Whitney U (tie-corrected normal approx) + a bootstrap CI for
                the difference in means (distribution-free — no normality assumed).
      python3 experiment.py continuous --a 12,9,15,… --b 14,11,20,…
  samplesize  — required n PER VARIANT to detect an absolute lift at alpha/power,
                or (with --n) the minimum detectable effect for a given n.
      python3 experiment.py samplesize --baseline 0.10 --mde 0.02
      python3 experiment.py samplesize --baseline 0.10 --n 4000

Facts only: outputs expose decision inputs, never a business verdict. Input counts
or samples are user-provided observations; all statistics emitted here are
Calculated. The default practical-lift reference is 15%, and callers should pass
their preregistered bar explicitly when it differs.

SECURITY: numeric inputs only; nothing is fetched. See ../../SECURITY.md.
Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

Exit codes: 0 ok · 1 bad input.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys


def _require_finite(label, *values):
    """Reject NaN/Infinity before they can silently poison comparisons or JSON."""
    for value in values:
        try:
            finite = math.isfinite(float(value))
        except (TypeError, ValueError):
            finite = False
        if not finite:
            raise ValueError("%s must contain only finite numbers" % label)


def _finite_samples(label, values):
    samples = [float(value) for value in values]
    _require_finite(label, *samples)
    return samples

# --------------------------------------------------------------------------- #
# Normal distribution helpers (exact CDF via erf; inverse via Acklam's rational
# approximation — both pure-stdlib, no scipy).
# --------------------------------------------------------------------------- #

def norm_cdf(z):
    """Standard-normal CDF Phi(z). Exact (math.erf)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def norm_ppf(p):
    """Standard-normal inverse CDF (quantile). Acklam's algorithm; |abs err| < 1.15e-9.

    Raises ValueError outside (0, 1). norm_ppf(0.975) == 1.959963985..."""
    if not (0.0 < p < 1.0):
        raise ValueError("norm_ppf domain is (0, 1), got %r" % (p,))
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    plow, phigh = 0.02425, 1.0 - 0.02425
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)


def _two_sided_p(z):
    """Two-sided p-value for a standard-normal test statistic z."""
    return 2.0 * (1.0 - norm_cdf(abs(z)))


# --------------------------------------------------------------------------- #
# Proportion (conversion-rate) test
# --------------------------------------------------------------------------- #

def wilson_interval(conv, n, conf=0.95):
    """Wilson score confidence interval for a proportion (better than normal at
    small n / extreme rates). Returns (low, high). Pure."""
    _require_finite("wilson interval", conv, n, conf)
    if not (0.0 < conf < 1.0):
        raise ValueError("conf must be in (0, 1), got %r" % (conf,))
    if n <= 0:
        return (0.0, 0.0)
    if conv < 0 or conv > n:
        raise ValueError("need 0 <= conversions <= n")
    z = norm_ppf(1.0 - (1.0 - conf) / 2.0)
    p = conv / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = (z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def two_proportion(c_conv, c_n, v_conv, v_n, alpha=0.05, min_lift=0.15):
    """Return statistical and practical-effect facts for two observed rates."""
    _require_finite("proportion test", c_conv, c_n, v_conv, v_n, alpha, min_lift)
    for name, conv, n in (("control", c_conv, c_n), ("variant", v_conv, v_n)):
        if n <= 0 or conv < 0 or conv > n:
            raise ValueError("%s: need 0 <= conversions <= n and n > 0" % name)
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1), got %r" % (alpha,))
    if min_lift < 0:
        raise ValueError("min_lift must be >= 0, got %r" % (min_lift,))
    pc, pv = c_conv / c_n, v_conv / v_n
    # Pooled proportion for the null-hypothesis standard error.
    p_pool = (c_conv + v_conv) / (c_n + v_n)
    se = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / c_n + 1.0 / v_n))
    z = (pv - pc) / se if se > 0 else 0.0
    p_value = _two_sided_p(z)
    conf = 1.0 - alpha
    abs_lift = pv - pc
    statistically_significant = p_value < alpha
    z_crit = norm_ppf(1.0 - alpha / 2.0)
    effect_se = math.sqrt(pc * (1.0 - pc) / c_n + pv * (1.0 - pv) / v_n)
    effect_interval = [max(-1.0, abs_lift - z_crit * effect_se),
                       min(1.0, abs_lift + z_crit * effect_se)]
    effect_interval_excludes_zero = effect_interval[0] > 0 or effect_interval[1] < 0
    if pc > 0:
        rel_lift = abs_lift / pc
        practical_lift_clears_bar = rel_lift >= min_lift
    elif pv > 0:
        rel_lift = None
        practical_lift_clears_bar = None
    else:
        rel_lift = None
        practical_lift_clears_bar = False
    if abs_lift > 0:
        direction = "variant_higher"
    elif abs_lift < 0:
        direction = "variant_lower"
    else:
        direction = "no_observed_difference"
    control_interval = list(wilson_interval(c_conv, c_n, conf))
    variant_interval = list(wilson_interval(v_conv, v_n, conf))
    return {
        "test": "two_proportion_z",
        "control": {"conversions": c_conv, "n": c_n, "rate": pc,
                    "confidence_interval": control_interval, "confidence": conf},
        "variant": {"conversions": v_conv, "n": v_n, "rate": pv,
                    "confidence_interval": variant_interval, "confidence": conf},
        "absolute_lift": abs_lift,
        "absolute_lift_confidence_interval": effect_interval,
        "confidence": conf,
        "relative_lift": rel_lift,
        "direction": direction,
        "z": z,
        "p_value": p_value,
        "alpha": alpha,
        "statistically_significant": statistically_significant,
        "effect_interval_excludes_zero": effect_interval_excludes_zero,
        "practical_lift_bar": min_lift,
        "practical_lift_clears_bar": practical_lift_clears_bar,
        "provenance": {"inputs": "user-provided-observations", "outputs": "calculated"},
        "note": "Two-sided two-proportion z-test on user-provided observed counts; all "
                "statistics are Calculated and no business action is returned. Per-arm "
                "intervals are Wilson intervals; the absolute "
                "lift interval uses the unpooled standard error. Overlapping per-arm intervals "
                "do NOT imply non-significance. A zero control makes relative lift undefined, "
                "so preregister an absolute-effect bar for that case. p assumes a single "
                "precommitted read; repeated peeking or parallel comparisons require an "
                "appropriate sequential or multiplicity-aware design.",
    }


# --------------------------------------------------------------------------- #
# Continuous metric: Mann-Whitney U (distribution-free) + bootstrap CI
# --------------------------------------------------------------------------- #

def _avg_ranks(values):
    """Fractional (tie-averaged) ranks of `values`, plus tie-group sizes. Pure."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    ties = []
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # 1-based average rank for the tie block
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        if j > i:
            ties.append(j - i + 1)
        i = j + 1
    return ranks, ties


def mann_whitney(a, b, alpha=0.05):
    """Mann-Whitney U (a vs b), tie-corrected normal approximation two-sided
    p-value. Distribution-free — no normality assumed. Pure / no network."""
    a = _finite_samples("sample a", a)
    b = _finite_samples("sample b", b)
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        raise ValueError("both samples must be non-empty")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1), got %r" % (alpha,))
    ranks, ties = _avg_ranks(a + b)
    r1 = sum(ranks[:n1])
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    mu = n1 * n2 / 2.0
    n = n1 + n2
    tie_term = sum(t ** 3 - t for t in ties)
    sigma = math.sqrt((n1 * n2 / 12.0) * ((n + 1) - tie_term / (n * (n - 1)))) if n > 1 else 0.0
    if sigma > 0:
        # continuity correction
        z = (u - mu + (0.5 if u < mu else -0.5)) / sigma
        p_value = _two_sided_p(z)
    else:
        z, p_value = 0.0, 1.0
    return {
        "test": "mann_whitney_u",
        "n_a": n1, "n_b": n2,
        "median_a": _median(a), "median_b": _median(b),
        "mean_a": sum(a) / n1, "mean_b": sum(b) / n2,
        "u": u, "z": z, "p_value": p_value, "alpha": alpha,
        "statistically_significant": p_value < alpha,
        "provenance": {"inputs": "user-provided-observations", "outputs": "calculated"},
        "note": "Distribution-free rank test on user-provided observed samples; tie-corrected "
                "normal approximation (valid for n>=~20 per group). p assumes a single "
                "pre-committed read: repeated peeking inflates false positives.",
    }


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def bootstrap_diff(a, b, stat="mean", B=10000, alpha=0.05, seed=0):
    """Percentile bootstrap CI for stat(b) - stat(a) (default difference in means).
    Distribution-free interval estimate. Deterministic given `seed`. Pure."""
    a = _finite_samples("sample a", a)
    b = _finite_samples("sample b", b)
    if not a or not b:
        raise ValueError("both samples must be non-empty")
    if B < 1:
        raise ValueError("bootstrap resamples (B) must be >= 1, got %r" % (B,))
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1), got %r" % (alpha,))
    na, nb = len(a), len(b)
    # With n<2 in either arm every resample is identical, so the CI collapses to a
    # point and excludes_zero must NOT be read as significance (see `reliable`).
    reliable = min(na, nb) >= 2
    agg = (lambda xs: sum(xs) / len(xs)) if stat == "mean" else _median
    rng = random.Random(seed)
    diffs = []
    for _ in range(B):
        ra = [a[rng.randrange(na)] for _ in range(na)]
        rb = [b[rng.randrange(nb)] for _ in range(nb)]
        diffs.append(agg(rb) - agg(ra))
    diffs.sort()
    lo = diffs[int((alpha / 2.0) * B)]
    hi = diffs[min(B - 1, int((1.0 - alpha / 2.0) * B))]
    point = agg(b) - agg(a)
    return {
        "statistic": stat,
        "point_estimate": point,
        "confidence_interval": [lo, hi],
        "confidence": 1.0 - alpha,
        "interval_excludes_zero": bool(reliable and (lo > 0 or hi < 0)),
        "reliable": reliable,
        "bootstrap_samples": B,
        "provenance": {"inputs": "user-provided-observations", "outputs": "calculated"},
        "note": "Percentile bootstrap CI for the difference (deterministic given the "
                "seed). interval_excludes_zero is forced "
                "False when reliable is False (n<2 in an arm -> a degenerate zero-width CI).",
    }


# --------------------------------------------------------------------------- #
# Sample size / minimum detectable effect (proportion test)
# --------------------------------------------------------------------------- #

def sample_size(baseline, mde, alpha=0.05, power=0.8):
    """Required n PER VARIANT to detect an ABSOLUTE lift `mde` on a baseline rate
    at two-sided `alpha` and `power` (two-proportion test). Pure."""
    _require_finite("sample-size inputs", baseline, mde, alpha, power)
    if not (0.0 < baseline < 1.0):
        raise ValueError("baseline must be in (0, 1)")
    if mde <= 0 or baseline + mde >= 1.0:
        raise ValueError("mde must be > 0 and baseline+mde < 1")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1), got %r" % (alpha,))
    if not (0.0 < power < 1.0):
        raise ValueError("power must be in (0, 1), got %r" % (power,))
    p1, p2 = baseline, baseline + mde
    z_a = norm_ppf(1.0 - alpha / 2.0)
    z_b = norm_ppf(power)
    p_bar = (p1 + p2) / 2.0
    n = ((z_a * math.sqrt(2 * p_bar * (1 - p_bar)) +
          z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (mde ** 2)
    return {
        "baseline": baseline, "mde_absolute": mde,
        "alpha": alpha, "power": power,
        "n_per_variant": math.ceil(n),
        "note": "Per-variant sample size for a two-sided two-proportion test.",
    }


def min_detectable_effect(baseline, n, alpha=0.05, power=0.8, tol=1e-6):
    """Invert sample_size to absolute accuracy `tol`; reject an infeasible n."""
    _require_finite("MDE inputs", baseline, n, alpha, power, tol)
    if not (0.0 < baseline < 1.0) or n <= 0:
        raise ValueError("baseline in (0,1) and n > 0 required")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1), got %r" % (alpha,))
    if not (0.0 < power < 1.0):
        raise ValueError("power must be in (0, 1), got %r" % (power,))
    if tol <= 0:
        raise ValueError("tol must be > 0")

    # Keep the upper rate strictly below one without using the search precision
    # as a probability margin (which excluded valid lifts near either endpoint).
    lo, hi = 0.0, math.nextafter(1.0, 0.0) - baseline
    while baseline + hi >= 1.0:
        hi = math.nextafter(hi, 0.0)
    if hi <= 0:
        raise ValueError("no representable higher rate below 1 for this baseline")
    z_a, z_b = norm_ppf(1.0 - alpha / 2.0), norm_ppf(power)
    if z_b < 0:
        # Write required n as (z_a*sqrt(x*x + 1/2) + z_b*x)**2,
        # where x*x = 2*p*(1-p)/lift**2 + (1-2*p)/lift - 1.
        # x decreases with lift. A negative z_b can put the minimum inside
        # the rate domain; search only up to that minimum, not past it.
        difference = z_a * z_a - z_b * z_b
        if difference == 0:
            raise ValueError("alpha and power give a zero MDE infimum, not a positive minimum")
        x_squared = (z_b * z_b if difference > 0 else z_a * z_a) / (
            2.0 * abs(difference))
        slope = 1.0 - 2.0 * baseline
        variance = 2.0 * baseline * (1.0 - baseline)
        radical = math.sqrt(slope * slope + 4.0 * (1.0 + x_squared) * variance)
        minimum_lift = ((slope + radical) / (2.0 * (1.0 + x_squared))
                        if slope >= 0 else 2.0 * variance / (radical - slope))
        hi = min(hi, minimum_lift)

    def required(effect):
        try:
            return sample_size(baseline, effect, alpha, power)["n_per_variant"]
        except (OverflowError, ZeroDivisionError):
            # A tiny trial lift can exceed the finite sample-size range.
            return math.inf

    if required(hi) > n:
        raise ValueError("no positive lift below a rate of 1 is detectable at this n")
    while hi - lo > tol:
        mid = (lo + hi) / 2.0
        if mid == lo or mid == hi:
            raise ValueError("tol is below floating-point resolution at this lift")
        need = required(mid)
        if need > n:
            lo = mid
        else:
            hi = mid
    return {"baseline": baseline, "n_per_variant": n, "alpha": alpha, "power": power,
            "mde_absolute": hi,
            "note": "Smallest absolute lift detectable at this n, within absolute tolerance %g." % tol}


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _floats(s):
    return [float(x) for x in s.replace(" ", "").split(",") if x != ""]


def build_parser():
    p = argparse.ArgumentParser(
        prog="experiment.py",
        description="Statistical significance for marketing A/B tests (keyless, stdlib).")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("proportion", help="Two-variant conversion/rate test.")
    pp.add_argument("--control", nargs=2, type=int, metavar=("CONV", "N"), required=True)
    pp.add_argument("--variant", nargs=2, type=int, metavar=("CONV", "N"), required=True)
    pp.add_argument("--alpha", type=float, default=0.05)
    pp.add_argument("--min-lift", type=float, default=0.15,
                    help="Precommitted RELATIVE practical-effect bar (default: 0.15).")

    pc = sub.add_parser("continuous", help="Two-variant continuous metric.")
    pc.add_argument("--a", type=_floats, required=True, help="Comma-separated control samples.")
    pc.add_argument("--b", type=_floats, required=True, help="Comma-separated variant samples.")
    pc.add_argument("--alpha", type=float, default=0.05)
    pc.add_argument("--stat", choices=("mean", "median"), default="mean")
    pc.add_argument("--boot", type=int, default=10000, help="Bootstrap resamples.")
    pc.add_argument("--seed", type=int, default=0)

    ps = sub.add_parser("samplesize", help="Sample size or MDE for a proportion test.")
    ps.add_argument("--baseline", type=float, required=True)
    ps.add_argument("--mde", type=float, default=None, help="Absolute lift to detect -> required n.")
    ps.add_argument("--n", type=int, default=None, help="n per variant -> detectable MDE.")
    ps.add_argument("--alpha", type=float, default=0.05)
    ps.add_argument("--power", type=float, default=0.8)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "proportion":
            out = two_proportion(args.control[0], args.control[1],
                                 args.variant[0], args.variant[1],
                                 alpha=args.alpha, min_lift=args.min_lift)
        elif args.cmd == "continuous":
            mw = mann_whitney(args.a, args.b, alpha=args.alpha)
            boot = bootstrap_diff(args.a, args.b, stat=args.stat, B=args.boot,
                                  alpha=args.alpha, seed=args.seed)
            out = {"mann_whitney": mw, "bootstrap": boot,
                   "decision_inputs": {
                       "rank_test_significant": mw["statistically_significant"],
                       "effect_interval_excludes_zero": boot["interval_excludes_zero"],
                       "effect_interval_reliable": boot["reliable"],
                   },
                   "provenance": {"inputs": "user-provided-observations",
                                  "outputs": "calculated"},
                   "note": "Statistical facts only. The calling skill applies its "
                           "precommitted practical-effect and business guardrail policy."}
        else:  # samplesize
            if args.mde is not None:
                out = sample_size(args.baseline, args.mde, args.alpha, args.power)
            elif args.n is not None:
                out = min_detectable_effect(args.baseline, args.n, args.alpha, args.power)
            else:
                print("error: pass either --mde (-> n) or --n (-> MDE)", file=sys.stderr)
                return 1
    except (ValueError, ZeroDivisionError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 1
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
