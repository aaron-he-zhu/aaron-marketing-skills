import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_skill_contracts", ROOT / "scripts" / "generate-skill-contracts.py"
)
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class SkillMachineContractTests(unittest.TestCase):
    @staticmethod
    def load(relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_generated_artifacts_are_current_and_cover_catalog_120_of_120(self):
        outputs = generator.build_outputs(ROOT)
        self.assertEqual(generator.check_outputs(outputs, ROOT), [])
        index = self.load(generator.INDEX_REF)
        self.assertEqual(index["contract_count"], 120)
        self.assertEqual(len(index["contracts"]), 120)
        self.assertEqual(len({entry["skill"] for entry in index["contracts"]}), 120)
        self.assertEqual(set(outputs), {
            generator.INDEX_REF,
            *(entry["contract_ref"] for entry in index["contracts"]),
        })

    def test_every_contract_binds_live_skill_and_authored_contract_fields(self):
        index = self.load(generator.INDEX_REF)
        fallback_triggers = 0
        fallback_outputs = 0
        shared_handoffs = 0
        unclassified_dimensions = 0
        for entry in index["contracts"]:
            path = ROOT / entry["contract_ref"]
            raw = path.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["contract_sha256"])
            contract = json.loads(raw)
            identity = contract["identity"]
            self.assertEqual(identity["name"], entry["skill"])
            self.assertEqual(
                hashlib.sha256((ROOT / identity["path"]).read_bytes()).hexdigest(),
                identity["sha256"],
            )
            for field in (
                    contract["routing_contract"]["trigger_phrases"],
                    contract["routing_contract"]["boundary"],
                    contract["input_contract"]["reads"],
                    contract["output_contract"]["writes"],
                    contract["completion_contract"]["done_when"],
                    contract["handoff_contract"]["next_best"],
                    contract["handoff_contract"]["target_skills"]):
                self.assertTrue(field)
            structured = (
                (contract["input_contract"], "reads", "clauses"),
                (contract["output_contract"], "writes", "clauses"),
                (contract["completion_contract"], "done_when", "clauses"),
                (contract["handoff_contract"], "next_best", "items"),
            )
            for projection, display_key, items_key in structured:
                self.assertIn(
                    projection["extraction_status"],
                    {"classified", "partially-classified", "unclassified"},
                )
                self.assertTrue(projection[items_key])
                display = projection[display_key]
                for item in projection[items_key]:
                    source = item["source"]
                    self.assertEqual(source["span_basis"], "field-text")
                    self.assertEqual(
                        display[source["start_char"]:source["end_char"]], item["text"]
                    )
                    unclassified_dimensions += sum(
                        value == "unclassified" for key, value in item.items()
                        if key in {
                            "kind", "requirement", "side_effect", "permission_posture"
                        }
                    )
            fallback_triggers += (
                contract["routing_contract"]["trigger_source"] == "when-to-use-fallback"
            )
            fallback_outputs += contract["output_contract"]["summary_source"] == "writes-fallback"
            shared_handoffs += (
                contract["handoff_contract"]["summary_source"] == "shared-skill-contract"
            )
        self.assertEqual(fallback_triggers, 6)
        self.assertEqual(fallback_outputs, 33)
        self.assertEqual(shared_handoffs, 8)
        self.assertGreater(unclassified_dimensions, 0)

    def test_runtime_required_bundle_references_are_explicit_and_closed(self):
        index = self.load(generator.INDEX_REF)
        required = []
        for entry in index["contracts"]:
            contract = self.load(entry["contract_ref"])
            for reference in contract["context_hints"]["bundle_references"]:
                if reference["requirement"] == "required":
                    required.append((entry["skill"], reference))
        self.assertEqual(len(required), 63)
        self.assertEqual(len({skill for skill, _reference in required}), 19)
        self.assertTrue(all(
            reference["reason_code"] == "explicit-runtime-read"
            for _skill, reference in required
        ))
        self.assertFalse(any(
            reference["path"] == "CONNECTORS.md"
            for _skill, reference in required
        ))

    def test_ambiguous_clauses_remain_explicitly_unclassified(self):
        reads = generator.input_clauses(
            "market context and priorities", "fixture/SKILL.md", "0" * 64
        )
        self.assertEqual(reads[0]["kind"], "unclassified")
        self.assertEqual(reads[0]["requirement"], "unclassified")
        self.assertEqual(reads[0]["extraction_status"], "unclassified")
        writes = generator.output_clauses(
            "a concise recommendation", "fixture/SKILL.md", "0" * 64
        )
        self.assertEqual(writes[0]["side_effect"], "unclassified")
        self.assertEqual(writes[0]["permission_posture"], "unclassified")
        self.assertEqual(writes[0]["extraction_status"], "unclassified")

    def test_detected_side_effects_inherit_shared_permission_boundary(self):
        fixtures = (
            ("report to memory/example/report.md", "project-write"),
            ("proposal through registry-events.py", "registry-proposal"),
            ("send the approved message", "external-mutation"),
        )
        for value, side_effect in fixtures:
            with self.subTest(value=value):
                clause = generator.output_clauses(
                    value, "fixture/SKILL.md", "0" * 64
                )[0]
                self.assertEqual(side_effect, clause["side_effect"])
                self.assertEqual(
                    "permission-required", clause["permission_posture"]
                )
                self.assertEqual("classified", clause["extraction_status"])

    def test_shared_max_depth_stop_preserves_one_user_controlled_successor(self):
        shared = (ROOT / "references/skill-contract.md").read_text(encoding="utf-8")
        self.assertIn("allow at most three automatic handoffs", shared)
        self.assertIn("handoff budget is the only stop", shared)
        self.assertIn("name that one skill", shared)
        self.assertIn("`recommended_next_skill`", shared)
        self.assertIn("record the exhausted budget and visited chain", shared)
        self.assertIn("`open_loops`", shared)
        self.assertIn("do not replace it with `none`", shared)

    def test_shared_write_authority_overrides_local_destination_language(self):
        shared = (ROOT / "references/skill-contract.md").read_text(encoding="utf-8")
        self.assertIn("cross-skill authority boundary", shared)
        self.assertIn("takes precedence over any skill-local imperative", shared)
        self.assertIn("never creates authorization", shared)
        self.assertIn("request fresh exact permission rather than transferring consent", shared)
        for token in ("write", "save", "submit", "append", "promote"):
            self.assertIn('"%s"' % token, shared)

    def test_shared_gate_ownership_forbids_decisive_non_auditor_results(self):
        shared = (ROOT / "references/skill-contract.md").read_text(encoding="utf-8")
        for token in (
            "apply **only** when the current target is one of the eight auditor-class skills",
            "potential control evidence",
            "must not instantiate a decisive auditor verdict",
            "A handoff or `Next Best Skill` link alone is never a request",
        ):
            self.assertIn(token, shared)

        paid = (ROOT / "ad/scale/paid-measurement-loop/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`readback_decision` is not an RQS auditor verdict", paid)
        self.assertIn("Call the observations potential control evidence, not verified vetoes", paid)
        self.assertIn("restore and verify the checkout conversion tag", paid)
        self.assertIn("de-duplicate cross-platform order IDs", paid)
        self.assertIn("The auditor is a separate invocation", paid)
        self.assertNotIn("per-change readback verdict", paid)

        paid_contract = self.load(
            "references/skill-contracts/paid-measurement-loop.json"
        )
        fit_contract = self.load("references/skill-contracts/fit-scorer.json")
        self.assertIn(
            "ad-account-auditor",
            paid_contract["handoff_contract"]["target_skills"],
        )
        self.assertIn(
            "creator-content-auditor",
            fit_contract["handoff_contract"]["target_skills"],
        )

    def test_clause_extraction_rejects_empty_source(self):
        with self.assertRaisesRegex(generator.ContractGenerationError, "no extractable clauses"):
            generator.clause_spans(" \n ; ", "fixture")

    def test_missing_required_markdown_contract_field_fails_closed(self):
        malformed = """
- **Reads**: evidence
- **Writes**: artifact
"""
        with self.assertRaisesRegex(generator.ContractGenerationError, "done when"):
            generator.contract_fields(malformed, "fixture/SKILL.md")

    def test_check_cli_reports_deterministically_current(self):
        first = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate-skill-contracts.py"), "--check"],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        second = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate-skill-contracts.py"), "--check"],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        self.assertEqual((first.returncode, first.stdout, first.stderr),
                         (second.returncode, second.stdout, second.stderr))
        self.assertEqual(first.returncode, 0, first.stderr)

    def test_check_detects_missing_generated_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = {"references/skill-contracts/example.json": b"{}\n"}
            self.assertEqual(
                generator.check_outputs(outputs, root),
                ["missing generated contract: references/skill-contracts/example.json"],
            )

    def test_only_closed_runtime_reads_declarations_make_references_required(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "skill").mkdir()
            (root / "references").mkdir()
            (root / "skill" / "SKILL.md").write_text("fixture\n", encoding="utf-8")
            (root / "references" / "required.md").write_text("required\n", encoding="utf-8")
            (root / "references" / "optional.md").write_text("optional\n", encoding="utf-8")
            body = """\
Read [the optional guide](../references/optional.md) before a read-only readout.

### Runtime Reads

- `../references/required.md`

### Instructions

The optional guide remains an authored reference even when prose says read.
"""
            references = generator.bundle_references(root, "skill/SKILL.md", body)
            by_path = {item["path"]: item for item in references}
            self.assertEqual(by_path["references/required.md"]["requirement"], "required")
            self.assertEqual(
                by_path["references/required.md"]["reason_code"],
                "explicit-runtime-read",
            )
            self.assertEqual(by_path["references/required.md"]["source_line"], 5)
            self.assertEqual(by_path["references/optional.md"]["requirement"], "optional")
            self.assertEqual(
                by_path["references/optional.md"]["reason_code"],
                "authored-reference",
            )

    def test_runtime_reads_section_rejects_prose_and_duplicate_sections(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "skill").mkdir()
            (root / "references").mkdir()
            (root / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
            malformed = """\
### Runtime Reads

Read `../references/guide.md` before continuing.
"""
            with self.assertRaisesRegex(
                    generator.ContractGenerationError, "invalid Runtime Reads entry"):
                generator.bundle_references(root, "skill/SKILL.md", malformed)

            duplicate = """\
### Runtime Reads
- `../references/guide.md`
### Instructions
Do work.
### Runtime Reads
- `../references/guide.md`
"""
            with self.assertRaisesRegex(
                    generator.ContractGenerationError, "more than one"):
                generator.bundle_references(root, "skill/SKILL.md", duplicate)

    def test_runtime_reads_heading_inside_code_fence_has_no_control_semantics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "skill").mkdir()
            (root / "references").mkdir()
            (root / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
            body = """\
```markdown
### Runtime Reads
- `../references/guide.md`
```
"""
            references = generator.bundle_references(root, "skill/SKILL.md", body)
            self.assertEqual(len(references), 1)
            self.assertEqual(references[0]["requirement"], "optional")

    def test_runtime_reads_heading_inside_indented_code_has_no_control_semantics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "skill").mkdir()
            (root / "references").mkdir()
            (root / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
            body = """\
    ### Runtime Reads
    - `../references/guide.md`
"""
            references = generator.bundle_references(root, "skill/SKILL.md", body)
            self.assertEqual(len(references), 1)
            self.assertEqual(references[0]["requirement"], "optional")


if __name__ == "__main__":
    unittest.main()
