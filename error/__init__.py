from typing import Any, Callable
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class AltohumanException(Exception):
    """The main error exception class"""

    pass


class CookieMissing(AltohumanException):
    """Cookie is missing"""

    pass


class InvalidSession(AltohumanException):
    """Session is invalid"""

    pass


class SessionExpired(AltohumanException):
    """Session has expired"""

    pass


class UserNotFound(AltohumanException):
    """User not found"""

    pass


def create_exception_handler(
    status_code: int, initial_value: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: AltohumanException):
        return JSONResponse(content=initial_value, status_code=status_code)

    return exception_handler


def require_error(app: FastAPI):
    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "message": "Oops something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        return JSONResponse(
            content={
                "message": "Oops something went wrong",
                "error_code": "database_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    app.add_exception_handler(
        CookieMissing,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_value={
                "message": "Authentication Cookie missing",
                "resolution": "Log in to continue",
                "error_code": "cookie_missing",
            },
        ),
    )

    app.add_exception_handler(
        InvalidSession,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_value={
                "message": "Invalid session",
                "resolution": "Please log in again",
                "error_code": "invalid_session",
            },
        ),
    )

    app.add_exception_handler(
        SessionExpired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_value={
                "message": "Session Expired",
                "resolution": "Please log in again",
                "error_code": "session_expired",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_value={
                "message": "User with session not found",
                "resolution": "Please log in again",
                "error_code": "user_not_found",
            },
        ),
    )
