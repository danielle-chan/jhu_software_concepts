"""Common SQL query strings and composed statements shared by run.py and query_data.py."""

from psycopg import sql

# -----------------------------------------------------
# Static SQL constants
# -----------------------------------------------------

SQL_COUNT_JHU_CS_MASTERS = """
    SELECT COUNT(*)
    FROM applicants
    WHERE (
        llm_generated_university ILIKE '%Johns Hopkins%'
        OR llm_generated_university ILIKE '%JHU%'
        OR llm_generated_university ILIKE '%Hopkins%'
    )
      AND llm_generated_program ILIKE '%Computer Science%'
      AND (
          degree ILIKE '%Master%'
          OR degree ILIKE '%MS%'
          OR degree ILIKE '%M.S.%'
          OR degree ILIKE '%Masters%'
      )
"""

SQL_COUNT_GEORGETOWN_CS_PHD_2025 = """
    SELECT COUNT(*)
    FROM applicants
    WHERE term ILIKE '%2025%'
      AND status ILIKE '%Accept%'
      AND llm_generated_university ILIKE '%Georgetown%'
      AND (
          degree ILIKE '%PhD%'
          OR degree ILIKE '%Ph.D.%'
          OR degree ILIKE '%Doctorate%'
      )
      AND llm_generated_program ILIKE '%Computer Science%'
"""

SQL_COUNT_GRE_SUBMITTED = """
    SELECT COUNT(*)
    FROM applicants
    WHERE gre IS NOT NULL
       OR gre_v IS NOT NULL
       OR gre_aw IS NOT NULL
"""

# -----------------------------------------------------
# Helper functions for commonly repeated queries
# -----------------------------------------------------

def build_avg_gpa_stmt(term, status=None, us_flag=None):
    """
    Build a composed SQL statement for average GPA.

    :param term: e.g. "Fall 2025"
    :param status: e.g. "%Accepted%" or None
    :param us_flag: e.g. "American" or None
    """
    where_clauses = [sql.SQL("term = {}").format(sql.Literal(term)),
                     sql.SQL("gpa IS NOT NULL")]

    if status is not None:
        where_clauses.insert(1, sql.SQL("status ILIKE {}").format(sql.Literal(status)))

    if us_flag is not None:
        where_clauses.insert(1, sql.SQL("us_or_international = {}").format(sql.Literal(us_flag)))

    return sql.SQL("SELECT AVG(gpa) FROM {tbl} WHERE " +
                   sql.SQL(" AND ").join(where_clauses).as_string(None) +
                   " LIMIT 1").format(tbl=sql.Identifier("applicants"))


def build_ds_count_stmt(term, program_pattern):
    """Build a composed SQL statement to count Data Science applicants."""
    return sql.SQL("""
        SELECT COUNT(*)
        FROM {tbl}
        WHERE term ILIKE {term}
          AND llm_generated_program ILIKE {prog}
        LIMIT 1
    """).format(
        tbl=sql.Identifier("applicants"),
        term=sql.Literal(term),
        prog=sql.Literal(program_pattern)
    )
