#!/usr/bin/env python3
"""Fail-closed maintenance-wiki lint — Python 3 stdlib only.

Checks references/wiki/ frontmatter, index coverage, stale dates, and the
runtime-exclusion rule: wiki must not enter Skill Runtime Reads, context
modules, or distribution allowlists.

Usage:
  python3 scripts/check-wiki.py   # CI / weekly lint; exit 1 on fail
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "references" / "wiki"
SCHEMA = WIKI / "SCHEMA.md"
INDEX = WIKI / "index.md"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
CONTEXT_MODULES = ROOT / "references" / "context-modules.json"
DISTRIBUTION = ROOT / "references" / "distribution-files.json"
RUNTIME_READS = re.compile(r"^### Runtime Reads\s*$(.*?)(?=^#{2,3} |\Z)", re.M | re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REQUIRED_RUNTIME_SENTENCE = "Runtime must not inject wiki."
REQUIRED_TYPES = {
    "index", "log", "pattern", "entity", "framework-annotation",
    "procedure", "proposal-template", "terminology", "example",
}
REQUIRED_STATUS = {"active", "draft", "deprecated", "rejected"}
SKIP_FRONTMATTER = {"SCHEMA.md"}


class WikiError(ValueError):
    pass


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise WikiError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def wiki_markdown():
    return sorted(path for path in WIKI.rglob("*.md") if path.is_file())


def parse_frontmatter(text: str, rel: str):
    if not text.startswith("---"):
        raise WikiError("%s has no YAML frontmatter" % rel)
    try:
        end = text.index("\n---", 3)
    except ValueError as exc:
        raise WikiError("%s has unterminated frontmatter" % rel) from exc
    block = text[3:end]
    data = {}
    current_list = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list is None:
                raise WikiError("%s has a list item with no key" % rel)
            data.setdefault(current_list, []).append(line[4:].strip())
            continue
        if ":" not in line:
            raise WikiError("%s frontmatter line is not key: value: %s" % (rel, line))
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            current_list = key
            data[key] = []
        else:
            current_list = None
            data[key] = value.strip("'\"")
    return data


def contains_wiki(value) -> bool:
    if isinstance(value, str):
        return "references/wiki" in value or value.startswith("wiki/")
    if isinstance(value, list):
        return any(contains_wiki(item) for item in value)
    if isinstance(value, dict):
        return any(contains_wiki(item) for item in value.values())
    return False


def walk_json_for_wiki(value, prefix=""):
    hits = []
    if isinstance(value, dict):
        for key, item in value.items():
            hits.extend(walk_json_for_wiki(item, "%s.%s" % (prefix, key) if prefix else key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(walk_json_for_wiki(item, "%s[%d]" % (prefix, index)))
    elif isinstance(value, str) and "wiki" in value.lower():
        if "references/wiki" in value or "/wiki/" in value:
            hits.append("%s=%s" % (prefix, value))
    return hits


def main():
    fails = []
    today = date.today()

    def fail(msg):
        fails.append(msg)
        print("FAIL  " + msg)

    if not SCHEMA.is_file():
        fail("references/wiki/SCHEMA.md missing")
        print("\nWIKI LINT FAILED — %d issue(s)." % len(fails))
        return 1

    schema_text = SCHEMA.read_text(encoding="utf-8")
    if REQUIRED_RUNTIME_SENTENCE not in schema_text:
        fail("SCHEMA.md must contain the exact sentence %r" % REQUIRED_RUNTIME_SENTENCE)

    pages = wiki_markdown()
    if not pages:
        fail("references/wiki/ has no Markdown pages")
        print("\nWIKI LINT FAILED — %d issue(s)." % len(fails))
        return 1

    ids = {}
    if not INDEX.is_file():
        fail("references/wiki/index.md missing")
        index_targets = set()
    else:
        index_text = INDEX.read_text(encoding="utf-8")
        index_targets = set()
        for raw in LINK.findall(index_text):
            target = raw.split("#", 1)[0].strip()
            if not target or ":" in target:
                continue
            resolved = (INDEX.parent / target).resolve()
            try:
                resolved.relative_to(WIKI.resolve())
            except ValueError:
                continue
            if resolved.suffix == ".md":
                index_targets.add(resolved)

    for path in pages:
        rel = str(path.relative_to(ROOT))
        name = path.relative_to(WIKI).as_posix()
        text = path.read_text(encoding="utf-8")
        if path.name in SKIP_FRONTMATTER:
            continue
        try:
            meta = parse_frontmatter(text, rel)
        except WikiError as exc:
            fail(str(exc))
            continue
        for key in ("type", "id", "title", "status", "generated"):
            if key not in meta or meta[key] in ("", []):
                fail("%s missing %s" % (rel, key))
        if meta.get("type") not in REQUIRED_TYPES:
            fail("%s type %r is not allowed" % (rel, meta.get("type")))
        if meta.get("status") not in REQUIRED_STATUS:
            fail("%s status %r is not allowed" % (rel, meta.get("status")))
        generated = meta.get("generated")
        if generated not in {"true", "false"}:
            fail("%s generated must be true or false" % rel)
        sources = meta.get("sources")
        if generated == "false" and not sources:
            fail("%s hand-authored page needs sources" % rel)
        page_id = meta.get("id")
        if page_id:
            if page_id in ids:
                fail("duplicate wiki id %s (%s and %s)" % (page_id, ids[page_id], rel))
            ids[page_id] = rel
        stale = meta.get("stale_after")
        if meta.get("status") == "active":
            if not stale:
                fail("%s active page needs stale_after" % rel)
            else:
                try:
                    stale_date = date.fromisoformat(stale)
                except ValueError:
                    fail("%s stale_after %r is not ISO date" % (rel, stale))
                else:
                    if stale_date < today:
                        fail("%s is stale (stale_after %s)" % (rel, stale))
        if path.resolve() not in index_targets and path != INDEX:
            fail("%s is not linked from index.md (orphan)" % rel)

    for target in sorted(index_targets):
        if not target.is_file():
            fail("index.md links to missing %s" % target.relative_to(ROOT))

    try:
        plugin = load_json(PLUGIN)
        skill_entries = plugin["skills"]
    except (WikiError, KeyError) as exc:
        fail("cannot read plugin skills: %s" % exc)
        skill_entries = []
    if len(skill_entries) != 120:
        fail("plugin.json must list exactly 120 skills (found %d); wiki must not add one"
             % len(skill_entries))

    for entry in skill_entries:
        rel_entry = entry[2:] if str(entry).startswith("./") else entry
        skill_file = ROOT / rel_entry / "SKILL.md"
        rel = str(skill_file.relative_to(ROOT))
        try:
            text = skill_file.read_text(encoding="utf-8")
        except OSError as exc:
            fail("cannot read %s: %s" % (rel, exc))
            continue
        if "references/wiki" in text:
            fail("%s mentions references/wiki — wiki is maintenance-only" % rel)
        reads = RUNTIME_READS.search(text)
        if reads and "wiki" in reads.group(1).lower():
            fail("%s Runtime Reads mention wiki" % rel)

    try:
        module_hits = walk_json_for_wiki(load_json(CONTEXT_MODULES))
        if module_hits:
            fail("context-modules.json wires wiki: %s" % "; ".join(module_hits))
    except WikiError as exc:
        fail(str(exc))
    try:
        dist_hits = walk_json_for_wiki(load_json(DISTRIBUTION))
        if dist_hits:
            fail("distribution-files.json allowlists wiki: %s" % "; ".join(dist_hits))
    except WikiError as exc:
        fail(str(exc))

    if fails:
        print("\nWIKI LINT FAILED — %d issue(s)." % len(fails))
        return 1
    print("Wiki lint passed: %d pages, unique ids, index coverage, "
          "runtime exclusion holds, 120 skills unchanged." % len(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
