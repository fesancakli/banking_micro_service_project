from datetime import datetime

from app.db.base import Base
from app.domain.entities import UserRole
from passlib.hash import bcrypt
from sqlalchemy import String, Integer, DateTime, func, Enum, event
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 📌 Tablo ilk kez CREATE edildiğinde admin ekle
@event.listens_for(User.__table__, "after_create")
def create_admin_user(target, connection, **kw):
    connection.execute(
        User.__table__.insert(),
        {
            "email": "admin@example.com",
            "full_name": "Admin User",
            "hashed_password": bcrypt.hash("admin123"),  # bcrypt hash
            "role": "ADMIN",
            "is_active": 1,
            "created_at": datetime.utcnow(),
        }
    )
