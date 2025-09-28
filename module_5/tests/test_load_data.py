"""Tests for the load_data module."""

import sys
import os
import json
import importlib

import pytest
import load_data  # pylint: disable=import-error

# Ensure src is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class DummyCursor:
    """A dummy cursor to capture executed SQL queries."""

    def __init__(self):
        self.queries = []

    def execute(self, query, params=None):
        """Capture the executed query and parameters."""
        self.queries.append((query, params))

    def close(self):
        """No-op close method for compatibility."""
        return None


class DummyConn:
    """A dummy database connection to capture commits and provide a cursor."""

    def __init__(self):
        self.cursor_obj = DummyCursor()
        self.committed = False

    def cursor(self):
        """Return the dummy cursor."""
        return self.cursor_obj

    def commit(self):
        """Mark that a commit occurred."""
        self.committed = True

    def close(self):
        """No-op close method for compatibility."""
        return None


@pytest.mark.load
def test_load_data_inserts(monkeypatch, tmp_path):
    """Test that load_data inserts applicants into the database."""
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
        "university": "Fake U",
    }

    # Create fake JSONL file
    file = tmp_path / "fake.jsonl"
    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(fake_entry) + "\n")

    # Patch psycopg.connect to use DummyConn
    dummy_conn = DummyConn()
    monkeypatch.setattr("psycopg.connect", lambda **kwargs: dummy_conn)

    # Save original open
    real_open = open

    # Patch builtins.open to redirect to fake file
    def fake_open(*args, **kwargs):
        fn = args[0]
        if isinstance(fn, str) and fn.endswith("full_out.jsonl"):
            return real_open(file, *args[1:], **kwargs)
        return real_open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    # Reload module to trigger insertion
    importlib.reload(load_data)

    # Assertions
    assert dummy_conn.committed, "Expected data commit in DB"
    assert dummy_conn.cursor_obj.queries, "Expected at least one INSERT query"
