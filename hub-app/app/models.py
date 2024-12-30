# .\hub-app\app\models.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from shared_libs.database import Base  # 共通のBaseをインポート

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth_schema'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # 必要に応じてリレーションシップを追加
    # 例:
    # documents = relationship("Document", back_populates="user")

class Client(Base):
    __tablename__ = 'clients'
    __table_args__ = {'schema': 'auth_schema'}

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True, nullable=False)
    client_secret = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # 必要に応じてリレーションシップを追加