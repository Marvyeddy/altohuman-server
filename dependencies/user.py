from fastapi import Depends, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone
from core.db import get_session
from models.session_model import Session
from models.user_model import User
from error import CookieMissing, InvalidSession, SessionExpired, UserNotFound


async def get_current_user(request: Request, db: AsyncSession = Depends(get_session)):
    raw_cookie = request.cookies.get("better-auth.session_token")
    if not raw_cookie:
        raise CookieMissing()

    session_token = raw_cookie.split(".")[0]

    statement = select(Session).where(Session.token == session_token)
    result = await db.exec(statement)
    db_session = result.first()

    if not db_session:
        raise InvalidSession()

    if db_session.expiresAt.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise SessionExpired()

    # 4. Get the associated user
    user_stmt = select(User).where(User.id == db_session.userId)
    user_result = await db.exec(user_stmt)
    user = user_result.first()

    if not user:
        raise UserNotFound()

    return user
