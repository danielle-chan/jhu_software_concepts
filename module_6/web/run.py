"""Main Flask application for the GradCafe ETL dashboard."""

import subprocess
import psycopg
from psycopg import sql
from flask import Flask, render_template, redirect, url_for, flash

from src.append_data import append_data
from worker.etl.sql_helpers import (
    SQL_COUNT_JHU_CS_MASTERS,
    SQL_COUNT_GEORGETOWN_CS_PHD_2025,
    SQL_COUNT_GRE_SUBMITTED,
    build_avg_gpa_stmt,
    build_ds_count_stmt,
)

# pylint: disable=no-member
# pylint: disable=too-many-locals   # Acceptable becayse index() route needs many values for the template

IS_RUNNING = False  # global flag to block simultaneous updates

app = Flask(__name__)
app.secret_key = "secret_key"  # Needed for flash messages


def get_db_connection():
    """Create and return a connection to the applicants database."""
    return psycopg.connect(
        dbname="applicants",
        user="daniellechan",
    )


@app.route("/")
def index():
    """Render the dashboard with all current statistics."""
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. How many applied for Fall 2025
    stmt_fall2025 = sql.SQL("""
        SELECT COUNT(*)
        FROM {tbl}
        WHERE term ILIKE {pattern}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"), pattern=sql.Literal("%Fall 2025%"))
    cur.execute(stmt_fall2025)
    count = cur.fetchone()[0]

    # 2. Percent of international students
    stmt_international = sql.SQL("""
        SELECT ROUND(
            100.0 * SUM(CASE WHEN us_or_international ILIKE {intl} THEN 1 ELSE 0 END) / COUNT(*), 2
        )
        FROM {tbl}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"), intl=sql.Literal("%International%"))
    cur.execute(stmt_international)
    percent_international = cur.fetchone()[0]

    # 3. Average GPA and GRE scores
    stmt_avg_scores = sql.SQL("""
        SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
        FROM {tbl}
        LIMIT 1
    """).format(tbl=sql.Identifier("applicants"))
    cur.execute(stmt_avg_scores)
    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

    # 4. Average GPA of American students (centralized)
    stmt_avg_gpa_american = build_avg_gpa_stmt(term="Fall 2025", us_flag="American")
    cur.execute(stmt_avg_gpa_american)
    avg_gpa_american = cur.fetchone()[0]

    # 5. Percent acceptances for Fall 2025
    stmt_acceptances = sql.SQL("""
        SELECT 100.0 * COUNT(*) FILTER (WHERE status ILIKE {acc}) / COUNT(*)
        FROM {tbl}
        WHERE term = {term}
        LIMIT 1
    """).format(
        tbl=sql.Identifier("applicants"),
        acc=sql.Literal("Accepted%"),
        term=sql.Literal("Fall 2025"),
    )
    cur.execute(stmt_acceptances)
    percent_acceptances = cur.fetchone()[0]

    # 6. Average GPA of acceptances from Fall 2025
    stmt_avg_gpa_accepted = build_avg_gpa_stmt(term="Fall 2025", status="%Accepted%")
    cur.execute(stmt_avg_gpa_accepted)
    avg_gpa_accepted = cur.fetchone()[0]

    # 7. Applicants who applied to JHU for master's in CS
    cur.execute(sql.SQL(SQL_COUNT_JHU_CS_MASTERS + " LIMIT 1"))
    jhu_apps = cur.fetchone()[0]

    # 8. 2025 applicants who applied to Georgetown for PhD in CS
    cur.execute(sql.SQL(SQL_COUNT_GEORGETOWN_CS_PHD_2025 + " LIMIT 1"))
    gtown_apps = cur.fetchone()[0]

    # 9. Fall 2025 Data Science applicants
    stmt_ds = build_ds_count_stmt(term="%Fall 2025%", program_pattern="%Data Science%")
    cur.execute(stmt_ds)
    ds_apps = cur.fetchone()[0]

    # 10. Number of applicants who submitted a GRE score
    cur.execute(sql.SQL(SQL_COUNT_GRE_SUBMITTED + " LIMIT 1"))
    count_gre = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        "index.html",
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
        count_gre=count_gre,
    )


@app.route("/pull_data")
def pull_data():
    """Scrape, clean, standardize, and append new data."""
    subprocess.run(["python3", "scrape.py"], check=True)
    subprocess.run(["python3", "clean.py"], check=True)
    subprocess.run([
        "python3", "llm_hosting/app.py",
        "--file", "cleaned_applicant_data.json",
        "--out", "llm_hosting/full_out.jsonl",
    ], check=True)

    append_data("llm_hosting/full_out.jsonl")
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
    app.run(host="0.0.0.0", port=8000, debug=True)
