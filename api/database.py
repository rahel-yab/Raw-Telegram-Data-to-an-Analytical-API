import os
import re

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "POSTGRES_DSN",
    f"postgresql://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'password123')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5433')}/{os.getenv('DB_NAME', 'medical_data')}",
)
MARTS_SCHEMA = os.getenv("MARTS_SCHEMA", "marts")
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", MARTS_SCHEMA):
    raise ValueError("MARTS_SCHEMA must be a valid PostgreSQL identifier.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
