"""Tests for inserting applicants into the database."""

# pylint: disable=redefined-outer-name

import psycopg
import pytest


@pytest.fixture
def db_conn_fixture():
    """Provide a temporary DB connection for tests, rolling back after use."""
    conn = psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )
    yield conn
    conn.rollback()  # pylint: disable=no-member
    conn.close()     # pylint: disable=no-member


@pytest.mark.db
def test_insert_and_select(db_conn_fixture):
    """Verify that inserting a new applicant works and can be queried."""
    cur = db_conn_fixture.cursor()

    test_url = "http://test-unique-url.com"

    cur.execute(
        """
        INSERT INTO applicants (
            program, degree, comments, date_added, status, url,
            gpa, gre, gre_v, gre_aw, term, us_or_international,
            llm_generated_program, llm_generated_university, university
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        ON CONFLICT (url) DO NOTHING
        """,
        (
            "Computer Science",
            "Masters",
            "Test comment",
            "2025-01-01",
            "Accepted",
            test_url,
            3.8, 320, 160, 4.5,
            "Fall 2025",
            "American",
            "Computer Science",
            "Test University",
            "Test University",
        ),
    )

    cur.execute("SELECT * FROM applicants WHERE url = %s", (test_url,))
    row = cur.fetchone()
    assert row is not None, "Row was not inserted into applicants table"


@pytest.mark.db
def test_duplicate_insert_is_ignored(db_conn_fixture):
    """Verify that duplicate inserts using the same URL are ignored."""
    cur = db_conn_fixture.cursor()

    url = "http://test-duplicate-url.com"

    cur.execute(
        """
        INSERT INTO applicants (program, degree, comments, date_added, status, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
        """,
        (
            "Data Science",
            "PhD",
            "Initial comment",
            "2025-01-02",
            "Rejected",
            url,
        ),
    )

    cur.execute(
        """
        INSERT INTO applicants (program, degree, comments, date_added, status, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
        """,
        (
            "Data Science",
            "PhD",
            "Duplicate comment should be ignored",
            "2025-01-02",
            "Rejected",
            url,
        ),
    )

    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = %s", (url,))
    count = cur.fetchone()[0]
    assert count == 1, f"Expected 1 row for {url}, but found {count}"
