Architecture
============

The GradCafe application is organized into three main layers: **ETL (Extract, Transform, Load)**,
**Database**, and **Web Application**. Each layer is responsible for a different part of the system,
but all work together to provide a clean workflow from scraping data to displaying insights in a web app.

ETL Layer
---------

* **scrape.py**  
  Scrapes raw data from the GradCafe forum using BeautifulSoup.  
  This script is the entry point for data ingestion.

* **clean.py**  
  Cleans and standardizes the scraped data into a structured JSON-like format.  
  Ensures consistent field naming and replaces missing fields with defaults.

* **load_data.py**  
  Loads the cleaned data into a PostgreSQL database. Inserts are structured to
  enforce schema consistency, with unique primary keys ensuring integrity.

Database Layer
--------------

* **query_data.py**  
  Provides query functions for statistics and analysis.  
  Queries include metrics like average GPA, GRE scores, and acceptance rates.  
  Designed to highlight meaningful insights from the dataset.

* **append_data.py**  
  Appends new applicant rows into the database while avoiding duplicates.
  This allows incremental updates without reloading the full dataset.

* **constraint.py**  
  Enforces database-level constraints such as unique URLs.  
  Combined with ``append_data.py``, this ensures data integrity through both
  application-level checks and strict database safeguards.

Web Application Layer
---------------------

* **run.py**  
  Entry point for the Flask web app. Initializes the app, registers routes, and
  sets the ``secret_key`` (needed for flash messages).  
  It exposes the cleaned and queried GradCafe data via a browser interface, while
  keeping scraping, loading, and querying logic modular and testable.

Summary
-------

- **ETL**: Scraping, cleaning, and loading raw GradCafe data into PostgreSQL.  
- **Database**: Querying, appending, and enforcing constraints on applicant data.  
- **Web App**: Serving queries and statistics to users through a Flask application.
