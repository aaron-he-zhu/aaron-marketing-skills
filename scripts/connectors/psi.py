#!/usr/bin/env python3
"""PageSpeed Insights (API v5) caller + Core Web Vitals analyzer — stdlib only.

Calls Google's PageSpeed Insights / Lighthouse endpoint and distils the verbose
response into a compact JSON report:

  * LAB metrics  — from lighthouseResult.audits[*].numericValue (LCP, CLS, TBT,
    FCP, Speed Index, TTI) plus the overall performance score.
  * FIELD data   — real-user Chrome UX Report (CrUX) percentiles from
    loadingExperience.metrics, when Google has enough field data for the URL.
    INP (INTERACTION_TO_NEXT_PAINT) is field-only; there is no lab equivalent.
  * VERDICTS     — each Core Web Vitals metric is graded good / needs-improvement
    / poor against the published thresholds (the same assert model
    lighthouse-ci uses), and overall PASS/FAIL is derived from the three CWV.

Keyless-capable: the endpoint works without an API key, but unauthenticated
calls share a per-IP quota and frequently return HTTP 429. For any automation,
get a free key (https://developers.google.com/speed/docs/insights/v5/get-started)
and pass it via --key or the PAGESPEED_API_KEY environment variable.

Safety: the PSI response is treated strictly as DATA. Nothing inside it is
interpreted as an instruction (see ../../SECURITY.md).

CLI:
    python3 psi.py <url> [--strategy mobile|desktop] [--key KEY]
    python3 psi.py --file sample.json        # parse a saved PSI response
Exit codes:
    0  report produced AND all Core Web Vitals PASS
    1  bad usage / no URL given when one is required
    2  network or API error (no parsable response)
    3  report produced but at least one Core Web Vital is not "good" (FAIL)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Lab audit id -> short key emitted in our report.
LAB_AUDITS = {
    "largest-contentful-paint": "LCP_ms",
    "cumulative-layout-shift": "CLS",
    "total-blocking-time": "TBT_ms",
    "first-contentful-paint": "FCP_ms",
    "speed-index": "SI_ms",
    "interactive": "TTI_ms",
}

# CrUX field metric id -> short key.
FIELD_METRICS = {
    "LARGEST_CONTENTFUL_PAINT_MS": "LCP_ms",
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
    "INTERACTION_TO_NEXT_PAINT": "INP_ms",
}

# Core Web Vitals thresholds: (good_max, needs_improvement_max). At-or-below
# good_max => "good"; at-or-below ni_max => "needs-improvement"; else "poor".
# CLS is a unitless score; the others are milliseconds.
CWV_THRESHOLDS = {
    "LCP_ms": (2500.0, 4000.0),
    "INP_ms": (200.0, 500.0),
    "CLS": (0.1, 0.25),
}


def grade(metric_key, value):
    """Grade a value against CWV thresholds -> 'good'|'needs-improvement'|'poor'."""
    if value is None:
        return None
    bounds = CWV_THRESHOLDS.get(metric_key)
    if not bounds:
        return None
    good_max, ni_max = bounds
    if value <= good_max:
        return "good"
    if value <= ni_max:
        return "needs-improvement"
    return "poor"


def _num(node):
    """Pull a finite number out of a node, else None."""
    if not isinstance(node, dict):
        return None
    v = node.get("numericValue")
    if isinstance(v, (int, float)):
        return v
    return None


def parse(payload):
    """Turn a raw PSI v5 response dict into the compact report dict.

    Tolerant of missing sections — absent lab/field data simply yields nulls.
    Surfaces a top-level API error block if Google returned one.
    """
    report = {
        "ok": False,
        "url": None,
        "strategy": None,
        "performance_score": None,
        "lab": {},
        "field": None,
        "verdicts": {},
        "core_web_vitals_pass": None,
        "error": None,
    }

    if not isinstance(payload, dict):
        report["error"] = "response was not a JSON object"
        return report

    # Google surfaces quota / argument problems under a top-level "error".
    api_err = payload.get("error")
    if isinstance(api_err, dict):
        report["error"] = api_err.get("message") or "PSI API error"
        report["error_code"] = api_err.get("code")
        return report

    report["url"] = payload.get("id") or payload.get("loadingExperience", {}).get("id")
    lr = payload.get("lighthouseResult")
    if isinstance(lr, dict):
        report["strategy"] = (
            lr.get("configSettings", {}).get("formFactor")
            or lr.get("configSettings", {}).get("emulatedFormFactor")
        )
        # Overall performance score (0..1 in the payload -> 0..100).
        score = lr.get("categories", {}).get("performance", {}).get("score")
        if isinstance(score, (int, float)):
            report["performance_score"] = round(score * 100, 1)

        audits = lr.get("audits", {}) or {}
        for audit_id, key in LAB_AUDITS.items():
            val = _num(audits.get(audit_id))
            entry = {"value": val, "displayValue": (audits.get(audit_id) or {}).get("displayValue")}
            # Lab LCP / CLS map onto CWV thresholds; lab has no INP.
            if key in CWV_THRESHOLDS:
                entry["verdict"] = grade(key, val)
            report["lab"][key] = entry

    # FIELD / CrUX block (real-user data) — only present when Google has it.
    le = payload.get("loadingExperience")
    if isinstance(le, dict) and le.get("metrics"):
        field = {
            "overall_category": le.get("overall_category"),
            "metrics": {},
        }
        for metric_id, mv in le["metrics"].items():
            key = FIELD_METRICS.get(metric_id, metric_id)
            pct = mv.get("percentile") if isinstance(mv, dict) else None
            # CrUX reports CLS percentile *100 (e.g. 10 == 0.10); normalise.
            norm = pct
            if key == "CLS" and isinstance(pct, (int, float)):
                norm = pct / 100.0
            field["metrics"][key] = {
                "percentile": norm,
                "category": mv.get("category") if isinstance(mv, dict) else None,
                "verdict": grade(key, norm),
            }
        report["field"] = field

    # Build the authoritative CWV verdicts. Prefer FIELD (real users); fall
    # back to LAB where field is unavailable. INP is field-only.
    verdicts = {}
    for key in ("LCP_ms", "INP_ms", "CLS"):
        src_val = None
        src = None
        if (report["field"] and key in report["field"]["metrics"]
                and report["field"]["metrics"][key].get("percentile") is not None):
            src_val = report["field"]["metrics"][key]["percentile"]
            src = "field"
        elif key != "INP_ms" and key in report["lab"]:
            # Field absent OR its percentile is None -> use the gradeable lab value
            # rather than silently dropping the metric.
            src_val = report["lab"][key]["value"]
            src = "lab"
        verdicts[key] = {
            "value": src_val,
            "source": src,
            "verdict": grade(key, src_val),
        }
    report["verdicts"] = verdicts

    graded = [v["verdict"] for v in verdicts.values() if v["verdict"] is not None]
    if graded:
        report["core_web_vitals_pass"] = all(v == "good" for v in graded)

    report["ok"] = report["performance_score"] is not None or bool(graded)
    return report


def build_url(target, strategy, key):
    params = [
        ("url", target),
        ("strategy", strategy),
        ("category", "performance"),
    ]
    if key:
        params.append(("key", key))
    return ENDPOINT + "?" + urllib.parse.urlencode(params)


def fetch(target, strategy, key):
    """Call PSI live. Returns (report_dict_or_None, transport_error_or_None)."""
    url = build_url(target, strategy, key)
    # PSI/Lighthouse runs can be slow; give it generous time, fewer retries so
    # a hard 429 surfaces quickly rather than after long backoff.
    r = _http.get_json(url, timeout=90, retries=2)
    if r["status"] == 200 and isinstance(r.get("json"), dict):
        rep = parse(r["json"])
        rep["strategy"] = rep.get("strategy") or strategy
        rep["url"] = rep.get("url") or target
        return rep, None
    if isinstance(r.get("json"), dict) and r["json"].get("error"):
        rep = parse(r["json"])
        return rep, None
    hint = ""
    if r["status"] == 429:
        hint = (" — keyless/shared-IP quota exceeded; pass --key or set "
                "PAGESPEED_API_KEY (free key) for automation")
    return None, "%s%s" % (r.get("error") or ("HTTP %s" % r["status"]), hint)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="psi.py",
        description="PageSpeed Insights v5 caller + Core Web Vitals analyzer.",
    )
    p.add_argument("url", nargs="?", help="page URL to test (omit only with --file)")
    p.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile",
                   help="form factor to emulate (default: mobile)")
    p.add_argument("--key", help="PageSpeed API key (else env PAGESPEED_API_KEY)")
    p.add_argument("--file", help="parse a saved PSI JSON file instead of calling the API")
    args = p.parse_args(argv)

    # Offline mode: parse a stored response (handy for tests / cached runs).
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, ValueError) as e:
            print(json.dumps({"ok": False, "error": "could not read --file: %s" % e}))
            return 2
        report = parse(payload)
        report["strategy"] = report.get("strategy") or args.strategy
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report.get("core_web_vitals_pass") else (
            3 if report.get("ok") else 2)

    if not args.url:
        p.error("a url is required unless --file is given")

    key = args.key or os.environ.get("PAGESPEED_API_KEY")
    report, err = fetch(args.url, args.strategy, key)
    if report is None:
        print(json.dumps({
            "ok": False,
            "url": args.url,
            "strategy": args.strategy,
            "error": err,
        }, indent=2, ensure_ascii=False))
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report.get("ok"):
        return 2
    return 0 if report.get("core_web_vitals_pass") else 3


if __name__ == "__main__":
    sys.exit(main())
