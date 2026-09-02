import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate-router-facades.py"
SPEC = importlib.util.spec_from_file_location("router_facades_under_test", GENERATOR)
router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(router)


class RouterFacadeTests(unittest.TestCase):
    @staticmethod
    def catalog_names(catalog):
        names = []
        for discipline in catalog["logical_order"]:
            if discipline == "protocol":
                names.extend(catalog["protocol"]["skills"])
                continue
            spec = catalog["disciplines"][discipline]
            for phase in spec["phase_order"]:
                names.extend(spec["phases"][phase])
        return names

    def test_outputs_are_deterministic_and_partition_all_120_once(self):
        first = router.build_outputs(ROOT)
        second = router.build_outputs(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(9, len(first))
        manifest = json.loads(first[router.SIDECAR_REF])
        self.assertEqual(
            router.compact_json(manifest), first[router.SIDECAR_REF]
        )
        self.assertEqual(8, manifest["facade_count"])
        self.assertEqual(120, manifest["canonical_business_skill_count"])
        self.assertEqual(
            [
                "narrative", "seo-geo", "social", "email", "ad",
                "influencer", "launch", "protocol",
            ],
            [item["discipline"] for item in manifest["facades"]],
        )
        targets = [
            target
            for facade in manifest["facades"]
            for target in facade["targets"]
        ]
        names = [target["name"] for target in targets]
        catalog = json.loads((ROOT / router.SYSTEM_CATALOG_REF).read_text())
        self.assertEqual(self.catalog_names(catalog), names)
        self.assertEqual(120, len(names))
        self.assertEqual(120, len(set(names)))
        self.assertEqual(
            hashlib.sha256(router.canonical_json(targets)).hexdigest(),
            manifest["coverage_sha256"],
        )
        for facade in manifest["facades"]:
            content = first[facade["path"]]
            self.assertEqual(hashlib.sha256(content).hexdigest(), facade["sha256"])
            self.assertEqual(len(facade["targets"]), facade["target_count"])
            text = content.decode("utf-8")
            self.assertIn("canonical_business_skill\":false", text)
            self.assertIn("does not execute domain work", text)
            self.assertIn("Before selecting, read every plausible target", text)
            self.assertNotIn("  - Boundary:", text)
            self.assertNotIn("  - Route when:", text)

    def test_facades_are_not_canonical_plugin_or_catalog_skills(self):
        outputs = router.build_outputs(ROOT)
        manifest = json.loads(outputs[router.SIDECAR_REF])
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        plugin_paths = {value.removeprefix("./") + "/SKILL.md" for value in plugin["skills"]}
        catalog = json.loads((ROOT / router.SYSTEM_CATALOG_REF).read_text())
        self.assertEqual(120, catalog["counts"]["total_skills"])
        for facade in manifest["facades"]:
            self.assertNotIn(facade["path"], plugin_paths)
            self.assertTrue(facade["path"].startswith("router-facades/"))

    def test_non_router_host_profile_is_rejected(self):
        with self.assertRaisesRegex(
                router.RouterFacadeError, "does not select router-skills"):
            router.build_outputs(ROOT, "claude-code-plugin-host")

    def test_target_hashes_bind_the_actual_business_skill_files(self):
        outputs = router.build_outputs(ROOT)
        sidecar = json.loads(outputs[router.SIDECAR_REF])
        facade_contents = {
            facade["path"]: outputs[facade["path"]]
            for facade in sidecar["facades"]
        }
        target_contents = {
            target["path"]: (ROOT / target["path"]).read_bytes()
            for facade in sidecar["facades"]
            for target in facade["targets"]
        }
        router.validate_sidecar(
            sidecar, facade_contents, target_contents=target_contents,
        )
        first_path = next(iter(target_contents))
        target_contents[first_path] += b"\ntampered\n"
        with self.assertRaisesRegex(
                router.RouterFacadeError, "target hash is invalid"):
            router.validate_sidecar(
                sidecar, facade_contents, target_contents=target_contents,
            )

    def test_duplicate_or_missing_catalog_targets_fail_closed(self):
        catalog = json.loads((ROOT / router.SYSTEM_CATALOG_REF).read_text())
        duplicate = copy.deepcopy(catalog)
        duplicate["disciplines"]["narrative"]["phases"]["trace"][1] = (
            duplicate["disciplines"]["narrative"]["phases"]["trace"][0]
        )
        with self.assertRaisesRegex(router.RouterFacadeError, "target list|more than once"):
            router.catalog_groups(ROOT, duplicate)

        missing = copy.deepcopy(catalog)
        missing["disciplines"]["narrative"]["phases"]["trace"][0] = "missing-skill"
        with self.assertRaisesRegex(router.RouterFacadeError, "cannot read"):
            router.catalog_groups(ROOT, missing)

    def test_host_catalog_surface_capabilities_fail_closed(self):
        host = json.loads((ROOT / router.HOST_PROFILES_REF).read_text())
        malformed = copy.deepcopy(host)
        malformed["profiles"]["generic-shared-root-host"]["capabilities"].remove(
            "router-skills"
        )
        with self.assertRaisesRegex(router.RouterFacadeError, "routing surface"):
            router.validate_host_profiles(malformed)


if __name__ == "__main__":
    unittest.main()
