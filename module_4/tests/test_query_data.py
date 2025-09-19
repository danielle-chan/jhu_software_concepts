import sys, os, importlib
import pytest

# Ensure src is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import query_data


class DummyCursor:
    """Fake psycopg cursor that records queries and returns fake results."""

    def __init__(self):
        self.queries = []
        self.fetchall_results = []
        self.fetchone_result = None

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def fetchall(self):
        return self.fetchall_results

    def fetchone(self):
        return self.fetchone_result

    def close(self):
        pass


class DummyConn:
    def __init__(self):
        self.cur = DummyCursor()

    def cursor(self):
        return self.cur

    def commit(self):
        pass

    def close(self):
        pass


@pytest.mark.query
def test_query_data_runs(monkeypatch, capsys):
    """Test that query_data.py runs end-to-end with mocked DB"""

    dummy_conn = DummyConn()
    dummy_cur = dummy_conn.cur

    # Define fake DB results to simulate realistic queries
    dummy_cur.fetchone_result = (3.8,)  # e.g. GPA average