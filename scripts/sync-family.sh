#!/usr/bin/env bash
# sync-family.sh — verify (and, with --live, push) the downstream repo family from this SSOT.
#
# Registry, tiers, and banner templates: docs/repo-family.md (human policy).
# This script is the executable mapping — keep the two in step.
#
# Usage:
#   bash scripts/sync-family.sh          # dry-run: fetch live mirrors, report drift + diffs; exit 1 on any drift
#   bash scripts/sync-family.sh --live   # additionally clone drifted `body`/`list` targets, apply, commit, push
#
# Modes (per docs/repo-family.md §Sync modes):
#   body — README content between SYNC markers regenerated from a references/ file
#          (relative .md links rewritten to absolute umbrella URLs)
#   list — skill list between SYNC markers regenerated from .claude-plugin/plugin.json
#   ids  — verify-only: every item ID the umbrella source references must exist in the
#          published standard; never auto-pushed (manual reconciliation)
#
# Owner-run at release time (CONTRIBUTING §6). CI (family-drift.yml) runs the dry-run
# weekly — read-only GitHub Contents API fetches (token-authenticated when GITHUB_TOKEN
# is present to clear the 60 req/hr unauthenticated cap), no push.

set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/publish-common.sh

OWNER="aaron-he-zhu"
UMBRELLA="aaron-marketing-skills"
REF_URL="https://github.com/$OWNER/$UMBRELLA/blob/main/references"
LIVE=0
[ "${1:-}" = "--live" ] && LIVE=1
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
SOURCE_ROOT="."
if [ "$LIVE" -eq 1 ]; then
  SOURCE_ROOT="$TMP/source"
  RELEASE_IDENTITY="$(publish_prepare_release_source "$SOURCE_ROOT")"
  SOURCE_REPO="${RELEASE_IDENTITY%%$'\t'*}"
  SOURCE_COMMIT="${RELEASE_IDENTITY#*$'\t'}"
  [ "$SOURCE_REPO" = "$OWNER/$UMBRELLA" ] || {
    echo "FAIL: family live source $SOURCE_REPO is not $OWNER/$UMBRELLA" >&2
    exit 1
  }
  echo "family provenance: $SOURCE_REPO@$SOURCE_COMMIT (pinned commit export)"
fi
VERSION=$(/usr/bin/python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$SOURCE_ROOT/.claude-plugin/plugin.json")
DRIFT=0

fetch_raw() { # $1 repo, $2 file → stdout (fails silently; caller checks)
  # Use the GitHub Contents API raw media response instead of raw.githubusercontent:
  # right after --live pushes, raw.githubusercontent can serve a stale cached blob
  # and make the owner-run verification look drifted even when the repo is synced.
  # The UNAUTHENTICATED Contents API is only 60 req/hr per IP — on shared-IP CI runners
  # that budget can already be spent by other jobs, and a 403 then reads as "repo
  # missing/drifted" (a false CI failure). Pass a token when one is present (Actions
  # always provides GITHUB_TOKEN) to raise the limit to 5,000/hr.
  # Owner-run local shells usually have no GITHUB_TOKEN — borrow the gh CLI's
  # token so repeated runs don't exhaust the 60 req/hr anonymous cap (observed
  # at v18.0.0 as ROTATING false "unreachable" repos across back-to-back runs).
  local tok="${GITHUB_TOKEN:-}" ghbin
  if [ -z "$tok" ]; then
    for ghbin in gh /opt/homebrew/bin/gh; do
      command -v "$ghbin" >/dev/null 2>&1 && { tok="$("$ghbin" auth token 2>/dev/null || true)"; break; }
    done
  fi
  local url="https://api.github.com/repos/$OWNER/$1/contents/$2?ref=main"
  if [ -n "$tok" ]; then
    curl -fsSL -H "Authorization: Bearer $tok" -H 'Accept: application/vnd.github.raw' "$url"
  else
    curl -fsSL -H 'Accept: application/vnd.github.raw' "$url"
  fi
}

between_markers() { awk '/<!-- SYNC:BEGIN/{f=1;next} /<!-- SYNC:END/{f=0} f'; }

# ---- generators -------------------------------------------------------------

gen_body() { # $1 references/<file>.md → stdout, relative md links → absolute umbrella URLs
  sed -E "s,\]\(([A-Za-z0-9._-]+\.md)(#[^)]*)?\),](${REF_URL}/\1\2),g" "$1"
}

gen_list() { # $1 plugin.json path prefix (ad|email), $2 pinned/dry-run plugin.json → stdout
  /usr/bin/python3 - "$1" "$2" <<'PY'
import json, sys
pre = sys.argv[1] + "/"
plugin = json.load(open(sys.argv[2]))
url = "https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/"
phases = {}
for s in plugin["skills"]:
    s = s.lstrip("./")
    if not s.startswith(pre):
        continue
    _, phase, name = s.split("/")
    phases.setdefault(phase, []).append((name, s))
for phase, items in phases.items():
    print(f"**{phase.capitalize()}**\n")
    for name, path in items:
        print(f"- [`{name}`]({url}{path}/SKILL.md)")
    print()
PY
}

extract_ids() { # $1 file → sorted unique item IDs (bold anywhere, or leading table cell)
  # The trailing grep must not fail the pipeline under pipefail when a source
  # legitimately contains zero IDs (e.g. an index page); emptiness is judged
  # by the caller, which fails loudly on an empty umbrella ID set.
  # Leading-cell forms covered: | S1 | · | **S1** | · | `S1` | · | `S2` ⛔ |
  # (star-benchmark.md backticks its IDs and marks veto rows with a trailing ⛔).
  {
    grep -oE '\*\*[A-Z][0-9]{1,2}\*\*' "$1" || true
    grep -oE '^\|[[:space:]]*[*`]*[A-Z][0-9]{1,2}[*`]*[[:space:]]*(⛔[[:space:]]*)?\|' "$1" || true
  } | { grep -oE '[A-Z][0-9]{1,2}' || true; } | sort -u
}

# ---- checkers ---------------------------------------------------------------

check_marker_target() { # $1 repo, $2 source label, $3 generated-body file
  local repo="$1" src="$2" gen="$3"
  local remote="$TMP/$repo.README.md"
  if ! fetch_raw "$repo" README.md > "$remote" 2>/dev/null; then
    echo "✗ $repo — unreachable or missing README (repo not created yet?)"
    DRIFT=1
    return
  fi
  between_markers < "$remote" > "$TMP/$repo.remote-body"
  if diff -q "$TMP/$repo.remote-body" "$gen" >/dev/null 2>&1; then
    echo "✓ $repo — in sync"
    return
  fi
  echo "✗ $repo — DRIFT (remote vs regenerated):"
  diff "$TMP/$repo.remote-body" "$gen" | head -40 || true
  DRIFT=1
  if [ $LIVE -eq 1 ]; then
    push_marker_target "$repo" "$src" "$gen"
  fi
}

push_marker_target() { # $1 repo, $2 source label, $3 generated-body file
  local repo="$1" src="$2" gen="$3"
  local clone="$TMP/clone-$repo"
  git clone --quiet --depth 1 "https://github.com/$OWNER/$repo.git" "$clone"
  local rd="$clone/README.md" new="$TMP/new-$repo.md"
  awk '/<!-- SYNC:BEGIN/{exit} {print}' "$rd" > "$new"
  printf '<!-- SYNC:BEGIN source=%s umbrella=v%s — generated by scripts/sync-family.sh; edit the source, not this block -->\n' "$src" "$VERSION" >> "$new"
  cat "$gen" >> "$new"
  printf '<!-- SYNC:END -->\n' >> "$new"
  awk 'f{print} /<!-- SYNC:END/{f=1}' "$rd" >> "$new"
  mv "$new" "$rd"
  git -C "$clone" commit --quiet -am "sync: umbrella v$VERSION"
  git -C "$clone" push --quiet
  echo "  ↳ pushed sync: umbrella v$VERSION → $repo"
}

check_ids_target() { # $1 repo, $2 colon-separated references source file(s), $3… repo files to scan
  local repo="$1" src="$2"; shift 2
  local remote_all="$TMP/$repo.all.md"
  : > "$remote_all"
  local f got=0 failed=0
  for f in "$@"; do
    if fetch_raw "$repo" "$f" >> "$remote_all" 2>/dev/null; then got=1; else failed=1; fi
    echo >> "$remote_all"
  done
  # got=0 means NOT ONE file fetched -> truly unreachable. (The per-iteration
  # `echo` pads a newline every loop, so the old `! -s` emptiness test never fired.)
  if [ $got -eq 0 ]; then
    echo "✗ $repo — unreachable"
    DRIFT=1
    return
  fi
  # A partial fetch (some files 404 while others succeed) leaves $remote_all
  # missing IDs from the unreachable files. Comparing against it would report
  # false "missing ID" drift, so treat any fetch failure as unreachable/partial.
  if [ $failed -eq 1 ]; then
    echo "✗ $repo — partial fetch (one or more files unreachable); skipping ID comparison"
    DRIFT=1
    return
  fi
  local want="$TMP/$repo.want" srcfile
  : > "$want"
  local -a src_files
  IFS=':' read -r -a src_files <<< "$src"
  for srcfile in "${src_files[@]}"; do
    extract_ids "$srcfile" >> "$want"
  done
  sort -u -o "$want" "$want"
  if [ ! -s "$want" ]; then
    echo "✗ $repo — umbrella source(s) $src contain no item IDs; the ids policy for this target is misconfigured (fix the sync-family target list)"
    DRIFT=1
    return
  fi
  extract_ids "$remote_all" > "$TMP/$repo.have"
  local missing
  missing=$(comm -23 "$want" "$TMP/$repo.have")
  if [ -z "$missing" ]; then
    echo "✓ $repo — all $(wc -l < "$TMP/$repo.want" | tr -d ' ') umbrella-referenced item IDs present"
  else
    echo "✗ $repo — item IDs referenced in $src but missing from the published standard (reconcile manually):"
    echo "$missing" | sed 's/^/    /'
    DRIFT=1
  fi
}

# ---- targets (keep in step with docs/repo-family.md §Registry) ---------------

echo "sync-family — umbrella v$VERSION $([ $LIVE -eq 1 ] && echo '(LIVE)' || echo '(dry-run)')"
echo

gen_body "$SOURCE_ROOT/references/roas-benchmark.md" > "$TMP/gen-roas.md"
check_marker_target paid-ads-roas-benchmark references/roas-benchmark.md "$TMP/gen-roas.md"

gen_body "$SOURCE_ROOT/references/send-benchmark.md" > "$TMP/gen-send.md"
check_marker_target email-marketing-send-benchmark references/send-benchmark.md "$TMP/gen-send.md"

gen_body "$SOURCE_ROOT/references/ramp-benchmark.md" > "$TMP/gen-ramp.md"
check_marker_target launch-marketing-ramp-benchmark references/ramp-benchmark.md "$TMP/gen-ramp.md"

gen_body "$SOURCE_ROOT/references/echo-benchmark.md" > "$TMP/gen-echo.md"
check_marker_target social-marketing-echo-benchmark references/echo-benchmark.md "$TMP/gen-echo.md"

gen_body "$SOURCE_ROOT/references/tale-benchmark.md" > "$TMP/gen-tale.md"
check_marker_target narrative-marketing-tale-benchmark references/tale-benchmark.md "$TMP/gen-tale.md"

gen_list ad "$SOURCE_ROOT/.claude-plugin/plugin.json" > "$TMP/gen-ad.md"
check_marker_target paid-ads-agent-skills 'plugin.json#ad' "$TMP/gen-ad.md"

gen_list email "$SOURCE_ROOT/.claude-plugin/plugin.json" > "$TMP/gen-email.md"
check_marker_target email-marketing-agent-skills 'plugin.json#email' "$TMP/gen-email.md"

gen_list seo-geo "$SOURCE_ROOT/.claude-plugin/plugin.json" > "$TMP/gen-seo-geo.md"
check_marker_target seo-geo-claude-skills 'plugin.json#seo-geo' "$TMP/gen-seo-geo.md"

gen_list influencer "$SOURCE_ROOT/.claude-plugin/plugin.json" > "$TMP/gen-influencer.md"
check_marker_target influencer-marketing-agent-skills 'plugin.json#influencer' "$TMP/gen-influencer.md"

gen_list launch "$SOURCE_ROOT/.claude-plugin/plugin.json" > "$TMP/gen-launch.md"
check_marker_target product-launch-agent-skills 'plugin.json#launch' "$TMP/gen-launch.md"

gen_list social "$SOURCE_ROOT/.claude-plugin/plugin.json" > "$TMP/gen-social.md"
check_marker_target social-media-agent-skills 'plugin.json#social' "$TMP/gen-social.md"

gen_list narrative "$SOURCE_ROOT/.claude-plugin/plugin.json" > "$TMP/gen-narrative.md"
check_marker_target brand-narrative-agent-skills 'plugin.json#narrative' "$TMP/gen-narrative.md"

check_ids_target core-eeat-content-benchmark "$SOURCE_ROOT/references/core-eeat-benchmark.md" README.md
check_ids_target cite-domain-rating "$SOURCE_ROOT/references/cite-domain-rating.md" README.md
# v18 replaced the C3 split with the single references/star-benchmark.md (STAR).
# The GitHub mirror is already influencer-marketing-star-benchmark (ids-mode).
check_ids_target influencer-marketing-star-benchmark \
  "$SOURCE_ROOT/references/star-benchmark.md" \
  README.md star-benchmark.md

echo
if [ $DRIFT -eq 1 ]; then
  [ $LIVE -eq 1 ] && echo "Drift found — body/list targets pushed; ids targets need manual reconciliation." \
                  || echo "Drift found — rerun with --live to push body/list targets."
  exit 1
fi
echo "All family repos in sync."
