import re
from bs4 import BeautifulSoup
from urllib.request import urlopen

#url = "https://www.thegradcafe.com/survey/"
#page = urlopen(url)
#html_bytes = page.read()
#html = html_bytes.decode("utf-8")
#soup = BeautifulSoup(html, 'html.parser')
applicant_urls = "https://www.thegradcafe.com/result/986418#insticator-commenting"

# GPA
gpas =[]
app_page = urlopen(applicant_urls)
app_html_bytes = app_page.read()
app_html = app_html_bytes.decode("utf-8")
app_soup = BeautifulSoup(app_html, 'html.parser')

gpa_html = app_soup.find("div", class_="tw-mt-1 tw-text-sm tw-leading-6 tw-text-gray-700 sm:tw-mt-2")
if gpa_html:
    text = gpa_html.get_text(strip=True)
else:
    text = "N/A"
gpas.append(text)

print(gpas)

print(html)