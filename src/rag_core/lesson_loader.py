"""Load a colocated course ``lab.py`` module from a notebook.

Lesson directories use human-readable names such as ``03-query-reranking``.
Those names are intentionally not Python package names, so notebooks use this
small loader instead of importing legacy compatibility modules from ``examples``.
"""

from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType


@lru_cache(maxsize=None)
def load_lesson_module(relative_path: str) -> ModuleType:
    """Load and cache a lesson module relative to the repository root."""

    root = Path(__file__).resolve().parents[2]
    path = root / relative_path
    module_name = f"_rag_lesson_{relative_path.replace('/', '_').replace('-', '_').replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load lesson module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
