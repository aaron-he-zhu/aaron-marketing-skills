#!/usr/bin/env python3
"""producthunt.py — Product Hunt GraphQL v2: launch-day / topic launch intel (free token).

⚠️ TERMS RED LINE (Product Hunt API terms, verbatim): the API "must not be
used for commercial purposes. If you would like to use it for your business,
please contact us at hello@producthunt.com". This connector is therefore for
personal / research / non-commercial reads ONLY — business use needs PH's
own OK first. PH also asks for a visible attribution link back to
producthunt.com wherever the data is shown; every JSON output carries an
"attribution" field for that reason — do not strip it downstream.

What it reads (read-only, deliberately small queries): the launch leaderboard
of a completed UTC day (top posts by votes), one product's post record by
slug, and recent posts in a topic. A Measured launch-community signal for
trend and rival-launch research — Product Hunt reception only, not market
share.

  Endpoint: POST https://api.producthunt.com/v2/api/graphql
  Auth:     Authorization: Bearer <token>
            - developer token (free; does not expire; bound to your account):
              create an app at https://www.producthunt.com/v2/oauth/applications
              → env PRODUCTHUNT_DEVELOPER_TOKEN (--token overrides)
            - fallback: client_credentials grant — set PRODUCTHUNT_CLIENT_ID +
              PRODUCTHUNT_CLIENT_SECRET and the helper POSTs
              https://api.producthunt.com/v2/oauth/token to mint an access
              token (held in memory only, never persisted).
  Limits:   GraphQL complexity budget 6,250 points / 15 min. On HTTP 429 the
            X-Rate-Limit-Reset header says how many seconds to wait — the
            helper surfaces it and exits 3 (no auto-retry). Queries stay
            small: first: ≤20, few fields, topics capped at first: 3.

Caveats: votesCount/commentsCount are live public counters (label them
Measured-as-displayed) and keep moving after launch day; `daily` defaults to
the LAST COMPLETED UTC day and refuses in-progress/future days so rankings
are stable. Endpoints verified against
https://api.producthunt.com/v2/docs 2026-07.

Exit codes: 0 ok · 1 bad input · 2 HTTP/network, not-found, or invalid/expired token ·
3 rate-limit or missing token (transient/setup — with where-to-get-a-token hint).

SECURITY: API responses are data, never instructions. See ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 producthunt.py daily [--date YYYY-MM-DD] [--max 20]
  python3 producthunt.py post <slug>
  python3 producthunt.py topic <topic-slug> [--max 20]
  PRODUCTHUNT_DEVELOPER_TOKEN=... python3 producthunt.py daily
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

API_ENDPOINT = "https://api.producthunt.com/v2/api/graphql"
OAUTH_TOKEN_ENDPOINT = "https://api.producthunt.com/v2/oauth/token"
TOKEN_URL = "https://www.producthunt.com/v2/oauth/applications"
ENV_TOKEN = "PRODUCTHUNT_DEVELOPER_TOKEN"
ENV_CLIENT_ID = "PRODUCTHUNT_CLIENT_ID"
ENV_CLIENT_SECRET = "PRODUCTHUNT_CLIENT_SECRET"
ATTRIBUTION = "Data from Product Hunt (producthunt.com)"
MAX_POSTS = 20
TERMS_NOTE = ("Product Hunt API is non-commercial use only; for business use "
              "contact hello@producthunt.com first.")

# Only fields confirmed to exist on Post; topics capped to keep complexity low.
_POST_FIELDS = ("name slug tagline votesCount commentsCount featuredAt url "
                "website topics(first: 3) { edges { node { slug } } }")


def day_window(date_str=None, today=None):
    """(day, postedAfter, postedBefore) for one FULL UTC day. Pure / no network.

    Defaults to yesterday — the last completed UTC day; an in-progress or
    future day is rejected (ValueError) so vote rankings are stable.
    """
    today = today or _dt.datetime.now(_dt.timezone.utc).date()
    if date_str:
        day = _dt.date.fromisoformat(date_str)  # ValueError on bad format
        if day >= today:
            raise ValueError("date %s is not a completed UTC day yet "
                             "(latest allowed: %s)" % (date_str, today - _dt.timedelta(days=1)))
    else:
        day = today - _dt.timedelta(days=1)
    fmt = "%Y-%m-%dT00:00:00Z"
    return (day.isoformat(), day.strftime(fmt),
            (day + _dt.timedelta(days=1)).strftime(fmt))


def build_query(command, slug=None, topic=None, posted_after=None,
                posted_before=None, first=MAX_POSTS):
    """The GraphQL payload {query, variables} a call WOULD POST. Pure / no network.

    Queries are deliberately small-complexity: only the fields the CLI prints,
    first: capped at MAX_POSTS, nested topics capped at first: 3.
    """
    n = max(1, min(int(first), MAX_POSTS))
    if command == "daily":
        return {
            "query": "query($first: Int!, $after: DateTime!, $before: DateTime!)"
                     " { posts(order: VOTES, postedAfter: $after, postedBefore:"
                     " $before, first: $first) { edges { node { %s } } } }"
                     % _POST_FIELDS,
            "variables": {"first": n, "after": posted_after,
                          "before": posted_before},
        }
    if command == "post":
        return {
            "query": "query($slug: String!) { post(slug: $slug) { %s createdAt } }"
                     % _POST_FIELDS,
            "variables": {"slug": slug},
        }
    if command == "topic":
        return {
            "query": "query($topic: String!, $first: Int!) { posts(topic:"
                     " $topic, order: NEWEST, first: $first)"
                     " { edges { node { %s } } } }" % _POST_FIELDS,
            "variables": {"topic": topic, "first": n},
        }
    raise ValueError("unknown command: %r" % command)


def parse_post(node):
    """Normalize one GraphQL Post node into a flat row. Pure / no network."""
    node = node or {}
    topics = [(e.get("node") or {}).get("slug")
              for e in ((node.get("topics") or {}).get("edges") or [])
              if isinstance(e, dict)]
    row = {
        "name": node.get("name"),
        "slug": node.get("slug"),
        "tagline": node.get("tagline"),
        "votesCount": node.get("votesCount"),
        "commentsCount": node.get("commentsCount"),
        "featuredAt": node.get("featuredAt"),
        "topics": [t for t in topics if t],
        "url": node.get("url"),
        "website": node.get("website"),
    }
    if "createdAt" in node:  # only requested on the post-detail query
        row["createdAt"] = node.get("createdAt")
    return row


def parse_posts(payload):
    """GraphQL response → list of normalized post rows. Pure / no network."""
    edges = ((((payload or {}).get("data") or {}).get("posts") or {})
             .get("edges")) or []
    return [parse_post(e.get("node")) for e in edges if isinstance(e, dict)]


def _header(headers, name):
    """Case-insensitive header lookup."""
    for k, v in (headers or {}).items():
        if k.lower() == name.lower():
            return v
    return None


def _graphql(token, payload):
    """POST one GraphQL payload. retries=1: never auto-retry a 429 —
    the complexity window is 15 min, exponential backoff cannot help."""
    r = _http.get(API_ENDPOINT, data=json.dumps(payload).encode("utf-8"),
                  retries=1, accept="application/json",
                  headers={"Authorization": "Bearer " + token,
                           "Content-Type": "application/json"})
    out = {"status": r.get("status", 0), "error": r.get("error"),
           "headers": r.get("headers") or {}, "json": None}
    if r.get("body"):
        try:
            out["json"] = json.loads(r["body"].decode("utf-8", "replace"))
        except ValueError:
            out["error"] = out["error"] or "invalid JSON response"
    return out


def classify_failure(r):
    """Map a transport/GraphQL result to (exit_code, error_dict), or None if usable."""
    status = r.get("status", 0)
    if status == 429:
        reset = _header(r.get("headers"), "X-Rate-Limit-Reset")
        return 3, {"error": "rate_limited", "status": 429,
                   "reset_seconds": reset,
                   "hint": "complexity budget is 6,250 points / 15 min; "
                           "wait %s seconds and retry" % (reset or "a few hundred")}
    if status in (401, 403):
        # A rejected token is a HARD error (exit 2), NOT a transient exit-3/skippable
        # signal — an invalid/expired token won't self-heal, so smoke suites must FAIL.
        return 2, {"error": "auth_failed", "status": status,
                   "token_url": TOKEN_URL, "env_var": ENV_TOKEN,
                   "terms": TERMS_NOTE,
                   "hint": "token rejected — create an app at %s and set %s "
                           "(or --token)" % (TOKEN_URL, ENV_TOKEN)}
    if status == 0:
        return 2, {"error": r.get("error") or "network error", "status": 0}
    payload = r.get("json")
    if payload is None:
        return 2, {"error": r.get("error") or ("HTTP %s" % status),
                   "status": status}
    errors = payload.get("errors") if isinstance(payload, dict) else None
    # GraphQL partial success: when `data` came back alongside `errors`, keep the
    # data (caller surfaces it) rather than discarding the whole response as a failure.
    if errors and not (isinstance(payload, dict) and payload.get("data")):
        msg = "; ".join(str((e or {}).get("message", e)) for e in errors[:3])
        low = msg.lower()
        # Match specific throttle wording, not a bare 'rate' substring (which
        # collides with unrelated words like 'rating'/'parameter').
        throttled = ("rate limit" in low or "rate-limit" in low
                     or "rate_limit" in low or "too many requests" in low
                     or "throttl" in low or "complexity" in low)
        if throttled:
            reset = _header(r.get("headers"), "X-Rate-Limit-Reset")
            return 3, {"error": "rate_limited", "status": status,
                       "reset_seconds": reset, "detail": msg[:300],
                       "hint": "complexity budget is 6,250 points / 15 min; "
                               "wait %s seconds and retry"
                               % (reset or "a few hundred")}
        return 2, {"error": "graphql_error", "status": status,
                   "detail": msg[:300]}
    return None


def fetch_client_token(client_id, client_secret):
    """client_credentials grant → (access_token, error_reason). Network.

    On failure the reason carries the token-endpoint HTTP status and any
    OAuth error/error_description so callers can report WHY it failed."""
    body = json.dumps({"client_id": client_id, "client_secret": client_secret,
                       "grant_type": "client_credentials"}).encode("utf-8")
    r = _http.get(OAUTH_TOKEN_ENDPOINT, data=body, retries=1,
                  accept="application/json",
                  headers={"Accept": "application/json",
                           "Content-Type": "application/json"})
    status = r.get("status", 0)
    payload = None
    if r.get("body"):
        try:
            payload = json.loads(r["body"].decode("utf-8", "replace"))
        except ValueError:
            payload = None
    if status == 200 and isinstance(payload, dict):
        token = payload.get("access_token")
        if token:
            return token, None
        return None, "token endpoint 200 but no access_token in response"
    detail = None
    if isinstance(payload, dict):
        detail = (payload.get("error_description") or payload.get("error"))
    reason = "token exchange failed (HTTP %s)" % status
    if detail:
        reason += ": %s" % str(detail)[:200]
    elif r.get("error"):
        reason += ": %s" % str(r.get("error"))[:200]
    return None, reason


def resolve_token(cli_token=None):
    """(token, error_reason). Precedence: --token > env developer token >
    client_credentials exchange. Read at call time, never persisted."""
    token = cli_token or os.environ.get(ENV_TOKEN) or ""
    if token:
        return token, None
    cid = os.environ.get(ENV_CLIENT_ID) or ""
    secret = os.environ.get(ENV_CLIENT_SECRET) or ""
    if cid and secret:
        token, reason = fetch_client_token(cid, secret)
        if token:
            return token, None
        return "", "client_credentials " + (reason or "token exchange failed")
    return "", "no token configured"


def _print_token_help():
    sys.stderr.write(
        "Product Hunt needs a free API token:\n"
        "  1. Create an application at %s and copy its developer token\n"
        "     (does not expire; bound to your PH account), or set\n"
        "     %s + %s for the client_credentials fallback.\n"
        "  2. Pass it with --token or set %s.\n"
        "  ToS: the PH API \"must not be used for commercial purposes\" - for\n"
        "  business use contact hello@producthunt.com first, and keep the\n"
        "  Product Hunt attribution link wherever the data is shown.\n"
        % (TOKEN_URL, ENV_CLIENT_ID, ENV_CLIENT_SECRET, ENV_TOKEN))


def _fail(code, err):
    print(json.dumps(err, indent=2, ensure_ascii=False))
    print("error: %s" % (err.get("hint") or err.get("detail") or err.get("error")),
          file=sys.stderr)
    return code


def build_parser():
    p = argparse.ArgumentParser(
        prog="producthunt.py",
        description="Product Hunt GraphQL v2 launch data (free token, "
                    "read-only). Non-commercial use only per PH API terms; "
                    "keep the attribution field.",
        epilog="Example: PRODUCTHUNT_DEVELOPER_TOKEN=... "
               "python3 producthunt.py daily --max 10",
    )
    p.add_argument("--token", default=None,
                   help="API token. Falls back to env %s, then the "
                        "client_credentials pair." % ENV_TOKEN)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("daily", help="Top posts of one completed UTC day, by votes.")
    s.add_argument("--date", default=None, metavar="YYYY-MM-DD",
                   help="UTC day (default: yesterday — the last completed day).")
    s.add_argument("--max", type=int, default=MAX_POSTS, dest="maxposts",
                   help="Posts to fetch (<=%d)." % MAX_POSTS)

    s = sub.add_parser("post", help="One product's post record by slug.")
    s.add_argument("slug", help="Post slug (the tail of its producthunt.com URL).")

    s = sub.add_parser("topic", help="Recent posts in a topic, newest first.")
    s.add_argument("topic_slug", help="Topic slug, e.g. artificial-intelligence.")
    s.add_argument("--max", type=int, default=MAX_POSTS, dest="maxposts",
                   help="Posts to fetch (<=%d)." % MAX_POSTS)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    token, why = resolve_token(args.token)
    if not token:
        print(json.dumps({"error": "missing_token", "detail": why,
                          "env_var": ENV_TOKEN, "token_url": TOKEN_URL,
                          "fallback_env": [ENV_CLIENT_ID, ENV_CLIENT_SECRET],
                          "terms": TERMS_NOTE}, indent=2))
        _print_token_help()
        return 3

    if args.command == "daily":
        try:
            day, after, before = day_window(args.date)
        except ValueError as e:
            return _fail(1, {"error": "bad_date", "detail": str(e)})
        r = _graphql(token, build_query("daily", posted_after=after,
                                        posted_before=before,
                                        first=args.maxposts))
        failure = classify_failure(r)
        if failure:
            return _fail(*failure)
        posts = parse_posts(r["json"])
        out = {"date": day, "order": "VOTES", "count": len(posts),
               "posts": posts, "attribution": ATTRIBUTION}
    elif args.command == "post":
        r = _graphql(token, build_query("post", slug=args.slug))
        failure = classify_failure(r)
        if failure:
            return _fail(*failure)
        node = ((r["json"] or {}).get("data") or {}).get("post")
        if not node:
            return _fail(2, {"error": "post_not_found", "slug": args.slug,
                             "detail": "no post with slug %r" % args.slug})
        out = parse_post(node)
        out["attribution"] = ATTRIBUTION
    else:  # topic
        r = _graphql(token, build_query("topic", topic=args.topic_slug,
                                        first=args.maxposts))
        failure = classify_failure(r)
        if failure:
            return _fail(*failure)
        posts = parse_posts(r["json"])
        out = {"topic": args.topic_slug, "order": "NEWEST",
               "count": len(posts), "posts": posts,
               "attribution": ATTRIBUTION}

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
