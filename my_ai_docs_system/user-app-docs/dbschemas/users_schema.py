# .\user-app-docs\dbschemas\users_schema.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from shared_libs.database import Base  # 共通のBaseをインポート
from .local_doc_schema import LocalDoc  # LocalDocをインポート

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth_schema"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # リレーションシップの定義
    local_docs = relationship("LocalDoc", back_populates="owner")