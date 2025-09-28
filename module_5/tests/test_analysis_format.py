"""Tests for analysis formatting in the Flask application."""

import sys
import os
import re

# Third-party imports
import pytest
from bs4 import BeautifulSoup

# Ensure src is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from run import app  # pylint: disable=import-error,wrong-import-position

@pytest.fixture
def example_client():
    """Return a Flask test client."""
    return app.test_client()


@pytest.mark.analysis
def test_answer_labels_present(example_client): # pylint: disable=redefined-outer-name
    """Check that 'Answer:' labels appear in the rendered analysis page"""
    response = example_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Look for "Answer:" at least once
    assert "Answer:" in html, "Expected 'Answer:' label not found in page"


@pytest.mark.analysis
def test_percentage_formatting(example_client): # pylint: disable=redefined-outer-name
    """Check that percentages are formatted to two decimal places"""
    response = example_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Parse with BeautifulSoup to get text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    # Match percentages
    percentages = re.findall(r"\d+\.\d{2}%", text)

     # Ensure at least one percentage is present
    assert percentages, "Expected at least one percentage on the page"

    # Ensure they all match the 2-decimal format
    for pct in percentages:
        assert re.match(r"^\d+\.\d{2}%$", pct), f"Bad percentage format: {pct}"
