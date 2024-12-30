# .\user-app-docs\routers\auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import get_current_user
from database import get_db
from dbschemas.users_schema import User
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["ユーザー認証"])

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True

@router.get("/profile", response_model=UserProfile)
def read_user_profile(current_user: User = Depends(get_current_user)):
    """
    ユーザーのプロフィール情報を取得するエンドポイント。
    """
    return current_user

@router.put("/profile", response_model=UserProfile)
def update_user_profile(
    email: str = None,
    password: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ユーザーのプロフィール情報を更新するエンドポイント。
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if email:
        current_user.email = email
    if password:
        current_user.hashed_password = pwd_context.hash(password)  # 'hashed_password' に修正

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user