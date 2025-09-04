# app/api/deps.py
from typing import Generator
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import jwt
from fastapi.security import OAuth2PasswordBearer

# Pick any one of your login endpoints as the tokenUrl.
# It only affects the Swagger "Get token" UI link, not your runtime behavior.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

COOKIE_NAME = "aurexus_access"

# -------- DB dependency --------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Auth helpers --------
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials if credentials else extract_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        role = payload.get("role")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


# -------- RBAC helpers --------
def require_roles(*allowed: str):
    allowed = {r.lower() for r in allowed}
    def checker(current_user: User = Depends(get_current_user)) -> User:
        role = (current_user.role or "").lower()
        if role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Requires role in {sorted(allowed)}")
        return current_user
    return checker

require_admin     = require_roles("admin")
require_developer = require_roles("developer")
require_investor  = require_roles("investor")
