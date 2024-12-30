# .\user-app-docs\dbschemas\docs_schema.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from shared_libs.database import Base  # 共通のBaseをインポート

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "hub_docs"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 必要に応じてリレーションシップを追加