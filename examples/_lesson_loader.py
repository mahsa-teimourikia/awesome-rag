"""Compatibility loader for lesson implementations relocated into curriculum."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def reexport_lesson(namespace: dict, relative_path: str) -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / relative_path
    module_name = f"_course_{path.parent.name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load lesson module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    namespace.update({name: value for name, value in vars(module).items() if not name.startswith("_")})
