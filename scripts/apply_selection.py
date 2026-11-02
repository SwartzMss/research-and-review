#!/usr/bin/env python3
"""Export selected research sources for downstream writing/directing."""

import argparse
import json
from pathlib import Path

from common import load_catalog, load_selection


def apply(catalog_path, selection_path, output_path):
    catalog = load_catalog(catalog_path)
    selection = load_selection(selection_path, catalog)
    choices = {item["source_id"]: item for item in selection["decisions"]}
    picked = []
    for source in catalog["sources"]:
        decision = choices.get(source["id"], {"decision": "pending", "note": ""})
        if decision["decision"] in ("research", "visual"):
            picked.append({**source, "review_decision": decision["decision"], "review_note": decision["note"]})
    result = {
        "schema_version": 1,
        "topic": catalog["topic"],
        "sources": picked,
        "reviewed_count": len(selection["decisions"]),
        "selection_exported_at": selection.get("exported_at"),
        "notice": "Selection is not fact verification or copyright clearance."
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target, len(picked)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", help="Input sources.json")
    parser.add_argument("selection", help="selection.json exported from review.html")
    parser.add_argument("--output", default="output/selected.json", help="Selected sources JSON")
    args = parser.parse_args()
    target, count = apply(args.catalog, args.selection, args.output)
    print("Selected", count, "sources ->", target.resolve())


if __name__ == "__main__":
    main()
