from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.api.core.config import settings

engine = create_async_engine(settings.database_url, echo=True, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session
