# .\user-app-docs\routers\login.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from auth import get_current_user
from database import get_db
from dbschemas.users_schema import User
from jose import jwt, JWTError
from config import DocsSettings
from passlib.context import CryptContext
import logging

router = APIRouter(prefix="/login", tags=["認証"])

settings = DocsSettings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ログの設定
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

@router.post("/signup", response_model=dict)
def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    """
    ユーザー登録エンドポイント。
    """
    # ユーザーの存在確認
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ユーザー名またはメールアドレスは既に登録されています。")

    # 新規ユーザーの作成
    new_user = User(username=username, email=email, hashed_password=pwd_context.hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "ユーザーが正常に作成されました。"}

@router.post("/login", response_model=dict)
def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    ユーザーログインエンドポイント。JWTトークンを生成して返します。
    """
    logger.info(f"Type of db: {type(db)}")  # 追加
    logger.info(f"Login attempt for username: {username}")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        logger.warning(f"User not found: {username}")
        raise HTTPException(status_code=400, detail="ユーザー名またはパスワードが無効です。")
    #logger.info(f"password: {password}")
    #logger.info(f"user.hashed_password: {user.hashed_password}")
    #logger.info(f"test hashed_password: {pwd_context.hash(password)}")
    if not pwd_context.verify(password, user.hashed_password):
        logger.warning(f"Invalid password for user: {username}")
        raise HTTPException(status_code=400, detail="ユーザー名またはパスワードが無効です。")

    # JWTトークンの生成
    access_token = jwt.encode(
        {"sub": user.username},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    logger.info(f"User {username} logged in successfully.")

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", response_model=dict)
def logout():
    """
    ユーザーログアウトエンドポイント。クッキーのトークンを削除します。
    """
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token")
    return {"message": "正常にログアウトしました。"}
