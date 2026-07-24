#!/usr/bin/env python3
"""Generate deterministic public release projections from repository SSOTs.

JSON projections are complete canonical documents. Markdown projections are
deliberately narrower: this tool will only replace content between an exact
``release-surface`` marker pair declared in publication-metadata.json. It never
inserts markers, rewrites a whole Markdown file, or performs global version
substitution.

Usage:
  python3 scripts/generate-release-surfaces.py --check
  python3 scripts/generate-release-surfaces.py --write
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import string
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CATALOG_REL = Path("references/system-catalog.json")
METADATA_REL = Path("references/publication-metadata.json")

JSON_TARGETS = (
    Path(".claude-plugin/plugin.json"),
    Path("marketplace.json"),
    Path(".claude-plugin/marketplace.json"),
    Path("openclaw.plugin.json"),
    Path(".github/repo-about.json"),
    Path("skills.sh.json"),
)
STATIC_MARKDOWN_TARGETS = {
    Path("README.md"),
    Path("CLAUDE.md"),
    Path("AGENTS.md"),
    Path("SECURITY.md"),
}
DISCIPLINES = {
    "narrative", "seo-geo", "social", "email", "ad", "influencer", "launch",
}
LOCALES = {"zh", "de", "es", "fr", "it", "ja", "ko", "pt", "zh-Hant"}
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MARKER_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PLACEHOLDER_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class GenerationError(ValueError):
    """An authored source or projection cannot be handled safely."""


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _load_json(root: Path, relative: Path) -> dict:
    path = root / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GenerationError("cannot read %s: %s" % (relative, exc)) from exc
    if not isinstance(value, dict):
        raise GenerationError("%s must contain a JSON object" % relative)
    return value


def _exact_keys(value: dict, expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing %s" % ", ".join(missing))
        if unknown:
            details.append("unknown %s" % ", ".join(unknown))
        raise GenerationError("%s fields are invalid (%s)" % (label, "; ".join(details)))


def _nonempty_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GenerationError("%s must be a non-empty string" % label)
    return value


def _unique_text_list(value: object, label: str) -> list[str]:
    if (
            not isinstance(value, list)
            or not value
            or not all(isinstance(item, str) and item for item in value)
            or len(value) != len(set(value))):
        raise GenerationError("%s must be a non-empty unique string list" % label)
    return value


def _catalog_skill_inventory(catalog: dict) -> tuple[list[str], dict[str, list[str]]]:
    try:
        logical_order = catalog["logical_order"]
        disciplines = catalog["disciplines"]
        protocol = catalog["protocol"]
        counts = catalog["counts"]
    except KeyError as exc:
        raise GenerationError("system catalog is missing %s" % exc) from exc
    if (
            not isinstance(logical_order, list)
            or not logical_order
            or len(logical_order) != len(set(logical_order))):
        raise GenerationError("system catalog logical_order must be a unique list")

    grouped: dict[str, list[str]] = {}
    paths: list[str] = []
    for key in logical_order:
        if key == "protocol":
            skills = protocol.get("skills")
            if not isinstance(skills, list):
                raise GenerationError("system catalog protocol.skills must be a list")
            if any(
                    not isinstance(skill, str) or not SLUG_RE.fullmatch(skill)
                    for skill in skills):
                raise GenerationError("system catalog protocol has an invalid skill slug")
            grouped[key] = list(skills)
            paths.extend("./protocol/%s" % skill for skill in skills)
            continue
        if key not in disciplines:
            raise GenerationError("logical_order references unknown discipline %s" % key)
        discipline = disciplines[key]
        phase_order = discipline.get("phase_order")
        phases = discipline.get("phases")
        if not isinstance(phase_order, list) or not isinstance(phases, dict):
            raise GenerationError("%s phase topology is invalid" % key)
        skills = []
        for phase in phase_order:
            phase_skills = phases.get(phase)
            if not isinstance(phase_skills, list):
                raise GenerationError("%s.%s must be a skill list" % (key, phase))
            for skill in phase_skills:
                if not isinstance(skill, str) or not SLUG_RE.fullmatch(skill):
                    raise GenerationError("%s.%s has an invalid skill slug" % (key, phase))
                skills.append(skill)
                paths.append("./%s/%s/%s" % (key, phase, skill))
        grouped[key] = skills

    if len(paths) != len(set(paths)):
        raise GenerationError("system catalog skill paths are not unique")
    expected = counts.get("total_skills")
    if expected != len(paths):
        raise GenerationError(
            "system catalog declares %r total skills but orders %d" % (expected, len(paths))
        )
    return paths, grouped


def _validate_metadata(metadata: dict, catalog: dict, grouped: dict[str, list[str]]) -> None:
    _exact_keys(
        metadata,
        {"schema_version", "plugin", "github_about", "skills_sh", "markdown_surfaces"},
        "publication metadata",
    )
    if metadata["schema_version"] != "1.0":
        raise GenerationError("publication metadata schema_version must be 1.0")

    plugin = metadata["plugin"]
    if not isinstance(plugin, dict):
        raise GenerationError("publication metadata plugin must be an object")
    _exact_keys(
        plugin,
        {
            "id", "name", "display_name", "description", "author", "homepage",
            "repository", "license", "keywords", "marketplace",
        },
        "publication metadata plugin",
    )
    for field in ("id", "name", "display_name", "description", "homepage", "repository", "license"):
        _nonempty_text(plugin[field], "plugin.%s" % field)
    if not SLUG_RE.fullmatch(plugin["id"]) or not SLUG_RE.fullmatch(plugin["name"]):
        raise GenerationError("plugin id and name must be lowercase slugs")
    if not plugin["repository"].startswith("https://github.com/"):
        raise GenerationError("plugin.repository must use canonical GitHub HTTPS")
    if plugin["homepage"] != plugin["repository"]:
        raise GenerationError("plugin homepage and repository must match")
    _unique_text_list(plugin["keywords"], "plugin.keywords")

    author = plugin["author"]
    if not isinstance(author, dict):
        raise GenerationError("plugin.author must be an object")
    _exact_keys(author, {"name", "email", "url"}, "plugin.author")
    for field in ("name", "email", "url"):
        _nonempty_text(author[field], "plugin.author.%s" % field)

    marketplace = plugin["marketplace"]
    if not isinstance(marketplace, dict):
        raise GenerationError("plugin.marketplace must be an object")
    _exact_keys(
        marketplace, {"name", "category", "source", "commands", "tags"},
        "plugin.marketplace",
    )
    for field in ("name", "category", "source", "commands"):
        _nonempty_text(marketplace[field], "plugin.marketplace.%s" % field)
    _unique_text_list(marketplace["tags"], "plugin.marketplace.tags")
    if set(marketplace["tags"]) != set(plugin["keywords"]):
        raise GenerationError("plugin keywords and marketplace tags must have the same set")

    counts = catalog.get("counts", {})
    expected_prefix = "%s marketing skills and %s commands" % (
        counts.get("total_skills"), counts.get("commands"),
    )
    if not plugin["description"].startswith(expected_prefix):
        raise GenerationError(
            "plugin.description must start with catalog-derived %r" % expected_prefix
        )

    about = metadata["github_about"]
    if not isinstance(about, dict):
        raise GenerationError("github_about must be an object")
    _exact_keys(about, {"comment", "description", "topics"}, "github_about")
    _nonempty_text(about["comment"], "github_about.comment")
    _nonempty_text(about["description"], "github_about.description")
    _unique_text_list(about["topics"], "github_about.topics")
    if not about["description"].startswith("%s " % counts.get("total_skills")):
        raise GenerationError("github_about.description must lead with the catalog skill count")

    skills_sh = metadata["skills_sh"]
    if not isinstance(skills_sh, dict):
        raise GenerationError("skills_sh must be an object")
    _exact_keys(skills_sh, {"schema", "not_grouped", "groupings"}, "skills_sh")
    _nonempty_text(skills_sh["schema"], "skills_sh.schema")
    _nonempty_text(skills_sh["not_grouped"], "skills_sh.not_grouped")
    groupings = skills_sh["groupings"]
    if not isinstance(groupings, list):
        raise GenerationError("skills_sh.groupings must be a list")
    keys = []
    for index, grouping in enumerate(groupings):
        if not isinstance(grouping, dict):
            raise GenerationError("skills_sh.groupings[%d] must be an object" % index)
        _exact_keys(
            grouping, {"catalog_key", "title", "description"},
            "skills_sh.groupings[%d]" % index,
        )
        key = _nonempty_text(grouping["catalog_key"], "grouping.catalog_key")
        _nonempty_text(grouping["title"], "grouping.title")
        _nonempty_text(grouping["description"], "grouping.description")
        keys.append(key)
    if keys != list(grouped):
        raise GenerationError(
            "skills_sh grouping order %r must equal catalog logical order %r"
            % (keys, list(grouped))
        )

    surfaces = metadata["markdown_surfaces"]
    if not isinstance(surfaces, list):
        raise GenerationError("markdown_surfaces must be a list")
    seen = set()
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            raise GenerationError("markdown_surfaces[%d] must be an object" % index)
        _exact_keys(surface, {"path", "marker", "template"}, "markdown surface %d" % index)
        path = _relative_path(surface["path"], "markdown surface path")
        if not _markdown_target_allowed(path):
            raise GenerationError("markdown projection target is not allowlisted: %s" % path)
        marker = _nonempty_text(surface["marker"], "markdown surface marker")
        if not MARKER_RE.fullmatch(marker):
            raise GenerationError("markdown marker must be a lowercase slug: %s" % marker)
        template = _nonempty_text(surface["template"], "markdown surface template")
        identity = (path.as_posix(), marker)
        if identity in seen:
            raise GenerationError("duplicate markdown projection: %s %s" % identity)
        seen.add(identity)
        _validate_template(template)


def _relative_path(value: object, label: str) -> Path:
    text = _nonempty_text(value, label)
    path = Path(text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise GenerationError("%s must be a canonical repository-relative path" % label)
    return path


def _markdown_target_allowed(path: Path) -> bool:
    if path in STATIC_MARKDOWN_TARGETS:
        return True
    if len(path.parts) == 2 and path.parts[0] == "docs":
        match = re.fullmatch(r"README\.([A-Za-z-]+)\.md", path.name)
        return bool(match and match.group(1) in LOCALES)
    if len(path.parts) == 2 and path.parts[0] in DISCIPLINES:
        return path.name in {"README.md", "README.zh.md"}
    if len(path.parts) == 2 and path.parts[0] == "commands":
        return path.suffix == ".md" and path.stem in DISCIPLINES | {"auto"}
    return False


def _template_values(catalog: dict) -> dict[str, object]:
    counts = catalog["counts"]
    version = catalog.get("bundle_version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        raise GenerationError("system catalog bundle_version must be semver")
    return {
        "bundle_version": version,
        "bundle_major": version.split(".", 1)[0],
        "total_skills": counts["total_skills"],
        "command_count": counts["commands"],
        "discipline_count": counts["disciplines"],
        "protocol_skill_count": counts["protocol_skills"],
        "registry_count": counts["registries"],
        "auditor_count": counts["auditors"],
    }


def _validate_template(template: str) -> None:
    if "<!-- GENERATED:" in template:
        raise GenerationError("markdown templates may not contain generated markers")
    allowed = set(_template_values_placeholder_names())
    try:
        fields = list(string.Formatter().parse(template))
    except ValueError as exc:
        raise GenerationError("invalid markdown template: %s" % exc) from exc
    for _literal, field, format_spec, conversion in fields:
        if field is None:
            continue
        if (
                not PLACEHOLDER_RE.fullmatch(field)
                or field not in allowed
                or format_spec
                or conversion):
            raise GenerationError("unsafe or unknown markdown placeholder: %s" % field)


def _template_values_placeholder_names() -> tuple[str, ...]:
    return (
        "bundle_version", "bundle_major", "total_skills", "command_count",
        "discipline_count", "protocol_skill_count", "registry_count", "auditor_count",
    )


def _render_json_outputs(
        catalog: dict, metadata: dict, paths: list[str], grouped: dict[str, list[str]],
) -> dict[Path, bytes]:
    plugin_meta = metadata["plugin"]
    author = plugin_meta["author"]
    marketplace_meta = plugin_meta["marketplace"]
    version = catalog["bundle_version"]
    plugin = {
        "id": plugin_meta["id"],
        "name": plugin_meta["name"],
        "version": version,
        "description": plugin_meta["description"],
        "author": author,
        "homepage": plugin_meta["homepage"],
        "repository": plugin_meta["repository"],
        "license": plugin_meta["license"],
        "keywords": plugin_meta["keywords"],
        "commands": [marketplace_meta["commands"]],
        "skills": paths,
    }
    marketplace = {
        "name": marketplace_meta["name"],
        "owner": {"name": author["name"], "url": author["url"]},
        "metadata": {
            "description": plugin_meta["description"],
            "version": version,
            "repository": plugin_meta["repository"],
        },
        "plugins": [{
            "name": plugin_meta["name"],
            "source": marketplace_meta["source"],
            "description": plugin_meta["description"],
            "version": version,
            "category": marketplace_meta["category"],
            "commands": marketplace_meta["commands"],
            "tags": marketplace_meta["tags"],
            "skills": paths,
        }],
    }
    openclaw = {
        "id": plugin_meta["id"],
        "name": plugin_meta["display_name"],
        "version": version,
        "description": plugin_meta["description"],
        "configSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {},
        },
    }
    about_meta = metadata["github_about"]
    about = {
        "_comment": about_meta["comment"],
        "description": about_meta["description"],
        "topics": about_meta["topics"],
    }
    skills_sh_meta = metadata["skills_sh"]
    skills_sh = {
        "$schema": skills_sh_meta["schema"],
        "notGrouped": skills_sh_meta["not_grouped"],
        "groupings": [{
            "title": item["title"],
            "description": item["description"],
            "skills": grouped[item["catalog_key"]],
        } for item in skills_sh_meta["groupings"]],
    }
    marketplace_bytes = _canonical_json(marketplace)
    return {
        Path(".claude-plugin/plugin.json"): _canonical_json(plugin),
        Path("marketplace.json"): marketplace_bytes,
        Path(".claude-plugin/marketplace.json"): marketplace_bytes,
        Path("openclaw.plugin.json"): _canonical_json(openclaw),
        Path(".github/repo-about.json"): _canonical_json(about),
        Path("skills.sh.json"): _canonical_json(skills_sh),
    }


def _marker_lines(marker: str) -> tuple[str, str]:
    return (
        "<!-- GENERATED:BEGIN release-surface:%s -->" % marker,
        "<!-- GENERATED:END release-surface:%s -->" % marker,
    )


def _project_markdown(text: str, relative: Path, marker: str, body: str) -> str:
    begin, end = _marker_lines(marker)
    lines = text.splitlines(keepends=True)
    begin_positions = [
        index for index, line in enumerate(lines) if line.rstrip("\r\n") == begin
    ]
    end_positions = [
        index for index, line in enumerate(lines) if line.rstrip("\r\n") == end
    ]
    if len(begin_positions) != 1 or len(end_positions) != 1:
        raise GenerationError(
            "%s requires exactly one marker pair for %s; add lines %r and %r"
            % (relative, marker, begin, end)
        )
    start = begin_positions[0]
    stop = end_positions[0]
    if start >= stop:
        raise GenerationError("%s marker pair is out of order for %s" % (relative, marker))
    projected = body.rstrip("\r\n") + "\n"
    return "".join(lines[:start + 1]) + projected + "".join(lines[stop:])


def _render_all(root: Path) -> tuple[dict[Path, bytes], dict[Path, bytes]]:
    catalog = _load_json(root, CATALOG_REL)
    metadata = _load_json(root, METADATA_REL)
    paths, grouped = _catalog_skill_inventory(catalog)
    _validate_metadata(metadata, catalog, grouped)
    values = _template_values(catalog)
    json_outputs = _render_json_outputs(catalog, metadata, paths, grouped)
    if set(json_outputs) != set(JSON_TARGETS):
        raise GenerationError("internal JSON target set drift")

    markdown_outputs: dict[Path, bytes] = {}
    current_text: dict[Path, str] = {}
    for surface in metadata["markdown_surfaces"]:
        relative = Path(surface["path"])
        if relative not in current_text:
            try:
                current_text[relative] = (root / relative).read_text(encoding="utf-8")
            except OSError as exc:
                raise GenerationError("cannot read markdown projection %s: %s" % (relative, exc)) from exc
        body = surface["template"].format_map(values)
        current_text[relative] = _project_markdown(
            current_text[relative], relative, surface["marker"], body,
        )
    for relative, text in current_text.items():
        markdown_outputs[relative] = text.encode("utf-8")
    return json_outputs, markdown_outputs


def _checked_target(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise GenerationError("unsafe output path: %s" % relative)
    root = root.resolve()
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        try:
            status = current.lstat()
        except OSError as exc:
            raise GenerationError("output parent is unavailable for %s: %s" % (relative, exc)) from exc
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
            raise GenerationError("output parent must be a real directory: %s" % current)
    target = root / relative
    if target.exists() or target.is_symlink():
        status = target.lstat()
        if (
                stat.S_ISLNK(status.st_mode)
                or not stat.S_ISREG(status.st_mode)
                or status.st_nlink != 1):
            raise GenerationError("output must be a single-link regular file: %s" % relative)
    return target


def _atomic_write(path: Path, content: bytes) -> None:
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    temporary = None
    try:
        fd, temporary = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
        os.chmod(temporary, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def check_outputs(root: Path = ROOT) -> list[str]:
    json_outputs, markdown_outputs = _render_all(root)
    problems = []
    for relative, expected in {**json_outputs, **markdown_outputs}.items():
        path = _checked_target(root, relative)
        try:
            actual = path.read_bytes()
        except OSError:
            problems.append("missing release projection: %s" % relative)
            continue
        if actual != expected:
            problems.append("stale release projection: %s" % relative)
    return problems


def write_outputs(root: Path = ROOT) -> int:
    json_outputs, markdown_outputs = _render_all(root)
    outputs = {**json_outputs, **markdown_outputs}
    targets = {relative: _checked_target(root, relative) for relative in outputs}
    changed = 0
    for relative, expected in outputs.items():
        target = targets[relative]
        if target.is_file() and target.read_bytes() == expected:
            continue
        _atomic_write(target, expected)
        changed += 1
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.write:
            changed = write_outputs(ROOT)
            print("release projections written (%d changed)" % changed)
            return 0
        problems = check_outputs(ROOT)
    except (GenerationError, KeyError, TypeError, OSError) as exc:
        print("FAIL  %s" % exc, file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print("FAIL  %s" % problem, file=sys.stderr)
        print(
            "run: python3 scripts/generate-release-surfaces.py --write",
            file=sys.stderr,
        )
        return 1
    print("release projections are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
