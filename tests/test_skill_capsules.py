import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-skill-capsules.py"
SPEC = importlib.util.spec_from_file_location("generate_skill_capsules", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_link_parts(raw):
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    path, separator, fragment = target.partition("#")
    if not path or URI_SCHEME.match(path):
        return None
    return path, fragment if separator else None


def projected_strings(value, path=()):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from projected_strings(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from projected_strings(item, path + (index,))


class SkillCapsuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_path = ROOT / "references" / "skill-capsules" / "index.json"
        cls.index = json.loads(cls.index_path.read_text(encoding="utf-8"))
        cls.contract_index = json.loads(
            (ROOT / "references" / "skill-contracts" / "index.json").read_text(
                encoding="utf-8"
            )
        )
        cls.contracts = {
            item["skill"]: item for item in cls.contract_index["contracts"]
        }

    def _assert_projected_links_preserve_targets(
            self, source_path, capsule_path, source_text, capsule_text, label):
        source_links = MARKDOWN_LINK.findall(source_text)
        capsule_links = MARKDOWN_LINK.findall(capsule_text)
        self.assertEqual(len(source_links), len(capsule_links), label)
        local_count = 0
        for source_raw, capsule_raw in zip(source_links, capsule_links):
            source_parts = local_link_parts(source_raw)
            capsule_parts = local_link_parts(capsule_raw)
            if source_parts is None:
                self.assertEqual(source_raw, capsule_raw, label)
                continue
            local_count += 1
            self.assertIsNotNone(capsule_parts, label)
            source_target, source_anchor = source_parts
            capsule_target, capsule_anchor = capsule_parts
            self.assertEqual(
                (source_path.parent / source_target).resolve(),
                (capsule_path.parent / capsule_target).resolve(),
                label,
            )
            self.assertEqual(source_anchor, capsule_anchor, label)
        self.assertGreater(local_count, 0, label)

    def test_generator_check_passes(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("120 skills", completed.stdout)

    def test_index_covers_every_machine_contract_once(self):
        entries = self.index["capsules"]
        names = [item["skill"] for item in entries]
        self.assertEqual(120, self.index["capsule_count"])
        self.assertEqual(120, len(entries))
        self.assertEqual(sorted(self.contracts), names)
        self.assertEqual(len(names), len(set(names)))

    def test_every_capsule_is_hash_anchored_to_live_sources(self):
        for item in self.index["capsules"]:
            skill = item["skill"]
            capsule_path = ROOT / item["capsule_ref"]
            self.assertEqual(item["capsule_sha256"], sha256(capsule_path), skill)
            self.assertEqual(item["model_bytes"], (
                capsule_path.stat().st_size
                + (ROOT / self.index["policy_kernel"]["path"]).stat().st_size
            ), skill)
            capsule = json.loads(capsule_path.read_text(encoding="utf-8"))
            source = capsule["provenance"]["source"]
            machine = capsule["provenance"]["machine_contract"]
            self.assertEqual(source["sha256"], sha256(ROOT / source["path"]), skill)
            self.assertEqual(machine["sha256"], sha256(ROOT / machine["path"]), skill)
            self.assertEqual(
                self.contracts[skill]["contract_sha256"], machine["sha256"], skill
            )

    def test_capsule_keeps_operations_but_removes_standard_harness_sections(self):
        omitted = MODULE.OMITTED_STANDARD_SECTIONS
        for item in self.index["capsules"]:
            capsule = json.loads((ROOT / item["capsule_ref"]).read_text(encoding="utf-8"))
            operational = capsule["execution"]["operational_markdown"]
            self.assertIn("## Instructions", operational, item["skill"])
            for title in omitted:
                self.assertIsNone(
                    re.search(r"(?m)^## %s\s*$" % re.escape(title), operational),
                    item["skill"],
                )

    def test_local_operational_links_are_rebased_closed_and_anchor_preserving(self):
        rendered = MODULE.render_all()
        capsule_count = 0
        local_link_count = 0
        for relative, raw in sorted(rendered.items()):
            if relative.endswith("/index.json"):
                continue
            capsule_count += 1
            capsule_path = ROOT / relative
            capsule = json.loads(raw.decode("utf-8"))
            source_path = ROOT / capsule["provenance"]["source"]["path"]
            source_markdown = MODULE._operational_markdown(
                source_path.read_text(encoding="utf-8")
            )
            source_links = MARKDOWN_LINK.findall(source_markdown)
            capsule_links = MARKDOWN_LINK.findall(
                capsule["execution"]["operational_markdown"]
            )
            self.assertEqual(len(source_links), len(capsule_links), relative)
            for source_raw, capsule_raw in zip(source_links, capsule_links):
                source_parts = local_link_parts(source_raw)
                capsule_parts = local_link_parts(capsule_raw)
                if source_parts is None:
                    self.assertEqual(source_raw, capsule_raw, relative)
                    continue
                local_link_count += 1
                self.assertIsNotNone(capsule_parts, relative)
                source_target, source_anchor = source_parts
                capsule_target, capsule_anchor = capsule_parts
                source_resolved = (source_path.parent / source_target).resolve()
                capsule_resolved = (capsule_path.parent / capsule_target).resolve()
                self.assertEqual(source_resolved, capsule_resolved, relative)
                self.assertEqual(source_anchor, capsule_anchor, relative)
                try:
                    source_resolved.relative_to(ROOT.resolve())
                except ValueError:
                    self.fail("%s link escapes repository: %s" % (relative, capsule_raw))
                self.assertTrue(source_resolved.exists(), (relative, capsule_raw))
        self.assertEqual(120, capsule_count)
        self.assertGreater(local_link_count, 500)

    def test_every_local_link_in_every_capsule_string_is_closed(self):
        rendered = MODULE.render_all()
        capsule_count = 0
        local_link_count = 0
        for relative, raw in sorted(rendered.items()):
            if relative.endswith("/index.json"):
                continue
            capsule_count += 1
            capsule_path = ROOT / relative
            capsule = json.loads(raw.decode("utf-8"))
            for field, text in projected_strings(capsule):
                for raw_target in MARKDOWN_LINK.findall(text):
                    parts = local_link_parts(raw_target)
                    if parts is None:
                        continue
                    local_link_count += 1
                    target, _anchor = parts
                    resolved = (capsule_path.parent / target).resolve()
                    try:
                        resolved.relative_to(ROOT.resolve())
                    except ValueError:
                        self.fail(
                            "%s.%s escapes repository: %s"
                            % (relative, ".".join(map(str, field)), raw_target)
                        )
                    self.assertTrue(
                        resolved.exists(),
                        (relative, ".".join(map(str, field)), raw_target),
                    )
        self.assertEqual(120, capsule_count)
        self.assertGreater(local_link_count, 1200)

    def test_reads_writes_and_done_when_links_use_skill_source_base(self):
        rendered = MODULE.render_all()
        cases = (
            ("audience-belief-mapper", "input_contract", "reads", "reads"),
            ("audience-belief-mapper", "output_contract", "writes", "writes"),
            (
                "message-test-designer", "completion_contract", "done_when",
                "done_when",
            ),
        )
        for skill, contract_section, contract_field, capsule_field in cases:
            with self.subTest(skill=skill, field=capsule_field):
                relative = "references/skill-capsules/%s.json" % skill
                capsule = json.loads(rendered[relative].decode("utf-8"))
                contract = json.loads(
                    (ROOT / self.contracts[skill]["contract_ref"]).read_text(
                        encoding="utf-8"
                    )
                )
                source_path = ROOT / contract["identity"]["path"]
                self._assert_projected_links_preserve_targets(
                    source_path,
                    ROOT / relative,
                    contract[contract_section][contract_field],
                    capsule["execution"][capsule_field],
                    "%s.%s" % (skill, capsule_field),
                )

    def test_handoff_condition_and_text_links_use_skill_source_base(self):
        rendered = MODULE.render_all()
        skill = "ad-creative-builder"
        relative = "references/skill-capsules/%s.json" % skill
        capsule = json.loads(rendered[relative].decode("utf-8"))
        contract = json.loads(
            (ROOT / self.contracts[skill]["contract_ref"]).read_text(encoding="utf-8")
        )
        source_path = ROOT / contract["identity"]["path"]
        source_item = contract["handoff_contract"]["items"][1]
        capsule_item = capsule["handoff"]["items"][1]
        for field in ("condition", "text"):
            self._assert_projected_links_preserve_targets(
                source_path,
                ROOT / relative,
                source_item[field],
                capsule_item[field],
                "%s.handoff.%s" % (skill, field),
            )

    def test_link_rebaser_rejects_escape_and_missing_targets(self):
        source = ROOT / "narrative/trace/narrative-baseline-mapper/SKILL.md"
        capsule = ROOT / "references/skill-capsules/test-only.json"
        rendered = MODULE._rebase_projected_markdown(
            "[policy](../../../SECURITY.md#reporting) "
            "[same](#mode-selector) [web](https://example.com/a#b)",
            source,
            capsule,
        )
        self.assertIn("[policy](../../SECURITY.md#reporting)", rendered)
        self.assertIn("[same](#mode-selector)", rendered)
        self.assertIn("[web](https://example.com/a#b)", rendered)
        with self.assertRaisesRegex(MODULE.CapsuleError, "escapes repository"):
            MODULE._rebase_projected_markdown(
                "[escape](../../../../../../outside.md)", source, capsule
            )
        with self.assertRaisesRegex(MODULE.CapsuleError, "does not exist"):
            MODULE._rebase_projected_markdown(
                "[missing](../../../definitely-missing.md)", source, capsule
            )

    def test_explicit_runtime_reads_are_preserved_exactly(self):
        skills_with_runtime_reads = 0
        for item in self.index["capsules"]:
            skill = item["skill"]
            capsule = json.loads((ROOT / item["capsule_ref"]).read_text(encoding="utf-8"))
            contract = json.loads(
                (ROOT / self.contracts[skill]["contract_ref"]).read_text(encoding="utf-8")
            )
            expected = [
                {"path": reference["path"], "sha256": reference["sha256"]}
                for reference in contract["context_hints"]["bundle_references"]
                if reference["requirement"] == "required"
            ]
            self.assertEqual(expected, capsule["runtime_reads"], skill)
            if expected:
                skills_with_runtime_reads += 1
        self.assertEqual(18, skills_with_runtime_reads)

    def test_policy_kernel_and_safety_overlays_cannot_drift_per_skill(self):
        kernel = self.index["policy_kernel"]
        self.assertEqual(kernel["sha256"], sha256(ROOT / kernel["path"]))
        for item in self.index["capsules"]:
            capsule = json.loads((ROOT / item["capsule_ref"]).read_text(encoding="utf-8"))
            self.assertEqual(kernel, capsule["policy"]["kernel"], item["skill"])
            self.assertEqual(
                MODULE.ALWAYS_ON_OVERLAYS,
                capsule["policy"]["always_on_overlays"],
                item["skill"],
            )

    def test_all_selected_fixed_representation_reclassification_exceeds_seventy_percent(self):
        shared_bytes = (ROOT / "references" / "skill-contract.md").stat().st_size
        legacy = []
        capsules = []
        ratios = []
        for item in self.index["capsules"]:
            skill = item["skill"]
            contract_ref = self.contracts[skill]["contract_ref"]
            contract = json.loads((ROOT / contract_ref).read_text(encoding="utf-8"))
            legacy_bytes = (
                (ROOT / contract["identity"]["path"]).stat().st_size
                + (ROOT / contract_ref).stat().st_size
                + shared_bytes
            )
            legacy.append(legacy_bytes)
            capsules.append(item["model_bytes"])
            ratios.append(item["model_bytes"] / legacy_bytes)
        self.assertLess(sum(capsules), sum(legacy) * 0.30)
        self.assertLess(max(ratios), 0.40)
        self.assertLess(statistics.median(capsules), statistics.median(legacy) * 0.30)

    def test_model_visible_capsule_representation_reduces_bytes_by_half(self):
        shared_bytes = (ROOT / "references/skill-contract.md").stat().st_size
        explicit = []
        capsules = []
        for item in self.index["capsules"]:
            contract_ref = self.contracts[item["skill"]]["contract_ref"]
            contract = json.loads((ROOT / contract_ref).read_text(encoding="utf-8"))
            explicit.append(
                (ROOT / contract["identity"]["path"]).stat().st_size
                + shared_bytes
            )
            capsules.append(item["model_bytes"])
        self.assertLess(sum(capsules), sum(explicit) * 0.50)
        self.assertLess(
            statistics.median(capsules), statistics.median(explicit) * 0.50
        )

    def test_documented_capsule_baseline_is_exactly_derived(self):
        document = (ROOT / "docs/context-engineering.md").read_text(encoding="utf-8")
        model_aggregate = re.search(
            r"\| Model-visible explicit aggregate: Skill \+ shared contract, all 120 "
            r"\| ([0-9,]+) B \| ([0-9,]+) B with capsule \+ kernel "
            r"\| [−-]([0-9.]+)% \|",
            document,
        )
        model_median = re.search(
            r"\| Model-visible explicit median \| ([0-9,.]+) B "
            r"\| ([0-9,.]+) B \(~([0-9,]+) B\) with capsule \+ kernel "
            r"\| [−-]([0-9.]+)% \|",
            document,
        )
        all_selected_aggregate = re.search(
            r"\| All-selected fixed representation aggregate: Skill \+ "
            r"controller-only machine contract \+ shared contract, all 120 "
            r"\| ([0-9,]+) B \| ([0-9,]+) B with capsule \+ kernel "
            r"\| [−-]([0-9.]+)% \|",
            document,
        )
        all_selected_median = re.search(
            r"\| All-selected fixed representation median \| ([0-9,.]+) B "
            r"\| ([0-9,.]+) B \(~([0-9,]+) B\) with capsule \+ kernel "
            r"\| [−-]([0-9.]+)% \|",
            document,
        )
        for match in (
                model_aggregate, model_median,
                all_selected_aggregate, all_selected_median):
            self.assertIsNotNone(match)

        shared_bytes = (ROOT / "references/skill-contract.md").stat().st_size
        explicit = []
        all_selected = []
        capsules = []
        for item in self.index["capsules"]:
            contract_ref = self.contracts[item["skill"]]["contract_ref"]
            contract = json.loads((ROOT / contract_ref).read_text(encoding="utf-8"))
            skill_bytes = (ROOT / contract["identity"]["path"]).stat().st_size
            explicit.append(skill_bytes + shared_bytes)
            all_selected.append(
                skill_bytes + (ROOT / contract_ref).stat().st_size + shared_bytes
            )
            capsules.append(item["model_bytes"])

        capsule_median = statistics.median(capsules)
        for aggregate, median, baseline in (
                (model_aggregate, model_median, explicit),
                (all_selected_aggregate, all_selected_median, all_selected)):
            documented_aggregate = (
                int(aggregate.group(1).replace(",", "")),
                int(aggregate.group(2).replace(",", "")),
                float(aggregate.group(3)),
            )
            expected_aggregate = (
                sum(baseline),
                sum(capsules),
                round((1 - sum(capsules) / sum(baseline)) * 100, 1),
            )
            self.assertEqual(expected_aggregate, documented_aggregate)

            baseline_median = statistics.median(baseline)
            documented_median = (
                float(median.group(1).replace(",", "")),
                float(median.group(2).replace(",", "")),
                int(median.group(3).replace(",", "")),
                float(median.group(4)),
            )
            expected_median = (
                baseline_median,
                capsule_median,
                int(capsule_median + 0.5),
                round((1 - capsule_median / baseline_median) * 100, 1),
            )
            self.assertEqual(expected_median, documented_median)


if __name__ == "__main__":
    unittest.main()
