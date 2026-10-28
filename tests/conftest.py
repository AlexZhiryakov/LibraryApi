"""Общие фикстуры для тестов.

Тесты работают на SQLite в памяти: зависимость get_db подменяется через
app.dependency_overrides, поэтому реальная БД (PostgreSQL) не требуется.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import hash_password

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _prepare_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_credentials():
    return {"username": "librarian", "password": "librarian-pass-1"}


@pytest.fixture
def admin_headers(client, db_session, admin_credentials):
    db_session.add(
        User(
            username=admin_credentials["username"],
            hashed_password=hash_password(admin_credentials["password"]),
            is_admin=True,
        )
    )
    db_session.commit()
    response = client.post("/token", json=admin_credentials)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def reader_credentials():
    return {"username": "reader", "password": "reader-pass-123"}


@pytest.fixture
def reader_headers(client, reader_credentials):
    client.post("/register", json=reader_credentials)
    response = client.post("/token", json=reader_credentials)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
