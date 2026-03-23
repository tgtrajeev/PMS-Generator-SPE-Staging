"""
Database configuration for PMS Generator.
SQLAlchemy engine and session management with SQLite.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pms_generator.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
