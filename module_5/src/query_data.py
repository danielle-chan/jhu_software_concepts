"""Query the applicants database and print summary statistics."""

import psycopg
from psycopg import sql

from src.sql_helpers import (
    SQL_COUNT_JHU_CS_MASTERS,
    SQL_COUNT_GEORGETOWN_CS_PHD_2025,
    SQL_COUNT_GRE_SUBMITTED,
    build_avg_gpa_stmt,
    build_ds_count_stmt,
)


# pylint: disable=no-member

def get_connection():
    """Return a connection to the applicants database."""
    return psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )


# ---------------------------
# Individual report functions
# ---------------------------

def report_fall2025_applicants(cur):
    """Print the number of Fall 2025 applicants."""
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
    """Print the percentage of international applicants."""
    stmt = sql.SQL("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN us_or_international ILIKE {intl} THEN 1 ELSE 0 END) / COUNT(*),
            2
        )
        FROM {tbl}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"), intl=sql.Literal("%International%"))
    cur.execute(stmt)
    pct = cur.fetchone()[0]
    if pct is not None:
        print(f"Percentage of international applicants: {pct:.2f}%")
    else:
        print("No applicants in the database.")


def report_average_scores(cur):
    """Print average GPA and GRE scores."""
    stmt = sql.SQL("""
        SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
        FROM {tbl}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"))
    cur.execute(stmt)
    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

    print("Averages:")
    print(f"  GPA   : {avg_gpa:.2f}" if avg_gpa else "  GPA   : No data")
    print(f"  GRE   : {avg_gre:.2f}" if avg_gre else "  GRE   : No data")
    print(f"  GRE V : {avg_gre_v:.2f}" if avg_gre_v else "  GRE V : No data")
    print(f"  GRE AW: {avg_gre_aw:.2f}" if avg_gre_aw else "  GRE AW: No data")


def report_avg_gpa_american_fall2025(cur):
    """Print average GPA of American applicants in Fall 2025."""
    stmt_avg_gpa_american = build_avg_gpa_stmt(term="Fall 2025", us_flag="American")
    cur.execute(stmt_avg_gpa_american)
    avg_gpa = cur.fetchone()[0]
    if avg_gpa is not None:
        print(f"Average GPA of American applicants in Fall 2025: {avg_gpa:.2f}")
    else:
        print("No GPA data available for American applicants in Fall 2025.")


def report_acceptance_percentage_fall2025(cur):
    """Print acceptance percentage for Fall 2025 applicants."""
    stmt = sql.SQL("""
        SELECT 100.0 * COUNT(*) FILTER (WHERE status ILIKE {acc}) / COUNT(*)
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
    if pct is not None:
        print(f"Percentage of Fall 2025 entries that are Acceptances: {pct:.2f}%")
    else:
        print("No entries found for Fall 2025.")


def report_avg_gpa_accepted_fall2025(cur):
    """Print average GPA of accepted Fall 2025 applicants."""
    stmt_avg_gpa_accepted = build_avg_gpa_stmt(term="Fall 2025", status="%Accepted%")
    cur.execute(stmt_avg_gpa_accepted)
    avg_gpa_acc = cur.fetchone()[0]
    if avg_gpa_acc is not None:
        print(f"Average GPA of accepted applicants for Fall 2025: {avg_gpa_acc:.2f}")
    else:
        print("No data available for accepted Fall 2025 applicants.")


def report_jhu_cs_masters(cur):
    """Print number of applicants to JHU for a Master's in CS."""
    cur.execute(sql.SQL(SQL_COUNT_JHU_CS_MASTERS + " LIMIT 1"))
    count = cur.fetchone()[0]
    print(f"Number of applicants to JHU for a Master's in Computer Science: {count}")


def report_georgetown_cs_phd_acceptances(cur):
    """Print number of 2025 Georgetown PhD CS acceptances."""
    cur.execute(sql.SQL(SQL_COUNT_GEORGETOWN_CS_PHD_2025 + " LIMIT 1"))
    count = cur.fetchone()[0]
    print(f"Number of 2025 Georgetown PhD Computer Science acceptances: {count}")


def report_datascience_fall2025(cur):
    """Print number of Fall 2025 Data Science applicants."""
    stmt_ds = build_ds_count_stmt(term="%Fall 2025%", program_pattern="%Data Science%")
    cur.execute(stmt_ds)
    ds_apps = cur.fetchone()[0]
    print(f"Number of Fall 2025 Data Science applicants: {ds_apps}")


def report_gre_submitters(cur):
    """Print number of applicants who submitted any GRE score."""
    cur.execute(sql.SQL(SQL_COUNT_GRE_SUBMITTED + " LIMIT 1"))
    count = cur.fetchone()[0]
    print(f"Number of applicants who submitted a GRE score: {count}")


# ---------------------------
# Main runner
# ---------------------------

def main():
    """Run all reports in sequence."""
    conn = get_connection()
    cur = conn.cursor()

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

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
