"""Lock the vendored Agent Plugins v1 manifest schema to its upstream sources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STANDARD_ROOT = ROOT / "references" / "standards" / "agent-plugins" / "1.0.0"
SCHEMA_PATH = STANDARD_ROOT / "plugin.schema.json"
PROVENANCE_PATH = STANDARD_ROOT / "PROVENANCE.json"
SCHEMA_SHA256 = "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
RELEASE_COMMIT = "f24daf829224fd7fb685ae117c518ea27cbe7b9e"
AGENT_SKILLS_COMMIT = "217be548739f21d6008915c29aefe320ea1a90af"
CANONICAL_SCHEMA_URL = (
    "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
)


class AgentPluginsProvenanceTests(unittest.TestCase):
    def load_json(self, path: Path) -> dict:
        value = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def test_vendored_schema_has_exact_upstream_digest_and_closed_fields(self):
        raw = SCHEMA_PATH.read_bytes()
        self.assertEqual(len(raw), 1805)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SCHEMA_SHA256)

        schema = json.loads(raw)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema"
        )
        self.assertEqual(schema["$id"], CANONICAL_SCHEMA_URL)
        self.assertEqual(schema["required"], ["$schema", "name"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            set(schema["properties"]),
            {
                "$schema",
                "name",
                "version",
                "description",
                "author",
                "homepage",
                "repository",
                "license",
                "keywords",
                "extensions",
            },
        )
        self.assertEqual(
            schema["properties"]["$schema"]["const"], CANONICAL_SCHEMA_URL
        )
        self.assertFalse(schema["properties"]["author"]["additionalProperties"])
        self.assertEqual(
            schema["properties"]["extensions"]["additionalProperties"],
            {"type": "object"},
        )

    def test_provenance_binds_schema_and_upstream_baselines(self):
        provenance = self.load_json(PROVENANCE_PATH)
        artifact = provenance["artifact"]
        self.assertEqual(
            artifact["path"],
            "references/standards/agent-plugins/1.0.0/plugin.schema.json",
        )
        self.assertEqual(artifact["media_type"], "application/schema+json")
        self.assertEqual(artifact["bytes"], SCHEMA_PATH.stat().st_size)
        self.assertEqual(artifact["sha256"], SCHEMA_SHA256)

        agent_plugins = provenance["agent_plugins"]
        self.assertEqual(agent_plugins["specification_version"], "1.0.0")
        self.assertEqual(agent_plugins["status"], "Published")
        self.assertEqual(agent_plugins["canonical_schema_url"], CANONICAL_SCHEMA_URL)
        self.assertEqual(agent_plugins["release_commit"], RELEASE_COMMIT)
        self.assertEqual(
            agent_plugins["release_committed_at"], "2026-07-27T21:53:19Z"
        )
        self.assertIn(RELEASE_COMMIT, agent_plugins["specification_url"])
        self.assertIn(RELEASE_COMMIT, agent_plugins["commit_pinned_schema_url"])
        self.assertEqual(
            agent_plugins["commit_pinned_schema_sha256"], SCHEMA_SHA256
        )

        agent_skills = provenance["agent_skills_baseline"]
        self.assertEqual(agent_skills["commit"], AGENT_SKILLS_COMMIT)
        self.assertEqual(agent_skills["committed_at"], "2026-08-04T22:52:17Z")
        self.assertIn(AGENT_SKILLS_COMMIT, agent_skills["commit_url"])
        self.assertIn(
            AGENT_SKILLS_COMMIT,
            agent_skills["commit_pinned_specification_url"],
        )
        self.assertEqual(
            agent_skills["specification_url"],
            "https://agentskills.io/specification",
        )


if __name__ == "__main__":
    unittest.main()
