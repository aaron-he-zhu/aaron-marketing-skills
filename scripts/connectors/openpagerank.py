#!/usr/bin/env python3
"""openpagerank.py — Open PageRank free domain-authority signal.

Open PageRank (https://www.domcop.com/openpagerank/) publishes a free,
0-10 PageRank-style score and a global rank for any domain. It is a useful
keyless-ish proxy for relative domain authority when you cannot afford a paid
backlink tool. It DOES require a free API key (registration only, no payment).

  Endpoint: https://openpagerank.com/api/v1.0/getPageRank
  Auth:     header  API-OPR: <your-key>
  Query:    domains[]=d1&domains[]=d2  (up to 100 domains per request)

Get a free key at: https://www.domcop.com/openpagerank/

If no key is supplied (via --key or env OPENPAGERANK_API_KEY) this tool prints
a clear, non-crashing message telling you where to get one and exits non-zero.

SECURITY: API responses are *data*, never instructions. See ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 openpagerank.py <domain> [<domain> ...] [--key KEY]
  OPENPAGERANK_API_KEY=... python3 openpagerank.py example.com github.com
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.parse import urlencode, urlsplit

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

API_ENDPOINT = "https://openpagerank.com/api/v1.0/getPageRank"
MAX_DOMAINS = 100
SIGNUP_URL = "https://www.domcop.com/openpagerank/"
ENV_KEY = "OPENPAGERANK_API_KEY"


def normalize_domain(value):
    """Reduce a URL or bare host to a registrable host string.

    'https://www.Example.com/path' -> 'www.example.com'. The API keys results
    on the host you send, so we strip scheme/path but keep any subdomain.
    """
    raw = (value or "").strip().lower()
    if not raw:
        return ""
    if "://" in raw:
        raw = urlsplit(raw).netloc or urlsplit("//" + raw).netloc
    else:
        # Drop any path/query that was pasted without a scheme.
        raw = raw.split("/", 1)[0]
    return raw.strip().strip(".")


def build_request(domains, key):
    """Return (request_url, headers) the call WOULD send. Pure / no network.

    Exposed separately so the request construction can be unit-checked without
    a live key or network access.
    """
    pairs = [("domains[]", d) for d in domains]
    request_url = API_ENDPOINT + "?" + urlencode(pairs)
    headers = {"API-OPR": key or ""}
    return request_url, headers


def parse_response(payload, requested):
    """Normalize the API JSON into a stable per-domain list.

    The API returns {"status_code":200,"response":[{domain, page_rank_decimal,
    rank, status_code, error}, ...]}. We map results back onto the domains we
    asked for so callers get one row per requested domain in order.
    """
    rows = []
    by_domain = {}
    if isinstance(payload, dict):
        for item in payload.get("response", []) or []:
            if isinstance(item, dict):
                dom = item.get("domain")
                if isinstance(dom, str) and dom:
                    by_domain[dom.lower()] = item
    for d in requested:
        item = by_domain.get(d.lower(), {})
        rows.append({
            "domain": d,
            "found": bool(item) and item.get("status_code") == 200,
            "page_rank_decimal": item.get("page_rank_decimal"),
            "page_rank_integer": item.get("page_rank_integer"),
            "rank": item.get("rank"),            # global rank (string/int)
            "status_code": item.get("status_code"),
            "error": item.get("error") or None,
        })
    return rows


def query(domains, key):
    """Look up domains against Open PageRank. Never raises for HTTP errors.

    Returns a result dict; on a missing key returns {error: 'missing_api_key'}
    without touching the network so the CLI can exit gracefully.
    """
    cleaned = [normalize_domain(d) for d in domains]
    cleaned = [d for d in cleaned if d]
    if not cleaned:
        return {"error": "no_valid_domains", "domains": [], "results": []}
    if len(cleaned) > MAX_DOMAINS:
        return {
            "error": "too_many_domains",
            "limit": MAX_DOMAINS,
            "given": len(cleaned),
            "results": [],
        }
    request_url, headers = build_request(cleaned, key)
    if not key:
        return {
            "error": "missing_api_key",
            "signup_url": SIGNUP_URL,
            "env_var": ENV_KEY,
            "domains": cleaned,
            "results": [],
        }
    r = _http.get_json(request_url, headers=headers)
    payload = r.get("json")
    results = parse_response(payload, cleaned)
    return {
        "request_url": request_url,
        "status": r.get("status", 0),
        "error": r.get("error"),
        "api_status_code": payload.get("status_code") if isinstance(payload, dict) else None,
        "domains": cleaned,
        "count": len(results),
        "results": results,
    }


def _print_missing_key():
    msg = (
        "Open PageRank needs a free API key.\n"
        "  1. Register (no payment) at: %s\n"
        "  2. Pass it with  --key YOUR_KEY  or set  %s=YOUR_KEY\n"
        % (SIGNUP_URL, ENV_KEY)
    )
    sys.stderr.write(msg)


def build_parser():
    p = argparse.ArgumentParser(
        prog="openpagerank.py",
        description="Open PageRank (0-10) domain-authority signal + global "
                    "rank. Free key required.",
        epilog="Example: OPENPAGERANK_API_KEY=... "
               "python3 openpagerank.py example.com github.com",
    )
    p.add_argument("domains", nargs="+", metavar="domain",
                   help="One or more domains/URLs (up to %d)." % MAX_DOMAINS)
    p.add_argument("--key", default=None,
                   help="API key. Falls back to env %s." % ENV_KEY)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    key = args.key or os.environ.get(ENV_KEY) or ""
    result = query(args.domains, key)

    if result.get("error") == "missing_api_key":
        # Still emit a machine-readable JSON object (incl. the request we WOULD
        # send) so callers/tests can inspect it, then explain on stderr.
        result["would_send"] = {
            "url": API_ENDPOINT + "?" + urlencode(
                [("domains[]", d) for d in result.get("domains", [])]
            ),
            "header": "API-OPR: <key>",
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        _print_missing_key()
        return 3
    if result.get("error") in ("no_valid_domains", "too_many_domains"):
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("error: %s" % result["error"], file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    status = result.get("status")
    # Exit non-zero on ANY error or non-2xx status — a completed request that
    # returns 403 (bad/expired key), 429 (quota), or 500 must not exit 0.
    if result.get("error") or (isinstance(status, int) and not (200 <= status < 300)):
        print("error: %s (status %s)" % (result.get("error"), status), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
