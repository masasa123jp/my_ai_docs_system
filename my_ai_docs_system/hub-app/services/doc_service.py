# .\hub-app\services\doc_service.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dbschemas.docs_schema import BaseDocs, Document
from config import Settings
import logging

settings = Settings()

engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, future=True)

class DocService:
    @staticmethod
    def create_document(db: Session, title: str, content: str) -> int:
        try:
            doc = Document(title=title, content=content, created_at=datetime.utcnow())
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc.id
        except Exception as e:
            logging.error(f"Error in create_document: {e}")
            db.rollback()
            raise e

    @staticmethod
    def list_documents(db: Session) -> list:
        try:
            docs = db.query(Document).all()
            return [{"id": d.id, "title": d.title, "created_at": d.created_at} for d in docs]
        except Exception as e:
            logging.error(f"Error in list_documents: {e}")
            raise e