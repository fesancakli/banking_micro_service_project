from sqlalchemy import Column, Integer, String, Numeric, Enum as SqlEnum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from app.domain.entities import AccountStatus, Currency

Base = declarative_base()


class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    currency = Column(SqlEnum(Currency), nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, default=0.00)
    status = Column(SqlEnum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
