from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PaymentPublic(BaseModel):
    amount: int
    createdAt: datetime

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    credit: int
    currentPlan: str
    # Use a default empty list so it doesn't fail if the user has no payments
    payments: List[PaymentPublic] = []

    class Config:
        from_attributes = True
