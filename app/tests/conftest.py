import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from database import get_db

# Test database - use PostgreSQL test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://ollama_user:ollama_password@postgres:5432/ollama_fastapi_test"
)

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables for testing
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session
    
    # Clean up - drop all tables after test
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_chat_request():
    """Sample chat request data for testing"""
    return {
        "message": "Hello, how are you?",
        "model_name": "llama3.1:8b"
    }

@pytest.fixture
def sample_model_request():
    """Sample model request data for testing"""
    return {
        "model_name": "test-model",
        "prompt": "Test prompt",
        "status": "pending"
    }
