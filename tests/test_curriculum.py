from pathlib import Path

def test_curriculum_structure():
    """Verify that the core curriculum tracks exist."""
    root = Path(__file__).parent.parent
    curriculum = root / "curriculum"
    
    assert curriculum.exists()
    assert (curriculum / "beginner").exists()
    assert (curriculum / "intermediate").exists()
    assert (curriculum / "advanced").exists()
