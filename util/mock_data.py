from SQLAlchemy_models import User, Post, Reply
import db_session


def add_sample_users():
    zak = User()
    zak.username = "zak"
    zak.email = "z@z.com"
    zak.hs_password = "123"

    jess = User()
    jess.username = "jess"
    jess.email = "j@j.com"
    jess.hs_password = "123"

    theo = User()
    theo.username = "theo"
    theo.email = "t@t.com"
    theo.hs_password = "123"

    elliot = User()
    elliot.username = "elliot"
    elliot.email = "e@e.com"
    elliot.hs_password = "123"

    session = db_session.create_session()
    try:
        session.add(zak)
        session.add(jess)
        session.add(theo)
        session.add(elliot)
        session.commit()
        return "added users"
    except Exception as error:
        return f"error occurred: {error}"


def add_sample_posts():
    session = db_session.create_session()
    zak = session.query(User).filter_by(username="zak").first()
    jess = session.query(User).filter_by(username="jess").first()
    theo = session.query(User).filter_by(username="theo").first()
    elliot = session.query(User).filter_by(username="elliot").first()

    pz = Post()
    pz.title = "zak's first post"
    pz.body = "This is a first test post of mock data"
    pz.user_id = zak.id

    pj = Post()
    pj.title = "jess's first post"
    pj.body = "This is a first test post of mock data"
    pj.user_id = jess.id

    pt = Post()
    pt.title = "theo's first post"
    pt.body = "This is a first test post of mock data"
    pt.user_id = theo.id

    pe = Post()
    pe.title = "elliot's first post"
    pe.body = "This is a first test post of mock data"
    pe.user_id = elliot.id

    try:
        session.add(pz)
        session.add(pj)
        session.add(pt)
        session.add(pe)
        session.commit()
        return "added posts"
    except Exception as error:
        return f"error occurred: {error}"


def add_sample_replies():
    session = db_session.create_session()
    pz = session.query(Post).filter_by(user_id=1).first()
    pj = session.query(Post).filter_by(user_id=2).first()
    pt = session.query(Post).filter_by(user_id=3).first()
    pe = session.query(Post).filter_by(user_id=4).first()

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

    rt = Reply()
    rt.title = "theo's first reply"
    rt.body = "This is a first test reply of mock data"
    rt.user_id = pt.user_id
    rt.post_id = pt.id

    re = Reply()
    re.title = "elliot's first reply"
    re.body = "This is a first test reply of mock data"
    re.user_id = pe.user_id
    re.post_id = pe.id

    try:
        session.add(rz)
        session.add(rj)
        session.add(rt)
        session.add(re)
        session.commit()
        return "added replies"
    except Exception as error:
        return f"error occurred: {error}"


def add_sample_follows():
    session = db_session.create_session()
    zak = session.query(User).filter_by(username="zak").first()
    jess = session.query(User).filter_by(username="jess").first()
    theo = session.query(User).filter_by(username="theo").first()
    elliot = session.query(User).filter_by(username="elliot").first()

    try:
        zak.followers += [theo, elliot]
        jess.followers += [zak, theo, elliot]
        session.commit()
        return "added follows"
    except Exception as error:
        return f"error occurred: {error}"
