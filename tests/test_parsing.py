import pytest
from pathlib import Path
from src.parsing.text_extract import extract_note, extract_file

def test_extract_note_valid():
    text = "   This is a sample note about machine learning.   "
    extracted = extract_note(text)
    assert extracted == "This is a sample note about machine learning."

def test_extract_note_empty():
    with pytest.raises(ValueError):
        extract_note("   ")

def test_extract_file_markdown_and_txt(tmp_path):
    md_file = tmp_path / "sample.md"
    md_file.write_text("# Knowledge Base\nSecond Brain concept.", encoding="utf-8")
    
    content = extract_file(str(md_file))
    assert "Knowledge Base" in content
    assert "Second Brain concept" in content

    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("Plain text notes content.", encoding="utf-8")
    content_txt = extract_file(str(txt_file))
    assert content_txt == "Plain text notes content."

def test_extract_file_nonexistent():
    with pytest.raises(FileNotFoundError):
        extract_file("nonexistent_file.xyz")

def test_extract_file_unsupported_type(tmp_path):
    unsupported = tmp_path / "image.png"
    unsupported.write_bytes(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_file(str(unsupported))
