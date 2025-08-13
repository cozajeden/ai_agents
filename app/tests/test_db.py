import os
from sqlmodel import create_engine, Session, select


def test_test_db(session):
    """Test that the test database is set up correctly"""
    url_str = os.environ.get("DATABASE_URL")
    assert url_str, "DATABASE_URL must be set by test setup"
    assert url_str.endswith("_test") or "/_test" in url_str, "DATABASE_URL must point to a _test database during tests"

    result = session.exec(select(1)).one()
    assert result == 1
