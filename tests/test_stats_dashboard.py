import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "stats_dashboard", ROOT / "scripts" / "stats-dashboard.py"
)
stats = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stats)


class ClaudeSkillsStatsTests(unittest.TestCase):
    def test_combines_both_collection_install_totals(self):
        pages = {
            "aaron-marketing-skills": (
                '<span class="font-semibold text-foreground">37.9K</span> '
                "total installs"
            ),
            "seo-geo-claude-skills": (
                '<span class="font-semibold text-foreground">126.2K</span> '
                "total installs"
            ),
        }

        def fetch(url):
            return next(body for repo, body in pages.items() if f"/{repo}/" in url)

        with mock.patch.object(stats, "_get_text", side_effect=fetch):
            self.assertEqual(
                stats.claudeskills_repos_total("aaron-he-zhu", tuple(pages)),
                164_100,
            )

    def test_returns_none_when_either_collection_cannot_be_parsed(self):
        with mock.patch.object(
            stats,
            "_get_text",
            side_effect=["37.9K total installs", "<html>missing total</html>"],
        ):
            self.assertIsNone(
                stats.claudeskills_repos_total(
                    "aaron-he-zhu", stats.CLAUDESKILLS_REPOS
                )
            )

    def test_writes_claudeskills_endpoint_badge(self):
        with tempfile.TemporaryDirectory() as directory:
            stats.write_badges(pathlib.Path(directory), None, None, None, 164_100)
            badge = json.loads(
                (pathlib.Path(directory) / "claudeskills.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(badge["label"], "ClaudeSkills")
        self.assertEqual(badge["message"], "164.1k")


if __name__ == "__main__":
    unittest.main()
