# .\user-app-docs\routers\admin_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from auth import get_current_user  # ユーザー認証の依存関係
from database import get_db
from scripts.update_password_hashes import update_hashed_passwords  # パスワード更新スクリプトのインポート

router = APIRouter(
    prefix="/admin",
    tags=["管理者"]
)

# 管理者ユーザーの認証を確認する関数（例として、usernameが'admin'のユーザーのみ許可）
def get_admin_user(current_user: Dict = Depends(get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限がありません。",
        )
    return current_user

@router.post("/update_password_hashes", summary="パスワードハッシュの更新")
def update_password_hashes_endpoint(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_admin_user)
):
    """
    管理者が全ユーザーのパスワードハッシュを更新するエンドポイント。
    """
    try:
        update_hashed_passwords()
        return {"message": "パスワードハッシュが正常に更新されました。"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"パスワードハッシュの更新中にエラーが発生しました: {str(e)}"
        )