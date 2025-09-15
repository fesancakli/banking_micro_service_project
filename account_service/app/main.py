from fastapi import FastAPI
from app.api.v1 import accounts
from app.db.models import Base
from app.db.base import engine

app = FastAPI(title="Account Service")


# Tablo oluşturmak için async context kullanmalısın
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(accounts.router)
