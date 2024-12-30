# .\user-app-docs\dbschemas\ai_schema.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from shared_libs.database import Base  # 共通のBaseをインポート

class AICallLogs(Base):
    __tablename__ = "ai_call_logs"
    __table_args__ = {"schema": "ai_schema"}

    call_id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DocEmbedding(Base):
    __tablename__ = "doc_embeddings"
    __table_args__ = {"schema": "ai_schema"}

    embedding_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_ref = Column(String(100), nullable=False)
    embedding_vector = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)