# .\hub-app\routers\doc_router.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.doc_service import DocService
from sqlalchemy.orm import Session
from app.database import SessionLocal
import logging

router = APIRouter(
    prefix="/doc",
    tags=["Documents"]
)

class DocCreate(BaseModel):
    title: str
    content: str

@router.post("/create", response_model=dict)
def create_document(doc: DocCreate, db: Session = Depends(SessionLocal)):
    try:
        doc_id = DocService.create_document(db, doc.title, doc.content)
        return {"doc_id": doc_id}
    except Exception as e:
        logging.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Document creation failed.")

@router.get("/list", response_model=list)
def list_documents(db: Session = Depends(SessionLocal)):
    try:
        documents = DocService.list_documents(db)
        return documents
    except Exception as e:
        logging.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents.")