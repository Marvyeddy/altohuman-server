from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg


class Session(SQLModel, table=True):
    __tablename__ = "session"
    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    )
    userId: uuid.UUID = Field(foreign_key="user.id", index=True)
    token: str = Field(index=True)
    expiresAt: datetime
    createdAt: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)
        )
    )
    updatedAt: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            default=datetime.now(timezone.utc),
            onupdate=datetime.now(timezone.utc),
        )
    )

    def __repr__(self):
        return f"<Session-id {self.userId}>"
