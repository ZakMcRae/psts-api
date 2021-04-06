import fastapi

import db_session
from models import User

from util.mock_data import (
    add_sample_users,
    add_sample_posts,
    add_sample_replies,
    add_sample_follows,
)

router = fastapi.APIRouter()


@router.get("/")
def home():
    # display all routes for quick access for testing - temp home
    all_routes = [f"http://127.0.0.1:8000/{route.name}" for route in router.routes]
    return all_routes


@router.get("/test")
def test():
    session = db_session.create_session()
    zak: User = session.query(User).filter_by(username="zak").first()
    # jess: User = session.query(User).filter_by(username="jess").first()
    # theo: User = session.query(User).filter_by(username="theo").first()
    # elliot: User = session.query(User).filter_by(username="elliot").first()

    return zak.followers


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
