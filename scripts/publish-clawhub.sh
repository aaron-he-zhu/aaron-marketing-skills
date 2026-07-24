#!/usr/bin/env bash
# publish-clawhub.sh — publish the bundle's skills to ClawHub (OpenClaw's registry).
#
# ClawHub is publish-based (no repo crawling): each skill is pushed with
# `clawhub skill publish <dir>` under your logged-in handle. This script walks
# the plugin.json skill list so the published set always matches the manifest,
# and passes each skill's real frontmatter version so registry versions track
# VERSIONS.md instead of ClawHub's auto-patch counter.
#
# ⚠️ LICENSE: everything published on ClawHub is relicensed MIT-0 (free use,
# no attribution) regardless of this repo's Apache-2.0. Real publishes
# therefore require the explicit --i-accept-mit0 flag.
#
# Prereqs: npm i -g clawhub && clawhub login   (GitHub account, aged)
#
# Usage:
#   bash scripts/publish-clawhub.sh --dry-run                 # preview all manifest skills
#   bash scripts/publish-clawhub.sh --skill keyword-research --dry-run
#   bash scripts/publish-clawhub.sh --i-accept-mit0           # publish all
#   bash scripts/publish-clawhub.sh --i-accept-mit0 --owner myorg
#
# Exit: 0 all requested skills processed, 1 on any publish/setup failure.

set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"
source scripts/publish-common.sh

DRY_RUN=0
ACCEPT_MIT0=0
ONLY_SKILL=""
OWNER=""
THROTTLE=15       # seconds between real publishes (ClawHub rate-limits new-skill creation)
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --i-accept-mit0) ACCEPT_MIT0=1 ;;
    --skill) shift; ONLY_SKILL="${1:-}" ;;
    --owner) shift; OWNER="${1:-}" ;;
    --throttle) shift; THROTTLE="${1:-15}" ;;
    *) echo "unknown flag: $1" >&2; exit 1 ;;
  esac
  shift
done

if ! command -v clawhub >/dev/null 2>&1; then
  echo "FAIL: clawhub CLI not found — install with: npm i -g clawhub" >&2
  exit 1
fi

if [ "$DRY_RUN" -eq 0 ] && [ "$ACCEPT_MIT0" -eq 0 ]; then
  cat >&2 <<'EOF'
FAIL: real publishes require --i-accept-mit0.

ClawHub licenses every published skill under MIT-0: anyone may use, modify,
and redistribute the published copies, commercially, without attribution —
this is broader than the repo's Apache-2.0. Re-run with --i-accept-mit0 to
acknowledge, or use --dry-run to preview without uploading.
EOF
  exit 1
fi

PUBLISH_COMMIT=""; PUBLISH_REPO=""; BUILD_ROOT=""; SOURCE_ROOT="."
if [ "$DRY_RUN" -eq 0 ]; then
  BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/aaron-clawhub-skills.XXXXXX")" || {
    echo "FAIL: cannot create a private publish build directory" >&2; exit 1;
  }
  trap '[ -n "${BUILD_ROOT:-}" ] && rm -rf -- "$BUILD_ROOT"' EXIT
  SOURCE_ROOT="$BUILD_ROOT/source"
  RELEASE_IDENTITY="$(publish_prepare_release_source "$SOURCE_ROOT")" || exit 1
  PUBLISH_REPO="${RELEASE_IDENTITY%%$'\t'*}"
  PUBLISH_COMMIT="${RELEASE_IDENTITY#*$'\t'}"
  echo "Live provenance: $PUBLISH_REPO@$PUBLISH_COMMIT (clean, reachable from origin/main)"
fi

# Skill dirs from the manifest (the same list every other host installs from)
SKILL_DIRS=$(python3 -c '
import json, sys
for p in json.load(open(sys.argv[1]))["skills"]:
    print(p[2:] if p.startswith("./") else p)
' "$SOURCE_ROOT/.claude-plugin/plugin.json") || {
  echo "FAIL: cannot read the pinned plugin skill manifest" >&2
  exit 1
}
[ -n "$SKILL_DIRS" ] || { echo "FAIL: pinned plugin skill manifest is empty" >&2; exit 1; }

fail=0 count=0
for dir in $SKILL_DIRS; do
  name=$(basename "$dir")
  if [ -n "$ONLY_SKILL" ] && [ "$name" != "$ONLY_SKILL" ]; then continue; fi
  if [ ! -f "$SOURCE_ROOT/$dir/SKILL.md" ]; then
    echo "FAIL: $dir/SKILL.md missing" >&2; fail=1; continue
  fi
  version=$(sed -n 's/^version: *"\([0-9][0-9.]*\)".*/\1/p' "$SOURCE_ROOT/$dir/SKILL.md" | head -1)
  if [ -z "$version" ]; then
    echo "FAIL: no version in $dir/SKILL.md" >&2; fail=1; continue
  fi

  publish_dir="$SOURCE_ROOT/$dir"
  if [ "$DRY_RUN" -eq 0 ]; then
    publish_dir="$BUILD_ROOT/$name"
    publish_build_verified_skill \
      "$dir" "$publish_dir" "$PUBLISH_REPO" "$PUBLISH_COMMIT" "$SOURCE_ROOT" || {
        echo "FAIL: cannot build verified publish payload for $name" >&2
        fail=1
        continue
      }
  fi

  cmd=(clawhub skill publish "$publish_dir" --version "$version")
  [ "$DRY_RUN" -eq 1 ] && cmd+=(--dry-run)
  [ -n "$OWNER" ] && cmd+=(--owner "$OWNER")

  suffix=""; [ "$DRY_RUN" -eq 1 ] && suffix=" (dry-run)"
  echo "==> $name v$version$suffix"
  if [ "$DRY_RUN" -eq 1 ]; then
    "${cmd[@]}" || { echo "FAIL: dry-run failed for $name" >&2; fail=1; }
  else
    # ClawHub enforces a new-skill creation rate limit — retry with backoff.
    # "already exists" = this exact version is published — idempotent success
    # (explicit --version bypasses the CLI's content-fingerprint skip).
    attempts=0 ok=0
    while [ "$attempts" -lt 4 ]; do
      out=$("${cmd[@]}" 2>&1); rc=$?
      echo "$out"
      if [ "$rc" -eq 0 ]; then ok=1; break; fi
      if echo "$out" | grep -q "already exists"; then
        echo "    version already on ClawHub — skipping"
        ok=1; break
      fi
      if echo "$out" | grep -qi "RateLimit\|reset in\|too many"; then
        attempts=$((attempts + 1))
        echo "    rate-limited — waiting 70s (retry $attempts/4)"
        sleep 70
      else
        break
      fi
    done
    if [ "$ok" -ne 1 ]; then
      echo "FAIL: publish failed for $name" >&2
      fail=1
    fi
    [ "$THROTTLE" -gt 0 ] && sleep "$THROTTLE"
  fi
  count=$((count + 1))
done

if [ -n "$ONLY_SKILL" ] && [ "$count" -eq 0 ]; then
  echo "FAIL: skill '$ONLY_SKILL' not found in plugin.json" >&2
  exit 1
fi

echo "processed $count skill(s)$( [ "$DRY_RUN" -eq 1 ] && echo ' — dry-run, nothing uploaded')"
exit $fail
