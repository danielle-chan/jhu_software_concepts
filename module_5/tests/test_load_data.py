import sys, os, json, importlib
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
import load_data


class DummyCursor:
    def __init__(self):
        self.queries = []

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def close(self):
        pass


class DummyConn:
    def __init__(self):
        self.cursor_obj = DummyCursor()
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        pass

@pytest.mark.load
def test_load_data_inserts(monkeypatch, tmp_path):
    fake_entry = {
        "program": "CS",
        "degree_type": "Masters",
        "comments": "Good",
        "date_added": "2025-01-01",
        "status": "Accepted",
        "url": "http://fake-url.com",
        "GPA": 3.9,
        "GRE_G": 320,
        "GRE_V": 160,
        "GRE_AW": 4.5,
        "term": "Fall 2025",
        "US/International": "American",
        "llm-generated-program": "CS",
        "llm-generated-university": "Fake U",
        "university": "Fake U"
    }

    # Create fake jsonl file
    file = tmp_path / "fake.jsonl"
    with open(file, "w") as f:
        f.write(json.dumps(fake_entry) + "\n")

    # Patch psycopg.connect to return DummyConn
    dummy_conn = DummyConn()
    monkeypatch.setattr("psycopg.connect", lambda **kwargs: dummy_conn)

    # Save original open
    real_open = open

    # Patch builtins.open
    def fake_open(fn, mode="r", *args, **kwargs):
        if isinstance(fn, str) and fn.endswith("full_out.jsonl"):
            return real_open(file, mode, *args, **kwargs)
        return real_open(fn, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    # Reload module to trigger execution
    importlib.reload(load_data)

    # Assertions
    assert dummy_conn.committed
    assert dummy_conn.cursor_obj.queries  # at least one INSERT happened