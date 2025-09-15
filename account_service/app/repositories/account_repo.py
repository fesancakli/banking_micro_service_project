from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import AccountModel


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, account: AccountModel) -> AccountModel:
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def get_by_user_id(self, user_id: int) -> list[AccountModel]:
        result = await self.db.execute(
            select(AccountModel).where(AccountModel.user_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_account_by_id(db: AsyncSession, account_id: int):
        result = await db.execute(select(AccountModel).where(AccountModel.id == account_id))
        return result.scalars().first()

    @staticmethod
    async def update_balance(db: AsyncSession, account: AccountModel):
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account
