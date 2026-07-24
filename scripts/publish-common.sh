#!/usr/bin/env bash
# Shared fail-closed provenance/build helpers for owner-run live publishers.

publish_origin_url() {
  local remote count
  remote="$(git config --get-all remote.origin.url 2>/dev/null)" || {
    echo "FAIL: cannot resolve the origin remote" >&2
    return 1
  }
  count="$(printf '%s\n' "$remote" | /usr/bin/python3 -c 'import sys; print(len(sys.stdin.read().splitlines()))')" || return 1
  [ "$count" = "1" ] && [ -n "$remote" ] || {
    echo "FAIL: origin must have exactly one URL" >&2
    return 1
  }
  printf '%s\n' "$remote"
}

publish_parse_github_slug() {
  /usr/bin/python3 - "$1" <<'PY'
import re
import sys

remote = sys.argv[1]
segment = r"[A-Za-z0-9_.-]+"
patterns = (
    rf"https://github\.com/(?P<owner>{segment})/(?P<repo>{segment}?)(?:\.git)?",
    rf"ssh://git@github\.com/(?P<owner>{segment})/(?P<repo>{segment}?)(?:\.git)?",
    rf"git@github\.com:(?P<owner>{segment})/(?P<repo>{segment}?)(?:\.git)?",
)
matched = next((re.fullmatch(pattern, remote) for pattern in patterns
                if re.fullmatch(pattern, remote)), None)
if matched is None:
    raise SystemExit(1)
owner, repo = matched.group("owner"), matched.group("repo")
if owner in {".", ".."} or repo in {".", ".."}:
    raise SystemExit(1)
print(f"{owner}/{repo}")
PY
}

publish_repo_slug() {
  local remote slug
  remote="$(publish_origin_url)" || return 1
  slug="$(publish_parse_github_slug "$remote")" || {
    echo "FAIL: origin must be a canonical github.com HTTPS, SSH, or scp URL" >&2
    return 1
  }
  printf '%s\n' "$slug"
}

publish_require_release_identity() {
  local commit post_remote post_rewrites remote remote_commit repo rewrites
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "FAIL: live publishing requires a Git worktree" >&2
    return 1
  }
  [ -z "$(git status --porcelain=v1 --untracked-files=all)" ] || {
    echo "FAIL: working tree is dirty — commit or remove every tracked/untracked change before live publishing" >&2
    return 1
  }
  remote="$(publish_origin_url)" || return 1
  repo="$(publish_parse_github_slug "$remote")" || {
    echo "FAIL: origin must be a canonical github.com HTTPS, SSH, or scp URL" >&2
    return 1
  }
  rewrites="$(git config --get-regexp '^url\..*\.insteadof$' 2>/dev/null || true)"
  [ -z "$rewrites" ] || {
    echo "FAIL: Git URL rewrite rules are not allowed for live publishing" >&2
    return 1
  }
  commit="$(git rev-parse --verify 'HEAD^{commit}' 2>/dev/null)" || {
    echo "FAIL: cannot resolve HEAD to a commit" >&2
    return 1
  }

  # Fetch the already validated literal URL, not the mutable remote name. The
  # explicit refspec also makes the refreshed comparison ref unambiguous.
  git fetch -q -- "$remote" '+refs/heads/main:refs/remotes/origin/main' || {
    echo "FAIL: cannot refresh origin/main; refusing unverifiable live publishing" >&2
    return 1
  }
  remote_commit="$(git rev-parse --verify 'refs/remotes/origin/main^{commit}' 2>/dev/null)" || {
    echo "FAIL: cannot resolve the refreshed origin/main commit" >&2
    return 1
  }
  git merge-base --is-ancestor "$commit" "$remote_commit" 2>/dev/null || {
    echo "FAIL: HEAD $commit is not reachable from origin/main $remote_commit — push it first" >&2
    return 1
  }

  # The returned tuple is one release identity.  Recheck the mutable Git
  # configuration before exposing it so a concurrent origin/rewrite switch
  # cannot splice a repository slug from one gate onto another commit.
  post_remote="$(publish_origin_url)" || return 1
  post_rewrites="$(git config --get-regexp '^url\..*\.insteadof$' 2>/dev/null || true)"
  [ "$post_remote" = "$remote" ] && [ -z "$post_rewrites" ] || {
    echo "FAIL: origin or Git URL rewrites changed during the release gate" >&2
    return 1
  }
  printf '%s\t%s\n' "$repo" "$commit"
}

publish_require_expected_release_identity() {
  local repo commit expected_repo expected_commit
  repo="$1"
  commit="$2"
  expected_repo="${AARON_PUBLISH_EXPECTED_REPO:-}"
  expected_commit="${AARON_PUBLISH_EXPECTED_COMMIT:-}"
  if [ -z "$expected_repo" ] && [ -z "$expected_commit" ]; then
    return 0
  fi
  [ -n "$expected_repo" ] && [ -n "$expected_commit" ] || {
    echo "FAIL: inherited release identity must provide both repository and commit" >&2
    return 1
  }
  [ "$repo" = "$expected_repo" ] && [ "$commit" = "$expected_commit" ] || {
    echo "FAIL: live child release identity $repo@$commit does not match parent $expected_repo@$expected_commit" >&2
    return 1
  }
}

publish_release_version_at_commit() {
  local commit plugin_json
  commit="$1"
  plugin_json="$(git show "${commit}:.claude-plugin/plugin.json" 2>/dev/null)" || {
    echo "FAIL: cannot read the committed plugin version at $commit" >&2
    return 1
  }
  printf '%s' "$plugin_json" | /usr/bin/python3 -c '
import json
import re
import sys
value = json.load(sys.stdin).get("version")
if not isinstance(value, str) or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value) is None:
    raise SystemExit("committed plugin version is not numeric semver")
print(value)
' || {
    echo "FAIL: committed plugin version is invalid" >&2
    return 1
  }
}

publish_final_gate_token() {
  /usr/bin/python3 - "$1" "$2" "$3" "$4" <<'PY'
import hashlib
import sys

print(hashlib.sha256("\0".join(sys.argv[1:]).encode("utf-8")).hexdigest())
PY
}

publish_require_final_release() {
  local repo commit version receipt receipt_identity receipt_sha release_candidate receipt_commit
  local gate_token inherited_token tag tag_commit release_json runs_json asset_root
  repo="$1"
  commit="$2"
  version="$(publish_release_version_at_commit "$commit")" || return 1
  if [ "${version%%.*}" -lt 19 ]; then
    return 0
  fi
  receipt="${AARON_RELEASE_RECEIPT:-}"
  [ -n "$receipt" ] || {
    echo "FAIL: v19 live distribution requires AARON_RELEASE_RECEIPT" >&2
    return 1
  }
  receipt_identity="$(/usr/bin/python3 scripts/verify-release-receipt.py \
    "$receipt" \
    --source-commit "$commit" \
    --release-version "$version" \
    --verifier scripts/verify-profile-outcomes.py)" || return 1
  IFS=$'\t' read -r receipt_sha release_candidate receipt_commit <<< "$receipt_identity"
  [ -n "$receipt_sha" ] && [ -n "$release_candidate" ] && [ "$receipt_commit" = "$commit" ] || {
    echo "FAIL: private release receipt identity is malformed" >&2
    return 1
  }
  gate_token="$(publish_final_gate_token "$repo" "$commit" "$version" "$receipt_sha")" || return 1
  inherited_token="${AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN:-}"
  if [ -n "$inherited_token" ]; then
    [ -n "${AARON_PUBLISH_EXPECTED_REPO:-}" ] \
      && [ -n "${AARON_PUBLISH_EXPECTED_COMMIT:-}" ] \
      && [ "$repo" = "$AARON_PUBLISH_EXPECTED_REPO" ] \
      && [ "$commit" = "$AARON_PUBLISH_EXPECTED_COMMIT" ] \
      && [ "$inherited_token" = "$gate_token" ] || {
        echo "FAIL: inherited final-release gate does not match this child" >&2
        return 1
      }
    PUBLISH_FINAL_GATE_TOKEN="$gate_token"
    return 0
  fi

  command -v gh >/dev/null 2>&1 || {
    echo "FAIL: GitHub CLI is required to verify the final release" >&2
    return 1
  }
  tag="v$version"
  tag_commit="$(gh api "repos/$repo/commits/$tag" --jq .sha 2>/dev/null)" || {
    echo "FAIL: cannot resolve immutable GitHub tag $tag" >&2
    return 1
  }
  [ "$tag_commit" = "$commit" ] || {
    echo "FAIL: GitHub tag $tag resolves to $tag_commit, not $commit" >&2
    return 1
  }
  release_json="$(gh release view "$tag" --repo "$repo" \
    --json tagName,isDraft,isPrerelease 2>/dev/null)" || {
    echo "FAIL: final GitHub release $tag does not exist" >&2
    return 1
  }
  RELEASE_JSON="$release_json" /usr/bin/python3 - "$tag" <<'PY' || {
import json
import os
import sys

value = json.loads(os.environ["RELEASE_JSON"])
if (
    not isinstance(value, dict)
    or set(value) != {"tagName", "isDraft", "isPrerelease"}
    or value["tagName"] != sys.argv[1]
    or value["isDraft"] is not False
    or value["isPrerelease"] is not False
):
    raise SystemExit("release is missing, draft, prerelease, or has the wrong tag")
PY
    echo "FAIL: GitHub release $tag is not an immutable final release" >&2
    return 1
  }
  runs_json="$(gh api --method GET \
    "repos/$repo/actions/workflows/release-validation.yml/runs?head_sha=$commit&status=completed&per_page=100" \
    2>/dev/null)" || {
    echo "FAIL: cannot inspect release-validation workflow runs" >&2
    return 1
  }
  RELEASE_RUNS_JSON="$runs_json" /usr/bin/python3 - "$commit" <<'PY' || {
import json
import os
import sys

value = json.loads(os.environ["RELEASE_RUNS_JSON"])
runs = value.get("workflow_runs") if isinstance(value, dict) else None
if not isinstance(runs, list) or not any(
    isinstance(run, dict)
    and run.get("head_sha") == sys.argv[1]
    and run.get("conclusion") == "success"
    and run.get("event") == "workflow_dispatch"
    for run in runs
):
    raise SystemExit("no successful owner-run release validation exists for this commit")
PY
    echo "FAIL: release validation is not green on $commit" >&2
    return 1
  }

  asset_root="$(mktemp -d "${TMPDIR:-/tmp}/aaron-release-assets.XXXXXX")" || {
    echo "FAIL: cannot create a private release verification directory" >&2
    return 1
  }
  if ! gh release download "$tag" --repo "$repo" --dir "$asset_root" >/dev/null 2>&1; then
    rm -rf -- "$asset_root"
    echo "FAIL: cannot download the final GitHub release assets" >&2
    return 1
  fi
  if ! /usr/bin/python3 scripts/build-release-assets.py \
    --verify "$asset_root" \
    --source-repo . \
    --source-repository "$repo" \
    --source-commit "$commit" \
    --version "$version" >/dev/null; then
    rm -rf -- "$asset_root"
    echo "FAIL: GitHub release assets do not match the exact release commit" >&2
    return 1
  fi
  rm -rf -- "$asset_root"
  PUBLISH_FINAL_GATE_TOKEN="$gate_token"
  echo "Final release gate: $repo@$commit ($tag, $release_candidate, assets and CI verified)" >&2
}

publish_require_release_provenance() {
  local identity
  identity="$(publish_require_release_identity)" || return 1
  printf '%s\n' "${identity#*$'\t'}"
}

publish_prepare_pinned_source() {
  local destination commit archive
  destination="$1"
  commit="$2"
  archive="${destination}.git-archive.tar"
  [ ! -e "$destination" ] && [ ! -L "$destination" ] || {
    echo "FAIL: pinned source destination already exists: $destination" >&2
    return 1
  }
  git cat-file -e "${commit}^{commit}" 2>/dev/null || {
    echo "FAIL: pinned source commit is unavailable: $commit" >&2
    return 1
  }
  (umask 077 && mkdir -m 700 -- "$destination") || {
    echo "FAIL: cannot create private pinned source directory" >&2
    return 1
  }
  if ! git archive --format=tar --output="$archive" "$commit"; then
    rm -f -- "$archive"
    rm -rf -- "$destination"
    echo "FAIL: cannot export pinned source commit $commit" >&2
    return 1
  fi
  if ! tar -xf "$archive" -C "$destination"; then
    rm -f -- "$archive"
    rm -rf -- "$destination"
    echo "FAIL: cannot unpack pinned source commit $commit" >&2
    return 1
  fi
  rm -f -- "$archive"
  if [ -n "$(find "$destination" -type l -print -quit)" ]; then
    rm -rf -- "$destination"
    echo "FAIL: pinned source archive contains a symbolic link" >&2
    return 1
  fi
  [ -f "$destination/scripts/build-distribution.py" ] || {
    rm -rf -- "$destination"
    echo "FAIL: pinned source is missing scripts/build-distribution.py" >&2
    return 1
  }
}

publish_prepare_release_source() {
  local destination identity repo commit
  destination="$1"
  identity="$(publish_require_release_identity)" || return 1
  repo="${identity%%$'\t'*}"
  commit="${identity#*$'\t'}"
  [ -n "$repo" ] && [ -n "$commit" ] && [ "$repo" != "$commit" ] || {
    echo "FAIL: release identity is malformed" >&2
    return 1
  }
  publish_require_expected_release_identity "$repo" "$commit" || return 1
  publish_require_final_release "$repo" "$commit" || return 1
  publish_prepare_pinned_source "$destination" "$commit" || return 1
  printf '%s\t%s\n' "$repo" "$commit"
}

publish_build_verified_skill() {
  local skill_path output repo commit source_root
  skill_path="$1"
  output="$2"
  repo="$3"
  commit="$4"
  source_root="${5:-.}"
  (
    cd "$source_root" || exit 1
    /usr/bin/python3 scripts/build-distribution.py \
      --output "$output" \
      --skill "$skill_path" \
      --source-repository "$repo" \
      --source-commit "$commit" >&2
  ) || return 1
  (
    cd "$source_root" || exit 1
    /usr/bin/python3 scripts/build-distribution.py \
      --verify-manifest "$output" \
      --source-repository "$repo" \
      --source-commit "$commit" >&2
  ) || return 1
  [ -f "$output/distribution-manifest.json" ] || {
    echo "FAIL: verified distribution manifest is missing for $skill_path" >&2
    return 1
  }
}
