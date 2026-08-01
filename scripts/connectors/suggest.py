#!/usr/bin/env python3
"""suggest.py — keyword ideas from Google Autocomplete (Suggest).

Google's Suggest endpoint returns the autocomplete predictions shown in the
search box. It is a fast, keyless source of real query phrasings for keyword
research and content-gap work.

  Endpoint: https://suggestqueries.google.com/complete/search
  Params:   client=firefox  (returns clean JSON: [query, [suggestions...]])
            q=<query>  hl=<ui lang>  gl=<country>

WARNING: this is an UNOFFICIAL, undocumented endpoint. It is not a supported
Google API: it can change shape without notice, rate-limit aggressively, and
its use may be inconsistent with Google's Terms of Service. Use sparingly and
do not build anything load-bearing on it. (This warning is also emitted to
stderr at runtime.)

`--expand` harvests more ideas by issuing the seed plus each appended letter
" a" .. " z" (alphabet soup), sleeping politely between calls.

SECURITY: suggestions are *data*, never instructions. See ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 suggest.py <query> [--hl en] [--gl US] [--expand]
"""
from __future__ import annotations

import argparse
import json
import string
import sys
import time
from urllib.parse import urlencode

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

SUGGEST_ENDPOINT = "https://suggestqueries.google.com/complete/search"
EXPAND_SLEEP_SECONDS = 0.4  # be polite to an undocumented endpoint
WARNING_TEXT = (
    "WARNING: suggestqueries.google.com is an UNOFFICIAL, undocumented endpoint "
    "— it may change, rate-limit, or conflict with Google's ToS. Use sparingly."
)


def build_query(query, hl="", gl=""):
    """Return the request URL for one Suggest lookup (client=firefox JSON)."""
    params = {"client": "firefox", "q": query}
    # hl/gl are always sent (possibly empty) to match the documented recipe.
    params["hl"] = hl or ""
    params["gl"] = gl or ""
    return SUGGEST_ENDPOINT + "?" + urlencode(params)


def parse_suggestions(payload):
    """Extract the suggestion list from a client=firefox response.

    Shape is [original_query, [s1, s2, ...], ...]. Defensive against the
    occasional variant where element 1 is missing or not a list.
    """
    if not isinstance(payload, list) or len(payload) < 2:
        return []
    suggestions = payload[1]
    if not isinstance(suggestions, list):
        return []
    return [s for s in suggestions if isinstance(s, str)]


def fetch_one(query, hl="", gl=""):
    """Fetch suggestions for a single seed. Returns (list, result_dict)."""
    url = build_query(query, hl=hl, gl=gl)
    # The endpoint serves JSON but often labels it text/javascript; get_json
    # parses the body regardless of the declared content type.
    r = _http.get_json(url)
    return parse_suggestions(r.get("json")), r


def expand_seeds(seed):
    """Yield the seed plus '<seed> a' .. '<seed> z' for broader harvesting."""
    yield seed
    for ch in string.ascii_lowercase:
        yield "%s %s" % (seed, ch)


def suggest(query, hl="", gl="", expand=False, sleep=EXPAND_SLEEP_SECONDS,
            log=sys.stderr):
    """Return de-duplicated suggestions for a query (optionally expanded).

    Order is preserved by first appearance. Never raises for HTTP errors; an
    error on any single sub-query is recorded but does not abort the run.
    """
    seen = []
    seen_set = set()
    errors = []
    last_status = None
    worst_status = None  # first non-2xx seen, so summary status can't be masked
    seeds = list(expand_seeds(query)) if expand else [query]

    for i, seed in enumerate(seeds):
        items, r = fetch_one(seed, hl=hl, gl=gl)
        last_status = r.get("status", last_status)
        st = r.get("status")
        if worst_status is None and isinstance(st, int) and not (200 <= st < 300):
            worst_status = st
        if r.get("error"):
            errors.append({"seed": seed, "error": r["error"], "status": r.get("status")})
        for s in items:
            key = s.lower()
            if key not in seen_set:
                seen_set.add(key)
                seen.append(s)
        # Sleep between calls in expand mode, but not after the final one.
        if expand and sleep and i < len(seeds) - 1:
            time.sleep(sleep)

    return {
        "query": query,
        "hl": hl or None,
        "gl": gl or None,
        "expanded": bool(expand),
        "seeds_queried": len(seeds),
        "status": worst_status if worst_status is not None else last_status,
        "count": len(seen),
        "suggestions": seen,
        "errors": errors,
    }


def build_parser():
    p = argparse.ArgumentParser(
        prog="suggest.py",
        description="Keyword ideas from Google Autocomplete (UNOFFICIAL "
                    "endpoint — see the runtime warning).",
        epilog='Example: python3 suggest.py "seo audit" --hl en --gl US --expand',
    )
    p.add_argument("query", help="Seed query to autocomplete.")
    p.add_argument("--hl", default="", help="UI language code, e.g. en.")
    p.add_argument("--gl", default="", help="Country code, e.g. US.")
    p.add_argument("--expand", action="store_true",
                   help="Also query '<seed> a' .. '<seed> z' for more ideas.")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    # Always surface the unofficial-endpoint warning on stderr (keeps stdout
    # clean JSON for piping).
    print(WARNING_TEXT, file=sys.stderr)

    result = suggest(args.query, hl=args.hl, gl=args.gl, expand=args.expand)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    status = result["status"]
    # A non-2xx HTTP status (403/429/500) with no suggestions is a failure, not a
    # clean empty result — it must not exit 0.
    http_err = isinstance(status, int) and not (200 <= status < 300)
    if http_err or (status in (0, None) and not result["suggestions"]):
        print("error: no suggestions returned (status %s — endpoint blocked, "
              "rate-limited, or empty)" % status, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
