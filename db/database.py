"""
Database configuration for PMS Generator.
SQLAlchemy engine and session management with SQLite.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# On Render (or any cloud env), use /tmp which is always writable.
# Locally, keep the DB next to the project root.
if os.environ.get("DATABASE_URL"):
    # PostgreSQL or other external DB provided via env var
    DATABASE_URL = os.environ["DATABASE_URL"]
    # Fix Render's postgres:// → postgresql:// for SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    DB_PATH = None
elif os.environ.get("RENDER"):
    # Render.com — use /tmp so writes always succeed
    DB_PATH = "/tmp/pms_generator.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pms_generator.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread is SQLite-only; pass it only when using SQLite
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def run_migrations():
    """Add any new columns to existing tables without dropping data."""
    new_columns = [
        ("design_pressure_barg", "REAL"),
        ("design_temp_c",        "REAL"),
        ("corrosion_allowance",  "REAL"),
        ("flange_class",         "TEXT"),
        ("service",              "TEXT"),
        ("is_nace",              "INTEGER DEFAULT 0"),
        ("is_low_temp",          "INTEGER DEFAULT 0"),
    ]
    with engine.connect() as conn:
        for col_name, col_type in new_columns:
            try:
                conn.execute(text(f"ALTER TABLE saved_specs ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                pass  # Column already exists — safe to ignore


def get_db():
    """Dependency injection for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
