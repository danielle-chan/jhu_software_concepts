"""Load cleaned and standardized GradCafe applicant data into the PostgreSQL database."""

import json
import psycopg
from psycopg import sql

# pylint: disable=no-member

def load_data_from_jsonl(file_path="src/llm_hosting/full_out.jsonl"):
    """Truncate the applicants table and load all rows from the given JSONL file."""

    conn = psycopg.connect( # pylint: disable=no-member
        dbname="applicants",
        user="daniellechan",
    )
    cur = conn.cursor() # pylint: disable=no-member

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
        LIMIT 100000
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
            )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    load_data_from_jsonl()
