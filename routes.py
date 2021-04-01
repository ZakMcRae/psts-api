import fastapi

import db_session
from models import User

from util.mock_data import add_users, add_posts, add_replies

router = fastapi.APIRouter()


@router.get("/")
def home():
    all_routes = [f"http://127.0.0.1:8000/{route.name}" for route in router.routes]
    return all_routes


@router.get("/test")
def test():
    session = db_session.create_session()
    user = session.query(User).filter_by(username="zak").first()
    return user.replies


@router.get("/queryusers")
def queryusers():
    session = db_session.create_session()
    x = session.query(User).all()
    # y = session.query(User).filter_by(id=1).first()
    # z = session.query(User).filter_by(name="Jess").first()
    return x


@router.get("/addusers")
def addusers():
    return add_users()


@router.get("/addposts")
def addposts():
    return add_posts()


@router.get("/addreplies")
def addreplies():
    return add_replies()
