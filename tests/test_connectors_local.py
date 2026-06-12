import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "connectors"))

import onpage  # noqa: E402
import linkgraph  # noqa: E402
import schema_lint  # noqa: E402


class OnPageParserTests(unittest.TestCase):
    def test_word_count_excludes_non_visible_head_and_script_text(self):
        html = """<!doctype html>
        <html>
          <head>
            <title>Invisible title</title>
            <style>.hidden words should not count</style>
            <script>var fake = "many invisible words here";</script>
          </head>
          <body>
            <h1>Hello world</h1>
            <p>Visible text only.</p>
          </body>
        </html>"""

        result = onpage.analyze(html)

        self.assertEqual(result["title"], "Invisible title")
        self.assertEqual(result["headings"]["h1"], ["Hello world"])
        self.assertEqual(result["word_count"], 5)


class LinkGraphTests(unittest.TestCase):
    def test_analyze_deduplicates_internal_links_and_reports_orphans(self):
        pages = [
            {
                "url": "https://example.com/",
                "depth": 0,
                "title": "Home",
                "links_out": [
                    "https://example.com/a",
                    "https://example.com/a",
                    "https://external.test/",
                ],
            },
            {
                "url": "https://example.com/a",
                "depth": 1,
                "title": "A",
                "links_out": [],
            },
            {
                "url": "https://example.com/orphan",
                "depth": 2,
                "title": "Orphan",
                "links_out": [],
            },
        ]

        result = linkgraph.analyze(pages)

        self.assertEqual(result["summary"]["total_internal_links"], 1)
        self.assertEqual(result["degrees"]["https://example.com/a"]["in"], 1)
        self.assertEqual(result["orphans"], ["https://example.com/orphan"])


class SchemaLintTests(unittest.TestCase):
    def test_lint_html_reports_required_schema_errors(self):
        html = """<script type="application/ld+json">
        {"@context":"https://schema.org","@type":"Article"}
        </script>"""

        result = schema_lint.lint_html(html, source="<test>")

        self.assertEqual(result["summary"]["errors"], 1)
        self.assertEqual(result["objects"][0]["@type"], "Article")
        self.assertEqual(result["objects"][0]["missing_required"], ["headline"])


if __name__ == "__main__":
    unittest.main()
