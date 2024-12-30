# .\hub-app\routers\login.py

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import logging

router = APIRouter(
    prefix="/user-docs",
    tags=["User Docs"]
)

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # ユーザー認証の処理 (AuthService を利用)
    # ここでは仮の認証ロジックを示します。実際の実装では AuthService を使用してください。
    if username == "user" and password == "pass":
        params = {
            "response_type": "code",
            "client_id": "your-client-id-from-hub-app",
            "redirect_uri": "http://localhost:8100/auth",
            "scope": "openid profile email",
            "state": "secure-random-state",
            "nonce": "secure-random-nonce"
        }
        query_string = urlencode(params)
        authorize_url = f"http://localhost:8000/authorize?{query_string}"
        return RedirectResponse(url=authorize_url)
    else:
        logging.warning(f"Failed login attempt for user: {username}")
        return RedirectResponse(url="/user-docs/login-failed", status_code=302)