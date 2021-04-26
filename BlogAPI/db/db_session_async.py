from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# todo - change conn string to production not testing
# Production db
# SQLALCHEMY_DATABASE_URL = (
#     r"sqlite:///C:\Users\Zak\PycharmProjects\BlogAPI\BlogAPI\db\blog.db"
# )


def create_async_session() -> AsyncSession:
    # This points the api/test client to test.db instead of blog.db
    SQLALCHEMY_DATABASE_URL = r"sqlite+aiosqlite:///C:\Users\Zak\PycharmProjects\BlogAPI\BlogAPI\tests\test.db"

    async_engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    session: AsyncSession = AsyncSession(async_engine)
    session.sync_session.expire_on_commit = False

    return session
