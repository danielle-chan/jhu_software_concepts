from bs4 import BeautifulSoup
from urllib.request import urlopen

# Graduate Cafe Survey results
url = "https://thegradcafe.com/survey/"

# Open webpage
page = urlopen(url)

# Extract HTML from the page
html_bytes = page.read()
html = html_bytes.decode("utf-8")
soup = BeautifulSoup(html, 'html.parser')

# Find all the program names
program_html = soup.find_all("td", class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500")
programs =[]
for td in program_html:
    div = td.find("div", class_="tw-text-gray-900")
    if div:
        first_span = div.find("span")
        if first_span:  # only grab the first <span>
            programs.append(first_span.get_text(strip=True))

print(programs)

# Find all the university names
university_html = soup.find_all('div',class_="tw-font-medium tw-text-gray-900 tw-text-sm")
universities = [i.get_text(strip=True) for i in university_html]
print(universities)

# Comments
#note_html = soup.find_all('p',class_="tw-text-gray-500 tw-text-sm tw-my-0")
#notes = [i.get_text(strip=True) for i in note_html]
#print(notes) # only grabs if there are notes. need to be N/A if not notes

# Date of information Added to Grad Cafe and Applicant Status
date_html = soup.find_all('td',class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500 tw-whitespace-nowrap tw-hidden md:tw-table-cell")
dates_added = []
applicant_status = []
for td in date_html:
    # only keep if it has no <div> inside
    if not td.find("div"):
        text = td.get_text(strip=True)
        if text:  # skip empty ones
            dates_added.append(text)
    # if it has <div> inside, it's applicant status
    else:
        text = td.get_text(strip=True)
        applicant_status.append(text)
print(dates_added)
print(applicant_status)

# URL Link to the applicant entry
link_html = soup.find_all('a',href=True,class_="")
link = [i.get_text(strip=True) for i in link_html]
#print(link)



