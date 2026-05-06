from fastapi import APIRouter, Depends
from sqlalchemy.orm import selectinload
from sqlmodel import select
from dependencies.user import get_current_user
from models.user_model import User
from schema.user_schema import UserPublic
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session


user_router = APIRouter()


@user_router.get("/me", response_model=UserPublic)
async def get_user(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)
):
    # 1. Fetch user with relations
    statement = (
        select(User).where(User.id == user.id).options(selectinload(User.payments))
    )
    result = await db.exec(statement)
    user_with_relations = result.first()

    # 2. Return the OBJECT directly, not {"user": user_with_relations}
    return user_with_relations
