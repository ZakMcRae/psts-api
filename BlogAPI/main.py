import json

import fastapi
import uvicorn

from BlogAPI.routers import routes
from BlogAPI.db import db_session

api = fastapi.FastAPI()


def configure():
    configure_db()
    configure_routing()
    configure_env_variables()


def configure_db():
    db_session.global_init()


def configure_routing():
    api.include_router(routes.router)


def configure_env_variables():
    with open("config.json") as fin:
        config_info = json.load(fin)

    routes.secret_key = config_info.get("secret_key")


if __name__ == "__main__":
    configure()
    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
else:
    configure()
