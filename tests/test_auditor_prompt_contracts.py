from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "scripts" / "generate-auditor-prompt-contracts.py"
SYSTEM_CATALOG_PATH = ROOT / "references" / "system-catalog.json"
FRAMEWORK_CATALOG_PATH = ROOT / "references" / "framework-catalog.json"
CONTRACT_SCHEMA_PATH = ROOT / "references" / "auditor-prompt-contract.schema.json"
INDEX_SCHEMA_PATH = ROOT / "references" / "auditor-prompt-contract-index.schema.json"
INDEX_PATH = ROOT / "references" / "prompt-contracts" / "index.json"
VARIANT_IDS = [
    "complete",
    "missing-evidence",
    "single-veto",
    "multi-veto",
    "persistence-authority",
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_version(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r'^version:\s*["\']?([^"\'\s]+)["\']?\s*$', text, re.MULTILINE)
    if match is None:
        raise AssertionError("missing skill version: %s" % path)
    return match.group(1)


def qualify(framework, item_id):
    prefix = framework + "-"
    return item_id if item_id.startswith(prefix) else prefix + item_id


class AuditorPromptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = load_json(SYSTEM_CATALOG_PATH)
        cls.frameworks = load_json(FRAMEWORK_CATALOG_PATH)
        cls.index = load_json(INDEX_PATH)
        spec = importlib.util.spec_from_file_location("auditor_prompt_contract_generator", GENERATOR_PATH)
        cls.generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.generator)

    def contracts(self):
        for entry in self.index["contracts"]:
            yield entry, load_json(ROOT / entry["ref"])

    def test_checked_projection_is_current_and_deterministic(self):
        result = subprocess.run(
            [sys.executable, str(GENERATOR_PATH), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("8 contracts, 40 variants", result.stdout)
        first = self.generator.build_outputs()
        second = self.generator.build_outputs()
        self.assertEqual(first, second)

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_numbers(self):
        cases = (
            (b'{"outer": {"value": 1, "value": 2}}', "duplicate JSON key"),
            (b'{"value": NaN}', "non-finite JSON number NaN"),
            (b'{"value": Infinity}', "non-finite JSON number Infinity"),
            (b'{"value": -Infinity}', "non-finite JSON number -Infinity"),
            (b'{"value": 1e400}', "non-finite JSON number 1e400"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = root / "catalog.json"
            with mock.patch.object(self.generator, "ROOT", root):
                for content, message in cases:
                    with self.subTest(content=content):
                        catalog.write_bytes(content)
                        with self.assertRaisesRegex(
                                self.generator.GenerationError, message):
                            self.generator.load_json("catalog.json")
        with self.assertRaisesRegex(
                self.generator.GenerationError, "Out of range float values"):
            self.generator.canonical_json({"value": float("nan")})

    def test_build_reads_each_bound_source_once_and_hashes_that_snapshot(self):
        reads = Counter()
        real_read = self.generator.safe_read_bytes

        def changing_source(relative):
            reads[relative] += 1
            content = real_read(relative)
            if reads[relative] > 1:
                return content + b"\nconcurrent replacement"
            return content

        with mock.patch.object(
                self.generator, "safe_read_bytes", side_effect=changing_source):
            outputs = self.generator.build_outputs()

        expected_sources = {
            self.generator.SYSTEM_CATALOG_REF,
            self.generator.FRAMEWORK_CATALOG_REF,
            self.generator.CONTRACT_SCHEMA_REF,
        }
        for auditor in self.system["auditors"]:
            expected_sources.add(auditor["path"] + "/SKILL.md")
            expected_sources.update(auditor["runtime_sources"])
        self.assertEqual(set(reads), expected_sources)
        self.assertTrue(all(count == 1 for count in reads.values()), reads)

        index = json.loads(
            outputs["references/prompt-contracts/index.json"].decode("utf-8")
        )
        self.assertEqual(index["source_catalog"]["sha256"], sha256(SYSTEM_CATALOG_PATH))
        self.assertEqual(
            index["framework_catalog"]["sha256"], sha256(FRAMEWORK_CATALOG_PATH)
        )
        for entry in index["contracts"]:
            contract = json.loads(outputs[entry["ref"]].decode("utf-8"))
            self.assertEqual(
                contract["source_catalog"]["sha256"], sha256(SYSTEM_CATALOG_PATH)
            )
            for source in contract["gate"]["runtime_sources"]:
                self.assertEqual(source["sha256"], sha256(ROOT / source["path"]))

    def test_safe_source_read_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as repository, tempfile.TemporaryDirectory() as external:
            root = Path(repository)
            outside = Path(external) / "runtime.md"
            outside.write_bytes(b"external")
            (root / "runtime.md").symlink_to(outside)
            with mock.patch.object(self.generator, "ROOT", root):
                with self.assertRaises(self.generator.GenerationError):
                    self.generator.safe_read_bytes("runtime.md")

    def test_atomic_write_rejects_symlink_parent_without_external_write(self):
        with tempfile.TemporaryDirectory() as repository, tempfile.TemporaryDirectory() as external:
            root = Path(repository)
            outside = Path(external)
            (root / "references").mkdir()
            (root / "references" / "prompt-contracts").symlink_to(
                outside, target_is_directory=True
            )
            outside_target = outside / "index.json"
            outside_target.write_bytes(b"external-original")
            target = root / "references" / "prompt-contracts" / "index.json"
            with mock.patch.object(self.generator, "ROOT", root):
                with self.assertRaises(self.generator.GenerationError):
                    self.generator.atomic_write(target, b"generated")
            self.assertEqual(outside_target.read_bytes(), b"external-original")

    def test_atomic_write_preserves_existing_permissions(self):
        with tempfile.TemporaryDirectory() as repository:
            root = Path(repository)
            target = root / "generated" / "contract.json"
            target.parent.mkdir()
            target.write_bytes(b"old")
            target.chmod(0o640)
            with mock.patch.object(self.generator, "ROOT", root):
                self.generator.atomic_write(target, b"new")
            self.assertEqual(target.read_bytes(), b"new")
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_index_has_exact_catalog_order_and_hashes(self):
        auditors = self.system["auditors"]
        entries = self.index["contracts"]
        self.assertEqual(self.index["contract_count"], 8)
        self.assertEqual(self.index["variant_count"], 40)
        self.assertEqual(len(entries), 8)
        self.assertEqual([entry["skill"] for entry in entries], [item["skill"] for item in auditors])
        self.assertEqual([entry["framework"] for entry in entries], [item["framework"] for item in auditors])
        self.assertEqual(len({entry["ref"] for entry in entries}), 8)
        for entry in entries:
            path = ROOT / entry["ref"]
            self.assertTrue(path.is_file())
            self.assertEqual(entry["sha256"], sha256(path))
            self.assertEqual(entry["evaluation_variant_count"], 5)
            self.assertEqual(entry["evaluation_variant_ids"], VARIANT_IDS)

    def test_contract_identity_and_runtime_sources_come_from_system_catalog(self):
        by_skill = {item["skill"]: item for item in self.system["auditors"]}
        system_hash = sha256(SYSTEM_CATALOG_PATH)
        framework_hash = sha256(FRAMEWORK_CATALOG_PATH)
        for entry, contract in self.contracts():
            declared = by_skill[entry["skill"]]
            skill_path = ROOT / declared["path"] / "SKILL.md"
            self.assertEqual(contract["contract_id"], "auditor-gate:" + declared["skill"])
            self.assertEqual(contract["skill"]["name"], declared["skill"])
            self.assertEqual(contract["skill"]["path"], declared["path"] + "/SKILL.md")
            self.assertEqual(contract["skill"]["version"], skill_version(skill_path))
            self.assertEqual(contract["skill"]["sha256"], sha256(skill_path))
            self.assertEqual(entry["skill_version"], contract["skill"]["version"])
            self.assertEqual(entry["skill_sha256"], contract["skill"]["sha256"])
            self.assertEqual(contract["gate"]["framework"], declared["framework"])
            self.assertEqual(contract["gate"]["sink"], declared["sink"])
            self.assertEqual(
                [source["path"] for source in contract["gate"]["runtime_sources"]],
                declared["runtime_sources"],
            )
            for source in contract["gate"]["runtime_sources"]:
                self.assertEqual(source["sha256"], sha256(ROOT / source["path"]))
            self.assertEqual(
                contract["source_catalog"],
                {
                    "path": "references/system-catalog.json",
                    "version": self.system["architecture_version"],
                    "sha256": system_hash,
                },
            )
            self.assertEqual(contract["framework_contract"]["catalog_version"], self.frameworks["catalog_version"])
            self.assertEqual(contract["framework_contract"]["catalog_sha256"], framework_hash)

    def test_framework_inputs_profiles_and_vetoes_are_typed_projections(self):
        for _, contract in self.contracts():
            framework_name = contract["gate"]["framework"]
            declared = self.frameworks["frameworks"][framework_name]
            projected = contract["framework_contract"]
            qualified = [qualify(framework_name, item_id) for item_id in declared["veto_items"]]
            self.assertEqual(projected["profiles"], list(declared["profiles"]))
            self.assertEqual(projected["required_context"], declared["required_context"])
            self.assertEqual(projected["qualified_veto_ids"], qualified)
            self.assertEqual(contract["prompt"]["input_contract"]["allowed_profiles"], list(declared["profiles"]))
            self.assertEqual(contract["prompt"]["input_contract"]["required_context"], declared["required_context"])
            self.assertEqual(contract["prompt"]["output_contract"]["qualified_veto_ids"], qualified)
            for item_id in qualified:
                self.assertTrue(item_id.startswith(framework_name + "-"), item_id)

    def test_exactly_forty_runner_ready_semantic_variants(self):
        variants = []
        for entry, contract in self.contracts():
            current = contract["evaluation_variants"]
            variants.extend(current)
            self.assertEqual([item["id"] for item in current], VARIANT_IDS)
            self.assertEqual(entry["evaluation_variant_ids"], VARIANT_IDS)
            for item in current:
                self.assertEqual(set(item), {"id", "input", "expected", "semantic_case"})
                self.assertEqual(
                    set(item["semantic_case"]),
                    {"scenario", "input_summary", "expected_behavior", "failure_modes"},
                )
                self.assertTrue(item["semantic_case"]["scenario"])
                self.assertTrue(item["semantic_case"]["input_summary"])
                self.assertGreaterEqual(len(item["semantic_case"]["expected_behavior"]), 1)
                self.assertGreaterEqual(len(item["semantic_case"]["failure_modes"]), 1)
        self.assertEqual(len(variants), 40)

    def test_variant_semantics_match_scoring_and_authority_contract(self):
        for _, contract in self.contracts():
            framework = contract["gate"]["framework"]
            vetoes = contract["framework_contract"]["qualified_veto_ids"]
            variants = {item["id"]: item for item in contract["evaluation_variants"]}

            complete = variants["complete"]
            self.assertEqual(complete["input"]["verified_veto_ids"], [])
            self.assertEqual(complete["expected"]["score_state"], "SCORED")
            self.assertEqual(complete["expected"]["final_score_policy"], "equals-raw")

            missing = variants["missing-evidence"]
            self.assertEqual(missing["input"]["evidence_coverage"], "incomplete")
            self.assertEqual(missing["expected"]["missing_evidence_state"], "unknown")
            self.assertEqual(missing["expected"]["status_any_of"], ["NEEDS_INPUT"])
            self.assertEqual(missing["expected"]["verdict_any_of"], ["UNDECIDED"])
            self.assertEqual(missing["expected"]["raw_score_policy"], "omit")

            single = variants["single-veto"]
            self.assertEqual(single["input"]["verified_veto_ids"], vetoes[:1])
            self.assertEqual(single["expected"]["cap_applied"], True)
            self.assertEqual(single["expected"]["final_score_policy"], "cap-at-59")
            self.assertEqual(single["expected"]["verdict_any_of"], ["FIX"])

            multi = variants["multi-veto"]
            self.assertEqual(multi["input"]["verified_veto_ids"], vetoes[:2])
            self.assertEqual(multi["expected"]["verdict_any_of"], ["BLOCK"])
            self.assertEqual(multi["expected"]["final_score_policy"], "omit")
            self.assertTrue(all(item.startswith(framework + "-") for item in multi["input"]["verified_veto_ids"]))

            persistence = variants["persistence-authority"]
            self.assertEqual(persistence["input"]["persistence_requested"], True)
            self.assertEqual(persistence["input"]["persistence_authorized"], False)
            self.assertEqual(
                persistence["expected"]["persistence_action"],
                "deny-and-request-explicit-authorization",
            )
            self.assertEqual(contract["prompt"]["authority"]["persistence_requires_explicit_authorization"], True)
            self.assertEqual(contract["prompt"]["authority"]["persistence_sink"], contract["gate"]["sink"])

    def test_contract_and_index_schemas_close_every_object_shape(self):
        def walk(node, location):
            if isinstance(node, dict):
                if node.get("type") == "object":
                    self.assertIs(
                        node.get("additionalProperties"),
                        False,
                        "open object schema at %s" % location,
                    )
                for key, value in node.items():
                    walk(value, "%s/%s" % (location, key))
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, "%s/%d" % (location, index))

        contract_schema = load_json(CONTRACT_SCHEMA_PATH)
        index_schema = load_json(INDEX_SCHEMA_PATH)
        walk(contract_schema, "contract")
        walk(index_schema, "index")
        self.assertEqual(self.index["contract_schema"]["sha256"], sha256(CONTRACT_SCHEMA_PATH))

    def test_contract_shapes_have_no_undeclared_projection_fields(self):
        contract_keys = {
            "$schema", "schema_version", "contract_id", "contract_kind",
            "source_catalog", "skill", "gate", "framework_contract", "prompt",
            "evaluation_variants",
        }
        for _, contract in self.contracts():
            self.assertEqual(set(contract), contract_keys)
            self.assertEqual(set(contract["source_catalog"]), {"path", "version", "sha256"})
            self.assertEqual(set(contract["skill"]), {"name", "path", "version", "sha256"})
            self.assertEqual(set(contract["gate"]), {"framework", "runtime_sources", "sink"})
            self.assertEqual(
                set(contract["prompt"]),
                {"role", "input_contract", "directives", "execution_steps", "output_contract", "authority"},
            )

    def test_generator_does_not_hardcode_auditor_identities(self):
        source = GENERATOR_PATH.read_text(encoding="utf-8")
        for auditor in self.system["auditors"]:
            self.assertNotIn('"%s"' % auditor["skill"], source)


if __name__ == "__main__":
    unittest.main()
