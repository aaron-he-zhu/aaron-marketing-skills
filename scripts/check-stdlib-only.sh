#!/usr/bin/env bash
# Dependency-creep guard — the moat protector.
#
# This project's contract: the ONLY allowed code is the bash validator + Python
# *stdlib-only* connector/check helpers. No pip / third-party deps, ever. This
# guard fails CLOSED: every top-level module imported by scripts/*.py and
# scripts/connectors/*.py and scripts/adapters/*.py must be on the ALLOWLIST — (a) the Python standard
# library (sys.stdlib_module_names, queried from the interpreter at runtime) or
# (b) a local module in those same directories (derived from the .py filenames,
# e.g. _http, robots). Anything else — numpy, requests, yaml, or a brand-new
# package no denylist has heard of — fails the build, naming file and module.
#
# Run: bash scripts/check-stdlib-only.sh   (exit 0 = clean, 1 = violation)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Fail CLOSED on a dead glob: if any scanned location stops matching files the
# guard must abort, not silently pass with an empty scan set (the historical
# "scans a directory that no longer exists" bug class).
for pat in "scripts/*.py" "scripts/connectors/*.py" "scripts/adapters/*.py" "tests/*.py"; do
  compgen -G "$pat" > /dev/null || { echo "MOAT GUARD MISCONFIGURED — no files match '$pat'"; exit 1; }
done

# (a) Python stdlib module names, straight from the interpreter (no hardcoded list).
STDLIB="$(python3 -c "import sys;print('\n'.join(sorted(sys.stdlib_module_names)))")"

# (b) The repo's own local modules: one name per .py file in the checked dirs.
LOCAL=""
for f in scripts/*.py scripts/connectors/*.py scripts/adapters/*.py tests/*.py; do
  [ -e "$f" ] || continue
  LOCAL="${LOCAL}$(basename "$f" .py)"$'\n'
done

violations=""
for f in scripts/*.py scripts/connectors/*.py scripts/adapters/*.py tests/*.py; do
  [ -e "$f" ] || continue
  # Emit "lineno:module" for every import statement via the stdlib ast parser —
  # handles `import a, b`, `import a.b as c`, `from a.b import x`, and indented
  # (in-function) imports, while ignoring docstrings/comments (a line-based grep
  # would trip on prose like "from a fetched page ..."). Relative imports
  # (`from .x import y`) are local by definition and skipped. A file that fails
  # to parse emits a sentinel so the guard still fails closed.
  while IFS=: read -r ln mod; do
    [ -n "$mod" ] || continue
    if ! grep -qxF "$mod" <<<"$STDLIB" && ! grep -qxF "$mod" <<<"$LOCAL"; then
      violations="${violations}${f}:${ln}: import of '${mod}' is neither Python stdlib nor a local scripts/ module"$'\n'
    fi
  done < <(python3 -c '
import ast, sys
path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
except Exception:
    # Any read/parse failure (SyntaxError, ValueError, RecursionError,
    # UnicodeDecodeError, ...) emits the sentinel so the guard fails closed.
    print("0:UNPARSEABLE_FILE")  # not stdlib, not local -> guard fails closed
    sys.exit(0)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            print("%d:%s" % (node.lineno, alias.name.split(".")[0]))
    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
        print("%d:%s" % (node.lineno, node.module.split(".")[0]))
' "$f")
done

if [ -n "$violations" ]; then
  echo "DEPENDENCY-CREEP VIOLATION — non-allowlisted import(s) found under scripts/:"
  printf '%s' "$violations"
  echo ""
  echo "Only the Python standard library (plus the repo's own scripts/ modules) is allowed. Reimplement with stdlib (urllib, json, re, csv, html.parser, ...) or drop the dependency."
  exit 1
fi

# --- Paid Ads red line: a paid SKILL.md must never require a keyed ad-platform API at Tier 1 ---
[ -d ad ] || { echo "MOAT GUARD MISCONFIGURED — ad/ discipline dir missing (red-line scan has no target)"; exit 1; }
# Best-effort prose tripwire (heuristic; a sentence mixing "required" with an exonerating word on the
# same line can evade it). The real guarantee is the keyless/own-export framing authored into each skill.
ad_hits="$(grep -rnEi "(google ads|meta( marketing)?|ads platform|marketing) api" --include='SKILL.md' ad/ 2>/dev/null \
  | grep -Ei "require|must have|tier.?1|precondition|necessary" \
  | grep -Eiv "optional|opt-in|tier.?2|tier.?3|mcp|never|not required|own[ -]data|manual export" || true)"
if [ -n "$ad_hits" ]; then
  echo "PAID-ADS RED-LINE VIOLATION — a paid SKILL.md phrases a keyed ad-platform API as required/Tier-1:"
  echo "$ad_hits"
  echo ""
  echo "Paid Ads must score from own-account manual export at Tier 1; keyed ad APIs are opt-in Tier-2/3 MCP only."
  exit 1
fi

echo "moat guard clean — no third-party imports under scripts/, no required keyed ad APIs in ad/."
exit 0
