from fastapi import Depends, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone
from core.db import get_session
from models.session_model import Session
from models.user_model import User
from error import CookieMissing, InvalidSession, SessionExpired, UserNotFound


SESSION_COOKIE_NAMES = (
    "__Secure-better-auth.session_token",
    "better-auth.session_token",
)


def get_session_token(request: Request) -> str:
    for cookie_name in SESSION_COOKIE_NAMES:
        raw_cookie = request.cookies.get(cookie_name)
        if raw_cookie:
            return raw_cookie.split(".")[0]

    raise CookieMissing()


async def get_current_user(request: Request, db: AsyncSession = Depends(get_session)):
    session_token = get_session_token(request)

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
