from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    target_root = args.target_root.resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    for name in ["state", "reports", "results"]:
        source = source_root / name
        if source.exists():
            copy_tree(source, target_root / name)

    readme_source = source_root / "README.md"
    if readme_source.exists():
        shutil.copy2(readme_source, target_root / "README.md")


if __name__ == "__main__":
    main()
