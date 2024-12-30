# .\hub-app\dbschemas\docs_schema.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.schema import SchemaItem
from datetime import datetime

BaseDocs = declarative_base()

class Document(BaseDocs):
    __tablename__ = "documents"
    __table_args__ = {"schema": "hub_docs"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # owner_id = Column(Integer, ForeignKey("auth_schema.users.id"))  # 必要に応じて外部キーを追加
    # owner = relationship("User", back_populates="documents")