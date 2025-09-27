import sys, os, pytest
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import scrape


class FakeResponse:
    def __init__(self, html):
        self.html = html
    def read(self):
        return self.html.encode("utf-8")

@pytest.mark.scrape
def test_scrape_data_with_fake_html(monkeypatch):
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

    def fake_urlopen(url):
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

@pytest.mark.scrape
def test_scrape_handles_missing_extra_fields(monkeypatch):
    fake_html = """
    <html>
      <body>
        <div class="tw-font-medium tw-text-gray-900 tw-text-sm">Fake University</div>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500">
          <div class="tw-text-gray-900">
            <span>Math</span><span>PhD</span>
          </div>
        </td>
        <tr><p class="tw-text-gray-500 tw-text-sm tw-my-0">No extras</p></tr>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell">2025-02-01</td>
        <td class="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell"><div>Pending</div></td>
        <a href="https://www.thegradcafe.com/result/67890">Result</a>
      </body>
    </html>
    """
    class DummyResponse:
        def __init__(self, text): self._t = text
        def read(self): return self._t.encode("utf-8")
    monkeypatch.setattr(scrape, "urlopen", lambda url: DummyResponse(fake_html))
    data = scrape.scrape_data(pages=1)
    assert data[0]["gpa"] == "N/A"  # ensures missing fields branch executed