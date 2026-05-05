from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Column, Field, SQLModel, text
import sqlalchemy.dialects.postgresql as pg


class Verification(SQLModel, table=True):
    __tablename__ = "verification"
    id: str = Field(primary_key=True)
    identifier: str = Field(
        sa_column=Column(pg.TEXT, nullable=False)
    )  # Index matches SQL
    value: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    expiresAt: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )
    createdAt: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        )
    )
    updatedAt: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        )
    )

    def __repr__(self):
        return f"<Verification {self.identifier}>"
