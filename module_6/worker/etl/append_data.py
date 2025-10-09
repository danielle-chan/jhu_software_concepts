"""Append new applicant rows to the database from the LLM-standardized JSON/JSONL file."""

from __future__ import annotations
import os
import json
import re
import psycopg
from typing import Iterable, Dict, Any, Optional

# Config
DEFAULT_FILE = os.getenv("DATA_FILE", "/app/data/full_out.jsonl")

def _db_dsn() -> str:
    """Build a Postgres DSN from env; prefer DATABASE_URL if set."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    db = os.getenv("POSTGRES_DB", "applicants")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

# Helpers 
_NUM_RE = re.compile(r'[-+]?\d*\.?\d+')

def _to_float(v: Any) -> Optional[float]:
    """Extract a float from messy strings like '3.9', '160/170', '4.5 (AW)', or return None."""
    if v in (None, "", "N/A"):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    m = _NUM_RE.search(s)
    return float(m.group()) if m else None

def _clean(v: Any) -> Optional[str]:
    """Normalize empty placeholders to None."""
    return None if v in ("N/A", "", None) else v

def _iter_entries(path: str) -> Iterable[Dict[str, Any]]:
    """
    Yield entries from either:
      - JSONL: one JSON object per line, OR
      - JSON array file.
    """
    with open(path, "r", encoding="utf-8") as f:
        # Peek first non-whitespace char
        pos = f.tell()
        first = f.read(1)
        while first.isspace():
            first = f.read(1)
        f.seek(pos)

        if first == "[":
            data = json.load(f)
            for obj in data:
                yield obj
        else:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

# Core 
def append_data(filename: Optional[str] = None) -> int:
    """
    Append new applicants into the database, skipping duplicates by URL.
    Returns the number of attempted inserts (duplicates are ignored by ON CONFLICT).
    """
    path = filename or DEFAULT_FILE

    dsn = _db_dsn()
    conn = psycopg.connect(dsn)
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO applicants (
            program, degree, comments, date_added, status, url,
            gpa, gre, gre_v, gre_aw, term, us_or_international,
            llm_generated_program, llm_generated_university, university
        ) VALUES (
            %(program)s, %(degree)s, %(comments)s, %(date_added)s, %(status)s, %(url)s,
            %(gpa)s, %(gre)s, %(gre_v)s, %(gre_aw)s, %(term)s, %(us_or_international)s,
            %(llm_generated_program)s, %(llm_generated_university)s, %(university)s
        )
        ON CONFLICT (url) DO NOTHING
    """

    n = 0
    try:
        for entry in _iter_entries(path):
            row = {
                "program": _clean(entry.get("program")),
                "degree": _clean(entry.get("degree_type")),
                "comments": _clean(entry.get("comments")),
                "date_added": _clean(entry.get("date_added")),
                "status": _clean(entry.get("status")),
                "url": _clean(entry.get("url")),
                "gpa": _to_float(entry.get("GPA")),
                "gre": _to_float(entry.get("GRE_G")),
                "gre_v": _to_float(entry.get("GRE_V")),
                "gre_aw": _to_float(entry.get("GRE_AW")),
                "term": _clean(entry.get("term")),
                "us_or_international": _clean(entry.get("US/International")),
                "llm_generated_program": _clean(entry.get("llm-generated-program")),
                "llm_generated_university": _clean(entry.get("llm-generated-university")),
                "university": _clean(entry.get("university")),
            }
            cur.execute(insert_sql, row)
            n += 1

        conn.commit()
        return n
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    count = append_data()
    print(f"Attempted inserts: {count}")
