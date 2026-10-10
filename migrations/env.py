from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import create_engine

from redteam.core.config import get_settings
from redteam.models import attack as _attack  # noqa: F401
from redteam.models import attack_result as _attack_result  # noqa: F401
from redteam.models import target as _target  # noqa: F401
from redteam.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata



def get_database_url() -> str:
    import os

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



def run_migrations_offline() -> None:
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
