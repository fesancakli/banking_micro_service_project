from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.schemas import UserCreate, UserRead, UserUpdate
from app.repositories.user_repo import UserRepo
from app.services.user_service import UserService
from app.domain.errors import EmailAlreadyExists, UserNotFound
from app.schemas import UserLogin, Token
from app.core.security import create_access_token
from app.domain.errors import InvalidCredentials
from app.api.deps import get_current_user
from app.api.deps import require_role
from app.domain.entities import UserRole
from app.db.models import User

router = APIRouter(tags=["users"])
service = UserService(UserRepo())


@router.post("/auth/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await service.signup(db, email=payload.email, password=payload.password, full_name=payload.full_name)
        return user
    except EmailAlreadyExists:
        raise HTTPException(status_code=409, detail="Email already exists")


@router.post("/auth/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        user = await service.login(db, email=payload.email, password=payload.password)
        token = create_access_token(user_id=user.id, role=user.role.value)
        return {"access_token": token, "token_type": "bearer"}
    except InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


@router.get("/users/me", response_model=UserRead)
async def read_current_user(current_user=Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserRead])
async def list_users(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(require_role([UserRole.ADMIN]))
):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(require_role([UserRole.ADMIN]))
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/me", response_model=UserRead)
async def update_my_profile(
        payload: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    try:
        return await service.update_profile(
            db,
            user_id=current_user.id,
            full_name=payload.full_name,
            email=payload.email
        )
    except EmailAlreadyExists:
        raise HTTPException(status_code=409, detail="Email already exists")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")


from app.schemas import PasswordChange
from app.domain.errors import InvalidCredentials


@router.patch("/auth/change-password")
async def change_password(
        payload: PasswordChange,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    try:
        await service.change_password(
            db,
            user_id=current_user.id,
            old_password=payload.old_password,
            new_password=payload.new_password
        )
        return {"detail": "Password updated successfully"}
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Old password is incorrect")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/users/me")
async def deactivate_my_account(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    try:
        await service.deactivate_account(db, user_id=current_user.id)
        return {"detail": "Account deactivated successfully"}
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")


from app.api.deps import require_role
from app.domain.entities import UserRole


@router.patch("/users/{user_id}/activate")
async def activate_user_account(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(require_role([UserRole.ADMIN]))
):
    try:
        await service.activate_account(db, user_id=user_id)
        return {"detail": "Account activated successfully"}
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
