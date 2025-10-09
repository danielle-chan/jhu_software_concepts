"""Load cleaned and standardized GradCafe applicant data into the PostgreSQL database."""

import os
import json
import psycopg
from psycopg import sql
import re

DEFAULT_FILE = "/app/data/full_out.jsonl"

def _iter_records(file_path):
    # JSONL: one JSON object per line
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def ensure_watermark_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_watermarks (
            source TEXT PRIMARY KEY,
            last_seen TEXT,
            updated_at TIMESTAMPTZ DEFAULT now()
        );
    """)

def to_float(v):
    """Return a float or None from messy numeric strings like '3.9', '320', '160/170', '4.5 (AW)', 'N/A'."""
    if v in (None, "", "N/A"):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    m = re.search(r'[-+]?\d*\.?\d+', s)  # first number in the string
    return float(m.group()) if m else None

# pylint: disable=no-member

DB_NAME = os.getenv("POSTGRES_DB", "applicants")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

DEFAULT_FILE = "/app/data/full_out.jsonl"

def load_data_from_jsonl(file_path=DEFAULT_FILE):
    """Truncate the applicants table and load all rows from the given JSONL file."""

    conn = psycopg.connect(  # pylint: disable=no-member
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
    )
    cur = conn.cursor() # pylint: disable=no-member

    ensure_watermark_table(cur)

    # --- Step 1: Clear old data
    truncate_stmt = sql.SQL("TRUNCATE TABLE {tbl}").format(
        tbl=sql.Identifier("applicants")
    )
    cur.execute(truncate_stmt)

    # --- Step 2: Prepare INSERT statement
    insert_stmt = sql.SQL("""
        INSERT INTO {tbl} (
            program, degree, comments, date_added, status, url,
            gpa, gre, gre_v, gre_aw, term, us_or_international,
            llm_generated_program, llm_generated_university, university
        )
        VALUES (
            {program}, {degree}, {comments}, {date_added}, {status}, {url},
            {gpa}, {gre}, {gre_v}, {gre_aw}, {term}, {us_or_international},
            {llm_prog}, {llm_uni}, {university}
        )
        ON CONFLICT (url) DO NOTHING
    """).format(
        tbl=sql.Identifier("applicants"),
        program=sql.Placeholder(),
        degree=sql.Placeholder(),
        comments=sql.Placeholder(),
        date_added=sql.Placeholder(),
        status=sql.Placeholder(),
        url=sql.Placeholder(),
        gpa=sql.Placeholder(),
        gre=sql.Placeholder(),
        gre_v=sql.Placeholder(),
        gre_aw=sql.Placeholder(),
        term=sql.Placeholder(),
        us_or_international=sql.Placeholder(),
        llm_prog=sql.Placeholder(),
        llm_uni=sql.Placeholder(),
        university=sql.Placeholder(),
    )

    # --- Step 3: Helper for cleaning values
    def clean_val(v):
        return None if v in ("N/A", "", None) else v

    # --- Step 4: Insert rows
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)

            cur.execute(
                insert_stmt,
                (
                    clean_val(entry.get("program")),
                    clean_val(entry.get("degree_type")),
                    clean_val(entry.get("comments")),
                    clean_val(entry.get("date_added")),
                    clean_val(entry.get("status")),
                    clean_val(entry.get("url")),
                    to_float(entry.get("GPA")),
                    to_float(entry.get("GRE_G")),
                    to_float(entry.get("GRE_V")),
                    to_float(entry.get("GRE_AW")),
                    clean_val(entry.get("term")),
                    clean_val(entry.get("US/International")),
                    clean_val(entry.get("llm-generated-program")),
                    clean_val(entry.get("llm-generated-university")),
                    clean_val(entry.get("university")),
                )
            )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    load_data_from_jsonl()
