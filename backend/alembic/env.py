# backend/alembic/env.py
from __future__ import annotations
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Importez votre Base SQLAlchemy
from app.models.alarm import Base

# --- Config globale Alembic ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# URL de base : depuis l'ENV ou fallback alembic.ini
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # ⚠️ IMPORTANT : échapper % pour configparser
    db_url_escaped = DATABASE_URL.replace('%', '%%')
    config.set_main_option("sqlalchemy.url", db_url_escaped)

def run_migrations_offline():
    """Exécution offline (génère le SQL sans se connecter)."""
    url = DATABASE_URL or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """
    IMPORTANT : tout le cycle de migration DOIT être exécuté ici,
    via un handle de connexion SYNC fourni par run_sync().
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Exécution online (connexion DB, mode async sous le capot)."""
    url = DATABASE_URL or config.get_main_option("sqlalchemy.url")

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
    )

    async def run():
        async with connectable.connect() as async_conn:
            # ⚠️ TOUT se passe dans do_run_migrations via un handle sync
            await async_conn.run_sync(do_run_migrations)

    asyncio.run(run())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
