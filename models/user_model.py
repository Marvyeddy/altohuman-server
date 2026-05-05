from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Column, Field, Relationship, SQLModel, text
import sqlalchemy.dialects.postgresql as pg

if TYPE_CHECKING:
    from .session_model import Session
    from .account_model import Account
    from .payment_model import Payment


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: str = Field(primary_key=True)
    name: str
    email: str = Field(sa_column=Column(pg.TEXT, unique=True, nullable=False))
    emailVerified: bool = Field(default=False, nullable=False)
    image: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))

    # Custom fields for your credits plan
    credit: int = Field(default=50)
    wordLimit: int = Field(default=300)

    # Timestamps matching "timestamptz default CURRENT_TIMESTAMP"
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

    # Relationships (Using strings to avoid circular import errors)
    sessions: List["Session"] = Relationship(back_populates="user")
    accounts: List["Account"] = Relationship(back_populates="user")
    payments: List["Payment"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} name={self.name} email={self.email}>"
