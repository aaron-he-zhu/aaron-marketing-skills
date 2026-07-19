#!/usr/bin/env python3
"""Build minimal user distributions from the repository source tree."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import re


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "system-catalog.json"
MANIFEST = ROOT / "references" / "distribution-files.json"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
PLUGIN_GENERATED_NAMES = {"auditor-runtime.md"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RUNTIME_PATH = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\$\{CLAUDE_PLUGIN_ROOT\}/)?"
    r"((?:references|scripts/connectors)/[A-Za-z0-9_./-]+\.(?:md|json|py)"
    r"|scripts/[A-Za-z0-9_-]+\.py)"  # top-level runtimes referenced in prose ship too
)


class DistributionError(ValueError):
    pass


def load_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise DistributionError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def skill_paths(catalog):
    paths = []
    for discipline in catalog["logical_order"]:
        if discipline == "protocol":
            paths.extend("protocol/%s" % slug for slug in catalog["protocol"]["skills"])
            continue
        spec = catalog["disciplines"][discipline]
        for phase in spec["phase_order"]:
            paths.extend(
                "%s/%s/%s" % (discipline, phase, slug)
                for slug in spec["phases"][phase]
            )
    return paths


def validate_relative(relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise DistributionError("unsafe distribution path: %s" % relative)
    return path


def ignored(_directory, names):
    return [
        name for name in names
        if name in IGNORED_NAMES or Path(name).suffix in IGNORED_SUFFIXES
    ]


def plugin_ignored(directory, names):
    return sorted(set(ignored(directory, names)) | (set(names) & PLUGIN_GENERATED_NAMES))


def copy_entry(relative, destination, tree_ignore=ignored):
    relative_path = validate_relative(relative)
    source = ROOT / relative_path
    target = destination / relative_path
    if not source.exists():
        raise DistributionError("required distribution input is missing: %s" % relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target, ignore=tree_ignore)
    elif source.is_file():
        shutil.copy2(source, target)
    else:
        raise DistributionError("unsupported distribution input: %s" % relative)


def runtime_dependencies(relative):
    """Return repository runtime files directly named by one text source."""
    source = ROOT / validate_relative(relative)
    if source.suffix != ".md":
        return set()
    text = source.read_text(encoding="utf-8")
    dependencies = set()
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().lstrip("<").rstrip(">").split("#", 1)[0]
        if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
            continue
        resolved = (source.parent / target).resolve()
        try:
            candidate = resolved.relative_to(ROOT.resolve())
        except ValueError:
            continue
        if candidate.parts[0] in {"references", "scripts"} and resolved.is_file():
            dependencies.add(str(candidate))
    dependencies.update(match.group(1) for match in RUNTIME_PATH.finditer(text))
    return {
        dependency for dependency in dependencies
        if (ROOT / validate_relative(dependency)).is_file()
    }


def copy_runtime_closure(seed_entries, destination):
    pending = list(seed_entries)
    copied = set()
    while pending:
        relative = pending.pop()
        if relative in copied:
            continue
        copy_entry(relative, destination)
        copied.add(relative)
        pending.extend(sorted(runtime_dependencies(relative) - copied))
    return copied


def prepare_destination(destination):
    resolved = destination.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise DistributionError("destination must be outside the source repository")
    if destination.exists() and any(destination.iterdir()):
        raise DistributionError("destination exists and is not empty: %s" % destination)
    destination.mkdir(parents=True, exist_ok=True)


def build_plugin(destination, catalog, manifest, slim_frontmatter=False):
    profile = manifest["plugin"]
    skills = skill_paths(catalog)
    entries = profile["root_files"] + profile["trees"]
    entries += profile["runtime_scripts"] + profile["runtime_script_trees"] + skills
    if len(entries) != len(set(entries)):
        raise DistributionError("plugin distribution manifest contains duplicate entries")
    for relative in entries:
        copy_entry(relative, destination, tree_ignore=plugin_ignored)
    markdown_seeds = [
        relative for relative in profile["root_files"]
        if Path(relative).suffix == ".md"
    ]
    markdown_seeds += ["commands/%s.md" % command for command in catalog["commands"]]
    markdown_seeds += [path + "/SKILL.md" for path in skills]
    referenced = set(profile["runtime_references"])
    for relative in markdown_seeds:
        referenced.update(runtime_dependencies(relative))
    copy_runtime_closure(referenced, destination)
    for forbidden in manifest["excluded_top_level"]:
        if (destination / forbidden).exists():
            raise DistributionError("maintenance path leaked into plugin: %s" % forbidden)
    if slim_frontmatter:
        for skill in skills:
            slim_skill_frontmatter(destination / skill / "SKILL.md")


# Frontmatter keys that exist only for publishing-time registries (SkillHub's
# `slug`/`displayName`/`summary` listing identity). They are dead weight on
# every installed host: `skillhub publish` runs from the source repo, so the
# distribution can drop them. Host extensions (metadata.hermes/openclaw) and
# the routing surface (description/when_to_use) stay untouched.
SLIM_FRONTMATTER_KEYS = ("slug", "displayName", "summary")


def slim_skill_frontmatter(skill_file):
    lines = skill_file.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise DistributionError("cannot slim frontmatter: %s has no frontmatter" % skill_file)
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise DistributionError("cannot slim frontmatter: %s is unterminated" % skill_file) from exc
    kept = [line for line in lines[1:end]
            if not any(line.startswith(key + ":") for key in SLIM_FRONTMATTER_KEYS)]
    required = ("name:", "version:", "description:", "metadata:")
    if any(not any(k.startswith(prefix) for k in kept) for prefix in required):
        raise DistributionError(
            "slimming %s would drop a required frontmatter key — refusing" % skill_file)
    skill_file.write_text("".join([lines[0], *kept, *lines[end:]]), encoding="utf-8")


def build_standalone(destination, catalog, requested):
    known = set(skill_paths(catalog))
    requested = str(validate_relative(requested)).rstrip("/")
    if requested not in known:
        raise DistributionError("unknown skill path: %s" % requested)
    source = ROOT / requested
    for child in source.iterdir():
        if child.name in IGNORED_NAMES or child.suffix in IGNORED_SUFFIXES:
            continue
        target = destination / child.name
        if child.is_dir():
            shutil.copytree(child, target, ignore=ignored)
        elif child.is_file():
            shutil.copy2(child, target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plugin", action="store_true")
    group.add_argument("--skill", metavar="DISCIPLINE/PHASE/SKILL")
    parser.add_argument(
        "--slim-frontmatter",
        action="store_true",
        help="Plugin builds only: strip publishing-only frontmatter keys "
             "(slug/displayName/summary) from shipped SKILL.md files.",
    )
    args = parser.parse_args(argv)
    try:
        catalog = load_json(CATALOG)
        manifest = load_json(MANIFEST)
        prepare_destination(args.output)
        if args.slim_frontmatter and not args.plugin:
            raise DistributionError("--slim-frontmatter applies to --plugin builds only")
        if args.plugin:
            build_plugin(args.output, catalog, manifest,
                         slim_frontmatter=args.slim_frontmatter)
            kind = "plugin"
        else:
            build_standalone(args.output, catalog, args.skill)
            kind = "standalone skill"
    except DistributionError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    files = sum(1 for path in args.output.rglob("*") if path.is_file())
    size = sum(path.stat().st_size for path in args.output.rglob("*") if path.is_file())
    print("built %s distribution: %d files, %d bytes" % (kind, files, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
