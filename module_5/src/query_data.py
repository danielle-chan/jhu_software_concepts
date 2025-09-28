"""Query the applicants database and print summary statistics."""

# pylint: disable=no-member

import psycopg

from src.sql_helpers import (
    SQL_COUNT_JHU_CS_MASTERS,
    SQL_COUNT_GEORGETOWN_CS_PHD_2025,
    SQL_COUNT_GRE_SUBMITTED,
)


def get_connection():
    """Return a connection to the applicants database."""
    return psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )


# Individual report functions

def report_fall2025_applicants(cur):
    """Print the number of Fall 2025 applicants."""
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term ILIKE %s
    """, ("%Fall 2025%",))
    count = cur.fetchone()[0]
    print("Number of Fall 2025 applicants:", count)


def report_international_percentage(cur):
    """Print the percentage of international applicants."""
    cur.execute("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN us_or_international ILIKE '%International%' THEN 1 ELSE 0 END) / COUNT(*),
            2
        )
        FROM applicants;
    """)
    pct = cur.fetchone()[0]
    if pct:
        print(f"Percentage of international applicants: {pct:.2f}%")
    else:
        print("No applicants in the database.")


def report_average_scores(cur):
    """Print average GPA and GRE scores."""
    cur.execute("""
        SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
        FROM applicants
    """)
    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

    print("Averages:")
    print(f"  GPA   : {avg_gpa:.2f}" if avg_gpa else "  GPA   : No data")
    print(f"  GRE   : {avg_gre:.2f}" if avg_gre else "  GRE   : No data")
    print(f"  GRE V : {avg_gre_v:.2f}" if avg_gre_v else "  GRE V : No data")
    print(f"  GRE AW: {avg_gre_aw:.2f}" if avg_gre_aw else "  GRE AW: No data")


def report_avg_gpa_american_fall2025(cur):
    """Print average GPA of American applicants in Fall 2025."""
    cur.execute("""
        SELECT AVG(gpa)
        FROM applicants
        WHERE term = 'Fall 2025'
          AND us_or_international = 'American'
          AND gpa IS NOT NULL;
    """)
    avg_gpa = cur.fetchone()[0]
    if avg_gpa:
        print(f"Average GPA of American applicants in Fall 2025: {avg_gpa:.2f}")
    else:
        print("No GPA data available for American applicants in Fall 2025.")


def report_acceptance_percentage_fall2025(cur):
    """Print acceptance percentage for Fall 2025 applicants."""
    cur.execute("""
        SELECT 100.0 * COUNT(*) FILTER (WHERE status ILIKE 'Accepted%') / COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2025'
    """)
    pct = cur.fetchone()[0]
    if pct is not None:
        print(f"Percentage of Fall 2025 entries that are Acceptances: {pct:.2f}%")
    else:
        print("No entries found for Fall 2025.")


def report_avg_gpa_accepted_fall2025(cur):
    """Print average GPA of accepted Fall 2025 applicants."""
    cur.execute("""
        SELECT AVG(gpa)
        FROM applicants
        WHERE term = 'Fall 2025'
          AND status ILIKE '%Accepted%'
          AND gpa IS NOT NULL;
    """)
    avg = cur.fetchone()[0]
    if avg:
        print(f"Average GPA of accepted applicants for Fall 2025: {avg:.2f}")
    else:
        print("No data available for accepted Fall 2025 applicants.")


def report_jhu_cs_masters(cur):
    """Print number of applicants to JHU for a Master's in CS."""
    cur.execute(SQL_COUNT_JHU_CS_MASTERS)

    count = cur.fetchone()[0]
    print(f"Number of applicants to JHU for a Master's in Computer Science: {count}")


def report_georgetown_cs_phd_acceptances(cur):
    """Print number of 2025 Georgetown PhD CS acceptances."""
    cur.execute(SQL_COUNT_GEORGETOWN_CS_PHD_2025)

    count = cur.fetchone()[0]
    print(f"Number of 2025 Georgetown PhD Computer Science acceptances: {count}")


def report_datascience_fall2025(cur):
    """Print number of Fall 2025 Data Science applicants."""
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term ILIKE '%Fall 2025%'
          AND llm_generated_program ILIKE '%Data Science%';
    """)
    count = cur.fetchone()[0]
    print(f"Number of Fall 2025 Data Science applicants: {count}")


def report_gre_submitters(cur):
    """Print number of applicants who submitted any GRE score."""
    cur.execute(SQL_COUNT_GRE_SUBMITTED)

    count = cur.fetchone()[0]
    print(f"Number of applicants who submitted a GRE score: {count}")


# Main runner

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
