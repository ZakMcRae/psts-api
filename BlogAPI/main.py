import fastapi
import uvicorn

from BlogAPI.db import db_session
from BlogAPI.routers import temp_routes, user_routes, post_routes, reply_routes

api = fastapi.FastAPI()


def configure():
    configure_db()
    configure_routing()


def configure_db():
    db_session.global_init()


def configure_routing():
    api.include_router(temp_routes.router, tags=["Temp"])
    api.include_router(user_routes.router, tags=["User"])
    api.include_router(post_routes.router, tags=["Post"])
    api.include_router(reply_routes.router, tags=["Reply"])


if __name__ == "__main__":
    configure()
    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
else:
    configure()
