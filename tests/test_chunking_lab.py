from examples.beginner.chunking_lab import (
    answer_coverage,
    by_heading,
    by_heading_bounded,
    by_sentence_window,
    coverage_result,
    describe_chunks,
    fixed_size,
    scorecard,
)


def test_fixed_size_has_overlap_and_stable_metadata():
    chunks = fixed_size("abcdefghij" * 10, "guide", size=25, overlap=5)
    assert len(chunks) > 1
    assert chunks[0].source == "guide"
    assert chunks[0].chunk_id == "guide-fixed-1"
    assert chunks[0].text[-5:] == chunks[1].text[:5]


def test_heading_chunking_preserves_sections():
    chunks = by_heading("# Intro\n\nOne.\n\n## Retrieval\n\nTwo.", "guide")
    assert [chunk.section for chunk in chunks] == ["Intro", "Retrieval"]
    assert chunks[1].text == "Two."


def test_invalid_fixed_size_configuration_is_rejected():
    try:
        fixed_size("text", "guide", size=0)
    except ValueError as error:
        assert "size" in str(error)
    else:
        raise AssertionError("invalid size should fail")


def test_sentence_windows_and_diagnostics_are_inspectable():
    chunks = by_sentence_window("One fact. Two facts. Three facts.", "guide", sentences_per_chunk=2, overlap_sentences=1)
    assert len(chunks) == 2
    assert chunks[0].text.endswith("Two facts.")
    assert describe_chunks(chunks)["chunks_with_sections"] == 2


def test_answer_coverage_reveals_when_terms_are_split():
    chunks = fixed_size("restart production services requires approval", "guide", size=18, overlap=0)
    assert answer_coverage(chunks, {"restart", "approval"}) == []


def test_bounded_heading_children_keep_source_section_and_parent_identity():
    markdown = "# Policy\n\n" + "restart requires approval. " * 12
    chunks = by_heading_bounded(markdown, "guide", max_characters=60, overlap=10)
    assert len(chunks) > 1
    assert all(chunk.section == "Policy" for chunk in chunks)
    assert all(chunk.parent_id == "guide-section-1" for chunk in chunks)
    assert describe_chunks(chunks)["chunks_with_parent_ids"] == len(chunks)


def test_scorecard_makes_boundary_coverage_and_overlap_visible():
    chunks = fixed_size("restart requires approval. " * 5, "guide", size=30, overlap=8)
    report = scorecard(chunks, {"approval": {"restart", "approval"}})
    coverage = coverage_result(chunks, {"restart", "approval"})
    assert report["count"] == len(chunks)
    assert report["question_count"] == 1
    assert report["adjacent_overlap_characters"] > 0
    assert coverage.covered
