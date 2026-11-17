import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Citim variabilele din fișierul .env (dacă există), ca parola să nu stea în cod
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/travel_agency",
)

# SQLAlchemy 2.1+ folosește implicit driverul psycopg (v3) pentru "postgresql://".
# Noi avem instalat psycopg2, așa că îl cerem explicit.
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency FastAPI: deschide o sesiune pe request și o închide la final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
