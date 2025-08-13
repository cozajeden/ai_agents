import os
from urllib.parse import urlsplit, urlunsplit, SplitResult
import pytest
from sqlmodel import create_engine, Session
from fastapi.testclient import TestClient
from app import main

PROD_DB_URL = os.environ.get("DATABASE_URL")
if not PROD_DB_URL:
    raise RuntimeError("DATABASE_URL env var must be set for tests")

_SPLIT = urlsplit(PROD_DB_URL)
_BASE_DB_NAME = _SPLIT.path.lstrip("/")
if not _BASE_DB_NAME:
    raise RuntimeError("DATABASE_URL must include a database name")

TEST_DB_NAME = f"{_BASE_DB_NAME}_test"
_TEST_SPLIT = SplitResult(_SPLIT.scheme, _SPLIT.netloc, f"/{TEST_DB_NAME}", _SPLIT.query, _SPLIT.fragment)
TEST_DB_URL = urlunsplit(_TEST_SPLIT)
_ADMIN_SPLIT = SplitResult(_SPLIT.scheme, _SPLIT.netloc, "/postgres", _SPLIT.query, _SPLIT.fragment)
ADMIN_URL = urlunsplit(_ADMIN_SPLIT)


def set_up_tests():
    """Set up the test database"""
    os.environ["DATABASE_URL"] = TEST_DB_URL
    admin_engine = create_engine(ADMIN_URL, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.exec_driver_sql(
            f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'"
        ).scalar() is not None
        if not exists:
            conn.exec_driver_sql(f"CREATE DATABASE \"{TEST_DB_NAME}\"")


def tear_down_tests():
    """Tear down the test database"""
    admin_engine = create_engine(ADMIN_URL, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.exec_driver_sql(
            f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid()"
        )
        conn.exec_driver_sql(f"DROP DATABASE IF EXISTS \"{TEST_DB_NAME}\"")


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown():
    """Set up and tear down the test database"""
    set_up_tests()
    yield
    tear_down_tests()


@pytest.fixture(scope="function")
def client():
    """FastAPI TestClient bound to the app. Uses app lifespan (DB init/close)."""
    with TestClient(main.app) as c:
        yield c


@pytest.fixture(scope="function")
def session():
    """Provide a SQLModel Session bound to the test database for tests that request 'session'."""
    engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
    with Session(engine) as s:
        yield s
