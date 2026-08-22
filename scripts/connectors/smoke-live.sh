#!/usr/bin/env bash
# smoke-live.sh — manual live smoke test for the bundled connectors.
#
# NOT run in CI (CI stays offline: tests/test_connectors_local.py covers the
# pure request-builders). Run this by hand before a release or when a vendor
# announcement suggests an API change — it makes one minimal real call per
# hosted connector listed below and asserts the response *shape*, so sampled endpoint drift
# (renamed fields, retired routes, auth changes) surfaces here instead of in
# a user's session.
#
#   bash scripts/connectors/smoke-live.sh
#
# Keyed connectors (resend, openpagerank) run only when their env key is set;
# rate-limit answers (GDELT shared-IP throttle, Tavily/Firecrawl keyless
# caps) count as SKIP, not FAIL — they prove the endpoint is alive.

set -u
cd "$(dirname "$0")"
PASS=0; FAIL=0; SKIP=0

check() { # <name> <python-assert reading stdin JSON> <cmd...>
  local name="$1" assert="$2"; shift 2
  local out rc
  out=$("$@" 2>/dev/null); rc=$?
  # Exit code 3 is the connectors' documented rate-limit / keyless-cap signal —
  # it proves the endpoint is alive, so it counts as SKIP, not FAIL (per header).
  if [ $rc -eq 3 ]; then
    skip "$name" "rate-limit / keyless cap (exit 3) — endpoint alive, retry later"
  elif [ $rc -eq 0 ] && printf '%s' "$out" | python3 -c "$assert" 2>/dev/null; then
    echo "PASS  $name"; PASS=$((PASS+1))
  else
    echo "FAIL  $name"; FAIL=$((FAIL+1))
  fi
}

skip() { echo "SKIP  $1 ($2)"; SKIP=$((SKIP+1)); }

echo "== live connector smoke ($(date -u +%Y-%m-%dT%H:%MZ)) =="

# --- keyless public APIs -----------------------------------------------------
check "doh.py auth" \
  'import json,sys; d=json.load(sys.stdin); assert d["spf"]["present"] and d["dmarc"]["present"]' \
  python3 doh.py auth gmail.com

check "pageviews.py" \
  'import json,sys; d=json.load(sys.stdin); assert d["points"] and d["total"] > 0' \
  python3 pageviews.py "Anthropic" --months 3

out=$(python3 gdelt.py '"google"' --days 2 --max 2 2>/dev/null); rc=$?
if [ $rc -eq 0 ]; then
  echo "PASS  gdelt.py"; PASS=$((PASS+1))
elif [ $rc -eq 3 ]; then
  skip "gdelt.py" "shared-IP throttle — endpoint alive, retry later"
else
  echo "FAIL  gdelt.py"; FAIL=$((FAIL+1))
fi

# psi keyless is slow and transport-flaky; only a completed-but-wrong response fails.
out=$(python3 psi.py https://example.com 2>/dev/null)
if printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d.get("ok")' 2>/dev/null; then
  echo "PASS  psi.py (keyless)"; PASS=$((PASS+1))
elif printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); e=str(d.get("error") or ""); assert any(t in e for t in ("SSL","timed out","timeout","EOF","429","reset"))' 2>/dev/null; then
  skip "psi.py (keyless)" "transport flake / keyless quota — endpoint alive"
else
  echo "FAIL  psi.py (keyless)"; FAIL=$((FAIL+1))
fi

check "kg.py reconcile" \
  'import json,sys; d=json.load(sys.stdin); assert d["query"] and d["matches"] and d["count"] == len(d["matches"])' \
  python3 kg.py reconcile "Anthropic"

check "hn.py search" \
  'import json,sys; d=json.load(sys.stdin); assert d["error"] is None and d["endpoint"] == "search" and d["hits"]' \
  python3 hn.py search "google" --tags story --max 3

check "appstore.py charts" \
  'import json,sys; d=json.load(sys.stdin); assert d and d[0]["rank"] == 1 and d[0]["id"] and d[0]["name"]' \
  python3 appstore.py charts --country us --max 10

# --- keyless social listening --------------------------------------------------
check "bluesky.py profile" \
  'import json,sys; d=json.load(sys.stdin); assert d["error"] is None and d["did"] and d["followers"] is not None' \
  python3 bluesky.py profile bsky.app

check "fediverse.py trends" \
  'import json,sys; d=json.load(sys.stdin); assert d["error"] is None and d["instance"]["version"] and isinstance(d["tags"], list)' \
  python3 fediverse.py trends --instance mastodon.social --max 3

check "discourse.py health" \
  'import json,sys; d=json.load(sys.stdin); assert d["error"] is None and d["about"]["users_count"] and d["about"]["title"]' \
  python3 discourse.py health https://meta.discourse.org --max 20

check "youtube.py rss (keyless)" \
  'import json,sys; d=json.load(sys.stdin); assert d["error"] is None and d["channel_id"] and d["video_count_in_feed"] > 0' \
  python3 youtube.py rss UC_x5XG1OV2P6uZZ5FSM9Ttw

# --- keyless hosted fetchers ---------------------------------------------------
check "firecrawl.py scrape" \
  'import json,sys; d=json.load(sys.stdin); assert d["status"]==200 and d["data"]["data"]["markdown"]' \
  python3 firecrawl.py scrape https://example.com

check "tavily.py search" \
  'import json,sys; d=json.load(sys.stdin); assert d["status"]==200 and d["data"]["results"]' \
  python3 tavily.py search "example domain documentation" --limit 2

# --- keyed connectors (conditional) -------------------------------------------
if [ -n "${RESEND_API_KEY:-}" ]; then
  check "resend.py domains" \
    'import json,sys; d=json.load(sys.stdin); assert d["status"]==200' \
    python3 resend.py domains
else
  skip "resend.py domains" "RESEND_API_KEY not set"
fi

if [ -n "${YOUTUBE_API_KEY:-}" ]; then
  check "youtube.py channel" \
    'import json,sys; d=json.load(sys.stdin); assert d.get("found") and d.get("subscribers_displayed")' \
    python3 youtube.py channel @youtube
else
  skip "youtube.py channel" "YOUTUBE_API_KEY not set"
fi

if [ -n "${PRODUCTHUNT_DEVELOPER_TOKEN:-}" ]; then
  check "producthunt.py daily" \
    'import json,sys; d=json.load(sys.stdin); assert d["date"] and d["count"] and d["posts"][0]["votesCount"] is not None and d["attribution"]' \
    python3 producthunt.py daily --max 3
else
  skip "producthunt.py daily" "PRODUCTHUNT_DEVELOPER_TOKEN not set"
fi

if [ -n "${XQUIK_API_KEY:-}" ]; then
  check "xquik.py listen" \
    'import json,sys; d=json.load(sys.stdin); assert d["error"] is None and d["count"] == 1 and d["queries"][0]["next_cursor"] is not None' \
    python3 xquik.py listen "open source marketing" --limit 1
else
  skip "xquik.py listen" "XQUIK_API_KEY not set"
fi

# indexpush is mutation-class: smoke only its dry-run (no network, no submission).
check "indexpush.py (dry-run)" \
  'import json,sys; d=json.load(sys.stdin); assert d["dry_run"] and d["request"]["body"]["host"]=="example.com"' \
  python3 indexpush.py indexnow https://example.com/a --key smoketestkey0

if [ -n "${OPENPAGERANK_API_KEY:-}" ]; then
  check "openpagerank.py" \
    'import json,sys; d=json.load(sys.stdin); assert d["results"]' \
    python3 openpagerank.py example.com
else
  skip "openpagerank.py" "OPENPAGERANK_API_KEY not set"
fi

echo "== $PASS pass · $FAIL fail · $SKIP skip =="
[ $FAIL -eq 0 ]
