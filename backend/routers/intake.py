import json
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.claude_service import stream_intake
from services.config_service import load_country_config

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class IntakeChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)
    country: str


@router.post("/chat")
async def intake_chat(req: IntakeChatRequest):
    try:
        _, cfg = load_country_config(req.country)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    async def gen():
        try:
            async for event in stream_intake(
                conversation_history=[m.model_dump() for m in req.messages],
                country_config=cfg,
            ):
                yield event
        except Exception as e:
            yield ("\n[STREAM_ERROR]\n" + json.dumps({"error": str(e), "service": "intake_router"})).encode("utf-8")

    return StreamingResponse(gen(), media_type="text/plain")

