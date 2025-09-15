from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User


class UserRepo:
    async def by_email(self, db: AsyncSession, email: str) -> User | None:
        res = await db.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, email: str, hashed_password: str, full_name: str | None) -> User:
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
