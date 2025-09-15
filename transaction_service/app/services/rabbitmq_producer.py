import json
import aio_pika
from app.api.core.config import settings


async def publish_transaction_event(message: dict, routing_key: str):
    """
    Transaction eventini RabbitMQ topic exchange'e gönderir.
    routing_key örnekleri: "transaction.deposit", "transaction.withdraw", "transaction.transfer"
    """
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        # Topic exchange tanımla
        exchange = await channel.declare_exchange(
            "transaction_exchange", aio_pika.ExchangeType.TOPIC, durable=True
        )

        await exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key,
        )
