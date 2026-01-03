"""Database connection and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.schemas import Base
import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/publix_db"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


@lru_cache()
def get_engine():
    """Get cached database engine"""
    return engine
