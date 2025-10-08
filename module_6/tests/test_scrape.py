"""Tests for scrape.py using fake HTML and dummy responses."""

import sys
import os
import pytest
import scrape  # pylint: disable=import-error  # keep at top now

# Ensure src is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class FakeResponse: # pylint: disable=too-few-public-methods
    """Fake response object for urlopen that returns preset HTML."""

    def __init__(self, html):
        self.html = html

    def read(self):
        """Return the fake HTML as bytes."""
        return self.html.encode("utf-8")


@pytest.mark.scrape
def test_scrape_data_with_fake_html(monkeypatch):
    """Test scrape_data on a page with all expected fields."""
    fake_html = """
    <html>
      <body>
        <div class="tw-font-medium tw-text-gray-900 tw-text-sm">Fake University</div>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500">
          <div class="tw-text-gray-900">
            <span>Computer Science</span><span>Masters</span>
          </div>
        </td>
        <tr>
          <p class="tw-text-gray-500 tw-text-sm tw-my-0">Great program!</p>
        </tr>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell">
          2025-01-01
        </td>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell">
          <div>Status</div>
        </td>
        <a href="https://www.thegradcafe.com/result/12345">Result</a>
      </body>
    </html>
    """

    def fake_urlopen(_url):
        """Return FakeResponse with the preset HTML."""
        return FakeResponse(fake_html)

    monkeypatch.setattr(scrape, "urlopen", fake_urlopen)

    data = scrape.scrape_data(pages=1)

    assert len(data) == 1
    assert data[0]["university"] == "Fake University"
    assert data[0]["program"] == "Computer Science"
    assert data[0]["degree_type"] == "Masters"
    assert data[0]["comment"] == "Great program!"
    assert data[0]["date_added"] == "2025-01-01"
    assert data[0]["applicant_status"] == "Status"
    assert data[0]["url"].startswith("https://www.thegradcafe.com/result/")


class DummyResponse: # pylint: disable=too-few-public-methods
    """Another fake urlopen response."""

    def __init__(self, text):
        self._text = text

    def read(self):
        """Return the fake HTML as bytes."""
        return self._text.encode("utf-8")


@pytest.mark.scrape
def test_scrape_handles_missing_extra_fields(monkeypatch):
    """Test scrape_data handles missing GPA / GRE gracefully."""
    fake_html = """
    <html>
      <body>
        <div class="tw-font-medium tw-text-gray-900 tw-text-sm">Fake University</div>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500">
          <div class="tw-text-gray-900">
            <span>Math</span><span>PhD</span>
          </div>
        </td>
        <tr>
          <p class="tw-text-gray-500 tw-text-sm tw-my-0">No extras</p>
        </tr>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell">
          2025-02-01
        </td>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell">
          <div>Pending</div>
        </td>
        <a href="https://www.thegradcafe.com/result/67890">Result</a>
      </body>
    </html>
    """

    monkeypatch.setattr(scrape, "urlopen", lambda _ignored: DummyResponse(fake_html))

    data = scrape.scrape_data(pages=1)
    assert data[0]["gpa"] == "N/A"  # ensures missing fields handled
