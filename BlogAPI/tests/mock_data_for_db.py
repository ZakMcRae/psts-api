from passlib.hash import bcrypt

from BlogAPI.db.SQLAlchemy_models import User, Post, Reply
from BlogAPI.tests.test_db_setup import TestingSessionLocal, Base, engine

session = TestingSessionLocal()


def add_sample_users():
    """
    adds 4 different users
    to build a test database full of test info
    """
    zak = User()
    zak.username = "zaktest"
    zak.email = "zaktest@example.com"
    zak.hs_password = bcrypt.hash("123")

    jess = User()
    jess.username = "jesstest"
    jess.email = "jesstest@example.com"
    jess.hs_password = bcrypt.hash("123")

    theo = User()
    theo.username = "theotest"
    theo.email = "theotest@example.com"
    theo.hs_password = bcrypt.hash("123")

    elliot = User()
    elliot.username = "elliottest"
    elliot.email = "elliottest@example.com"
    elliot.hs_password = bcrypt.hash("123")

    session = TestingSessionLocal()
    try:
        session.add(zak)
        session.add(jess)
        session.add(theo)
        session.add(elliot)
        session.commit()
        session.close()
        print("Users added successfully")
        return True
    except Exception as error:
        return f"error occurred: {error}"


def add_sample_posts():
    """
    adds 5 posts for 4 different users
    to build a test database full of test info
    """
    session = TestingSessionLocal()

    all_users = ["zaktest", "jesstest", "theotest", "elliottest"]

    for counter in range(1, 6):
        for user in all_users:
            user = session.query(User).filter_by(username=f"{user}").first()

            post = Post()
            post.title = f"{user.username}'s post #{counter}"
            post.body = f"This is a post of mock data. Post #{counter}"
            post.user_id = user.id
            post.username = user.username

            session.add(post)
            session.commit()

    session.close()
    print("Posts added successfully")


def add_sample_replies():
    """
    adds 1 reply per user to every post
    to build a test database full of test info
    """
    session = TestingSessionLocal()

    posts = session.query(Post).all()

    for counter, post in enumerate(posts):
        all_users = ["zaktest", "jesstest", "theotest", "elliottest"]

        for user in all_users:
            user = session.query(User).filter_by(username=f"{user}").first()

            reply = Reply()
            reply.body = f"This is a reply of mock data. Reply #{counter + 1}"
            reply.user_id = user.id
            reply.post_id = post.id
            reply.username = user.username

            session.add(reply)
            session.commit()

    session.close()
    print("Replies added successfully")


def add_sample_follows():
    """
    makes users follow each other
    for testing follower/following functionality
    to build a test database full of test info
    """
    session = TestingSessionLocal()

    zak = session.query(User).filter_by(username="zaktest").first()
    jess = session.query(User).filter_by(username="jesstest").first()
    theo = session.query(User).filter_by(username="theotest").first()
    # leaving elliot blank to test no followers/following

    try:
        zak.followers += [jess, theo]
        jess.followers += [zak, theo]
        theo.followers += [zak, jess]
        session.commit()
        print("Follows added successfully")
    except Exception as error:
        return f"error occurred: {error}"


def rebuild_test_db():
    """
    Mock data for testing
    4 users (with some following others), 20 posts (5 per user), 80 replies (1 reply per user per post)
    """

    # drop tables and then recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # add mock data
    add_sample_users()
    add_sample_posts()
    add_sample_replies()
    add_sample_follows()


if __name__ == "__main__":
    rebuild_test_db()
