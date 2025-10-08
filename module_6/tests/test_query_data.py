"""Tests for query_data module using dummy DB objects."""

import sys
import os
import pytest
import query_data  # pylint: disable=import-error

# Ensure src is on sys.path before importing the module
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class DummyCursor:
    """Fake psycopg cursor that records queries and returns fake results."""

    def __init__(self):
        self.queries = []
        self.fetchall_results = []
        self.fetchone_result = None

    def execute(self, query, params=None):
        """Record the executed query and parameters."""
        self.queries.append((query, params))

    def fetchall(self):
        """Return preset fetchall results."""
        return self.fetchall_results

    def fetchone(self):
        """Return preset fetchone result."""
        return self.fetchone_result

    def close(self):
        """Close the cursor (noop for dummy)."""
        return None


class DummyConn:
    """Fake psycopg connection with a dummy cursor."""

    def __init__(self):
        self.cur = DummyCursor()

    def cursor(self):
        """Return dummy cursor."""
        return self.cur

    def commit(self):
        """Pretend to commit (noop)."""
        return None

    def close(self):
        """Pretend to close (noop)."""
        return None


@pytest.mark.query
def test_query_data_runs(monkeypatch, capsys):
    """Run query_data with a mocked DB and check it prints results."""

    dummy_conn = DummyConn()
    dummy_cur = dummy_conn.cur

    # Set up fake query results
    dummy_cur.fetchone_result = (3.8,)  # e.g., GPA average
    dummy_cur.fetchall_results = [("Sample row",), ("Another row",)]

    # Patch psycopg.connect to use our dummy connection
    monkeypatch.setattr("psycopg.connect", lambda **kwargs: dummy_conn)

    # Run the main function to exercise the code
    query_data.main()

    # Capture and check output
    captured = capsys.readouterr()
    assert "3.8" in captured.out or "Sample row" in captured.out
