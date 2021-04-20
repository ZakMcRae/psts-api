from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from BlogAPI.main import api
from BlogAPI.dependencies.dependencies import get_db
from BlogAPI.db.SQLAlchemy_models import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


api.dependency_overrides[get_db] = override_get_db

client = TestClient(api)


def test_get_user():
    resp = client.get("/get_user_test?user_id=1")

    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "email": "zak@example.com",
        "username": "zaktest",
        "hs_password": "password",
    }
