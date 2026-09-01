"""Central cross-discipline control binding and projection tests."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_skill_contracts_control_bindings",
    ROOT / "scripts" / "generate-skill-contracts.py",
)
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class ControlBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(
            (ROOT / generator.CATALOG_REF).read_text(encoding="utf-8")
        )
        cls.ordered = generator.catalog_skill_paths(cls.catalog)
        cls.binding_document = json.loads(
            (ROOT / generator.CONTROL_BINDINGS_REF).read_text(encoding="utf-8")
        )

    def test_bindings_equal_the_authored_control_profile_closure(self):
        bindings, source = generator.load_control_bindings(ROOT, self.ordered)
        influencer = {
            skill for skill, _path, discipline, _phase in self.ordered
            if discipline == "influencer"
        }
        profile_markers = {
            "measurement-control.md",
            "send-control.md",
            "action-control.md",
            "stimulus-binding.md",
            "evidence-and-cycle-control.md",
            "human-action-control.md",
        }
        authored_profiles = set()
        for skill, skill_dir, discipline, _phase in self.ordered:
            if discipline == "influencer":
                continue
            text = (ROOT / skill_dir / "SKILL.md").read_text(encoding="utf-8")
            if any(marker in text for marker in profile_markers):
                authored_profiles.add(skill)
        self.assertEqual(influencer | authored_profiles, set(bindings))
        self.assertEqual(49, len(bindings))
        self.assertEqual(generator.CONTROL_BINDINGS_REF, source["path"])
        self.assertEqual(64, len(source["sha256"]))

    def test_generated_contracts_project_binding_or_explicit_empty_array(self):
        bindings, source = generator.load_control_bindings(ROOT, self.ordered)
        contracts = generator.build_contracts(ROOT)
        self.assertEqual(120, len(contracts))
        for contract in contracts:
            skill = contract["identity"]["name"]
            self.assertEqual(bindings.get(skill, []), contract["control_requirements"])
            if skill in bindings:
                provenance = contract["provenance"]["control_bindings"]
                self.assertEqual(source["path"], provenance["path"])
                self.assertEqual(source["sha256"], provenance["sha256"])
                self.assertEqual({"path", "sha256"}, set(provenance))
            else:
                self.assertNotIn("control_bindings", contract["provenance"])

    def test_empty_binding_set_is_valid_but_stale_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / generator.CONTROL_BINDINGS_REF
            target.parent.mkdir(parents=True)
            empty = copy.deepcopy(self.binding_document)
            empty["bindings"] = {}
            empty.pop("handoff_requirements", None)
            target.write_text(json.dumps(empty), encoding="utf-8")
            bindings, _source = generator.load_control_bindings(root, self.ordered)
            self.assertEqual({}, bindings)

            stale = copy.deepcopy(self.binding_document)
            stale["bindings"]["campaign-planner"]["skill_path"] = (
                "influencer/scout/campaign-planner/SKILL.md"
            )
            target.write_text(json.dumps(stale), encoding="utf-8")
            with self.assertRaisesRegex(
                    generator.ContractGenerationError, "path differs"):
                generator.load_control_bindings(root, self.ordered)

    def test_handoff_requirements_are_nonempty_sorted_and_source_producible(self):
        handoffs = self.binding_document["handoff_requirements"]
        self.assertTrue(handoffs)
        observed = set()
        for edge_id, requirements in handoffs.items():
            source, target = edge_id.split("--", 1)
            self.assertTrue(source)
            self.assertTrue(target)
            self.assertEqual(sorted(requirements), requirements)
            self.assertEqual(len(requirements), len(set(requirements)))
            self.assertTrue(
                set(requirements)
                <= set(self.binding_document["bindings"][source]["control_requirements"])
            )
            observed.update(requirements)
        self.assertEqual(generator.CONTROL_REQUIREMENTS, observed)

    def test_email_and_social_control_handoffs_use_native_consumers(self):
        handoffs = self.binding_document["handoff_requirements"]
        self.assertIn(
            "send-experiment-designer--email-quality-auditor", handoffs
        )
        self.assertNotIn(
            "send-experiment-designer--performance-analyzer", handoffs
        )
        self.assertIn(
            "social-measurement-loop--social-quality-auditor", handoffs
        )
        self.assertNotIn(
            "social-measurement-loop--report-generator", handoffs
        )

    def test_handoff_requirements_fail_closed_on_order_duplicates_and_enum(self):
        edge_id = "campaign-planner--performance-analyzer"
        mutations = []

        unsorted = copy.deepcopy(self.binding_document)
        unsorted["handoff_requirements"][edge_id] = list(reversed(
            unsorted["handoff_requirements"][edge_id]
        ))
        mutations.append(unsorted)

        duplicated = copy.deepcopy(self.binding_document)
        duplicated["handoff_requirements"][edge_id].append(
            duplicated["handoff_requirements"][edge_id][-1]
        )
        mutations.append(duplicated)

        unknown = copy.deepcopy(self.binding_document)
        unknown["handoff_requirements"][edge_id] = ["unknown-control"]
        mutations.append(unknown)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / generator.CONTROL_BINDINGS_REF
            target.parent.mkdir(parents=True)
            for document in mutations:
                with self.subTest(document=document["handoff_requirements"][edge_id]):
                    target.write_text(json.dumps(document), encoding="utf-8")
                    with self.assertRaisesRegex(
                            generator.ContractGenerationError,
                            "requirements are invalid or not sorted"):
                        generator.load_control_bindings(root, self.ordered)

    def test_control_enum_is_identical_across_closed_surfaces(self):
        binding_schema = json.loads(
            (ROOT / "references/control-bindings.schema.json").read_text(
                encoding="utf-8"
            )
        )
        machine_schema = json.loads(
            (ROOT / "references/skill-machine-contract.schema.json").read_text(
                encoding="utf-8"
            )
        )
        capsule_schema = json.loads(
            (ROOT / "references/skill-capsule.schema.json").read_text(
                encoding="utf-8"
            )
        )
        expected = generator.CONTROL_REQUIREMENTS
        self.assertEqual(
            expected,
            set(binding_schema["$defs"]["controlRequirement"]["enum"]),
        )
        self.assertEqual(
            expected,
            set(machine_schema["$defs"]["controlRequirement"]["enum"]),
        )
        self.assertEqual(
            expected,
            set(capsule_schema["$defs"]["controlRequirement"]["enum"]),
        )

    def test_first_release_reuses_artifact_validation_without_new_run_events(self):
        run_schema = json.loads(
            (ROOT / "references/run-event.schema.json").read_text(encoding="utf-8")
        )
        event_types = set(run_schema["properties"]["event_type"]["enum"])
        self.assertIn("artifact_validated", event_types)
        self.assertTrue(generator.CONTROL_REQUIREMENTS.isdisjoint(event_types))


if __name__ == "__main__":
    unittest.main()
