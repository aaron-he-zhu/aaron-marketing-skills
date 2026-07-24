#!/usr/bin/env bash
# publish-package.sh — publish the whole plugin to ClawHub as an OpenClaw
# bundle-plugin package.
#
# Live publishing is only allowed from the verified Governed distribution
# build. Name/version/display come from openclaw.plugin.json +
# .claude-plugin/plugin.json. Dry-run remains the default.
#
# --from-build publishes the minimal plugin profile built by
# scripts/build-distribution.py (references/distribution-files.json closure —
# no docs/evals/tests) from a fresh temp directory. It is mandatory for live
# publishing; the full git archive first exceeded ClawHub's upload limit at
# v17.0.0 (413 Request Entity Too Large). The same committed-HEAD guardrails
# apply, so the live profile is generated from a private export of what GitHub
# serves.
#
# Usage:
#   bash scripts/publish-package.sh                     # dry-run: show the file set + metadata
#   bash scripts/publish-package.sh --from-build --live # publish the built minimal profile
#
# Requires: openclaw.plugin.json committed at HEAD, HEAD pushed to origin, and the
# `clawhub` CLI logged in. Owner-run, never CI. See docs/distribution.md.
set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"
source scripts/publish-common.sh

LIVE=0; FROM_BUILD=0
while [ $# -gt 0 ]; do
  case "$1" in
    --live) LIVE=1 ;;
    --dry-run) LIVE=0 ;;
    --from-build) FROM_BUILD=1 ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--from-build] [--live]" >&2; exit 1 ;;
  esac
  shift
done

command -v clawhub >/dev/null 2>&1 || { echo "FAIL: clawhub CLI not found/logged in" >&2; exit 2; }
[ -f openclaw.plugin.json ] || { echo "FAIL: openclaw.plugin.json missing at repo root" >&2; exit 1; }

if [ "$LIVE" -eq 1 ]; then
  RELEASE_IDENTITY="$(publish_require_release_identity)" || exit 1
  REPO_SLUG="${RELEASE_IDENTITY%%$'\t'*}"
  COMMIT="${RELEASE_IDENTITY#*$'\t'}"
  publish_require_expected_release_identity "$REPO_SLUG" "$COMMIT" || exit 1
  [ "$FROM_BUILD" -eq 1 ] || {
    echo "FAIL: live package publishing requires --from-build so only the verified Governed distribution is uploaded" >&2
    exit 1
  }
  publish_require_final_release "$REPO_SLUG" "$COMMIT" || exit 1
else
  REPO_SLUG="$(publish_repo_slug)" || exit 1
  COMMIT="$(git rev-parse --verify 'HEAD^{commit}' 2>/dev/null)" || {
    echo "FAIL: cannot resolve HEAD for the package dry-run" >&2
    exit 1
  }
fi
OWNER="${REPO_SLUG%%/*}"
# Live metadata is read from the exact clean, freshly verified commit rather
# than reopening mutable worktree paths after the provenance check.
if [ "$LIVE" -eq 1 ]; then
  PLUGIN_JSON="$(git show "${COMMIT}:.claude-plugin/plugin.json" 2>/dev/null)" || {
    echo "FAIL: .claude-plugin/plugin.json is not committed at $COMMIT" >&2; exit 1;
  }
  OPENCLAW_JSON="$(git show "${COMMIT}:openclaw.plugin.json" 2>/dev/null)" || {
    echo "FAIL: openclaw.plugin.json is not committed at $COMMIT" >&2; exit 1;
  }
else
  PLUGIN_JSON="$(/bin/cat .claude-plugin/plugin.json)" || exit 1
  OPENCLAW_JSON="$(/bin/cat openclaw.plugin.json)" || exit 1
fi
VER="$(printf '%s' "$PLUGIN_JSON" | /usr/bin/python3 -c 'import json,sys;print(json.load(sys.stdin)["version"])')" || exit 1
NAME="$(printf '%s' "$OPENCLAW_JSON" | /usr/bin/python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["id"])')" || exit 1
DISPLAY="$(printf '%s' "$OPENCLAW_JSON" | /usr/bin/python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("name",d["id"]))')" || exit 1
mv="$(printf '%s' "$OPENCLAW_JSON" | /usr/bin/python3 -c 'import json,sys;print(json.load(sys.stdin)["version"])')" || exit 1
[ "$mv" = "$VER" ] || { echo "FAIL: openclaw.plugin.json version $mv != bundle $VER" >&2; exit 1; }

SOURCE="$REPO_SLUG@$COMMIT"
BUILD_DIR=""; PINNED_SOURCE=""; CONTENT_DIGEST=""
if [ "$FROM_BUILD" -eq 1 ]; then
  BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/aaron-plugin-build.XXXXXX")" || {
    echo "FAIL: cannot create a private package build directory" >&2
    exit 1
  }
  trap '[ -n "${BUILD_DIR:-}" ] && rm -rf -- "$BUILD_DIR"' EXIT
  if [ "$LIVE" -eq 1 ]; then
    PINNED_SOURCE="$BUILD_DIR/source"
    publish_prepare_pinned_source "$PINNED_SOURCE" "$COMMIT" || exit 1
    (
      cd "$PINNED_SOURCE" || exit 1
      /usr/bin/python3 scripts/build-distribution.py --plugin --profile governed \
        --output "$BUILD_DIR/pkg" \
        --source-repository "$REPO_SLUG" --source-commit "$COMMIT"
      /usr/bin/python3 scripts/build-distribution.py --verify-manifest "$BUILD_DIR/pkg" \
        --source-repository "$REPO_SLUG" --source-commit "$COMMIT"
    ) || { echo "FAIL: pinned plugin distribution build or verification failed" >&2; exit 1; }
  else
    /usr/bin/python3 scripts/build-distribution.py --plugin --profile governed \
      --output "$BUILD_DIR/pkg" \
      || { echo "FAIL: governed plugin distribution build failed" >&2; exit 1; }
    /usr/bin/python3 scripts/build-distribution.py --verify-manifest "$BUILD_DIR/pkg" \
      || { echo "FAIL: built plugin distribution verification failed" >&2; exit 1; }
  fi
  if [ "$LIVE" -eq 1 ]; then
    CONTENT_DIGEST="$(/usr/bin/python3 - "$BUILD_DIR/pkg/distribution-manifest.json" "$REPO_SLUG" "$COMMIT" <<'PY'
import json
from pathlib import Path
import re
import sys

path, repository, commit = sys.argv[1:]
try:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
except (OSError, UnicodeDecodeError, ValueError) as exc:
    print("FAIL: cannot read verified distribution content identity: %s" % exc, file=sys.stderr)
    raise SystemExit(1)
digest = manifest.get("files_sha256")
if (manifest.get("profile") != "governed"
        or manifest.get("source") != {"repository": repository, "commit": commit}
        or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
    print("FAIL: verified distribution content identity is incomplete", file=sys.stderr)
    raise SystemExit(1)
print(digest)
PY
    )" || exit 1
  fi
  SOURCE="$BUILD_DIR/pkg"
fi

echo "Package : $NAME@$VER  (family bundle-plugin, owner $OWNER)"
if [ "$FROM_BUILD" -eq 1 ]; then
  echo "Source  : built verified minimal profile from HEAD $COMMIT ($SOURCE)"
else
  echo "Source  : github:$SOURCE"
fi
echo "Mode    : $([ $LIVE -eq 1 ] && echo LIVE || echo dry-run)"

cmd=(clawhub package publish "$SOURCE"
     --family bundle-plugin --name "$NAME" --display-name "$DISPLAY"
     --owner "$OWNER" --version "$VER"
     --source-repo "$REPO_SLUG" --source-commit "$COMMIT"
     --changelog "aaron-marketing bundle-plugin @ $VER — 120 skills + 8 commands, seven disciplines + protocol layer.")
[ "$LIVE" -eq 0 ] && cmd+=(--dry-run)

out=$("${cmd[@]}" 2>&1); rc=$?
printf '%s\n' "$out"
# A transport error AFTER the upload landed is indistinguishable from a failed
# upload by exit code alone. Recovery therefore inspects the exact version and
# its remotely served distribution manifest. Version alone is insufficient:
# source repository/commit and files_sha256 must all match this pinned build.
# Older CLIs that cannot return these fields fail closed.
if [ "$LIVE" -eq 1 ] && [ "$rc" -ne 0 ]; then
  remote_inspect="$BUILD_DIR/remote-inspect.json"
  if clawhub package inspect "$NAME" --version "$VER" \
      --file distribution-manifest.json --json > "$remote_inspect" 2>/dev/null \
      && /usr/bin/python3 - "$remote_inspect" "$NAME" "$VER" "$REPO_SLUG" \
        "$COMMIT" "$CONTENT_DIGEST" <<'PY'
import json
from pathlib import Path
import re
import stat
import sys

path, name, version, repository, commit, digest = sys.argv[1:]
try:
    status = Path(path).lstat()
    if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1 or status.st_size > 500_000:
        raise ValueError("inspect output is not a bounded regular file")
    remote = json.loads(Path(path).read_text(encoding="utf-8"))
except (OSError, UnicodeDecodeError, ValueError) as exc:
    print("FAIL: remote package identity is unavailable: %s" % exc, file=sys.stderr)
    raise SystemExit(1)

package = remote.get("package")
selected = remote.get("version")
file_record = remote.get("file")
if (not isinstance(package, dict) or package.get("name") != name
        or not isinstance(selected, dict) or selected.get("version") != version):
    print("FAIL: remote package name/version does not match the attempted upload", file=sys.stderr)
    raise SystemExit(1)
verification = selected.get("verification")
if (not isinstance(verification, dict)
        or verification.get("sourceRepo") != repository
        or verification.get("sourceCommit") != commit):
    print("FAIL: remote package source repository/commit is absent or mismatched", file=sys.stderr)
    raise SystemExit(1)
if (not isinstance(file_record, dict)
        or file_record.get("path") != "distribution-manifest.json"
        or not isinstance(file_record.get("content"), str)):
    print("FAIL: remote package cannot return its distribution manifest", file=sys.stderr)
    raise SystemExit(1)
try:
    manifest = json.loads(file_record["content"])
except ValueError:
    print("FAIL: remote distribution manifest is invalid JSON", file=sys.stderr)
    raise SystemExit(1)
if (manifest.get("profile") != "governed"
        or manifest.get("source") != {"repository": repository, "commit": commit}
        or manifest.get("files_sha256") != digest
        or not re.fullmatch(r"[0-9a-f]{64}", digest)):
    print("FAIL: remote package content digest/source identity does not match the pinned build", file=sys.stderr)
    raise SystemExit(1)
PY
  then
    echo "NOTE: CLI reported a transport error, but $NAME@$VER is live with matching source commit and content digest — treating as success."
    exit 0
  fi
  echo "FAIL: package publish errored and exact remote source/content identity could not be confirmed" >&2
  exit 1
fi
exit $rc
