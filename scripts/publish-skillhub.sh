#!/usr/bin/env bash
# publish-skillhub.sh — publish the bundle's skills to skillhub.cn (中文 Skills 社区).
#
# SkillHub is publish-based: each skill goes up with `skillhub publish <dir>`
# under your logged-in account and then enters platform review (pending_review).
# Every SKILL.md already carries the SkillHub frontmatter (slug: aaron-<name>,
# displayName, summary) alongside the Agent Skills fields, so the repo folders
# publish as-is. This script walks the plugin.json skill list so the published
# set always matches the manifest.
#
# Prereqs (one-time):
#   curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only
#   skillhub login --key "$SKILLHUB_KEY" --host https://api.skillhub.cn
#   (create the key at skillhub.cn 个人中心 → API keys; real-name verification
#    required before publishing — a 403 means complete it in the browser first)
#
# Usage:
#   bash scripts/publish-skillhub.sh                          # dry-run (default): local pre-check, all manifest skills
#   bash scripts/publish-skillhub.sh --skill keyword-research # dry-run one skill
#   bash scripts/publish-skillhub.sh --live                   # publish all (changelog 首次发布)
#   bash scripts/publish-skillhub.sh --live --changelog "v19.2.0 更新说明"
#   bash scripts/publish-skillhub.sh --live --skill x --attempts 1 --throttle 0
#                          # orchestrated mode: publish-registries.sh owns retry/pacing
#
# Exit: 0 all requested skills processed, 1 on any failure.

set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"
source scripts/publish-common.sh

HOST="https://api.skillhub.cn"
DRY_RUN=1         # dry-run by default, like every other publisher; --live to upload
ONLY_SKILL=""
CHANGELOG="首次发布"
THROTTLE=25       # seconds BETWEEN real publishes (leading, so a single-skill run never sleeps)
ATTEMPTS=4        # rate-limit retries per skill; orchestrators pass --attempts 1
RESUME_FROM=""    # skip manifest entries until this skill name (inclusive start)
while [ $# -gt 0 ]; do
  case "$1" in
    --live) DRY_RUN=0 ;;
    --dry-run) DRY_RUN=1 ;;
    --skill) shift; ONLY_SKILL="${1:-}" ;;
    --changelog) shift; CHANGELOG="${1:-}" ;;
    --host) shift; HOST="${1:-}" ;;
    --throttle) shift; THROTTLE="${1:-25}" ;;
    --attempts) shift; ATTEMPTS="${1:-4}" ;;
    --resume-from) shift; RESUME_FROM="${1:-}" ;;
    *) echo "unknown flag: $1" >&2; exit 1 ;;
  esac
  shift
done

SKILLHUB_BIN="${SKILLHUB_BIN:-$HOME/.local/bin/skillhub}"
command -v skillhub >/dev/null 2>&1 && SKILLHUB_BIN=skillhub
if ! command -v "$SKILLHUB_BIN" >/dev/null 2>&1; then
  echo "FAIL: skillhub CLI not found — install with:" >&2
  echo "  curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only" >&2
  exit 1
fi

PUBLISH_COMMIT=""; PUBLISH_REPO=""; BUILD_ROOT=""; SOURCE_ROOT="."
if [ "$DRY_RUN" -eq 0 ]; then
  BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/aaron-skillhub-skills.XXXXXX")" || {
    echo "FAIL: cannot create a private publish build directory" >&2; exit 1;
  }
  trap '[ -n "${BUILD_ROOT:-}" ] && rm -rf -- "$BUILD_ROOT"' EXIT
  SOURCE_ROOT="$BUILD_ROOT/source"
  RELEASE_IDENTITY="$(publish_prepare_release_source "$SOURCE_ROOT")" || exit 1
  PUBLISH_REPO="${RELEASE_IDENTITY%%$'\t'*}"
  PUBLISH_COMMIT="${RELEASE_IDENTITY#*$'\t'}"
  echo "Live provenance: $PUBLISH_REPO@$PUBLISH_COMMIT (clean, reachable from origin/main)"
fi

SKILL_DIRS=$(python3 -c '
import json, sys
for p in json.load(open(sys.argv[1]))["skills"]:
    print(p[2:] if p.startswith("./") else p)
' "$SOURCE_ROOT/.claude-plugin/plugin.json") || {
  echo "FAIL: cannot read the pinned plugin skill manifest" >&2
  exit 1
}
[ -n "$SKILL_DIRS" ] || { echo "FAIL: pinned plugin skill manifest is empty" >&2; exit 1; }

fail=0 count=0 skipping=0 published=0
[ -n "$RESUME_FROM" ] && skipping=1
for dir in $SKILL_DIRS; do
  name=$(basename "$dir")
  if [ "$skipping" -eq 1 ]; then
    if [ "$name" = "$RESUME_FROM" ]; then skipping=0; else continue; fi
  fi
  if [ -n "$ONLY_SKILL" ] && [ "$name" != "$ONLY_SKILL" ]; then continue; fi
  if [ ! -f "$SOURCE_ROOT/$dir/SKILL.md" ]; then
    echo "FAIL: $dir/SKILL.md missing" >&2; fail=1; continue
  fi
  slug=$(sed -n 's/^slug: *//p' "$SOURCE_ROOT/$dir/SKILL.md" | head -1)
  if [ -z "$slug" ]; then
    echo "FAIL: no slug in $dir/SKILL.md (SkillHub requires slug/displayName/summary frontmatter)" >&2
    fail=1; continue
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

  cmd=("$SKILLHUB_BIN" publish "$publish_dir" --host "$HOST")
  if [ "$DRY_RUN" -eq 1 ]; then
    cmd+=(--dry-run)
    echo "==> $slug (dry-run)"
    "${cmd[@]}" || { echo "FAIL: dry-run failed for $slug" >&2; fail=1; }
  else
    cmd+=(--changelog "$CHANGELOG")
    echo "==> $slug"
    # throttle BETWEEN publishes (leading): a single-skill invocation — the
    # orchestrated per-skill path — no longer burns a trailing sleep.
    [ "$published" -gt 0 ] && [ "$THROTTLE" -gt 0 ] && sleep "$THROTTLE"
    published=$((published + 1))
    # rate-limit aware: up to $ATTEMPTS tries with a 70s backoff on 频率/429.
    # Orchestrators (publish-registries.sh) pass --attempts 1 and own the
    # retry policy, so the two layers cannot multiply into 16 requests.
    attempts=0 ok=0
    while [ "$attempts" -lt "$ATTEMPTS" ]; do
      out=$("${cmd[@]}" 2>&1); rc=$?
      echo "$out"
      if [ "$rc" -eq 0 ]; then ok=1; break; fi
      if echo "$out" | grep -q "频率\|稍后再试\|429"; then
        attempts=$((attempts + 1))
        [ "$attempts" -lt "$ATTEMPTS" ] || break
        echo "    rate-limited — waiting 70s (retry $attempts/$ATTEMPTS)"
        sleep 70
      else
        break
      fi
    done
    if [ "$ok" -ne 1 ]; then
      echo "FAIL: publish failed for $slug" >&2
      fail=1
    fi
  fi
  count=$((count + 1))
done

if [ -n "$ONLY_SKILL" ] && [ "$count" -eq 0 ]; then
  echo "FAIL: skill '$ONLY_SKILL' not found in plugin.json" >&2
  exit 1
fi

suffix=""; [ "$DRY_RUN" -eq 1 ] && suffix=" — dry-run, nothing uploaded"
echo "processed $count skill(s)$suffix"
exit $fail
