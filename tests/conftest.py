import pytest

from redteam.core.database import engine
from redteam.core.session import SessionLocal


@pytest.fixture
def db_session():
    connection = engine.connect()
    outer_transaction = connection.begin()

    session = SessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()

        if outer_transaction.is_active:
            outer_transaction.rollback()

        connection.close()
