from fastapi import APIRouter

from BlogAPI.util.mock_data import (
    add_sample_users,
    add_sample_posts,
    add_sample_replies,
    add_sample_follows,
)

router = APIRouter()


# todo - delete - temp route for testing/dev


@router.get("/add-db-info")
def add_db_info():
    add_sample_users()
    add_sample_posts()
    add_sample_replies()
    add_sample_follows()
    return "Complete"


#
#
# @router.get("/test")
# def test():
#     user = validate_new_user("jes", "z@z.co")
#     return user


@router.get("/add_posts")
def add_posts():
    for i in range(10):
        add_sample_posts()
    return "Success"


@router.get("/add_replies")
def add_replies():
    for i in range(10):
        add_sample_replies()
    return "Success"
