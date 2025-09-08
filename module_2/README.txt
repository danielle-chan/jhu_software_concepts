Danielle Chan - JHID: F84B10

Module 2 Web Scrape Assignment
Due Date: 09/07/2025 11:59PM


OVERVIEW:
This project scrapes applicant data from The GradCafe and converts the data into a structured JSON format.
* scrape.py gathers raw applicant data
* clean.py cleans and structures the raw applicant data and then saves it into a JSON file
The goal was to build a dataset of at least 30,000 applicant data.


BUGS:
If there are certificate errors on a Mac, run the following line:
/Applications/Python\ 3.13/Install\ Certificates.command


APPROACH:

First, I confirmed that the robot.txt file permits scraping.



scrape.py:
Since each page on The GradCafe has 20 applicant entries, 1500 pages of data were needed to gather at least 30,000 applicant data. 
Therefore, iteratation through each page is needed. The script loops through each page up until the default of page 1500.

To parse through the HTMl, BeautifulSoup was used because it could easily gather the data based off of the tags and regex was used 
because of ease with similar regualr expressions.
* Program name and degree type was extracted from <span>
* University name was extracted from <div> tags 
* Separates date added and application status by checking if <td> contains the nested element <div>
* GRE scores, GPA, semester start, international/US status were found inside <div class="tw-inline-flex"> tags 
    and they were categorized based on prefixes like "GRE V", "GRE AW", "GPA", "Spring", "International".
* Comments were extracted from <p> tags
* Applicant URLs were extracted using regex because the text before the ID number in https://www\.thegradcafe\.com/result/ID remained
    the same across applicant pages

To assemble the data, each applicant's information was stitched together into a dictionary. The result is a list of dictionaries, each 
dictionary belonging to a singular applicant.


clean.py:
clean.py standardizes and structures the raw scraped data from scrape.py.
* clean_data() serves to rename and standardize the raw data and ensures missing values are represented as N/A. The function .get() was 
    used to gather the raw data. Some keys were renamed in this process to be similar to examples from class lecture. The output is a 
    cleaned list of dictionaries with consistent fields:
    * university
    * program
    * degree_type
    * comments
    * date_added
    * status
    * url
    * GPA
    * GRE_G (general)
    * GRE_V (verbal)
    * GRE_AW (analytical writing)
    * term (semester start)
    * US/International
* save_data() serves to saves the cleaned data into a file called cleaned_applicant_data.json
* load_data() serves to reload the JSON file to confirm it saved


USAGE:

1. Scraping the data

To scrape the data, run scrape.py to collect applicant data (default is 1500 pages/30000 applicant entries):
python3 scrape.py

The function scrape_data() returns a list of dictionaries, each representing one applicant entry and the associated data categories.


2. Clean the data

To clean and structure the data, run clean.py:
python3 clean.py

The file will call scrape_data() from scrape.py, clean the data, save the resulting cleaned data into a JSON file called 
cleaned_applicant_data.json, and load the JSON file.


Output:
The output is cleaned_applicant_data.json.










