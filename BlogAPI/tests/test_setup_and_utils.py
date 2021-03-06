import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from BlogAPI.db.SQLAlchemy_models import Base, User
from main import api

# This points the api/test client to test.db instead of blog.db
SQLALCHEMY_DATABASE_URL = (
    r"sqlite:///C:\Users\Zak\PycharmProjects\BlogAPI\BlogAPI\tests\test.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)


def override_get_current_user_zak():
    # for fastapi dependency overrides - skip authentication for tests
    return User(
        id=1,
        username="zaktest",
        email="zaktest@example.com",
        hs_password="$2b$12$avqsZP6Gt1Ixgxd7C9BQFe/I44yAm4sqklNUl9DFbyUhLBRzDQtCK",
    )


def override_get_current_user_elliot():
    # for fastapi dependency overrides - skip authentication for tests
    return User(
        id=4,
        username="elliottest",
        email="elliottest@example.com",
        hs_password="$2b$12$avqsZP6Gt1Ixgxd7C9BQFe/I44yAm4sqklNUl9DFbyUhLBRzDQtCK",
    )


@pytest.fixture
def db_non_commit(monkeypatch):
    """
    changes SQLAlchemy orm behaviours
    this does not allow any changes to be made to the test db
    """

    # noinspection PyUnusedLocal
    def mock_return(*args, **kwargs):
        pass

    monkeypatch.setattr(Session, "add", mock_return)
    monkeypatch.setattr(Session, "delete", mock_return)
    monkeypatch.setattr(Session, "commit", mock_return)
    monkeypatch.setattr(Session, "refresh", mock_return)


# import client into other test files to test routes on test.db
client = TestClient(api)
