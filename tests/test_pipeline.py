"""Integration tests for catalog validation, HTML generation, and selection."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_selection import apply
from build_review import build
from common import load_catalog, load_selection


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.catalog_path = ROOT / "examples" / "sources.json"
        self.selection_path = ROOT / "examples" / "selection.json"

    def test_sample_catalog_and_selection(self):
        catalog = load_catalog(self.catalog_path)
        selection = load_selection(self.selection_path, catalog)
        self.assertEqual(len(catalog["sources"]), 3)
        self.assertEqual(len(selection["decisions"]), 3)

    def test_build_and_export(self):
        with tempfile.TemporaryDirectory() as directory:
            html_path = Path(directory) / "review.html"
            selected_path = Path(directory) / "selected.json"
            build(self.catalog_path, html_path)
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("示例视频素材", html)
            self.assertNotIn("__CATALOG_JSON__", html)
            self.assertIn("导出 selection.json", html)
            _, count = apply(self.catalog_path, self.selection_path, selected_path)
            data = json.loads(selected_path.read_text(encoding="utf-8"))
            self.assertEqual(count, 2)
            self.assertEqual({v["id"] for v in data["sources"]}, {"article001", "video001"})

    def test_reject_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            d = json.loads(self.catalog_path.read_text(encoding="utf-8"))
            d["sources"][1]["id"] = d["sources"][0]["id"]
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(d), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate source id"):
                load_catalog(path)

    def test_escape_html_data(self):
        with tempfile.TemporaryDirectory() as directory:
            d = json.loads(self.catalog_path.read_text(encoding="utf-8"))
            d["sources"][0]["title"] = "</script><script>alert(1)</script>"
            path = Path(directory) / "data.json"
            out = Path(directory) / "review.html"
            path.write_text(json.dumps(d), encoding="utf-8")
            build(path, out)
            html = out.read_text(encoding="utf-8")
            self.assertNotIn("</script><script>alert", html)
            self.assertIn("\\u003c/script", html)


if __name__ == "__main__":
    unittest.main()
