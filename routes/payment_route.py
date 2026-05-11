import hashlib
import hmac
import uuid
import httpx
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from models.payment_model import Payment
from models.user_model import User
from dependencies.user import get_current_user
from core.config import Config as cfg

payment_router = APIRouter()

PLANS = {
    "starter": {"amount": 20000, "credits": 200, "wordLimit": 600},
    "pro": {"amount": 50000, "credits": 500, "wordLimit": 1200},
    "advanced": {"amount": 100000, "credits": 1000, "wordLimit": 3000},
}


@payment_router.post("/initialize/{plan_name}")
async def initialize_payment(
    plan_name: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    plan = PLANS.get(plan_name.lower())
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")

    paystack_url = "https://api.paystack.co/transaction/initialize"
    reference = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {cfg.PAYSTACK_SECRET_TEST_KEY.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "email": current_user.email,
        "amount": int(plan["amount"]),  # Must be integer
        "reference": reference,
        "callback_url": "https://altohuman.vercel.app/dashboard?status=success",
        "metadata": {"plan_name": plan_name.lower(), "user_id": current_user.id},
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                paystack_url, json=payload, headers=headers, timeout=20.0
            )

        content_type = res.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            print(
                f"Non-JSON response from Paystack ({res.status_code}): "
                f"{res.text[:500]}"
            )
            raise HTTPException(
                status_code=502,
                detail="Payment gateway returned a non-JSON response",
            )

        data = res.json()
    except httpx.RequestError as e:
        print(f"Paystack connection error: {e}")
        raise HTTPException(
            status_code=502, detail="Could not connect to payment gateway"
        )
    except ValueError as e:
        print(f"Paystack JSON parse error: {e}")
        raise HTTPException(
            status_code=502, detail="Payment gateway returned invalid JSON"
        )

    if not data.get("status"):
        raise HTTPException(
            status_code=400,
            detail=data.get("message", "Payment initialization failed"),
        )

    payment = Payment(
        reference=reference,
        amount=int(plan["amount"]),
        credits_granted=int(plan["credits"]),
        new_word_limit=int(plan["wordLimit"]),
        plan=plan_name.lower(),
        user_id=current_user.id,
    )
    db.add(payment)
    await db.commit()

    return {
        "checkout_url": data["data"]["authorization_url"],
        "reference": reference,
    }


@payment_router.post("/webhook")
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_session),
    x_paystack_signature: str = Header(None),
):
    body = await request.body()

    # Verify Signature
    computed_hash = hmac.new(
        cfg.PAYSTACK_SECRET_TEST_KEY.encode("utf-8"), body, hashlib.sha512
    ).hexdigest()

    if computed_hash != x_paystack_signature:
        raise HTTPException(status_code=401, detail="Invalid Signature")

    data = await request.json()

    if data.get("event") == "charge.success":
        reference = data["data"]["reference"]

        statement = select(Payment).where(Payment.reference == reference)
        result = await db.exec(statement)
        payment_rec = result.first()

        if payment_rec and payment_rec.status == "pending":
            payment_rec.status = "success"

            user_statement = select(User).where(User.id == payment_rec.user_id)
            user_result = await db.exec(user_statement)
            user = user_result.first()

            if user:
                user.credit += payment_rec.credits_granted
                user.wordLimit = payment_rec.new_word_limit
                user.currentPlan = payment_rec.plan

                db.add(user)
                db.add(payment_rec)
                await db.commit()
                print(f"Success: {user.email} upgraded.")

    return {"status": "received"}
