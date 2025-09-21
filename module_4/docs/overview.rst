Overview & Setup
================

This project implements an **ETL + Web Application pipeline** for analyzing
applicant data scraped from the GradCafe forum. It combines scraping,
cleaning, database loading, and a Flask web app to expose statistics.

Requirements
------------

The project requires:

* Python 3.13 (tested)  
* PostgreSQL database  
* A virtual environment with the dependencies listed in ``requirements.txt``  

Setup
-----

1. **Set Up Virtual Environment**:

   .. code-block:: bash

      python3 -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt

2. **Set up PostgreSQL**:  
   Ensure PostgreSQL is installed and running locally.  
   Create a database named ``applicants``:

   .. code-block:: bash

      createdb applicants

3. **Environment Variables**:

   The application connects to PostgreSQL using ``psycopg``.  
   By default, connection settings are hardcoded as:

   .. code-block:: text

      dbname=applicants
      user=<your-username>

Running the Application
-----------------------

1. **Scrape, clean, and load data**:

   .. code-block:: bash

      python src/scrape.py
      python src/clean.py
      python src/load_data.py

2. **Run the Flask web app**:

   .. code-block:: bash

      python src/run.py

   The app will be available at: http://127.0.0.1:8000

Testing
-------

This project uses **pytest** for testing.

* To run all tests with coverage:

  .. code-block:: bash

     pytest --cov=src --cov-report=term-missing

* Tests are **marked** by category in ``pytest.ini``:

  - ``web`` → Page load / HTML structure  
  - ``buttons`` → Button endpoints & busy-state behavior  
  - ``analysis`` → Labels and percentage formatting  
  - ``db`` → Database schema/inserts/selects  
  - ``integration`` → End-to-end flows  
  - ``clean`` → Data normalization, save/load  
  - ``scrape`` → HTML parsing, fake urlopen  
  - ``load`` → File insert, DB mock  
  - ``query`` → SQL queries / reporting  

* Example: Run only the query tests:

  .. code-block:: bash

     pytest -m query

* Some tests use **test doubles**:
  - ``DummyConn`` and ``DummyCursor`` simulate a database connection for
    ``query_data.py``.
  - Monkeypatching is used to replace scraping/DB calls with lightweight mocks.
