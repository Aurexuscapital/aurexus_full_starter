from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_roles, require_developer
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

# Anyone logged in (admin, investor, or developer)
@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(require_roles("admin", "investor", "developer"))):
    return current_user

# Developer-only route
@router.get("/dev-dashboard")
def dev_dashboard(current_user: User = Depends(require_developer)):
    return {"msg": f"hello developer {current_user.email}"}
