import sys, os
import pytest

# Ensure src is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from run import app

@pytest.fixture
def example_client():
    return app.test_client()

@pytest.mark.web
def test_flask(example_client):
    response = example_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Pull Data" in html
    assert "Update Analysis" in html
    assert "Analysis" in html
    assert "Answer:" in html