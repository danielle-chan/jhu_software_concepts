"""Ensure the applicants table has a unique URL constraint."""

import psycopg
from psycopg import Connection, Cursor

def ensure_unique_constraint():
    """Add (or reset) a UNIQUE constraint on the applicants.url column."""
    # pylint: disable=no-member
    conn: Connection = psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )
    cur: Cursor = conn.cursor()

    cur.execute("ALTER TABLE applicants DROP CONSTRAINT IF EXISTS unique_url;")
    cur.execute("ALTER TABLE applicants ADD CONSTRAINT unique_url UNIQUE (url);")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    ensure_unique_constraint()
