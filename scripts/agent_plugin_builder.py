#!/usr/bin/env python3
"""Build and verify the generated Agent Plugins v1 Portable Lite surface.

The source repository deliberately keeps its richer, host-specific layout.
This module projects that source into the fixed Agent Plugins discovery layout
without treating commands, hooks, runtimes, connectors, or persistent state as
portable capabilities.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = PurePosixPath("references/system-catalog.json")
CATALOG_SCHEMA_PATH = PurePosixPath("references/system-catalog.schema.json")
PROFILE_PATH = PurePosixPath("references/agent-plugin-portable-profile.json")
PROFILE_SCHEMA_PATH = PurePosixPath("references/agent-plugin-portable-profile.schema.json")
SOURCE_PLUGIN_PATH = PurePosixPath(".claude-plugin/plugin.json")
STANDARD_SCHEMA_PATH = PurePosixPath(
    "references/standards/agent-plugins/1.0.0/plugin.schema.json"
)
STANDARD_PROVENANCE_PATH = PurePosixPath(
    "references/standards/agent-plugins/1.0.0/PROVENANCE.json"
)
DISTRIBUTION_MANIFEST = PurePosixPath("distribution-manifest.json")
PROJECTION_PATH = PurePosixPath("agent-plugin-projection.json")
PORTABILITY_PATH = PurePosixPath("PORTABILITY.md")
PLUGIN_PATH = PurePosixPath("plugin.json")
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PLUGIN_NAME = "aaron-marketing"
PLUGIN_DESCRIPTION = (
    "120 portable marketing Agent Skills across strategy, channels, launch "
    "orchestration, and protocol workflows. Portable Lite provides static "
    "instructions and references only; it does not bundle commands, hooks, MCP "
    "servers, connectors, persistent writes, or deterministic scoring runtimes."
)
STANDARD_SCHEMA_SHA256 = "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
AGENT_PLUGINS_RELEASE_COMMIT = "f24daf829224fd7fb685ae117c518ea27cbe7b9e"
AGENT_SKILLS_COMMIT = "217be548739f21d6008915c29aefe320ea1a90af"
EXPECTED_SKILL_COUNT = 120
MANIFEST_SCHEMA_VERSION = "1.2"
PROJECTION_SCHEMA_VERSION = "1.0"
PROJECTION_KIND = "agent-plugins-v1-projection"
FRONTMATTER_POLICY_VERSION = "1.0"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SOURCE_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SOURCE_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
MARKDOWN_LINK = re.compile(
    r"(?P<image>!?)\[(?P<label>[^\]\n]*)\]\((?P<destination>[^)\n]+)\)"
)
EXTERNAL_LINK = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
PROJECTED_FRONTMATTER_FIELDS = {"name", "description", "license", "metadata"}
REQUIRED_FRONTMATTER_FIELDS = {"name", "description"}
PORTABLE_METADATA_FIELDS = {
    "author", "version", "discipline", "phase", "geo-relevance",
}
PLUGIN_FIELDS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords",
}
PROFILE_FIELDS = {
    "$schema", "schema_version", "profile", "host_profile", "capabilities",
    "excluded_capabilities", "routing_surface", "reference_surface",
    "connector_surface", "mcp_policy", "frontmatter_policy_version",
    "package_ceiling",
}
PROFILE_CONSTANTS = {
    "$schema": "./agent-plugin-portable-profile.schema.json",
    "schema_version": "1.0",
    "profile": "portable-lite",
    "host_profile": "agent-plugins-v1",
    "routing_surface": "direct-skill",
    "reference_surface": "packaged-static-closure",
    "connector_surface": "none",
    "mcp_policy": "absent",
    "frontmatter_policy_version": FRONTMATTER_POLICY_VERSION,
}
EXPECTED_CAPABILITIES = [
    "authored-workflows",
    "inline-delivery",
    "canonical-state-read",
    "static-reference-access",
]
RUNTIME_TOP_LEVEL = {
    ".claude-plugin", ".codex-plugin", ".github", ".githooks",
    "commands", "evals", "hooks", "memory", "scripts", "tests",
}
RESERVED_OUTPUTS = {
    PLUGIN_PATH.as_posix(), PORTABILITY_PATH.as_posix(),
    PROJECTION_PATH.as_posix(), DISTRIBUTION_MANIFEST.as_posix(),
}
STATIC_SUFFIXES = {
    ".avif", ".csv", ".gif", ".htm", ".html", ".jpeg", ".jpg",
    ".json", ".md", ".pdf", ".png", ".svg", ".toml", ".tsv",
    ".txt", ".webp", ".xml", ".yaml", ".yml",
}
STATIC_BASENAMES = {"LICENSE", "NOTICE"}
BOUNDARY_MARKER = "<!-- GENERATED: agent-plugins-v1 portable-lite boundary -->"
BOUNDARY = """\
<!-- GENERATED: agent-plugins-v1 portable-lite boundary -->
> [!IMPORTANT]
> **Portable Lite boundary:** This generated Agent Plugins v1 projection supports
> direct skill discovery, inline delivery, canonical-state reads from packaged
> static references, and static-reference access. Slash commands, hooks, local
> runtime scripts, connector sidecars or native connectors, persistence and
> writes, working memory, registries, runtime controllers, and workflow or audit
> loops are not packaged. Treat runtime instructions as capability-gated guidance;
> any runtime-dependent artifact is `NOT_VERIFIED`. Do not claim execution,
> persistence, selected ancestry, a current head, a verified receipt, or
> permission from static content. See [PORTABILITY.md](../../PORTABILITY.md).
"""
PORTABILITY = """\
# Portable Lite Compatibility Boundary

This directory is a generated, project-defined **Portable Lite** compatibility
projection for Agent Plugins v1. It exposes the standard root `plugin.json` and
120 directly discoverable `skills/<name>/SKILL.md` entries, plus skill-local
static material and the reachable static-reference closure.

## Runtime and persistence boundary

The package intentionally does not include slash commands, hooks, local runtime
scripts, connector sidecars, native plugin connectors, MCP configuration,
working-memory state, registry writers, audit persistence, workflow controllers,
or execution loops. A source skill may describe one of those richer-host paths;
in this package that text is guidance only. Do not report a write, connector
call, deterministic runtime result, persisted audit, or loop execution unless
the active host independently supplies and verifies that capability.

Any locally drafted control artifact is `NOT_VERIFIED`. Static schema presence
does not verify selected ancestry or a current head, does not turn an action
record into a verified receipt, does not grant or consume permission, and does
not prove that state was persisted. Use a Governed runtime for those claims.

Relative links whose source targets require an omitted runtime are redirected to
this section. Static links are rewritten to their projected package locations.

## Provenance

`agent-plugin-projection.json` binds each projected skill to its source path and
the SHA-256 digests of both source and projected `SKILL.md` bytes.
`distribution-manifest.json` binds that projection, the typed Portable Lite
profile, source provenance, and every packaged file.
"""


class AgentPluginError(ValueError):
    """Raised when a portable projection cannot be built or verified safely."""


def _canonical_json(value):
    try:
        return (
            json.dumps(
                value, ensure_ascii=False, allow_nan=False, indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AgentPluginError("cannot encode canonical JSON: %s" % exc) from exc


def _compact_json(value):
    try:
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise AgentPluginError("cannot encode compact JSON: %s" % exc) from exc


def _strict_json(content, label):
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate key: %s" % key)
            value[key] = item
        return value

    try:
        return json.loads(
            content.decode("utf-8"), object_pairs_hook=unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ValueError("non-finite constant: %s" % item)
            ),
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise AgentPluginError("%s is not strict UTF-8 JSON: %s" % (label, exc)) from exc


def _sha256(content):
    return hashlib.sha256(content).hexdigest()


def _relative(value):
    if isinstance(value, (Path, PurePosixPath)):
        value = value.as_posix()
    if not isinstance(value, str) or not value or "\\" in value:
        raise AgentPluginError("unsafe relative path: %r" % value)
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise AgentPluginError("unsafe relative path: %s" % value)
    normalized = posixpath.normpath(value)
    if normalized != value.rstrip("/") or normalized.startswith("../"):
        raise AgentPluginError("non-canonical relative path: %s" % value)
    return PurePosixPath(normalized)


def _source_node(source_root, relative, *, directory=None):
    relative = _relative(relative)
    try:
        root_status = source_root.lstat()
    except OSError as exc:
        raise AgentPluginError("repository root is unavailable: %s" % exc) from exc
    if stat.S_ISLNK(root_status.st_mode) or not stat.S_ISDIR(root_status.st_mode):
        raise AgentPluginError("repository root must be a real directory")
    current = source_root
    status = root_status
    for index, part in enumerate(relative.parts):
        current = current / part
        try:
            status = current.lstat()
        except OSError as exc:
            raise AgentPluginError("required source path is unavailable: %s" % relative) from exc
        if stat.S_ISLNK(status.st_mode):
            raise AgentPluginError("source path contains a symlink: %s" % relative)
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(status.st_mode):
            raise AgentPluginError("source parent is not a directory: %s" % relative)
    if directory is True and not stat.S_ISDIR(status.st_mode):
        raise AgentPluginError("source path must be a directory: %s" % relative)
    if directory is False:
        if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
            raise AgentPluginError("source path must be a single-link regular file: %s" % relative)
    if directory is None and not (stat.S_ISDIR(status.st_mode) or stat.S_ISREG(status.st_mode)):
        raise AgentPluginError("source path is not a regular file or directory: %s" % relative)
    return current, status


def _read_source(source_root, relative):
    path, before = _source_node(source_root, relative, directory=False)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise AgentPluginError("cannot safely open source %s: %s" % (relative, exc)) from exc
    try:
        opened = os.fstat(descriptor)
        identity = ("st_dev", "st_ino", "st_mode", "st_nlink")
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or any(getattr(opened, key) != getattr(before, key) for key in identity)
        ):
            raise AgentPluginError("source changed or became unsafe: %s" % relative)
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            content = handle.read()
            after = os.fstat(handle.fileno())
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(opened, key) != getattr(after, key) for key in stable):
        raise AgentPluginError("source changed while reading: %s" % relative)
    return content


def _write_file(destination, relative, content, mode=0o644):
    relative = _relative(relative)
    target = destination.joinpath(*relative.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise AgentPluginError("projected path already exists: %s" % relative)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(target, flags, mode)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise AgentPluginError("cannot install projected file %s: %s" % (relative, exc)) from exc


def _read_built(destination, relative, label=None):
    relative = _relative(relative)
    path = destination.joinpath(*relative.parts)
    try:
        status = path.lstat()
    except OSError as exc:
        raise AgentPluginError("%s is unavailable: %s" % (label or relative, exc)) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
        raise AgentPluginError("%s must be a single-link regular file" % (label or relative))
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AgentPluginError("cannot read %s: %s" % (label or relative, exc)) from exc


def _load_profile(source_root):
    raw = _read_source(source_root, PROFILE_PATH)
    profile = _strict_json(raw, str(PROFILE_PATH))
    if not isinstance(profile, dict) or set(profile) != PROFILE_FIELDS:
        raise AgentPluginError("portable profile has unknown or missing fields")
    for key, expected in PROFILE_CONSTANTS.items():
        if profile.get(key) != expected:
            raise AgentPluginError("portable profile %s must be %r" % (key, expected))
    if profile.get("capabilities") != EXPECTED_CAPABILITIES:
        raise AgentPluginError("portable profile capabilities are not canonical")
    excluded = profile.get("excluded_capabilities")
    if (
        not isinstance(excluded, list)
        or not excluded
        or len(excluded) != len(set(excluded))
        or any(not isinstance(item, str) or not SAFE_ID.fullmatch(item) for item in excluded)
        or set(excluded) & set(EXPECTED_CAPABILITIES)
    ):
        raise AgentPluginError("portable profile excluded_capabilities are invalid")
    ceiling = profile.get("package_ceiling")
    if (
        not isinstance(ceiling, dict)
        or set(ceiling) != {"max_files", "max_bytes"}
        or isinstance(ceiling["max_files"], bool)
        or not isinstance(ceiling["max_files"], int)
        or not 120 <= ceiling["max_files"] <= 1000
        or isinstance(ceiling["max_bytes"], bool)
        or not isinstance(ceiling["max_bytes"], int)
        or not 1_000_000 <= ceiling["max_bytes"] <= 10_000_000
    ):
        raise AgentPluginError("portable profile package_ceiling is invalid")
    return profile, raw


def _load_catalog(source_root):
    raw = _read_source(source_root, CATALOG_PATH)
    catalog = _strict_json(raw, str(CATALOG_PATH))
    if not isinstance(catalog, dict):
        raise AgentPluginError("system catalog must be an object")
    counts = catalog.get("counts")
    if not isinstance(counts, dict) or counts.get("total_skills") != EXPECTED_SKILL_COUNT:
        raise AgentPluginError("system catalog must declare exactly 120 skills")
    logical_order = catalog.get("logical_order")
    disciplines = catalog.get("disciplines")
    protocol = catalog.get("protocol")
    if (
        not isinstance(logical_order, list)
        or not isinstance(disciplines, dict)
        or not isinstance(protocol, dict)
        or logical_order.count("protocol") != 1
    ):
        raise AgentPluginError("system catalog topology is invalid")
    skills = []
    for discipline in logical_order:
        if discipline == "protocol":
            names = protocol.get("skills")
            if not isinstance(names, list):
                raise AgentPluginError("system catalog protocol skills are invalid")
            for name in names:
                skills.append({
                    "name": name,
                    "source_path": "protocol/%s/SKILL.md" % name,
                })
            continue
        definition = disciplines.get(discipline)
        if not isinstance(definition, dict):
            raise AgentPluginError("system catalog discipline is missing: %s" % discipline)
        phases = definition.get("phases")
        phase_order = definition.get("phase_order")
        if not isinstance(phases, dict) or not isinstance(phase_order, list):
            raise AgentPluginError("system catalog phases are invalid: %s" % discipline)
        for phase in phase_order:
            names = phases.get(phase)
            if not isinstance(names, list):
                raise AgentPluginError("system catalog phase is invalid: %s/%s" % (discipline, phase))
            for name in names:
                skills.append({
                    "name": name,
                    "source_path": "%s/%s/%s/SKILL.md" % (discipline, phase, name),
                })
    names = [item["name"] for item in skills]
    paths = [item["source_path"] for item in skills]
    if (
        len(skills) != EXPECTED_SKILL_COUNT
        or len(set(names)) != EXPECTED_SKILL_COUNT
        or len(set(paths)) != EXPECTED_SKILL_COUNT
        or any(not isinstance(name, str) or not SAFE_ID.fullmatch(name) for name in names)
    ):
        raise AgentPluginError("system catalog must enumerate 120 unique safe skill names")
    for item in skills:
        _source_node(source_root, item["source_path"], directory=False)
    return sorted(skills, key=lambda item: item["name"]), catalog, raw


def _parse_frontmatter(content, label):
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AgentPluginError("%s is not UTF-8" % label) from exc
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise AgentPluginError("%s has no frontmatter" % label)
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise AgentPluginError("%s has unterminated frontmatter" % label) from exc
    values = {}
    raw_values = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line[:1].isspace() or ":" not in line:
            raise AgentPluginError("%s frontmatter must use one-line top-level fields" % label)
        key, value = line.rstrip("\r\n").split(":", 1)
        if key in values or not key:
            raise AgentPluginError("%s frontmatter has duplicate or empty field %r" % (label, key))
        raw_value = value.lstrip()
        values[key] = _yaml_scalar(raw_value, "%s.%s" % (label, key))
        raw_values[key] = raw_value
    return values, raw_values, "".join(lines[end + 1:])


def _yaml_scalar(raw, label):
    if not raw:
        return ""
    if raw[0] in {'"', "'"}:
        if len(raw) < 2 or raw[-1] != raw[0]:
            raise AgentPluginError("%s has an unsupported quoted scalar" % label)
        if raw[0] == '"':
            try:
                value = json.loads(raw)
            except ValueError as exc:
                raise AgentPluginError("%s has an invalid quoted scalar" % label) from exc
            if not isinstance(value, str):
                raise AgentPluginError("%s must be a string scalar" % label)
            return value
        return raw[1:-1].replace("''", "'")
    return raw


def _project_frontmatter(content, skill_name, source_path):
    values, raw_values, body = _parse_frontmatter(content, source_path)
    if values.get("name") != skill_name:
        raise AgentPluginError("source skill name does not match catalog: %s" % source_path)
    if any(key not in values for key in ("description", "license", "metadata")):
        raise AgentPluginError("source skill lacks portable frontmatter inputs: %s" % source_path)
    try:
        source_metadata = _strict_json(
            raw_values["metadata"].encode("utf-8"), "%s metadata" % source_path,
        )
    except AgentPluginError:
        raise
    if not isinstance(source_metadata, dict):
        raise AgentPluginError("source skill metadata must be an object: %s" % source_path)
    metadata = {}
    for key, value in sorted(source_metadata.items()):
        if key not in PORTABLE_METADATA_FIELDS:
            continue
        if not isinstance(key, str) or not key:
            raise AgentPluginError("source skill metadata key is invalid: %s" % source_path)
        metadata[key] = value if isinstance(value, str) else _compact_json(value)
    if "class" in values:
        metadata["class"] = values["class"]
    if not metadata or any(not isinstance(value, str) for value in metadata.values()):
        raise AgentPluginError("projected skill metadata must map strings to strings: %s" % source_path)
    output = ["---\n"]
    # Host compatibility declarations and tool pre-approvals belong to the
    # richer source channels.  Portable Lite is intentionally authority-free.
    ordered = ("name", "description", "license")
    for key in ordered:
        if key in raw_values:
            output.append("%s: %s\n" % (key, raw_values[key]))
    output.append("metadata: %s\n" % _compact_json(metadata))
    output.append("---\n\n")
    return "".join(output), body


def _static_file(relative):
    path = PurePosixPath(relative)
    if not path.parts or path.parts[0] in RUNTIME_TOP_LEVEL:
        return False
    if path.as_posix() in RESERVED_OUTPUTS or path.parts[0] == "skills":
        return False
    return path.name in STATIC_BASENAMES or path.suffix.lower() in STATIC_SUFFIXES


def _runtime_target(relative):
    parts = PurePosixPath(relative).parts
    return not parts or parts[0] in RUNTIME_TOP_LEVEL


def _source_tree_files(source_root, directory):
    directory = _relative(directory)
    root, _ = _source_node(source_root, directory, directory=True)
    results = []

    def visit(path, relative):
        try:
            entries = sorted(os.scandir(path), key=lambda item: item.name)
        except OSError as exc:
            raise AgentPluginError("cannot scan source directory %s: %s" % (relative, exc)) from exc
        for entry in entries:
            child_relative = relative / entry.name
            try:
                status = (path / entry.name).lstat()
            except OSError as exc:
                raise AgentPluginError("cannot inspect source %s: %s" % (child_relative, exc)) from exc
            if stat.S_ISLNK(status.st_mode):
                raise AgentPluginError("source tree contains a symlink: %s" % child_relative)
            if stat.S_ISDIR(status.st_mode):
                visit(path / entry.name, child_relative)
            elif stat.S_ISREG(status.st_mode) and status.st_nlink == 1:
                results.append(child_relative)
            else:
                raise AgentPluginError("source tree contains an unsafe node: %s" % child_relative)

    visit(root, directory)
    return results


class _Projection:
    def __init__(self, source_root, destination, skills):
        self.source_root = source_root
        self.destination = destination
        self.skills = skills
        self.skill_roots = {
            PurePosixPath(item["source_path"]).parent: item["name"] for item in skills
        }
        self.root_pending = deque()
        self.root_seen = set()

    def _skill_mapping(self, source_relative):
        source_relative = PurePosixPath(source_relative)
        for root, name in self.skill_roots.items():
            if source_relative == root:
                return PurePosixPath("skills") / name
            try:
                remainder = source_relative.relative_to(root)
            except ValueError:
                continue
            return PurePosixPath("skills") / name / remainder
        return None

    def _normalize_link(self, source_file, destination):
        stripped = destination.strip()
        title_suffix = ""
        if stripped.startswith("<"):
            closing = stripped.find(">")
            if closing < 0:
                return None, "", ""
            target = stripped[1:closing]
            title_suffix = stripped[closing + 1:]
            wrapper = "angle"
        else:
            match = re.match(r"([^\s]+)(.*)$", stripped, re.DOTALL)
            if not match:
                return None, "", ""
            target, title_suffix = match.groups()
            wrapper = "plain"
        if (
            not target
            or target.startswith("#")
            or target.startswith("//")
            or EXTERNAL_LINK.match(target)
        ):
            return "external", target, (wrapper, title_suffix)
        path_text, separator, fragment = target.partition("#")
        if not path_text or path_text.startswith("/") or "\\" in path_text:
            return None, fragment if separator else "", (wrapper, title_suffix)
        normalized = posixpath.normpath(
            posixpath.join(PurePosixPath(source_file).parent.as_posix(), path_text)
        )
        if normalized in {"", ".", ".."} or normalized.startswith("../"):
            return None, fragment if separator else "", (wrapper, title_suffix)
        return PurePosixPath(normalized), fragment if separator else "", (wrapper, title_suffix)

    def _redirect(self, output_file):
        return self._relative_output_link(
            PurePosixPath(output_file), PORTABILITY_PATH,
        ) + "#runtime-and-persistence-boundary"

    @staticmethod
    def _relative_output_link(output_file, output_target, *, directory=False):
        start = PurePosixPath(output_file).parent.as_posix()
        value = posixpath.relpath(PurePosixPath(output_target).as_posix(), start=start)
        if directory and not value.endswith("/"):
            value += "/"
        return value

    def _target(self, source_file, output_file, raw_destination):
        normalized, fragment, wrapper = self._normalize_link(source_file, raw_destination)
        if normalized == "external":
            return raw_destination
        if normalized is None:
            return self._redirect(output_file)
        source_target = normalized
        mapped = self._skill_mapping(source_target)
        target_path = self.source_root.joinpath(*source_target.parts)
        try:
            status = target_path.lstat()
        except OSError:
            return self._redirect(output_file)
        if stat.S_ISLNK(status.st_mode):
            return self._redirect(output_file)
        is_directory = stat.S_ISDIR(status.st_mode)
        if not is_directory and (not stat.S_ISREG(status.st_mode) or status.st_nlink != 1):
            return self._redirect(output_file)
        if mapped is not None:
            if not is_directory and not _static_file(source_target):
                return self._redirect(output_file)
            output_target = mapped
        else:
            if _runtime_target(source_target):
                return self._redirect(output_file)
            if is_directory:
                for child in _source_tree_files(self.source_root, source_target):
                    if _static_file(child):
                        self.root_pending.append(child)
            elif _static_file(source_target):
                self.root_pending.append(source_target)
            else:
                return self._redirect(output_file)
            output_target = source_target
        link = self._relative_output_link(output_file, output_target, directory=is_directory)
        if fragment:
            link += "#" + fragment
        wrapper_kind, title_suffix = wrapper
        if wrapper_kind == "angle":
            return "<%s>%s" % (link, title_suffix)
        return link + title_suffix

    def rewrite_markdown(self, content, source_file, output_file):
        try:
            text = content.decode("utf-8") if isinstance(content, bytes) else content
        except UnicodeDecodeError as exc:
            raise AgentPluginError("Markdown source is not UTF-8: %s" % source_file) from exc

        def replace(match):
            destination = self._target(
                source_file, output_file, match.group("destination")
            )
            return "%s[%s](%s)" % (
                match.group("image"), match.group("label"), destination,
            )

        return MARKDOWN_LINK.sub(replace, text).encode("utf-8")

    def copy_skill(self, item):
        name = item["name"]
        source_skill = PurePosixPath(item["source_path"])
        source_root = source_skill.parent
        source_bytes = _read_source(self.source_root, source_skill)
        frontmatter, body = _project_frontmatter(
            source_bytes, name, source_skill.as_posix(),
        )
        output_skill = PurePosixPath("skills") / name / "SKILL.md"
        rewritten_body = self.rewrite_markdown(
            body.encode("utf-8"), source_skill, output_skill,
        ).decode("utf-8")
        projected = (frontmatter + BOUNDARY + "\n" + rewritten_body).encode("utf-8")
        _write_file(self.destination, output_skill, projected)
        for source_file in _source_tree_files(self.source_root, source_root):
            if source_file == source_skill:
                continue
            output_file = self._skill_mapping(source_file)
            if output_file is None or not _static_file(source_file):
                continue
            content = _read_source(self.source_root, source_file)
            if source_file.suffix.lower() == ".md":
                content = self.rewrite_markdown(content, source_file, output_file)
            _write_file(self.destination, output_file, content)
        return {
            "name": name,
            "source_path": source_skill.as_posix(),
            "projected_path": output_skill.as_posix(),
            "source_sha256": _sha256(source_bytes),
            "projected_sha256": _sha256(projected),
        }

    def copy_root_closure(self):
        while self.root_pending:
            source_file = PurePosixPath(self.root_pending.popleft())
            key = source_file.as_posix()
            if key in self.root_seen:
                continue
            self.root_seen.add(key)
            if not _static_file(source_file):
                continue
            if self._skill_mapping(source_file) is not None:
                continue
            content = _read_source(self.source_root, source_file)
            if source_file.suffix.lower() == ".md":
                content = self.rewrite_markdown(content, source_file, source_file)
            _write_file(self.destination, source_file, content)


def _plugin_manifest(source_root, catalog):
    source = _strict_json(
        _read_source(source_root, SOURCE_PLUGIN_PATH), str(SOURCE_PLUGIN_PATH),
    )
    if not isinstance(source, dict):
        raise AgentPluginError("source plugin manifest must be an object")
    version = catalog.get("bundle_version")
    if not isinstance(version, str) or source.get("version") != version:
        raise AgentPluginError("source plugin version does not match system catalog")
    manifest = {
        "$schema": PLUGIN_SCHEMA,
        "name": PLUGIN_NAME,
        "description": PLUGIN_DESCRIPTION,
    }
    for key in (
        "version", "author", "homepage", "repository", "license",
        "keywords",
    ):
        if key in source:
            manifest[key] = source[key]
    if set(manifest) - PLUGIN_FIELDS:
        raise AgentPluginError("projected plugin manifest contains unsupported fields")
    return manifest


def _files(destination):
    records = []

    def visit(directory):
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise AgentPluginError("cannot inspect projected distribution: %s" % exc) from exc
        for entry in entries:
            path = directory / entry.name
            relative = PurePosixPath(path.relative_to(destination).as_posix())
            try:
                status = path.lstat()
            except OSError as exc:
                raise AgentPluginError("cannot inspect projected output %s" % relative) from exc
            if stat.S_ISLNK(status.st_mode):
                raise AgentPluginError("projected distribution contains a symlink: %s" % relative)
            if stat.S_ISDIR(status.st_mode):
                visit(path)
                continue
            if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
                raise AgentPluginError("projected distribution contains an unsafe file: %s" % relative)
            if relative == DISTRIBUTION_MANIFEST:
                continue
            content = path.read_bytes()
            records.append({
                "bytes": len(content),
                "mode": "%04o" % stat.S_IMODE(status.st_mode),
                "path": relative.as_posix(),
                "sha256": _sha256(content),
            })

    visit(destination)
    return records


def _validate_source_identity(repository, commit):
    if (repository is None) != (commit is None):
        raise AgentPluginError("source repository and commit must be supplied together")
    if repository is not None and (
        not isinstance(repository, str) or not SOURCE_REPOSITORY.fullmatch(repository)
    ):
        raise AgentPluginError("source repository must be an owner/repository slug")
    if commit is not None and (
        not isinstance(commit, str) or not SOURCE_COMMIT.fullmatch(commit)
    ):
        raise AgentPluginError("source commit must be a lowercase 40- or 64-hex object ID")


def _validate_ceiling(files, ceiling, manifest_bytes=0):
    count = len(files) + (1 if manifest_bytes else 0)
    size = sum(item["bytes"] for item in files) + manifest_bytes
    if count > ceiling["max_files"] or size > ceiling["max_bytes"]:
        raise AgentPluginError(
            "portable package exceeds ceiling: %d/%d files, %d/%d bytes"
            % (count, ceiling["max_files"], size, ceiling["max_bytes"])
        )


MANIFEST_FIELDS = {
    "schema_version", "kind", "plugin_version", "profile",
    "capability_ceiling", "capabilities", "excluded_capabilities",
    "catalog_sha256", "profile_definition_sha256", "host_profile",
    "host_capabilities", "host_profile_definition_sha256", "routing_surface",
    "reference_surface", "connector_surface", "mcp_policy", "package_ceiling",
    "hash_algorithm", "manifest_path", "manifest_excludes", "source",
    "standard", "agent_plugin_projection", "files_sha256", "files",
}


def _standard_bundle(source_root):
    schema_bytes = _read_source(source_root, STANDARD_SCHEMA_PATH)
    provenance_bytes = _read_source(source_root, STANDARD_PROVENANCE_PATH)
    if _sha256(schema_bytes) != STANDARD_SCHEMA_SHA256:
        raise AgentPluginError("vendored Agent Plugins schema digest is not canonical")
    schema = _strict_json(schema_bytes, str(STANDARD_SCHEMA_PATH))
    provenance = _strict_json(provenance_bytes, str(STANDARD_PROVENANCE_PATH))
    try:
        provenance_artifact = provenance["artifact"]
        agent_plugins = provenance["agent_plugins"]
        agent_skills = provenance["agent_skills_baseline"]
    except (KeyError, TypeError) as exc:
        raise AgentPluginError("Agent Plugins standard provenance is incomplete") from exc
    if (
        not isinstance(schema, dict)
        or schema.get("$id") != PLUGIN_SCHEMA
        or provenance_artifact.get("path") != STANDARD_SCHEMA_PATH.as_posix()
        or provenance_artifact.get("sha256") != STANDARD_SCHEMA_SHA256
        or agent_plugins.get("specification_version") != "1.0.0"
        or agent_plugins.get("canonical_schema_url") != PLUGIN_SCHEMA
        or agent_plugins.get("release_commit") != AGENT_PLUGINS_RELEASE_COMMIT
        or agent_skills.get("commit") != AGENT_SKILLS_COMMIT
    ):
        raise AgentPluginError("Agent Plugins standard provenance does not match baselines")
    return schema_bytes, provenance_bytes, {
        "name": "agent-plugins",
        "version": "1.0.0",
        "schema_url": PLUGIN_SCHEMA,
        "schema_path": STANDARD_SCHEMA_PATH.as_posix(),
        "schema_sha256": STANDARD_SCHEMA_SHA256,
        "provenance_path": STANDARD_PROVENANCE_PATH.as_posix(),
        "provenance_sha256": _sha256(provenance_bytes),
        "agent_skills_commit": AGENT_SKILLS_COMMIT,
    }


def _install_or_confirm(destination, relative, content):
    path = destination.joinpath(*PurePosixPath(relative).parts)
    if path.exists() and not path.is_symlink():
        if _read_built(destination, relative) != content:
            raise AgentPluginError("projected static standard differs: %s" % relative)
        return
    _write_file(destination, relative, content)


def build_agent_plugin(
    destination, source_root=ROOT, source_repository=None, source_commit=None,
):
    """Build one complete Portable Lite package into an empty destination."""
    destination = Path(destination)
    source_root = Path(source_root)
    _validate_source_identity(source_repository, source_commit)
    try:
        status = destination.lstat()
    except FileNotFoundError:
        destination.mkdir(parents=True)
        status = destination.lstat()
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise AgentPluginError("destination must be a real directory")
    if any(destination.iterdir()):
        raise AgentPluginError("destination must be empty")
    profile, profile_raw = _load_profile(source_root)
    profile_schema_raw = _read_source(source_root, PROFILE_SCHEMA_PATH)
    skills, catalog, catalog_raw = _load_catalog(source_root)
    catalog_schema_raw = _read_source(source_root, CATALOG_SCHEMA_PATH)
    standard_schema, standard_provenance, standard = _standard_bundle(source_root)
    plugin = _plugin_manifest(source_root, catalog)
    _write_file(destination, PLUGIN_PATH, _canonical_json(plugin))
    _write_file(destination, PORTABILITY_PATH, PORTABILITY.encode("utf-8"))

    projection_builder = _Projection(source_root, destination, skills)
    projected_skills = [projection_builder.copy_skill(item) for item in skills]
    projection_builder.copy_root_closure()
    _install_or_confirm(destination, CATALOG_PATH, catalog_raw)
    _install_or_confirm(destination, CATALOG_SCHEMA_PATH, catalog_schema_raw)
    _install_or_confirm(destination, PROFILE_PATH, profile_raw)
    _install_or_confirm(destination, PROFILE_SCHEMA_PATH, profile_schema_raw)
    _install_or_confirm(destination, STANDARD_SCHEMA_PATH, standard_schema)
    _install_or_confirm(destination, STANDARD_PROVENANCE_PATH, standard_provenance)
    projection = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "kind": PROJECTION_KIND,
        "plugin_version": plugin["version"],
        "source_root": ".",
        "frontmatter_policy_version": profile["frontmatter_policy_version"],
        "skill_count": len(projected_skills),
        "skills": projected_skills,
    }
    projection_bytes = _canonical_json(projection)
    _write_file(destination, PROJECTION_PATH, projection_bytes)

    files = _files(destination)
    _validate_ceiling(files, profile["package_ceiling"])
    definition_sha = _sha256(profile_raw)
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "kind": "agent-plugin",
        "plugin_version": plugin["version"],
        "profile": profile["profile"],
        "capability_ceiling": profile["profile"],
        "capabilities": profile["capabilities"],
        "excluded_capabilities": profile["excluded_capabilities"],
        "catalog_sha256": _sha256(catalog_raw),
        "profile_definition_sha256": definition_sha,
        "host_profile": profile["host_profile"],
        "host_capabilities": profile["capabilities"],
        "host_profile_definition_sha256": definition_sha,
        "routing_surface": profile["routing_surface"],
        "reference_surface": profile["reference_surface"],
        "connector_surface": profile["connector_surface"],
        "mcp_policy": profile["mcp_policy"],
        "package_ceiling": profile["package_ceiling"],
        "hash_algorithm": "sha256",
        "manifest_path": DISTRIBUTION_MANIFEST.as_posix(),
        "manifest_excludes": [DISTRIBUTION_MANIFEST.as_posix()],
        "source": {"repository": source_repository, "commit": source_commit},
        "standard": standard,
        "agent_plugin_projection": {
            "path": PROJECTION_PATH.as_posix(),
            "sha256": _sha256(projection_bytes),
            "skill_count": EXPECTED_SKILL_COUNT,
            "frontmatter_policy_version": FRONTMATTER_POLICY_VERSION,
        },
        "files_sha256": _sha256(_canonical_json(files)),
        "files": files,
    }
    if set(manifest) != MANIFEST_FIELDS:
        raise AgentPluginError("internal agent-plugin manifest shape drift")
    manifest_bytes = _canonical_json(manifest)
    _validate_ceiling(files, profile["package_ceiling"], len(manifest_bytes))
    _write_file(destination, DISTRIBUTION_MANIFEST, manifest_bytes, mode=0o600)
    return verify_agent_plugin_distribution(
        destination,
        expected_repository=source_repository,
        expected_commit=source_commit,
        expected_profile=profile["profile"],
        expected_host_profile=profile["host_profile"],
        source_root=source_root,
    )


def _frontmatter_from_built(content, label):
    values, raw_values, body = _parse_frontmatter(content, label)
    if set(values) != PROJECTED_FRONTMATTER_FIELDS:
        raise AgentPluginError("projected skill frontmatter violates Portable Lite policy: %s" % label)
    if not REQUIRED_FRONTMATTER_FIELDS.issubset(values):
        raise AgentPluginError("projected skill lacks required frontmatter: %s" % label)
    metadata_raw = raw_values.get("metadata")
    if metadata_raw is not None:
        metadata = _strict_json(metadata_raw.encode("utf-8"), "%s metadata" % label)
        if (
            not isinstance(metadata, dict)
            or any(not isinstance(key, str) or not isinstance(value, str)
                   for key, value in metadata.items())
            or set(metadata) - (PORTABLE_METADATA_FIELDS | {"class"})
        ):
            raise AgentPluginError(
                "projected skill metadata violates Portable Lite policy: %s" % label
            )
    if BOUNDARY_MARKER not in body:
        raise AgentPluginError("projected skill lacks the Portable Lite boundary: %s" % label)
    return values


def _validate_internal_links(destination, relative, content):
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AgentPluginError("projected Markdown is not UTF-8: %s" % relative) from exc
    for match in MARKDOWN_LINK.finditer(text):
        raw = match.group("destination").strip()
        if raw.startswith("<"):
            close = raw.find(">")
            raw = raw[1:close] if close >= 0 else raw
        else:
            raw = raw.split(None, 1)[0]
        if not raw or raw.startswith("#") or raw.startswith("//") or EXTERNAL_LINK.match(raw):
            continue
        target = raw.split("#", 1)[0]
        if not target:
            continue
        normalized = posixpath.normpath(
            posixpath.join(PurePosixPath(relative).parent.as_posix(), target)
        )
        if normalized.startswith("../") or normalized in {".", ".."}:
            raise AgentPluginError("projected Markdown link escapes package: %s -> %s" % (relative, raw))
        path = destination.joinpath(*PurePosixPath(normalized).parts)
        try:
            status = path.lstat()
        except OSError as exc:
            raise AgentPluginError("projected Markdown link is broken: %s -> %s" % (relative, raw)) from exc
        if stat.S_ISLNK(status.st_mode):
            raise AgentPluginError("projected Markdown link targets a symlink: %s -> %s" % (relative, raw))


def verify_agent_plugin_distribution(
    destination, expected_repository=None, expected_commit=None,
    expected_profile=None, expected_host_profile=None, source_root=ROOT,
):
    """Read-only, strict verification of one generated Portable Lite package."""
    destination = Path(destination)
    source_root = Path(source_root)
    _validate_source_identity(expected_repository, expected_commit)
    profile, profile_raw = _load_profile(source_root)
    profile_schema_raw = _read_source(source_root, PROFILE_SCHEMA_PATH)
    skills, catalog, catalog_raw = _load_catalog(source_root)
    catalog_schema_raw = _read_source(source_root, CATALOG_SCHEMA_PATH)
    standard_schema, standard_provenance, standard = _standard_bundle(source_root)
    manifest_bytes = _read_built(destination, DISTRIBUTION_MANIFEST, "distribution manifest")
    manifest = _strict_json(manifest_bytes, "distribution manifest")
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_FIELDS:
        raise AgentPluginError("agent-plugin distribution manifest has unknown or missing fields")
    definition_sha = _sha256(profile_raw)
    static_expectations = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "kind": "agent-plugin",
        "profile": profile["profile"],
        "capability_ceiling": profile["profile"],
        "capabilities": profile["capabilities"],
        "excluded_capabilities": profile["excluded_capabilities"],
        "catalog_sha256": _sha256(catalog_raw),
        "profile_definition_sha256": definition_sha,
        "host_profile": profile["host_profile"],
        "host_capabilities": profile["capabilities"],
        "host_profile_definition_sha256": definition_sha,
        "routing_surface": profile["routing_surface"],
        "reference_surface": profile["reference_surface"],
        "connector_surface": profile["connector_surface"],
        "mcp_policy": profile["mcp_policy"],
        "package_ceiling": profile["package_ceiling"],
        "hash_algorithm": "sha256",
        "manifest_path": DISTRIBUTION_MANIFEST.as_posix(),
        "manifest_excludes": [DISTRIBUTION_MANIFEST.as_posix()],
        "standard": standard,
    }
    for key, expected in static_expectations.items():
        if manifest.get(key) != expected:
            raise AgentPluginError("agent-plugin manifest %s does not match its typed source" % key)
    if expected_profile is not None and manifest["profile"] != expected_profile:
        raise AgentPluginError("agent-plugin manifest profile does not match")
    if expected_host_profile is not None and manifest["host_profile"] != expected_host_profile:
        raise AgentPluginError("agent-plugin manifest host profile does not match")
    source = manifest.get("source")
    if not isinstance(source, dict) or set(source) != {"repository", "commit"}:
        raise AgentPluginError("agent-plugin manifest source provenance is invalid")
    _validate_source_identity(source["repository"], source["commit"])
    if expected_repository is not None and source != {
        "repository": expected_repository, "commit": expected_commit,
    }:
        raise AgentPluginError("agent-plugin manifest source provenance does not match")
    if manifest.get("standard") != standard:
        raise AgentPluginError("agent-plugin standard binding is invalid")
    if _read_built(destination, CATALOG_PATH) != catalog_raw:
        raise AgentPluginError("packaged system catalog differs from its manifest binding")
    if _read_built(destination, CATALOG_SCHEMA_PATH) != catalog_schema_raw:
        raise AgentPluginError("packaged system catalog schema differs from source")
    if _read_built(destination, PROFILE_PATH) != profile_raw:
        raise AgentPluginError("packaged Portable Lite profile differs from its manifest binding")
    if _read_built(destination, PROFILE_SCHEMA_PATH) != profile_schema_raw:
        raise AgentPluginError("packaged Portable Lite profile schema differs from source")
    if _read_built(destination, STANDARD_SCHEMA_PATH) != standard_schema:
        raise AgentPluginError("packaged Agent Plugins schema differs from its standard binding")
    if _read_built(destination, STANDARD_PROVENANCE_PATH) != standard_provenance:
        raise AgentPluginError("packaged Agent Plugins provenance differs from its binding")

    plugin_bytes = _read_built(destination, PLUGIN_PATH, "Agent Plugins root manifest")
    plugin = _strict_json(plugin_bytes, "Agent Plugins root manifest")
    if (
        not isinstance(plugin, dict)
        or set(plugin) - PLUGIN_FIELDS
        or plugin.get("$schema") != PLUGIN_SCHEMA
        or plugin.get("name") != PLUGIN_NAME
        or plugin.get("description") != PLUGIN_DESCRIPTION
        or not isinstance(plugin.get("version"), str)
        or plugin.get("version") != catalog.get("bundle_version")
        or manifest.get("plugin_version") != plugin.get("version")
    ):
        raise AgentPluginError("Agent Plugins root manifest is invalid")
    if (destination / "mcp.json").exists() or (destination / "mcp.json").is_symlink():
        raise AgentPluginError("Portable Lite must not contain mcp.json")
    for forbidden in RUNTIME_TOP_LEVEL:
        if (destination / forbidden).exists() or (destination / forbidden).is_symlink():
            raise AgentPluginError("runtime surface leaked into Portable Lite: %s" % forbidden)

    projection_bytes = _read_built(destination, PROJECTION_PATH, "agent-plugin projection")
    projection = _strict_json(projection_bytes, "agent-plugin projection")
    projection_fields = {
        "schema_version", "kind", "plugin_version", "source_root",
        "frontmatter_policy_version", "skill_count", "skills",
    }
    if (
        not isinstance(projection, dict)
        or set(projection) != projection_fields
        or projection.get("schema_version") != PROJECTION_SCHEMA_VERSION
        or projection.get("kind") != PROJECTION_KIND
        or projection.get("plugin_version") != plugin["version"]
        or projection.get("source_root") != "."
        or projection.get("frontmatter_policy_version") != FRONTMATTER_POLICY_VERSION
        or projection.get("skill_count") != EXPECTED_SKILL_COUNT
        or not isinstance(projection.get("skills"), list)
    ):
        raise AgentPluginError("agent-plugin projection identity is invalid")
    binding = manifest.get("agent_plugin_projection")
    expected_binding = {
        "path": PROJECTION_PATH.as_posix(),
        "sha256": _sha256(projection_bytes),
        "skill_count": EXPECTED_SKILL_COUNT,
        "frontmatter_policy_version": FRONTMATTER_POLICY_VERSION,
    }
    if binding != expected_binding:
        raise AgentPluginError("agent-plugin projection binding is invalid")

    entries = projection["skills"]
    entry_fields = {
        "name", "source_path", "projected_path", "source_sha256",
        "projected_sha256",
    }
    if (
        len(entries) != EXPECTED_SKILL_COUNT
        or [item.get("name") for item in entries if isinstance(item, dict)]
        != sorted(item["name"] for item in skills)
        or any(not isinstance(item, dict) or set(item) != entry_fields for item in entries)
    ):
        raise AgentPluginError("agent-plugin projection skill list is invalid")
    expected_sources = {item["name"]: item["source_path"] for item in skills}
    direct_names = set()
    for entry in entries:
        name = entry["name"]
        source_path = expected_sources.get(name)
        projected_path = "skills/%s/SKILL.md" % name
        if (
            source_path is None
            or entry["source_path"] != source_path
            or entry["projected_path"] != projected_path
            or not isinstance(entry["source_sha256"], str)
            or not SHA256.fullmatch(entry["source_sha256"])
            or not isinstance(entry["projected_sha256"], str)
            or not SHA256.fullmatch(entry["projected_sha256"])
        ):
            raise AgentPluginError("agent-plugin projection entry is invalid: %s" % name)
        source_bytes = _read_source(source_root, source_path)
        projected_bytes = _read_built(destination, projected_path, "projected skill %s" % name)
        if _sha256(source_bytes) != entry["source_sha256"]:
            raise AgentPluginError("projection source hash differs: %s" % name)
        if _sha256(projected_bytes) != entry["projected_sha256"]:
            raise AgentPluginError("projection output hash differs: %s" % name)
        values = _frontmatter_from_built(projected_bytes, projected_path)
        if values.get("name") != name:
            raise AgentPluginError("projected skill name differs: %s" % name)
        direct_names.add(name)

    skills_root = destination / "skills"
    try:
        direct_entries = sorted(os.scandir(skills_root), key=lambda item: item.name)
    except OSError as exc:
        raise AgentPluginError("projected skills directory is unavailable") from exc
    actual_direct = set()
    for item in direct_entries:
        status = (skills_root / item.name).lstat()
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
            raise AgentPluginError("skills must contain only direct skill directories")
        actual_direct.add(item.name)
    if actual_direct != direct_names:
        raise AgentPluginError("direct skill discovery set does not match projection")
    all_skill_files = sorted(skills_root.rglob("SKILL.md"))
    if len(all_skill_files) != EXPECTED_SKILL_COUNT:
        raise AgentPluginError("Portable Lite must contain exactly 120 SKILL.md files")

    actual_files = _files(destination)
    if manifest.get("files") != actual_files:
        raise AgentPluginError("agent-plugin files do not match the SHA-256 manifest")
    if manifest.get("files_sha256") != _sha256(_canonical_json(actual_files)):
        raise AgentPluginError("agent-plugin aggregate SHA-256 is invalid")
    _validate_ceiling(actual_files, profile["package_ceiling"], len(manifest_bytes))
    paths = {item["path"] for item in actual_files}
    if not {PLUGIN_PATH.as_posix(), PORTABILITY_PATH.as_posix(), PROJECTION_PATH.as_posix()}.issubset(paths):
        raise AgentPluginError("Portable Lite generated roots are incomplete")
    for record in actual_files:
        if record["path"].endswith(".md"):
            _validate_internal_links(
                destination, record["path"],
                _read_built(destination, record["path"]),
            )
    return manifest


def distribution_kind(destination):
    """Return a readable manifest kind, or ``None`` for absent/invalid JSON."""
    try:
        raw = _read_built(Path(destination), DISTRIBUTION_MANIFEST)
        value = _strict_json(raw, "distribution manifest")
    except AgentPluginError:
        return None
    return value.get("kind") if isinstance(value, dict) else None
