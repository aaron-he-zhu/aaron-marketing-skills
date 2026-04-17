#!/usr/bin/env python3
"""Sync version from .claude-plugin/plugin.json to all cross-agent manifests.

Canonical source: .claude-plugin/plugin.json `version`.
Targets:
  - marketplace.json (root) — top-level `version` and `plugins[*].version`
  - gemini-extension.json — top-level `version`
  - qwen-extension.json — top-level `version`
  - .codebuddy-plugin/marketplace.json — top-level `version` and `plugins[*].version`

Usage:
  python3 scripts/sync-versions.py            # apply
  python3 scripts/sync-versions.py --dry-run  # preview, no writes
  python3 scripts/sync-versions.py --help

Exit code: 0 on success (or no-op), 1 on error.

Why targeted paths (not recursive)? Each target has a known, enumerated set of
`version` fields. A blanket recursive bump would accidentally overwrite any
future unrelated `version` key (e.g., a nested schema version). The targeted
approach is predictable and auditable.
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent.resolve()

CANONICAL = ROOT / ".claude-plugin" / "plugin.json"

# Each target: (path, [list of dotted paths to bump]).
# Dotted path syntax: top-level "version", nested "metadata.version",
# list element wildcard "plugins[*].version".
TARGETS = [
    (ROOT / "marketplace.json", ["metadata.version", "plugins[*].version"]),
    (ROOT / "gemini-extension.json", ["version"]),
    (ROOT / "qwen-extension.json", ["version"]),
    (ROOT / ".codebuddy-plugin" / "marketplace.json", ["version", "plugins[*].version"]),
]


def set_path(obj, dotted_path, value):
    """Set a dotted path (supports `plugins[*].version` list wildcard). Returns count of writes."""
    parts = dotted_path.split(".")
    return _walk(obj, parts, value)


def _walk(cur, parts, value):
    if not parts:
        return 0
    head, *rest = parts
    if head.endswith("[*]"):
        key = head[:-3]
        if not isinstance(cur, dict) or key not in cur or not isinstance(cur[key], list):
            return 0
        return sum(_walk(item, rest, value) for item in cur[key])
    if not rest:
        if isinstance(cur, dict) and head in cur:
            if cur[head] != value:
                cur[head] = value
                return 1
        return 0
    if isinstance(cur, dict) and head in cur:
        return _walk(cur[head], rest, value)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Sync version across cross-agent manifests.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    args = parser.parse_args()

    if not CANONICAL.exists():
        print(f"ERROR: canonical source not found: {CANONICAL}", file=sys.stderr)
        return 1

    canonical_data = json.loads(CANONICAL.read_text())
    version = canonical_data.get("version")
    if not version:
        print(f"ERROR: no `version` field in {CANONICAL}", file=sys.stderr)
        return 1

    mode = "[dry-run] " if args.dry_run else ""
    print(f"{mode}Target version: {version}")

    changed_files = 0
    for target, paths in TARGETS:
        if not target.exists():
            print(f"  skip    {target.relative_to(ROOT)} (not found)")
            continue

        data = json.loads(target.read_text())
        writes = sum(set_path(data, p, version) for p in paths)
        if writes:
            changed_files += 1
            if args.dry_run:
                print(f"  would-update {target.relative_to(ROOT)} ({writes} field(s))")
            else:
                target.write_text(json.dumps(data, indent=2) + "\n")
                print(f"  updated     {target.relative_to(ROOT)} ({writes} field(s))")
        else:
            print(f"  ok          {target.relative_to(ROOT)}")

    print(f"{mode}Done. {changed_files} file(s) {'would change' if args.dry_run else 'changed'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
