"""Ensure the applicants table has a unique URL constraint."""

import os
import psycopg
from psycopg import Connection, Cursor

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "applicants"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )

def ensure_unique_constraint():
    """Add (or reset) a UNIQUE constraint on the applicants.url column."""
    # pylint: disable=no-member
    conn: Connection = get_db_connection()
    cur: Cursor = conn.cursor() # pylint: disable=no-member

    cur.execute("ALTER TABLE applicants DROP CONSTRAINT IF EXISTS unique_url;")
    cur.execute("ALTER TABLE applicants ADD CONSTRAINT unique_url UNIQUE (url);")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    ensure_unique_constraint()
