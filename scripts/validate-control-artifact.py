#!/usr/bin/env python3
"""Validate non-authoritative cross-discipline control artifacts.

The validator is intentionally Python-stdlib-only. It validates the closed
control-artifact union, exact canonical JSON bytes, bounded/pseudonymous
metadata, local reference digests, and the semantic bindings that JSON Schema
cannot express. It never writes project memory or a registry and never calls an
external system.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata


SCHEMA_VERSION = "1.0"
SCHEMA_REF = "references/control-artifact.schema.json"
AUTHORITY = "non-authoritative-operational-evidence"
KINDS = {
    "evidence-observation",
    "measurement-contract",
    "action-intent",
    "action-receipt",
    "cycle-retro",
}
EVIDENCE_TYPES = {"measured", "user-provided", "calculated", "estimated", "proxy"}
FIELD_STATES = {"observed", "unknown", "not-applicable", "conflict"}
FRESHNESS = {"current", "stale", "unknown"}
MISSING_REASONS = {
    "no-source", "not-observed", "stale-source", "conflicting-sources",
    "not-applicable", "withheld",
}
READINESS = {"ready", "needs-refresh", "ineligible", "unknown"}
COUNTERFACTUAL_TYPES = {
    "randomized-control", "holdout", "matched-control", "interrupted-series",
    "none-exploratory",
}
RECEIPT_STATUSES = {"succeeded", "failed", "partial", "unknown"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}$")
OPAQUE_REF = re.compile(r"^opaque:[A-Za-z0-9][A-Za-z0-9._:-]{0,504}$")
PROJECT_REF = re.compile(
    r"^(?!/)(?!.*//)(?!.*@)(?!.*(?:^|/)\.\.?(?:/|$))"
    r"[A-Za-z0-9](?:[A-Za-z0-9._/-]*[A-Za-z0-9._-])?$"
)
VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$")
OPERATION = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
RFC3339_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
RAW_PHONE_CANDIDATE = re.compile(
    r"(?<![A-Za-z0-9])\+?\d[\d ().-]{7,}\d(?![A-Za-z0-9])"
)
EMAIL_ADDRESS = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]{1,64}"
    r"@[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?"
    r"\.[A-Za-z]{2,63}(?![A-Za-z0-9.-])"
)
URL_OR_LOCATOR = re.compile(
    r"(?:[A-Za-z][A-Za-z0-9+.-]*://|\bwww\.|\bmailto:|\btel:|\bfile:)",
    re.IGNORECASE,
)
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")
IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
SENSITIVE_KEYS = {
    "email", "email_address", "phone", "phone_number", "name", "full_name",
    "first_name", "last_name", "address", "postal_address", "raw_identifier",
    "ip", "ip_address", "credential", "credentials",
    "password", "secret", "token", "api_key", "latitude", "longitude",
    "access_token", "refresh_token", "id_token", "auth_token", "oauth_token",
    "api_token", "authorization", "auth_header", "bearer", "bearer_token",
    "client_secret", "client_password", "private_key", "secret_key",
    "signing_key", "encryption_key", "webhook_secret", "session_token",
    "session_cookie", "connection_string", "aws_secret_access_key",
}
SENSITIVE_KEYS_COMPACT = {key.replace("_", "") for key in SENSITIVE_KEYS}
TEXT_FIELD_KEY = re.compile(
    r'''(?im)(?:^|[\s,{\[])(?:!![A-Za-z0-9_.:-]+\s+)?'''
    r'''(?:"([^"\r\n]{1,96})"|'([^'\r\n]{1,96})'|'''
    r'''([^\r\n"'=:,{}\[\]]{1,96}?))\s*[:=]'''
)
YAML_HEX_ESCAPE = re.compile(
    r"\\(?:x([0-9A-Fa-f]{2})|u([0-9A-Fa-f]{4})|U([0-9A-Fa-f]{8}))"
)
YAML_LINE_CONTINUATION = re.compile(r"\\\r?\n")
FRONTMATTER_VERSION = re.compile(
    r"(?m)^\s*(?:schema_version|version)\s*:\s*['\"]?"
    r"([A-Za-z0-9][A-Za-z0-9._+-]{0,63})['\"]?\s*$"
)
MAX_DOCUMENT_BYTES = 1_000_000
MAX_REFERENCE_BYTES = 10_000_000
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 10_000
MAX_INTEGER_DIGITS = 1_000
DIRFD_AVAILABLE = (
    os.name == "posix"
    and os.open in getattr(os, "supports_dir_fd", set())
    and os.stat in getattr(os, "supports_dir_fd", set())
)

TOP_FIELDS = {
    "$schema", "schema_version", "kind", "artifact_id", "created_at",
    "authoritative", "authority", "registry_effect",
    "external_mutation_authorized", "payload",
}
BINDING_FIELDS = {"ref", "sha256", "version"}


class ControlArtifactError(ValueError):
    """Raised for one fail-closed validation error."""


def canonical_bytes(value: object) -> bytes:
    """Return the sole on-disk encoding accepted for control JSON."""
    try:
        return (
            json.dumps(
                value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ControlArtifactError("document cannot be encoded as canonical JSON: %s" % exc) from exc


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate key: %s" % key)
        value[key] = item
    return value


def _bounded_int(lexeme: str) -> int:
    if len(lexeme.lstrip("-")) > MAX_INTEGER_DIGITS:
        raise ValueError("JSON integer exceeds digit limit")
    return int(lexeme)


def _bounded_float(lexeme: str) -> float:
    digits = sum(character.isdigit() for character in lexeme)
    if digits > MAX_INTEGER_DIGITS:
        raise ValueError("JSON number exceeds digit limit")
    number = float(lexeme)
    if not math.isfinite(number):
        raise ValueError("JSON number must be finite")
    return number


def strict_json_loads(raw: bytes, label: str = "artifact") -> object:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ControlArtifactError("%s must be UTF-8" % label) from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_int=_bounded_int,
            parse_float=_bounded_float,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ValueError("non-finite constant: %s" % item)
            ),
        )
    except (ValueError, RecursionError) as exc:
        raise ControlArtifactError("%s must be strict JSON: %s" % (label, exc)) from exc
    _bounded_walk(value, label)
    return value


def _bounded_walk(value: object, label: str) -> None:
    stack = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
            raise ControlArtifactError("%s exceeds bounded JSON depth/node limits" % label)
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
        elif isinstance(current, int) and not isinstance(current, bool):
            if current.bit_length() > 4096:
                raise ControlArtifactError("%s contains an oversized integer" % label)
        elif isinstance(current, float) and not math.isfinite(current):
            raise ControlArtifactError("%s contains a non-finite number" % label)


def _read_regular(path: Path, limit: int, label: str) -> bytes:
    if not DIRFD_AVAILABLE:
        raise ControlArtifactError(
            "%s validation requires POSIX dirfd no-follow support" % label
        )
    absolute = Path(os.path.abspath(path))
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptors: list[int] = []
    links: list[tuple[int, str, int, tuple[int, int]]] = []
    file_fd = None
    try:
        parent_fd = os.open(os.path.sep, directory_flags)
        descriptors.append(parent_fd)
        for component in absolute.parts[1:-1]:
            before = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise ControlArtifactError(
                    "%s path must not traverse a symlink or non-directory" % label
                )
            child_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            opened = os.fstat(child_fd)
            current = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
            identity = (opened.st_dev, opened.st_ino)
            if (
                    not stat.S_ISDIR(opened.st_mode)
                    or stat.S_ISLNK(current.st_mode)
                    or identity != (before.st_dev, before.st_ino)
                    or identity != (current.st_dev, current.st_ino)):
                os.close(child_fd)
                raise ControlArtifactError(
                    "%s directory changed during anchored traversal" % label
                )
            links.append((parent_fd, component, child_fd, identity))
            descriptors.append(child_fd)
            parent_fd = child_fd

        name = absolute.parts[-1]
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if (
                stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode)
                or before.st_nlink != 1):
            raise ControlArtifactError(
                "%s must be a stable single-link non-symlink regular file" % label
            )
        file_flags = (
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        file_fd = os.open(name, file_flags, dir_fd=parent_fd)
        opened = os.fstat(file_fd)
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if (
                not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or stat.S_ISLNK(current.st_mode)
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
                or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino)):
            raise ControlArtifactError(
                "%s changed during anchored open" % label
            )
        if opened.st_size > limit:
            raise ControlArtifactError("%s exceeds %d bytes" % (label, limit))
        with os.fdopen(file_fd, "rb") as handle:
            file_fd = None
            raw = handle.read(limit + 1)
            after = os.fstat(handle.fileno())
            current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            stable_fields = (
                "st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns",
            )
            if (
                    len(raw) > limit or len(raw) != opened.st_size
                    or any(
                        getattr(opened, field) != getattr(after, field)
                        for field in stable_fields
                    )
                    or (after.st_dev, after.st_ino) != (current.st_dev, current.st_ino)):
                raise ControlArtifactError("%s changed during anchored read" % label)
        for ancestor_fd, component, child_fd, identity in reversed(links):
            child = os.fstat(child_fd)
            current = os.stat(
                component, dir_fd=ancestor_fd, follow_symlinks=False,
            )
            if (
                    stat.S_ISLNK(current.st_mode)
                    or (child.st_dev, child.st_ino) != identity
                    or (current.st_dev, current.st_ino) != identity):
                raise ControlArtifactError(
                    "%s directory changed during anchored read" % label
                )
        return raw
    except ControlArtifactError:
        raise
    except OSError as exc:
        raise ControlArtifactError(
            "cannot securely read %s %s: %s" % (label, path, exc)
        ) from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _read_input(path: str) -> bytes:
    if path == "-":
        raw = sys.stdin.buffer.read(MAX_DOCUMENT_BYTES + 1)
        if len(raw) > MAX_DOCUMENT_BYTES:
            raise ControlArtifactError("artifact exceeds %d bytes" % MAX_DOCUMENT_BYTES)
        return raw
    supplied = Path(path)
    try:
        if stat.S_ISLNK(supplied.lstat().st_mode):
            raise ControlArtifactError("artifact must not be a symlink")
        resolved = supplied.resolve(strict=True)
    except ControlArtifactError:
        raise
    except OSError as exc:
        raise ControlArtifactError("cannot resolve artifact %s: %s" % (path, exc)) from exc
    return _read_regular(resolved, MAX_DOCUMENT_BYTES, "artifact")


def _timestamp(value: object, label: str, errors: list[str]) -> dt.datetime | None:
    if not isinstance(value, str) or not RFC3339_UTC.fullmatch(value):
        errors.append("%s must be a UTC RFC 3339 date-time ending in Z" % label)
        return None
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        errors.append("%s must be a real UTC date-time" % label)
        return None
    return parsed


def _exact_object(
    value: object, fields: set[str], label: str, errors: list[str],
) -> dict | None:
    if not isinstance(value, dict):
        errors.append("%s must be an object" % label)
        return None
    missing = sorted(fields - set(value))
    extra = sorted(set(value) - fields)
    if missing:
        errors.append("%s missing fields: %s" % (label, ", ".join(missing)))
    if extra:
        errors.append("%s has unknown fields: %s" % (label, ", ".join(extra)))
    return value


def _safe_id(value: object, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value) or "@" in value:
        errors.append("%s must be an opaque non-PII safe identifier" % label)
        return False
    return True


def _safe_field(value: object, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not SAFE_FIELD.fullmatch(value):
        errors.append("%s must be a safe field identifier" % label)
        return False
    return True


def _safe_ref(value: object, label: str, errors: list[str]) -> bool:
    """Validate a bare reference as an immutable opaque ID.

    A project-relative path is meaningful only together with its digest and
    embedded version, so callers must wrap it in ``artifact_binding``.
    """
    if not isinstance(value, str) or not OPAQUE_REF.fullmatch(value):
        if isinstance(value, str) and URL_OR_LOCATOR.search(value) is not None:
            errors.append("%s must not be a URL or external locator" % label)
        elif isinstance(value, str) and "/" in value:
            errors.append(
                "%s is a project-relative ref and requires an artifact-binding "
                "with ref, sha256, and version" % label
            )
        else:
            errors.append("%s must be an opaque immutable ID using opaque:<id>" % label)
        return False
    return True


def _binding_ref(value: object, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str):
        errors.append("%s must be an opaque ID or project-relative path" % label)
        return False
    if OPAQUE_REF.fullmatch(value) or PROJECT_REF.fullmatch(value):
        return True
    if (
            value.startswith(("/", "~")) or WINDOWS_ABSOLUTE.match(value)
            or "\\" in value or URL_OR_LOCATOR.search(value) is not None):
        errors.append("%s must not be an absolute path, URL, or external locator" % label)
    else:
        errors.append(
            "%s must be opaque:<id> or a safe project-relative artifact path" % label
        )
    return False


def _binding(value: object, label: str, errors: list[str]) -> dict | None:
    binding = _exact_object(value, BINDING_FIELDS, label, errors)
    if binding is None:
        return None
    _binding_ref(binding.get("ref"), label + ".ref", errors)
    digest = binding.get("sha256")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        errors.append("%s.sha256 must be a lowercase SHA-256 digest" % label)
    version = binding.get("version")
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        errors.append("%s.version must be a bounded safe version" % label)
    return binding


def _reference(
    value: object, label: str, errors: list[str], root: Path | None,
) -> object | None:
    """Validate one opaque ID or an exact local/opaque artifact binding."""
    if isinstance(value, dict):
        binding = _binding(value, label, errors)
        if binding is not None:
            try:
                _verify_binding_bytes(binding, root, label)
            except ControlArtifactError as exc:
                errors.append(str(exc))
        return binding
    _safe_ref(value, label, errors)
    return value


def _reference_key(value: object) -> tuple:
    if isinstance(value, dict):
        key = _binding_key(value) or (None, None, None)
        if all(isinstance(item, str) for item in key):
            return ("binding",) + key
        return "invalid-binding", type(value.get("ref")).__name__
    if isinstance(value, str):
        return "opaque", value
    return "invalid-reference", type(value).__name__


def _binding_key(value: object) -> tuple | None:
    if not isinstance(value, dict):
        return None
    return value.get("ref"), value.get("sha256"), value.get("version")


def _window(value: object, label: str, errors: list[str]) -> tuple | None:
    window = _exact_object(value, {"start_at", "end_at"}, label, errors)
    if window is None:
        return None
    start = _timestamp(window.get("start_at"), label + ".start_at", errors)
    end = _timestamp(window.get("end_at"), label + ".end_at", errors)
    if start is not None and end is not None and start > end:
        errors.append("%s start_at must not be later than end_at" % label)
    return start, end


def _array(value: object, label: str, errors: list[str], minimum: int, maximum: int) -> list:
    if not isinstance(value, list):
        errors.append("%s must be an array" % label)
        return []
    if len(value) < minimum or len(value) > maximum:
        errors.append("%s must contain between %d and %d items" % (label, minimum, maximum))
    return value


def _unique_scalars(values: list, label: str, errors: list[str]) -> None:
    try:
        if len(values) != len(set(values)):
            errors.append("%s must not contain duplicates" % label)
    except TypeError:
        errors.append("%s must contain scalar values" % label)


def _unique_references(values: list, label: str, errors: list[str]) -> None:
    keys = [_reference_key(value) for value in values]
    if len(keys) != len(set(keys)):
        errors.append("%s must not contain duplicate references" % label)


def _string_leaves(value: object, root_label: str = "artifact"):
    stack = [(value, root_label)]
    while stack:
        current, path = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                yield path + ".<key>", key
                stack.append((item, path + "." + str(key)))
        elif isinstance(current, list):
            for index, item in enumerate(current):
                stack.append((item, "%s[%d]" % (path, index)))
        elif isinstance(current, str):
            yield path, current


def _normalized_field_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        character for character in decomposed
        if (
            not unicodedata.category(character).startswith("M")
            and unicodedata.category(character) != "Cf"
        )
    )
    normalized = unicodedata.normalize("NFKC", normalized).strip()
    normalized = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", normalized)
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    return re.sub(r"[^A-Za-z0-9]+", "_", normalized).strip("_").lower()


def _is_sensitive_key(value: str) -> bool:
    normalized = _normalized_field_key(value)
    return (
        normalized in SENSITIVE_KEYS
        or normalized.replace("_", "") in SENSITIVE_KEYS_COMPACT
    )


def _field_key_requires_ascii(value: str) -> bool:
    """Fail closed on non-ASCII/format key spellings; values remain Unicode-safe."""
    return any(
        ord(character) > 127 or unicodedata.category(character) == "Cf"
        for character in unicodedata.normalize("NFKC", value)
    )


def _privacy_checks(
    record: object, errors: list[str], root_label: str = "artifact",
) -> None:
    """Apply the shared sensitive-field and direct-PII checks.

    URLs, domains, and ordinary search queries are not PII by category. Control
    reference fields remain locator-free through their structural validators;
    this content scanner intentionally does not reject arbitrary URL text.
    """
    for path, value in _string_leaves(record, root_label):
        normalized = unicodedata.normalize("NFKC", value)
        if path.endswith(".<key>"):
            if _is_sensitive_key(normalized) or _field_key_requires_ascii(normalized):
                errors.append("%s contains forbidden sensitive/PII key %s" % (path, value))
            continue
        if EMAIL_ADDRESS.search(normalized):
            errors.append("%s must not contain an email address" % path)
        if IPV4.fullmatch(normalized):
            octets = [int(part) for part in normalized.split(".")]
            if all(part <= 255 for part in octets):
                errors.append("%s must not contain an IP address" % path)
        if path.endswith(("created_at", "observed_at", "start_at", "end_at", "stop_at",
                          "read_at", "locked_at", "requested_at", "expires_at",
                          "attempted_at", "completed_at", "decided_at", "next_read_at")):
            continue
        for candidate in RAW_PHONE_CANDIDATE.finditer(normalized):
            digit_count = sum(character.isdigit() for character in candidate.group(0))
            if 10 <= digit_count <= 15:
                errors.append("%s must not contain a raw phone number" % path)
                break


def _privacy_checks_text(text: str, errors: list[str], label: str) -> None:
    """Scan versioned non-JSON local text without treating web data as PII."""
    if YAML_LINE_CONTINUATION.search(text):
        errors.append(
            "%s contains an unsupported escaped line continuation" % label
        )
    decomposed = unicodedata.normalize("NFKD", text)
    normalized = "".join(
        character for character in decomposed
        if not unicodedata.category(character).startswith("M")
    )
    normalized = unicodedata.normalize("NFKC", normalized)

    def decode_yaml_hex(match):
        token = next(value for value in match.groups() if value is not None)
        try:
            character = chr(int(token, 16))
        except (ValueError, OverflowError):
            return match.group(0)
        return character if character not in "\r\n\x00" else match.group(0)

    normalized = YAML_HEX_ESCAPE.sub(decode_yaml_hex, normalized)
    field_keys = (
        next(value for value in match.groups() if value is not None)
        for match in TEXT_FIELD_KEY.finditer(normalized)
    )
    if any(
            _is_sensitive_key(field_key) or _field_key_requires_ascii(field_key)
            for field_key in field_keys):
        errors.append("%s contains a forbidden sensitive/PII field" % label)
    if EMAIL_ADDRESS.search(normalized):
        errors.append("%s must not contain an email address" % label)
    for candidate in RAW_PHONE_CANDIDATE.finditer(normalized):
        digit_count = sum(character.isdigit() for character in candidate.group(0))
        if 10 <= digit_count <= 15:
            errors.append("%s must not contain a raw phone number" % label)
            break
    for token in re.findall(r"(?<![A-Za-z0-9])(?:\d{1,3}\.){3}\d{1,3}(?![A-Za-z0-9])", normalized):
        octets = [int(part) for part in token.split(".")]
        if all(part <= 255 for part in octets):
            errors.append("%s must not contain an IP address" % label)
            break


def _local_artifact_version(raw: bytes, label: str, errors: list[str]) -> str | None:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(
            "%s is not UTF-8 and cannot be inspected for sensitive fields; "
            "use an opaque immutable ID or a versioned text artifact" % label
        )
        return None

    stripped = text.lstrip()
    parsed = None
    if stripped.startswith(("{", "[")):
        try:
            parsed = strict_json_loads(raw, label)
        except ControlArtifactError as exc:
            errors.append(str(exc))
            return None
        _privacy_checks(parsed, errors, label)
        if not isinstance(parsed, dict):
            errors.append("%s JSON must be an object with version or schema_version" % label)
            return None
        versions = [
            parsed.get(field) for field in ("version", "schema_version")
            if parsed.get(field) is not None
        ]
        if not versions:
            errors.append("%s must embed version or schema_version" % label)
            return None
        if any(not isinstance(item, str) or not VERSION.fullmatch(item) for item in versions):
            errors.append("%s embedded version must be a bounded safe string" % label)
            return None
        if len(set(versions)) != 1:
            errors.append("%s has conflicting embedded versions" % label)
            return None
        return versions[0]

    _privacy_checks_text(text, errors, label)
    if not text.startswith("---\n"):
        errors.append(
            "%s non-JSON text must begin with YAML frontmatter containing version" % label
        )
        return None
    end = text.find("\n---", 4)
    if end < 0:
        errors.append("%s has unterminated YAML frontmatter" % label)
        return None
    versions = FRONTMATTER_VERSION.findall(text[4:end])
    if len(set(versions)) != 1:
        errors.append("%s must embed exactly one unambiguous version" % label)
        return None
    return versions[0]


def _project_reference_path(root: Path, reference: str, label: str) -> Path:
    if reference.startswith("opaque:"):
        raise ControlArtifactError("%s must be a project-relative control artifact reference" % label)
    parts = reference.split("/")
    if (
            reference.startswith(("/", "~")) or "\\" in reference
            or any(part in {"", ".", ".."} for part in parts)):
        raise ControlArtifactError("%s escapes the project root" % label)
    try:
        root_status = root.lstat()
    except OSError as exc:
        raise ControlArtifactError("cannot inspect project root: %s" % exc) from exc
    if stat.S_ISLNK(root_status.st_mode) or not stat.S_ISDIR(root_status.st_mode):
        raise ControlArtifactError("project root must be a real directory")
    return root.joinpath(*parts)


def _verify_binding_bytes(binding: dict, root: Path | None, label: str) -> bytes | None:
    reference = binding.get("ref")
    if not isinstance(reference, str) or OPAQUE_REF.fullmatch(reference):
        return None
    if not PROJECT_REF.fullmatch(reference):
        raise ControlArtifactError(
            "%s.ref must be an opaque ID or safe project-relative artifact path" % label
        )
    if root is None:
        raise ControlArtifactError(
            "%s is a local artifact binding and requires a project root" % label
        )
    path = _project_reference_path(root, reference, label + ".ref")
    raw = _read_regular(path, MAX_REFERENCE_BYTES, label + " reference")
    actual = sha256_bytes(raw)
    if actual != binding.get("sha256"):
        raise ControlArtifactError(
            "%s.sha256 digest does not match referenced bytes: expected %s, got %s"
            % (label, binding.get("sha256"), actual)
        )
    inspection_errors: list[str] = []
    embedded_version = _local_artifact_version(
        raw, label + " reference", inspection_errors,
    )
    if embedded_version is not None and embedded_version != binding.get("version"):
        inspection_errors.append(
            "%s.version %s does not match referenced embedded version %s"
            % (label, binding.get("version"), embedded_version)
        )
    if inspection_errors:
        raise ControlArtifactError("; ".join(inspection_errors[:8]))
    return raw


def _control_reference(
    binding: dict, root: Path | None, label: str, expected_kind: str,
) -> tuple[dict, bytes]:
    if root is None:
        raise ControlArtifactError("%s requires a project root" % label)
    raw = _verify_binding_bytes(binding, root, label)
    if raw is None:
        raise ControlArtifactError(
            "%s must bind a local project-relative control artifact" % label
        )
    record = strict_json_loads(raw, label + " reference")
    if raw != canonical_bytes(record):
        raise ControlArtifactError("%s reference is not canonical JSON" % label)
    linked_errors: list[str] = []
    _privacy_checks(record, linked_errors)
    _validate_record(record, linked_errors, root, resolve_linked=False)
    if linked_errors:
        raise ControlArtifactError(
            "%s reference is invalid: %s" % (label, "; ".join(linked_errors[:4]))
        )
    if record.get("kind") != expected_kind:
        raise ControlArtifactError("%s must reference kind %s" % (label, expected_kind))
    if binding.get("version") != record.get("schema_version"):
        raise ControlArtifactError("%s.version must equal the referenced schema_version" % label)
    return record, raw


def _validate_evidence(payload: object, errors: list[str], root: Path | None) -> None:
    fields = {"target", "observation_window", "fields", "readiness", "unresolved_conflicts"}
    value = _exact_object(payload, fields, "payload", errors)
    if value is None:
        return
    target = _binding(value.get("target"), "payload.target", errors)
    if target:
        try:
            _verify_binding_bytes(target, root, "payload.target")
        except ControlArtifactError as exc:
            errors.append(str(exc))
    _window(value.get("observation_window"), "payload.observation_window", errors)
    observations = _array(value.get("fields"), "payload.fields", errors, 1, 256)
    seen_fields: set[str] = set()
    conflict_groups: set[str] = set()
    states: list[tuple[str, str]] = []
    for index, item in enumerate(observations):
        label = "payload.fields[%d]" % index
        field = _exact_object(
            item,
            {"field_id", "state", "sources", "value_ref", "freshness", "missing_reason",
             "conflict_group"},
            label,
            errors,
        )
        if field is None:
            continue
        field_id = field.get("field_id")
        if _safe_field(field_id, label + ".field_id", errors):
            if field_id in seen_fields:
                errors.append("payload.fields has duplicate field_id %s" % field_id)
            seen_fields.add(field_id)
        state = field.get("state")
        if state not in FIELD_STATES:
            errors.append("%s.state is unsupported" % label)
        freshness = field.get("freshness")
        if freshness not in FRESHNESS:
            errors.append("%s.freshness is unsupported" % label)
        states.append((state, freshness))
        sources = _array(field.get("sources"), label + ".sources", errors, 0, 8)
        for source_index, source_value in enumerate(sources):
            source_label = "%s.sources[%d]" % (label, source_index)
            source = _exact_object(
                source_value, {"evidence_type", "ref", "observed_at", "window"},
                source_label, errors,
            )
            if source is None:
                continue
            if source.get("evidence_type") not in EVIDENCE_TYPES:
                errors.append("%s.evidence_type is unsupported" % source_label)
            _reference(source.get("ref"), source_label + ".ref", errors, root)
            _timestamp(source.get("observed_at"), source_label + ".observed_at", errors)
            if source.get("window") is not None:
                _window(source.get("window"), source_label + ".window", errors)
        value_ref = field.get("value_ref")
        if value_ref is not None:
            _reference(value_ref, label + ".value_ref", errors, root)
        missing_reason = field.get("missing_reason")
        if missing_reason is not None and missing_reason not in MISSING_REASONS:
            errors.append("%s.missing_reason is unsupported" % label)
        conflict_group = field.get("conflict_group")
        if conflict_group is not None:
            _safe_id(conflict_group, label + ".conflict_group", errors)
        if state == "observed":
            if not sources or value_ref is None or missing_reason is not None or conflict_group is not None:
                errors.append("%s observed state requires source/value and forbids missing/conflict markers" % label)
            if freshness not in {"current", "stale"}:
                errors.append("%s observed state cannot have unknown freshness" % label)
        elif state == "unknown":
            if value_ref is not None or missing_reason not in {
                    "no-source", "not-observed", "stale-source", "withheld"} or conflict_group is not None:
                errors.append("%s unknown state requires a missing reason and no value/conflict" % label)
            if freshness == "current":
                errors.append("%s unknown state cannot be current" % label)
        elif state == "not-applicable":
            if sources or value_ref is not None or freshness != "unknown" \
                    or missing_reason != "not-applicable" or conflict_group is not None:
                errors.append("%s not-applicable state must carry only the not-applicable reason" % label)
        elif state == "conflict":
            if len(sources) < 2 or value_ref is not None \
                    or missing_reason != "conflicting-sources" or conflict_group is None:
                errors.append("%s conflict state requires two sources and an unresolved conflict group" % label)
            if isinstance(conflict_group, str):
                conflict_groups.add(conflict_group)
    readiness = value.get("readiness")
    if readiness not in READINESS:
        errors.append("payload.readiness is unsupported")
    unresolved = _array(
        value.get("unresolved_conflicts"), "payload.unresolved_conflicts", errors, 0, 256,
    )
    for index, item in enumerate(unresolved):
        _safe_id(item, "payload.unresolved_conflicts[%d]" % index, errors)
    _unique_scalars(unresolved, "payload.unresolved_conflicts", errors)
    if set(item for item in unresolved if isinstance(item, str)) != conflict_groups:
        errors.append("payload.unresolved_conflicts must exactly list conflict field groups")
    if readiness == "ready" and any(
            state in {"unknown", "conflict"} or freshness != "current"
            for state, freshness in states if state != "not-applicable"):
        errors.append("ready evidence cannot contain unknown, conflict, or stale fields")
    if readiness == "needs-refresh" and not any(
            state in {"unknown", "conflict"} or freshness == "stale"
            for state, freshness in states):
        errors.append("needs-refresh requires a stale, unknown, or conflicting field")


def _validate_measurement(payload: object, errors: list[str], root: Path | None) -> None:
    fields = {
        "target", "contract_version", "population_ref", "scope_ref", "analysis_unit",
        "counterfactual_type", "control", "candidate", "primary_metric",
        "guardrail_metric_ids", "start_at", "stop_at", "read_at", "decision_rule_ref",
        "decision_owner_ref", "locked_at", "exploratory",
    }
    value = _exact_object(payload, fields, "payload", errors)
    if value is None:
        return
    for name in ("target", "candidate"):
        binding = _binding(value.get(name), "payload." + name, errors)
        if binding:
            try:
                _verify_binding_bytes(binding, root, "payload." + name)
            except ControlArtifactError as exc:
                errors.append(str(exc))
    control = value.get("control")
    if control is not None:
        binding = _binding(control, "payload.control", errors)
        if binding:
            try:
                _verify_binding_bytes(binding, root, "payload.control")
            except ControlArtifactError as exc:
                errors.append(str(exc))
    version = value.get("contract_version")
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        errors.append("payload.contract_version must be a safe version")
    for name in ("population_ref", "scope_ref", "decision_rule_ref", "decision_owner_ref"):
        _reference(value.get(name), "payload." + name, errors, root)
    _safe_id(value.get("analysis_unit"), "payload.analysis_unit", errors)
    counterfactual = value.get("counterfactual_type")
    if counterfactual not in COUNTERFACTUAL_TYPES:
        errors.append("payload.counterfactual_type is unsupported")
    exploratory = value.get("exploratory")
    if not isinstance(exploratory, bool):
        errors.append("payload.exploratory must be boolean")
    if counterfactual == "none-exploratory":
        if control is not None or exploratory is not True:
            errors.append("none-exploratory requires null control and exploratory true")
    elif control is None or exploratory is not False:
        errors.append("confirmatory counterfactual requires a control and exploratory false")
    metric = _exact_object(
        value.get("primary_metric"),
        {"metric_id", "unit", "direction", "truth_source_ref", "attribution_rule_ref",
         "conversion_lag_ref"},
        "payload.primary_metric", errors,
    )
    primary_id = None
    if metric is not None:
        primary_id = metric.get("metric_id")
        _safe_id(primary_id, "payload.primary_metric.metric_id", errors)
        _safe_id(metric.get("unit"), "payload.primary_metric.unit", errors)
        if metric.get("direction") not in {"increase", "decrease", "target-range"}:
            errors.append("payload.primary_metric.direction is unsupported")
        for name in ("truth_source_ref", "attribution_rule_ref", "conversion_lag_ref"):
            _reference(
                metric.get(name), "payload.primary_metric." + name, errors, root,
            )
    guardrails = _array(value.get("guardrail_metric_ids"), "payload.guardrail_metric_ids", errors, 0, 32)
    for index, item in enumerate(guardrails):
        _safe_id(item, "payload.guardrail_metric_ids[%d]" % index, errors)
    _unique_scalars(guardrails, "payload.guardrail_metric_ids", errors)
    if primary_id in guardrails:
        errors.append("primary metric cannot also be a guardrail metric")
    locked = _timestamp(value.get("locked_at"), "payload.locked_at", errors)
    start = _timestamp(value.get("start_at"), "payload.start_at", errors)
    stop = _timestamp(value.get("stop_at"), "payload.stop_at", errors)
    read = _timestamp(value.get("read_at"), "payload.read_at", errors)
    if all(item is not None for item in (locked, start, stop, read)) \
            and not (locked <= start < stop <= read):
        errors.append("measurement times must satisfy locked_at <= start_at < stop_at <= read_at")


def _validate_intent(payload: object, errors: list[str], root: Path | None) -> None:
    fields = {
        "operation", "target", "content", "audience_ref", "channel_ref",
        "constraint_refs", "safety_checks", "permission_ref", "permission_observed_at",
        "permission_effect", "requested_at", "expires_at", "single_use",
    }
    value = _exact_object(payload, fields, "payload", errors)
    if value is None:
        return
    operation = value.get("operation")
    if not isinstance(operation, str) or not OPERATION.fullmatch(operation):
        errors.append("payload.operation must be a lowercase operation slug")
    for name in ("target", "content"):
        binding_value = value.get(name)
        if binding_value is None and name == "content":
            continue
        binding = _binding(binding_value, "payload." + name, errors)
        if binding:
            try:
                _verify_binding_bytes(binding, root, "payload." + name)
            except ControlArtifactError as exc:
                errors.append(str(exc))
    for name in ("audience_ref", "channel_ref"):
        if value.get(name) is not None:
            _reference(value.get(name), "payload." + name, errors, root)
    constraints = _array(value.get("constraint_refs"), "payload.constraint_refs", errors, 0, 32)
    for index, item in enumerate(constraints):
        _reference(item, "payload.constraint_refs[%d]" % index, errors, root)
    _unique_references(constraints, "payload.constraint_refs", errors)
    checks = _array(value.get("safety_checks"), "payload.safety_checks", errors, 0, 32)
    check_refs = []
    for index, item in enumerate(checks):
        binding = _binding(item, "payload.safety_checks[%d]" % index, errors)
        if binding:
            check_refs.append(binding.get("ref"))
            try:
                _verify_binding_bytes(binding, root, "payload.safety_checks[%d]" % index)
            except ControlArtifactError as exc:
                errors.append(str(exc))
    _unique_scalars(check_refs, "payload.safety_checks refs", errors)
    permission_ref = value.get("permission_ref")
    permission_at = value.get("permission_observed_at")
    if permission_ref is not None:
        _reference(permission_ref, "payload.permission_ref", errors, root)
    parsed_permission = None
    if permission_at is not None:
        parsed_permission = _timestamp(permission_at, "payload.permission_observed_at", errors)
    if (permission_ref is None) != (permission_at is None):
        errors.append("permission_ref and permission_observed_at must be present together")
    if value.get("permission_effect") != "provenance-only":
        errors.append("action-intent permission_ref is provenance-only and cannot grant permission")
    if value.get("single_use") is not True:
        errors.append("action-intent must be single_use")
    requested = _timestamp(value.get("requested_at"), "payload.requested_at", errors)
    expires = _timestamp(value.get("expires_at"), "payload.expires_at", errors)
    if requested is not None and expires is not None and requested >= expires:
        errors.append("action-intent expires_at must be later than requested_at")
    if parsed_permission is not None and requested is not None and parsed_permission > requested:
        errors.append("permission provenance cannot be observed after the intent request")


def _validate_receipt(
    payload: object, errors: list[str], root: Path | None, resolve_linked: bool,
) -> None:
    fields = {
        "intent", "intent_id", "operation", "actual_target", "actual_content",
        "actual_audience_ref", "actual_channel_ref", "applied_constraint_refs",
        "status", "attempted_at", "completed_at", "provider_operation_ref",
        "evidence", "failure_code", "permission_effect",
    }
    value = _exact_object(payload, fields, "payload", errors)
    if value is None:
        return
    intent_binding = _binding(value.get("intent"), "payload.intent", errors)
    _safe_id(value.get("intent_id"), "payload.intent_id", errors)
    operation = value.get("operation")
    if not isinstance(operation, str) or not OPERATION.fullmatch(operation):
        errors.append("payload.operation must be a lowercase operation slug")
    actual_target = _binding(value.get("actual_target"), "payload.actual_target", errors)
    actual_content = None
    if value.get("actual_content") is not None:
        actual_content = _binding(value.get("actual_content"), "payload.actual_content", errors)
    for label, binding in (("payload.actual_target", actual_target),
                           ("payload.actual_content", actual_content)):
        if binding:
            try:
                _verify_binding_bytes(binding, root, label)
            except ControlArtifactError as exc:
                errors.append(str(exc))
    for name in ("actual_audience_ref", "actual_channel_ref"):
        if value.get(name) is not None:
            _reference(value.get(name), "payload." + name, errors, root)
    applied_constraints = _array(
        value.get("applied_constraint_refs"), "payload.applied_constraint_refs", errors, 0, 32,
    )
    for index, item in enumerate(applied_constraints):
        _reference(item, "payload.applied_constraint_refs[%d]" % index, errors, root)
    _unique_references(applied_constraints, "payload.applied_constraint_refs", errors)
    status = value.get("status")
    if status not in RECEIPT_STATUSES:
        errors.append("payload.status is unsupported")
    attempted = _timestamp(value.get("attempted_at"), "payload.attempted_at", errors)
    completed = None
    if value.get("completed_at") is not None:
        completed = _timestamp(value.get("completed_at"), "payload.completed_at", errors)
    if attempted is not None and completed is not None and completed < attempted:
        errors.append("receipt completed_at cannot precede attempted_at")
    provider_ref = value.get("provider_operation_ref")
    if provider_ref is not None:
        _reference(provider_ref, "payload.provider_operation_ref", errors, root)
    evidence = _array(value.get("evidence"), "payload.evidence", errors, 0, 32)
    evidence_refs = []
    for index, item in enumerate(evidence):
        binding = _binding(item, "payload.evidence[%d]" % index, errors)
        if binding:
            evidence_refs.append(binding.get("ref"))
            try:
                _verify_binding_bytes(binding, root, "payload.evidence[%d]" % index)
            except ControlArtifactError as exc:
                errors.append(str(exc))
    _unique_scalars(evidence_refs, "payload.evidence refs", errors)
    failure_code = value.get("failure_code")
    if failure_code is not None:
        _safe_id(failure_code, "payload.failure_code", errors)
    if value.get("permission_effect") != "provenance-only":
        errors.append("action-receipt cannot grant or transfer permission")
    if status == "succeeded" and (
            completed is None or provider_ref is None or not evidence or failure_code is not None):
        errors.append("succeeded receipt requires completion/provider/evidence and no failure_code")
    elif status == "failed" and (completed is None or failure_code is None):
        errors.append("failed receipt requires completed_at and failure_code")
    elif status == "partial" and (
            completed is None or provider_ref is None or not evidence or failure_code is None):
        errors.append("partial receipt requires completion/provider/evidence/failure_code")
    elif status == "unknown" and (completed is not None or failure_code is None):
        errors.append("unknown receipt requires null completed_at and a failure_code")
    if resolve_linked and intent_binding:
        try:
            intent, _ = _control_reference(
                intent_binding, root, "payload.intent", "action-intent",
            )
            if value.get("intent_id") != intent.get("artifact_id"):
                errors.append("receipt intent_id does not match referenced action-intent")
            intent_payload = intent.get("payload", {})
            if operation != intent_payload.get("operation"):
                errors.append("receipt operation does not match referenced action-intent")
            if _binding_key(actual_target) != _binding_key(intent_payload.get("target")):
                errors.append("receipt actual_target does not match referenced action-intent")
            if _binding_key(actual_content) != _binding_key(intent_payload.get("content")):
                errors.append("receipt actual_content does not match referenced action-intent")
            if value.get("actual_audience_ref") != intent_payload.get("audience_ref"):
                errors.append("receipt actual_audience_ref does not match referenced action-intent")
            if value.get("actual_channel_ref") != intent_payload.get("channel_ref"):
                errors.append("receipt actual_channel_ref does not match referenced action-intent")
            if applied_constraints != intent_payload.get("constraint_refs"):
                errors.append("receipt applied constraints do not match referenced action-intent")
            requested = _timestamp(intent_payload.get("requested_at"), "referenced intent requested_at", errors)
            expires = _timestamp(intent_payload.get("expires_at"), "referenced intent expires_at", errors)
            if attempted is not None and requested is not None and attempted < requested:
                errors.append("receipt attempted_at precedes the referenced intent")
            if attempted is not None and expires is not None and attempted > expires:
                errors.append("receipt attempted_at is outside the intent scope window")
        except ControlArtifactError as exc:
            errors.append(str(exc))


def _validate_retro(
    payload: object, errors: list[str], root: Path | None, resolve_linked: bool,
) -> None:
    fields = {
        "measurement_contract", "measurement_contract_id", "current_head", "head_state",
        "evidence", "decision_code", "decision_taxonomy_ref", "decision_owner_ref",
        "decided_at", "limitations",
        "hypothesis_ref", "hypothesis_evidence_weight", "next_read_at",
    }
    value = _exact_object(payload, fields, "payload", errors)
    if value is None:
        return
    measurement_binding = _binding(
        value.get("measurement_contract"), "payload.measurement_contract", errors,
    )
    _safe_id(value.get("measurement_contract_id"), "payload.measurement_contract_id", errors)
    current_head = _binding(value.get("current_head"), "payload.current_head", errors)
    if current_head:
        try:
            _verify_binding_bytes(current_head, root, "payload.current_head")
        except ControlArtifactError as exc:
            errors.append(str(exc))
    state = _exact_object(
        value.get("head_state"), {"is_current", "fork_count", "selected_ancestry_ref"},
        "payload.head_state", errors,
    )
    if state is not None:
        if state.get("is_current") is not True:
            errors.append("cycle retro requires is_current true")
        if state.get("fork_count") != 0 or isinstance(state.get("fork_count"), bool):
            errors.append("cycle retro requires a non-forked current head")
        _reference(
            state.get("selected_ancestry_ref"),
            "payload.head_state.selected_ancestry_ref", errors, root,
        )
    evidence = _array(value.get("evidence"), "payload.evidence", errors, 1, 64)
    evidence_refs = []
    for index, item in enumerate(evidence):
        binding = _binding(item, "payload.evidence[%d]" % index, errors)
        if binding:
            evidence_refs.append(binding.get("ref"))
            try:
                _verify_binding_bytes(binding, root, "payload.evidence[%d]" % index)
            except ControlArtifactError as exc:
                errors.append(str(exc))
    _unique_scalars(evidence_refs, "payload.evidence refs", errors)
    _safe_id(value.get("decision_code"), "payload.decision_code", errors)
    _reference(
        value.get("decision_taxonomy_ref"), "payload.decision_taxonomy_ref", errors, root,
    )
    _reference(
        value.get("decision_owner_ref"), "payload.decision_owner_ref", errors, root,
    )
    decided = _timestamp(value.get("decided_at"), "payload.decided_at", errors)
    limitations = _array(value.get("limitations"), "payload.limitations", errors, 0, 32)
    for index, item in enumerate(limitations):
        _safe_id(item, "payload.limitations[%d]" % index, errors)
    _unique_scalars(limitations, "payload.limitations", errors)
    if value.get("hypothesis_ref") is not None:
        _reference(value.get("hypothesis_ref"), "payload.hypothesis_ref", errors, root)
    if value.get("hypothesis_evidence_weight") != 0 \
            or isinstance(value.get("hypothesis_evidence_weight"), bool):
        errors.append("retro hypothesis_evidence_weight must be exactly zero")
    next_read = None
    if value.get("next_read_at") is not None:
        next_read = _timestamp(value.get("next_read_at"), "payload.next_read_at", errors)
    if next_read is not None and decided is not None and next_read <= decided:
        errors.append("retro next_read_at must be later than decided_at")
    if resolve_linked and measurement_binding:
        try:
            measurement, _ = _control_reference(
                measurement_binding, root, "payload.measurement_contract", "measurement-contract",
            )
            if value.get("measurement_contract_id") != measurement.get("artifact_id"):
                errors.append("retro measurement_contract_id does not match referenced contract")
            measurement_payload = measurement.get("payload", {})
            if _binding_key(current_head) != _binding_key(measurement_payload.get("target")):
                errors.append("retro current_head must equal the measurement target binding")
            if value.get("decision_owner_ref") != measurement_payload.get("decision_owner_ref"):
                errors.append("retro decision owner must match the measurement contract")
            read_at = _timestamp(
                measurement_payload.get("read_at"), "referenced measurement read_at", errors,
            )
            if decided is not None and read_at is not None and decided < read_at:
                errors.append("retro cannot decide before the preregistered read_at")
        except ControlArtifactError as exc:
            errors.append(str(exc))


def _validate_record(
    record: object, errors: list[str], root: Path | None, resolve_linked: bool = True,
) -> None:
    value = _exact_object(record, TOP_FIELDS, "artifact", errors)
    if value is None:
        return
    if value.get("$schema") != SCHEMA_REF:
        errors.append("$schema must be %s" % SCHEMA_REF)
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be %s" % SCHEMA_VERSION)
    kind = value.get("kind")
    if kind not in KINDS:
        errors.append("kind is unsupported; no authorization/control kind exists")
    _safe_id(value.get("artifact_id"), "artifact_id", errors)
    created = _timestamp(value.get("created_at"), "created_at", errors)
    if value.get("authoritative") is not False:
        errors.append("control artifacts must be non-authoritative")
    if value.get("authority") != AUTHORITY:
        errors.append("authority must be %s" % AUTHORITY)
    if value.get("registry_effect") is not False:
        errors.append("control artifacts cannot write or mutate a registry")
    if value.get("external_mutation_authorized") is not False:
        errors.append("control artifacts cannot authorize an external mutation")
    if kind == "evidence-observation":
        _validate_evidence(value.get("payload"), errors, root)
    elif kind == "measurement-contract":
        _validate_measurement(value.get("payload"), errors, root)
    elif kind == "action-intent":
        _validate_intent(value.get("payload"), errors, root)
    elif kind == "action-receipt":
        _validate_receipt(value.get("payload"), errors, root, resolve_linked)
    elif kind == "cycle-retro":
        _validate_retro(value.get("payload"), errors, root, resolve_linked)
    payload = value.get("payload")
    if created is not None and isinstance(payload, dict):
        comparison = None
        for field in ("completed_at", "attempted_at", "decided_at", "requested_at", "locked_at"):
            if payload.get(field) is not None:
                comparison = _timestamp(payload.get(field), "payload." + field, [])
                if comparison is not None:
                    break
        if comparison is not None and created < comparison:
            errors.append("created_at cannot precede the artifact's defining event")


def validate(path: str, project_root: str | os.PathLike | None = None):
    """Return ``(record, errors, canonical_sha256)`` for one artifact."""
    errors: list[str] = []
    record = None
    digest = None
    try:
        raw = _read_input(path)
        record = strict_json_loads(raw)
        canonical = canonical_bytes(record)
        digest = sha256_bytes(canonical)
        if raw != canonical:
            errors.append("artifact bytes are not canonical JSON (sorted keys, 2-space indent, final newline)")
        root = Path(project_root).resolve(strict=True) if project_root is not None else None
        _privacy_checks(record, errors)
        _validate_record(record, errors, root)
    except (ControlArtifactError, OSError) as exc:
        errors.append(str(exc))
    return record, sorted(set(errors)), digest


def markdown_code_span(value: str) -> str:
    """Render a CommonMark code span that cannot break surrounding markup.

    A longer backtick fence wraps any embedded backticks. Leading or trailing
    backticks or spaces get one space of padding so the fence stays intact.
    Line breaks are escaped so they cannot terminate the span or inject a
    heading or list marker on a following line.
    """
    if not isinstance(value, str):
        raise TypeError("markdown code span value must be a string")
    escaped = (
        value.replace("\r\n", "\n")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    longest = 0
    run = 0
    for char in escaped:
        if char == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    fence = "`" * (longest + 1)
    if not escaped or escaped[0] in " `" or escaped[-1] in " `":
        return "%s %s %s" % (fence, escaped, fence)
    return "%s%s%s" % (fence, escaped, fence)


def project_artifacts(
    paths: list[str], project_root: str | os.PathLike,
) -> tuple[str | None, list[str]]:
    """Render a deterministic, read-only Markdown/YAML projection to a string."""
    errors: list[str] = []
    try:
        lexical_root = Path(os.path.abspath(project_root))
        root = Path(project_root).resolve(strict=True)
    except OSError as exc:
        return None, ["cannot resolve project root: %s" % exc]
    if not paths:
        return None, ["project requires at least one control artifact"]
    sources = []
    seen_ids: set[str] = set()
    for path_text in paths:
        if path_text == "-":
            errors.append("project does not accept stdin because every source needs a stable ref")
            continue
        try:
            supplied_path = Path(path_text)
            lexical_path = Path(os.path.abspath(supplied_path))
            try:
                relative_parts = lexical_path.relative_to(lexical_root).parts
            except ValueError:
                errors.append("projection source escapes the project root: %s" % path_text)
                continue
            cursor = lexical_root
            traverses_symlink = False
            for part in relative_parts:
                cursor = cursor / part
                metadata = cursor.lstat()
                if stat.S_ISLNK(metadata.st_mode):
                    traverses_symlink = True
                    break
            if traverses_symlink:
                errors.append("projection source must not traverse a symlink: %s" % path_text)
                continue
            path = supplied_path.resolve(strict=True)
            if path != root and root not in path.parents:
                errors.append("projection source escapes the project root: %s" % path_text)
                continue
            source_ref = path.relative_to(root).as_posix()
        except (OSError, ValueError) as exc:
            errors.append("cannot resolve projection source %s: %s" % (path_text, exc))
            continue
        # Filesystem names do not inherit the artifact's reference validation.
        # Apply the project_ref contract before using a path in either YAML or
        # Markdown; in particular, no quotes, backticks, or line breaks survive.
        if len(source_ref) > 512 or not PROJECT_REF.fullmatch(source_ref):
            errors.append(
                "projection source ref must be a safe project-relative artifact "
                "path of at most 512 characters"
            )
            continue
        record, validation_errors, digest = validate(str(path), root)
        if validation_errors:
            errors.extend("%s: %s" % (source_ref, item) for item in validation_errors)
            continue
        artifact_id = record["artifact_id"]
        if artifact_id in seen_ids:
            errors.append("duplicate artifact_id in projection inputs: %s" % artifact_id)
            continue
        seen_ids.add(artifact_id)
        sources.append({
            "artifact_id": artifact_id,
            "kind": record["kind"],
            "ref": source_ref,
            "sha256": digest,
            "record": record,
        })
    if errors:
        return None, sorted(set(errors))
    sources.sort(key=lambda item: (item["artifact_id"], item["ref"]))
    source_manifest = [
        {
            "artifact_id": item["artifact_id"],
            "kind": item["kind"],
            "ref": item["ref"],
            "sha256": item["sha256"],
        }
        for item in sources
    ]
    manifest_sha = sha256_bytes(canonical_bytes(source_manifest))
    heads_by_key = {}
    for item in sources:
        if item["kind"] != "cycle-retro":
            continue
        binding = item["record"]["payload"]["current_head"]
        heads_by_key[_binding_key(binding)] = binding
    heads = sorted(
        heads_by_key.values(), key=lambda item: (item["ref"], item["version"], item["sha256"]),
    )
    lines = [
        "---",
        'view: "control-artifact-projection"',
        'schema_version: "1.0"',
        "authoritative: false",
        "source_count: %d" % len(sources),
        "sources_sha256: %s" % json.dumps(manifest_sha),
        "source_refs:",
    ]
    for item in source_manifest:
        lines.extend([
            "  - ref: %s" % json.dumps(item["ref"]),
            "    sha256: %s" % json.dumps(item["sha256"]),
            "    artifact_id: %s" % json.dumps(item["artifact_id"]),
            "    kind: %s" % json.dumps(item["kind"]),
        ])
    if heads:
        lines.append("current_heads:")
        for head in heads:
            lines.extend([
                "  - ref: %s" % json.dumps(head["ref"]),
                "    sha256: %s" % json.dumps(head["sha256"]),
                "    version: %s" % json.dumps(head["version"]),
            ])
    else:
        lines.append("current_heads: []")
    lines.extend([
        "---",
        "",
        "# Control artifact projection",
        "",
        "This is a deterministic read model. It is not canonical state, permission, or proof of an external action.",
        "",
        "## Sources",
        "",
    ])
    for item in source_manifest:
        lines.append(
            "- %s — %s; %s; %s"
            % (
                markdown_code_span(item["artifact_id"]),
                markdown_code_span(item["kind"]),
                markdown_code_span(item["ref"]),
                markdown_code_span("sha256:" + item["sha256"]),
            )
        )
    lines.extend(["", "## Current heads", ""])
    if heads:
        for head in heads:
            lines.append(
                "- %s at version %s; %s"
                % (
                    markdown_code_span(head["ref"]),
                    markdown_code_span(head["version"]),
                    markdown_code_span("sha256:" + head["sha256"]),
                )
            )
    else:
        lines.append("- None declared by a validated `cycle-retro` input.")
    lines.extend([
        "",
        "Changing this projection cannot mutate or supersede any source artifact.",
        "",
    ])
    return "\n".join(lines), []


def _validate_command(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", help="canonical control artifact JSON or - for stdin")
    parser.add_argument(
        "--project-root",
        help="root used to resolve and hash-check project-relative bindings",
    )
    parser.add_argument(
        "--print-normalized",
        action="store_true",
        help="print canonical JSON after successful validation",
    )
    args = parser.parse_args(argv)
    record, errors, digest = validate(args.artifact, args.project_root)
    if errors:
        for error in errors:
            print("ERROR: %s" % error, file=sys.stderr)
        return 1
    if args.print_normalized:
        sys.stdout.buffer.write(canonical_bytes(record))
    else:
        print("valid %s sha256:%s" % (record["kind"], digest))
    return 0


def _project_command(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Render validated control artifacts as a read-only Markdown/YAML projection."
    )
    parser.add_argument("artifacts", nargs="+", help="canonical control artifact JSON files")
    parser.add_argument(
        "--project-root", required=True,
        help="root used for stable source refs and project-relative digest verification",
    )
    args = parser.parse_args(argv)
    output, errors = project_artifacts(args.artifacts, args.project_root)
    if errors:
        for error in errors:
            print("ERROR: %s" % error, file=sys.stderr)
        return 1
    sys.stdout.write(output)
    return 0


def main(argv=None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "project":
        return _project_command(arguments[1:])
    if arguments and arguments[0] == "validate":
        arguments = arguments[1:]
    return _validate_command(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
