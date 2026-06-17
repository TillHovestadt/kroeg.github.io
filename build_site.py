from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "_build"
DOCS_DIR = ROOT / "docs"
PLOTS_DIR = ROOT / "plots"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def copytree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    BUILD_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)

    run([sys.executable, "scripts/build_manifest.py"])
    run([sys.executable, "export_panel.py"])

    # Render the Quarto website to docs/
    run(["quarto", "render"])

    # Copy the static Panel export and map files into the published site.
    shutil.copy2(BUILD_DIR / "panel-dashboard.html", DOCS_DIR / "panel-dashboard.html")
    copytree(PLOTS_DIR, DOCS_DIR / "plots")

    print("Static site ready in docs/")


if __name__ == "__main__":
    main()
