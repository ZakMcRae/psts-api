import json

from fastapi.testclient import TestClient

from BlogAPI.main import api

client = TestClient(api)


# def test_get_user():
#     resp = client.get("/user/<user_id>?user_id=1")
#     x = json.loads(resp.content)
#     assert x == {"username": "zak", "email": "z@z.com", "id": 1}
#     # assert resp.status_code == 200


def test_letters():
    resp = client.get("/h/<letters>?letters=abcd")
    assert resp.status_code == 200
    assert resp.json() == {"a": 0, "b": 1, "c": 2, "d": 3}


# def test_token():
#     body = {"username": "zak", "password": "123"}
#     resp = client.post("http://127.0.0.1:8000/token", body)
#     assert resp.status_code == 200
#     assert resp.json() ==
# todo how to test for token - ie random output
