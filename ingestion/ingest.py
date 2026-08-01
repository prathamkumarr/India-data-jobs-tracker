import time, datetime, requests, os
from zoneinfo import ZoneInfo
from sqlalchemy import create_engine, text
from db import db_url
from config import COUNTRY, SEARCH_TERMS, PAGES_PER_TERM, RESULTS_PER_PAGE

APP_ID  = os.environ["ADZUNA_APP_ID"]
APP_KEY = os.environ["ADZUNA_APP_KEY"]
engine  = create_engine(db_url())
run_date = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).date()

def fetch(term, page, max_retries=3):
    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}"
    params = {
        "app_id": APP_ID, "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE, "what": term,
        "content-type": "application/json",
    }
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json().get("results", [])
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                print(f"  !! {term} p{page} failed after {max_retries} attempts: {e}")
                return []          # skip this page, keep the run alive
            wait = 2 ** attempt    # 2s, then 4s
            print(f"  .. {term} p{page} attempt {attempt} failed, retrying in {wait}s")
            time.sleep(wait)

def normalize(job):
    return {
        "job_id":        str(job["id"]),
        "title":         job.get("title"),
        "company":       (job.get("company")  or {}).get("display_name"),
        "location_raw":  (job.get("location") or {}).get("display_name"),
        "description":   job.get("description"),
        "salary_min":    job.get("salary_min"),
        "salary_max":    job.get("salary_max"),
        "contract_type": job.get("contract_type"),
        "category":      (job.get("category") or {}).get("label"),
        "redirect_url":  job.get("redirect_url"),
        "created_at":    job.get("created"),
    }

UPSERT_JOB = text("""
INSERT INTO raw_jobs (job_id, title, company, location_raw, description,
    salary_min, salary_max, contract_type, category, redirect_url,
    created_at, first_seen_date, last_seen_date)
VALUES (:job_id, :title, :company, :location_raw, :description,
    :salary_min, :salary_max, :contract_type, :category, :redirect_url,
    :created_at, :run_date, :run_date)
ON CONFLICT (job_id) DO UPDATE
    SET last_seen_date = EXCLUDED.last_seen_date;
""")

INSERT_SNAPSHOT = text("""
INSERT INTO daily_snapshots (job_id, snapshot_date, search_term)
VALUES (:job_id, :run_date, :search_term)
ON CONFLICT (job_id, snapshot_date) DO NOTHING;
""")

def main():
    processed = 0
    failed_pages = 0
    with engine.begin() as conn:
        for term in SEARCH_TERMS:
            for page in range(1, PAGES_PER_TERM + 1):
                jobs = fetch(term, page)
                if not jobs:
                    failed_pages += 1
                for job in jobs:
                    rec = normalize(job)
                    rec["run_date"] = run_date
                    conn.execute(UPSERT_JOB, rec)
                    conn.execute(INSERT_SNAPSHOT, {**rec, "search_term": term})
                    processed += 1
                print(f"  {term} p{page}: {len(jobs)} jobs")
                time.sleep(1)
    print(f"[{run_date}] processed {processed} postings ({failed_pages} pages skipped)")

if __name__ == "__main__":
    main()