Danielle Chan - JHID: F84B10
Module 5
Due Date: 09/28/2025 11:59PM

Overview:
This module enhances the GradCafe ETL + Web Application by adding:
* Improved SQL query structure via a dedicated `sql_helpers.py` module
* Refactored code to reach top linting scores (`pylint`: 10/10 for `src`)
* Dependency graph visualization with `pydeps` and `graphviz`
* Supply-chain security analysis using Snyk
* Updated README, requirements, and pylint reports

The system still follows the ETL pipeline:
* Scraping forum posts
* Cleaning and normalizing data
* Loading into a PostgreSQL database
* Querying and presenting statistics in a Flask app

Requirements
* Python 3.13  
* PostgreSQL (installed and running locally)
* Python packages (install via `requirements.txt`):
    * Flask>=2.0
    * psycopg[binary]>=3.1
    * beautifulsoup4>=4.12.0
    * pytest
    * pytest-cov
    * sphinx
    * sphinx-rtd-theme
    * graphviz
    * pylint
    * pydeps


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
    * sql_helpers.py → Centralize SQL statements for reuse
* tests/ → Pytest test suite
* docs/ → Sphinx documentation (built on ReadTheDocs)
* .github/workflows/tests.yml → CI workflow
* snyk-analysis.png  → Proof of clean dependency scan
* pylint_src_report.txt → Linting report for src
* pylint_tests_report.txt → Linting report for tests

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

Static Analysis:
* pylint for src/ → 10/10
* pyliny for tests/ → 9/96/10 (slight deduction due to unavaoidable duplicate test setup)

Dependeny Graph
Created using:
pydeps src/run.py --output dependency.svg

The graph shows run.py as the central controller connecting:
Flask → for web interface
psycopg → for secure DB connections
subprocess → to run ETL scripts
append_data and sql_helpers → for data loading & query reuse
This star-like structure confirms a clean separation of concerns and avoids circular dependencies

Security Scan
Used Snyk to analyze the environment and requirements.txt:
snyk auth
snyk test
* Result: No known malicious or vulnerable packages detected
* Proof included as snyk-analysis.png

Continuous Integration
Configured GitHub Actions workflow:
* Installs dependencies
* Starts PostgreSQL service
* Runs pytest
* Runs pylint for linting

Documentation
Documentation is built with Sphinx and hosted on ReadTheDocs.
To build locally:
cd docs
make html
open build/html/index.html

Docs include:
* Setup Guide → Installation, running app/tests
* Architecture → ETL + Web + DB overview
* API Reference → Auto-generated docs for each module
* Testing Guide → Markers, coverage & CI/CD details


Issues Encountered
* Initial SQL queries caused syntax errors (LIMIT placement) — resolved by consolidating into sql_helpers.py
* Too-many-locals & duplicate-code warnings fixed by refactoring and adding # pylint: disable=duplicate-code where needed
* Import-path issues in tests resolved by consistent sys.path setup
