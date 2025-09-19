import sys, os
import pytest

# Make sure "src" is on the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import run
import append_data


@pytest.fixture
def example_client():
    return run.app.test_client()


@pytest.mark.buttons
def test_pull_data_redirects(example_client, monkeypatch):
    """Test that /pull_data redirects after running"""

    # Monkeypatch subprocess.run so we don’t actually scrape/clean
    monkeypatch.setattr("subprocess.run", lambda *a, **k: None)

    # Monkeypatch append_data *inside run.py*
    monkeypatch.setattr("run.append_data", lambda fn: None)

    response = example_client.get("/pull_data")
    assert response.status_code == 302  # should redirect
    assert response.headers["Location"].endswith("/")


@pytest.mark.buttons
def test_update_analysis_redirects(example_client):
    """Test that /update_analysis works when not busy"""
    run.is_running = False
    response = example_client.get("/update_analysis", follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Analysis updated with the latest data." in html


@pytest.mark.buttons
def test_update_analysis_busy_state(example_client):
    """Test that /update_analysis refuses when busy"""
    run.is_running = True
    response = example_client.get("/update_analysis", follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Please wait. Cannot update analysis" in html
    run.is_running = False  # reset flag so other tests aren’t affected
