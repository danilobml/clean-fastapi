import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.core import Base

@pytest.fixture(scope="function")
def db_session():
    MOCK_DB_URL = "sqlite:///./test.db"
    engine = create_engine(MOCK_DB_URL, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
