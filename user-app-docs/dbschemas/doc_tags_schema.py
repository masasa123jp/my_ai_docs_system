# .\user-app-docs\dbschemas\doc_tags_schema.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from shared_libs.database import Base  # 共通のBaseをインポート


class DocTag(Base):
    __tablename__ = "doc_tags"
    __table_args__ = {"schema": "doc_app"}

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Relationship with LocalDoc through DocTagLink
    documents = relationship(
        "LocalDoc",
        secondary="doc_app.doc_tag_links",
        back_populates="tags"
    )


class DocTagLink(Base):
    __tablename__ = "doc_tag_links"
    __table_args__ = {"schema": "doc_app"}

    doc_id = Column(Integer, ForeignKey('doc_app.local_docs.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('doc_app.doc_tags.tag_id'), primary_key=True)