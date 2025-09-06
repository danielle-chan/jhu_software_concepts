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

        # Program name
        program_html = soup.find_all("td", class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500")
        programs =[]
        for td in program_html:
            div = td.find("div", class_="tw-text-gray-900")
            if div:
                first_span = div.find("span")
                if first_span:  # only grab the first <span>
                    programs.append(first_span.get_text(strip=True))

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
        urls = re.findall(r'https://www\.thegradcafe\.com/result/\d+\S*', html)

        # stitch them together by index
        for i in range(min(len(universities), len(programs), len(comments), len(dates_added), len(statuses), len(urls))):
            all_data.append({
                "university": universities[i],
                "program": programs[i],
                "comment": comments[i],
                "date_added": dates_added[i],
                "status": statuses[i],
                "url": urls[i]
            })
    return all_data

data = scrape_data(pages=1)
print(len(data), "entries")
print(data[:2])





# Graduate Cafe Survey results
#url = "https://thegradcafe.com/survey/"

# Open webpage
#page = urlopen(url)

# Extract HTML from the page
#html_bytes = page.read()
#html = html_bytes.decode("utf-8")
#soup = BeautifulSoup(html, 'html.parser')

# Find all the program names
#program_html = soup.find_all("td", class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500")
#programs =[]
#for td in program_html:
#    div = td.find("div", class_="tw-text-gray-900")
#    if div:
#        first_span = div.find("span")
#        if first_span:  # only grab the first <span>
#            programs.append(first_span.get_text(strip=True))

#print(programs)

# Find all the university names
#university_html = soup.find_all('div',class_="tw-font-medium tw-text-gray-900 tw-text-sm")
#universities = [i.get_text(strip=True) for i in university_html]
#print(universities)

# Find all the comments
#rows = soup.find_all("tr")

#comments = []
#for row in rows:
#    notes_html = row.find("p", class_="tw-text-gray-500 tw-text-sm tw-my-0")
#    if notes_html:
#        comments.append(notes_html.get_text(strip=True))
#    else:
#        comments.append("N/A")
#print(comments)

# Find all the Date of information Added to Grad Cafe and Applicant Status
#date_html = soup.find_all('td',class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell")
#dates_added = []
#applicant_status = []
#for td in date_html:
#    # only keep if it has no <div> inside
#    if not td.find("div"):
#        text = td.get_text(strip=True)
#        if text:  # skip empty ones
#            dates_added.append(text)
#    # if it has <div> inside, it's applicant status
#    else:
#        text = td.get_text(strip=True)
#        applicant_status.append(text)
#print(dates_added)
#print(applicant_status)

# URL Link to the applicant entry
#applicant_urls = re.findall(r'https://www\.thegradcafe\.com/result/\d+\S*', html)
#print(applicant_urls)

# Semester and Year of Program Start

# GRE Score

# GRE V Score

# Masters or PhD

# GPA

# GRE AW

# use to search HTML
#search_term = "North Dakota"
#if search_term in html:
#    print(f'"{search_term}" found in HTML!')
#    # Get position of first match
#    idx = html.index(search_term)
#    # Print 300 characters before and after
#    snippet = html[idx-1000: idx+13000]
#    print(snippet)
#else:
#    print(f'"{search_term}" not found in HTML.')