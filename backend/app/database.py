# backend/app/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL")

# 👉 Ne PAS convertir vers asyncpg : psycopg supporte l’async avec SQLAlchemy 2.x
DATABASE_URL_ASYNC = DATABASE_URL  # attendu: "postgresql+psycopg://..."

engine = create_async_engine(DATABASE_URL_ASYNC, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
