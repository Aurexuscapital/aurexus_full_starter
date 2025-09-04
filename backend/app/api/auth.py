# app/api/auth.py
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import Token, UserRegister, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

# --- password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --- JWT helpers ---
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_minutes: int = 60) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


# --- DB helpers ---
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# ---------------------------
# Registration (kept generic)
# ---------------------------
@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new user with role: 'admin' | 'developer' | 'investor'
    """
    if payload.role not in {"admin", "developer", "investor"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------
# Role-specific logins
# ---------------------------
@router.post("/admin-login", response_model=Token)
def login_admin(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Admins sign in here.
    """
    user = authenticate_user(db, form.username, form.password)
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials"
        )
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/developer-login", response_model=Token)
def login_developer(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Property developers sign in here.
    """
    user = authenticate_user(db, form.username, form.password)
    if not user or user.role != "developer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid developer credentials",
        )
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/investor-login", response_model=Token)
def login_investor(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Investors sign in here.
    """
    user = authenticate_user(db, form.username, form.password)
    if not user or user.role != "investor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid investor credentials",
        )
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
def login_any(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Generic login for Swagger Authorize popup.
    Accepts any valid user and returns a token embedding their role.
    RBAC is still enforced by your route dependencies.
    """
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
