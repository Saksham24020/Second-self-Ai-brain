import pytest
from src.manager import derive_clean_title, derive_clean_summary

def test_derive_clean_title_with_valid_original():
    title = derive_clean_title("cap_12345", "Neural Networks Deep Dive", "Some content")
    assert title == "Neural Networks Deep Dive"

def test_derive_clean_title_from_heading():
    content = "# Introduction to Python\nPython is a programming language."
    title = derive_clean_title("cap_custom_99999999", "Placeholder title", content)
    assert title == "Introduction to Python"

def test_derive_clean_title_fallback():
    title = derive_clean_title("cap_20260901_120000_12345678", "Placeholder title", "")
    assert title == "Note 12345678"

def test_derive_clean_summary_from_content():
    content = "# Architecture\nThis note outlines the event-driven microservice system and caching layer."
    summary = derive_clean_summary("cap_test_abc", "Placeholder summary for testing.", content)
    assert "Architecture" in summary
    assert "event-driven" in summary
