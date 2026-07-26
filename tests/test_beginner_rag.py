from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from examples.beginner.first_local_rag import answer, load_chunks, retrieve


ROOT = Path(__file__).parents[1]


def test_fixture_loads_with_source_ids():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    assert len(chunks) >= 5
    assert all(chunk.chunk_id and chunk.source for chunk in chunks)


def test_retrieval_returns_relevant_evidence():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    results = retrieve("What is an abstention?", chunks)
    assert results
    assert "abstention" in results[0][0].text.lower()


def test_answer_abstains_without_evidence():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    assert answer("What is the capital of France?", chunks).startswith("I don't have enough evidence")
