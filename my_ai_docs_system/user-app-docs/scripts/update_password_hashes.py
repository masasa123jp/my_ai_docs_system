# .\user-app-docs\scripts\update_password_hashes.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from dbschemas.users_schema import User
import os

# 設定の読み込み
from config import DocsSettings

settings = DocsSettings()

engine = create_engine(
    settings.DOCAPP_DB_URL,
    echo=False,
    pool_size=20,
    max_overflow=0,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_hashed_passwords():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            # 既存のパスワードハッシュがbcryptでない場合のみ更新
            if pwd_context.identify(user.hashed_password) != 'bcrypt':
                # ここでは仮にプレーンテキストパスワードを設定
                # 実際にはユーザーに再設定を依頼する必要があります
                plain_password = "new_secure_password"  # ユーザーに依頼
                user.hashed_password = pwd_context.hash(plain_password)
                db.add(user)
                print(f"User {user.username} password hash updated.")
        db.commit()
    except Exception as e:
        print(f"Error updating password hashes: {e}")
        db.rollback()
        raise e  # エラーを再スローしてエンドポイントでハンドリング
    finally:
        db.close()

if __name__ == "__main__":
    update_hashed_passwords()