import re
from bs4 import BeautifulSoup
from urllib.request import urlopen


def scrape_data(pages=1500):
    all_data = []

    for page_num in range(1, pages + 1):
        url = f"https://www.thegradcafe.com/survey/?page={page_num}"
        print(f"Scraping page {page_num}: {url}")

        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')

        # Program name and Degree type
        program_html = soup.find_all("td", class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500")
        programs =[]
        degree_types = []

        for td in program_html:
            div = td.find("div", class_="tw-text-gray-900")
            if div:
                spans = div.find_all("span")
                if len(spans) > 0:
                    programs.append(spans[0].get_text(strip=True))  # first span = program
                else:
                    programs.append("N/A")
                if len(spans) > 1:
                    degree_types.append(spans[1].get_text(strip=True))  # second span = degree type
                else:
                    degree_types.append("N/A")

        # University
        university_html = soup.find_all('div',class_="tw-font-medium tw-text-gray-900 tw-text-sm")
        universities = [i.get_text(strip=True) for i in university_html]

        # Comments
        rows = soup.find_all("tr")
        comments = []
        for row in rows:
            notes_html = row.find("p", class_="tw-text-gray-500 tw-text-sm tw-my-0")
            if notes_html:
                comments.append(notes_html.get_text(strip=True))
            else:
                comments.append("N/A")

        # Date added and Applicant Status
        date_html = soup.find_all('td',class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell")
        dates_added = []
        statuses = []
        for td in date_html:
            # only keep if it has no <div> inside
            if not td.find("div"):
                text = td.get_text(strip=True)
                if text:  # skip empty ones
                    dates_added.append(text)
            # if it has <div> inside, it's applicant status
            else:
                text = td.get_text(strip=True)
                statuses.append(text)
        
        # Applicant URLs
        applicant_urls = re.findall(r'https://www\.thegradcafe\.com/result/\d+\S*', html)

        # GRE, GPA, Semester, International
        gre_g_scores, gre_v_scores, gre_aw_scores, gpas, semesters, intl_flags = [], [], [], [], [], []
        extra_html = soup.find_all("div", class_=re.compile(r"tw-inline-flex"))

        for tag in extra_html:
            text = tag.get_text(strip=True)

            if text.startswith("GRE V"):
                gre_v_scores.append(text.replace("GRE V", "").strip())
            elif text.startswith("GRE AW"):
                gre_aw_scores.append(text.replace("GRE AW", "").strip())
            elif text.startswith("GRE "):
                gre_g_scores.append(text.replace("GRE", "").strip())
            elif text.startswith("GPA"):
                gpas.append(text.replace("GPA", "").strip())
            elif "Spring" in text or "Fall" in text or "Summer" in text:
                semesters.append(text.strip())
            elif text in ["International", "American"]:
                intl_flags.append(text)

        # stitch them together by index
        for i in range(len(universities)):
            all_data.append({
                "university": universities[i],
                "program": programs[i],
                "degree_type": degree_types[i],
                "comment": comments[i],
                "date_added": dates_added[i],
                "applicant_status": statuses[i],
                "url": applicant_urls[i],
                "gpa": gpas[i] if i < len(gpas) else "N/A",
                "gre_general": gre_g_scores[i] if i < len(gre_g_scores) else "N/A",
                "gre_verbal": gre_v_scores[i] if i < len(gre_v_scores) else "N/A",
                "gre_aw": gre_aw_scores[i] if i < len(gre_aw_scores) else "N/A",
                "semester_start": semesters[i] if i < len(semesters) else "N/A",
                "international_status": intl_flags[i] if i < len(intl_flags) else "N/A",
            })
    return all_data

