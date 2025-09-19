import json
import sys, os, json
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from clean import clean_data, save_data, load_data

@pytest.mark.clean
def test_clean_data_normalizes_missing_fields():
    raw = [{"university": "Test U"}]  # leave "program" key out completely
    cleaned = clean_data(raw)
    assert cleaned[0]["program"] == "N/A"

@pytest.mark.clean
def test_save_and_load_roundtrip(tmp_path):
    cleaned = [{"university": "U", "program": "CS"}]
    file = tmp_path / "test.json"
    save_data(cleaned, file)
    loaded = load_data(file)
    assert loaded == cleaned

@pytest.mark.clean
def test_clean_data_handles_empty_list():
    cleaned = clean_data([])
    assert cleaned == []  # should just return empty without errors