import fastapi
import uvicorn
from fastapi import Depends
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session

from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.db.db_session import Base, engine
from BlogAPI.dependencies.dependencies import get_db

api = fastapi.FastAPI()


# todo - delete this test route
@api.get("/get_user_test")
def get_user_test(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).get(user_id)


def configure():
    configure_routing()


def configure_routing():
    # api.include_router(temp_routes.router, tags=["Temp"])
    # api.include_router(user_routes.router, tags=["User"])
    # api.include_router(post_routes.router, tags=["Post"])
    # api.include_router(reply_routes.router, tags=["Reply"])
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
