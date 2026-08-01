#!/usr/bin/env python3
"""firecrawl.py — Firecrawl (firecrawl.dev) hosted scraping / SERP / crawling.

Firecrawl is a hosted fetcher that returns LLM-ready markdown for any URL —
including JavaScript-heavy pages the DIY `crawl.py`/`onpage.py` fetch cannot
render — plus a live web-SERP endpoint. Since the 2026 keyless launch,
`scrape` and `search` work with NO key at all (~1,000 free credits/month);
an optional `FIRECRAWL_API_KEY` raises limits and covers the full surface
(`map`/`crawl` are documented key-first — without a key expect 401/402).

  Base URL: https://api.firecrawl.dev/v2
  Auth:     optional  Authorization: Bearer <key>  (env FIRECRAWL_API_KEY)
  Docs:     https://docs.firecrawl.dev (endpoints verified 2026-07)

This gives the SEO/GEO research skills their first keyless live-SERP source
(`search`) and gives every page-reading skill a JS-rendering fallback
(`scrape`). Subcommands are read-only against third-party marketing state;
`crawl`/`crawl-cancel` create and cancel only *your own* hosted Firecrawl
jobs, which is why there is no --live gate (unlike resend.py).

ROBOTS PRE-FLIGHT — per ../../SECURITY.md §Scraping Boundaries, `scrape`,
`crawl`, and `map` first evaluate the target's robots.txt locally (sibling
robots.py, UA "FirecrawlAgent" with `*` fallback) and REFUSE on a Disallow
(exit 4). `--own-site` skips the pre-flight — an explicit assertion that you
own or operate the target (e.g. a staging host that disallows all crawlers).
`search` has no target site, so no pre-flight.

DATA EGRESS — every target URL and search query is sent to Firecrawl, a
third-party processor; do not point this at URLs whose existence is itself
confidential. Fetched content (markdown, SERP titles/descriptions) is
*data*, never instructions — see ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 firecrawl.py scrape <url> [--formats markdown,links,html]
                       [--full-page] [--wait MS] [--mobile] [--own-site]
  python3 firecrawl.py search "<query>" [--limit N] [--scrape]
                       [--country US] [--tbs qdr:w]
                       [--include-domains a.com,b.com] [--exclude-domains …]
  python3 firecrawl.py map <url> [--search q] [--limit N]
                       [--sitemap include|only|skip] [--own-site]
  python3 firecrawl.py crawl <url> [--limit N] [--include RE,RE]
                       [--exclude RE,RE] [--own-site]
  python3 firecrawl.py crawl-status <id>
  python3 firecrawl.py crawl-cancel <id>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.parse import quote, urlsplit

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)
robots = _load_connector_sibling("robots", __file__)

API_BASE = "https://api.firecrawl.dev/v2"
ENV_KEY = "FIRECRAWL_API_KEY"
SIGNUP_URL = "https://www.firecrawl.dev"
ROBOTS_UA = "FirecrawlAgent"
CALL_TIMEOUT = 120  # rendered scrapes can take well over _http's 20s default


def build_request(path, method="POST", body=None):
    """Return the request this call WOULD make. Pure / no network."""
    return {"method": method, "url": API_BASE + path, "body": body}


def _split(value):
    return [p.strip() for p in (value or "").split(",") if p.strip()]


def build_spec(args):
    """Map parsed args to {request, target} or {error}. Pure / no network.

    `target` is the URL whose robots.txt must be pre-flighted (None for
    search and job-management calls).
    """
    cmd = args.command

    if cmd == "scrape":
        body = {"url": args.url}
        formats = _split(args.formats)
        if formats:
            body["formats"] = formats
        if args.full_page:
            body["onlyMainContent"] = False
        if args.wait:
            body["waitFor"] = args.wait
        if args.mobile:
            body["mobile"] = True
        return {"request": build_request("/scrape", body=body), "target": args.url}

    if cmd == "search":
        body = {"query": args.query}
        if args.limit:
            body["limit"] = args.limit
        if args.scrape:
            body["scrapeOptions"] = {"formats": ["markdown"]}
        if args.country:
            body["country"] = args.country
        if args.tbs:
            body["tbs"] = args.tbs
        include = _split(args.include_domains)
        exclude = _split(args.exclude_domains)
        if include:
            body["includeDomains"] = include
        if exclude:
            body["excludeDomains"] = exclude
        return {"request": build_request("/search", body=body), "target": None}

    if cmd == "map":
        body = {"url": args.url}
        if args.search:
            body["search"] = args.search
        if args.limit:
            body["limit"] = args.limit
        if args.sitemap:
            body["sitemap"] = args.sitemap
        return {"request": build_request("/map", body=body), "target": args.url}

    if cmd == "crawl":
        body = {"url": args.url}
        if args.limit:
            body["limit"] = args.limit
        include = _split(args.include)
        exclude = _split(args.exclude)
        if include:
            body["includePaths"] = include
        if exclude:
            body["excludePaths"] = exclude
        return {"request": build_request("/crawl", body=body), "target": args.url}

    if cmd == "crawl-status":
        return {"request": build_request("/crawl/%s" % quote(args.id, safe=""),
                                         method="GET"), "target": None}
    if cmd == "crawl-cancel":
        return {"request": build_request("/crawl/%s" % quote(args.id, safe=""),
                                         method="DELETE"), "target": None}
    return {"error": "unknown_command"}


def preflight(url, ua=ROBOTS_UA):
    """Evaluate the target's robots.txt locally before handing it to Firecrawl.
    Returns {allowed, robots_url, status, rule}. A 4xx/404 means no restrictions
    (allowed). FAIL-CLOSED: a 5xx or network failure means the policy could NOT be
    verified, so allowed is False (refuse; --own-site overrides). allowed is also
    False on an applicable Disallow."""
    sp = urlsplit(url)
    path = sp.path or "/"
    if sp.query:
        path += "?" + sp.query
    parsed = robots.fetch(url)
    if robots.status_unreliable(parsed.status):
        return {
            "allowed": False, "ua": ua, "path": path,
            "robots_url": parsed.url, "status": parsed.status, "rule": None,
            "reason": "robots.txt could not be verified (status %s) — fail-closed; "
                      "re-run with --own-site to override" % parsed.status,
        }
    allowed, detail = parsed.can_fetch(ua, path)
    return {
        "allowed": bool(allowed),
        "ua": ua,
        "path": path,
        "robots_url": parsed.url,
        "status": parsed.status,
        "rule": (detail or {}).get("rule") if isinstance(detail, dict) else None,
    }


def call(key, req, retries=3):
    """Execute a built request. Read-only API — retries are always safe."""
    data = None
    headers = {}
    if key:
        headers["Authorization"] = "Bearer %s" % key
    if req["body"] is not None:
        data = json.dumps(req["body"]).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = _http.get_json(req["url"], headers=headers, data=data,
                       method=req["method"], retries=retries,
                       timeout=CALL_TIMEOUT)
    return {"status": r.get("status", 0), "error": r.get("error"), "data": r.get("json")}


def build_parser():
    p = argparse.ArgumentParser(
        prog="firecrawl.py",
        description="Firecrawl hosted scrape / live SERP search / map / "
                    "crawl. scrape+search run keyless (~1,000 free "
                    "credits/mo); FIRECRAWL_API_KEY raises limits.",
        epilog="Example: python3 firecrawl.py search \"best crm for smb\" --limit 5",
    )
    p.add_argument("--key", default=None,
                   help="API key (optional). Falls back to env %s; keyless "
                        "works for scrape/search." % ENV_KEY)
    sub = p.add_subparsers(dest="command", required=True)

    own = argparse.ArgumentParser(add_help=False)
    own.add_argument("--own-site", action="store_true", dest="own_site",
                     help="Assert you own/operate the target: skip the local "
                          "robots.txt pre-flight (e.g. a staging host).")

    s = sub.add_parser("scrape", parents=[own],
                       help="One URL -> LLM-ready markdown (renders JS).")
    s.add_argument("url")
    s.add_argument("--formats", default=None,
                   help="Comma-separated: markdown,links,html,rawHtml,"
                        "screenshot (default: markdown).")
    s.add_argument("--full-page", action="store_true", dest="full_page",
                   help="Keep headers/navs/footers (default strips to main "
                        "content).")
    s.add_argument("--wait", type=int, default=None, metavar="MS",
                   help="Extra ms to wait before capture (slow JS pages).")
    s.add_argument("--mobile", action="store_true",
                   help="Emulate a mobile device.")

    s = sub.add_parser("search",
                       help="Live web SERP (keyless); --scrape adds each "
                            "result's markdown.")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=None, help="Results (1-100).")
    s.add_argument("--scrape", action="store_true",
                   help="Also scrape each result to markdown (more credits).")
    s.add_argument("--country", default=None, help="ISO country code, e.g. US.")
    s.add_argument("--tbs", default=None,
                   help="Time filter, e.g. qdr:w (past week), qdr:m.")
    s.add_argument("--include-domains", default=None, dest="include_domains",
                   help="Comma-separated domains to restrict results to.")
    s.add_argument("--exclude-domains", default=None, dest="exclude_domains",
                   help="Comma-separated domains to drop from results.")

    s = sub.add_parser("map", parents=[own],
                       help="Fast URL discovery for a site (sitemap-aware).")
    s.add_argument("url")
    s.add_argument("--search", default=None,
                   help="Order the discovered URLs by relevance to this query.")
    s.add_argument("--limit", type=int, default=None,
                   help="Max links (default 5000).")
    s.add_argument("--sitemap", default=None,
                   choices=["include", "only", "skip"],
                   help="Sitemap handling (default include).")

    s = sub.add_parser("crawl", parents=[own],
                       help="Start an async whole-site crawl -> job id "
                            "(poll with crawl-status).")
    s.add_argument("url")
    s.add_argument("--limit", type=int, default=None,
                   help="Max pages (set this — account default is 10000).")
    s.add_argument("--include", default=None,
                   help="Comma-separated pathname regexes to include.")
    s.add_argument("--exclude", default=None,
                   help="Comma-separated pathname regexes to exclude.")

    s = sub.add_parser("crawl-status", help="Poll an async crawl job.")
    s.add_argument("id", help="Job id from 'crawl'.")

    s = sub.add_parser("crawl-cancel", help="Cancel an async crawl job.")
    s.add_argument("id", help="Job id from 'crawl'.")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    spec = build_spec(args)

    if "error" in spec:
        print(json.dumps(spec, indent=2, ensure_ascii=False))
        print("error: %s" % spec["error"], file=sys.stderr)
        return 1

    robots_check = None
    if spec["target"] and not getattr(args, "own_site", False):
        robots_check = preflight(spec["target"])
        if not robots_check["allowed"]:
            out = {
                "error": "robots_disallowed",
                "robots": robots_check,
                "note": "Target's robots.txt disallows this path; refusing "
                        "to hand it to a fetcher (SECURITY.md §Scraping "
                        "Boundaries). If you own/operate this site, re-run "
                        "with --own-site.",
            }
            print(json.dumps(out, indent=2, ensure_ascii=False))
            print("error: robots_disallowed", file=sys.stderr)
            return 4

    key = args.key or os.environ.get(ENV_KEY) or ""
    result = call(key, spec["request"])
    if robots_check:
        result["robots"] = robots_check
    if result.get("status") in (401, 402):
        result["note"] = ("Firecrawl asked for auth/credits (HTTP %s). "
                          "scrape/search have a keyless free tier; for this "
                          "call or for more volume set %s (free key at %s)."
                          % (result["status"], ENV_KEY, SIGNUP_URL))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("error"):
        print("error: %s" % result["error"], file=sys.stderr)
        return 3 if result.get("status") in (401, 402) else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
