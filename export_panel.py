from __future__ import annotations

from pathlib import Path

import panel as pn

from panel_dashboard import make_dashboard, load_manifest

pn.extension(sizing_mode="stretch_width")

ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "_build"
BUILD_DIR.mkdir(exist_ok=True)


def main() -> None:
    manifest = load_manifest()
    dashboard = make_dashboard(manifest)
    out = BUILD_DIR / "panel-dashboard.html"
    dashboard.save(
        str(out),
        title="Map dashboard",
        resources="cdn",
        embed=False,
    )
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
