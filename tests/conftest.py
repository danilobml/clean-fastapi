import os
from uuid import UUID, uuid4
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
from src.entities.job import Job, Priority
from src.entities.user import User
from src.security.jwt import create_access_token
from src.security.password import get_hashed_password
from src.rate_limiting import limiter

limiter.enabled = False

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


@pytest.fixture(scope="function")
def _test_user(db_session, test_user_data, test_user_id):
    user = User(
        id=UUID(test_user_id),
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def _two_users(db_session, test_user_data, test_user_2_data):
    user_1 = User(
        first_name=test_user_data.first_name,
        last_name=test_user_data.last_name,
        email=test_user_data.email,
        hashed_password=get_hashed_password(test_user_data.password),
    )
    user_2 = User(
        first_name=test_user_2_data.first_name,
        last_name=test_user_2_data.last_name,
        email=test_user_2_data.email,
        hashed_password=get_hashed_password(test_user_2_data.password),
    )

    db_session.add_all([user_1, user_2])
    db_session.commit()
    db_session.refresh(user_1)
    db_session.refresh(user_2)

    return user_1, user_2


@pytest.fixture(scope="function")
def test_job(db_session):
    job = Job(
        id=uuid4(),
        user_id=UUID(TEST_USER_ID),
        description="Test job",
        due_date=datetime.now() + timedelta(days=2),
        priority=Priority.medium,
    )

    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture(scope="function")
def three_test_jobs(db_session, _two_users):
    user_1, user_2 = _two_users

    job_1 = Job(
        id=uuid4(),
        user_id=user_1.id,
        description="Test job 1",
        due_date=datetime.now() + timedelta(days=2),
        priority=Priority.medium,
    )
    job_2 = Job(
        id=uuid4(),
        user_id=user_1.id,
        description="Test job 2",
        due_date=datetime.now() + timedelta(days=1),
        priority=Priority.high,
        is_completed=True,
    )
    job_3 = Job(
        id=uuid4(),
        user_id=user_2.id,
        description="Test job 3",
        due_date=datetime.now() + timedelta(days=5),
        priority=Priority.low,
    )

    db_session.add_all([job_1, job_2, job_3])
    db_session.commit()
    db_session.refresh(job_1)
    db_session.refresh(job_2)
    db_session.refresh(job_3)

    return job_1, job_2, job_3


@pytest.fixture(scope="function")
def auth_user(db_session):
    user = User(
        id=UUID("9c3e5a1f-6b2d-4d8e-8a7f-2f9c6b1e4a73"),
        first_name="Auth",
        last_name="User",
        email="auth_user@mail.com",
        hashed_password=get_hashed_password("auth-pass"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(auth_user):
    token = create_access_token(
        email=auth_user.email, user_id=auth_user.id, expire_delta=timedelta(minutes=30)
    )

    return {"Authorization": f"Bearer {token}"}
