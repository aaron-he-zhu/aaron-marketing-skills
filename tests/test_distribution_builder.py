import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build-distribution.py"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def load_builder_module():
    specification = importlib.util.spec_from_file_location(
        "distribution_builder_under_test", BUILDER
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load distribution builder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


BUILDER_MODULE = load_builder_module()


def packed_member(output, relative):
    path = output / "references/skill-contracts.pack.json.gz"
    pack = json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
    matches = [item for item in pack["files"] if item["path"] == relative]
    if len(matches) != 1:
        raise AssertionError("packed member is missing or duplicated: %s" % relative)
    content = (
        json.dumps(
            matches[0]["content"],
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    return content, pack


class DistributionBuilderTests(unittest.TestCase):
    def build(self, *arguments):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "distribution"
        subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output), *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return output

    def test_plugin_contains_runtime_and_excludes_maintenance(self):
        output = self.build("--plugin", "--profile", "governed")
        plugin = json.loads((output / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(120, len(plugin["skills"]))
        self.assertEqual(120, len(list(output.glob("*/*/*/SKILL.md"))) + len(list(output.glob("protocol/*/SKILL.md"))))
        for path in (
            "scripts/audit-loop.py",
            "scripts/rubric-score.py",
            "scripts/validate-audit-artifact.py",
            "scripts/registry-events.py",
            "scripts/run-events.py",
            "scripts/context-resolver.py",
            "scripts/context-plan.py",
            "scripts/runtime-controller.py",
            "scripts/workflow-graph.py",
            "scripts/workflow-loop.py",
            "scripts/workflow_loop.py",
            "references/context-request.schema.json",
            "references/context-manifest.schema.json",
            "references/context-planning.md",
            "references/context-resolution.md",
            "references/runtime-controller.md",
            "references/runtime-controller-request.schema.json",
            "references/skill-contracts.pack.json.gz",
            "references/skill-machine-contract.schema.json",
            "references/skill-machine-contract-index.schema.json",
            "references/audit-loop-state.schema.json",
            "references/audit-loop-protocol.md",
            "references/auto-routing-scenarios.md",
            "references/run-event.schema.json",
            "references/turn-snapshot.schema.json",
            "references/workflow-graph-protocol.md",
            "references/workflow-graph.json",
            "references/workflow-graph.source.json",
            "references/workflow-graph.schema.json",
            "references/workflow-loop-protocol.md",
            "references/workflow-loop-request.schema.json",
            "references/workflow-loop-state.schema.json",
            "docs/workflow-graph.md",
            "references/save-point.schema.json",
            "references/run-envelope.schema.json",
            "references/runtime-protocol.md",
            "references/system-catalog.json",
            "references/scheduling.md",
            "commands/auto.md",
            "hooks/hooks.json",
        ):
            self.assertTrue((output / path).is_file(), path)
        for shard in (
            "narrative", "seo-geo", "social", "email", "ad", "influencer",
            "launch", "cross-discipline",
        ):
            self.assertTrue((output / "references" / "auto-routing" / (shard + ".md")).is_file(), shard)
        self.assertFalse((output / "evals/auto-routing-scenarios.source.md").exists())
        self.assertFalse((output / "scripts/generate-auto-routing-shards.py").exists())
        self.assertTrue((output / "scripts/connectors/resend.py").is_file())
        self.assertTrue((output / "references/skill-contract.md").is_file())
        for path in ("tests", "evals", ".github", ".githooks", "AGENTS.md", "CONTRIBUTING.md"):
            self.assertFalse((output / path).exists(), path)
        self.assertEqual(
            {Path("workflow-graph.md")},
            {path.relative_to(output / "docs") for path in (output / "docs").rglob("*") if path.is_file()},
        )
        self.assertEqual(10, len(list((output / "references/workflow-graph").glob("edges-*.json"))))
        self.assertFalse(any(path.name == "__pycache__" for path in output.rglob("*")))
        self.assertFalse(any(path.suffix == ".pyc" for path in output.rglob("*")))
        self.assertEqual(
            8, sum(path.name == "auditor-runtime.md" for path in output.rglob("*"))
        )
        manifest = json.loads(
            (output / "distribution-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual("1.1", manifest["schema_version"])
        self.assertEqual("plugin", manifest["kind"])
        self.assertEqual("governed", manifest["profile"])
        self.assertIn("registry-write", manifest["capabilities"])
        self.assertEqual("governed", manifest["capability_ceiling"])
        self.assertRegex(manifest["catalog_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(manifest["profile_definition_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual("sha256", manifest["hash_algorithm"])
        self.assertEqual(
            hashlib.sha256(BUILDER_MODULE.canonical_json(manifest["files"])).hexdigest(),
            manifest["files_sha256"],
        )
        expected_paths = sorted(
            path.relative_to(output).as_posix()
            for path in output.rglob("*")
            if path.is_file() and path.name != "distribution-manifest.json"
        )
        self.assertEqual(expected_paths, sorted(item["path"] for item in manifest["files"]))
        source_references = {path.relative_to(ROOT / "references") for path in (ROOT / "references").rglob("*") if path.is_file()}
        shipped_references = {path.relative_to(output / "references") for path in (output / "references").rglob("*") if path.is_file()}
        self.assertLess(len(shipped_references), len(source_references))

        for runtime in ("runtime-controller.py", "workflow-graph.py", "workflow-loop.py"):
            result = subprocess.run(
                [sys.executable, str(output / "scripts" / runtime), "--help"],
                cwd=output, capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, "%s: %s" % (runtime, result.stderr))
        self.assertFalse((output / "references/skill-contracts").exists())
        with tempfile.TemporaryDirectory() as project:
            request = Path(project) / "request.json"
            planned = subprocess.run(
                [
                    sys.executable, str(output / "scripts/context-plan.py"), "plan",
                    "--skill", "content-writer",
                    "--run-id", "11111111-1111-4111-8111-111111111111",
                    "--turn-id", "turn-1",
                    "--as-of", "2026-07-24T00:00:00Z",
                    "--project-root", project,
                    "--bundle-root", str(output),
                    "--output", str(request),
                ],
                cwd=output, capture_output=True, text=True,
            )
            self.assertEqual(0, planned.returncode, planned.stderr)
            validated = subprocess.run(
                [
                    sys.executable, str(output / "scripts/context-plan.py"), "validate",
                    "--request", str(request),
                    "--project-root", project,
                    "--bundle-root", str(output),
                ],
                cwd=output, capture_output=True, text=True,
            )
            self.assertEqual(0, validated.returncode, validated.stderr)

    def test_profiles_are_monotonic_closed_and_within_package_ceilings(self):
        distribution = json.loads(
            (ROOT / "references/distribution-files.json").read_text()
        )
        catalog_sha256 = hashlib.sha256(
            (ROOT / "references/system-catalog.json").read_bytes()
        ).hexdigest()
        capability_catalog = json.loads(
            (ROOT / "references/capability-profiles.json").read_text()
        )
        outputs = {
            profile: self.build("--plugin", "--profile", profile)
            for profile in ("lite", "pro", "governed")
        }
        paths = {}
        capabilities = {}
        expected_ceilings = {
            "lite": {"max_files": 350, "max_bytes": 3_000_000},
            "pro": {"max_files": 400, "max_bytes": 3_700_000},
            "governed": {"max_files": 460, "max_bytes": 5_200_000},
        }
        for profile, output in outputs.items():
            plugin = json.loads((output / ".claude-plugin/plugin.json").read_text())
            self.assertEqual(120, len(plugin["skills"]))
            manifest = json.loads((output / "distribution-manifest.json").read_text())
            self.assertEqual(profile, manifest["profile"])
            self.assertEqual(catalog_sha256, manifest["catalog_sha256"])
            self.assertEqual(
                BUILDER_MODULE.resolve_plugin_profile(
                    distribution, profile,
                )["definition_sha256"],
                manifest["profile_definition_sha256"],
            )
            paths[profile] = {item["path"] for item in manifest["files"]}
            capabilities[profile] = set(manifest["capabilities"])
            self.assertEqual(
                capability_catalog["profiles"][profile]["capabilities"],
                manifest["capabilities"],
            )
            ceiling = manifest["package_ceiling"]
            self.assertEqual(expected_ceilings[profile], ceiling)
            self.assertLessEqual(len(manifest["files"]) + 1, ceiling["max_files"])
            self.assertLessEqual(
                sum(item["bytes"] for item in manifest["files"])
                + (output / "distribution-manifest.json").stat().st_size,
                ceiling["max_bytes"],
            )
            self.assertEqual(
                8, sum(path.name == "auditor-runtime.md" for path in output.rglob("*"))
            )
            self.assertFalse(any(
                re.fullmatch(r".+ [0-9]+\.[A-Za-z0-9]+", path.name)
                for path in output.rglob("*") if path.is_file()
            ))
            with tempfile.TemporaryDirectory() as project:
                resolution = subprocess.run(
                    [
                        sys.executable, str(output / "scripts/profile-resolver.py"),
                        "--root", project, "--bundle-root", str(output),
                        "diagnose", "--json",
                    ],
                    cwd=output, capture_output=True, text=True,
                )
                self.assertEqual(0, resolution.returncode, resolution.stderr)
                resolved = json.loads(resolution.stdout)
                self.assertEqual(profile, resolved["package_ceiling"])
                self.assertEqual("lite", resolved["effective_profile"])

        self.assertLess(paths["lite"], paths["pro"])
        self.assertLess(paths["pro"], paths["governed"])
        self.assertLess(capabilities["lite"], capabilities["pro"])
        self.assertLess(capabilities["pro"], capabilities["governed"])

        lite = outputs["lite"]
        self.assertFalse((lite / "scripts/connectors/resend.py").exists())
        self.assertTrue((lite / "scripts/rubric-score.py").is_file())
        self.assertFalse((lite / "scripts/validate-audit-artifact.py").exists())
        self.assertFalse((lite / "scripts/registry-events.py").exists())
        self.assertFalse((lite / "hooks").exists())
        self.assertFalse((lite / "references/skill-contracts").exists())

        pro = outputs["pro"]
        self.assertTrue((pro / "scripts/connectors/resend.py").is_file())
        self.assertTrue((pro / "scripts/rubric-score.py").is_file())
        self.assertTrue((pro / "scripts/validate-audit-artifact.py").is_file())
        self.assertFalse((pro / "scripts/registry-events.py").exists())
        self.assertFalse((pro / "hooks").exists())
        self.assertFalse((pro / "references/skill-contracts").exists())

        governed = outputs["governed"]
        self.assertTrue((governed / "scripts/registry-events.py").is_file())
        self.assertTrue((governed / "scripts/runtime-controller.py").is_file())
        self.assertTrue((governed / "hooks/hooks.json").is_file())
        self.assertTrue(
            (governed / "references/skill-contracts.pack.json.gz").is_file()
        )
        self.assertFalse((governed / "references/skill-contracts").exists())
        self.assertLessEqual(
            (governed / "references/skill-contracts.pack.json.gz").stat().st_size,
            1_000_000,
        )
        _index_raw, pack = packed_member(
            governed, "references/skill-contracts/index.json"
        )
        self.assertEqual(121, pack["file_count"])
        for profile, runtimes in {
            "lite": ("profile-resolver.py", "rubric-score.py"),
            "pro": ("validate-audit-artifact.py",),
            "governed": ("registry-events.py", "runtime-controller.py"),
        }.items():
            for runtime in runtimes:
                result = subprocess.run(
                    [sys.executable, str(outputs[profile] / "scripts" / runtime), "--help"],
                    cwd=outputs[profile], capture_output=True, text=True,
                )
                self.assertEqual(
                    0, result.returncode,
                    "%s/%s: %s" % (profile, runtime, result.stderr),
                )

    def test_profile_builds_are_reproducible(self):
        for profile in ("lite", "pro", "governed"):
            first = json.loads((
                self.build("--plugin", "--profile", profile)
                / "distribution-manifest.json"
            ).read_text())
            second = json.loads((
                self.build("--plugin", "--profile", profile)
                / "distribution-manifest.json"
            ).read_text())
            self.assertEqual(first["files_sha256"], second["files_sha256"], profile)
            self.assertEqual(
                first["profile_definition_sha256"],
                second["profile_definition_sha256"],
                profile,
            )
            self.assertEqual(first["files"], second["files"], profile)

    def test_bare_plugin_is_governed_alias_with_warning(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "distribution"
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(output), "--plugin"],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("deprecated governed alias through v20", result.stderr)
            manifest = json.loads((output / "distribution-manifest.json").read_text())
            self.assertEqual("governed", manifest["profile"])
            self.assertTrue((output / "scripts/registry-events.py").is_file())

    def test_profile_rejected_for_standalone_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable, str(BUILDER),
                    "--output", str(Path(temporary) / "distribution"),
                    "--skill", "narrative/evaluate/narrative-quality-auditor",
                    "--profile", "lite",
                ],
                cwd=ROOT, capture_output=True, text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--profile applies to --plugin builds only", result.stderr)

    def test_standalone_contains_only_one_skill_payload(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        self.assertTrue((output / "SKILL.md").is_file())
        self.assertTrue((output / "references/auditor-runtime.md").is_file())
        self.assertFalse((output / "scripts").exists())
        self.assertFalse((output / ".claude-plugin").exists())
        manifest = json.loads((output / "distribution-manifest.json").read_text())
        self.assertEqual("1.1", manifest["schema_version"])
        self.assertEqual("lite", manifest["profile"])
        self.assertEqual("standalone-skill", manifest["kind"])
        self.assertEqual(
            ["inline-delivery", "canonical-state-read"],
            manifest["capabilities"],
        )

    def test_slim_frontmatter_strips_publishing_keys_only(self):
        output = self.build(
            "--plugin", "--profile", "governed", "--slim-frontmatter",
        )
        skills = list(output.glob("*/*/*/SKILL.md")) + list(output.glob("protocol/*/SKILL.md"))
        self.assertEqual(120, len(skills))
        for skill in skills:
            frontmatter = skill.read_text(encoding="utf-8").split("---")[1]
            for stripped in ("slug:", "displayName:", "summary:"):
                self.assertNotIn(stripped, frontmatter, skill)
            for required in ("name:", "version:", "description:", "metadata:",
                             "license:", "compatibility:"):
                self.assertIn(required, frontmatter, skill)
        index_raw, _pack = packed_member(
            output, "references/skill-contracts/index.json"
        )
        index = json.loads(index_raw)
        entry = next(item for item in index["contracts"] if item["skill"] == "content-writer")
        contract_raw, _pack = packed_member(output, entry["contract_ref"])
        contract = json.loads(contract_raw)
        self.assertEqual(
            contract["identity"]["sha256"],
            hashlib.sha256((output / contract["identity"]["path"]).read_bytes()).hexdigest(),
        )

    def test_slim_frontmatter_rejects_standalone(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "distribution"
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output),
             "--skill", "narrative/evaluate/narrative-quality-auditor", "--slim-frontmatter"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--slim-frontmatter applies to --plugin builds only", result.stderr)

    def test_plugin_runtime_markdown_links_are_closed(self):
        distribution = json.loads(
            (ROOT / "references/distribution-files.json").read_text()
        )
        for profile_name in ("lite", "pro", "governed"):
            output = self.build("--plugin", "--profile", profile_name)
            profile = BUILDER_MODULE.resolve_plugin_profile(
                distribution, profile_name,
            )
            missing = []
            runtime_roots = [output / "commands", output / "references"]
            runtime_roots.extend(
                output / path.removeprefix("./") for path in json.loads(
                    (output / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
                )["skills"]
            )
            sources = [(path, True) for path in output.glob("*.md") if path.is_file()]
            for runtime_root in runtime_roots:
                sources.extend((path, False) for path in runtime_root.rglob("*.md"))
            for source, runtime_only in sources:
                for raw in MARKDOWN_LINK.findall(source.read_text(encoding="utf-8")):
                    target = raw.strip().lstrip("<").rstrip(">").split("#", 1)[0]
                    if (target == "url" or not target
                            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)):
                        continue
                    resolved = (source.parent / target).resolve()
                    if runtime_only:
                        try:
                            relative = resolved.relative_to(output.resolve())
                        except ValueError:
                            continue
                        if (not relative.parts
                                or relative.parts[0] not in {"references", "scripts"}):
                            continue
                    try:
                        relative = resolved.relative_to(output.resolve())
                    except ValueError:
                        missing.append(
                            "%s -> %s" % (source.relative_to(output), target)
                        )
                    else:
                        if (not resolved.exists()
                                and BUILDER_MODULE.dependency_allowed(
                                    relative.as_posix(), profile)):
                            missing.append(
                                "%s -> %s" % (source.relative_to(output), target)
                            )
            self.assertEqual([], missing, profile_name)

    def test_unknown_skill_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(Path(temporary) / "out"), "--skill", "missing/skill"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown skill path", result.stderr)

    def _assert_tree_copy_rejected(self, setup, pattern):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_root = base / "source"
            source_root.mkdir()
            tree = source_root / "tree"
            tree.mkdir()
            setup(base, tree)
            output = base / "output"
            output.mkdir()
            with mock.patch.object(BUILDER_MODULE, "ROOT", source_root):
                with self.assertRaisesRegex(BUILDER_MODULE.DistributionError, pattern):
                    BUILDER_MODULE.copy_entry("tree", output)

    def test_tree_copy_skips_untracked_and_backup_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            tree = root / "tree"
            tree.mkdir(parents=True)
            (tree / "tracked.md").write_text("tracked", encoding="utf-8")
            (tree / "untracked.md").write_text("untracked", encoding="utf-8")
            (tree / "tracked 2.md").write_text("backup", encoding="utf-8")
            output = Path(temporary) / "output"
            output.mkdir()

            def git_files(mode):
                if mode == "tracked":
                    return {"tree/tracked.md", "tree/tracked 2.md"}
                return {"tree/untracked.md"}

            with (
                mock.patch.object(BUILDER_MODULE, "ROOT", root),
                mock.patch.object(BUILDER_MODULE, "_git_file_set", side_effect=git_files),
            ):
                BUILDER_MODULE.copy_entry("tree", output)
            self.assertTrue((output / "tree/tracked.md").is_file())
            self.assertFalse((output / "tree/untracked.md").exists())
            self.assertFalse((output / "tree/tracked 2.md").exists())

    def test_explicit_declared_file_may_be_untracked_but_not_ignored_backup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            (root / "generated.json").write_text("{}", encoding="utf-8")
            (root / "generated 2.json").write_text("{}", encoding="utf-8")
            output = Path(temporary) / "output"
            output.mkdir()
            with (
                mock.patch.object(BUILDER_MODULE, "ROOT", root),
                mock.patch.object(BUILDER_MODULE, "_git_file_set", return_value=set()),
            ):
                BUILDER_MODULE.copy_entry(
                    "generated.json", output, allow_untracked=True,
                )
                copied = BUILDER_MODULE.copy_entry(
                    "generated 2.json", output, allow_untracked=True,
                )
            self.assertTrue((output / "generated.json").is_file())
            self.assertFalse(copied)
            self.assertFalse((output / "generated 2.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_copy_rejects_external_file_symlink(self):
        def setup(base, tree):
            external = base / "outside.txt"
            external.write_text("outside", encoding="utf-8")
            try:
                (tree / "external-file").symlink_to(external)
            except OSError as exc:
                self.skipTest("cannot create symlink: %s" % exc)

        self._assert_tree_copy_rejected(setup, "contains a symlink")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_copy_rejects_external_directory_symlink(self):
        def setup(base, tree):
            external = base / "outside-dir"
            external.mkdir()
            (external / "secret.txt").write_text("outside", encoding="utf-8")
            try:
                (tree / "external-dir").symlink_to(external, target_is_directory=True)
            except OSError as exc:
                self.skipTest("cannot create directory symlink: %s" % exc)

        self._assert_tree_copy_rejected(setup, "contains a symlink")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_copy_rejects_circular_symlink(self):
        def setup(_base, tree):
            try:
                (tree / "cycle").symlink_to("cycle")
            except OSError as exc:
                self.skipTest("cannot create circular symlink: %s" % exc)

        self._assert_tree_copy_rejected(setup, "contains a symlink")

    @unittest.skipUnless(hasattr(os, "link"), "hard links are unavailable")
    def test_copy_rejects_multi_link_regular_file(self):
        def setup(_base, tree):
            original = tree / "original.txt"
            original.write_text("same inode", encoding="utf-8")
            try:
                os.link(original, tree / "alias.txt")
            except OSError as exc:
                self.skipTest("cannot create hard link: %s" % exc)

        self._assert_tree_copy_rejected(setup, "single-link regular file")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFOs are unavailable")
    def test_copy_rejects_special_file(self):
        def setup(_base, tree):
            try:
                os.mkfifo(tree / "pipe")
            except OSError as exc:
                self.skipTest("cannot create FIFO: %s" % exc)

        self._assert_tree_copy_rejected(setup, "special file")

    def test_manifest_verification_detects_post_build_tampering(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        (output / "SKILL.md").write_text("tampered\n", encoding="utf-8")
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError,
                "do not match the SHA-256 manifest"):
            BUILDER_MODULE.verify_distribution_manifest(output)

    def test_manifest_verifier_is_read_only_compatible_with_v1(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        path = output / "distribution-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["schema_version"] = "1.0"
        for key in (
            "profile", "capability_ceiling", "capabilities", "catalog_sha256",
            "profile_definition_sha256", "package_ceiling",
        ):
            manifest.pop(key)
        path.write_bytes(BUILDER_MODULE.canonical_json(manifest))
        verified = BUILDER_MODULE.verify_distribution_manifest(output)
        self.assertEqual("1.0", verified["schema_version"])
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "has no profile identity"):
            BUILDER_MODULE.verify_distribution_manifest(
                output, expected_profile="lite",
            )

    def test_manifest_profile_and_ceiling_are_enforced(self):
        output = self.build("--plugin", "--profile", "lite")
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "profile does not match"):
            BUILDER_MODULE.verify_distribution_manifest(
                output, expected_profile="pro",
            )
        path = output / "distribution-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["package_ceiling"]["max_files"] = 1
        path.write_bytes(BUILDER_MODULE.canonical_json(manifest))
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "exceeds package ceiling"):
            BUILDER_MODULE.verify_distribution_manifest(output)

    def test_cli_verifies_manifest_and_bound_source_provenance(self):
        commit = "1" * 40
        output = self.build(
            "--skill", "narrative/evaluate/narrative-quality-auditor",
            "--source-repository", "owner/repository",
            "--source-commit", commit,
        )
        manifest = json.loads(
            (output / "distribution-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {"repository": "owner/repository", "commit": commit},
            manifest["source"],
        )
        result = subprocess.run(
            [
                sys.executable, str(BUILDER), "--verify-manifest", str(output),
                "--source-repository", "owner/repository", "--source-commit", commit,
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("verified standalone-skill distribution", result.stdout)

        wrong = subprocess.run(
            [
                sys.executable, str(BUILDER), "--verify-manifest", str(output),
                "--source-repository", "owner/repository", "--source-commit", "2" * 40,
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(0, wrong.returncode)
        self.assertIn("source provenance does not match", wrong.stderr)

    def test_source_provenance_must_be_complete(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable, str(BUILDER), "--output", str(Path(temporary) / "out"),
                    "--skill", "narrative/evaluate/narrative-quality-auditor",
                    "--source-repository", "owner/repository",
                ],
                cwd=ROOT, capture_output=True, text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must be supplied together", result.stderr)


if __name__ == "__main__":
    unittest.main()
