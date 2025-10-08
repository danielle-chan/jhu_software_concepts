"""Tests for the Flask application buttons."""

import sys      # then standard library
import os
import pytest  # third-party first

# Ensure "src" is on the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from run import app  # pylint: disable=import-error, wrong-import-position


@pytest.fixture(name="client")
def fixture_client():
    """Return a Flask test client."""
    return app.test_client()


@pytest.mark.buttons
def test_pull_data_redirects(client, monkeypatch):
    """Test that /pull_data redirects after running."""
    # Monkeypatch subprocess.run so we don’t actually scrape/clean
    monkeypatch.setattr("subprocess.run", lambda *a, **k: None)

    # Monkeypatch append_data *inside run.py*
    monkeypatch.setattr("run.append_data", lambda fn: None)

    response = client.get("/pull_data")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


@pytest.mark.buttons
def test_update_analysis_redirects(client):
    """Test that /update_analysis works when not busy."""
    app.is_running = False
    response = client.get("/update_analysis", follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Analysis updated with the latest data." in html


@pytest.mark.buttons
def test_update_analysis_busy_state(client):
    """Test that /update_analysis refuses when busy."""
    app.is_running = True
    response = client.get("/update_analysis", follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Please wait. Cannot update analysis" in html
    app.is_running = False  # reset for other tests
