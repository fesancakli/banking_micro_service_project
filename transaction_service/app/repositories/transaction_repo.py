from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Transaction


async def create_transaction(db: AsyncSession, transaction: Transaction):
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def get_transactions(db: AsyncSession):
    result = await db.execute(select(Transaction))
    return result.scalars().all()
