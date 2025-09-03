from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.engines_routes import router as engines_router

# Create one global router
api_router = APIRouter()

# Include each module's router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(engines_router, prefix="/engines", tags=["engines"])

# Mount auth under /auth so tokenUrl /auth/login is valid
api_router.include_router(auth_router, prefix="/auth")

api_router.include_router(users_router)

@api_router.get("/ping")
async def ping():
    return {"pong": True}
