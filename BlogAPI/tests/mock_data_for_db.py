from passlib.hash import bcrypt

from BlogAPI.db.SQLAlchemy_models import User, Post, Reply
from BlogAPI.tests.test_setup_and_utils import TestingSessionLocal, Base, engine

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

    db_session = TestingSessionLocal()
    try:
        db_session.add(zak)
        db_session.add(jess)
        db_session.add(theo)
        db_session.add(elliot)
        db_session.commit()
        db_session.close()
        print("Users added successfully")
        return True
    except Exception as error:
        return f"error occurred: {error}"


def add_sample_posts(number_of_posts: int = 5):
    """
    adds 5 posts for 4 different users
    to build a test database full of test info
    """
    db_session = TestingSessionLocal()

    all_users = ["zaktest", "jesstest", "theotest", "elliottest"]

    for counter in range(1, number_of_posts + 1):
        for user in all_users:
            user = db_session.query(User).filter_by(username=f"{user}").first()

            post = Post()
            post.title = f"{user.username}'s post #{counter}"
            post.body = f"This is a post of mock data. Post #{counter}"
            post.user_id = user.id
            post.username = user.username

            db_session.add(post)
            db_session.commit()

    db_session.close()
    print("Posts added successfully")


def add_sample_replies():
    """
    adds 1 reply per user to every post
    to build a test database full of test info
    """
    db_session = TestingSessionLocal()

    posts = db_session.query(Post).all()

    for counter, post in enumerate(posts):
        all_users = ["zaktest", "jesstest", "theotest", "elliottest"]

        for user in all_users:
            user = db_session.query(User).filter_by(username=f"{user}").first()

            reply = Reply()
            reply.body = f"This is a reply of mock data. Reply #{counter + 1}"
            reply.user_id = user.id
            reply.post_id = post.id
            reply.username = user.username

            db_session.add(reply)
            db_session.commit()

    db_session.close()
    print("Replies added successfully")


def add_sample_follows():
    """
    makes users follow each other
    for testing follower/following functionality
    to build a test database full of test info
    """
    db_session = TestingSessionLocal()

    zak = db_session.query(User).filter_by(username="zaktest").first()
    jess = db_session.query(User).filter_by(username="jesstest").first()
    theo = db_session.query(User).filter_by(username="theotest").first()
    # leaving elliot blank to test no followers/following

    try:
        zak.followers += [jess, theo]
        jess.followers += [zak, theo]
        theo.followers += [zak, jess]
        db_session.commit()
        print("Follows added successfully")
    except Exception as error:
        return f"error occurred: {error}"


def rebuild_test_db(number_of_posts: int = 5):
    """
    Mock data for testing
    4 users (with some following others), 20 posts (5 per user), 80 replies (1 reply per user per post)
    """

    # drop tables and then recreate
    print("Drop all tables")
    Base.metadata.drop_all(bind=engine)
    print("Create all tables")
    Base.metadata.create_all(bind=engine)

    # add mock data
    add_sample_users()
    add_sample_posts(number_of_posts)
    add_sample_replies()
    add_sample_follows()


if __name__ == "__main__":
    rebuild_test_db(5)

    # default to not interfere with tests is 5
    # rebuild_test_db(5)
