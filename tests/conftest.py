import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from database.session import get_session
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    }
