"""
pytest config/fixture file, this run before test start.
main purpose is to make test use separate test db, not the real dev db.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://urluser:urlpassword@localhost:5434/urlshortener_test",
)
"""hardcoded connection string for test postgres db (different port 5434 so it dont clash with dev db)"""


engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    """
    same as get_db but pointing to test db instead of real one.
    """
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()



app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """
    fixture that give fresh TestClient for each test, also wipe n
    recreate table so every test start clean, no leftover data from
    previous test.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    
