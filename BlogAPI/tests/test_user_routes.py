import json

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from BlogAPI.db.SQLAlchemy_models import user_follow
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.dependencies.dependencies import get_current_user
from BlogAPI.main import api

# noinspection PyUnresolvedReferences
# db_non_commit pytest fixture used below - shows unused in editor
from BlogAPI.tests.test_setup_and_utils import (
    db_non_commit,
    override_get_current_user_zak,
    override_get_current_user_elliot,
)


@pytest.mark.asyncio
async def test_generate_token():
    # successful test case - valid username and email
    body = {
        "username": "zaktest",
        "password": 123,
    }
    header = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/token", data=body, headers=header)

    token_info = resp.json()

    assert resp.status_code == 200
    assert token_info.get("access_token") is not None
    assert token_info.get("token_type") == "bearer"

    # wrong username case
    body = {
        "username": "jim",
        "password": 123,
    }
    header = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/token", data=body, headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid Username or Password"}

    # wrong password case
    body = {
        "username": "zaktest",
        "password": "password",
    }
    header = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/token", data=body, headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid Username or Password"}


@pytest.mark.asyncio
async def test_get_user():
    # successful test case
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/1")

    assert resp.status_code == 200
    assert resp.json() == {
        "username": "zaktest",
        "email": "zaktest@example.com",
        "id": 1,
    }


@pytest.mark.asyncio
async def test_create_user(db_non_commit):
    # db_non_commit - allows testing without database changes

    # successful test case
    body = {"username": "zoetest", "email": "zoetest@example.com", "password": 123}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/user", data=json.dumps(body))
    user_info = resp.json()

    assert resp.status_code == 201
    assert user_info.get("username") == "zoetest"
    assert user_info.get("email") == "zoetest@example.com"

    # taken username case
    body = {"username": "zaktest", "email": "zoetest@example.com", "password": 123}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/user", data=json.dumps(body))

    assert resp.status_code == 409
    assert resp.json() == {"detail": "Username is taken, please try another"}

    # taken email case
    body = {"username": "zoetest", "email": "zaktest@example.com", "password": 123}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/user", data=json.dumps(body))

    assert resp.status_code == 409
    assert resp.json() == {"detail": "Email is taken, please try another"}


@pytest.mark.asyncio
async def test_get_me(monkeypatch):
    # fail case - invalid token
    header = {"Authorization": "Bearer a.fake.token"}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/me", headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid token"}

    # fail case - expired token
    # token stored outside of git in test_info.json
    with open(
        r"C:\Users\Zak\PycharmProjects\BlogAPI\BlogAPI\tests\test_info.json"
    ) as fin:
        test_info = json.load(fin)

    header = {"Authorization": f"Bearer {test_info.get('expired_test_token')}"}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/me", headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Token is expired"}

    # successful test case
    def mock_return_valid(*args, **kwargs):
        user_info = {"id": 1, "username": "zaktest", "exp": 1621605216}
        return user_info

    # simulates jwt.decode being called - returns mock output "user_info"
    monkeypatch.setattr(jwt, "decode", mock_return_valid)

    header = {"Authorization": "Bearer a.fake.token"}
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/me", headers=header)

    assert resp.status_code == 200
    assert resp.json() == {
        "username": "zaktest",
        "email": "zaktest@example.com",
        "id": 1,
    }


@pytest.mark.asyncio
async def test_get_users_posts():
    # successful case - id:1, skip:1, limit:3, sort:new first
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/1/posts?skip=1&limit=3&sort-newest-first=true")
    posts = resp.json()

    assert resp.status_code == 200
    assert posts[0].get("title") == "zaktest's post #4"
    assert posts[2].get("title") == "zaktest's post #2"

    # successful case - id:3, skip:0, limit:5, sort:old first
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/3/posts?skip=0&limit=5&sort-newest-first=false")
    posts = resp.json()

    assert resp.status_code == 200
    assert posts[0].get("title") == "theotest's post #1"
    assert posts[4].get("title") == "theotest's post #5"


@pytest.mark.asyncio
async def test_get_users_replies():
    # successful case - id:1, skip:1, limit:3, sort:new first
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/1/replies?skip=1&limit=3&sort-newest-first=true")
    replies = resp.json()

    assert resp.status_code == 200
    assert replies[0].get("body") == "This is a reply of mock data. Reply #19"
    assert replies[2].get("body") == "This is a reply of mock data. Reply #17"

    # successful case - id:3, skip:0, limit:5, sort:old first
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/3/replies?skip=0&limit=5&sort-newest-first=false")
    replies = resp.json()

    assert resp.status_code == 200
    assert replies[0].get("body") == "This is a reply of mock data. Reply #1"
    assert replies[4].get("body") == "This is a reply of mock data. Reply #5"


@pytest.mark.asyncio
async def test_follow_user(db_non_commit):
    # fail case - user already followed
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/user/follow/2")

    assert resp.status_code == 409
    assert resp.json() == {"detail": "User already followed"}

    # successful case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_elliot
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.post("/user/follow/3")

    assert resp.status_code == 201
    assert resp.json() == {"detail": "Success - User followed"}

    # delete dependency overwrite - don't want to conflict with other tests
    del api.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_unfollow_user():
    # successful case
    # mock authorization - return user directly
    api.dependency_overrides[get_current_user] = override_get_current_user_zak
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/user/follow/2")

    assert resp.status_code == 204
    assert resp.json() == {"detail": "Success - User unfollowed"}

    # fail case - user already not following after above unfollow
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.delete("/user/follow/2")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "This user is not currently being followed"}

    # reinsert row to maintain database state
    async with create_async_session() as session:
        stmt = user_follow.insert().values(user_id=2, following_id=1)
        await session.execute(stmt)
        await session.commit()

    # verify reinsert successful
    async with create_async_session() as session:
        query = select(user_follow.c.user_id).filter(user_follow.c.following_id == 1)
        result = await session.execute(query)

    following_ids = list(result.scalars())

    assert 2 in following_ids


@pytest.mark.asyncio
async def test_get_followers():
    # successful case - user with followers
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/1/followers")

    followers = resp.json()

    assert resp.status_code == 200
    assert followers[0].get("username") == "jesstest"
    assert followers[1].get("username") == "theotest"

    # successful case - user with no followers
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/4/followers")

    followers = resp.json()

    assert resp.status_code == 200
    assert len(followers) == 0


@pytest.mark.asyncio
async def test_get_following():
    # successful case - user a following
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/2/followers")

    following = resp.json()

    assert resp.status_code == 200
    assert following[0].get("username") == "zaktest"
    assert following[1].get("username") == "theotest"

    # successful case - user with no followers
    async with AsyncClient(app=api, base_url="http://127.0.0.1:8000") as ac:
        resp = await ac.get("/user/4/followers")

    following = resp.json()

    assert resp.status_code == 200
    assert len(following) == 0
