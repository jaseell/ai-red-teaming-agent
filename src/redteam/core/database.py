
import os

from sqlalchemy import create_engine

from redteam.core.config import get_settings


def build_database_url() -> str:
    settings = get_settings()

    database_name = settings.postgres_db

    if os.getenv("APP_ENV") == "test":
        database_name = settings.test_postgres_db or "redteam_test"

    return (
        f"postgresql+psycopg://"
        f"{settings.postgres_user}:"
        f"{settings.postgres_password}@"
        f"{settings.postgres_host}:"
        f"{settings.postgres_port}/"
        f"{database_name}"
    )


engine = create_engine(
    build_database_url(),
    pool_pre_ping=True,
)
