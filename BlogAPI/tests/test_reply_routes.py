import pytest
from httpx import AsyncClient

from BlogAPI.dependencies.dependencies import get_current_user
from main import api

# noinspection PyUnresolvedReferences
# db_non_commit pytest fixture used below - shows unused in editor
from BlogAPI.tests.test_setup_and_utils import (
    override_get_current_user_zak,
    db_non_commit,
)


@pytest.mark.asyncio
async def test_update_reply(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"body": "Great post! Can't wait to hear more."}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.put("/reply/1", json=body)
    reply = resp.json()

    assert resp.status_code == 200
    assert reply.get("body") == "Great post! Can't wait to hear more."
    assert reply.get("id") == 1
    assert reply.get("date_modified") is not None

    # fail case - reply belongs to another user
    body = {"title": "My First Updated Reply", "body": "Welcome to my blog."}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.put("/reply/2", json=body)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This reply belongs to another user"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_delete_reply(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/reply/1")

    assert resp.status_code == 204
    assert resp.json() == {"detail": "success"}

    # fail case - reply belongs to another user
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/reply/2")

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This reply belongs to another user"}

    # fail case - reply does not exist
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/reply/999")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "This reply does not exist"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_get_reply():
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/reply/1")
    reply = resp.json()

    assert resp.status_code == 200
    assert reply.get("body") == "This is a reply of mock data. Reply #1"
    assert reply.get("username") == "zaktest"
