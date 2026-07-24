import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "workflow_graph", ROOT / "scripts" / "workflow-graph.py"
)
workflow_graph = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow_graph)


class WorkflowGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, _ = workflow_graph.load_json(
            ROOT / workflow_graph.CATALOG_REL, "catalog"
        )
        cls.source, _, cls.edges, _ = workflow_graph.load_authoritative_source(ROOT)

    def validate(self, source, edges=None):
        return workflow_graph.validate_source(
            source, self.catalog, ROOT,
            copy.deepcopy(self.edges if edges is None else edges),
        )

    def test_projection_covers_catalog_and_real_launch_fanout_join(self):
        failures, graph = workflow_graph.check(ROOT)
        self.assertEqual([], failures)
        self.assertEqual(120, graph["counts"]["nodes"])
        self.assertEqual(376, graph["counts"]["edges"])
        self.assertEqual(
            {node["id"] for node in workflow_graph.catalog_nodes(self.catalog)},
            {node["id"] for node in graph["nodes"]},
        )
        workflow = next(
            item for item in graph["workflows"]
            if item["id"] == "product-launch-execution"
        )
        self.assertEqual("launch-asset-packager", workflow["entry_node"])
        self.assertEqual(["launch-retro-analyzer"], workflow["terminal_nodes"])
        edges = {edge["id"]: edge for edge in self.edges}
        for target in (
                "community-launch-runner", "launch-readiness-auditor",
                "press-media-relations"):
            edge = edges["launch-asset-packager--" + target]
            self.assertEqual("fan-out", edge["type"])
        for source in (
                "community-launch-runner", "launch-day-conductor",
                "press-media-relations"):
            edge = edges[source + "--launch-monitor"]
            self.assertEqual("join", edge["type"])
        release = edges["launch-readiness-auditor--launch-day-conductor"]
        self.assertEqual("gate", release["type"])
        self.assertEqual("launch-readiness-auditor", release["gate"])
        self.assertEqual(["external-action-approval"], release["permissions"])
        self.assertIn("audit-evidence", release["required_inputs"])
        self.assertIn("execution-approval", release["required_inputs"])
        self.assertIn("permission-approved", release["precondition_codes"])
        self.assertEqual(set(workflow["edge_ids"]), {
            "launch-asset-packager--community-launch-runner",
            "launch-asset-packager--launch-readiness-auditor",
            "launch-asset-packager--press-media-relations",
            "launch-readiness-auditor--launch-day-conductor",
            "community-launch-runner--launch-monitor",
            "launch-day-conductor--launch-monitor",
            "press-media-relations--launch-monitor",
            "launch-monitor--launch-retro-analyzer",
        })

    def test_non_auditor_control_evidence_has_explicit_gate_branches(self):
        edges = {edge["id"]: edge for edge in self.edges}
        for edge_id, gate in (
            ("paid-measurement-loop--ad-account-auditor", "ad-account-auditor"),
            ("fit-scorer--creator-content-auditor", "creator-content-auditor"),
        ):
            with self.subTest(edge=edge_id):
                edge = edges[edge_id]
                self.assertEqual("gate", edge["type"])
                self.assertEqual(gate, edge["gate"])
                self.assertEqual("quality-gate", edge["condition_code"])
                self.assertIn("audit-evidence", edge["required_inputs"])
                self.assertIn("gate-evidence-ready", edge["precondition_codes"])
                self.assertIn("separate invocation", edge["condition_text"])

        report = edges["paid-measurement-loop--report-generator"]
        self.assertEqual("cross-discipline", report["type"])
        self.assertIn("Trustworthy readback decision", report["condition_text"])

    def test_rejects_dangling_edge(self):
        edges = copy.deepcopy(self.edges)
        edges[0]["to"] = "missing-skill"
        with self.assertRaisesRegex(workflow_graph.GraphError, "dangling"):
            self.validate(copy.deepcopy(self.source), edges)

    def test_release_gate_requires_ship_evidence_and_independent_approval_contract(self):
        for field, replacement in (
                ("permissions", ["none"]),
                ("required_inputs", ["audit-evidence", "handoff-summary"]),
                ("precondition_codes", [
                    "automatic-handoff-cap-available", "gate-evidence-ready",
                    "handoff-unambiguous", "required-inputs-present",
                    "target-not-visited",
                ])):
            with self.subTest(field=field):
                edges = copy.deepcopy(self.edges)
                release = next(
                    edge for edge in edges
                    if edge["id"] == "launch-readiness-auditor--launch-day-conductor"
                )
                release[field] = replacement
                with self.assertRaisesRegex(
                        workflow_graph.GraphError,
                        "execution approval|semantic drift"):
                    self.validate(copy.deepcopy(self.source), edges)

    def test_rejects_markdown_source_drift_in_both_directions(self):
        edges = copy.deepcopy(self.edges)
        edges[0]["documentation_required"] = False
        with self.assertRaisesRegex(workflow_graph.GraphError, "Next Best Skill/source drift"):
            self.validate(copy.deepcopy(self.source), edges)

        edges = copy.deepcopy(self.edges)
        edges[0]["to"] = edges[1]["to"]
        with self.assertRaises(workflow_graph.GraphError):
            self.validate(copy.deepcopy(self.source), edges)

    def test_rejects_unbounded_cycle_and_undeclared_phase_inversion(self):
        edges = copy.deepcopy(self.edges)
        cycle_edge = next(
            edge for edge in edges
            if edge["loop_policy"] == {"mode": "visited-set", "max_traversals": 1}
        )
        cycle_edge["loop_policy"] = {"mode": "acyclic", "max_traversals": 1}
        with self.assertRaisesRegex(workflow_graph.GraphError, "illegal cycle"):
            self.validate(copy.deepcopy(self.source), edges)

        edges = copy.deepcopy(self.edges)
        inversion = next(
            edge for edge in edges
            if edge["id"] == "attribution-reconciler--ad-account-auditor"
        )
        inversion["exception"] = None
        with self.assertRaisesRegex(workflow_graph.GraphError, "phase inversion"):
            self.validate(copy.deepcopy(self.source), edges)

    def test_rejects_unexpected_non_terminal_dead_end(self):
        source = copy.deepcopy(self.source)
        edges = copy.deepcopy(self.edges)
        node = next(
            item for item in workflow_graph.catalog_nodes(self.catalog)
            if item["id"] not in source["terminal_nodes"]
            and any(edge["from"] == item["id"] for edge in edges)
        )["id"]
        edges = [edge for edge in edges if edge["from"] != node]
        source["edge_shards"][0]["edge_count"] -= len(self.edges) - len(edges)
        with self.assertRaisesRegex(workflow_graph.GraphError, "dead end"):
            self.validate(source, edges)

    def test_rejects_unexpected_orphan_even_when_declared_terminal(self):
        source = copy.deepcopy(self.source)
        edges = copy.deepcopy(self.edges)
        node = next(
            item["id"] for item in workflow_graph.catalog_nodes(self.catalog)
            if item["id"] not in source["terminal_nodes"]
        )
        source["terminal_nodes"].append(node)
        policy = next(
            item for item in source["node_stopping_policies"] if item["node"] == node
        )
        policy["mode"] = "terminal"
        policy["condition_codes"] = ["objective-complete"]
        edges = [
            edge for edge in edges if edge["from"] != node and edge["to"] != node
        ]
        source["edge_shards"][0]["edge_count"] -= len(self.edges) - len(edges)
        with self.assertRaisesRegex(workflow_graph.GraphError, "orphan"):
            self.validate(source, edges)

    def test_rejects_unreachable_named_workflow_node(self):
        source = copy.deepcopy(self.source)
        workflow = source["workflows"][0]
        workflow["edge_ids"].remove("launch-monitor--launch-retro-analyzer")
        with self.assertRaisesRegex(
                workflow_graph.GraphError, "unreachable|dead end"):
            self.validate(source)


if __name__ == "__main__":
    unittest.main()
