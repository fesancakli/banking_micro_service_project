import asyncio

from app.api.v1 import accounts
from app.db.base import engine
from app.db.models import Base
from app.metrics import setup_metrics
from app.services.rabbit_consumer import start_consumer  # buraya import ettik
from fastapi import FastAPI

app = FastAPI(title="Account Service")
setup_metrics(app)

@app.on_event("startup")
async def on_startup():
    # DB tabloları
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Rabbit consumer'ı arka planda çalıştır
    asyncio.create_task(start_consumer())


app.include_router(accounts.router)
