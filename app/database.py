from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from contextlib import asynccontextmanager
import os

# Database configuration - use PostgreSQL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ollama_user:ollama_password@postgres:5432/ollama_fastapi")

# Create engine
engine = None

async def init_db():
    """Initialize database connection and create tables"""
    global engine

    # Create engine with PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections every 5 minutes
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("Database tables created")

    print(f"Database initialized with PostgreSQL")

async def close_db():
    """Close database connections"""
    global engine

    if engine:
        engine.dispose()
        engine = None
        print("Database connections closed")

def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    if not engine:
        raise RuntimeError("Database not initialized")

    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
