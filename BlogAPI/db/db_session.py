from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# todo - change conn string to production not testing
# Production db
# SQLALCHEMY_DATABASE_URL = (
#     r"sqlite:///C:\Users\Zak\PycharmProjects\BlogAPI\BlogAPI\db\blog.db"
# )

# This points the api/test client to test.db instead of blog.db
SQLALCHEMY_DATABASE_URL = (
    r"sqlite:///C:\Users\Zak\PycharmProjects\BlogAPI\BlogAPI\tests\test.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
