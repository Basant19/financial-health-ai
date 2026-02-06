# E:\financial-health-ai\database\database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

# ----------------------------------
# Load environment variables
# ----------------------------------
load_dotenv()
logger = get_logger("Database")

# ----------------------------------
# Database URL
# ----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL not set in environment variables!")
    raise CustomException("DATABASE_URL environment variable is missing.")

# ----------------------------------
# SQLAlchemy Engine & Session
# ----------------------------------
try:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine and session created successfully.")
except Exception as e:
    logger.exception("Failed to create database engine/session.")
    raise CustomException(f"Database connection failed: {str(e)}")

# ----------------------------------
# Base class for models
# ----------------------------------
Base = declarative_base()

# ----------------------------------
# FastAPI dependency
# ----------------------------------
def get_db():
    """
    Yield a database session for FastAPI routes.
    Ensures session is closed after use.
    """
    db = None
    try:
        db = SessionLocal()
        logger.debug("Database session created.")
        yield db
    except Exception as e:
        logger.exception("Error in database session.")
        raise CustomException(f"Database session error: {str(e)}")
    finally:
        if db:
            db.close()
            logger.debug("Database session closed.")
