from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class TransactionBase(BaseModel):
    account_id: int = Field(..., description="Paranın işlendiği/çıktığı hesap ID")
    amount: float = Field(..., gt=0, description="İşlem tutarı (pozitif olmalı)")
    type: str = Field(..., description="İşlem tipi: deposit, withdraw, transfer")
    target_account_id: Optional[int] = Field(None, description="Transferlerde alıcı hesap ID")

    @validator("target_account_id", always=True)
    def validate_transfer(cls, v, values):
        """
        transfer işleminde target_account_id zorunlu olmalı,
        diğer tiplerde boş olmalı
        """
        tx_type = values.get("type")
        if tx_type == "transfer" and v is None:
            raise ValueError("Transfer işlemleri için target_account_id zorunludur.")
        if tx_type in ["deposit", "withdraw"] and v is not None:
            raise ValueError("Deposit/Withdraw işlemlerinde target_account_id kullanılmaz.")
        return v


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
