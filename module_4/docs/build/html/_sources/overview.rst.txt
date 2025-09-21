Overview & Setup
================

The Grad Cafe application scrapes, cleans, and analyzes admissions data.

Setup Instructions
------------------
1. Clone the repository: ``git clone <your_repo_url>``
2. Create and activate a virtual environment: ``python -m venv venv && source venv/bin/activate``
3. Install requirements: ``pip install -r requirements.txt``

Environment Variables
---------------------
Set the following before running:

- ``DATABASE_URL`` (or ``dbname`` + ``user`` in ``psycopg`` connect)
- ``FLASK_ENV`` (development or production)

Running Tests
-------------
Run all tests:

.. code-block:: bash

   pytest -v --cov=src

To run specific groups:

.. code-block:: bash

   pytest -m "db"
