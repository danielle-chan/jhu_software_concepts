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
