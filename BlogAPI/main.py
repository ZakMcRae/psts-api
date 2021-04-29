import fastapi
import uvicorn
from fastapi.openapi.utils import get_openapi

from BlogAPI.db.SQLAlchemy_models import Base
from BlogAPI.db.db_session import engine
from BlogAPI.routers import user_routes, post_routes, reply_routes

api = fastapi.FastAPI()
# todo - path parameters not working in urls ie /post/1 returns errors
# change <> to {}
# maybe use Path with aliases


def configure():
    configure_routing()


def configure_routing():
    api.include_router(user_routes.router, tags=["User"])
    api.include_router(post_routes.router, tags=["Post"])
    api.include_router(reply_routes.router, tags=["Reply"])
    pass


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
    Base.metadata.create_all(bind=engine)
    configure()
    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
else:
    configure()
