import psycopg

conn = psycopg.connect(
    dbname="applicants",
    user="daniellechan",
)

cur = conn.cursor()

# Add a unique constraint on url
cur.execute("ALTER TABLE applicants ADD CONSTRAINT unique_url UNIQUE (url);")

conn.commit()
cur.close()
conn.close()
