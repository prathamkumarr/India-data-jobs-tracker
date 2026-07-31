CREATE TABLE IF NOT EXISTS raw_jobs (
    job_id          TEXT PRIMARY KEY,
    title           TEXT,
    company         TEXT,
    location_raw    TEXT,
    description     TEXT,
    salary_min      NUMERIC,
    salary_max      NUMERIC,
    contract_type   TEXT,
    category        TEXT,
    redirect_url    TEXT,
    created_at      TIMESTAMPTZ,
    first_seen_date DATE NOT NULL,
    last_seen_date  DATE NOT NULL,
    ingested_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS daily_snapshots (
    job_id        TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    search_term   TEXT,
    PRIMARY KEY (job_id, snapshot_date)
);

CREATE TABLE IF NOT EXISTS job_enrichment (
    job_id         TEXT PRIMARY KEY REFERENCES raw_jobs(job_id),
    seniority      TEXT,
    min_years_exp  INT,
    salary_min_inr NUMERIC,
    salary_max_inr NUMERIC,
    salary_period  TEXT,
    enriched_at    TIMESTAMPTZ DEFAULT now()
);

CREATE SCHEMA IF NOT EXISTS analytics;