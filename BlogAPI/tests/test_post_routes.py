import datetime
import json

from sqlalchemy.orm import Session

from BlogAPI.db.SQLAlchemy_models import Post
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
