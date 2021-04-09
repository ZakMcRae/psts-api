import fastapi
import uvicorn

from BlogAPI.db import db_session
from BlogAPI.routers import routes, user

api = fastapi.FastAPI()


def configure():
    configure_db()
    configure_routing()


def configure_db():
    db_session.global_init()


def configure_routing():
    api.include_router(routes.router)
    api.include_router(user.router)


if __name__ == "__main__":
    configure()
    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
else:
    configure()
