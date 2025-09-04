# app/api/ai.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.nl_entry import route_query

router = APIRouter()

class QueryIn(BaseModel):
    prompt: str

@router.post("/ai/query")
async def ai_query(body: QueryIn):
    return await route_query(body.prompt)