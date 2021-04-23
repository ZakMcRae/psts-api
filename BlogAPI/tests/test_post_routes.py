import json

from sqlalchemy.orm import Session

from BlogAPI.db.SQLAlchemy_models import Post, Reply
from BlogAPI.dependencies.dependencies import get_current_user
from BlogAPI.main import api
from BlogAPI.tests.test_setup_and_utils import (
    client,
    db_non_commit,
    override_get_current_user_zak,
    TestingSessionLocal,
)


def test_create_post():
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"title": "My First Post", "body": "Welcome to my blog"}
    resp = client.post("/post", json.dumps(body))
    post = resp.json()

    assert resp.status_code == 200
    assert post.get("title") == "My First Post"
    assert post.get("id") == 21

    # delete created post to maintain database state
    db: Session = TestingSessionLocal()
    created_post = db.query(Post).get(post.get("id"))
    db.delete(created_post)
    db.commit()

    # verify created_post deleted successfully
    assert db.query(Post).get(post.get("id")) is None

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


def test_update_post(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"title": "My First Updated Post", "body": "Welcome to my blog."}
    resp = client.put("/post/<post-id>?post_id=1", json.dumps(body))
    post = resp.json()

    assert resp.status_code == 200
    assert post.get("title") == "My First Updated Post"
    assert post.get("id") == 1
    assert post.get("date_modified") is not None

    # fail case - post belongs to another user
    body = {"title": "My First Updated Post", "body": "Welcome to my blog."}
    resp = client.put("/post/<post-id>?post_id=2", json.dumps(body))

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This post belongs to another user"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


def test_delete_post(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    resp = client.delete("/post/<post-id>?post_id=1")

    assert resp.status_code == 200
    assert resp.json() == {"detail": "success"}

    # fail case - post belongs to another user
    resp = client.delete("/post/<post-id>?post_id=2")

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This post belongs to another user"}

    # fail case - post does not exist
    resp = client.delete("/post/<post-id>?post_id=999")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "This post does not exist"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


def test_get_post():
    resp = client.get("/post/<post-id>?post_id=1")
    post = resp.json()

    assert resp.status_code == 200
    assert post.get("title") == "zaktest's post #1"
    assert post.get("body") == "This is a post of mock data. Post #1"


def test_create_reply():
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"body": "My First Reply"}
    resp = client.post("/post/post-id/reply?post_id=1", json.dumps(body))
    reply = resp.json()

    assert resp.status_code == 200
    assert reply.get("body") == "My First Reply"
    assert reply.get("id") == 81

    # delete created post to maintain database state
    db: Session = TestingSessionLocal()
    created_reply = db.query(Reply).get(reply.get("id"))
    db.delete(created_reply)
    db.commit()

    # verify created_reply deleted successfully
    assert db.query(Post).get(reply.get("id")) is None

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


def test_get_replies():
    # successful case - id:1, skip:1, limit:3, sort:new first
    resp = client.get(
        "/post/<post-id>/replies?post_id=1&skip=1&limit=3&sort-newest-first=true"
    )
    replies = resp.json()

    assert resp.status_code == 200
    assert replies[0].get("body") == "This is a reply of mock data. Reply #1"
    assert replies[0].get("username") == "theotest"
    assert replies[2].get("username") == "zaktest"

    # successful case - id:3, skip:0, limit:4, sort:old first
    resp = client.get(
        "/post/<post-id>/replies?post_id=3&skip=0&limit=4&sort-newest-first=false"
    )
    replies = resp.json()

    assert resp.status_code == 200
    assert replies[0].get("body") == "This is a reply of mock data. Reply #3"
    assert replies[0].get("username") == "zaktest"
    assert replies[3].get("username") == "elliottest"


def test_get_recent_posts():
    # successful case - skip: 0, limit:5
    resp = client.get("/posts/recent?skip=0&limit=5")
    recent_posts = resp.json()

    assert resp.status_code == 200
    assert recent_posts[0].get("title") == "elliottest's post #5"
    assert recent_posts[4].get("title") == "elliottest's post #4"

    # failure case - skip: 0, limit:100
    resp = client.get("/posts/recent?skip=0&limit=100")
    resp_dict = resp.json()

    assert resp.status_code == 422
    assert (
        resp_dict["detail"][0].get("msg")
        == "ensure this value is less than or equal to 25"
    )
