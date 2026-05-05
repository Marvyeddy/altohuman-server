import hashlib
import hmac
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from models.payment_model import Payment
from models.user_model import User
from dependencies.user import get_current_user
from core.config import Config as cfg
import uuid
import httpx

payment_router = APIRouter()

PLANS = {
    "starter": {"amount": 10000, "credits": 200, "wordLimit": 600},
    "pro": {"amount": 50000, "credits": 500, "wordLimit": 1200},
    "advanced": {"amount": 100000, "credits": 1000, "wordLimit": 3000},
}


@payment_router.post("/initialize")
async def initialize_payment(
    plan_name: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    plan = PLANS.get(plan_name.lower())
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")

    headers = {"Authorization": f"Bearer {cfg.PAYSTACK_SECRET_KEY}"}

    tx_ref = str(uuid.uuid4())

    payload = {
        "email": current_user.email,
        "amount": plan["amount"],
        "reference": tx_ref,
        "callback_url": "http://localhost:3000/dashboard?status=success",
        "metadata": {"user_id": current_user.id, "plan_name": plan_name.lower()},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://paystack.co", json=payload, headers=headers
        )
        res_data = response.json()

        if res_data.get("status"):
            # Create a pending payment record in your table
            new_payment = Payment(
                reference=tx_ref,
                amount=plan["amount"],
                credits_granted=plan["credits"],
                new_word_limit=plan["wordLimit"],
                user_id=current_user.id,
                status="pending",
            )

            db.add(new_payment)
            db.commit()

            return {"checkout_url": res_data["data"]["authorization_url"]}

        raise HTTPException(status_code=400, detail="Paystack error")


@payment_router.post("/webhook")
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_session),
    x_paystack_signature: str = Header(None),
):
    # Verify Paystack Signature
    body = await request.body()
    computed_hash = hmac.new(
        cfg.PAYSTACK_SECRET_KEY.encode("utf-8"), body, hashlib.sha512
    ).hexdigest()

    if computed_hash != x_paystack_signature:
        raise HTTPException(status_code=401, detail="Invalid Signature")

    data = await request.json()

    if data.get("event") == "charge.success":
        reference = data["data"]["reference"]

        # 1. Find the payment record
        statement = select(Payment).where(Payment.reference == reference)
        payment_rec = db.exec(statement).first()

        if payment_rec and payment_rec.status == "pending":
            # 2. Update Payment Status
            payment_rec.status = "success"

            # 3. Update User Credits and Word Limit
            user_statement = select(User).where(User.id == payment_rec.user_id)
            user = db.exec(user_statement).first()

            if user:
                user.credit += payment_rec.credits_granted
                user.wordLimit = payment_rec.new_word_limit

                db.add(user)
                db.add(payment_rec)
                db.commit()
                print(f"Success: {user.email} upgraded to {user.wordLimit} limit.")

    return {"status": "received"}
