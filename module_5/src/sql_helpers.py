"""Common SQL query strings used by run.py and query_data.py."""

# SQL to count JHU CS master’s applicants
SQL_COUNT_JHU_CS_MASTERS = """
    SELECT COUNT(*)
    FROM applicants
    WHERE (
        llm_generated_university ILIKE '%Johns Hopkins%'
        OR llm_generated_university ILIKE '%JHU%'
        OR llm_generated_university ILIKE '%Hopkins%'
    )
    AND (
        llm_generated_program ILIKE '%Computer Science%'
    )
    AND (
        degree ILIKE '%Master%'
        OR degree ILIKE '%MS%'
        OR degree ILIKE '%M.S.%'
        OR degree ILIKE '%Masters%'
    );
"""

# SQL to count Georgetown CS PhD 2025 applicants
SQL_COUNT_GEORGETOWN_CS_PHD_2025 = """
    SELECT COUNT(*)
    FROM applicants
    WHERE
        term ILIKE '%2025%'
        AND status ILIKE '%Accept%'
        AND (
            llm_generated_university ILIKE '%Georgetown%'
        )
        AND (
            degree ILIKE '%PhD%'
            OR degree ILIKE '%Ph.D.%'
            OR degree ILIKE '%Doctorate%'
        )
        AND (
            llm_generated_program ILIKE '%Computer Science%'
        );
"""

# SQL to count all applicants who submitted GRE scores
SQL_COUNT_GRE_SUBMITTED = """
    SELECT COUNT(*)
    FROM applicants
    WHERE gre IS NOT NULL
        OR gre_v IS NOT NULL
        OR gre_aw IS NOT NULL;
"""
