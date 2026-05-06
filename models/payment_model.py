from datetime import datetime, timezone
import uuid
from sqlmodel import Column, Field, Relationship, SQLModel
import sqlalchemy.dialects.postgresql as pg
from models.user_model import User


class Payment(SQLModel, table=True):
    __tablename__ = "payment"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    reference: str = Field(unique=True, index=True)
    amount: int
    credits_granted: int
    new_word_limit: int
    status: str = Field(default="pending")
    plan: str

    user_id: str = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="payments")
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __repr__(self):
        return f"<Payment {self.amount}>"
