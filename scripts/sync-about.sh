#!/usr/bin/env bash
# sync-about.sh — verify (and, with --live, push) the GitHub repo "About" from its SSOT.
#
# The GitHub repo About (sidebar description + topics) is NOT a file in the repo, so it is
# invisible to the 8-file version contract and to check-versions.sh's file scan — which is
# exactly why it silently went stale on the v13 and v14 discipline bumps. This makes it a
# first-class tracked surface:
#   .github/repo-about.json         — the SSOT (edit this when the counts change)
#   scripts/sync-about.sh (here)    — projects the SSOT onto GitHub
#   scripts/check-versions.sh §4    — asserts the SSOT's skill count matches the tree (offline)
#   .github/workflows/about-drift.yml — weekly read-only sentinel: fails red if GitHub drifts
#
# Editing repo metadata needs ADMIN on the repo, which the CI GITHUB_TOKEN cannot hold — so,
# exactly like sync-family.sh, this is OWNER-RUN at release time (uses your own `gh` auth),
# and CI only runs the read-only dry-run to make drift loud.
#
# Usage:
#   bash scripts/sync-about.sh          # dry-run: compare live GitHub About to the SSOT; exit 1 on drift
#   bash scripts/sync-about.sh --live   # PATCH description + PUT topics from the SSOT (needs admin auth)
#
# Owner-run at release time (CONTRIBUTING §6). Python 3 stdlib for JSON parsing (repo dep policy);
# gh for the API calls.

set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"
source scripts/publish-common.sh

REPO="${GITHUB_REPOSITORY:-aaron-he-zhu/aaron-marketing-skills}"
SOURCE_ROOT="."
SSOT=""
LIVE=0
[ "${1:-}" = "--live" ] && LIVE=1

if [ "$LIVE" -eq 1 ]; then
  BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/aaron-about-sync.XXXXXX")" || {
    echo "sync-about: cannot create a private release source directory" >&2
    exit 1
  }
  trap '[ -n "${BUILD_ROOT:-}" ] && rm -rf -- "$BUILD_ROOT"' EXIT
  SOURCE_ROOT="$BUILD_ROOT/source"
  RELEASE_IDENTITY="$(publish_prepare_release_source "$SOURCE_ROOT")" || exit 1
  SOURCE_REPO="${RELEASE_IDENTITY%%$'\t'*}"
  SOURCE_COMMIT="${RELEASE_IDENTITY#*$'\t'}"
  [ "$SOURCE_REPO" = "$REPO" ] || {
    echo "sync-about: live target $REPO does not match origin source $SOURCE_REPO" >&2
    exit 1
  }
  echo "sync-about provenance: $SOURCE_REPO@$SOURCE_COMMIT (pinned commit export)"
fi
SSOT="$SOURCE_ROOT/.github/repo-about.json"

command -v gh >/dev/null 2>&1 || { echo "sync-about: 'gh' CLI not found — install it or run in CI" >&2; exit 2; }
[ -f "$SSOT" ] || { echo "sync-about: missing $SSOT" >&2; exit 2; }

want_desc=$(/usr/bin/python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["description"])' "$SSOT")
want_topics=$(/usr/bin/python3 -c 'import json,sys;print("\n".join(sorted(json.load(open(sys.argv[1]))["topics"])))' "$SSOT")

have_desc=$(gh api "repos/$REPO" --jq .description 2>/dev/null || true)
have_topics=$(gh api "repos/$REPO" --jq '.topics[]' 2>/dev/null | sort || true)

desc_drift=0; topics_drift=0
[ "$want_desc" = "$have_desc" ] || desc_drift=1
[ "$want_topics" = "$have_topics" ] || topics_drift=1

if [ "$LIVE" -eq 0 ]; then
  # ---- dry-run: report drift, exit 1 if any (the about-drift.yml sentinel path) ----
  if [ "$desc_drift" -eq 0 ] && [ "$topics_drift" -eq 0 ]; then
    echo "about-sync clean — GitHub About matches $SSOT"
    exit 0
  fi
  echo "about-drift — GitHub About differs from $SSOT (run: bash scripts/sync-about.sh --live)" >&2
  if [ "$desc_drift" -eq 1 ]; then
    echo "  description:" >&2
    echo "    want: $want_desc" >&2
    echo "    have: $have_desc" >&2
  fi
  if [ "$topics_drift" -eq 1 ]; then
    echo "  topics differ:" >&2
    diff <(printf '%s\n' "$want_topics") <(printf '%s\n' "$have_topics") | sed 's/^/    /' >&2 || true
  fi
  exit 1
fi

# ---- --live: project the SSOT onto GitHub (owner admin auth) ----
echo "sync-about (LIVE) — projecting $SSOT onto $REPO"
if [ "$desc_drift" -eq 1 ]; then
  gh api -X PATCH "repos/$REPO" -f description="$want_desc" >/dev/null \
    && echo "  ✓ description updated" \
    || { echo "  ✗ description PATCH failed (needs admin auth on the repo)" >&2; exit 1; }
else
  echo "  · description already current"
fi
if [ "$topics_drift" -eq 1 ]; then
  /usr/bin/python3 -c 'import json,sys;print(json.dumps({"names":json.load(open(sys.argv[1]))["topics"]}))' "$SSOT" \
    | gh api -X PUT "repos/$REPO/topics" --input - >/dev/null \
    && echo "  ✓ topics updated" \
    || { echo "  ✗ topics PUT failed (needs admin auth on the repo)" >&2; exit 1; }
else
  echo "  · topics already current"
fi
echo "sync-about done."
