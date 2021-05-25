from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from BlogAPI.config import config_settings


def create_async_session() -> AsyncSession:
    # This points the api/test client to test.db instead of blog.db
    SQLALCHEMY_DATABASE_URL = fr"sqlite+aiosqlite:///{config_settings.db_path}"

    async_engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    session: AsyncSession = AsyncSession(async_engine)
    session.sync_session.expire_on_commit = False

    return session
