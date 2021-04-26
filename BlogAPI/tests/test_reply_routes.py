import json

from BlogAPI.dependencies.dependencies import get_current_user
from BlogAPI.main import api
from BlogAPI.tests.test_setup_and_utils import (
    client,
    override_get_current_user_zak,
    db_non_commit,
)


def test_update_reply(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"body": "Great post! Can't wait to hear more."}
    resp = client.put("/reply/<reply-id>?reply_id=1", json.dumps(body))
    reply = resp.json()

    assert resp.status_code == 200
    assert reply.get("body") == "Great post! Can't wait to hear more."
    assert reply.get("id") == 1
    assert reply.get("date_modified") is not None

    # fail case - reply belongs to another user
    body = {"title": "My First Updated Reply", "body": "Welcome to my blog."}
    resp = client.put("/reply/<reply-id>?reply_id=2", json.dumps(body))

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This reply belongs to another user"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


def test_delete_reply(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    resp = client.delete("/reply/<reply-id>?reply_id=1")

    assert resp.status_code == 200
    assert resp.json() == {"detail": "success"}

    # fail case - reply belongs to another user
    resp = client.delete("/reply/<reply-id>?reply_id=2")

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This reply belongs to another user"}

    # fail case - reply does not exist
    resp = client.delete("/reply/<reply-id>?reply_id=999")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "This reply does not exist"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


def test_get_reply():
    resp = client.get("/reply/<reply-id>?reply_id=1")
    reply = resp.json()

    assert resp.status_code == 200
    assert reply.get("body") == "This is a reply of mock data. Reply #1"
    assert reply.get("username") == "zaktest"
