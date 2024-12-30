# .\hub-app\services\auth_service.py

import hashlib
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from config import Settings
from dbschemas.auth_schema import User  # 'password_hash' ではなく 'hashed_password' を使用
from passlib.context import CryptContext
import logging
from typing import Optional

settings = Settings()

engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, future=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        try:
            user = db.query(User).filter_by(username=username).first()
            if not user:
                return None
            if not AuthService.verify_password(password, user.hashed_password):  # フィールド名を 'hashed_password' に変更
                return None
            if not user.is_active:
                return None
            return user
        except Exception as e:
            logging.error(f"Error in authenticate_user: {e}")
            return None

    @staticmethod
    def create_session(db: Session, user_id: int, expire_minutes: int = 1440) -> str:
        try:
            sid = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
            db.execute(
                text("INSERT INTO auth_schema.sessions (session_id, user_id, expires_at) "
                     "VALUES (:sid, :uid, :exp)"),
                {"sid": sid, "uid": user_id, "exp": expires_at}
            )
            db.commit()
            return sid
        except Exception as e:
            logging.error(f"Error in create_session: {e}")
            raise e

    @staticmethod
    def validate_session(db: Session, session_id: str) -> Optional[int]:
        try:
            row = db.execute(
                text("SELECT user_id, expires_at FROM auth_schema.sessions WHERE session_id=:sid"),
                {"sid": session_id}
            ).fetchone()
            if not row:
                return None
            user_id, exp = row
            if datetime.utcnow() > exp:
                db.execute(text("DELETE FROM auth_schema.sessions WHERE session_id=:sid"),
                           {"sid": session_id})
                db.commit()
                return None
            return user_id
        except Exception as e:
            logging.error(f"Error in validate_session: {e}")
            return None

    @staticmethod
    def logout_session(db: Session, session_id: str):
        try:
            db.execute(text("DELETE FROM auth_schema.sessions WHERE session_id=:sid"),
                       {"sid": session_id})
            db.commit()
        except Exception as e:
            logging.error(f"Error in logout_session: {e}")
            raise e

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> int:
        try:
            hashed = AuthService.hash_password(password)
            new_user = User(username=username, email=email, hashed_password=hashed)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user.id
        except Exception as e:
            logging.error(f"Error in create_user: {e}")
            db.rollback()
            raise e