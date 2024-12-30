# .\user-app-docs\dbschemas\local_doc_schema.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from shared_libs.database import Base  # 共通のBaseをインポート
from .doc_links_schema import DocLink  # DocLinkをインポート

class LocalDoc(Base):
    __tablename__ = "local_docs"
    __table_args__ = {"schema": "doc_app"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("auth_schema.users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)

    # リレーションシップの定義
    owner = relationship("User", back_populates="local_docs")

    # tags リレーションシップの追加
    tags = relationship(
        "DocTag",
        secondary="doc_app.doc_tag_links",
        back_populates="documents"
    )

    # outgoing_links と incoming_links のリレーションシップを追加
    outgoing_links = relationship(
        "DocLink",
        foreign_keys=[DocLink.source_doc_id],
        back_populates="source_doc",
        cascade="all, delete-orphan"
    )

    incoming_links = relationship(
        "DocLink",
        foreign_keys=[DocLink.target_doc_id],
        back_populates="target_doc",
        cascade="all, delete-orphan"
    )

    # versions リレーションシップの追加
    versions = relationship(
        "LocalDocVersion",
        back_populates="document",
        cascade="all, delete-orphan"
    )