# app/db/base.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Async engine (Postgres RDS bağlantısı .env'den gelir)
engine = create_async_engine(settings.database_url, echo=True, future=True)

# Session factory
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Base class (tüm modeller bunun üzerinden türeyecek)
Base = declarative_base()


# Dependency (FastAPI için DB session)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
