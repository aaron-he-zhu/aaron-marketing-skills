#!/usr/bin/env python3
"""Verify the pinned Agent Plugins v1 and Agent Skills standard baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = Path("references/standards/agent-plugins/1.0.0/PROVENANCE.json")
MAX_REMOTE_BYTES = 1_000_000
SHA256 = re.compile(r"^[0-9a-f]{64}$")
STANDARD_SCHEMA_SHA256 = "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
AGENT_PLUGINS_RELEASE_COMMIT = "f24daf829224fd7fb685ae117c518ea27cbe7b9e"
AGENT_SKILLS_COMMIT = "217be548739f21d6008915c29aefe320ea1a90af"
ALLOWED_REMOTE_HOSTS = {
    "agent-plugins.org",
    "raw.githubusercontent.com",
}


class StandardError(ValueError):
    pass


def _strict_json(content: bytes, label: str):
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate key: %s" % key)
            value[key] = item
        return value

    try:
        return json.loads(
            content.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ValueError("non-finite constant: %s" % item)
            ),
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise StandardError("%s is not strict UTF-8 JSON" % label) from exc


def _regular_bytes(path: Path, label: str) -> bytes:
    try:
        before = path.lstat()
    except OSError as exc:
        raise StandardError("%s is unavailable: %s" % (label, exc)) from exc
    if (
        stat.S_ISLNK(before.st_mode)
        or not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
    ):
        raise StandardError("%s must be a single-link regular file" % label)
    try:
        content = path.read_bytes()
        after = path.lstat()
    except OSError as exc:
        raise StandardError("cannot read %s: %s" % (label, exc)) from exc
    identity = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, key) != getattr(after, key) for key in identity):
        raise StandardError("%s changed while being read" % label)
    return content


def _object(value: object, keys: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise StandardError("%s has an invalid closed shape" % label)
    return value


def verify_local(root: Path) -> dict:
    root = root.resolve()
    provenance_bytes = _regular_bytes(root / PROVENANCE, "standard provenance")
    provenance = _strict_json(provenance_bytes, "standard provenance")
    provenance = _object(
        provenance,
        {
            "format_version",
            "artifact",
            "agent_plugins",
            "agent_skills_baseline",
            "retrieval",
        },
        "standard provenance",
    )
    if provenance["format_version"] != "1.0":
        raise StandardError("standard provenance format_version is unsupported")
    artifact = _object(
        provenance["artifact"],
        {"path", "media_type", "bytes", "sha256"},
        "standard artifact",
    )
    if artifact["path"] != "references/standards/agent-plugins/1.0.0/plugin.schema.json":
        raise StandardError("standard artifact path is not canonical")
    if artifact["media_type"] != "application/schema+json":
        raise StandardError("standard artifact media type is invalid")
    schema_bytes = _regular_bytes(root / artifact["path"], "vendored plugin schema")
    schema_sha = hashlib.sha256(schema_bytes).hexdigest()
    if (
        artifact["bytes"] != len(schema_bytes)
        or not isinstance(artifact["sha256"], str)
        or not SHA256.fullmatch(artifact["sha256"])
        or artifact["sha256"] != schema_sha
        or schema_sha != STANDARD_SCHEMA_SHA256
    ):
        raise StandardError("vendored plugin schema does not match provenance")
    schema = _strict_json(schema_bytes, "vendored plugin schema")
    if (
        not isinstance(schema, dict)
        or schema.get("$id")
        != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise StandardError("vendored plugin schema identity is invalid")
    plugins = _object(
        provenance["agent_plugins"],
        {
            "specification_version",
            "status",
            "canonical_schema_url",
            "specification_url",
            "repository_url",
            "release_commit",
            "release_commit_url",
            "release_committed_at",
            "commit_pinned_schema_url",
            "commit_pinned_schema_sha256",
        },
        "Agent Plugins provenance",
    )
    if (
        plugins["specification_version"] != "1.0.0"
        or plugins["status"] != "Published"
        or plugins["canonical_schema_url"] != schema["$id"]
        or plugins["release_commit"] != AGENT_PLUGINS_RELEASE_COMMIT
        or plugins["commit_pinned_schema_sha256"] != schema_sha
    ):
        raise StandardError("Agent Plugins provenance identity is invalid")
    skills = _object(
        provenance["agent_skills_baseline"],
        {
            "specification_url",
            "repository_url",
            "commit",
            "commit_url",
            "commit_pinned_specification_url",
            "committed_at",
            "reason",
        },
        "Agent Skills provenance",
    )
    if skills["commit"] != AGENT_SKILLS_COMMIT:
        raise StandardError("Agent Skills baseline commit is invalid")
    return {
        "schema_bytes": schema_bytes,
        "schema_sha256": schema_sha,
        "plugins": plugins,
        "skills": skills,
    }


def _fetch(url: str) -> bytes:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_REMOTE_HOSTS:
        raise StandardError("standard URL is not an approved HTTPS origin: %s" % url)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "aaron-marketing-standard-drift-check/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            final = urllib.parse.urlsplit(response.geturl())
            if final.scheme != "https" or final.hostname not in ALLOWED_REMOTE_HOSTS:
                raise StandardError("standard URL redirected to an unapproved origin")
            content = response.read(MAX_REMOTE_BYTES + 1)
    except StandardError:
        raise
    except OSError as exc:
        raise StandardError("cannot fetch standard URL %s: %s" % (url, exc)) from exc
    if len(content) > MAX_REMOTE_BYTES:
        raise StandardError("standard response exceeds its byte limit")
    return content


def verify_online(local: dict) -> None:
    plugins = local["plugins"]
    expected_schema = local["schema_bytes"]
    for key in ("canonical_schema_url", "commit_pinned_schema_url"):
        if _fetch(plugins[key]) != expected_schema:
            raise StandardError(
                "%s drifted from the pinned 1.0.0 bytes; review and add a new "
                "versioned standard directory instead of overwriting the pin" % key
            )
    skills = local["skills"]
    commit = skills["commit"]
    pinned_url = (
        "https://raw.githubusercontent.com/agentskills/agentskills/%s/"
        "docs/specification.mdx" % commit
    )
    current_url = (
        "https://raw.githubusercontent.com/agentskills/agentskills/main/"
        "docs/specification.mdx"
    )
    pinned = _fetch(pinned_url)
    if not pinned:
        raise StandardError("Agent Skills pinned specification is empty")
    if _fetch(current_url) != pinned:
        raise StandardError(
            "Agent Skills specification changed after the pinned baseline; "
            "review the diff before cutting a release"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--online",
        action="store_true",
        help="Also compare canonical upstream bytes with the pinned baseline.",
    )
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        local = verify_local(args.root)
        if args.online:
            verify_online(local)
    except StandardError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    scope = "local + upstream" if args.online else "local"
    print(
        "Agent Plugins 1.0.0 / Agent Skills baseline clean (%s; schema %s)"
        % (scope, local["schema_sha256"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
