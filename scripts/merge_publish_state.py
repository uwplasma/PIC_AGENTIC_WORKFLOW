from __future__ import annotations

import argparse
import json
from pathlib import Path

from jaxincell_drift_opt.publish_state import merge_campaign_state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--skip-render-movies", action="store_true")
    args = parser.parse_args()

    result = merge_campaign_state(
        args.source_root.resolve(),
        args.target_root.resolve(),
        render_movies=not args.skip_render_movies,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()