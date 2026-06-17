from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLOTS_DIR = ROOT / "plots"
MANIFEST_PATH = ROOT / "plot_manifest.json"


def build_manifest() -> dict:
    """Scan plots/*.html and build a manifest.

    Expected filename pattern:
        <group_level>__<indicator>.html

    Example:
        district__population_rate.html
        region__income.html
    """
    manifest = {"groups": [], "indicators": [], "plots": {}}

    if not PLOTS_DIR.exists():
        raise FileNotFoundError(f"Missing plots directory: {PLOTS_DIR}")

    groups = set()
    indicators = set()
    plots = {}

    for html_file in sorted(PLOTS_DIR.glob("*.html")):
        stem = html_file.stem
        if "__" not in stem:
            # Skip files that do not follow the naming convention.
            continue
        group, indicator = stem.split("__", 1)
        groups.add(group)
        indicators.add(indicator)
        plots[f"{group}::{indicator}"] = f"plots/{html_file.name}"

    manifest["groups"] = sorted(groups)
    manifest["indicators"] = sorted(indicators)
    manifest["plots"] = plots
    return manifest


def main() -> None:
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"Found {len(manifest['groups'])} group levels and {len(manifest['indicators'])} indicators")
    print(f"Mapped {len(manifest['plots'])} plot files")


if __name__ == "__main__":
    main()
