import pytest
from src.ask import _build_prompt

def test_build_prompt_structure(tmp_path):
    note_file = tmp_path / "test_note.md"
    note_file.write_text(
        "---\ntitle: Machine Learning\ncategory: Areas\n---\nGradient descent optimizes weights.",
        encoding="utf-8"
    )

    contexts = [
        {
            "id": "cap_001",
            "title": "Machine Learning",
            "wiki_path": str(note_file),
            "score": 0.895
        }
    ]

    prompt = _build_prompt("How does gradient descent work?", contexts)
    assert "How does gradient descent work?" in prompt
    assert "Machine Learning" in prompt
    assert "Gradient descent optimizes weights" in prompt
    assert "Retrieved Notes:" in prompt
