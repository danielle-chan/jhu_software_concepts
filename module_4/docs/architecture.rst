Architecture
============

The application is divided into three layers:

- **Web Layer**: Flask routes in ``run.py`` handle user interactions, trigger ETL steps, and render templates.
- **ETL Layer**:
   - ``scrape.py`` collects raw data.
   - ``clean.py`` normalizes and validates fields.
   - ``load_data.py`` inserts JSONL/structured data into PostgreSQL.
- **Database Layer**: ``query_data.py`` and ``constraint.py`` handle querying and schema enforcement.

This separation supports modular testing and allows reuse of ETL outside the web app.
