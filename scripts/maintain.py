#!/usr/bin/env python3
"""Refresh authored-source projections in dependency order; never bump or publish.

The generators stay independent programs with their own validation and --check.
This is an ordered list, not a task engine or a second CI policy.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GENERATORS = (
    "generate-release-surfaces.py",
    "generate-system-docs.py",
    "generate-claude-index.py",
    "generate-auto-routing-shards.py",
    "generate-auditor-runtime.py",
    "workflow-graph.py",
    "generate-skill-contracts.py",
    "generate-auditor-prompt-contracts.py",
)


def refresh(root=ROOT, *, write=False, list_only=False):
    mode = "--write" if write else "--check"
    for name in GENERATORS:
        script = Path(root) / "scripts" / name
        if not script.is_file():
            raise ValueError("required generator is missing: scripts/%s" % name)
    for name in GENERATORS:
        command = [sys.executable, str(Path(root) / "scripts" / name), mode]
        print("%s scripts/%s" % (mode[2:].upper(), name), flush=True)
        if list_only:
            continue
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Regenerate the existing projections.")
    mode.add_argument("--check", action="store_true", help="Check all projections (the default).")
    parser.add_argument("--list", action="store_true", help="Print the ordered commands without running them.")
    args = parser.parse_args(argv)
    try:
        return refresh(write=args.write, list_only=args.list)
    except (OSError, ValueError) as exc:
        print("MAINTENANCE FAILED: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
