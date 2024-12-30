# .\hub-app\routers\ai_router.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.ai_service import AIService
from sqlalchemy.orm import Session
from app.database import SessionLocal
import logging

router = APIRouter(prefix="/ai", tags=["AI"])

class GenerateReq(BaseModel):
    prompt: str

@router.post("/generate", response_model=dict)
def generate_text(req: GenerateReq, db: Session = Depends(SessionLocal)):
    """
    テキストを生成するエンドポイント
    """
    try:
        generated_text = AIService.generate_text(req.prompt, db)
        return {"generated_text": generated_text}
    except Exception as e:
        logging.error(f"Error in generate_text: {e}")
        raise HTTPException(status_code=500, detail="Text generation failed.")

@router.get("/rag_search", response_model=dict)
def rag_search(query: str, db: Session = Depends(SessionLocal)):
    """
    RAG検索を行い、回答を返すエンドポイント
    """
    try:
        answer = AIService.rag_search_and_answer(query, db)
        return {"answer": answer}
    except Exception as e:
        logging.error(f"Error in rag_search: {e}")
        raise HTTPException(status_code=500, detail="RAG search failed.")