import pytest
from src.storage.manifest import generate_capture_id, get_iso_timestamp, save_manifest, load_manifest

def test_generate_capture_id():
    cap_id_1 = generate_capture_id()
    cap_id_2 = generate_capture_id()
    assert cap_id_1.startswith("cap_")
    assert cap_id_2.startswith("cap_")
    assert cap_id_1 != cap_id_2

def test_get_iso_timestamp():
    ts = get_iso_timestamp()
    assert isinstance(ts, str)
    assert "T" in ts

def test_save_and_load_manifest(tmp_path, monkeypatch):
    # Route raw directory to tmp_path to prevent touching production data
    monkeypatch.chdir(tmp_path)
    
    cap_id = "cap_test_001"
    sample_meta = {
        "id": cap_id,
        "source_type": "note",
        "title": "Test Title",
        "tags": ["unit-test", "pytest"]
    }
    
    save_manifest(cap_id, sample_meta)
    loaded = load_manifest(cap_id)
    
    assert loaded["id"] == cap_id
    assert loaded["source_type"] == "note"
    assert loaded["title"] == "Test Title"
    assert "unit-test" in loaded["tags"]
