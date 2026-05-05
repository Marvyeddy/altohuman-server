from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Column, Field, Relationship, SQLModel, text
from .user_model import User
import sqlalchemy.dialects.postgresql as pg


class Account(SQLModel, table=True):
    __tablename__ = "account"
    id: str = Field(primary_key=True)
    accountId: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    providerId: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    userId: str = Field(foreign_key="user.id", index=True)  # Index matches your SQL

    accessToken: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    refreshToken: Optional[str] = None
    idToken: Optional[str] = None
    accessTokenExpiresAt: Optional[datetime] = Field(
        default=None, sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    refreshTokenExpiresAt: Optional[datetime] = Field(
        default=None, sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    scope: Optional[str] = None
    password: Optional[str] = None

    createdAt: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        )
    )
    updatedAt: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )

    user: User = Relationship(back_populates="accounts")

    def __repr__(self):
        return (
            f"<Account id={self.id} providerId={self.providerId} "
            f"accountId={self.accountId} userId={self.userId}>"
        )
