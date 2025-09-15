from fastapi import FastAPI
from app.api.v1.users import router as user_router
from app.db.base import Base, engine

app = FastAPI(title="User Service")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(user_router)
