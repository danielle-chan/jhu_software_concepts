Requirements:
* Python 3.10+
* Flask
* beautifulsoup4>=4.12.0
* urllib
* postgresql

You can install Flask with:
python -m pip install Flask

You can install PostgreSQl with:
brew install postgresql
brew services start postgresql
pip3 install "psycopg[binary]"

You can install BeautifulSoup with:
pip install beautifulsoup4

Running the Website
1. Download the module_3 repository to your computer
2. Navigate to the project folder

Create a virtual environment by running the following lines in your terminal:
python -m venv venv
source venv/bin/activate

Run the Flask application in your terminal:
python run.py

Open your Browswer and go to:
http://localhost:8000

File Structure:
* scrape.py - 
* clean.py - 
* load_data.py - Loads data in SQL database
* query_data.py - Queries database to gather statistics on GradCafe data
* append_data.py - Appends new applicants into the database, skipping duplicates
* constraint.py - Ensures constraint is added for URLs to be unique so no duplicates
* run.py - Entry point to run the Flask app
* templates/ - HTML templates
* llm/ - LLM for JSONL creation
* requirements.txt - Python dependencies
* limitations.pdf - Limitations of anonymously submitted data items
* query results.pdf - Descriptions of queries used and why

load_data.py:

query_data.py:

append_data.py and constraint.py:

run.py:

Technicalities and potential bugs:


