Danielle Chan - JHID: F84B10
Module 4
Due Date: 09/22/2025 11:59PM

Overview:
This module extends the GradCafe ETL + Web Application project with comprehensive testing and Sphinx documentation.
It includes unit/integration tests using pytest, coverage reporting, and auto-generated documentation via Read the Docs.

The system still follows the ETL pipeline:
* Scraping forum posts
* Cleaning and normalizing data
* Loading into a PostgreSQL database
* Querying and presenting statistics in a Flask app

Requirements
* Python 3.13
* PostgreSQL (installed and running locally)
* Python libraries:
    * Flask>=2.0
    * beautifulsoup4>=4.12.0
    * psycopg[binary]>=3.1
    * pytest>=8.0, pytest-cov>=4.0
    * sphinx>=8.0, sphinx-rtd-theme>=2.0

Install everything with:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Running the App
1. Start PostgreSQL and create the database:
    createdb applicants
2. Run the ETL pipeline manually:
    python src/scrape.py
    python src/clean.py
    python src/load_data.py
3. Launch the Flask app:
    python src/run.py
App available at: http://127.0.0.1:8000


File Structure:
* src/
    * scrape.py → Scrape GradCafe posts
    * clean.py → Clean/normalize raw data
    * load_data.py → Insert into PostgreSQL
    * query_data.py → Queries/statistics
    * append_data.py → Incremental inserts
    * constraint.py → Database-level uniqueness checks
    * run.py → Flask app entry point
* tests/ → Pytest test suite
* docs/ → Sphinx documentation (built on ReadTheDocs)
* .github/workflows/tests.yml → CI workflow

Testing
This project uses pytest with coverage.
Run full test suite with:
    pytest --cov=src --cov-report=term-missing

Markers (configured in pytest.ini):
* web → Flask routes and HTML checks
* buttons → Button endpoints and busy states
* analysis → Formatting & labeling tests
* db → Database schema/inserts/selects
* integration → End-to-end ETL flows
* clean → Data normalization & save/load
* scrape → HTML parsing with fake urlopen
* load → Database insert tests
* query → SQL query tests

Issues Encountered
* Could not sustain 100% coverage due to __main__ blocks (Flask app run code not easily testable).
* Several import path problems arose when mixing src/ package imports with test discovery.
* Mocking database connections worked for some tests, but Postgres-required tests failed in CI.

Continuous Integration (CI/CD)
* A minimal GitHub Actions workflow (.github/workflows/tests.yml) was added.
* It installs dependencies, starts PostgreSQL, and runs pytest.

Issues Encountered
* Initial workflow failed due to missing requirements.txt path.
* PostgreSQL service setup was inconsistent — psycopg.connect couldn’t always find the socket in CI.
* Final runs show partial failures in DB-related tests, while web and ETL tests pass.
* Future fix: use a test database URI and seed lightweight test data.

Documentation:
Documentation is built with Sphinx and hosted on ReadTheDocs.

To build locally:
cd module_4/docs
make html
open build/html/index.html

Docs include:
* Overview & Setup → Installation, environment vars, how to run app/tests
* Architecture → ETL + Web + DB design breakdown
* API Reference → Autodoc pages for scrape.py, clean.py, load_data.py, query_data.py, append_data.py, constraint.py, run.py
* Testing Guide → Markers, pytest usage, mocks

Issues Encountered
* API Reference page is blank due to import errors (src not on path). 
* Could not auto-document all functions due to missing docstrings (modules still imported, but details sparse).

Known Limitations:
* Coverage below 100% (Flask __main__ entry points untestable).
* GitHub Actions workflow does not fully support DB tests due to Postgres service mismatch.
* API Reference is minimal.