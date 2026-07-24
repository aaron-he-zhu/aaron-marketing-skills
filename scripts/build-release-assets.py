#!/usr/bin/env python3
"""Build or verify deterministic, commit-bound profile release assets."""
from __future__ import annotations

import argparse
from io import BytesIO
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = "aaron-marketing-skills"
PROFILES = ("lite", "pro", "governed")
LEDGER_NAME = "release-assets.json"
CHECKSUM_NAME = "SHA256SUMS"
LEDGER_SCHEMA_VERSION = "1.0"
MAX_GIT_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_RELEASE_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_RELEASE_TAR_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 2_000
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
COMMIT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA256 = re.compile(r"[0-9a-f]{64}")


class ReleaseAssetError(ValueError):
    pass


def canonical_json(value):
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=False,
                allow_nan=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ReleaseAssetError("cannot encode release asset JSON: %s" % exc) from exc


def _sha256(content):
    return hashlib.sha256(content).hexdigest()


def _validate_identity(repository, commit, version):
    if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
        raise ReleaseAssetError(
            "source repository must be an owner/repository slug"
        )
    if not isinstance(commit, str) or not COMMIT_ID.fullmatch(commit):
        raise ReleaseAssetError(
            "source commit must be an exact lowercase 40- or 64-hex object ID"
        )
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise ReleaseAssetError("version must be an exact X.Y.Z semantic version")


def _checked_regular_bytes(path, label, *, max_bytes=None):
    try:
        before = path.lstat()
    except OSError as exc:
        raise ReleaseAssetError("%s is unavailable: %s" % (label, exc)) from exc
    if (
        stat.S_ISLNK(before.st_mode)
        or not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
    ):
        raise ReleaseAssetError(
            "%s must be a single-link regular file" % label
        )
    if max_bytes is not None and before.st_size > max_bytes:
        raise ReleaseAssetError(
            "%s is %d bytes (limit %d)" % (label, before.st_size, max_bytes)
        )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ReleaseAssetError("cannot safely open %s: %s" % (label, exc)) from exc
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (opened.st_dev, opened.st_ino, opened.st_size)
            != (before.st_dev, before.st_ino, before.st_size)
        ):
            raise ReleaseAssetError("%s changed or is unsafe while opening" % label)
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            content = handle.read()
            after = os.fstat(handle.fileno())
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    stable = (
        "st_dev",
        "st_ino",
        "st_nlink",
        "st_size",
        "st_mtime_ns",
        "st_ctime_ns",
    )
    if any(getattr(opened, key) != getattr(after, key) for key in stable):
        raise ReleaseAssetError("%s changed while reading" % label)
    return content


def _validate_repo(path):
    try:
        status = path.lstat()
    except OSError as exc:
        raise ReleaseAssetError("source repo is unavailable: %s" % exc) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ReleaseAssetError("source repo must be a real directory")
    try:
        return path.resolve(strict=True)
    except OSError as exc:
        raise ReleaseAssetError("cannot resolve source repo: %s" % exc) from exc


def _run(command, *, cwd=None, stdout=None, env=None):
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            stdout=stdout if stdout is not None else subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=stdout is None,
            env=env,
            check=False,
        )
    except OSError as exc:
        raise ReleaseAssetError(
            "cannot run %s: %s" % (command[0], exc)
        ) from exc
    if completed.returncode:
        stderr = (
            completed.stderr.decode("utf-8", "replace")
            if isinstance(completed.stderr, bytes)
            else completed.stderr
        )
        raise ReleaseAssetError(
            "%s failed: %s" % (" ".join(command), (stderr or "").strip())
        )
    return completed


def _validate_member_name(name, expected_root):
    if not isinstance(name, str) or not name or "\x00" in name or "\\" in name:
        raise ReleaseAssetError("archive contains an invalid member name")
    try:
        name.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ReleaseAssetError(
            "archive member name is not canonical UTF-8 text"
        ) from exc
    normalized = name[:-1] if name.endswith("/") else name
    path = PurePosixPath(normalized)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.parts[0] != expected_root
        or path.as_posix() != normalized
    ):
        raise ReleaseAssetError("archive path escapes its fixed root: %s" % name)
    return path


def _mkdir_chain(root, relative_parts):
    current = root
    for part in relative_parts:
        current = current / part
        try:
            status = current.lstat()
        except FileNotFoundError:
            current.mkdir(mode=0o755)
            continue
        except OSError as exc:
            raise ReleaseAssetError(
                "cannot inspect extraction directory %s: %s" % (current, exc)
            ) from exc
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
            raise ReleaseAssetError(
                "archive extraction parent is not a real directory: %s" % current
            )
    return current


def _validate_ustar_stream(content):
    if not content or len(content) % 512:
        raise ReleaseAssetError("release tar stream is not 512-byte aligned")
    offset = 0
    members = 0
    while offset + 512 <= len(content):
        header = content[offset : offset + 512]
        if header == b"\0" * 512:
            if (
                offset + 1024 > len(content)
                or content[offset + 512 : offset + 1024] != b"\0" * 512
                or any(content[offset:])
            ):
                raise ReleaseAssetError(
                    "release tar end markers are not canonical"
                )
            return
        if header[257:263] != b"ustar\0" or header[263:265] != b"00":
            raise ReleaseAssetError("release tar header is not POSIX ustar")
        if header[156:157] not in {b"\0", b"0", b"5"}:
            raise ReleaseAssetError(
                "release tar contains an extension, link, or special header"
            )
        stored_checksum = header[148:156].rstrip(b"\0 ").strip()
        try:
            checksum = int(stored_checksum or b"0", 8)
        except ValueError as exc:
            raise ReleaseAssetError("release tar checksum field is invalid") from exc
        checksum_header = header[:148] + b" " * 8 + header[156:]
        if sum(checksum_header) != checksum:
            raise ReleaseAssetError("release tar header checksum is invalid")
        size_field = header[124:136].rstrip(b"\0 ").strip()
        try:
            size = int(size_field or b"0", 8)
        except ValueError as exc:
            raise ReleaseAssetError("release tar size field is invalid") from exc
        if size < 0:
            raise ReleaseAssetError("release tar member size is invalid")
        offset += 512 + ((size + 511) // 512) * 512
        if offset > len(content):
            raise ReleaseAssetError("release tar member exceeds the stream")
        members += 1
        if members > MAX_ARCHIVE_MEMBERS:
            raise ReleaseAssetError("release tar member count exceeds its limit")
    raise ReleaseAssetError("release tar has no canonical end markers")


def _extract_tar_bytes(
    content,
    destination,
    expected_root,
    *,
    require_release_metadata,
):
    if destination.exists() or destination.is_symlink():
        raise ReleaseAssetError("archive extraction destination must not exist")
    if require_release_metadata:
        _validate_ustar_stream(content)
    destination.mkdir(mode=0o700)
    seen = set()
    observed_names = []
    try:
        archive = tarfile.open(fileobj=BytesIO(content), mode="r:")
    except (OSError, tarfile.TarError) as exc:
        raise ReleaseAssetError("archive is not a valid tar stream: %s" % exc) from exc
    with archive:
        members = archive.getmembers()
        if not members or len(members) > MAX_ARCHIVE_MEMBERS:
            raise ReleaseAssetError("archive member count is invalid")
        for member in members:
            path = _validate_member_name(member.name, expected_root)
            normalized = path.as_posix()
            if normalized in seen:
                raise ReleaseAssetError(
                    "archive contains a duplicate member: %s" % normalized
                )
            seen.add(normalized)
            observed_names.append(normalized)
            if member.issym() or member.islnk():
                raise ReleaseAssetError(
                    "archive links are forbidden: %s" % normalized
                )
            if not (member.isdir() or member.isfile()):
                raise ReleaseAssetError(
                    "archive special files are forbidden: %s" % normalized
                )
            expected_mode = (
                0o755
                if member.isdir() or stat.S_IMODE(member.mode) & 0o111
                else 0o644
            )
            if require_release_metadata:
                if member.isdir() and stat.S_IMODE(member.mode) != 0o755:
                    raise ReleaseAssetError(
                        "archive directory mode is not canonical: %s" % normalized
                    )
                if member.isfile() and stat.S_IMODE(member.mode) not in {0o644, 0o755}:
                    raise ReleaseAssetError(
                        "archive file mode is not canonical: %s" % normalized
                    )
            if require_release_metadata:
                if (
                    member.mtime != 0
                    or member.uid != 0
                    or member.gid != 0
                    or member.uname != ""
                    or member.gname != ""
                    or member.pax_headers
                ):
                    raise ReleaseAssetError(
                        "archive metadata is not canonical: %s" % normalized
                    )
            relative_parts = path.parts[1:]
            target = destination / expected_root
            if not relative_parts:
                if not member.isdir():
                    raise ReleaseAssetError("archive fixed root must be a directory")
                target.mkdir(mode=0o755)
                continue
            parent = _mkdir_chain(target, relative_parts[:-1])
            target = parent / relative_parts[-1]
            if member.isdir():
                if not target.exists():
                    target.mkdir(mode=0o755)
                os.chmod(target, 0o755)
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                raise ReleaseAssetError(
                    "cannot read archive member: %s" % normalized
                )
            data = extracted.read()
            if len(data) != member.size:
                raise ReleaseAssetError(
                    "archive member size changed: %s" % normalized
                )
            flags = (
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0)
            )
            try:
                descriptor = os.open(target, flags, expected_mode)
                with os.fdopen(descriptor, "wb", closefd=True) as handle:
                    handle.write(data)
                os.chmod(target, expected_mode)
            except OSError as exc:
                raise ReleaseAssetError(
                    "cannot safely extract %s: %s" % (normalized, exc)
                ) from exc
    if expected_root not in seen:
        raise ReleaseAssetError("archive does not contain its fixed root directory")
    if require_release_metadata:
        expected_order = [expected_root] + sorted(
            (name for name in seen if name != expected_root),
            key=lambda name: name.encode("utf-8"),
        )
        if observed_names != expected_order:
            raise ReleaseAssetError("archive members are not in canonical path order")
    return destination / expected_root


def _export_commit(source_repo, commit, destination):
    git_environment = dict(os.environ)
    git_environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    resolved = _run(
        ["git", "-C", str(source_repo), "rev-parse", "--verify", commit + "^{commit}"],
        env=git_environment,
    ).stdout.strip()
    if resolved != commit:
        raise ReleaseAssetError(
            "source commit is not the exact resolved commit: %s" % resolved
        )
    archive_path = destination.parent / "source.tar"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(archive_path, flags, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            _run(
                [
                    "git",
                    "-C",
                    str(source_repo),
                    "archive",
                    "--format=tar",
                    "--prefix=source/",
                    commit,
                ],
                stdout=handle,
                env=git_environment,
            )
    except OSError as exc:
        raise ReleaseAssetError("cannot create private git archive: %s" % exc) from exc
    content = _checked_regular_bytes(
        archive_path, "private git archive", max_bytes=MAX_GIT_ARCHIVE_BYTES
    )
    return _extract_tar_bytes(
        content,
        destination,
        "source",
        require_release_metadata=False,
    )


def _source_version(exported_source, expected_version):
    path = exported_source / "references" / "system-catalog.json"
    try:
        catalog = json.loads(
            _checked_regular_bytes(path, "exported system catalog").decode("utf-8")
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReleaseAssetError(
            "exported system catalog is not valid UTF-8 JSON: %s" % exc
        ) from exc
    if not isinstance(catalog, dict):
        raise ReleaseAssetError("exported system catalog must be an object")
    version = catalog.get("bundle_version")
    if (
        version != expected_version
        or catalog.get("architecture_version") != expected_version
    ):
        raise ReleaseAssetError(
            "exported source bundle/architecture version does not match %s"
            % expected_version
        )
    return version


def _builder(exported_source):
    path = exported_source / "scripts" / "build-distribution.py"
    _checked_regular_bytes(path, "exported distribution builder")
    return path


def _build_profile(
    exported_source,
    profile,
    destination,
    repository,
    commit,
):
    command = [
        sys.executable,
        str(_builder(exported_source)),
        "--output",
        str(destination),
        "--plugin",
        "--profile",
        profile,
        "--source-repository",
        repository,
        "--source-commit",
        commit,
    ]
    _run(command, cwd=exported_source)
    _verify_distribution(
        exported_source, destination, profile, repository, commit
    )


def _verify_distribution(
    exported_source,
    distribution,
    profile,
    repository,
    commit,
):
    _run(
        [
            sys.executable,
            str(_builder(exported_source)),
            "--verify-manifest",
            str(distribution),
            "--profile",
            profile,
            "--source-repository",
            repository,
            "--source-commit",
            commit,
        ],
        cwd=exported_source,
    )


def _distribution_manifest(distribution):
    path = distribution / "distribution-manifest.json"
    content = _checked_regular_bytes(path, "distribution manifest")
    try:
        manifest = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReleaseAssetError(
            "distribution manifest is not valid UTF-8 JSON: %s" % exc
        ) from exc
    if not isinstance(manifest, dict):
        raise ReleaseAssetError("distribution manifest must be an object")
    return content, manifest


def _canonical_file_mode(status):
    return 0o755 if stat.S_IMODE(status.st_mode) & 0o111 else 0o644


def _distribution_records(root):
    records = []
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix().encode("utf-8"),
    ):
        relative = path.relative_to(root).as_posix()
        status = path.lstat()
        if stat.S_ISLNK(status.st_mode):
            raise ReleaseAssetError("distribution contains a link: %s" % relative)
        if stat.S_ISDIR(status.st_mode):
            records.append({"path": relative, "type": "directory", "mode": "0755"})
            continue
        if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
            raise ReleaseAssetError(
                "distribution contains a special or multi-link file: %s" % relative
            )
        mode = _canonical_file_mode(status)
        if (
            relative != "distribution-manifest.json"
            and stat.S_IMODE(status.st_mode) != mode
        ):
            raise ReleaseAssetError(
                "distribution file mode is not canonical: %s" % relative
            )
        content = _checked_regular_bytes(path, "distribution file %s" % relative)
        records.append(
            {
                "path": relative,
                "type": "file",
                "mode": "%04o" % mode,
                "bytes": len(content),
                "sha256": _sha256(content),
            }
        )
    return records


def _tar_bytes(distribution, archive_root):
    records = _distribution_records(distribution)
    buffer = BytesIO()
    try:
        with tarfile.open(
            fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT
        ) as archive:
            root_info = tarfile.TarInfo(archive_root)
            root_info.type = tarfile.DIRTYPE
            root_info.mode = 0o755
            root_info.mtime = 0
            root_info.uid = 0
            root_info.gid = 0
            root_info.uname = ""
            root_info.gname = ""
            archive.addfile(root_info)
            for record in records:
                info = tarfile.TarInfo(archive_root + "/" + record["path"])
                info.mode = int(record["mode"], 8)
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                if record["type"] == "directory":
                    info.type = tarfile.DIRTYPE
                    archive.addfile(info)
                    continue
                content = _checked_regular_bytes(
                    distribution / record["path"],
                    "distribution file %s" % record["path"],
                )
                info.type = tarfile.REGTYPE
                info.size = len(content)
                archive.addfile(info, BytesIO(content))
    except (OSError, tarfile.TarError, ValueError) as exc:
        raise ReleaseAssetError(
            "distribution cannot be represented as a safe ustar archive: %s" % exc
        ) from exc
    return buffer.getvalue()


def _deterministic_gzip(content):
    compressed = bytearray(gzip.compress(content, compresslevel=9, mtime=0))
    if len(compressed) < 10:
        raise ReleaseAssetError("gzip output is malformed")
    compressed[9] = 255
    return bytes(compressed)


def _bounded_gzip(content):
    if len(content) > MAX_RELEASE_ARCHIVE_BYTES:
        raise ReleaseAssetError(
            "release archive is %d bytes (limit %d)"
            % (len(content), MAX_RELEASE_ARCHIVE_BYTES)
        )
    if (
        len(content) < 10
        or content[:3] != b"\x1f\x8b\x08"
        or content[3] != 0
        or content[4:8] != b"\x00\x00\x00\x00"
        or content[9] != 255
    ):
        raise ReleaseAssetError("release archive gzip header is not canonical")
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        expanded = decompressor.decompress(content, MAX_RELEASE_TAR_BYTES + 1)
        if decompressor.unconsumed_tail or len(expanded) > MAX_RELEASE_TAR_BYTES:
            raise ReleaseAssetError("release archive expands beyond its hard limit")
        expanded += decompressor.flush(
            MAX_RELEASE_TAR_BYTES + 1 - len(expanded)
        )
    except zlib.error as exc:
        raise ReleaseAssetError("release archive gzip is invalid: %s" % exc) from exc
    if (
        len(expanded) > MAX_RELEASE_TAR_BYTES
        or not decompressor.eof
        or decompressor.unused_data
    ):
        raise ReleaseAssetError("release archive gzip stream is not singular and bounded")
    return expanded


def _write_new(path, content, mode=0o644):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(path, mode)
    except OSError as exc:
        raise ReleaseAssetError("cannot write %s: %s" % (path.name, exc)) from exc


def _archive_filename(version, profile):
    return "%s-%s-%s.tar.gz" % (PRODUCT, version, profile)


def _archive_root(version, profile):
    return "%s-%s-%s" % (PRODUCT, version, profile)


def _compare_distributions(expected, actual):
    if _distribution_records(expected) != _distribution_records(actual):
        raise ReleaseAssetError(
            "release archive payload does not match the exact source-commit build"
        )


def _verify_archive(
    archive_path,
    exported_source,
    expected_distribution,
    version,
    profile,
    repository,
    commit,
    temporary_root,
):
    filename = _archive_filename(version, profile)
    if archive_path.name != filename:
        raise ReleaseAssetError("release archive filename is invalid")
    content = _checked_regular_bytes(
        archive_path,
        "release archive %s" % filename,
        max_bytes=MAX_RELEASE_ARCHIVE_BYTES,
    )
    tar_content = _bounded_gzip(content)
    extraction = temporary_root / ("%s-extracted" % profile)
    extracted = _extract_tar_bytes(
        tar_content,
        extraction,
        _archive_root(version, profile),
        require_release_metadata=True,
    )
    _verify_distribution(
        exported_source, extracted, profile, repository, commit
    )
    _compare_distributions(expected_distribution, extracted)
    manifest_content, manifest = _distribution_manifest(extracted)
    return {
        "profile": profile,
        "filename": filename,
        "archive_root": _archive_root(version, profile),
        "bytes": len(content),
        "sha256": _sha256(content),
        "distribution_manifest_sha256": _sha256(manifest_content),
        "distribution_files_sha256": manifest.get("files_sha256"),
        "profile_definition_sha256": manifest.get("profile_definition_sha256"),
        "capability_ceiling": manifest.get("capability_ceiling"),
    }


def _ledger(repository, commit, version, assets, checksum_content):
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "product": PRODUCT,
        "version": version,
        "source": {"repository": repository, "commit": commit},
        "archive_policy": {
            "format": "tar+gzip",
            "tar_format": "ustar",
            "root": "filename-without-.tar.gz",
            "path_order": "bytewise-ascending",
            "mtime": 0,
            "uid": 0,
            "gid": 0,
            "uname": "",
            "gname": "",
            "directory_mode": "0755",
            "regular_mode": "0644",
            "executable_mode": "0755",
            "gzip_mtime": 0,
            "gzip_os": 255,
        },
        "assets": assets,
        "checksums": {
            "filename": CHECKSUM_NAME,
            "algorithm": "sha256",
            "covers": [item["filename"] for item in assets],
            "bytes": len(checksum_content),
            "sha256": _sha256(checksum_content),
        },
    }


def _validate_asset_record(record, version, profile):
    required = {
        "profile",
        "filename",
        "archive_root",
        "bytes",
        "sha256",
        "distribution_manifest_sha256",
        "distribution_files_sha256",
        "profile_definition_sha256",
        "capability_ceiling",
    }
    if not isinstance(record, dict) or set(record) != required:
        raise ReleaseAssetError("release asset ledger record shape is invalid")
    if (
        record["profile"] != profile
        or record["capability_ceiling"] != profile
        or record["filename"] != _archive_filename(version, profile)
        or record["archive_root"] != _archive_root(version, profile)
        or isinstance(record["bytes"], bool)
        or not isinstance(record["bytes"], int)
        or record["bytes"] <= 0
        or any(
            not isinstance(record[key], str) or not SHA256.fullmatch(record[key])
            for key in (
                "sha256",
                "distribution_manifest_sha256",
                "distribution_files_sha256",
                "profile_definition_sha256",
            )
        )
    ):
        raise ReleaseAssetError("release asset ledger record identity is invalid")


def _validate_ledger(ledger, repository, commit, version):
    required = {
        "schema_version",
        "product",
        "version",
        "source",
        "archive_policy",
        "assets",
        "checksums",
    }
    if not isinstance(ledger, dict) or set(ledger) != required:
        raise ReleaseAssetError("release asset ledger shape is invalid")
    if (
        ledger["schema_version"] != LEDGER_SCHEMA_VERSION
        or ledger["product"] != PRODUCT
        or ledger["version"] != version
        or ledger["source"] != {"repository": repository, "commit": commit}
    ):
        raise ReleaseAssetError("release asset ledger identity is invalid")
    expected_policy = _ledger(repository, commit, version, [], b"")[
        "archive_policy"
    ]
    if ledger["archive_policy"] != expected_policy:
        raise ReleaseAssetError("release asset archive policy is invalid")
    assets = ledger["assets"]
    if not isinstance(assets, list) or len(assets) != len(PROFILES):
        raise ReleaseAssetError("release asset ledger must contain three profiles")
    for profile, record in zip(PROFILES, assets):
        _validate_asset_record(record, version, profile)
    checksums = ledger["checksums"]
    if (
        not isinstance(checksums, dict)
        or set(checksums)
        != {"filename", "algorithm", "covers", "bytes", "sha256"}
        or checksums["filename"] != CHECKSUM_NAME
        or checksums["algorithm"] != "sha256"
        or checksums["covers"] != [item["filename"] for item in assets]
        or isinstance(checksums["bytes"], bool)
        or not isinstance(checksums["bytes"], int)
        or checksums["bytes"] <= 0
        or not isinstance(checksums["sha256"], str)
        or not SHA256.fullmatch(checksums["sha256"])
    ):
        raise ReleaseAssetError("release checksum ledger record is invalid")
    return assets


def _inspect_output(output):
    try:
        status = output.lstat()
    except OSError as exc:
        raise ReleaseAssetError("release asset directory is unavailable: %s" % exc) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ReleaseAssetError("release asset path must be a real directory")
    entries = {}
    try:
        children = list(output.iterdir())
    except OSError as exc:
        raise ReleaseAssetError("cannot list release asset directory: %s" % exc) from exc
    for path in children:
        child = path.lstat()
        if (
            stat.S_ISLNK(child.st_mode)
            or not stat.S_ISREG(child.st_mode)
            or child.st_nlink != 1
            or stat.S_IMODE(child.st_mode) != 0o644
        ):
            raise ReleaseAssetError(
                "release output contains an unsafe file: %s" % path.name
            )
        entries[path.name] = path
    return entries


def _load_ledger(output):
    content = _checked_regular_bytes(
        output / LEDGER_NAME, "release asset ledger"
    )
    try:
        ledger = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReleaseAssetError(
            "release asset ledger is not valid UTF-8 JSON: %s" % exc
        ) from exc
    return content, ledger


def _verify_output_set(
    output,
    exported_source,
    repository,
    commit,
    version,
    temporary_root,
):
    entries = _inspect_output(output)
    expected_names = {
        LEDGER_NAME,
        CHECKSUM_NAME,
        *(_archive_filename(version, profile) for profile in PROFILES),
    }
    if set(entries) != expected_names:
        raise ReleaseAssetError(
            "release output must contain exactly the three archives, "
            "SHA256SUMS, and release-assets.json"
        )
    ledger_content, ledger = _load_ledger(output)
    del ledger_content
    assets = _validate_ledger(ledger, repository, commit, version)
    checksum_content = _checked_regular_bytes(
        output / CHECKSUM_NAME, "release checksums"
    )
    expected_checksums = "".join(
        "%s  %s\n" % (item["sha256"], item["filename"]) for item in assets
    ).encode("utf-8")
    if checksum_content != expected_checksums:
        raise ReleaseAssetError("SHA256SUMS does not match the release asset ledger")
    checksum_record = ledger["checksums"]
    if (
        checksum_record["bytes"] != len(checksum_content)
        or checksum_record["sha256"] != _sha256(checksum_content)
    ):
        raise ReleaseAssetError("release checksum ledger digest is invalid")
    verified = []
    for profile, record in zip(PROFILES, assets):
        archive_path = output / record["filename"]
        content = _checked_regular_bytes(
            archive_path,
            "release archive %s" % record["filename"],
            max_bytes=MAX_RELEASE_ARCHIVE_BYTES,
        )
        if len(content) != record["bytes"] or _sha256(content) != record["sha256"]:
            raise ReleaseAssetError(
                "release archive does not match its ledger: %s"
                % record["filename"]
            )
        expected_distribution = temporary_root / ("%s-expected" % profile)
        _build_profile(
            exported_source,
            profile,
            expected_distribution,
            repository,
            commit,
        )
        actual = _verify_archive(
            archive_path,
            exported_source,
            expected_distribution,
            version,
            profile,
            repository,
            commit,
            temporary_root,
        )
        if actual != record:
            raise ReleaseAssetError(
                "release archive verified metadata does not match its ledger"
            )
        verified.append(actual)
    return verified


def _prepare_output(output):
    if output.exists() or output.is_symlink():
        raise ReleaseAssetError("release asset output must not already exist")
    parent = output.parent
    try:
        status = parent.lstat()
    except OSError as exc:
        raise ReleaseAssetError("release output parent is unavailable: %s" % exc) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ReleaseAssetError("release output parent must be a real directory")
    return Path(tempfile.mkdtemp(prefix=".release-assets-", dir=parent))


def build_release_assets(
    source_repo,
    output,
    repository,
    commit,
    version,
):
    _validate_identity(repository, commit, version)
    source_repo = _validate_repo(source_repo)
    stage = _prepare_output(output)
    temporary = Path(tempfile.mkdtemp(prefix="release-source-"))
    try:
        exported_source = _export_commit(
            source_repo, commit, temporary / "export"
        )
        _source_version(exported_source, version)
        assets = []
        for profile in PROFILES:
            distribution = temporary / ("%s-distribution" % profile)
            _build_profile(
                exported_source,
                profile,
                distribution,
                repository,
                commit,
            )
            filename = _archive_filename(version, profile)
            archive_content = _deterministic_gzip(
                _tar_bytes(distribution, _archive_root(version, profile))
            )
            archive_path = stage / filename
            _write_new(archive_path, archive_content)
            assets.append(
                _verify_archive(
                    archive_path,
                    exported_source,
                    distribution,
                    version,
                    profile,
                    repository,
                    commit,
                    temporary,
                )
            )
        checksums = "".join(
            "%s  %s\n" % (item["sha256"], item["filename"])
            for item in assets
        ).encode("utf-8")
        _write_new(stage / CHECKSUM_NAME, checksums)
        ledger = _ledger(repository, commit, version, assets, checksums)
        _write_new(stage / LEDGER_NAME, canonical_json(ledger))
        entries = _inspect_output(stage)
        expected = {
            LEDGER_NAME,
            CHECKSUM_NAME,
            *(_archive_filename(version, profile) for profile in PROFILES),
        }
        if set(entries) != expected:
            raise ReleaseAssetError("release asset build produced unexpected files")
        stage.rename(output)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
    return ledger


def verify_release_assets(
    source_repo,
    output,
    repository,
    commit,
    version,
):
    _validate_identity(repository, commit, version)
    source_repo = _validate_repo(source_repo)
    temporary = Path(tempfile.mkdtemp(prefix="release-verify-"))
    try:
        exported_source = _export_commit(
            source_repo, commit, temporary / "export"
        )
        _source_version(exported_source, version)
        return _verify_output_set(
            output,
            exported_source,
            repository,
            commit,
            version,
            temporary,
        )
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--output",
        type=Path,
        help="Create a new directory containing all release assets.",
    )
    action.add_argument(
        "--verify",
        type=Path,
        metavar="ASSET_DIRECTORY",
        help="Read-only verification of an existing release asset directory.",
    )
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=ROOT,
        help="Local Git object database used only for an exact git archive export.",
    )
    parser.add_argument("--source-repository", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args(argv)
    try:
        if args.output is not None:
            ledger = build_release_assets(
                args.source_repo,
                args.output,
                args.source_repository,
                args.source_commit,
                args.version,
            )
            print(
                "built %s %s release assets from %s@%s: %d archives"
                % (
                    PRODUCT,
                    args.version,
                    args.source_repository,
                    args.source_commit,
                    len(ledger["assets"]),
                )
            )
        else:
            assets = verify_release_assets(
                args.source_repo,
                args.verify,
                args.source_repository,
                args.source_commit,
                args.version,
            )
            print(
                "verified %s %s release assets from %s@%s: %d archives"
                % (
                    PRODUCT,
                    args.version,
                    args.source_repository,
                    args.source_commit,
                    len(assets),
                )
            )
    except ReleaseAssetError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
