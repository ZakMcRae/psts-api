from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BlogAPI.config import config_settings

# this non async db session is used for creating initial tables
# see db_session_async for async engine/session code that is used by the api
SQLALCHEMY_DATABASE_URL = fr"sqlite:///{config_settings.db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
