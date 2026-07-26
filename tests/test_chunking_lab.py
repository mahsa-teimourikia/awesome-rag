from examples.beginner.chunking_lab import by_heading, fixed_size


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
