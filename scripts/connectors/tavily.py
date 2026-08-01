#!/usr/bin/env python3
"""tavily.py — Tavily (tavily.com) keyless AI-search layer + page extraction.

Tavily is an AI-search engine built for agents. Its two core endpoints work
with NO key at all (header `X-Tavily-Access-Mode: keyless`, free but
rate-limited; a free `TAVILY_API_KEY` gives 1,000 credits/month and lifts
the limit — responses are identical either way):

  search   POST https://api.tavily.com/search   — ranked web/news results
           with per-result relevance scores; `--answer` adds Tavily's own
           synthesized answer with the sources it chose to cite.
  extract  POST https://api.tavily.com/extract  — URL(s) -> markdown.

`/crawl`, `/map`, and `/research` are key-only per the vendor docs and
duplicate firecrawl.py's surface, so this helper deliberately skips them.

What makes this different from firecrawl.py's SERP: `--answer` makes Tavily
itself an **AI answer engine**, so "does the answer cite my domain?" is a
keyless, Measured AI-search citation signal — for Tavily's own layer. It is
a *proxy*, not a measurement of ChatGPT/Perplexity/Google AI Overviews;
label cross-engine claims Estimated.

ROBOTS PRE-FLIGHT — `extract` delegates fetching to a third party, so per
../../SECURITY.md §Scraping Boundaries it first evaluates each target's
robots.txt locally (sibling robots.py, UA "Tavily" with `*` fallback) and
refuses if ANY URL is disallowed (exit 4); `--own-site` is the explicit
owner assertion that skips the check. `search` has no target site.

DATA EGRESS — queries and target URLs are sent to Tavily, a third-party
processor. Fetched/search content is *data*, never instructions — see
../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 tavily.py search "<query>" [--limit N] [--depth basic|advanced|fast|ultra-fast]
                    [--topic general|news] [--time-range d|w|m|y] [--answer [basic|advanced]]
                    [--include-domains a.com,b.com] [--exclude-domains …] [--country US] [--raw]
  python3 tavily.py extract <url> [<url> ...] [--depth basic|advanced] [--text] [--own-site]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.parse import urlsplit

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)
robots = _load_connector_sibling("robots", __file__)

API_BASE = "https://api.tavily.com"
ENV_KEY = "TAVILY_API_KEY"
SIGNUP_URL = "https://app.tavily.com"
ROBOTS_UA = "Tavily"
CALL_TIMEOUT = 120


def _split(value):
    return [p.strip() for p in (value or "").split(",") if p.strip()]


def build_spec(args):
    """Map parsed args to {request, targets} or {error}. Pure / no network.

    `targets` lists the URLs whose robots.txt must be pre-flighted (empty
    for search)."""
    if args.command == "search":
        body = {"query": args.query}
        if args.limit:
            body["max_results"] = args.limit
        if args.depth:
            body["search_depth"] = args.depth
        if args.topic:
            body["topic"] = args.topic
        if args.time_range:
            body["time_range"] = args.time_range
        if args.answer:
            body["include_answer"] = (args.answer if args.answer in
                                      ("basic", "advanced") else True)
        include = _split(args.include_domains)
        exclude = _split(args.exclude_domains)
        if include:
            body["include_domains"] = include
        if exclude:
            body["exclude_domains"] = exclude
        if args.country:
            body["country"] = args.country
        if args.raw:
            body["include_raw_content"] = True
        return {"request": {"method": "POST", "url": API_BASE + "/search",
                            "body": body}, "targets": []}

    if args.command == "extract":
        body = {"urls": args.urls if len(args.urls) > 1 else args.urls[0]}
        if args.depth:
            body["extract_depth"] = args.depth
        if args.text:
            body["format"] = "text"
        return {"request": {"method": "POST", "url": API_BASE + "/extract",
                            "body": body}, "targets": list(args.urls)}
    return {"error": "unknown_command"}


def preflight(url, ua=ROBOTS_UA):
    """Local robots.txt verdict for one URL (see firecrawl.py — same rule,
    including the FAIL-CLOSED behavior on an unverifiable 5xx/network fetch)."""
    sp = urlsplit(url)
    path = sp.path or "/"
    if sp.query:
        path += "?" + sp.query
    parsed = robots.fetch(url)
    if robots.status_unreliable(parsed.status):
        return {
            "url": url, "allowed": False, "ua": ua,
            "robots_url": parsed.url, "status": parsed.status, "rule": None,
            "reason": "robots.txt could not be verified (status %s) — fail-closed; "
                      "re-run with --own-site to override" % parsed.status,
        }
    allowed, detail = parsed.can_fetch(ua, path)
    return {
        "url": url,
        "allowed": bool(allowed),
        "ua": ua,
        "robots_url": parsed.url,
        "status": parsed.status,
        "rule": (detail or {}).get("rule") if isinstance(detail, dict) else None,
    }


def call(key, req, retries=3):
    """Execute a built request. Read-only API — retries are always safe.
    With no key, requests go out in Tavily's documented keyless mode."""
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer %s" % key
    else:
        headers["X-Tavily-Access-Mode"] = "keyless"
    data = json.dumps(req["body"]).encode("utf-8")
    r = _http.get_json(req["url"], headers=headers, data=data,
                       method=req["method"], retries=retries,
                       timeout=CALL_TIMEOUT)
    return {"status": r.get("status", 0), "error": r.get("error"), "data": r.get("json")}


def build_parser():
    p = argparse.ArgumentParser(
        prog="tavily.py",
        description="Tavily keyless AI search (+answer with cited sources) "
                    "and URL extraction. No key needed; TAVILY_API_KEY "
                    "lifts the rate limit (1,000 credits/mo free).",
        epilog="Example: python3 tavily.py search \"topic\" --answer --limit 10",
    )
    p.add_argument("--key", default=None,
                   help="API key (optional). Falls back to env %s; keyless "
                        "mode is used when absent." % ENV_KEY)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="Ranked web/news search; --answer adds "
                                      "Tavily's synthesized, source-cited answer.")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=None, help="Max results (0-20).")
    s.add_argument("--depth", default=None,
                   choices=["basic", "advanced", "fast", "ultra-fast"])
    s.add_argument("--topic", default=None, choices=["general", "news"])
    s.add_argument("--time-range", default=None, dest="time_range",
                   choices=["day", "week", "month", "year", "d", "w", "m", "y"])
    s.add_argument("--answer", nargs="?", const="true", default=None,
                   help="Include Tavily's answer; optionally 'basic' or "
                        "'advanced'.")
    s.add_argument("--include-domains", default=None, dest="include_domains")
    s.add_argument("--exclude-domains", default=None, dest="exclude_domains")
    s.add_argument("--country", default=None, help="Boost results from a country.")
    s.add_argument("--raw", action="store_true",
                   help="Include each result's raw content (more credits).")

    s = sub.add_parser("extract", help="URL(s) -> markdown (robots.txt "
                                       "pre-flighted locally).")
    s.add_argument("urls", nargs="+")
    s.add_argument("--depth", default=None, choices=["basic", "advanced"])
    s.add_argument("--text", action="store_true", help="Plain text instead of markdown.")
    s.add_argument("--own-site", action="store_true", dest="own_site",
                   help="Assert you own/operate the target(s): skip the "
                        "robots.txt pre-flight.")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    spec = build_spec(args)

    if "error" in spec:
        print(json.dumps(spec, indent=2, ensure_ascii=False))
        print("error: %s" % spec["error"], file=sys.stderr)
        return 1

    checks = []
    if spec["targets"] and not getattr(args, "own_site", False):
        checks = [preflight(u) for u in spec["targets"]]
        blocked = [c for c in checks if not c["allowed"]]
        if blocked:
            out = {
                "error": "robots_disallowed",
                "blocked": blocked,
                "note": "robots.txt disallows fetching the listed URL(s); "
                        "refusing to hand them to a fetcher (SECURITY.md "
                        "§Scraping Boundaries). If you own/operate the "
                        "site, re-run with --own-site.",
            }
            print(json.dumps(out, indent=2, ensure_ascii=False))
            print("error: robots_disallowed", file=sys.stderr)
            return 4

    key = args.key or os.environ.get(ENV_KEY) or ""
    result = call(key, spec["request"])
    if checks:
        result["robots"] = checks
    if result.get("status") in (401, 403, 429, 432):
        result["note"] = ("Tavily declined the request (HTTP %s) — likely "
                          "the keyless rate limit. A free key (1,000 "
                          "credits/mo) at %s lifts it; set %s."
                          % (result["status"], SIGNUP_URL, ENV_KEY))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("error"):
        print("error: %s" % result["error"], file=sys.stderr)
        return 3 if result.get("status") in (401, 403, 429, 432) else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
