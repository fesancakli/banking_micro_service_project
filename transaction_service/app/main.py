from fastapi import FastAPI
from app.api.v1 import transaction_routes
from app.db.base import Base, engine


# DB tablolarını oluştur (dev/test için)
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title="Transaction Service")

app.include_router(transaction_routes.router)


@app.on_event("startup")
async def on_startup():
    await init_models()
