import sys, os, json
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
import run
import append_data


@pytest.fixture
def example_client():
    return run.app.test_client()


@pytest.mark.integration
def test_end_to_end_flow(example_client, monkeypatch, tmp_path):
    """Simulate scraper -> append -> update -> render"""

    # Step 1: Fake applicant data
    fake_data = [{
        "program": "Computer Science",
        "degree_type": "Masters",
        "comments": "Test comment",
        "date_added": "2025-01-01",
        "status": "Accepted",
        "url": "http://integration-test-url.com",
        "GPA": 3.9,
        "GRE_G": 325,
        "GRE_V": 162,
        "GRE_AW": 4.5,
        "term": "Fall 2025",
        "US/International": "American",
        "llm-generated-program": "Computer Science",
        "llm-generated-university": "Integration U",
        "university": "Integration U"
    }]

    # Step 2: Write fake JSONL file
    jsonl_file = tmp_path / "fake_full_out.jsonl"
    with open(jsonl_file, "w") as f:
        for entry in fake_data:
            f.write(json.dumps(entry) + "\n")

    # Step 3: Patch subprocess.run (skip scraping) and append_data (use fake file)
    monkeypatch.setattr("subprocess.run", lambda *a, **k: None)
    monkeypatch.setattr("run.append_data", lambda fn=None: append_data.append_data(str(jsonl_file)))

    # Step 4: Call /pull_data (should load fake row)
    response = example_client.get("/pull_data", follow_redirects=True)
    assert response.status_code == 200

    # Step 5: Call /update_analysis
    response = example_client.get("/update_analysis", follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Analysis updated with the latest data." in html

    # Step 6: Verify our fake data shows up on /
    response = example_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Integration U" in html or "Answer:" in html