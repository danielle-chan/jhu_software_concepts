"""Query the applicants database and print summary statistics."""

from __future__ import annotations
import os
import psycopg
from psycopg import sql

try:
    # If running as part of the worker package
    from .sql_helpers import (  # type: ignore
        SQL_COUNT_JHU_CS_MASTERS,
        SQL_COUNT_GEORGETOWN_CS_PHD_2025,
        SQL_COUNT_GRE_SUBMITTED,
        build_avg_gpa_stmt,
        build_ds_count_stmt,
    )
except Exception:  # pragma: no cover
    # Fallback when running this file directly
    from worker.etl.sql_helpers import (
        SQL_COUNT_JHU_CS_MASTERS,
        SQL_COUNT_GEORGETOWN_CS_PHD_2025,
        SQL_COUNT_GRE_SUBMITTED,
        build_avg_gpa_stmt,
        build_ds_count_stmt,
    )

# DB connection helpers

def _db_dsn() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    db = os.getenv("POSTGRES_DB", "applicants")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

def get_db_connection():
    """Container-friendly DB connector (uses env vars set by docker-compose)."""
    return psycopg.connect(_db_dsn())

# Individual report functions

def report_fall2025_applicants(cur):
    stmt = sql.SQL("""
        SELECT COUNT(*)
        FROM {tbl}
        WHERE term ILIKE {pattern}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"), pattern=sql.Literal("%Fall 2025%"))
    cur.execute(stmt)
    count = cur.fetchone()[0]
    print("Number of Fall 2025 applicants:", count)

def report_international_percentage(cur):
    stmt = sql.SQL("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN us_or_international ILIKE {intl} THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0),
            2
        )
        FROM {tbl}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"), intl=sql.Literal("%International%"))
    cur.execute(stmt)
    pct = cur.fetchone()[0]
    print(
        f"Percentage of international applicants: {pct:.2f}%"
        if pct is not None else
        "Percentage of international applicants: N/A"
    )

def report_average_scores(cur):
    stmt = sql.SQL("""
        SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
        FROM {tbl}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"))
    cur.execute(stmt)
    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

    def fmt(x): return f"{x:.2f}" if x is not None else "No data"

    print("Averages:")
    print("  GPA   :", fmt(avg_gpa))
    print("  GRE   :", fmt(avg_gre))
    print("  GRE V :", fmt(avg_gre_v))
    print("  GRE AW:", fmt(avg_gre_aw))

def report_avg_gpa_american_fall2025(cur):
    stmt = build_avg_gpa_stmt(term="Fall 2025", us_flag="American")
    cur.execute(stmt)
    avg_gpa = cur.fetchone()[0]
    print(
        f"Average GPA of American applicants in Fall 2025: {avg_gpa:.2f}"
        if avg_gpa is not None else
        "Average GPA of American applicants in Fall 2025: N/A"
    )

def report_acceptance_percentage_fall2025(cur):
    stmt = sql.SQL("""
        SELECT 100.0 * COUNT(*) FILTER (WHERE status ILIKE {acc})
               / NULLIF(COUNT(*), 0)
        FROM {tbl}
        WHERE term = {term}
        LIMIT 1
    """).format(
        tbl=sql.Identifier("applicants"),
        acc=sql.Literal("Accepted%"),
        term=sql.Literal("Fall 2025"),
    )
    cur.execute(stmt)
    pct = cur.fetchone()[0]
    print(
        f"Percentage of Fall 2025 entries that are Acceptances: {pct:.2f}%"
        if pct is not None else
        "Percentage of Fall 2025 entries that are Acceptances: N/A"
    )

def report_avg_gpa_accepted_fall2025(cur):
    stmt = build_avg_gpa_stmt(term="Fall 2025", status="%Accepted%")
    cur.execute(stmt)
    avg_gpa_acc = cur.fetchone()[0]
    print(
        f"Average GPA of accepted applicants for Fall 2025: {avg_gpa_acc:.2f}"
        if avg_gpa_acc is not None else
        "Average GPA of accepted applicants for Fall 2025: N/A"
    )

def report_jhu_cs_masters(cur):
    cur.execute(sql.SQL(SQL_COUNT_JHU_CS_MASTERS + " LIMIT 1"))
    count = cur.fetchone()[0]
    print(f"Number of applicants to JHU for a Master's in Computer Science: {count}")

def report_georgetown_cs_phd_acceptances(cur):
    cur.execute(sql.SQL(SQL_COUNT_GEORGETOWN_CS_PHD_2025 + " LIMIT 1"))
    count = cur.fetchone()[0]
    print(f"Number of 2025 Georgetown PhD Computer Science acceptances: {count}")

def report_datascience_fall2025(cur):
    stmt = build_ds_count_stmt(term="%Fall 2025%", program_pattern="%Data Science%")
    cur.execute(stmt)
    ds_apps = cur.fetchone()[0]
    print(f"Number of Fall 2025 Data Science applicants: {ds_apps}")

def report_gre_submitters(cur):
    cur.execute(sql.SQL(SQL_COUNT_GRE_SUBMITTED + " LIMIT 1"))
    count = cur.fetchone()[0]
    print(f"Number of applicants who submitted a GRE score: {count}")


# Main runner


def main():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            report_fall2025_applicants(cur)
            report_international_percentage(cur)
            report_average_scores(cur)
            report_avg_gpa_american_fall2025(cur)
            report_acceptance_percentage_fall2025(cur)
            report_avg_gpa_accepted_fall2025(cur)
            report_jhu_cs_masters(cur)
            report_georgetown_cs_phd_acceptances(cur)
            report_datascience_fall2025(cur)
            report_gre_submitters(cur)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
