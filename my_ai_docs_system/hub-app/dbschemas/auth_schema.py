# .\hub-app\dbschemas\auth_schema.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth_schema"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)  # フィールド名を 'hashed_password' に変更
    email = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {"schema": "auth_schema"}

    session_id = Column(String(36), primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"
    __table_args__ = {"schema": "auth_schema"}

    code = Column(String(64), primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    client_id = Column(String(100), nullable=False)
    scope = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    __table_args__ = {"schema": "auth_schema"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(500), unique=True, nullable=False)
    revoked_at = Column(DateTime, nullable=False)

class Client(Base):
    __tablename__ = 'clients'
    __table_args__ = {'schema': 'auth_schema'}

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True, nullable=False)
    client_secret = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)