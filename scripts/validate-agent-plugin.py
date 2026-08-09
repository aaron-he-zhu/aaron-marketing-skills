#!/usr/bin/env python3
"""Fail-closed validator for the repository's Agent Plugins v1 projection.

The validator intentionally has no third-party dependencies.  It validates an
*unpacked* package, so callers can run it both in CI and against an extracted
release archive before installation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from urllib.parse import unquote, urlsplit


PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PROJECTION_FILE = "agent-plugin-projection.json"
DISTRIBUTION_MANIFEST = "distribution-manifest.json"
EXPECTED_SKILLS = 120
STANDARD_SCHEMA_PATH = (
    "references/standards/agent-plugins/1.0.0/plugin.schema.json"
)
STANDARD_PROVENANCE_PATH = (
    "references/standards/agent-plugins/1.0.0/PROVENANCE.json"
)
PORTABLE_PROFILE_PATH = "references/agent-plugin-portable-profile.json"
SYSTEM_CATALOG_PATH = "references/system-catalog.json"
STANDARD_SCHEMA_SHA256 = (
    "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
)
AGENT_SKILLS_COMMIT = "217be548739f21d6008915c29aefe320ea1a90af"
AGENT_PLUGINS_RELEASE_COMMIT = "f24daf829224fd7fb685ae117c518ea27cbe7b9e"

PLUGIN_FIELDS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
PLUGIN_REQUIRED = {"$schema", "name", "version"}
AUTHOR_FIELDS = {"name", "email", "url"}
SKILL_FIELDS = {
    "name", "description", "license", "compatibility", "metadata",
    "allowed-tools",
}
SKILL_REQUIRED = {"name", "description"}
PORTABLE_PROFILE_FIELDS = {
    "$schema", "schema_version", "profile", "host_profile", "capabilities",
    "excluded_capabilities", "routing_surface", "reference_surface",
    "connector_surface", "mcp_policy", "frontmatter_policy_version",
    "package_ceiling",
}
PROJECTION_FIELDS = {
    "schema_version", "kind", "plugin_version", "source_root",
    "frontmatter_policy_version", "skill_count", "skills",
}
PROJECTION_SKILL_FIELDS = {
    "name", "source_path", "projected_path", "source_sha256",
    "projected_sha256",
}
PROJECTION_BINDING_FIELDS = {
    "path", "sha256", "skill_count", "frontmatter_policy_version",
}
STANDARD_BINDING_FIELDS = {
    "name", "version", "schema_url", "schema_path", "schema_sha256",
    "provenance_path", "provenance_sha256", "agent_skills_commit",
}
AGENT_PLUGIN_MANIFEST_FIELDS = {
    "schema_version", "kind", "plugin_version", "profile",
    "capability_ceiling", "capabilities", "excluded_capabilities",
    "catalog_sha256", "profile_definition_sha256", "host_profile",
    "host_capabilities", "host_profile_definition_sha256",
    "routing_surface", "reference_surface", "connector_surface",
    "mcp_policy", "package_ceiling", "hash_algorithm", "manifest_path",
    "manifest_excludes", "source", "standard", "agent_plugin_projection",
    "files_sha256", "files",
}
PORTABLE_CAPABILITIES = [
    "authored-workflows",
    "inline-delivery",
    "canonical-state-read",
    "static-reference-access",
]
PORTABLE_EXCLUDED_CAPABILITIES = [
    "slash-commands",
    "prewrite-hooks",
    "local-runtime-scripts",
    "deterministic-scoring",
    "connector-sidecars",
    "native-plugin-connectors",
    "host-tool-preapproval",
    "audit-persistence",
    "persistent-project-memory",
    "working-memory-write",
    "registry-write",
    "run-evidence",
    "context-planning",
    "runtime-controller",
    "workflow-execution",
    "workflow-loop",
    "audit-loop",
    "owner-capability",
]
PORTABLE_PACKAGE_CEILING = {"max_files": 400, "max_bytes": 4_000_000}
FILE_RECORD_FIELDS = {"bytes", "mode", "path", "sha256"}

FORBIDDEN_TOP_LEVEL_FILES = {"mcp.json"}
FORBIDDEN_TOP_LEVEL_DIRS = {
    ".agents", ".claude", ".claude-plugin", ".codex-plugin", ".cursor",
    ".github", ".githooks", ".openclaw", "agents", "commands", "evals",
    "hooks", "memory", "router-facades", "scripts", "tests",
}

PLUGIN_NAME = re.compile(
    r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$"
)
SKILL_NAME = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REVERSE_DOMAIN = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?){2,}$"
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
MARKDOWN_REFERENCE = re.compile(
    r"(?m)^[ \t]{0,3}\[(?!\^)[^\]\n]+\]:[ \t]*(<[^>\n]+>|\S+)"
)
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")


class _DuplicateKey(ValueError):
    pass


class _Reporter:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def add(self, location: str, message: str) -> None:
        self.errors.append("%s: %s" % (location, message))

    def result(self) -> list[str]:
        return sorted(set(self.errors))


def _strict_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise _DuplicateKey("duplicate key %r" % key)
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError("non-finite JSON number %s" % value)


def _json_bytes(raw: bytes, location: str, reporter: _Reporter):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        reporter.add(location, "must be UTF-8 JSON (%s)" % exc)
        return None
    try:
        return json.loads(
            text, object_pairs_hook=_strict_object, parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, _DuplicateKey, ValueError) as exc:
        reporter.add(location, "invalid JSON (%s)" % exc)
        return None


def _read_regular(path: Path, location: str, reporter: _Reporter):
    try:
        before = path.lstat()
    except OSError as exc:
        reporter.add(location, "cannot be read (%s)" % exc)
        return None
    if (stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1):
        reporter.add(location, "must be a single-link regular file")
        return None
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        identity = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size")
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or any(getattr(opened, key) != getattr(before, key) for key in identity)):
            os.close(descriptor)
            descriptor = None
            reporter.add(location, "changed or became unsafe while it was opened")
            return None
        handle = os.fdopen(descriptor, "rb", closefd=True)
        descriptor = None
        with handle:
            raw = handle.read()
        after = path.lstat()
    except OSError as exc:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        reporter.add(location, "cannot be read (%s)" % exc)
        return None
    if any(getattr(after, key) != getattr(before, key) for key in identity):
        reporter.add(location, "changed while it was being read")
        return None
    return raw


def _safe_relative(value, location: str, field: str, reporter: _Reporter):
    if not isinstance(value, str) or not value:
        reporter.add(location, "%s must be a non-empty relative POSIX path" % field)
        return None
    if "\x00" in value or "\\" in value or WINDOWS_ABSOLUTE.match(value):
        reporter.add(location, "%s is not a safe relative POSIX path: %r" % (field, value))
        return None
    pure = PurePosixPath(value)
    if (pure.is_absolute() or value.startswith("./") or value.endswith("/")
            or any(part in {"", ".", ".."} for part in pure.parts)
            or pure.as_posix() != value):
        reporter.add(location, "%s is not a normalized contained path: %r" % (field, value))
        return None
    return pure


def _scan_tree(root: Path, reporter: _Reporter):
    """Inspect without following links and return safe regular-file paths."""
    files = []
    root_resolved = root.resolve(strict=False)

    def visit(directory: Path) -> None:
        try:
            with os.scandir(directory) as scanned:
                entries = sorted(scanned, key=lambda item: item.name)
        except OSError as exc:
            location = directory.relative_to(root).as_posix() or "."
            reporter.add(location, "cannot inspect directory (%s)" % exc)
            return
        for entry in entries:
            path = directory / entry.name
            location = path.relative_to(root).as_posix()
            try:
                status = path.lstat()
            except OSError as exc:
                reporter.add(location, "cannot inspect path (%s)" % exc)
                continue
            try:
                path.resolve(strict=False).relative_to(root_resolved)
            except (OSError, ValueError):
                reporter.add(location, "resolves outside the package root")
            if stat.S_ISLNK(status.st_mode):
                reporter.add(location, "symlinks are forbidden")
            elif stat.S_ISDIR(status.st_mode):
                visit(path)
            elif stat.S_ISREG(status.st_mode):
                if status.st_nlink != 1:
                    reporter.add(location, "hard-linked files are forbidden (link count %d)" % status.st_nlink)
                else:
                    files.append(path)
            else:
                reporter.add(location, "special files are forbidden")

    visit(root)
    return files


def _validate_plugin(root: Path, reporter: _Reporter):
    location = "plugin.json"
    raw = _read_regular(root / location, location, reporter)
    if raw is None:
        return None
    plugin = _json_bytes(raw, location, reporter)
    if not isinstance(plugin, dict):
        if plugin is not None:
            reporter.add(location, "top level must be an object")
        return None

    unknown = sorted(set(plugin) - PLUGIN_FIELDS)
    missing = sorted(PLUGIN_REQUIRED - set(plugin))
    if unknown:
        reporter.add(location, "unknown fields: %s" % ", ".join(unknown))
    if missing:
        reporter.add(location, "missing required fields: %s" % ", ".join(missing))

    schema = plugin.get("$schema")
    if schema != PLUGIN_SCHEMA:
        reporter.add(location, "$schema must equal %s" % PLUGIN_SCHEMA)

    name = plugin.get("name")
    if (not isinstance(name, str) or not 1 <= len(name) <= 64
            or PLUGIN_NAME.fullmatch(name) is None):
        reporter.add(location, "name must satisfy the Agent Plugins v1 name grammar and be 1-64 characters")

    version = plugin.get("version")
    if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
        reporter.add(location, "version must be a valid SemVer string")

    for field in ("description", "homepage", "repository", "license"):
        if field in plugin and not isinstance(plugin[field], str):
            reporter.add(location, "%s must be a string" % field)

    if "author" in plugin:
        author = plugin["author"]
        if not isinstance(author, dict):
            reporter.add(location, "author must be an object")
        else:
            extra = sorted(set(author) - AUTHOR_FIELDS)
            if extra:
                reporter.add(location, "author has unknown fields: %s" % ", ".join(extra))
            for field, value in author.items():
                if field in AUTHOR_FIELDS and not isinstance(value, str):
                    reporter.add(location, "author.%s must be a string" % field)

    if "keywords" in plugin:
        keywords = plugin["keywords"]
        if not isinstance(keywords, list):
            reporter.add(location, "keywords must be an array of strings")
        else:
            for index, value in enumerate(keywords):
                if not isinstance(value, str):
                    reporter.add(location, "keywords[%d] must be a string" % index)

    if "extensions" in plugin:
        extensions = plugin["extensions"]
        if not isinstance(extensions, dict):
            reporter.add(location, "extensions must be an object")
        else:
            for namespace, value in extensions.items():
                if not isinstance(namespace, str) or REVERSE_DOMAIN.fullmatch(namespace) is None:
                    reporter.add(location, "extension namespace is not reverse-domain notation: %r" % namespace)
                if not isinstance(value, dict):
                    reporter.add(location, "extension %r must contain an object" % namespace)
        reporter.add(location, "extensions are forbidden by the Portable Lite policy")
    return plugin


def _yaml_scalar(value: str):
    value = value.strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ValueError("unterminated single-quoted scalar")
        return value[1:-1].replace("''", "'")
    if value.startswith("{") or value.startswith("["):
        return json.loads(value, object_pairs_hook=_strict_object, parse_constant=_reject_constant)
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if re.fullmatch(r"[-+]?(?:0|[1-9][0-9]*)", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?", value):
        return float(value)
    return value


def _parse_frontmatter(raw: bytes, location: str, reporter: _Reporter):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        reporter.add(location, "must be UTF-8 (%s)" % exc)
        return None
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        reporter.add(location, "must begin with an exact YAML frontmatter delimiter")
        return None
    try:
        closing = lines.index("---", 1)
    except ValueError:
        reporter.add(location, "frontmatter has no closing --- delimiter")
        return None

    result = {}
    block_key = None
    for offset, line in enumerate(lines[1:closing], start=2):
        line_location = "%s:%d" % (location, offset)
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace():
            if block_key != "metadata":
                reporter.add(line_location, "nested YAML is allowed only for metadata")
                continue
            stripped = line.strip()
            if ":" not in stripped:
                reporter.add(line_location, "metadata entry must use key: value syntax")
                continue
            key, encoded = stripped.split(":", 1)
            key = key.strip()
            if not key or encoded.strip() == "":
                reporter.add(line_location, "metadata entries must have scalar values")
                continue
            if key in result["metadata"]:
                reporter.add(line_location, "duplicate metadata key %r" % key)
                continue
            try:
                result["metadata"][key] = _yaml_scalar(encoded)
            except (ValueError, json.JSONDecodeError, _DuplicateKey) as exc:
                reporter.add(line_location, "invalid metadata scalar (%s)" % exc)
            continue

        block_key = None
        if ":" not in line:
            reporter.add(line_location, "frontmatter entry must use key: value syntax")
            continue
        key, encoded = line.split(":", 1)
        key = key.strip()
        if not key or re.fullmatch(r"[A-Za-z0-9_-]+", key) is None:
            reporter.add(line_location, "invalid frontmatter key %r" % key)
            continue
        if key in result:
            reporter.add(line_location, "duplicate frontmatter field %r" % key)
            continue
        if encoded.strip() == "":
            if key == "metadata":
                result[key] = {}
                block_key = key
            else:
                result[key] = None
                reporter.add(line_location, "only metadata may use a block mapping")
            continue
        try:
            result[key] = _yaml_scalar(encoded)
        except (ValueError, json.JSONDecodeError, _DuplicateKey) as exc:
            reporter.add(line_location, "invalid frontmatter scalar (%s)" % exc)
    return result


def _validate_skill_frontmatter(
        root: Path, skill_dir: Path, reporter: _Reporter):
    location = (skill_dir / "SKILL.md").relative_to(root).as_posix()
    try:
        with os.scandir(skill_dir) as scanned:
            exact_names = {entry.name for entry in scanned}
    except OSError as exc:
        reporter.add(location, "cannot inspect skill directory (%s)" % exc)
        return
    if "SKILL.md" not in exact_names:
        reporter.add(location, "skill directory must contain exact uppercase SKILL.md")
        return
    raw = _read_regular(skill_dir / "SKILL.md", location, reporter)
    if raw is None:
        return
    frontmatter = _parse_frontmatter(raw, location, reporter)
    if not isinstance(frontmatter, dict):
        return
    unknown = sorted(set(frontmatter) - SKILL_FIELDS)
    missing = sorted(SKILL_REQUIRED - set(frontmatter))
    if unknown:
        reporter.add(location, "frontmatter has non-Agent-Skills fields: %s" % ", ".join(unknown))
    if missing:
        reporter.add(location, "frontmatter is missing: %s" % ", ".join(missing))

    name = frontmatter.get("name")
    if (not isinstance(name, str) or not 1 <= len(name) <= 64
            or SKILL_NAME.fullmatch(name) is None):
        reporter.add(location, "name must satisfy the Agent Skills name grammar and be 1-64 characters")
    elif name != skill_dir.name:
        reporter.add(location, "name %r does not match directory %r" % (name, skill_dir.name))

    description = frontmatter.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        reporter.add(location, "description must be a string of 1-1024 characters")
    if "license" in frontmatter and not isinstance(frontmatter["license"], str):
        reporter.add(location, "license must be a string")
    if "compatibility" in frontmatter:
        compatibility = frontmatter["compatibility"]
        if not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500:
            reporter.add(location, "compatibility must be a string of 1-500 characters")
        reporter.add(
            location,
            "source compatibility is forbidden by the Portable Lite frontmatter policy",
        )
    if "allowed-tools" in frontmatter and not isinstance(frontmatter["allowed-tools"], str):
        reporter.add(location, "allowed-tools must be a string")
    if "allowed-tools" in frontmatter:
        reporter.add(
            location,
            "allowed-tools host preapproval is forbidden by the Portable Lite frontmatter policy",
        )
    if "metadata" in frontmatter:
        metadata = frontmatter["metadata"]
        if not isinstance(metadata, dict):
            reporter.add(location, "metadata must be a string-to-string mapping")
        else:
            for key, value in metadata.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    reporter.add(location, "metadata entry %r must map string to string" % key)
            for client_key in ("hermes", "openclaw"):
                if client_key in metadata:
                    reporter.add(
                        location,
                        "client-specific metadata.%s is forbidden by the Portable Lite frontmatter policy"
                        % client_key,
                    )


def _validate_skills(root: Path, reporter: _Reporter, package_files):
    skills_root = root / "skills"
    try:
        root_status = skills_root.lstat()
    except OSError as exc:
        reporter.add("skills", "required directory is unavailable (%s)" % exc)
        return []
    if stat.S_ISLNK(root_status.st_mode) or not stat.S_ISDIR(root_status.st_mode):
        reporter.add("skills", "must be a real directory")
        return []
    try:
        with os.scandir(skills_root) as scanned:
            entries = sorted(scanned, key=lambda item: item.name)
    except OSError as exc:
        reporter.add("skills", "cannot enumerate direct children (%s)" % exc)
        return []

    directories = []
    for entry in entries:
        path = skills_root / entry.name
        location = path.relative_to(root).as_posix()
        try:
            status = path.lstat()
        except OSError as exc:
            reporter.add(location, "cannot inspect direct child (%s)" % exc)
            continue
        if stat.S_ISDIR(status.st_mode) and not stat.S_ISLNK(status.st_mode):
            directories.append(path)
        else:
            reporter.add(location, "skills/ may contain only direct child directories")
    if len(directories) != EXPECTED_SKILLS:
        reporter.add("skills", "must contain exactly %d direct skill directories; found %d" % (EXPECTED_SKILLS, len(directories)))
    for directory in directories:
        if (len(directory.name) > 64 or SKILL_NAME.fullmatch(directory.name) is None):
            reporter.add(directory.relative_to(root).as_posix(), "directory name does not satisfy the Agent Skills name grammar")
        _validate_skill_frontmatter(root, directory, reporter)
    skill_markers = [
        path for path in package_files
        if path.name == "SKILL.md"
        and path.relative_to(root).as_posix().startswith("skills/")
    ]
    expected_markers = {
        "skills/%s/SKILL.md" % directory.name for directory in directories
    }
    actual_markers = {path.relative_to(root).as_posix() for path in skill_markers}
    unexpected_markers = sorted(actual_markers - expected_markers)
    if len(skill_markers) != EXPECTED_SKILLS or unexpected_markers:
        reporter.add(
            "skills",
            "must contain exactly the %d direct SKILL.md files and no nested SKILL.md; found %d"
            % (EXPECTED_SKILLS, len(skill_markers)),
        )
        for marker in unexpected_markers:
            reporter.add(marker, "nested/extra SKILL.md is forbidden")
    return directories


def _link_target(encoded: str):
    value = encoded.strip()
    if value.startswith("<"):
        end = value.find(">")
        return value[1:end] if end >= 0 else value[1:]
    # Markdown titles follow whitespace; generated package paths never contain
    # unescaped spaces.  Keep escaped spaces in the target.
    match = re.match(r"(?:\\.|[^\s])+", value)
    return match.group(0).replace("\\ ", " ") if match else ""


def _markdown_code_spans(text: str):
    """Return fenced, indented, and inline-code spans to exclude from links."""
    spans = []
    offset = 0
    fence = None
    fence_start = None
    for line in text.splitlines(keepends=True):
        marker_match = re.match(r"^[ ]{0,3}(`{3,}|~{3,})", line)
        if fence is None:
            if marker_match:
                marker = marker_match.group(1)
                fence = (marker[0], len(marker))
                fence_start = offset
            elif line.startswith("    ") or line.startswith("\t"):
                spans.append((offset, offset + len(line)))
        elif (marker_match
                and marker_match.group(1)[0] == fence[0]
                and len(marker_match.group(1)) >= fence[1]):
            spans.append((fence_start, offset + len(line)))
            fence = None
            fence_start = None
        offset += len(line)
    if fence is not None:
        spans.append((fence_start, len(text)))

    fenced = list(spans)
    cursor = 0
    while cursor < len(text):
        opening = re.search(r"`+", text[cursor:])
        if opening is None:
            break
        start = cursor + opening.start()
        if any(begin <= start < end for begin, end in fenced):
            cursor = cursor + opening.end()
            continue
        marker = opening.group(0)
        end_match = re.search(re.escape(marker), text[cursor + opening.end():])
        if end_match is None:
            cursor = cursor + opening.end()
            continue
        end = cursor + opening.end() + end_match.end()
        spans.append((start, end))
        cursor = end
    return sorted(spans)


def _validate_local_links(root: Path, files, reporter: _Reporter) -> None:
    root_resolved = root.resolve(strict=False)
    for path in files:
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if path.suffix.lower() != ".md":
            continue
        raw = _read_regular(path, relative, reporter)
        if raw is None:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            # SKILL.md already reports this; references still get a local error.
            reporter.add(relative, "cannot inspect links in non-UTF-8 Markdown")
            continue
        matches = list(MARKDOWN_LINK.finditer(text))
        matches.extend(MARKDOWN_REFERENCE.finditer(text))
        matches.sort(key=lambda item: item.start())
        code_spans = _markdown_code_spans(text)
        for match in matches:
            if any(begin <= match.start() < end for begin, end in code_spans):
                continue
            target = _link_target(match.group(1))
            line = text.count("\n", 0, match.start()) + 1
            location = "%s:%d" % (relative, line)
            if not target or target.startswith("#"):
                continue
            decoded = unquote(target)
            if (decoded.startswith("/") or decoded.startswith("\\")
                    or WINDOWS_ABSOLUTE.match(decoded)
                    or decoded.lower().startswith("file:")):
                reporter.add(location, "absolute local link is forbidden: %s" % target)
                continue
            parsed = urlsplit(decoded)
            if parsed.scheme or parsed.netloc or decoded.startswith("//"):
                continue
            local_path = unquote(parsed.path)
            if not local_path:
                continue
            candidate = (path.parent / local_path).resolve(strict=False)
            try:
                candidate.relative_to(root_resolved)
            except ValueError:
                reporter.add(location, "local link escapes the package root: %s" % target)
                continue
            if not candidate.exists():
                reporter.add(location, "local link target does not exist: %s" % target)


def _validate_forbidden_surfaces(root: Path, plugin, reporter: _Reporter) -> None:
    for name in sorted(FORBIDDEN_TOP_LEVEL_FILES):
        path = root / name
        if path.exists() or path.is_symlink():
            reporter.add(name, "MCP is excluded from the portable Agent Plugins v1 package")
    for name in sorted(FORBIDDEN_TOP_LEVEL_DIRS):
        path = root / name
        if path.exists() or path.is_symlink():
            reporter.add(name, "client-specific/runtime directory is forbidden")
    if isinstance(plugin, dict) and isinstance(plugin.get("extensions"), dict):
        for namespace in plugin["extensions"]:
            if (isinstance(namespace, str)
                    and REVERSE_DOMAIN.fullmatch(namespace) is not None):
                path = root / namespace
                if path.exists() or path.is_symlink():
                    reporter.add(namespace, "client extension directory is forbidden in the portable package")
    try:
        entries = list(root.iterdir())
    except OSError:
        return
    for path in entries:
        try:
            status = path.lstat()
        except OSError:
            continue
        if stat.S_ISDIR(status.st_mode) and REVERSE_DOMAIN.fullmatch(path.name):
            reporter.add(path.name, "reverse-domain client directory is forbidden in the portable package")


def _validate_projection(root: Path, plugin, skill_dirs, reporter: _Reporter):
    location = PROJECTION_FILE
    raw = _read_regular(root / location, location, reporter)
    if raw is None:
        return None, None
    projection = _json_bytes(raw, location, reporter)
    if not isinstance(projection, dict):
        if projection is not None:
            reporter.add(location, "top level must be an object")
        return None, raw
    if set(projection) != PROJECTION_FIELDS:
        reporter.add(location, "must contain exactly: %s" % ", ".join(sorted(PROJECTION_FIELDS)))
    if projection.get("schema_version") != "1.0":
        reporter.add(location, "schema_version must be '1.0'")
    if projection.get("kind") != "agent-plugins-v1-projection":
        reporter.add(location, "kind must be 'agent-plugins-v1-projection'")
    if projection.get("frontmatter_policy_version") != "1.0":
        reporter.add(location, "frontmatter_policy_version must be '1.0'")
    if projection.get("skill_count") != EXPECTED_SKILLS:
        reporter.add(location, "skill_count must be %d" % EXPECTED_SKILLS)
    source_root = projection.get("source_root")
    if source_root != ".":
        reporter.add(location, "source_root must be '.' (the build-input repository root)")
    version = projection.get("plugin_version")
    if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
        reporter.add(location, "plugin_version must be SemVer")
    if isinstance(plugin, dict) and version != plugin.get("version"):
        reporter.add(location, "plugin_version does not match plugin.json version")

    entries = projection.get("skills")
    if not isinstance(entries, list):
        reporter.add(location, "skills must be an array")
        return projection, raw
    if len(entries) != EXPECTED_SKILLS:
        reporter.add(location, "skills must contain exactly %d entries; found %d" % (EXPECTED_SKILLS, len(entries)))
    names = []
    source_paths = set()
    projected_paths = set()
    for index, entry in enumerate(entries):
        entry_location = "%s:skills[%d]" % (location, index)
        if not isinstance(entry, dict):
            reporter.add(entry_location, "entry must be an object")
            continue
        if set(entry) != PROJECTION_SKILL_FIELDS:
            reporter.add(entry_location, "must contain exactly: %s" % ", ".join(sorted(PROJECTION_SKILL_FIELDS)))
        name = entry.get("name")
        if not isinstance(name, str) or SKILL_NAME.fullmatch(name) is None:
            reporter.add(entry_location, "name is not a valid Agent Skills name")
            continue
        names.append(name)
        source_path = _safe_relative(entry.get("source_path"), entry_location, "source_path", reporter)
        projected_path = _safe_relative(entry.get("projected_path"), entry_location, "projected_path", reporter)
        if source_path is not None:
            source_value = source_path.as_posix()
            if source_value in source_paths:
                reporter.add(entry_location, "duplicate source_path %r" % source_value)
            source_paths.add(source_value)
            if source_path.name != "SKILL.md" or source_path.parent.name != name:
                reporter.add(entry_location, "source_path must end in <name>/SKILL.md")
        expected_projected = "skills/%s/SKILL.md" % name
        if projected_path is not None:
            projected_value = projected_path.as_posix()
            if projected_value in projected_paths:
                reporter.add(entry_location, "duplicate projected_path %r" % projected_value)
            projected_paths.add(projected_value)
            if projected_value != expected_projected:
                reporter.add(entry_location, "projected_path must equal %s" % expected_projected)
        for field in ("source_sha256", "projected_sha256"):
            digest = entry.get(field)
            if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
                reporter.add(entry_location, "%s must be a lowercase SHA-256 digest" % field)
        target = root / expected_projected
        target_raw = _read_regular(target, expected_projected, reporter)
        if target_raw is not None and entry.get("projected_sha256") != hashlib.sha256(target_raw).hexdigest():
            reporter.add(entry_location, "projected_sha256 does not match %s" % expected_projected)
    if names != sorted(names):
        reporter.add(location, "skills entries must be sorted by name")
    if len(names) != len(set(names)):
        reporter.add(location, "skills entries contain duplicate names")
    actual_names = sorted(path.name for path in skill_dirs)
    if names != actual_names:
        missing = sorted(set(actual_names) - set(names))
        extra = sorted(set(names) - set(actual_names))
        detail = []
        if missing:
            detail.append("missing " + ", ".join(missing))
        if extra:
            detail.append("unknown " + ", ".join(extra))
        reporter.add(location, "skills mapping does not match direct skill directories%s" % (": " + "; ".join(detail) if detail else ""))
    return projection, raw


def _canonical_json(value) -> bytes:
    return (json.dumps(
        value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True,
    ) + "\n").encode("utf-8")


def _actual_file_records(root: Path, reporter: _Reporter):
    records = []

    def visit(directory: Path) -> None:
        try:
            with os.scandir(directory) as scanned:
                entries = sorted(scanned, key=lambda item: item.name)
        except OSError:
            return
        for entry in entries:
            path = directory / entry.name
            relative = path.relative_to(root).as_posix()
            try:
                status = path.lstat()
            except OSError:
                continue
            if stat.S_ISDIR(status.st_mode) and not stat.S_ISLNK(status.st_mode):
                visit(path)
                continue
            if (relative == DISTRIBUTION_MANIFEST or stat.S_ISLNK(status.st_mode)
                    or not stat.S_ISREG(status.st_mode) or status.st_nlink != 1):
                continue
            raw = _read_regular(path, relative, reporter)
            if raw is not None:
                records.append({
                    "bytes": len(raw),
                    "mode": "%04o" % stat.S_IMODE(status.st_mode),
                    "path": relative,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                })

    visit(root)
    return records


def _validate_standard_bundle(root: Path, manifest, reporter: _Reporter) -> None:
    """Validate the immutable standard snapshot and its provenance binding."""
    manifest_location = DISTRIBUTION_MANIFEST
    binding = manifest.get("standard") if isinstance(manifest, dict) else None
    if not isinstance(binding, dict):
        reporter.add(manifest_location, "standard must be an object")
        binding = {}
    elif set(binding) != STANDARD_BINDING_FIELDS:
        reporter.add(
            manifest_location,
            "standard must contain exactly: %s"
            % ", ".join(sorted(STANDARD_BINDING_FIELDS)),
        )
    expected_identity = {
        "name": "agent-plugins",
        "version": "1.0.0",
        "schema_url": PLUGIN_SCHEMA,
        "schema_path": STANDARD_SCHEMA_PATH,
        "schema_sha256": STANDARD_SCHEMA_SHA256,
        "provenance_path": STANDARD_PROVENANCE_PATH,
        "agent_skills_commit": AGENT_SKILLS_COMMIT,
    }
    for field, expected in expected_identity.items():
        if binding.get(field) != expected:
            reporter.add(
                manifest_location,
                "standard.%s must equal %r" % (field, expected),
            )

    schema_raw = _read_regular(
        root / STANDARD_SCHEMA_PATH, STANDARD_SCHEMA_PATH, reporter,
    )
    if schema_raw is not None:
        schema_digest = hashlib.sha256(schema_raw).hexdigest()
        if schema_digest != STANDARD_SCHEMA_SHA256:
            reporter.add(
                STANDARD_SCHEMA_PATH,
                "content does not match the pinned Agent Plugins v1 schema SHA-256",
            )
        if binding.get("schema_sha256") != schema_digest:
            reporter.add(
                manifest_location,
                "standard.schema_sha256 does not match the packaged schema",
            )
        schema = _json_bytes(schema_raw, STANDARD_SCHEMA_PATH, reporter)
        if isinstance(schema, dict):
            properties = schema.get("properties")
            if (schema.get("$id") != PLUGIN_SCHEMA
                    or schema.get("type") != "object"
                    or schema.get("required") != ["$schema", "name"]
                    or schema.get("additionalProperties") is not False
                    or not isinstance(properties, dict)
                    or set(properties) != PLUGIN_FIELDS):
                reporter.add(
                    STANDARD_SCHEMA_PATH,
                    "schema identity/closed plugin field set is invalid",
                )

    provenance_raw = _read_regular(
        root / STANDARD_PROVENANCE_PATH, STANDARD_PROVENANCE_PATH, reporter,
    )
    if provenance_raw is None:
        return
    provenance_digest = hashlib.sha256(provenance_raw).hexdigest()
    if binding.get("provenance_sha256") != provenance_digest:
        reporter.add(
            manifest_location,
            "standard.provenance_sha256 does not match packaged provenance",
        )
    provenance = _json_bytes(
        provenance_raw, STANDARD_PROVENANCE_PATH, reporter,
    )
    if not isinstance(provenance, dict):
        if provenance is not None:
            reporter.add(STANDARD_PROVENANCE_PATH, "top level must be an object")
        return
    artifact = provenance.get("artifact")
    agent_plugins = provenance.get("agent_plugins")
    agent_skills = provenance.get("agent_skills_baseline")
    if provenance.get("format_version") != "1.0":
        reporter.add(STANDARD_PROVENANCE_PATH, "format_version must be '1.0'")
    if (not isinstance(artifact, dict)
            or artifact.get("path") != STANDARD_SCHEMA_PATH
            or artifact.get("sha256") != STANDARD_SCHEMA_SHA256
            or (schema_raw is not None and artifact.get("bytes") != len(schema_raw))):
        reporter.add(
            STANDARD_PROVENANCE_PATH,
            "artifact does not bind the packaged pinned schema",
        )
    if (not isinstance(agent_plugins, dict)
            or agent_plugins.get("specification_version") != "1.0.0"
            or agent_plugins.get("canonical_schema_url") != PLUGIN_SCHEMA
            or agent_plugins.get("release_commit")
            != AGENT_PLUGINS_RELEASE_COMMIT
            or agent_plugins.get("commit_pinned_schema_sha256")
            != STANDARD_SCHEMA_SHA256):
        reporter.add(
            STANDARD_PROVENANCE_PATH,
            "Agent Plugins provenance identity is invalid",
        )
    if (not isinstance(agent_skills, dict)
            or agent_skills.get("commit") != AGENT_SKILLS_COMMIT):
        reporter.add(
            STANDARD_PROVENANCE_PATH,
            "Agent Skills baseline commit is invalid",
        )


def _catalog_skill_paths(catalog, reporter: _Reporter):
    paths = {}
    if not isinstance(catalog, dict):
        return paths
    logical_order = catalog.get("logical_order")
    disciplines = catalog.get("disciplines")
    protocol = catalog.get("protocol")
    if (not isinstance(logical_order, list)
            or not logical_order
            or len(logical_order) != len(set(logical_order))
            or logical_order.count("protocol") != 1
            or any(not isinstance(item, str) for item in logical_order)):
        reporter.add(SYSTEM_CATALOG_PATH, "logical_order must contain protocol exactly once and unique disciplines")
        return paths
    if not isinstance(disciplines, dict):
        reporter.add(SYSTEM_CATALOG_PATH, "disciplines must be an object")
        return paths
    for discipline in logical_order:
        if discipline == "protocol":
            protocol_names = protocol.get("skills") if isinstance(protocol, dict) else None
            if not isinstance(protocol_names, list):
                reporter.add(SYSTEM_CATALOG_PATH, "protocol.skills must be an array")
                continue
            for name in protocol_names:
                if not isinstance(name, str) or name in paths:
                    reporter.add(SYSTEM_CATALOG_PATH, "catalog skill names must be unique strings")
                    continue
                paths[name] = "protocol/%s/SKILL.md" % name
            continue
        definition = disciplines.get(discipline)
        if not isinstance(definition, dict):
            reporter.add(SYSTEM_CATALOG_PATH, "discipline definition is missing: %s" % discipline)
            continue
        phases = definition.get("phases")
        phase_order = definition.get("phase_order")
        if (not isinstance(phases, dict) or not isinstance(phase_order, list)
                or len(phase_order) != len(set(phase_order))
                or any(not isinstance(item, str) for item in phase_order)):
            reporter.add(SYSTEM_CATALOG_PATH, "discipline %s phases/phase_order are invalid" % discipline)
            continue
        for phase in phase_order:
            names = phases.get(phase)
            if not isinstance(names, list):
                reporter.add(SYSTEM_CATALOG_PATH, "discipline %s phase entries are invalid" % discipline)
                continue
            for name in names:
                if not isinstance(name, str) or name in paths:
                    reporter.add(SYSTEM_CATALOG_PATH, "catalog skill names must be unique strings")
                    continue
                paths[name] = "%s/%s/%s/SKILL.md" % (discipline, phase, name)
    if len(paths) != EXPECTED_SKILLS:
        reporter.add(
            SYSTEM_CATALOG_PATH,
            "catalog must resolve exactly %d unique skills; found %d"
            % (EXPECTED_SKILLS, len(paths)),
        )
    return paths


def _validate_profile_and_catalog(
        root: Path, manifest, plugin, projection, reporter: _Reporter) -> None:
    profile_raw = _read_regular(
        root / PORTABLE_PROFILE_PATH, PORTABLE_PROFILE_PATH, reporter,
    )
    profile = None
    if profile_raw is not None:
        profile_digest = hashlib.sha256(profile_raw).hexdigest()
        if manifest.get("profile_definition_sha256") != profile_digest:
            reporter.add(
                DISTRIBUTION_MANIFEST,
                "profile_definition_sha256 does not match the packaged portable profile",
            )
        if manifest.get("host_profile_definition_sha256") != profile_digest:
            reporter.add(
                DISTRIBUTION_MANIFEST,
                "host_profile_definition_sha256 does not match the packaged portable profile",
            )
        profile = _json_bytes(profile_raw, PORTABLE_PROFILE_PATH, reporter)
        expected_profile = {
            "schema_version": "1.0",
            "profile": "portable-lite",
            "host_profile": "agent-plugins-v1",
            "capabilities": PORTABLE_CAPABILITIES,
            "excluded_capabilities": PORTABLE_EXCLUDED_CAPABILITIES,
            "routing_surface": "direct-skill",
            "reference_surface": "packaged-static-closure",
            "connector_surface": "none",
            "mcp_policy": "absent",
            "frontmatter_policy_version": "1.0",
            "package_ceiling": PORTABLE_PACKAGE_CEILING,
        }
        if not isinstance(profile, dict):
            if profile is not None:
                reporter.add(PORTABLE_PROFILE_PATH, "top level must be an object")
        else:
            if set(profile) != PORTABLE_PROFILE_FIELDS:
                reporter.add(
                    PORTABLE_PROFILE_PATH,
                    "must have the closed Portable Lite profile shape",
                )
            for field, expected in expected_profile.items():
                if profile.get(field) != expected:
                    reporter.add(
                        PORTABLE_PROFILE_PATH,
                        "%s does not match the portable-lite contract" % field,
                    )
            if (isinstance(projection, dict)
                    and profile.get("frontmatter_policy_version")
                    != projection.get("frontmatter_policy_version")):
                reporter.add(
                    PORTABLE_PROFILE_PATH,
                    "frontmatter policy does not match the projection",
                )

    catalog_raw = _read_regular(
        root / SYSTEM_CATALOG_PATH, SYSTEM_CATALOG_PATH, reporter,
    )
    if catalog_raw is None:
        return
    catalog_digest = hashlib.sha256(catalog_raw).hexdigest()
    if manifest.get("catalog_sha256") != catalog_digest:
        reporter.add(
            DISTRIBUTION_MANIFEST,
            "catalog_sha256 does not match the packaged system catalog",
        )
    catalog = _json_bytes(catalog_raw, SYSTEM_CATALOG_PATH, reporter)
    if not isinstance(catalog, dict):
        if catalog is not None:
            reporter.add(SYSTEM_CATALOG_PATH, "top level must be an object")
        return
    plugin_version = plugin.get("version") if isinstance(plugin, dict) else None
    if (catalog.get("bundle_version") != plugin_version
            or catalog.get("architecture_version") != plugin_version):
        reporter.add(
            SYSTEM_CATALOG_PATH,
            "bundle/architecture version must match plugin.json",
        )
    counts = catalog.get("counts")
    if not isinstance(counts, dict) or counts.get("total_skills") != EXPECTED_SKILLS:
        reporter.add(
            SYSTEM_CATALOG_PATH,
            "counts.total_skills must be %d" % EXPECTED_SKILLS,
        )
    expected_paths = _catalog_skill_paths(catalog, reporter)
    entries = projection.get("skills") if isinstance(projection, dict) else None
    if isinstance(entries, list):
        mapped_paths = {
            entry.get("name"): entry.get("source_path")
            for entry in entries
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        }
        if mapped_paths != expected_paths:
            for name in sorted(set(mapped_paths) | set(expected_paths)):
                if mapped_paths.get(name) != expected_paths.get(name):
                    reporter.add(
                        PROJECTION_FILE,
                        "source_path for %s does not match %s"
                        % (name, SYSTEM_CATALOG_PATH),
                    )


def _validate_distribution_manifest(
        root: Path, plugin, projection, projection_raw, reporter: _Reporter) -> None:
    location = DISTRIBUTION_MANIFEST
    raw = _read_regular(root / location, location, reporter)
    if raw is None:
        return
    manifest = _json_bytes(raw, location, reporter)
    if not isinstance(manifest, dict):
        if manifest is not None:
            reporter.add(location, "top level must be an object")
        return
    if set(manifest) != AGENT_PLUGIN_MANIFEST_FIELDS:
        missing = sorted(AGENT_PLUGIN_MANIFEST_FIELDS - set(manifest))
        unknown = sorted(set(manifest) - AGENT_PLUGIN_MANIFEST_FIELDS)
        detail = []
        if missing:
            detail.append("missing " + ", ".join(missing))
        if unknown:
            detail.append("unknown " + ", ".join(unknown))
        reporter.add(location, "must have the closed agent-plugin shape (%s)" % "; ".join(detail))
    if not isinstance(manifest.get("schema_version"), str) or not manifest.get("schema_version"):
        reporter.add(location, "schema_version must be a non-empty string")
    if manifest.get("schema_version") != "1.2":
        reporter.add(location, "schema_version must be '1.2'")
    if manifest.get("kind") != "agent-plugin":
        reporter.add(location, "kind must be 'agent-plugin'")
    if manifest.get("profile") != "portable-lite":
        reporter.add(location, "profile must be 'portable-lite'")
    if manifest.get("capability_ceiling") != "portable-lite":
        reporter.add(location, "capability_ceiling must be 'portable-lite'")
    if manifest.get("host_profile") != "agent-plugins-v1":
        reporter.add(location, "host_profile must be 'agent-plugins-v1'")
    if manifest.get("capabilities") != PORTABLE_CAPABILITIES:
        reporter.add(location, "capabilities do not match the typed portable profile")
    if manifest.get("excluded_capabilities") != PORTABLE_EXCLUDED_CAPABILITIES:
        reporter.add(location, "excluded_capabilities do not match the typed portable profile")
    if manifest.get("host_capabilities") != PORTABLE_CAPABILITIES:
        reporter.add(location, "host_capabilities do not match the typed portable profile")
    for field in (
            "catalog_sha256", "profile_definition_sha256",
            "host_profile_definition_sha256"):
        value = manifest.get(field)
        if not isinstance(value, str) or SHA256.fullmatch(value) is None:
            reporter.add(location, "%s must be a lowercase SHA-256 digest" % field)
    if manifest.get("routing_surface") != "direct-skill":
        reporter.add(location, "routing_surface must be 'direct-skill'")
    if manifest.get("reference_surface") != "packaged-static-closure":
        reporter.add(location, "reference_surface must be 'packaged-static-closure'")
    if manifest.get("connector_surface") != "none":
        reporter.add(location, "connector_surface must be 'none'")
    if manifest.get("mcp_policy") != "absent":
        reporter.add(location, "mcp_policy must be 'absent'")
    if manifest.get("package_ceiling") != PORTABLE_PACKAGE_CEILING:
        reporter.add(location, "package_ceiling does not match the typed portable profile")
    if manifest.get("hash_algorithm") != "sha256":
        reporter.add(location, "hash_algorithm must be 'sha256'")
    if manifest.get("manifest_path") != DISTRIBUTION_MANIFEST:
        reporter.add(location, "manifest_path must be %s" % DISTRIBUTION_MANIFEST)
    if manifest.get("manifest_excludes") != [DISTRIBUTION_MANIFEST]:
        reporter.add(location, "manifest_excludes must contain only %s" % DISTRIBUTION_MANIFEST)
    plugin_version = manifest.get("plugin_version")
    if not isinstance(plugin_version, str) or SEMVER.fullmatch(plugin_version) is None:
        reporter.add(location, "plugin_version must be SemVer")
    if isinstance(plugin, dict) and plugin_version != plugin.get("version"):
        reporter.add(location, "plugin_version does not match plugin.json version")
    if isinstance(projection, dict) and plugin_version != projection.get("plugin_version"):
        reporter.add(location, "plugin_version does not match the projection")
    source = manifest.get("source")
    if not isinstance(source, dict) or set(source) != {"repository", "commit"}:
        reporter.add(location, "source must contain exactly repository and commit")
    else:
        repository = source.get("repository")
        commit = source.get("commit")
        if (repository is None) != (commit is None):
            reporter.add(location, "source repository and commit must be supplied together")
        elif repository is not None:
            if (not isinstance(repository, str)
                    or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None):
                reporter.add(location, "source.repository must be an owner/repository slug")
            if (not isinstance(commit, str)
                    or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit) is None):
                reporter.add(location, "source.commit must be a lowercase Git object ID")

    _validate_standard_bundle(root, manifest, reporter)
    _validate_profile_and_catalog(root, manifest, plugin, projection, reporter)

    actual_files = _actual_file_records(root, reporter)
    files = manifest.get("files")
    if not isinstance(files, list):
        reporter.add(location, "files must be an array")
    else:
        seen = set()
        for index, record in enumerate(files):
            record_location = "%s:files[%d]" % (location, index)
            if not isinstance(record, dict):
                reporter.add(record_location, "file record must be an object")
                continue
            if set(record) != FILE_RECORD_FIELDS:
                reporter.add(record_location, "must contain exactly bytes, mode, path, sha256")
            path = _safe_relative(record.get("path"), record_location, "path", reporter)
            if path is not None:
                value = path.as_posix()
                if value == DISTRIBUTION_MANIFEST:
                    reporter.add(record_location, "distribution manifest must exclude itself")
                if value in seen:
                    reporter.add(record_location, "duplicate file path %r" % value)
                seen.add(value)
            if (isinstance(record.get("bytes"), bool)
                    or not isinstance(record.get("bytes"), int)
                    or record.get("bytes", -1) < 0):
                reporter.add(record_location, "bytes must be a non-negative integer")
            if not isinstance(record.get("mode"), str) or re.fullmatch(r"[0-7]{4}", record.get("mode", "")) is None:
                reporter.add(record_location, "mode must be four octal digits")
            if not isinstance(record.get("sha256"), str) or SHA256.fullmatch(record.get("sha256", "")) is None:
                reporter.add(record_location, "sha256 must be a lowercase SHA-256 digest")
        if files != actual_files:
            actual_by_path = {item["path"]: item for item in actual_files}
            declared_by_path = {
                item.get("path"): item for item in files
                if isinstance(item, dict) and isinstance(item.get("path"), str)
            }
            for path in sorted(set(actual_by_path) - set(declared_by_path)):
                reporter.add(location, "files is missing %s" % path)
            for path in sorted(set(declared_by_path) - set(actual_by_path)):
                reporter.add(location, "files declares absent path %s" % path)
            for path in sorted(set(actual_by_path) & set(declared_by_path)):
                if actual_by_path[path] != declared_by_path[path]:
                    reporter.add(location, "file record does not match bytes/mode/hash for %s" % path)
            declared_order = [
                item.get("path") for item in files if isinstance(item, dict)
            ]
            actual_order = [item["path"] for item in actual_files]
            if (declared_order != actual_order
                    and all(isinstance(item, str) for item in declared_order)
                    and set(declared_order) == set(actual_order)):
                reporter.add(location, "files records are not in canonical order")
        try:
            declared_aggregate = hashlib.sha256(_canonical_json(files)).hexdigest()
        except (TypeError, ValueError):
            declared_aggregate = None
        if declared_aggregate is not None and manifest.get("files_sha256") != declared_aggregate:
            reporter.add(location, "files_sha256 does not match the declared files records")
    expected_aggregate = hashlib.sha256(_canonical_json(actual_files)).hexdigest()
    if manifest.get("files_sha256") != expected_aggregate:
        reporter.add(location, "files_sha256 does not match the unpacked package")
    package_bytes = sum(item["bytes"] for item in actual_files) + len(raw)
    package_files = len(actual_files) + 1
    if (package_files > PORTABLE_PACKAGE_CEILING["max_files"]
            or package_bytes > PORTABLE_PACKAGE_CEILING["max_bytes"]):
        reporter.add(
            location,
            "unpacked package exceeds the portable ceiling: %d/%d files, %d/%d bytes"
            % (
                package_files, PORTABLE_PACKAGE_CEILING["max_files"],
                package_bytes, PORTABLE_PACKAGE_CEILING["max_bytes"],
            ),
        )

    binding = manifest.get("agent_plugin_projection")
    if not isinstance(binding, dict):
        reporter.add(location, "agent_plugin_projection must be an object")
        return
    if set(binding) != PROJECTION_BINDING_FIELDS:
        reporter.add(location, "agent_plugin_projection must contain exactly: %s" % ", ".join(sorted(PROJECTION_BINDING_FIELDS)))
    if binding.get("path") != PROJECTION_FILE:
        reporter.add(location, "agent_plugin_projection.path must be %s" % PROJECTION_FILE)
    if projection_raw is not None:
        digest = hashlib.sha256(projection_raw).hexdigest()
        if binding.get("sha256") != digest:
            reporter.add(location, "agent_plugin_projection.sha256 does not match %s" % PROJECTION_FILE)
    elif not isinstance(binding.get("sha256"), str) or SHA256.fullmatch(binding.get("sha256", "")) is None:
        reporter.add(location, "agent_plugin_projection.sha256 must be a lowercase SHA-256 digest")
    if isinstance(projection, dict):
        if binding.get("skill_count") != projection.get("skill_count"):
            reporter.add(location, "agent_plugin_projection.skill_count does not match the projection")
        if binding.get("frontmatter_policy_version") != projection.get("frontmatter_policy_version"):
            reporter.add(location, "agent_plugin_projection.frontmatter_policy_version does not match the projection")


def validate_agent_plugin(package_root) -> list[str]:
    """Return deterministic, package-relative validation errors.

    An empty list means the unpacked directory satisfies the repository's
    strict portable Agent Plugins v1 contract.
    """
    reporter = _Reporter()
    root = Path(package_root)
    try:
        root_status = root.lstat()
    except OSError as exc:
        reporter.add(".", "package root is unavailable (%s)" % exc)
        return reporter.result()
    if stat.S_ISLNK(root_status.st_mode) or not stat.S_ISDIR(root_status.st_mode):
        reporter.add(".", "package root must be a real directory, not a symlink")
        return reporter.result()

    files = _scan_tree(root, reporter)
    plugin = _validate_plugin(root, reporter)
    _validate_forbidden_surfaces(root, plugin, reporter)
    skill_dirs = _validate_skills(root, reporter, files)
    _validate_local_links(root, files, reporter)
    projection, projection_raw = _validate_projection(
        root, plugin, skill_dirs, reporter,
    )
    _validate_distribution_manifest(
        root, plugin, projection, projection_raw, reporter,
    )
    return reporter.result()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an unpacked portable Agent Plugins v1 package.",
    )
    parser.add_argument("package_root", help="path to the unpacked plugin directory")
    args = parser.parse_args(argv)
    errors = validate_agent_plugin(args.package_root)
    if errors:
        for error in errors:
            print("ERROR: %s" % error, file=sys.stderr)
        print("FAILED: %d Agent Plugins v1 validation error(s)" % len(errors), file=sys.stderr)
        return 1
    print("OK: valid Agent Plugins v1 package: %s" % Path(args.package_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
