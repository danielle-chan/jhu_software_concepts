import sys, os
import pytest
import importlib

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

@pytest.mark.web
def test_run_main_starts_app(monkeypatch):
    called = {}
    def fake_run(*args, **kwargs):
        called["yes"] = True
    monkeypatch.setattr(run.app, "run", fake_run)
    importlib.reload(run)  # re-import triggers __main__
    assert "yes" in called