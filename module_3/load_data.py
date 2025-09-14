import psycopg
import json

# Connect to database applicants
conn = psycopg.connect(
    dbname="applicants",  
    user="daniellechan",   
)

# Open a cursor to perform database operations
cur = conn.cursor()

with open("full_out.jsonl", "r") as f:
    for line in f:
        entry = json.loads(line)

        # Replace "N/A" with None for nullable fields
        def clean_val(v):
            return None if v in ("N/A", "", None) else v

        cur.execute("""
    INSERT INTO applicants (
        program, degree, comments, date_added, status, url,
        gpa, gre, gre_v, gre_aw, term, us_or_international,
        llm_generated_program, llm_generated_university, university
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
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
    clean_val(entry.get("university"))
))

# Commit and close
conn.commit()
cur.close()
conn.close()