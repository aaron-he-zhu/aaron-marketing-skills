#!/usr/bin/env python3
"""Regression tests for the generated, bounded auto-routing scenario shards."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-auto-routing-shards.py"
SPEC = importlib.util.spec_from_file_location("generate_auto_routing_shards", SCRIPT)
assert SPEC and SPEC.loader
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


def runtime_case_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("- {")]


class AutoRoutingShardTests(unittest.TestCase):
    def build_root(self, root: Path, *, source: str | None = None,
                   catalog: dict | None = None) -> None:
        if source is None:
            source = (ROOT / GENERATOR.SOURCE_REL).read_text(encoding="utf-8")
        if catalog is None:
            catalog = json.loads((ROOT / GENERATOR.CATALOG_REL).read_text(encoding="utf-8"))
        source_path = root / GENERATOR.SOURCE_REL
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(source, encoding="utf-8")
        catalog_path = root / GENERATOR.CATALOG_REL
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    def test_authoritative_source_partitions_all_88_cases_once(self):
        order, _bodies, ids, runtime_cases = GENERATOR.parse_source(ROOT)
        catalog = json.loads((ROOT / GENERATOR.CATALOG_REL).read_text(encoding="utf-8"))
        self.assertEqual(set(catalog["disciplines"]) | {"cross-discipline"}, set(order))
        flattened = [case_id for shard in order for case_id in ids[shard]]
        self.assertEqual(88, len(flattened))
        self.assertEqual(88, len(set(flattened)))
        self.assertEqual(88, sum(len(runtime_cases[shard]) for shard in order))

    def test_generated_projection_is_current(self):
        self.assertEqual([], GENERATOR.check_outputs(ROOT))

    def test_generated_shards_project_only_runtime_route_fields(self):
        order, _bodies, _ids, runtime_cases = GENERATOR.parse_source(ROOT)
        outputs = GENERATOR.render_outputs(ROOT)
        for shard in order:
            relative = GENERATOR.SHARD_DIR_REL / (shard + ".md")
            rendered = [
                json.loads(line[2:]) for line in runtime_case_lines(outputs[relative])
            ]
            self.assertEqual(runtime_cases[shard], rendered, shard)
            for case in rendered:
                self.assertEqual(set(GENERATOR.RUNTIME_FIELDS), set(case))
                self.assertNotIn("expected_behavior", case)
                self.assertNotIn("failure_modes", case)
                self.assertNotIn("input_summary", case)

    def test_runtime_projection_is_materially_smaller_than_authoritative_cases(self):
        order, bodies, _ids, _runtime_cases = GENERATOR.parse_source(ROOT)
        outputs = GENERATOR.render_outputs(ROOT)
        source_bytes = sum(len(bodies[shard].encode("utf-8")) for shard in order)
        runtime_bytes = sum(
            len(outputs[GENERATOR.SHARD_DIR_REL / (shard + ".md")].encode("utf-8"))
            for shard in order
        )
        self.assertLess(runtime_bytes, source_bytes * 0.60)

    def test_runtime_outputs_never_link_to_authoritative_eval_source(self):
        outputs = GENERATOR.render_outputs(ROOT)
        for relative, content in outputs.items():
            self.assertNotIn("evals/", content, str(relative))
            if relative.parent == GENERATOR.SHARD_DIR_REL:
                self.assertIn("](../aaron-product-api-contract.md)", content, str(relative))
                self.assertNotIn("](aaron-product-api-contract.md)", content, str(relative))

    def test_index_encodes_bounded_loading_contract(self):
        index = GENERATOR.render_outputs(ROOT)[GENERATOR.INDEX_REL]
        self.assertIn("exactly one primary discipline shard", index)
        self.assertIn("at most **3 shards total**", index)
        self.assertIn("cross-discipline", index)
        self.assertNotIn("evals/", index)
        catalog = json.loads((ROOT / GENERATOR.CATALOG_REL).read_text(encoding="utf-8"))
        row_positions = [index.index("| `%s` |" % name) for name in catalog["disciplines"]]
        self.assertEqual(sorted(row_positions), row_positions)

    def test_catalog_discipline_without_marker_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = json.loads((ROOT / GENERATOR.CATALOG_REL).read_text(encoding="utf-8"))
            catalog["disciplines"]["podcast"] = {"phase_order": [], "phases": {}}
            self.build_root(root, catalog=catalog)
            with self.assertRaisesRegex(GENERATOR.SourceError, "missing markers: podcast"):
                GENERATOR.parse_source(root)

    def test_duplicate_case_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = (ROOT / GENERATOR.SOURCE_REL).read_text(encoding="utf-8")
            first_case = next(line for line in source.splitlines() if line.startswith("- {id:"))
            self.build_root(root, source=source + "\n" + first_case + "\n")
            with self.assertRaisesRegex(GENERATOR.SourceError, "duplicates case id"):
                GENERATOR.parse_source(root)

    def test_check_reports_stale_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_root(root)
            GENERATOR.write_outputs(root)
            index = root / GENERATOR.INDEX_REL
            index.write_text(index.read_text(encoding="utf-8") + "stale\n", encoding="utf-8")
            self.assertIn(
                "stale generated file: %s" % GENERATOR.INDEX_REL,
                GENERATOR.check_outputs(root),
            )


if __name__ == "__main__":
    unittest.main()
