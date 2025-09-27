"""Main Flask application for the GradCafe ETL dashboard."""

import subprocess

import psycopg
from flask import Flask, render_template, redirect, url_for, flash

from src.append_data import append_data

# pylint: disable=no-member  # psycopg cursor/connection false positives

IS_RUNNING = False  # global flag to block simultaneous updates

# Create the Flask application using the factory function defined within __init__.py
app = Flask(__name__)
app.secret_key = "secret_key" # Need a secret key to use flash

def get_db_connection():
    """Create and return a connection to the applicants database."""
    return psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )

@app.route('/')
def index():
    """Render the dashboard with all current statistics."""
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. How many applied for Fall 2025
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term ILIKE '%Fall 2025%';
    """)
    count = cur.fetchone()[0]


    # 2. Percent of international students
    cur.execute("""
        SELECT ROUND(100.0 * SUM(CASE WHEN us_or_international ILIKE '%International%' THEN 1 ELSE 0 END) / COUNT(*), 2)
        FROM applicants;
    """)
    percent_international = cur.fetchone()[0]


    # 3. Average GPA and GRE scores
    cur.execute("""
        SELECT AVG(gpa) AS avg_gpa, AVG(gre) AS avg_gre, AVG(gre_v) AS avg_gre_v, AVG(gre_aw) AS avg_gre_aw
        FROM applicants
    """)

    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()


    # 4. Average GPA of American students
    cur.execute("""
        SELECT AVG(gpa) AS avg_gpa
        FROM applicants
        WHERE term = 'Fall 2025'
        AND us_or_international = 'American'
        AND gpa IS NOT NULL;
    """)

    avg_gpa_american = cur.fetchone()[0]


    # 5. Percent acceptences for Fall 2025
    cur.execute("""
        SELECT
            100.0 * COUNT(*) FILTER (WHERE status ILIKE 'Accepted%') / COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2025'
    """)

    percent_acceptances = cur.fetchone()[0]


    # 6. Average GPA of acceptances from Fall 2025
    cur.execute("""
        SELECT AVG(gpa) AS avg_gpa_fall2025_acceptances
        FROM applicants
        WHERE term = 'Fall 2025'
        AND status ILIKE '%Accepted%'
        AND gpa IS NOT NULL;
    """)

    avg_gpa_accepted = cur.fetchone()[0]


    # 7. Applicants who applied to JHU for master's in CS
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

    jhu_apps = cur.fetchone()[0]


    # 8. 2025 applicants who applied to Georgwtown for PhD in CS
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

    gtown_apps = cur.fetchone()[0]

    # 9. Fall 2025 data science applicants
    cur.execute("""
    SELECT COUNT(*)
        FROM applicants
        WHERE 
            term ILIKE '%Fall 2025%'
            AND (
                llm_generated_program ILIKE '%Data Science%'
            );
    """)

    ds_apps = cur.fetchone()[0]

    # 10. Number of applicants who submitted a GRE score
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE gre IS NOT NULL
            OR gre_v IS NOT NULL
            OR gre_aw IS NOT NULL;
    """)

    count_gre = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        'index.html',
        count=count,
        percent_international=percent_international,
        avg_gpa=avg_gpa,
        avg_gre=avg_gre,
        avg_gre_v=avg_gre_v,
        avg_gre_aw=avg_gre_aw,
        avg_gpa_american=avg_gpa_american,
        percent_acceptances=percent_acceptances,
        avg_gpa_accepted=avg_gpa_accepted,
        jhu_apps=jhu_apps,
        gtown_apps=gtown_apps,
        ds_apps=ds_apps,
        count_gre=count_gre
    )


@app.route('/pull_data')
def pull_data():
    """Scrape, clean, standardize , append new data"""
    # 1. Scrape raw data
    subprocess.run(["python3", "scrape.py"], check=True)

    # 2. Clean data
    subprocess.run(["python3", "clean.py"], check=True)

    # 3. Standardize data (LLM CLI)
    subprocess.run([
        "python3", "llm_hosting/app.py",
        "--file", "cleaned_applicant_data.json",
        "--out", "llm_hosting/full_out.jsonl"
    ], check=True)

    # 4. Append to database
    append_data("llm_hosting/full_out.jsonl")

    # Redirect back to dashboard after completion
    return redirect(url_for("index"))


@app.route("/update_analysis")
def update_analysis():
    """Trigger a refresh of analysis unless a pull is running."""
    if IS_RUNNING:
        flash("Please wait. Cannot update analysis while a data pull is running.")
        return redirect(url_for("index"))

    flash("Analysis updated with the latest data.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Start the Flask development server
    app.run(host="0.0.0.0", port=8000, debug=True)
