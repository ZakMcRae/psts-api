from models import User, Post, Reply
import db_session


def add_users():
    zak = User()
    zak.username = "zak"
    zak.email = "z@z.com"
    zak.hs_password = "123"

    jess = User()
    jess.username = "jess"
    jess.email = "j@j.com"
    jess.hs_password = "123"

    session = db_session.create_session()
    try:
        session.add(zak)
        session.add(jess)
        session.commit()
        return "added users"
    except Exception as error:
        return f"error occurred: {error}"


def add_posts():
    session = db_session.create_session()
    zak = session.query(User).filter_by(username="zak").first()
    jess = session.query(User).filter_by(username="jess").first()

    pz = Post()
    pz.title = "zak's first post"
    pz.body = "This is a first test post of mock data"
    pz.user_id = zak.id

    pj = Post()
    pj.title = "jess's first post"
    pj.body = "This is a first test post of mock data"
    pj.user_id = jess.id

    try:
        session.add(pz)
        session.add(pj)
        session.commit()
        return "posted"
    except Exception as error:
        return f"error occurred: {error}"


def add_replies():
    session = db_session.create_session()
    pz = session.query(Post).filter_by(user_id=1).first()
    pj = session.query(Post).filter_by(user_id=2).first()

    rz = Reply()
    rz.title = "zak's first reply"
    rz.body = "This is a first test reply of mock data"
    rz.user_id = pz.user_id
    rz.post_id = pz.id

    rj = Reply()
    rj.title = "jess's first reply"
    rj.body = "This is a first test reply of mock data"
    rj.user_id = pj.user_id
    rj.post_id = pj.id

    try:
        session.add(rz)
        session.add(rj)
        session.commit()
        return "posted"
    except Exception as error:
        return f"error occurred: {error}"
