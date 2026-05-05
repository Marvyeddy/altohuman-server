from fastapi import APIRouter, Depends
from dependencies.user import get_current_user
from models.user_model import User

user_router = APIRouter()


@user_router.get("/me")
async def get_user(user: User = Depends(get_current_user)):
    return {"user": user}
