from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.account_repo import AccountRepository
from app.db.models import AccountModel
from app.domain.entities import AccountStatus, Currency
from app.services.schemas import AccountResponse
from app.services.schemas import AccountAdminResponse


async def create_account(user_id: int, currency: Currency, db: AsyncSession) -> AccountResponse:
    repo = AccountRepository(db)

    account = AccountModel(
        user_id=user_id,
        currency=currency,
        balance=Decimal("0.00"),
        status=AccountStatus.ACTIVE,
    )

    saved = await repo.add(account)

    # Pydantic v2 uyumlu dönüş
    return AccountResponse.model_validate(saved, from_attributes=True)


async def list_accounts(user_id: int, db: AsyncSession) -> list[AccountResponse]:
    repo = AccountRepository(db)
    accounts = await repo.get_by_user_id(user_id)
    return [AccountResponse.model_validate(acc, from_attributes=True) for acc in accounts]


async def list_accounts_by_user(user_id: int, db: AsyncSession) -> list[AccountAdminResponse]:
    repo = AccountRepository(db)
    accounts = await repo.get_by_user_id(user_id)
    return [AccountAdminResponse.model_validate(acc, from_attributes=True) for acc in accounts]
