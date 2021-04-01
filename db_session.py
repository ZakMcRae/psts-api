from typing import Callable, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

from models import SQLAlchemyBase

__factory: Optional[Callable[[], Session]] = None


def global_init():
    global __factory

    if __factory:
        return

    conn_str = "sqlite:///site.db"

    # Adding check_same_thread = False. This can be an issue about
    # creating / owner thread when cleaning up sessions, etc. This is a sqlite restriction
    engine = sa.create_engine(
        conn_str, echo=False, connect_args={"check_same_thread": False}
    )
    __factory = orm.sessionmaker(bind=engine)

    # noinspection PyUnresolvedReferences
    from models import User

    SQLAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory

    if not __factory:
        raise Exception("You must call global_init() before using this method.")

    session: Session = __factory()
    session.expire_on_commit = False

    return session
