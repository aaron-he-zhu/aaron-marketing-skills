import hashlib
from io import BytesIO
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build-release-assets.py"
SCHEMA = ROOT / "references" / "release-assets.schema.json"
REPOSITORY = "aaron-he-zhu/aaron-marketing-skills"


def load_builder():
    specification = importlib.util.spec_from_file_location(
        "release_asset_builder_under_test", BUILDER
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load release asset builder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


BUILDER_MODULE = load_builder()


def current_source_snapshot(destination):
    completed = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    relative_paths = sorted(
        item.decode("utf-8")
        for item in completed.stdout.split(b"\0")
        if item
    )
    for relative in relative_paths:
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        status = source.lstat()
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        elif source.is_file():
            shutil.copyfile(source, target)
            os.chmod(target, 0o755 if status.st_mode & 0o111 else 0o644)
    subprocess.run(["git", "init", "-q"], cwd=destination, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Release Asset Test"],
        cwd=destination,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "release-assets@example.com"],
        cwd=destination,
        check=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=destination, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "test source"],
        cwd=destination,
        check=True,
    )
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    catalog = json.loads(
        (destination / "references/system-catalog.json").read_text(encoding="utf-8")
    )
    return commit, catalog["bundle_version"]


def malicious_tar(member):
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        root = tarfile.TarInfo("fixed-root")
        root.type = tarfile.DIRTYPE
        root.mode = 0o755
        root.uid = root.gid = root.mtime = 0
        root.uname = root.gname = ""
        archive.addfile(root)
        archive.addfile(member, BytesIO(b"x") if member.isfile() else None)
    return buffer.getvalue()


class ReleaseAssetArchiveSafetyTests(unittest.TestCase):
    def assert_rejected(self, member):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name) / "extract"
        with self.assertRaises(BUILDER_MODULE.ReleaseAssetError):
            BUILDER_MODULE._extract_tar_bytes(
                malicious_tar(member),
                destination,
                "fixed-root",
                require_release_metadata=True,
            )

    def test_path_traversal_is_rejected(self):
        member = tarfile.TarInfo("fixed-root/../escape")
        member.type = tarfile.REGTYPE
        member.size = 1
        member.mode = 0o644
        member.uid = member.gid = member.mtime = 0
        member.uname = member.gname = ""
        self.assert_rejected(member)

    def test_symbolic_link_is_rejected(self):
        member = tarfile.TarInfo("fixed-root/link")
        member.type = tarfile.SYMTYPE
        member.linkname = "target"
        member.mode = 0o644
        member.uid = member.gid = member.mtime = 0
        member.uname = member.gname = ""
        self.assert_rejected(member)

    def test_hard_link_is_rejected(self):
        member = tarfile.TarInfo("fixed-root/hard-link")
        member.type = tarfile.LNKTYPE
        member.linkname = "fixed-root/target"
        member.mode = 0o644
        member.uid = member.gid = member.mtime = 0
        member.uname = member.gname = ""
        self.assert_rejected(member)

    def test_special_file_is_rejected(self):
        member = tarfile.TarInfo("fixed-root/fifo")
        member.type = tarfile.FIFOTYPE
        member.mode = 0o644
        member.uid = member.gid = member.mtime = 0
        member.uname = member.gname = ""
        self.assert_rejected(member)


class ReleaseAssetPromptBindingGateTests(unittest.TestCase):
    def test_release_build_rejects_nonempty_certified_bindings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_repo = root / "source-repo"
            source_repo.mkdir()
            _commit, version = current_source_snapshot(source_repo)
            catalog_path = source_repo / "references/prompt-profiles.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["certified_bindings"] = [{"hand_forged": True}]
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["git", "add", "references/prompt-profiles.json"],
                cwd=source_repo,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-q", "-m", "forge compact binding"],
                cwd=source_repo,
                check=True,
            )
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=source_repo,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            completed = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--output",
                    str(root / "release-assets"),
                    "--source-repo",
                    str(source_repo),
                    "--source-repository",
                    REPOSITORY,
                    "--source-commit",
                    commit,
                    "--version",
                    version,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn(
            "non-empty certified_bindings are not distributable",
            completed.stderr,
        )


class ReleaseAssetIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.source_repo = cls.root / "source-repo"
        cls.source_repo.mkdir()
        cls.commit, cls.version = current_source_snapshot(cls.source_repo)

        # The release builder must consume the committed object, never these
        # post-commit worktree bytes.
        with (cls.source_repo / "scripts/build-distribution.py").open(
            "a", encoding="utf-8"
        ) as handle:
            handle.write("\nraise RuntimeError('uncommitted worktree was executed')\n")

        cls.outputs = []
        for name in ("first", "second"):
            output = cls.root / name
            completed = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--output",
                    str(output),
                    "--source-repo",
                    str(cls.source_repo),
                    "--source-repository",
                    REPOSITORY,
                    "--source-commit",
                    cls.commit,
                    "--version",
                    cls.version,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            if completed.returncode:
                raise RuntimeError(
                    "release asset integration build failed:\n%s\n%s"
                    % (completed.stdout, completed.stderr)
                )
            cls.outputs.append(output)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_two_complete_builds_are_byte_identical(self):
        first_names = sorted(path.name for path in self.outputs[0].iterdir())
        second_names = sorted(path.name for path in self.outputs[1].iterdir())
        self.assertEqual(first_names, second_names)
        self.assertEqual(
            sorted(
                [
                    "SHA256SUMS",
                    "release-assets.json",
                    *[
                        "aaron-marketing-skills-%s-%s.tar.gz"
                        % (self.version, profile)
                        for profile in ("lite", "pro", "governed")
                    ],
                ]
            ),
            first_names,
        )
        for name in first_names:
            self.assertEqual(
                (self.outputs[0] / name).read_bytes(),
                (self.outputs[1] / name).read_bytes(),
                name,
            )

    def test_ledger_and_checksums_cover_all_three_archives(self):
        ledger = json.loads(
            (self.outputs[0] / "release-assets.json").read_text(encoding="utf-8")
        )
        self.assertEqual("1.0", ledger["schema_version"])
        self.assertEqual(
            {"repository": REPOSITORY, "commit": self.commit},
            ledger["source"],
        )
        self.assertEqual(
            ["lite", "pro", "governed"],
            [item["profile"] for item in ledger["assets"]],
        )
        checksum_lines = (
            self.outputs[0] / "SHA256SUMS"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(3, len(checksum_lines))
        for asset, line in zip(ledger["assets"], checksum_lines):
            content = (self.outputs[0] / asset["filename"]).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), asset["sha256"])
            self.assertEqual(
                "%s  %s" % (asset["sha256"], asset["filename"]),
                line,
            )

    def test_existing_asset_directory_verifies_against_exact_commit(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(BUILDER),
                "--verify",
                str(self.outputs[0]),
                "--source-repo",
                str(self.source_repo),
                "--source-repository",
                REPOSITORY,
                "--source-commit",
                self.commit,
                "--version",
                self.version,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("verified", completed.stdout)

    def test_archive_tampering_fails_closed(self):
        tampered = self.root / "tampered"
        shutil.copytree(self.outputs[0], tampered)
        archive = tampered / (
            "aaron-marketing-skills-%s-lite.tar.gz" % self.version
        )
        content = bytearray(archive.read_bytes())
        content[len(content) // 2] ^= 1
        archive.write_bytes(content)
        completed = subprocess.run(
            [
                sys.executable,
                str(BUILDER),
                "--verify",
                str(tampered),
                "--source-repo",
                str(self.source_repo),
                "--source-repository",
                REPOSITORY,
                "--source-commit",
                self.commit,
                "--version",
                self.version,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("does not match its ledger", completed.stderr)

    def test_ledger_schema_declares_exact_three_asset_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema",
            schema["$schema"],
        )
        self.assertEqual(3, schema["properties"]["assets"]["minItems"])
        self.assertEqual(3, schema["properties"]["assets"]["maxItems"])
        self.assertEqual(
            ["liteAsset", "proAsset", "governedAsset"],
            [
                item["$ref"].rsplit("/", 1)[-1]
                for item in schema["properties"]["assets"]["prefixItems"]
            ],
        )


if __name__ == "__main__":
    unittest.main()
