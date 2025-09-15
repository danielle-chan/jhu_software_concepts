Danielle Chan - JHID: F84B10
Module 3: SQL Data Analysis Assignment
Due Date: 09/14/2025 11:59PM

Overview:
This project scrapes the GradCafe data, cleans it, loads it in a PostgreSQL database, and provides a 
Flask web interface for running queries and viewing analysis

Requirements:
* Python 3.10+
* Flask>=2.0
* beautifulsoup4>=4.12.0
* psycopg[binary]>=3.1
* PostgreSQL (installed on your system)

Installation:
1. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate

2. Then install the required Python packages:
pip install -r requirements.txt

3. Install PostgreSQL (Mac)
brew install postgresql
brew services start postgresql
pip3 install "psycopg[binary]"

4. Install BeautifulSoup
pip install beautifulsoup4

Running the Website
1. Download the module_3 repository to your computer
2. Navigate to the project folder
3. Run the Flask application:
    python run.py
4. Open your browser and go to http://localhost:8000

File Structure:
* scrape.py - Scrapes raw GradCafe data
* clean.py - Cleans and standardizes the scraped data
* load_data.py - Loads data in SQL database
* query_data.py - Queries database to gather statistics on GradCafe data
* append_data.py - Appends new applicants into the database, skipping duplicates
* constraint.py - Ensures URLs are unique in the database
* run.py - Entry point to run the Flask app
* templates/ - HTML templates for the web app
* llm/ - LLM for JSONL creation
* requirements.txt - Python dependencies
* limitations.pdf - Limitations of anonymously submitted data items
* query results.pdf - Descriptions of queries used and why

Approach:
* load_data.py: Responsible for taking cleaned data and inserting it into the PostgreSQL database.
The approach was to structure the inserts in a way that would ensure consistent schema usage, 
with constraints handled by the database through unique primary keys. 

* query_data.py: Handles all database queries for statistics and analysis. Queries were chosen to 
highlight meaningful statistics in the GradCafe dataset. See 'query results.pdf' for further explanation.

* append_data.py and constraint.py: Together these scripts handle incremental data updates.
- `append_data.py` was designed to add new applicants without reloading the entire dataset, 
  which saves time and reduces database overhead.
- `constraint.py` enforces uniqueness at the database level by setting a constraint on URLs. 
  This guarantees no duplicate rows slip in, even if the append process misses something. 
The thought process was to combine application-level checks with database-level safeguards.

* run.py: This is the entry point of the Flask web application. It initializes the Flask app, registers 
routes, sets the `secret_key` (needed for flash messages), and starts the development server. The logic for 
scraping, loading, and querying remains modular and testable outside the Flask context.

Technicalities and potential bugs:
* The LLM can be slow when processing large JSON files
* Duplicate data is prevented at the database level with a unique identifier.
* When clicking the "Pull Data" button on the web app, loading may take a long time to load. This is 
partially because of the order in which I wrote my program to run. Duplicates are currently removed after 
the JSONL file is created. A potentially more efficient design would remove duplicates before JSONL 
creation, which could reduce latency when datasets overlap. If there are no overlaps, latency would 
remain an issue.
* Flash messages require Flask’s `secret_key` to be set (already included in `run.py`). 
* If you forget to start PostgreSQL, the app will fail to connect and queries won't be executed.