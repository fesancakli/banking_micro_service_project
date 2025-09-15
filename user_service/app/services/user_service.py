from http.client import HTTPException
from app.db.models import User
from app.repositories.user_repo import UserRepo
from app.core.security import hash_password
from app.domain.errors import EmailAlreadyExists, UserNotFound, InvalidCredentials
from app.core.security import verify_password
from sqlalchemy import select
from fastapi import status


class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def signup(self, db, *, email: str, password: str, full_name: str | None):
        if await self.repo.by_email(db, email):
            raise EmailAlreadyExists()
        hashed = hash_password(password)
        return await self.repo.create(db, email=email, hashed_password=hashed, full_name=full_name)

    async def login(self, db, *, email: str, password: str):
        user = await self.repo.by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        return user

        ...

    async def update_profile(self, db, *, user_id: int, full_name: str | None, email: str | None):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound()

        # Email değiştiriliyorsa kontrol et
        if email and email != user.email:
            existing = await db.execute(select(User).where(User.email == email))
            if existing.scalar_one_or_none():
                raise EmailAlreadyExists()
            user.email = email

        if full_name:
            user.full_name = full_name.strip()

        await db.commit()
        await db.refresh(user)
        return user

    async def change_password(self, db, *, user_id: int, old_password: str, new_password: str):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound()

        # Eski şifre doğru mu?
        if not verify_password(old_password, user.hashed_password):
            raise InvalidCredentials()

        # Yeni şifreyi hashle
        user.hashed_password = hash_password(new_password)

        await db.commit()
        await db.refresh(user)
        return user

    async def deactivate_account(self, db, *, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound()

        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return user

    async def activate_account(self, db, *, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound()

        user.is_active = True
        await db.commit()
        await db.refresh(user)
        return user
