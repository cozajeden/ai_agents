import os
from sqlmodel import create_engine
from sqlalchemy import text
from sqlalchemy.engine import make_url


def test_test_db():
	# Use DATABASE_URL as set by test session; it should already point to the test DB
	url_str = os.environ.get("DATABASE_URL")
	assert url_str, "DATABASE_URL must be set by test setup"
	url = make_url(url_str)
	assert url.database, "DATABASE_URL must include a database name"
	assert url.database.endswith("_test"), "DATABASE_URL must point to a _test database during tests"
	# Connect to the test DB and run a simple query
	engine = create_engine(url_str, pool_pre_ping=True)
	with engine.connect() as conn:
		current_db = conn.execute(text("SELECT current_database()"))
		current_db = current_db.scalar()
		assert current_db == url.database
		assert conn.execute(text("SELECT 1")).scalar() == 1
