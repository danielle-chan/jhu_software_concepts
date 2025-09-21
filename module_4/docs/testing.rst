Testing Guide
=============

Tests are grouped with markers for selective runs:

- ``@pytest.mark.web``: Flask page rendering
- ``@pytest.mark.buttons``: Endpoint busy/redirect behavior
- ``@pytest.mark.db``: Database schema, inserts, and constraints
- ``@pytest.mark.integration``: End-to-end ETL + web flows
- ``@pytest.mark.clean``: Data normalization

Run only database tests:

.. code-block:: bash

   pytest -m "db"

Fixtures & Doubles
------------------
- **DummyConn / DummyCursor**: Fake psycopg connections used in ``test_query_data`` and ``test_load_data``.
- **monkeypatch**: Used to override functions like ``scrape_data`` to prevent long runs.
