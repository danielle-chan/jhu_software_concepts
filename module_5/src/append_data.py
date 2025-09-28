"""Append new applicant rows to the database from the LLM-standardized JSONL file."""

import json
import psycopg
from psycopg import Connection, Cursor, sql

# pylint: disable=no-member

def append_data(filename="llm_hosting/full_out.jsonl"):
    """Append new applicants into the database, skipping duplicates by URL."""

    conn: Connection = psycopg.connect( # pylint: disable=no-member
        dbname="applicants",
        user="daniellechan",
    )
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
