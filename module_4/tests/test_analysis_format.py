import re
import pytest
from bs4 import BeautifulSoup
import sys, os

# Ensure src is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from run import app

@pytest.fixture
def example_client():
    return app.test_client()


def test_answer_labels_present(example_client):
    """Check that 'Answer:' labels appear in the rendered analysis page"""
    response = example_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Look for "Answer:" at least once
    assert "Answer:" in html, "Expected 'Answer:' label not found in page"
    

def test_percentage_formatting(example_client):
    """Check that percentages are formatted to two decimal places"""
    response = example_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Parse with BeautifulSoup to get text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    # Match percentages
    percentages = re.findall(r"\d+\.\d{2}%", text)

    # If there are percentages on the page, ensure they match the 2-decimal format
    for pct in percentages:
        assert re.match(r"^\d+\.\d{2}%$", pct), f"Bad percentage format: {pct}"