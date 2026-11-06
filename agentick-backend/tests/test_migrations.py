"""The migrations alone must build the schema the models describe (a hand-edited one did not)."""

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import settings
from app.db.base import Base

SCRATCH = "migration_check"


def test_migrations_build_the_schema_of_the_models(monkeypatch):
    admin = create_engine(settings.database_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH}"))
        conn.execute(text(f"CREATE DATABASE {SCRATCH}"))
    url = (
        make_url(settings.database_url).set(database=SCRATCH).render_as_string(hide_password=False)
    )
    monkeypatch.setattr(settings, "database_url", url)
    try:
        command.upgrade(Config("alembic.ini"), "head")
        engine = create_engine(url)
        with engine.connect() as conn:
            diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
        engine.dispose()
        assert diff == []
    finally:
        with admin.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH} WITH (FORCE)"))
