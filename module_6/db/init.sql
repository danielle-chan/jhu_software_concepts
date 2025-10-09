-- Minimal schema + unique constraint on URL
CREATE TABLE IF NOT EXISTS applicants (
  id SERIAL PRIMARY KEY,
  program TEXT,
  degree TEXT,
  comments TEXT,
  date_added TEXT,
  status TEXT,
  url TEXT UNIQUE,
  gpa DOUBLE PRECISION,
  gre DOUBLE PRECISION,
  gre_v DOUBLE PRECISION,
  gre_aw DOUBLE PRECISION,
  term TEXT,
  us_or_international TEXT,
  llm_generated_program TEXT,
  llm_generated_university TEXT,
  university TEXT
);

-- Single-row materialized view with a synthetic primary key (id=1)
-- so we can index it and (optionally) use CONCURRENTLY later.
CREATE MATERIALIZED VIEW IF NOT EXISTS applicant_summary AS
SELECT
  1 AS id,
  -- 1) How many applied for Fall 2025
  (SELECT COUNT(*) FROM applicants WHERE term ILIKE '%Fall 2025%') AS fall2025_count,

  -- 2) Percent of international students
  (SELECT ROUND(
      100.0 * SUM(CASE WHEN us_or_international ILIKE '%International%' THEN 1 ELSE 0 END)
      / NULLIF(COUNT(*), 0), 2
   ) FROM applicants) AS pct_international,

  -- 3) Averages
  (SELECT AVG(gpa)   FROM applicants) AS avg_gpa,
  (SELECT AVG(gre)   FROM applicants) AS avg_gre,
  (SELECT AVG(gre_v) FROM applicants) AS avg_gre_v,
  (SELECT AVG(gre_aw)FROM applicants) AS avg_gre_aw,

  -- 4) Avg GPA of American students in Fall 2025
  (SELECT AVG(gpa) FROM applicants
     WHERE term = 'Fall 2025' AND us_or_international = 'American' AND gpa IS NOT NULL
  ) AS avg_gpa_american_fall2025,

  -- 5) Percent acceptances for Fall 2025
  (SELECT 100.0 * COUNT(*) FILTER (WHERE status ILIKE 'Accepted%') / NULLIF(COUNT(*), 0)
     FROM applicants WHERE term = 'Fall 2025'
  ) AS pct_accept_fall2025,

  -- 6) Avg GPA of accepted Fall 2025
  (SELECT AVG(gpa) FROM applicants
     WHERE term = 'Fall 2025' AND status ILIKE '%Accepted%' AND gpa IS NOT NULL
  ) AS avg_gpa_accepted_fall2025,

  -- 7) JHU MS CS applicants
  (SELECT COUNT(*) FROM applicants
     WHERE (
       llm_generated_university ILIKE '%Johns Hopkins%' OR
       llm_generated_university ILIKE '%JHU%' OR
       llm_generated_university ILIKE '%Hopkins%'
     )
     AND llm_generated_program ILIKE '%Computer Science%'
     AND (
       degree ILIKE '%Master%' OR degree ILIKE '%MS%' OR
       degree ILIKE '%M.S.%'  OR degree ILIKE '%Masters%'
     )
  ) AS jhu_ms_cs_count,

  -- 8) 2025 Georgetown CS PhD acceptances
  (SELECT COUNT(*) FROM applicants
     WHERE term ILIKE '%2025%'
       AND status ILIKE '%Accept%'
       AND llm_generated_university ILIKE '%Georgetown%'
       AND (
         degree ILIKE '%PhD%' OR degree ILIKE '%Ph.D.%' OR degree ILIKE '%Doctorate%'
       )
       AND llm_generated_program ILIKE '%Computer Science%'
  ) AS gtown_cs_phd_2025_accepts,

  -- 9) Fall 2025 Data Science applicants
  (SELECT COUNT(*) FROM applicants
     WHERE term ILIKE '%Fall 2025%'
       AND llm_generated_program ILIKE '%Data Science%'
  ) AS ds_fall2025_count,

  -- 10) Number of applicants who submitted any GRE component
  (SELECT COUNT(*) FROM applicants
     WHERE gre IS NOT NULL OR gre_v IS NOT NULL OR gre_aw IS NOT NULL
  ) AS gre_submitters_count
;

-- Unique index so we can optionally REFRESH CONCURRENTLY:
CREATE UNIQUE INDEX IF NOT EXISTS applicant_summary_pk ON applicant_summary(id);
