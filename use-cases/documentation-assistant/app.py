"""Documentation assistant capstone assembled from the beginner modules."""

from __future__ import annotations

import sys
from pathlib import Path

from examples.beginner.citations import answer_with_citations, render_markdown
from examples.beginner.first_local_rag import load_chunks


ROOT = Path(__file__).parent / "docs"


def ask(question: str) -> str:
    chunks = load_chunks(ROOT)
    return render_markdown(answer_with_citations(question, chunks))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python use-cases/documentation-assistant/app.py "your question"')
    print(ask(sys.argv[1]))
