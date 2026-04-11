import os
import jwt
import pytest
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.db.base import Base
from src.db.core import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

TEST_EMAIL = "test@mail.com"
TEST_USER_ID = "2e3c7f4f-9c3a-4f7a-bb9c-6a4e3c5b3f1e"
TEST_FIRST_NAME = "Tester"
TEST_LAST_NAME = "Testermann"
TEST_PASSWORD = "test-pass"

TEST_EMAIL_2 = "test2@mail.com"
TEST_USER_ID_2 = "f2d7f3d2-6f5a-4a9c-bb6c-2a3f6e0f51e1"
TEST_FIRST_NAME_2 = "Jeb"
TEST_LAST_NAME_2 = "Jebbers"
TEST_PASSWORD_2 = "jeb-pass"


@dataclass(frozen=True)
class TestUserData:
    email: str
    first_name: str
    last_name: str
    password: str


@pytest.fixture(scope="function")
def db_session():
    mock_db_url = "sqlite:///./test.db"
    engine = create_engine(
        mock_db_url,
        connect_args={"check_same_thread": False},
    )
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_token() -> str:
    payload = {
        "sub": TEST_EMAIL,
        "id": TEST_USER_ID,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture(scope="function")
def test_user_data() -> TestUserData:
    return TestUserData(
        TEST_EMAIL,
        TEST_FIRST_NAME,
        TEST_LAST_NAME,
        TEST_PASSWORD,
    )


@pytest.fixture(scope="function")
def test_user_id() -> str:
    return TEST_USER_ID


@pytest.fixture(scope="function")
def test_user_2_data() -> TestUserData:
    return TestUserData(
        TEST_EMAIL_2,
        TEST_FIRST_NAME_2,
        TEST_LAST_NAME_2,
        TEST_PASSWORD_2,
    )


@pytest.fixture(scope="function")
def test_user_2_id() -> str:
    return TEST_USER_ID_2
