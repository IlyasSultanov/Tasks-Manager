"""Database session management with async support."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.config import settings


# Async engine for application use
async_engine = create_async_engine(
    settings.db_url.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    echo=settings.debug,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session for request lifecycle
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
