import pytest

from httpx import AsyncClient
from sqlalchemy import select

from BlogAPI.db.SQLAlchemy_models import Post, Reply
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.dependencies.dependencies import get_current_user
from main import api

# noinspection PyUnresolvedReferences
# db_non_commit pytest fixture used below - shows unused in editor
from BlogAPI.tests.test_setup_and_utils import (
    db_non_commit,
    override_get_current_user_zak,
)


@pytest.mark.asyncio
async def test_create_post():
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"title": "My First Post", "body": "Welcome to my blog"}

    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/post", json=body)

    post = resp.json()

    assert resp.status_code == 201
    assert post.get("title") == "My First Post"
    assert post.get("id") == 21

    # delete created post to maintain database state
    async with create_async_session() as session:
        query = select(Post).filter(Post.id == post.get("id"))
        result = await session.execute(query)
        created_post = result.scalar_one_or_none()

        await session.delete(created_post)
        await session.commit()

        # verify created_post deleted successfully

        query = select(Post).filter(Post.id == post.get("id"))
        result = await session.execute(query)
        test_post = result.scalar_one_or_none()

    assert test_post is None

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_update_post(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"title": "My First Updated Post", "body": "Welcome to my blog."}

    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.put("/post/1", json=body)

    post = resp.json()

    assert resp.status_code == 200
    assert post.get("title") == "My First Updated Post"
    assert post.get("id") == 1
    assert post.get("date_modified") is not None

    # fail case - post belongs to another user
    body = {"title": "My First Updated Post", "body": "Welcome to my blog."}

    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.put("/post/2", json=body)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This post belongs to another user"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_delete_post(db_non_commit):
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/post/1")

    assert resp.status_code == 204
    assert resp.json() == {"detail": "success"}

    # fail case - post belongs to another user
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/post/2")

    assert resp.status_code == 401
    assert resp.json() == {"detail": "This post belongs to another user"}

    # fail case - post does not exist
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/post/999")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "This post does not exist"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_get_post():
    # successful case
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/post/1")

    post = resp.json()

    assert resp.status_code == 200
    assert post.get("title") == "zaktest's post #1"
    assert post.get("body") == "This is a post of mock data. Post #1"

    # failure case - post does not exist
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/post/21")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "This post does not exist"}


@pytest.mark.asyncio
async def test_create_reply():
    # successful test case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    body = {"body": "My First Reply"}

    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/post/1/reply", json=body)

    reply = resp.json()

    assert resp.status_code == 201
    assert reply.get("body") == "My First Reply"
    assert reply.get("id") == 81

    # delete created reply to maintain database state
    async with create_async_session() as session:
        query = select(Reply).filter(Reply.id == reply.get("id"))
        result = await session.execute(query)

    created_reply = result.scalar_one_or_none()

    async with create_async_session() as session:
        await session.delete(created_reply)
        await session.commit()

        # verify created_reply deleted successfully
        query = select(Reply).filter(Reply.id == reply.get("id"))
        result = await session.execute(query)

        created_reply = result.scalar_one_or_none()

        assert created_reply is None

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_get_replies():
    # successful case - id:1, skip:1, limit:3, sort:new first
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/post/1/replies?skip=1&limit=3&sort-newest-first=true")

    replies = resp.json()

    assert resp.status_code == 200
    assert replies[0].get("body") == "This is a reply of mock data. Reply #1"
    assert replies[0].get("username") == "theotest"
    assert replies[2].get("username") == "zaktest"

    # successful case - id:3, skip:0, limit:4, sort:old first
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/post/3/replies?skip=0&limit=4&sort-newest-first=false")

    replies = resp.json()

    assert resp.status_code == 200
    assert replies[0].get("body") == "This is a reply of mock data. Reply #3"
    assert replies[0].get("username") == "zaktest"
    assert replies[3].get("username") == "elliottest"


@pytest.mark.asyncio
async def test_get_recent_posts():
    # successful case - skip: 0, limit:5
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/posts/recent?skip=0&limit=5")
    recent_posts = resp.json()

    assert resp.status_code == 200
    assert recent_posts[0].get("title") == "elliottest's post #5"
    assert recent_posts[4].get("title") == "elliottest's post #4"

    # failure case - skip: 0, limit:100
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/posts/recent?skip=0&limit=100")
    resp_dict = resp.json()

    assert resp.status_code == 422
    assert (
        resp_dict["detail"][0].get("msg")
        == "ensure this value is less than or equal to 25"
    )
