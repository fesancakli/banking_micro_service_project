from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.api.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return {
        "id": int(payload["sub"]),
        "role": payload.get("role", "user").lower()  # 👈 normalize
    }
