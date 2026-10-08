from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_groq import ChatGroq
from core.db import get_session
from dependencies.user import get_current_user
from models.user_model import User
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv

load_dotenv()

humanize_router = APIRouter()

# 🧠 FIXED: Set max_tokens to prevent 429 errors and hide reasoning raw blocks
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    streaming=True,
    reasoning_format="hidden",  # Keeps raw thinking tokens out of user output
    max_tokens=300,  # Keeps you safe under Groq's Free Tier limits
)


async def stream_humanizer(text: str):
    prompt = [
        (
            "system",
            "You are a professional editor. Rewrite the text to be indistinguishable from human writing. Maintain the original meaning but vary sentence structure and vocabulary.",
        ),
        ("human", text),
    ]

    # LangChain yields AIMessageChunk objects
    async for chunk in llm.astream(prompt):
        if chunk.content:
            clean_chunk = chunk.content.replace("*", "")
            yield clean_chunk


@humanize_router.post("/")
async def handle_action(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    data = await request.json()
    text = data.get("text")
    action = data.get("action")

    COSTS = {"score": 10, "humanize": 15}
    required_credits = COSTS.get(action, 1)

    # 2. Check Credit Balance
    if user.credit < required_credits:
        return JSONResponse(
            status_code=402,
            content={"detail": "Insufficient credits", "code": "OUT_OF_CREDITS"},
        )

    if action == "score":
        score_prompt = [
            (
                "system",
                "Analyze the text and return ONLY a number between 0 and 100 representing the likelihood it was written by AI. Do not include '%' or any text.",
            ),
            ("human", text),
        ]

        # We lower max_tokens drastically for scoring since it only needs to return a digit
        response = await llm.ainvoke(score_prompt, max_tokens=10)
        score_value = response.content.strip()

        # Database transaction
        user.credit -= required_credits
        db.add(user)
        await db.commit()
        await db.refresh(
            user
        )  # 🔄 FIXED: Refreshes state to prevent session detachment

        return JSONResponse(
            {
                "success": True,
                "text": text,
                "score": score_value,
                "message": f"AI Detection Score: {score_value}%",
            }
        )

    if action == "humanize":
        await db.refresh(user)
        user.credit -= required_credits
        db.add(user)
        await db.commit()

        # Stream the response safely back to frontend
        return StreamingResponse(
            stream_humanizer(text),
            media_type="text/plain",
            headers={"X-Human-Score": "99"},
        )
