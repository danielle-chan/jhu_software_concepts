"""Flask web app (read-only): shows GradCafe ETL statistics."""

import os

from flask import Flask, render_template, jsonify, current_app
import psycopg
from psycopg import sql
from publisher import publish_task 

app = Flask(__name__)
app.secret_key = "secret_key"

DB_NAME = os.getenv("POSTGRES_DB", "applicants")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))


def get_conn():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
    )

@app.route("/")
def index():
    """Render dashboard metrics."""
    # Using context managers ensures clean close; also plays nicely with linters.
    with get_conn() as conn, conn.cursor() as cur:

        # 1) How many applied for Fall 2025
        stmt_fall2025 = sql.SQL("""
            SELECT COUNT(*)
            FROM {tbl}
            WHERE term ILIKE {pattern}
            LIMIT 1
        """).format(tbl=sql.Identifier("applicants"),
                    pattern=sql.Literal("%Fall 2025%"))
        cur.execute(stmt_fall2025)
        count = cur.fetchone()[0]

        # 2) Percent of international students
        stmt_pct_intl = sql.SQL("""
            SELECT ROUND(
                100.0 * SUM(CASE WHEN us_or_international ILIKE {intl} THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
                2
            )
            FROM {tbl}
            LIMIT 1
        """).format(tbl=sql.Identifier("applicants"),
                    intl=sql.Literal("%International%"))
        cur.execute(stmt_pct_intl)
        percent_international = cur.fetchone()[0]

        # 3) Average GPA and GRE scores
        stmt_avgs = sql.SQL("""
            SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw)
            FROM {tbl}
            LIMIT 1
        """).format(tbl=sql.Identifier("applicants"))
        cur.execute(stmt_avgs)
        avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

        # 4) Average GPA of American students (Fall 2025)
        stmt_avg_gpa_american = sql.SQL("""
            SELECT AVG(gpa)
            FROM {tbl}
            WHERE term = {term}
              AND us_or_international = {flag}
              AND gpa IS NOT NULL
            LIMIT 1
        """).format(tbl=sql.Identifier("applicants"),
                    term=sql.Literal("Fall 2025"),
                    flag=sql.Literal("American"))
        cur.execute(stmt_avg_gpa_american)
        avg_gpa_american = cur.fetchone()[0]

        # 5) Percent acceptances for Fall 2025
        stmt_pct_accept = sql.SQL("""
            SELECT 100.0 * COUNT(*) FILTER (WHERE status ILIKE {acc}) / NULLIF(COUNT(*), 0)
            FROM {tbl}
            WHERE term = {term}
            LIMIT 1
        """).format(tbl=sql.Identifier("applicants"),
                    acc=sql.Literal("Accepted%"),
                    term=sql.Literal("Fall 2025"))
        cur.execute(stmt_pct_accept)
        percent_acceptances = cur.fetchone()[0]

        # 6) Average GPA of acceptances (Fall 2025)
        stmt_avg_gpa_accepted = sql.SQL("""
            SELECT AVG(gpa)
            FROM {tbl}
            WHERE term = {term}
              AND status ILIKE {acc}
              AND gpa IS NOT NULL
            LIMIT 1
        """).format(tbl=sql.Identifier("applicants"),
                    term=sql.Literal("Fall 2025"),
                    acc=sql.Literal("%Accepted%"))
        cur.execute(stmt_avg_gpa_accepted)
        avg_gpa_accepted = cur.fetchone()[0]

        # 7) Applicants to JHU for a Master’s in CS
        stmt_jhu_ms_cs = sql.SQL("""
            SELECT COUNT(*)
            FROM {tbl}
            WHERE (
                llm_generated_university ILIKE {u1}
                OR llm_generated_university ILIKE {u2}
                OR llm_generated_university ILIKE {u3}
            )
            AND llm_generated_program ILIKE {prog_cs}
            AND (
                degree ILIKE {m1}
                OR degree ILIKE {m2}
                OR degree ILIKE {m3}
                OR degree ILIKE {m4}
            )
            LIMIT 1
        """).format(
            tbl=sql.Identifier("applicants"),
            u1=sql.Literal("%Johns Hopkins%"),
            u2=sql.Literal("%JHU%"),
            u3=sql.Literal("%Hopkins%"),
            prog_cs=sql.Literal("%Computer Science%"),
            m1=sql.Literal("%Master%"),
            m2=sql.Literal("%MS%"),
            m3=sql.Literal("%M.S.%"),
            m4=sql.Literal("%Masters%"),
        )
        cur.execute(stmt_jhu_ms_cs)
        jhu_apps = cur.fetchone()[0]

        # 8) 2025 Georgetown PhD CS acceptances
        stmt_gtown_phd_cs_2025 = sql.SQL("""
            SELECT COUNT(*)
            FROM {tbl}
            WHERE term ILIKE {y2025}
              AND status ILIKE {accept}
              AND llm_generated_university ILIKE {gtown}
              AND (
                  degree ILIKE {phd1}
                  OR degree ILIKE {phd2}
                  OR degree ILIKE {phd3}
              )
              AND llm_generated_program ILIKE {prog_cs}
            LIMIT 1
        """).format(
            tbl=sql.Identifier("applicants"),
            y2025=sql.Literal("%2025%"),
            accept=sql.Literal("%Accept%"),
            gtown=sql.Literal("%Georgetown%"),
            phd1=sql.Literal("%PhD%"),
            phd2=sql.Literal("%Ph.D.%"),
            phd3=sql.Literal("%Doctorate%"),
            prog_cs=sql.Literal("%Computer Science%"),
        )
        cur.execute(stmt_gtown_phd_cs_2025)
        gtown_apps = cur.fetchone()[0]

        # 9) Fall 2025 Data Science applicants
        stmt_ds = sql.SQL("""
            SELECT COUNT(*)
            FROM {tbl}
            WHERE term ILIKE {term}
              AND llm_generated_program ILIKE {prog}
            LIMIT 1
        """).format(
            tbl=sql.Identifier("applicants"),
            term=sql.Literal("%Fall 2025%"),
            prog=sql.Literal("%Data Science%")
        )
        cur.execute(stmt_ds)
        ds_apps = cur.fetchone()[0]

        # 10) Number of applicants who submitted any GRE score
        stmt_gre_submitters = sql.SQL("""
            SELECT COUNT(*)
            FROM {tbl}
            WHERE gre IS NOT NULL
               OR gre_v IS NOT NULL
               OR gre_aw IS NOT NULL
            LIMIT 1
        """).format(tbl=sql.Identifier("applicants"))
        cur.execute(stmt_gre_submitters)
        count_gre = cur.fetchone()[0]

    # Render your existing template (place it at module_6/web/templates/index.html)
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

@app.post("/api/scrape")
def api_scrape():
    try:
        publish_task("scrape_new_data", payload={})
        return jsonify({"status": "queued", "task": "scrape_new_data"}), 202
    except Exception:
        current_app.logger.exception("Failed to publish scrape_new_data")
        return jsonify({"error": "publish_failed"}), 503


@app.post("/api/recompute")
def api_recompute():
    try:
        publish_task("recompute_analytics", payload={})
        return jsonify({"status": "queued", "task": "recompute_analytics"}), 202
    except Exception:
        current_app.logger.exception("Failed to publish recompute_analytics")
        return jsonify({"error": "publish_failed"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
