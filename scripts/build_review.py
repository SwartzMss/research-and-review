#!/usr/bin/env python3
"""Create a single-file, offline-friendly HTML source review board."""

import argparse
import json
from pathlib import Path

from common import load_catalog


def build(catalog_path, output_path):
    catalog = load_catalog(catalog_path)
    template = Path(__file__).resolve().parent.parent / "templates" / "review.html"
    html = template.read_text(encoding="utf-8")
    # Prevent </script>, markup and ampersands in research data from becoming HTML.
    payload = json.dumps(catalog, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    assert html.count("__CATALOG_JSON__") == 1, "template marker must be unique"
    html = html.replace("__CATALOG_JSON__", payload)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", help="Path to sources.json")
    parser.add_argument("--output", default="output/review.html", help="HTML output path")
    args = parser.parse_args()
    target = build(args.catalog, args.output)
    print("Review board:", target.resolve())
    print("Select sources and export selection.json from the browser.")


if __name__ == "__main__":
    main()
