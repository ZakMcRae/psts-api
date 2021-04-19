import fastapi
from fastapi.openapi.utils import get_openapi
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


def custom_openapi():
    if api.openapi_schema:
        return api.openapi_schema
    openapi_schema = get_openapi(
        title="BlogAPI",
        version="0.1",
        description="## A Practice API - Backend endpoints for a blog\n Made by: [ZakMcRae - GitHub](https://github.com/ZakMcRae)",
        routes=api.routes,
    )
    api.openapi_schema = openapi_schema
    return api.openapi_schema


api.openapi = custom_openapi

if __name__ == "__main__":
    configure()
    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
else:
    configure()
