#!/usr/bin/env python3
"""Sync version from .claude-plugin/plugin.json to all cross-agent manifests.

Canonical source: .claude-plugin/plugin.json `version`.
Targets:
  - marketplace.json (root)
  - gemini-extension.json
  - qwen-extension.json
  - .codebuddy-plugin/marketplace.json

Usage: python3 scripts/sync-versions.py
Exit code: 0 on success (or no-op), 1 on error.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent.resolve()

CANONICAL = ROOT / ".claude-plugin" / "plugin.json"
TARGETS = [
    ROOT / "marketplace.json",
    ROOT / "gemini-extension.json",
    ROOT / "qwen-extension.json",
    ROOT / ".codebuddy-plugin" / "marketplace.json",
]


def bump_version(obj, version):
    """Recursively set every `version` key to the target value. Returns True if changed."""
    changed = False
    if isinstance(obj, dict):
        if "version" in obj and obj["version"] != version:
            obj["version"] = version
            changed = True
        for value in obj.values():
            if bump_version(value, version):
                changed = True
    elif isinstance(obj, list):
        for item in obj:
            if bump_version(item, version):
                changed = True
    return changed


def main():
    if not CANONICAL.exists():
        print(f"ERROR: canonical source not found: {CANONICAL}", file=sys.stderr)
        return 1

    canonical_data = json.loads(CANONICAL.read_text())
    version = canonical_data.get("version")
    if not version:
        print(f"ERROR: no `version` field in {CANONICAL}", file=sys.stderr)
        return 1

    print(f"Target version: {version}")

    for target in TARGETS:
        if not target.exists():
            print(f"  skip    {target.relative_to(ROOT)} (not found)")
            continue

        data = json.loads(target.read_text())
        if bump_version(data, version):
            target.write_text(json.dumps(data, indent=2) + "\n")
            print(f"  updated {target.relative_to(ROOT)}")
        else:
            print(f"  ok      {target.relative_to(ROOT)}")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
