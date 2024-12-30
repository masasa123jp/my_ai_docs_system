# .\user-app-docs\dbschemas\local_doc_versions_schema.py

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from shared_libs.database import Base  # 共通のBaseをインポート

class LocalDocVersion(Base):
    __tablename__ = "local_doc_versions"
    __table_args__ = {"schema": "doc_app"}

    version_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey('doc_app.local_docs.id'), nullable=False)
    version_num = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with LocalDoc
    document = relationship("LocalDoc", back_populates="versions")