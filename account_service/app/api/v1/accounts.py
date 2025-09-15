from fastapi import HTTPException, status

from app.repositories.account_repo import AccountRepository
from app.services.schemas import AccountAdminResponse
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.account_services import create_account

from app.api.v1.deps import get_current_user
from app.services.account_services import list_accounts, list_accounts_by_user
from app.services.schemas import AccountResponse, AccountCreateRequest, AccountAdminResponse

# 👇 prefix ekle
router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse)
async def create_account_endpoint(
        request: AccountCreateRequest,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    print("👉 current_user:", current_user)
    response = await create_account(current_user["id"], request.currency, db)
    print("👉 response:", response)
    return response


@router.get("/", response_model=list[AccountResponse])
async def list_accounts_endpoint(
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    return await list_accounts(current_user["id"], db)


@router.get("/user/{user_id}", response_model=list[AccountAdminResponse])
async def list_accounts_by_user_endpoint(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return await list_accounts_by_user(user_id, db)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """
    ID ile tek bir hesabı döndürür.
    """
    account = await AccountRepository.get_account_by_id(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
