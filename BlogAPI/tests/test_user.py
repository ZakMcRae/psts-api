from fastapi.testclient import TestClient

from BlogAPI.main import api

client = TestClient(api)


def test_get_test():
    resp = client.get("/test")

    print(resp.status_code)
    print(resp.json())

    assert resp.status_code == 200
    assert resp.json() == "test1"


def test_get_user():
    resp = client.get("/user/<user_id>?user_id=1")

    assert resp.status_code == 200
    assert resp.json() == {
        "username": "testuser",
        "email": "testuser@example.com",
        "id": 1,
    }
