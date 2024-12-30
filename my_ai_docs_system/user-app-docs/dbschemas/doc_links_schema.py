# .\user-app-docs\dbschemas\doc_links_schema.py

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from shared_libs.database import Base  # 共通のBaseをインポート


class DocLink(Base):
    __tablename__ = "doc_links"
    __table_args__ = {"schema": "doc_app"}

    link_id = Column(Integer, primary_key=True, autoincrement=True)
    source_doc_id = Column(Integer, ForeignKey('doc_app.local_docs.id'), nullable=False)
    target_doc_id = Column(Integer, ForeignKey('doc_app.local_docs.id'), nullable=False)

    # Relationships
    source_doc = relationship("LocalDoc", foreign_keys=[source_doc_id], back_populates="outgoing_links")
    target_doc = relationship("LocalDoc", foreign_keys=[target_doc_id], back_populates="incoming_links")
