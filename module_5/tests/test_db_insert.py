import psycopg
import pytest

@pytest.fixture
def db_connection():
    conn = psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )
    yield conn
    conn.rollback()  # rollback test changes so DB stays clean
    conn.close()

@pytest.mark.db
def test_insert_and_select(db_connection):
    cur = db_connection.cursor()

    # Insert a fake applicant row
    cur.execute("""
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
    """, (
        "Computer Science",
        "Masters",
        "Test comment",
        "2025-01-01",
        "Accepted",
        "http://test-unique-url.com",
        3.8, 320, 160, 4.5,
        "Fall 2025",
        "American",
        "Computer Science",
        "Test University",
        "Test University"
    ))

    # Check that it got inserted
    cur.execute("SELECT * FROM applicants WHERE url = %s", ("http://test-unique-url.com",))
    row = cur.fetchone()
    assert row is not None, "Row was not inserted into applicants table"

@pytest.mark.db
def test_duplicate_insert_is_ignored(db_connection):
    cur = db_connection.cursor()
    url = "http://test-duplicate-url.com"

    # Insert once
    cur.execute("""
        INSERT INTO applicants (program, degree, comments, date_added, status, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
    """, (
        "Data Science",
        "PhD",
        "Initial comment",
        "2025-01-02",
        "Rejected",
        url
    ))

    # Insert duplicate with different comment
    cur.execute("""
        INSERT INTO applicants (program, degree, comments, date_added, status, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
    """, (
        "Data Science",
        "PhD",
        "Duplicate comment should be ignored",
        "2025-01-02",
        "Rejected",
        url
    ))

    # Should still only have 1 row
    cur.execute("SELECT COUNT(*) FROM applicants WHERE url = %s", (url,))
    count = cur.fetchone()[0]
    assert count == 1, f"Expected 1 row for {url}, but found {count}"