from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import User

from BlogAPI.util.mock_data import (
    add_sample_users,
    add_sample_posts,
    add_sample_replies,
    add_sample_follows,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
secret_key = None


@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return {"access_token": form_data.username + "token"}


@router.get("/test_token")
def test_token(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@router.get("/test")
def test():
    return "test"


@router.get("/")
def home():
    # display all routes for quick access for testing - temp home
    all_routes = [f"http://127.0.0.1:8000/{route.name}" for route in router.routes]
    return all_routes


@router.get("/query_users")
def query_users():
    session = db_session.create_session()
    x = session.query(User).all()
    # y = session.query(User).filter_by(id=1).first()
    # z = session.query(User).filter_by(name="Jess").first()
    return x


@router.get("/add_users")
def add_users():
    return add_sample_users()


@router.get("/add_posts")
def add_posts():
    return add_sample_posts()


@router.get("/add_replies")
def add_replies():
    return add_sample_replies()


@router.get("/add_follows")
def add_follows():
    return add_sample_follows()
