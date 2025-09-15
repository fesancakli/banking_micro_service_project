import aio_pika
import asyncio
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.repositories.account_repo import AccountRepository
import httpx
from decimal import Decimal
from app.api.core.config import settings

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        transaction_id = data["transaction_id"]
        account_id = data["account_id"]
        target_account_id = data.get("target_account_id")
        amount = Decimal(str(data["amount"]))
        tx_type = data["type"]

        logging.info(f"📩 Yeni transaction alındı: {data}")

        async for db in get_db():
            try:
                # Hesap var mı kontrol et
                account = await AccountRepository.get_account_by_id(db, account_id)
                if not account:
                    raise ValueError("Account not found")

                if tx_type == "deposit":
                    account.balance += amount
                    await AccountRepository.update_balance(db, account)
                    logging.info(f"💰 Deposit: {amount} eklendi -> Account {account.id}")

                elif tx_type == "withdraw":
                    if account.balance < amount:
                        raise ValueError("Insufficient funds")
                    account.balance -= amount
                    await AccountRepository.update_balance(db, account)
                    logging.info(f"🏧 Withdraw: {amount} düşüldü -> Account {account.id}")

                elif tx_type == "transfer":
                    if account.balance < amount:
                        raise ValueError("Insufficient funds")
                    target = await AccountRepository.get_account_by_id(db, target_account_id)
                    if not target:
                        raise ValueError("Target account not found")

                    # Para aktarımı
                    account.balance -= amount
                    target.balance += amount
                    await AccountRepository.update_balance(db, account)
                    await AccountRepository.update_balance(db, target)
                    logging.info(
                        f"🔄 Transfer: {amount} aktarıldı -> {account.id} → {target.id}"
                    )

                # Başarılı → Transaction Service'e bildir
                await notify_transaction_service(transaction_id, "success")
                logging.info(f"✅ Transaction {transaction_id} success olarak bildirildi")

            except Exception as e:
                # Hata → Transaction Service'e failed bildir
                logging.error(f"❌ Transaction {transaction_id} hata: {str(e)}")
                await notify_transaction_service(transaction_id, "failed", str(e))


async def notify_transaction_service(transaction_id: int, status: str, error: str = None):
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{settings.TRANSACTION_SERVICE_URL}/{transaction_id}/status",
            json={"status": status, "error": error},
        )


async def start_consumer():
    while True:
        try:
            logging.info("🔌 RabbitMQ'ya bağlanmaya çalışılıyor...")
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            async with connection:
                channel = await connection.channel()

                exchange = await channel.declare_exchange(
                    "transaction_exchange", aio_pika.ExchangeType.TOPIC, durable=True
                )

                # Kuyruklar
                deposit_queue = await channel.declare_queue("deposit_queue", durable=True)
                await deposit_queue.bind(exchange, routing_key="transaction.deposit")

                withdraw_queue = await channel.declare_queue("withdraw_queue", durable=True)
                await withdraw_queue.bind(exchange, routing_key="transaction.withdraw")

                transfer_queue = await channel.declare_queue("transfer_queue", durable=True)
                await transfer_queue.bind(exchange, routing_key="transaction.transfer")

                # Hepsini ayrı ayrı dinle
                await deposit_queue.consume(process_message)
                await withdraw_queue.consume(process_message)
                await transfer_queue.consume(process_message)

                logging.info(" [*] Waiting for transaction messages...")
                await asyncio.Future()  # sonsuz dinleme
        except Exception as e:
            logging.error(f"⚠️ RabbitMQ bağlantı hatası: {e}, 5 saniye sonra tekrar denenecek...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(start_consumer())
