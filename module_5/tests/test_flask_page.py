"""Tests for the main Flask page rendering."""

import sys
import os
import pytest

# Ensure src is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from run import app # pylint: disable=import-error, wrong-import-position

@pytest.fixture
def example_client():
    """Return a Flask test client."""
    return app.test_client()

@pytest.mark.web
def test_flask(example_client): # pylint: disable=redefined-outer-name
    """Check that the home page renders with expected content."""
    response = example_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Pull Data" in html
    assert "Update Analysis" in html
    assert "Analysis" in html
    assert "Answer:" in html
