from db import db_url
from sqlalchemy import create_engine, text

engine = create_engine(db_url())
with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) FROM raw_jobs;"))
    print("Connected! raw_jobs row count:", result.scalar())