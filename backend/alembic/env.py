"""Alembic environment script — configura a conexão e detecta modelos automaticamente."""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Importa Base e todos os modelos para autogenerate ────────────────────────
from app.core.database import Base
from app.core.config import settings

# import dos modelos para o Alembic detectar automaticamente
from app.models import Submission  # noqa: F401

# ── Configuração do Alembic ───────────────────────────────────────────────────
config = context.config

# Interpreta o arquivo de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados dos modelos para autogenerate
target_metadata = Base.metadata

# Substitui a URL do alembic.ini pela variável de ambiente
config.set_main_option("sqlalchemy.url", settings.database_url)


# ── Modo offline (sem conexão real) ───────────────────────────────────────────
def run_migrations_offline() -> None:
    """Gera SQL sem conexão ao banco (útil para revisão e CI)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Modo online (conexão real, assíncrona) ────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Cria engine assíncrono e executa as migrações."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Ponto de entrada para migrações online."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
