"""Append new applicant rows to the database from the LLM-standardized JSONL file."""

import os
import json
import psycopg
from psycopg import Connection, Cursor, sql

# pylint: disable=no-member

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "applicants"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )

def _iter_entries(filename: str):
    """Yield entries from either JSONL (one JSON object per line) or a JSON array file."""
    with open(filename, "r", encoding="utf-8") as f:
        first_char = f.read(1)
        f.seek(0)
        if first_char == "[":
            # JSON array
            data = json.load(f)
            for obj in data:
                yield obj
        else:
            # JSONL
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)


def append_data(filename="/data/full_out.json"):
    """Append new applicants into the database, skipping duplicates by URL."""

    conn: Connection = get_db_connection()
    cur: Cursor = conn.cursor() # pylint: disable=no-member

    def clean_val(v):
        """Return None for empty/N/A values."""
        return None if v in ("N/A", "", None) else v

    # Build the INSERT statement using psycopg.sql
    insert_stmt = sql.SQL("""
        INSERT INTO {table} (
            program, degree, comments, date_added, status, url,
            gpa, gre, gre_v, gre_aw, term, us_or_international,
            llm_generated_program, llm_generated_university, university
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        ON CONFLICT (url) DO NOTHING
    """).format(
        table=sql.Identifier("applicants")
    )

    # Read JSONL and insert each row
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)

            values = (
                clean_val(entry.get("program")),
                clean_val(entry.get("degree_type")),
                clean_val(entry.get("comments")),
                clean_val(entry.get("date_added")),
                clean_val(entry.get("status")),
                clean_val(entry.get("url")),
                clean_val(entry.get("GPA")),
                clean_val(entry.get("GRE_G")),
                clean_val(entry.get("GRE_V")),
                clean_val(entry.get("GRE_AW")),
                clean_val(entry.get("term")),
                clean_val(entry.get("US/International")),
                clean_val(entry.get("llm-generated-program")),
                clean_val(entry.get("llm-generated-university")),
                clean_val(entry.get("university")),
            )

            cur.execute(insert_stmt, values)

    conn.commit()
    cur.close()
    conn.close()
