"""Scrape GradCafe applicant data."""

# pylint: disable=too-many-locals, too-many-branches, invalid-name

from urllib.request import urlopen
import re
from bs4 import BeautifulSoup


def fetch_page_html(page_num):
    """Fetch raw HTML for a given page number."""
    url = f"https://www.thegradcafe.com/survey/?page={page_num}"
    with urlopen(url) as page:
        return page.read().decode("utf-8")


def scrape_data(pages=1500):
    """Scrape applicant data from multiple pages into a list of dicts."""
    results = []

    for page_num in range(1, pages + 1):
        soup = BeautifulSoup(fetch_page_html(page_num), "html.parser")

        # Collect all field lists in dictionaries
        main = {
            "universities": [d.get_text(strip=True) for d in soup.find_all(
                "div", class_="tw-font-medium tw-text-gray-900 tw-text-sm")],
            "programs": [],
            "degree_types": [],
            "comments": [],
            "dates": [],
            "statuses": [],
            "urls": re.findall(r'https://www\.thegradcafe\.com/result/\d+\S*', str(soup))
        }

        # Parse program/degree
        for td in soup.find_all("td", class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500"):
            div = td.find("div", class_="tw-text-gray-900")
            if div:
                spans = div.find_all("span")
                main["programs"].append(spans[0].get_text(strip=True) if spans else "N/A")
                main["degree_types"].append(
                    spans[1].get_text(strip=True) if len(spans) > 1 else "N/A"
                )

        # Parse comments
        for row in soup.find_all("tr"):
            note = row.find("p", class_="tw-text-gray-500 tw-text-sm tw-my-0")
            main["comments"].append(note.get_text(strip=True) if note else "N/A")

        # Parse dates and statuses
        for td in soup.find_all(
            "td",
            class_="tw-px-3 tw-py-5 tw-text-sm "
                   "tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell"
        ):
            if td.find("div"):
                main["statuses"].append(td.get_text(strip=True))
            else:
                txt = td.get_text(strip=True)
                if txt:
                    main["dates"].append(txt)

        # Parse extra fields with fewer branches
        extras = {"gpa": [], "gre_g": [], "gre_v": [], "gre_aw": [], "semester": [], "intl": []}
        PATTERNS = [
            ("GRE V", "gre_v"),
            ("GRE AW", "gre_aw"),
            ("GRE ", "gre_g"),
            ("GPA", "gpa"),
        ]

        for tag in soup.find_all("div", class_=re.compile(r"tw-inline-flex")):
            txt = tag.get_text(strip=True)

            matched = False
            for prefix, key in PATTERNS:
                if txt.startswith(prefix):
                    extras[key].append(txt.replace(prefix, "").strip())
                    matched = True
                    break

            if not matched:
                if any(season in txt for season in ("Spring", "Fall", "Summer")):
                    extras["semester"].append(txt.strip())
                elif txt in ("International", "American"):
                    extras["intl"].append(txt)

        # Stitch final records
        for i, uni in enumerate(main["universities"]):
            results.append({
                "university": uni,
                "program": main["programs"][i] if i < len(main["programs"]) else "N/A",
                "degree_type": main["degree_types"][i] if i < len(main["degree_types"]) else "N/A",
                "comment": main["comments"][i] if i < len(main["comments"]) else "N/A",
                "date_added": main["dates"][i] if i < len(main["dates"]) else "N/A",
                "applicant_status": main["statuses"][i] if i < len(main["statuses"]) else "N/A",
                "url": main["urls"][i] if i < len(main["urls"]) else "N/A",
                "gpa": extras["gpa"][i] if i < len(extras["gpa"]) else "N/A",
                "gre_general": extras["gre_g"][i] if i < len(extras["gre_g"]) else "N/A",
                "gre_verbal": extras["gre_v"][i] if i < len(extras["gre_v"]) else "N/A",
                "gre_aw": extras["gre_aw"][i] if i < len(extras["gre_aw"]) else "N/A",
                "semester_start": extras["semester"][i] if i < len(extras["semester"]) else "N/A",
                "international_status": extras["intl"][i] if i < len(extras["intl"]) else "N/A",
            })

    return results

if __name__ == "__main__":
    scrape_data(5)
