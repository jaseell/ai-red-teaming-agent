import pytest
from sqlalchemy import event

from redteam.core.database import engine
from redteam.core.session import SessionLocal


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = SessionLocal(bind=connection)

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
