from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Relationship, SQLModel, Field, Column, text
import sqlalchemy.dialects.postgresql as pg
from .user_model import User


class Session(SQLModel, table=True):
    __tablename__ = "session"
    id: str = Field(primary_key=True)
    expiresAt: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )
    token: str = Field(sa_column=Column(pg.TEXT, unique=True, nullable=False))
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
    ipAddress: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    userAgent: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))

    userId: str = Field(foreign_key="user.id", index=True)  # Index matches your SQL
    user: User = Relationship(back_populates="sessions")

    def __repr__(self):
        return (
            f"<Session id={self.id} userId={self.userId} "
            f"expiresAt={self.expiresAt} token={self.token}>"
        )
