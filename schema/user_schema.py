from pydantic import BaseModel
from typing import List
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
    wordLimit: int
    currentPlan: str
    payments: List[PaymentPublic] = []

    class Config:
        from_attributes = True
