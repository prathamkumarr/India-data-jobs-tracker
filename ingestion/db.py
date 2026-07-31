import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

def db_url():
    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["SUPABASE_DB_USER"],
        password=os.environ["SUPABASE_DB_PASSWORD"],
        host=os.environ["SUPABASE_DB_HOST"],
        port=int(os.environ.get("SUPABASE_DB_PORT", "5432")),
        database=os.environ["SUPABASE_DB_NAME"],
    )