from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Transaction
from app.services.schemas import TransactionCreate
from app.repositories import transaction_repo

from app.db.models import Transaction
from app.services.schemas import TransactionCreate
from app.repositories import transaction_repo
from app.services.rabbitmq_producer import publish_transaction_event


async def create_transaction_service(db, transaction_data: TransactionCreate):
    """
    Yeni bir transaction oluşturur ve RabbitMQ'ya event yollar.
    """
    new_tx = Transaction(
        account_id=transaction_data.account_id,
        target_account_id=transaction_data.target_account_id,
        amount=transaction_data.amount,
        type=transaction_data.type,
        status="pending"
    )

    saved_tx = await transaction_repo.create_transaction(db, new_tx)

    # RabbitMQ event publish
    event_message = {
        "transaction_id": saved_tx.id,
        "account_id": saved_tx.account_id,
        "target_account_id": saved_tx.target_account_id,
        "amount": str(saved_tx.amount),
        "type": str(saved_tx.type),
    }
    await publish_transaction_event(
        event_message,
        routing_key=f"transaction.{event_message['type']}"
    )

    return saved_tx


async def get_transactions_service(db: AsyncSession):
    """
    Tüm transaction'ları getirir.
    """
    return await transaction_repo.get_transactions(db)


async def get_transaction_by_id_service(db: AsyncSession, transaction_id: int):
    """
    ID'ye göre tek bir transaction getirir.
    """
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    return result.scalars().first()
