# src/constraint.py
import psycopg

def ensure_unique_constraint():
    conn = psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )
    cur = conn.cursor()

    cur.execute("ALTER TABLE applicants DROP CONSTRAINT IF EXISTS unique_url;")
    cur.execute("ALTER TABLE applicants ADD CONSTRAINT unique_url UNIQUE (url);")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    ensure_unique_constraint()

