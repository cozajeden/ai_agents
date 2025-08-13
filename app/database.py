from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from contextlib import asynccontextmanager
import asyncio
from pathlib import Path

# Database configuration - use the mounted volume directory
DATABASE_URL = "sqlite:///./data/ollama_fastapi.db"
DB_PATH = Path("./data/ollama_fastapi.db")

# Create engine
engine = None

async def init_db():
    """Initialize database connection and create tables"""
    global engine
    
    # Ensure database directory exists and has proper permissions
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine with proper SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging
        connect_args={
            "check_same_thread": False,
            "timeout": 30.0
        }
    )
    
    # Create all tables
    await create_tables()
    
    print(f"Database initialized at {DB_PATH.absolute()}")

async def close_db():
    """Close database connections"""
    global engine
    
    if engine:
        engine.dispose()
        engine = None
        print("Database connections closed")

async def create_tables():
    """Create database tables"""
    # Import your models here
    from models.base import ModelRequest, ChatInteraction
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("Database tables created")

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

# Helper function for database operations
def execute_query(query: str, params: dict = None) -> list:
    """Execute a raw query and return results"""
    if not engine:
        raise RuntimeError("Database not initialized")
    
    with Session(engine) as session:
        if params:
            result = session.exec(query, params)
        else:
            result = session.exec(query)
        return result.all()
