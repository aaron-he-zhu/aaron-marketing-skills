#!/usr/bin/env bash
# publish-registries.sh — publish ONLY the skills that are behind on each registry.
#
# Computes the behind-set from registry-status.sh (no hardcoded queue — that is
# exactly how the retired finish-registry-publish.sh rotted), then publishes each
# stale/missing skill at its current repo version via the per-skill publishers.
# Idempotent: an already-current version returns "版本已存在" (SkillHub) or the
# "already exists" path (ClawHub) and is counted in-sync, not a failure.
# Resumable (state file + entries keyed by bundle commit) and quota-aware.
# Dry-run default.
#
# Usage:
#   bash scripts/publish-registries.sh                     # dry-run: list the behind-set
#   bash scripts/publish-registries.sh --live              # publish behind-set on both
#   bash scripts/publish-registries.sh --live --parallel   # both platforms concurrently
#   bash scripts/publish-registries.sh --live clawhub      # one platform (clawhub|skillhub|both)
#   bash scripts/publish-registries.sh --from-json f.json  # reuse a registry-status --json snapshot
#   bash scripts/publish-registries.sh --skillhub-budget N # max SkillHub publishes this run (default 90)
#
# SkillHub quota (measured at v18.0.0, 2026-07): ~100 publishes per 24h ROLLING
# window, account-wide. Exceeding it returns 发布频率过高 for every skill, and
# retries themselves keep the window hot — so this script (a) stops at a budget
# below the cap, (b) retries a rate-limit ONCE after 5 min, then DEFERs the
# skill, and (c) aborts the SkillHub pass after 2 consecutive deferrals
# (account-level window). Deferred ≠ failed: exit 8 means "re-run this same
# command after the window" — the state file + idempotent publishes make the
# re-run cheap. Once the immutable final GitHub release gates exist, the shared
# publisher gate permits that continuation beyond the initial 24-hour issuance
# window while the committed semantic evidence policy remains current (30 days
# at v19); it still revalidates the complete private proof chain. ClawHub updates
# to existing skills are not hourly-capped (only brand-new skills are ~5/hr).
# ClawHub relicenses published skills MIT-0.
# Owner-run, never CI. Exit: 0 clean · 1 hard failure · 8 quota-deferred.
set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"
source scripts/publish-common.sh

LIVE=0; PLAT="both"; FROM=""; PARALLEL=0; SH_BUDGET=90
while [ $# -gt 0 ]; do
  case "$1" in
    --live) LIVE=1 ;;
    --parallel) PARALLEL=1 ;;
    --from-json) shift; FROM="${1:-}" ;;
    --skillhub-budget) shift; SH_BUDGET="${1:-90}" ;;
    clawhub|skillhub|both) PLAT="$1" ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--live] [--parallel] [clawhub|skillhub|both] [--from-json file] [--skillhub-budget N]" >&2; exit 1 ;;
  esac
  shift
done

# Resume state and every done entry bind repository + bundle version + exact
# source commit. A reused version or stale state from another commit can never
# skip a registry that the bound status snapshot says is behind.
VER=""
STATE_TOOL="scripts/publish-state.py"
REPO_SLUG=""; STATE=""; head_commit=""; FINAL_GATE_TOKEN=""
donep(){
  /usr/bin/python3 "$STATE_TOOL" --repo "$REPO_SLUG" --version "$VER" \
    --commit "$head_commit" has "$1"
  local rc=$?
  case "$rc" in 0) return 0;; 1) return 1;; *) echo "FAIL: cannot read private publisher state $STATE" >&2; exit 1;; esac
}
markp(){
  /usr/bin/python3 "$STATE_TOOL" --repo "$REPO_SLUG" --version "$VER" \
    --commit "$head_commit" mark "$1" || {
    echo "FAIL: cannot atomically update private publisher state $STATE" >&2
    exit 1
  }
}

# Establish one immutable repository+commit identity before any live registry
# status or child publisher is consulted. Children must independently pass
# their own gate and match this exact parent identity.
if [ "$LIVE" -eq 1 ]; then
  RELEASE_IDENTITY="$(publish_require_release_identity)" || exit 1
  REPO_SLUG="${RELEASE_IDENTITY%%$'\t'*}"
  head_commit="${RELEASE_IDENTITY#*$'\t'}"
  publish_require_expected_release_identity "$REPO_SLUG" "$head_commit" || exit 1
  publish_require_final_release "$REPO_SLUG" "$head_commit" || exit 1
  FINAL_GATE_TOKEN="${PUBLISH_FINAL_GATE_TOKEN:-}"
  PLUGIN_JSON="$(git show "${head_commit}:.claude-plugin/plugin.json" 2>/dev/null)" || {
    echo "FAIL: .claude-plugin/plugin.json is not committed at $head_commit" >&2
    exit 1
  }
  VER="$(printf '%s' "$PLUGIN_JSON" | /usr/bin/python3 -c 'import json,sys;print(json.load(sys.stdin)["version"])')" || exit 1
  STATE="$(/usr/bin/python3 "$STATE_TOOL" --repo "$REPO_SLUG" --version "$VER" \
    --commit "$head_commit" path)" || exit 1
  echo "    provenance -> $REPO_SLUG@$head_commit; private resume state -> $STATE"
else
  VER="$(/usr/bin/python3 -c 'import json;print(json.load(open(".claude-plugin/plugin.json"))["version"])')" || exit 1
  if [ -n "$FROM" ]; then
    REPO_SLUG="$(publish_repo_slug)" || exit 1
    head_commit="$(git rev-parse --verify 'HEAD^{commit}' 2>/dev/null)" || {
      echo "FAIL: --from-json requires a Git commit identity" >&2
      exit 1
    }
  fi
fi

echo "==> computing behind-set (registry-status)..."
if [ -n "$FROM" ]; then
  [ -f "$FROM" ] && [ ! -L "$FROM" ] || {
    echo "FAIL: --from-json must name a regular non-symlink file" >&2
    exit 1
  }
  snapshot_bytes="$(wc -c < "$FROM" | tr -d '[:space:]')" || exit 1
  case "$snapshot_bytes" in
    ''|*[!0-9]*) echo "FAIL: cannot size --from-json snapshot" >&2; exit 1 ;;
  esac
  [ "$snapshot_bytes" -le 200000 ] || {
    echo "FAIL: --from-json snapshot exceeds the 200KB bound" >&2
    exit 1
  }
  JSON="$(/bin/cat "$FROM")" || exit 1
else
  JSON="$(bash scripts/registry-status.sh --json --platform "$PLAT")" || exit 1
  if [ "$LIVE" -eq 0 ]; then
    REPO_SLUG="$(printf '%s' "$JSON" | /usr/bin/python3 -c 'import json,sys;print(json.load(sys.stdin)["repository"])')" || exit 1
    head_commit="$(printf '%s' "$JSON" | /usr/bin/python3 -c 'import json,sys;print(json.load(sys.stdin)["commit"])')" || exit 1
  fi
fi
[ -n "$JSON" ] || { echo "FAIL: no status JSON" >&2; exit 1; }

# A reusable status file is executable release input, not an advisory cache.
# Validate its exact schema and bind it to the repository, version, commit, and
# canonical 120-skill set at that commit.  OK booleans are re-derived from the
# recorded versions so a hand-edited snapshot cannot suppress a publish.
JSON="$(_STATUS_JSON="$JSON" /usr/bin/python3 - "$REPO_SLUG" "$head_commit" "$VER" "$PLAT" <<'PY'
import json
import os
from pathlib import Path
import re
import subprocess
import sys

expected_repo, expected_commit, expected_version, selected_platform = sys.argv[1:]

def fail(message):
    print("FAIL: invalid registry status snapshot: %s" % message, file=sys.stderr)
    raise SystemExit(1)

def git_json(path):
    try:
        raw = subprocess.check_output(
            ["git", "show", "%s:%s" % (expected_commit, path)],
            stderr=subprocess.DEVNULL,
        )
        return json.loads(raw.decode("utf-8"))
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError, ValueError):
        fail("cannot read %s at bound commit" % path)

try:
    snapshot = json.loads(os.environ["_STATUS_JSON"])
except (UnicodeDecodeError, ValueError, KeyError):
    fail("not UTF-8 JSON")
if not isinstance(snapshot, dict) or set(snapshot) != {
        "schema_version", "repository", "commit", "bundle", "platform", "package", "skills",
}:
    fail("top-level fields differ from the strict schema")
if snapshot["schema_version"] != "1.0":
    fail("unsupported schema_version")
if (snapshot["repository"] != expected_repo or snapshot["commit"] != expected_commit
        or snapshot["bundle"] != expected_version):
    fail("repository/version/commit identity does not match this release")
if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", snapshot["commit"]):
    fail("commit identity is malformed")
if snapshot["platform"] not in {"clawhub", "skillhub", "both"}:
    fail("platform is invalid")
if selected_platform == "both" and snapshot["platform"] != "both":
    fail("both-platform publish requires a both-platform snapshot")
if selected_platform != "both" and snapshot["platform"] not in {selected_platform, "both"}:
    fail("snapshot does not cover the selected platform")

plugin = git_json(".claude-plugin/plugin.json")
catalog = git_json("references/system-catalog.json")
repo_url = "https://github.com/%s" % expected_repo
if (plugin.get("version") != expected_version
        or catalog.get("bundle_version") != expected_version
        or plugin.get("repository", "").removesuffix(".git") != repo_url):
    fail("bound commit metadata does not match repository/version")

canonical = []
for discipline in catalog.get("logical_order", []):
    if discipline == "protocol":
        canonical.extend(
            ("protocol/%s" % slug, slug)
            for slug in catalog.get("protocol", {}).get("skills", [])
        )
        continue
    spec = catalog.get("disciplines", {}).get(discipline, {})
    for phase in spec.get("phase_order", []):
        canonical.extend(
            ("%s/%s/%s" % (discipline, phase, slug), slug)
            for slug in spec.get("phases", {}).get(phase, [])
        )
declared = [
    value[2:] if isinstance(value, str) and value.startswith("./") else value
    for value in plugin.get("skills", [])
]
if (len(canonical) != 120 or len({path for path, _ in canonical}) != 120
        or declared != [path for path, _ in canonical]):
    fail("bound commit does not declare the ordered canonical 120 skills")

expected_skills = {}
for path, name in canonical:
    try:
        text = subprocess.check_output(
            ["git", "show", "%s:%s/SKILL.md" % (expected_commit, path)],
            stderr=subprocess.DEVNULL,
        ).decode("utf-8")
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        fail("cannot read canonical SKILL.md for %s" % name)
    values = {}
    for line in text.splitlines()[1:]:
        if line == "---":
            break
        matched = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if matched:
            values[matched.group(1)] = matched.group(2).strip("\"'")
    version = values.get("version")
    if (values.get("name") != name or not isinstance(version, str)
            or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version)):
        fail("canonical skill identity/version is invalid for %s" % name)
    expected_skills[name] = {"slug": values.get("slug"), "version": version}
slugs = [value["slug"] for value in expected_skills.values()]
if len(set(slugs)) != 120 or any(not value for value in slugs):
    fail("canonical SkillHub slugs are missing or duplicated")

package = snapshot["package"]
if not isinstance(package, dict) or set(package) != {"name", "clawhub", "ok"}:
    fail("package fields differ from the strict schema")
if package["name"] != "aaron-marketing" or not isinstance(package["ok"], bool):
    fail("package identity is invalid")
if package["ok"] != (package["clawhub"] == expected_version):
    fail("package ok flag does not match its recorded version")

rows = snapshot["skills"]
if not isinstance(rows, list) or len(rows) != 120:
    fail("skills must contain exactly 120 records")
seen_names = set()
seen_slugs = set()
for row in rows:
    if not isinstance(row, dict) or set(row) != {
        "skill", "slug", "repo", "clawhub", "skillhub", "clawhub_ok", "skillhub_ok",
    }:
        fail("skill record fields differ from the strict schema")
    name = row["skill"]
    slug = row["slug"]
    if name not in expected_skills or expected_skills[name]["slug"] != slug:
        fail("skill/slug is outside the canonical set")
    if name in seen_names or slug in seen_slugs:
        fail("skill names and slugs must be unique")
    if row["repo"] != expected_skills[name]["version"]:
        fail("repo version does not match the bound canonical skill for %s" % name)
    if not isinstance(row["clawhub_ok"], bool) or not isinstance(row["skillhub_ok"], bool):
        fail("registry ok flags must be booleans")
    if row["clawhub_ok"] != (row["clawhub"] == row["repo"]):
        fail("ClawHub ok flag does not match recorded version for %s" % name)
    if row["skillhub_ok"] != (row["skillhub"] == row["repo"]):
        fail("SkillHub ok flag does not match recorded version for %s" % name)
    seen_names.add(name)
    seen_slugs.add(slug)
if seen_names != set(expected_skills):
    fail("snapshot does not equal the full canonical skill set")
print(json.dumps(snapshot, sort_keys=True, separators=(",", ":")))
PY
)" || exit 1

behind(){ printf '%s' "$JSON" | /usr/bin/python3 -c "import sys,json;d=json.load(sys.stdin);print('\n'.join(s['skill'] for s in d['skills'] if not s['$1']))"; }
CH="$( [ "$PLAT" != skillhub ] && behind clawhub_ok )"
SH="$( [ "$PLAT" != clawhub ] && behind skillhub_ok )"
nch=$(printf '%s' "$CH" | grep -c . || true); nsh=$(printf '%s' "$SH" | grep -c . || true)
echo "    behind -> ClawHub: $nch, SkillHub: $nsh   (mode: $([ $LIVE -eq 1 ] && echo LIVE || echo dry-run))"

publish_clawhub_set(){ # reads $CH; returns 0 clean, 1 hard failure
  local fail=0 s out rc
  while read -r s; do [ -n "$s" ] || continue
    if [ "$LIVE" -eq 0 ]; then echo "  would publish (clawhub) $s"; continue; fi
    if [ -n "$FROM" ] && donep "ch:$VER:$head_commit:$s"; then
      echo "  skip $s (done for $head_commit; reused bound snapshot)"
      continue
    fi
    out=$(AARON_PUBLISH_EXPECTED_REPO="$REPO_SLUG" \
      AARON_PUBLISH_EXPECTED_COMMIT="$head_commit" \
      AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN="$FINAL_GATE_TOKEN" \
      bash scripts/publish-clawhub.sh --skill "$s" --i-accept-mit0 2>&1); rc=$?
    if [ $rc -eq 0 ]; then echo "  OK $s"; markp "ch:$VER:$head_commit:$s"; else echo "  FAIL $s :: $(echo "$out"|tail -1)"; fail=1; fi
    sleep 6
  done <<< "$CH"
  return $fail
}

publish_skillhub_set(){ # reads $SH; returns 0 clean, 1 hard failure, 8 quota-deferred
  # Retry policy lives HERE (the inner publisher runs with --attempts 1) so the
  # two layers can no longer multiply into 16 requests per limited skill.
  local fail=0 deferred=0 consec=0 budget_used=0 s rest out rc limited try
  while read -r s; do [ -n "$s" ] || continue
    if [ "$LIVE" -eq 0 ]; then echo "  would publish (skillhub) $s"; continue; fi
    if [ -n "$FROM" ] && donep "sh:$VER:$head_commit:$s"; then
      echo "  skip $s (done for $head_commit; reused bound snapshot)"
      continue
    fi
    if [ "$budget_used" -ge "$SH_BUDGET" ]; then
      echo "  DEFER $s (budget $SH_BUDGET reached this run)"; deferred=$((deferred+1)); continue
    fi
    limited=0
    for try in 1 2; do
      out=$(AARON_PUBLISH_EXPECTED_REPO="$REPO_SLUG" \
        AARON_PUBLISH_EXPECTED_COMMIT="$head_commit" \
        AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN="$FINAL_GATE_TOKEN" \
        bash scripts/publish-skillhub.sh --live --skill "$s" --attempts 1 --throttle 0 --changelog "v$VER" 2>&1); rc=$?
      if echo "$out" | grep -qE 'Published|skillId'; then
        echo "  OK $s"; markp "sh:$VER:$head_commit:$s"; budget_used=$((budget_used+1)); consec=0; limited=0; break
      fi
      if echo "$out" | grep -q '已存在'; then
        echo "  CURRENT $s (already at repo version)"; markp "sh:$VER:$head_commit:$s"; consec=0; limited=0; break
      fi
      if echo "$out" | grep -qiE '频率过高|429|too many|rate'; then
        limited=1
        [ "$try" -eq 1 ] && { echo "  backoff $s (rate-limited, one retry in 5min)"; sleep 300; }
        continue
      fi
      echo "  FAIL $s :: $(echo "$out"|tail -1)"; fail=1; limited=0; break
    done
    if [ "$limited" -eq 1 ]; then
      echo "  DEFER $s (still rate-limited after retry — quota window)"
      deferred=$((deferred+1)); consec=$((consec+1))
      if [ "$consec" -ge 2 ]; then
        echo "  == account-level quota window detected (2 consecutive limited skills) — deferring the rest without touching the API =="
        while read -r rest; do [ -n "$rest" ] || continue
          if [ -n "$FROM" ] && donep "sh:$VER:$head_commit:$rest"; then
            continue
          fi
          echo "  DEFER $rest (quota window)"
          deferred=$((deferred+1))
        done
        break
      fi
    fi
    sleep 40
  done <<< "$SH"
  [ $fail -ne 0 ] && return 1
  if [ $deferred -gt 0 ]; then
    echo "  == SkillHub: $deferred skill(s) deferred to the next ~24h quota window — re-run: bash scripts/publish-registries.sh --live skillhub =="
    return 8
  fi
  return 0
}

run_ch(){ { [ "$PLAT" != skillhub ] && [ -n "$CH" ]; } || return 0
  echo "== ClawHub: publishing $nch behind skill(s) =="; publish_clawhub_set; }
run_sh(){ { [ "$PLAT" != clawhub ] && [ -n "$SH" ]; } || return 0
  echo "== SkillHub: publishing $nsh behind skill(s) (40s spacing, budget $SH_BUDGET) =="; publish_skillhub_set; }

r1=0; r2=0
if [ "$PARALLEL" -eq 1 ] && [ "$PLAT" = both ] && [ "$LIVE" -eq 1 ]; then
  # The two platforms are fully independent (different CLIs, different quotas,
  # state keys prefixed ch:/sh:), so run them concurrently — the ClawHub pass
  # folds entirely into the SkillHub window (~40% wall-clock saved at v18 scale).
  ( set -o pipefail; run_ch 2>&1 | while IFS= read -r l; do printf '[clawhub ] %s\n' "$l"; done ) & p1=$!
  ( set -o pipefail; run_sh 2>&1 | while IFS= read -r l; do printf '[skillhub] %s\n' "$l"; done ) & p2=$!
  wait "$p1"; r1=$?
  wait "$p2"; r2=$?
else
  run_ch; r1=$?
  run_sh; r2=$?
fi

if [ "$LIVE" -eq 0 ]; then echo "dry-run — nothing published. Re-run with --live."; exit 0; fi
if [ "$r1" -eq 1 ] || [ "$r2" -eq 1 ]; then echo "done with failures."; exit 1; fi
if [ "$r1" -eq 8 ] || [ "$r2" -eq 8 ]; then echo "done — quota deferrals pending (exit 8)."; exit 8; fi
echo "==> verifying final remote truth ($PLAT)..."
bash scripts/registry-status.sh --require-current --platform "$PLAT" || {
  echo "FAIL: publish pass ended but the selected remote scope is not fully current" >&2
  exit 1
}
echo "done."
exit 0
