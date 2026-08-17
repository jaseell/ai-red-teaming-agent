from sqlalchemy import create_engine

from redteam.core.config import get_settings


def build_database_url() -> str:
    settings = get_settings()

    return (
        f"postgresql+psycopg://"
        f"{settings.postgres_user}:"
        f"{settings.postgres_password}@"
        f"{settings.postgres_host}:"
        f"{settings.postgres_port}/"
        f"{settings.postgres_db}"
    )


engine = create_engine(
    build_database_url(),
    pool_pre_ping=True,
)
