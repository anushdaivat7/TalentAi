"""Phase 8 - AI recruiter chatbot endpoint."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ..services import chatbot

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
def chat(req: ChatRequest):
    return chatbot.answer(req.message)


@router.get("/suggestions")
def suggestions():
    return {"suggestions": [
        "Why is the top candidate ranked first?",
        "Show top 10 candidates",
        "Which candidates are strongest for this role?",
        "Which skills are most missing?",
        "Recommend an interview shortlist",
    ]}
