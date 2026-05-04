from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "user"  # Better Auth uses singular 'user'
    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    )
    name: str
    email: str = Field(sa_column=Column(pg.STRING, unique=True, index=True))
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
        return f"<User {self.name}>"
