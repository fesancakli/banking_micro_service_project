from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.base import get_db
from app.services import transaction_services
from app.services.schemas import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])
ACCOUNT_SERVICE_URL = "http://localhost:8001/accounts"
import logging

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services import transaction_services
from app.services.schemas import TransactionCreate, TransactionResponse
from app.api.v1.deps import get_current_user
import httpx
from app.api.core.config import settings

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
        transaction: TransactionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """
    Yeni bir transaction oluşturur.
    - Deposit: sadece account_id
    - Withdraw: sadece account_id
    - Transfer: account_id + target_account_id
    """

    # 👉 Account Service’ten doğrulama
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.ACCOUNT_SERVICE_URL}/{transaction.account_id}")
        if resp.status_code != 200:
            logger.warning(
                f"❌ Transaction attempt to non-existent account_id={transaction.account_id} by user_id={current_user['id']}")
            raise HTTPException(status_code=404, detail="Account not found")

        account_data = resp.json()
        if account_data["user_id"] != current_user["id"]:
            logger.warning(
                f"⚠️ Unauthorized access: user_id={current_user['id']} tried to use account_id={transaction.account_id} (belongs to user_id={account_data['user_id']}){current_user}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your account"
            )

    # ✅ Transaction yarat
    try:
        return await transaction_services.create_transaction_service(db, transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[TransactionResponse])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    """
    Tüm transaction’ları listeler
    """
    return await transaction_services.get_transactions_service(db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """
    Belirli bir transaction’ı ID’sine göre getirir
    """
    tx = await transaction_services.get_transaction_by_id_service(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.patch("/{transaction_id}/status")
async def update_transaction_status(
        transaction_id: int,
        status_update: dict,
        db: AsyncSession = Depends(get_db)
):
    """
    Transaction status günceller.
    Account Service, işlemi işledikten sonra burayı çağırır.
    """
    tx = await transaction_services.get_transaction_by_id_service(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.status = status_update["status"]
    await db.commit()
    await db.refresh(tx)

    return {"transaction_id": tx.id, "status": tx.status}
