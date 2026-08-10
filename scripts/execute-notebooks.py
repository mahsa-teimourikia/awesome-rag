#!/usr/bin/env python3
"""Execute every credential-free course notebook in a real Jupyter kernel.

The curriculum notebooks, the scenario-first tracks, and the local use cases
share the same import and fixture contracts. Keeping all of them in this runner
makes a folder restructuring observable in CI rather than only in a learner's
local Jupyter session.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("beginner", "enterprise", "evaluation", "adaptive-rag")


def notebook_paths() -> list[Path]:
    scenario_tracks = [path for track in TRACKS for path in sorted((ROOT / "notebooks" / track).glob("*.ipynb"))]
    curriculum = sorted((ROOT / "curriculum").glob("*/*/*.ipynb"))
    use_cases = sorted((ROOT / "use-cases").glob("*/*.ipynb"))
    return scenario_tracks + curriculum + use_cases


def execute(path: Path, timeout: int) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )
    client.execute()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=90, help="per-cell timeout in seconds")
    parser.add_argument("--list", action="store_true", help="print the CI notebook manifest without executing it")
    args = parser.parse_args()
    paths = notebook_paths()
    if not paths:
        raise SystemExit("No notebook execution targets found")
    if args.list:
        print("\n".join(str(path.relative_to(ROOT)) for path in paths))
        return
    for index, path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] execute {path.relative_to(ROOT)}", flush=True)
        execute(path, args.timeout)
    print(f"Executed {len(paths)} credential-free course notebooks.")


if __name__ == "__main__":
    main()
