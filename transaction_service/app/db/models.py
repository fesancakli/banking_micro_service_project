from sqlalchemy import Column, Integer, Numeric, String, DateTime, func
from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False)  # paranın çıktığı / işlendiği hesap
    target_account_id = Column(Integer, nullable=True)  # sadece transfer için dolu olur
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(String(20), nullable=False)  # deposit, withdraw, transfer
    status = Column(String(20), default="pending")  # pending, success, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
