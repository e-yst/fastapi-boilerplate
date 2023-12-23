from fastapi import APIRouter

from app.auth.api import router as auth_router

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(auth_router)
