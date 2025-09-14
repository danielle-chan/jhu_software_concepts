import psycopg

# Connect to database applicants
conn = psycopg.connect(
    dbname="applicants",  
    user="daniellechan",   
)

# Open a cursor to perform database operations
cur = conn.cursor()

# How many entries do you have in your database who have applied for Fall 2025?
# Select all students who applied in Fall 2025
cur.execute("""
    SELECT COUNT(*) 
    FROM applicants
    WHERE term ILIKE %s
""", ("%Fall 2025%",))

count = cur.fetchone()[0]
print("Number of Fall 2025 applicants:", count)


# What percentage of entries are from international students (not American or Other) (to two decimal places)?
# Count international applicants (not 'American' or 'Other')
cur.execute("""
     SELECT ROUND(100.0 * SUM(CASE WHEN us_or_international ILIKE '%International%' THEN 1 ELSE 0 END) / COUNT(*), 2)
    FROM applicants;
""")
percent_international = cur.fetchone()[0]
print(f"Percentage of international applicants: {percent_international:.2f}%" if percent_international else "No applicants in the database.")


# What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?
cur.execute("""
    SELECT 
        AVG(gpa) AS avg_gpa,
        AVG(gre) AS avg_gre,
        AVG(gre_v) AS avg_gre_v,
        AVG(gre_aw) AS avg_gre_aw
    FROM applicants
""")

avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

print("Averages:")
print(f"  GPA   : {avg_gpa:.2f}" if avg_gpa else "  GPA   : No data")
print(f"  GRE   : {avg_gre:.2f}" if avg_gre else "  GRE   : No data")
print(f"  GRE V : {avg_gre_v:.2f}" if avg_gre_v else "  GRE V : No data")
print(f"  GRE AW: {avg_gre_aw:.2f}" if avg_gre_aw else "  GRE AW: No data")


# What is the average GPA of American students in Fall 2025?
# Calculate the average GPA of all American applicants from Fall 2025 
cur.execute("""
    SELECT AVG(gpa) AS avg_gpa
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


# What percent of entries for Fall 2025 are Acceptances (to two decimal places)?
# Calculate the percent of acceptances from Fall 2025
cur.execute("""
    SELECT
        100.0 * COUNT(*) FILTER (WHERE status ILIKE 'Accepted%') / COUNT(*)
    FROM applicants
    WHERE term = 'Fall 2025'
""")

percent_acceptances = cur.fetchone()[0]

if percent_acceptances is not None:
    print(f"Percentage of Fall 2025 entries that are Acceptances: {percent_acceptances:.2f}%")
else:
    print("No entries found for Fall 2025.")


# What is the average GPA of applicants who applied for Fall 2025 who are Acceptances?
cur.execute("""
    SELECT AVG(gpa) AS avg_gpa_fall2025_acceptances
    FROM applicants
    WHERE term = 'Fall 2025'
      AND status ILIKE '%Accepted%'
      AND gpa IS NOT NULL;
""")

avg_gpa_accepted = cur.fetchone()
print(f"Average GPA of accepted applicants for Fall 2025: {avg_gpa_accepted[0]:.2f}" if avg_gpa_accepted[0] else "No data available")


# How many entries are from applicants who applied to JHU for a masters degree in Computer Science?
# Select applicants who applied to JHU for a masters degree in CS
cur.execute("""
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
""")

jhu_apps = cur.fetchone()
print(f"Number of applicants to JHU for a Master's in Computer Science: {jhu_apps[0]}")


# How many entries from 2025 are acceptances from applicants who applied to Georgetown University for a PhD in Computer Science?
# Select applicants who applied in 2025 for Georgetown's PhD in CS
cur.execute("""
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
""")

gtown_apps = cur.fetchone()
print(f"Number of 2025 Georgetown PhD Computer Science acceptances: {gtown_apps[0]}")


# How many students applied for Fall 2025 to a Data Science program?
# Select applicants who applied in 2025 for Data Science
cur.execute("""
    SELECT COUNT(*)
    FROM applicants
    WHERE 
        term ILIKE '%Fall 2025%'
        AND (
            llm_generated_program ILIKE '%Data Science%'
        );
""")

ds_apps = cur.fetchone()
print(f"Number of Fall 2025 Data Science applicants: {ds_apps[0]}")


# How many students submitted a GRE score?
# Select all students who submitted any type of GRE score
cur.execute("""
    SELECT COUNT(*)
    FROM applicants
    WHERE gre IS NOT NULL
       OR gre_v IS NOT NULL
       OR gre_aw IS NOT NULL;
""")

count_gre = cur.fetchone()
print(f"Number of applicants who submitted a GRE score: {count_gre[0]}")

cur.close()
conn.close()