from pydantic import BaseModel
from decimal import Decimal
from app.domain.entities import Currency, AccountStatus


class AccountCreateRequest(BaseModel):
    currency: Currency  # artık user_id istemiyor


class AccountResponse(BaseModel):
    id: int
    user_id: int
    currency: Currency
    balance: Decimal
    status: AccountStatus

    class Config:
        from_attributes = True


class AccountAdminResponse(BaseModel):
    id: int
    user_id: int
    currency: Currency
    status: AccountStatus

    class Config:
        from_attributes = True
