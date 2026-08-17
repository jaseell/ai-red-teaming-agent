from sqlalchemy import text

from redteam.core.session import SessionLocal


def test_database_session():
    with SessionLocal() as session:
        result = session.execute(text("SELECT 1")).scalar_one()

    assert result == 1
