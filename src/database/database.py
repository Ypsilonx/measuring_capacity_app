# src/database/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.utils.app_logger import get_logger

logger = get_logger()

# --- Configuration ---
# Define the path for the data directory
DATA_DIR = "data"
DB_NAME = "measuring_capacity.db"
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, DB_NAME)}"

# --- Engine ---
# The engine is the central point of communication with the database.
# `connect_args` is specific to SQLite to allow multithreaded access.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True to see generated SQL statements
)

# --- Session ---
# SessionLocal is a factory for creating new Session objects.
# A Session is the workspace for all database operations (queries, commits, etc.).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Database Initialization ---
def init_db():
    """
    Creates the data directory if it doesn't exist and then creates all
    database tables based on the models defined in models.py.
    This function should be called once at application startup.
    """
    # Ensure the data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Vytvořen adresář: {DATA_DIR}")

    # Create all tables
    logger.info("Inicializace databáze a vytváření tabulek...")
    Base.metadata.create_all(bind=engine)
    logger.info("Databázové tabulky jsou připraveny.")

def get_db():
    """
    Dependency function to get a database session.
    Ensures that the database session is always closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

