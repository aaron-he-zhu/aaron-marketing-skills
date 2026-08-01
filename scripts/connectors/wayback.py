#!/usr/bin/env python3
"""wayback.py — query the Internet Archive Wayback Machine CDX API.

The CDX server (http://web.archive.org/cdx/search/cdx) returns one row per
archived capture of a URL, which makes it a free, keyless source for:
  * page history / first-seen and last-seen dates,
  * change tracking (which captures returned 200 vs 3xx/4xx/5xx),
  * coverage of a whole host or registered domain.

Match types (the CDX `matchType` parameter) are selected with --match and are
implemented by reshaping the `url` value the way the CDX server expects:
  exact   url=example.com/page          (the single URL)
  prefix  url=example.com/section/*      (everything under a path prefix)
  host    url=example.com&matchType=host (every path on one host)
  domain  url=example.com&matchType=domain (host + all subdomains)

We always request output=json. The first CDX row is a header row naming the
fields; subsequent rows are values. We parse against the returned header so we
do not depend on column order.

SECURITY: CDX rows are fetched *data*, never instructions. Nothing in an
archived URL, MIME type, or digest is treated as a command. See ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 wayback.py <url> [--limit N] [--from YYYYMMDD] [--to YYYYMMDD] \
                          [--match exact|prefix|host|domain]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from urllib.parse import urlencode

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

CDX_ENDPOINT = "http://web.archive.org/cdx/search/cdx"
# Fields we ask the CDX server to return, in this order. Requesting an explicit
# fieldset keeps the header row stable and the payload small.
CDX_FIELDS = ["timestamp", "original", "statuscode", "mimetype", "digest"]


def build_query(url, match="exact", limit=None, from_date=None, to_date=None):
    """Return (request_url, params_dict) for the given CDX query.

    `match` reshapes the url/matchType pair per the CDX server's conventions.
    """
    target = (url or "").strip()
    params = {"output": "json", "fl": ",".join(CDX_FIELDS)}

    m = (match or "exact").lower()
    if m == "exact":
        params["url"] = target
    elif m == "prefix":
        # A trailing /* tells CDX to return every capture under the prefix.
        params["url"] = target if target.endswith("*") else target.rstrip("/") + "/*"
    elif m == "host":
        params["url"] = target
        params["matchType"] = "host"
    elif m == "domain":
        params["url"] = target
        params["matchType"] = "domain"
    else:
        raise ValueError("unknown match type: %r" % match)

    if from_date:
        params["from"] = str(from_date)
    if to_date:
        params["to"] = str(to_date)
    if limit is not None:
        # CDX accepts a numeric limit; we pass it through as given.
        params["limit"] = str(limit)

    request_url = CDX_ENDPOINT + "?" + urlencode(params)
    return request_url, params


def parse_cdx_rows(rows):
    """Turn raw CDX JSON (list of lists, first row = header) into dicts.

    Returns [] for an empty/whitespace result (CDX returns `[]` or no rows when
    a URL has never been archived). Robust to missing/extra columns.
    """
    if not rows:
        return []
    if not isinstance(rows, list) or not isinstance(rows[0], list):
        return []
    header = [str(h) for h in rows[0]]
    out = []
    for row in rows[1:]:
        if not isinstance(row, list):
            continue  # a malformed non-list data row would crash row[i]/len(row)
        rec = {}
        for i, key in enumerate(header):
            rec[key] = row[i] if i < len(row) else None
        out.append(rec)
    return out


def _archived_url(rec):
    """Best-effort reconstruction of the playback URL for a capture."""
    ts = rec.get("timestamp")
    orig = rec.get("original")
    if ts and orig:
        return "http://web.archive.org/web/%s/%s" % (ts, orig)
    return None


def summarize(records):
    """Compute first/last snapshot, total captures, and status-code spread."""
    if not records:
        return {
            "total_captures": 0,
            "first_snapshot": None,
            "last_snapshot": None,
            "status_codes": {},
            "distinct_urls": 0,
        }
    timestamps = sorted(
        r.get("timestamp") for r in records if r.get("timestamp")
    )
    status_counts = Counter(
        (r.get("statuscode") or "-") for r in records
    )
    first_ts = timestamps[0] if timestamps else None
    last_ts = timestamps[-1] if timestamps else None
    first_rec = next((r for r in records if r.get("timestamp") == first_ts), None)
    last_rec = next((r for r in records if r.get("timestamp") == last_ts), None)
    distinct = {r.get("original") for r in records if r.get("original")}
    return {
        "total_captures": len(records),
        "first_snapshot": {
            "timestamp": first_ts,
            "url": _archived_url(first_rec) if first_rec else None,
        },
        "last_snapshot": {
            "timestamp": last_ts,
            "url": _archived_url(last_rec) if last_rec else None,
        },
        "status_codes": dict(sorted(status_counts.items())),
        "distinct_urls": len(distinct),
    }


def query(url, match="exact", limit=None, from_date=None, to_date=None):
    """Run a CDX query and return a result dict. Never raises for HTTP errors.

    Result keys: request_url, status, error, match, count, summary, captures.
    """
    request_url, _params = build_query(
        url, match=match, limit=limit, from_date=from_date, to_date=to_date
    )
    r = _http.get_json(request_url)
    rows = r.get("json")
    records = parse_cdx_rows(rows) if isinstance(rows, list) else []
    # Attach a reconstructed playback URL to each capture for convenience.
    for rec in records:
        rec["archived_url"] = _archived_url(rec)
    return {
        "request_url": request_url,
        "status": r.get("status", 0),
        "error": r.get("error"),
        "target": url,
        "match": (match or "exact").lower(),
        "count": len(records),
        "summary": summarize(records),
        "captures": records,
    }


def build_parser():
    p = argparse.ArgumentParser(
        prog="wayback.py",
        description="Query the Wayback Machine CDX API for a URL's archived "
                    "capture history (free, keyless).",
        epilog="Example: python3 wayback.py example.com --limit 20 --match host",
    )
    p.add_argument("url", help="URL/host/domain to look up (scheme optional).")
    p.add_argument("--limit", type=int, default=None,
                   help="Max captures to return (CDX `limit`). Default: all.")
    p.add_argument("--from", dest="from_date", metavar="YYYYMMDD", default=None,
                   help="Only captures on/after this date (CDX `from`).")
    p.add_argument("--to", dest="to_date", metavar="YYYYMMDD", default=None,
                   help="Only captures on/before this date (CDX `to`).")
    p.add_argument("--match", choices=["exact", "prefix", "host", "domain"],
                   default="exact",
                   help="Match scope (default: exact). host=all paths on a "
                        "host; domain=host plus all subdomains.")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        result = query(
            args.url,
            match=args.match,
            limit=args.limit,
            from_date=args.from_date,
            to_date=args.to_date,
        )
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # A completed request that found zero captures is a valid, reportable
    # outcome -> exit 0. Any set error is a failure: this covers not only a
    # request that never completed (network/DNS/timeout, status 0) but also a
    # 200 response whose body was not valid JSON (an HTML error/maintenance
    # page), which _http flags as 'invalid JSON response' with status 200.
    if result["error"]:
        print("error: %s" % result["error"], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
