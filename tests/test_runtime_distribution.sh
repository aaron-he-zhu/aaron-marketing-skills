#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

resolve_root() {
  local resolved
  resolved="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
  [ -f "$resolved/.claude-plugin/plugin.json" ] || return 1
  [ -f "$resolved/references/system-catalog.json" ] || return 1
  [ -f "$resolved/references/registry-event.schema.json" ] || return 1
  [ -f "$resolved/references/run-event.schema.json" ] || return 1
  [ -f "$resolved/scripts/registry-events.py" ] || return 1
  [ -f "$resolved/scripts/run-events.py" ] || return 1
  printf '%s\n' "$resolved"
}

# Claude Code plugin mode: the host-provided root wins even outside a Git checkout.
mkdir -p "$TMP/plugin-cwd"
plugin_resolved="$(cd "$TMP/plugin-cwd" && CLAUDE_PLUGIN_ROOT="$ROOT" resolve_root)"
[ "$plugin_resolved" = "$ROOT" ]

# Full-clone mode: a nested skill resolves to this repository's top level.
clone_resolved="$(cd "$ROOT/narrative/evaluate/narrative-quality-auditor" && unset CLAUDE_PLUGIN_ROOT && resolve_root)"
[ "$clone_resolved" = "$ROOT" ]

# Standalone one-folder mode: no root catalogs/runtimes means a fail-closed result.
mkdir -p "$TMP/standalone/references"
cp "$ROOT/narrative/evaluate/narrative-quality-auditor/SKILL.md" "$TMP/standalone/SKILL.md"
cp "$ROOT/narrative/evaluate/narrative-quality-auditor/references/auditor-runtime.md" "$TMP/standalone/references/auditor-runtime.md"
if (cd "$TMP/standalone" && unset CLAUDE_PLUGIN_ROOT && resolve_root >/dev/null 2>&1); then
  echo "standalone skill unexpectedly resolved a root runtime" >&2
  exit 1
fi

# All four root entry points are present and executable through the resolved root.
python3 "$plugin_resolved/scripts/rubric-score.py" check-catalog >/dev/null
python3 "$plugin_resolved/scripts/validate-audit-artifact.py" --help >/dev/null
python3 "$plugin_resolved/scripts/registry-events.py" --help >/dev/null
python3 "$plugin_resolved/scripts/run-events.py" --help >/dev/null

# Registry instructions use the same host-root resolution and never leave a
# runnable working-directory-relative registry command behind.
registry_skills=(
  entity-registry creator-registry offer-claims-registry consent-registry
  channel-registry launch-registry narrative-registry memory-management
)
for skill in "${registry_skills[@]}"; do
  grep -Fq 'AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"' \
    "$ROOT/protocol/$skill/SKILL.md"
done
# grep, not rg: a missing optional tool must not fail-open this negative guard.
if grep -rEn 'python3[[:space:]]+scripts/registry-events\.py' \
    "$ROOT/protocol" "$ROOT/references" >/dev/null; then
  echo "found a working-directory-relative registry runtime example" >&2
  exit 1
fi

echo "runtime distribution contract clean: plugin, full clone, standalone fail-closed"
