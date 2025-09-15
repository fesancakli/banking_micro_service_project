from pydantic import BaseModel, EmailStr, Field
from app.domain.entities import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str | None = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
