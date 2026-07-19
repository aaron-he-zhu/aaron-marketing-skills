#!/usr/bin/env python3
"""Validate repository-local Markdown link targets without network access."""
from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
EXCLUDED_PARTS = {
    ".git", ".planning", ".agents", ".codex", "reference-oss", "node_modules",
}


def markdown_files():
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if " 2" in path.name or re.search(r"(?:^| )\d+\.md$", path.name):
            continue
        if path.name == "auditor-runtime.md":
            # Generated concatenations inherit documentary source links. Their
            # authoritative source files are checked independently.
            continue
        yield path


def target_value(raw):
    raw = raw.strip()
    if raw.startswith("<"):
        closing = raw.find(">")
        if closing == -1:
            return raw
        return raw[1:closing]
    # Strip an optional Markdown title after the target.
    matched = re.match(r"^(\S+)(?:\s+[\"'].*)?$", raw)
    return matched.group(1) if matched else raw


def main():
    failures = []
    checked = 0
    for path in markdown_files():
        in_fence = False
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            scan_line = re.sub(r"`[^`]*`", "", line)
            for matched in LINK.finditer(scan_line):
                target = target_value(matched.group(1))
                if not target or target.startswith("#"):
                    continue
                if target.startswith("/") and not target.startswith("//"):
                    failures.append(
                        "%s:%d root-absolute link target (use a plugin-relative path): %s"
                        % (path.relative_to(ROOT), line_number, target)
                    )
                    continue
                if SCHEME.match(target) or target.startswith("//"):
                    continue
                if any(marker in target for marker in ("<", ">", "{", "}", "*", "$")):
                    continue
                parsed = urlsplit(target)
                local = unquote(parsed.path)
                if not local:
                    continue
                checked += 1
                resolved = (path.parent / local).resolve()
                try:
                    resolved.relative_to(ROOT.resolve())
                except ValueError:
                    failures.append(
                        "%s:%d local link escapes repository: %s"
                        % (path.relative_to(ROOT), line_number, target)
                    )
                    continue
                if not resolved.exists():
                    failures.append(
                        "%s:%d missing local target: %s"
                        % (path.relative_to(ROOT), line_number, target)
                    )
    if failures:
        print("LOCAL LINK CHECK FAILED: %d issue(s)" % len(failures))
        for failure in failures:
            print("- " + failure)
        return 1
    print("local link check clean: %d targets resolved" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
