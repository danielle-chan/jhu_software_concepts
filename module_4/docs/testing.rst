Testing Guide
=============

This project uses **pytest** for automated testing, with coverage reporting
enabled via **pytest-cov**.

Running Tests
-------------

To run the entire suite with coverage:

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

This will show which lines of code are covered and highlight any missing coverage.

Markers
-------

Tests are organized into categories using ``pytest.ini`` markers:

- ``web`` → Page load / HTML structure  
- ``buttons`` → Button endpoints & busy-state behavior  
- ``analysis`` → Labels and percentage formatting  
- ``db`` → Database schema/inserts/selects  
- ``integration`` → End-to-end flows  
- ``clean`` → Data normalization, save/load  
- ``scrape`` → HTML parsing, fake urlopen  
- ``load`` → File insert, DB mock  
- ``query`` → SQL queries / reporting  

Examples
--------

Run only the **query** tests:

.. code-block:: bash

   pytest -m query

Run both **scrape** and **clean** tests:

.. code-block:: bash

   pytest -m "scrape or clean"

Fixtures & Test Doubles
-----------------------

Several tests use **test doubles** instead of real database or scraping calls:

- ``DummyConn`` and ``DummyCursor`` simulate a database connection for
  ``query_data.py``.  
- Monkeypatching replaces heavy operations with mocks, e.g.:
  - Fake versions of ``scrape_data`` return a small test dataset.
  - Flask's ``app.run()`` is replaced with a no-op to prevent blocking.

Expected Selectors
------------------

Some tests assert on specific selectors or strings in the rendered HTML:

- **Buttons page**: looks for "Pull Data" and "Update Analysis".  
- **Analysis page**: checks for formatted percentages and "Answer:" labels.  

CI/CD Integration
-----------------

Coverage must remain at **100%**, enforced by the ``--cov-fail-under=100`` setting
in ``pytest.ini``. Any new code should include tests to maintain this threshold.

