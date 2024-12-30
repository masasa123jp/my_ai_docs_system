# .\hub-app\routers\authorize.py

from fastapi import APIRouter, Request, HTTPException, Form, Depends, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from services.oauth2_service import OAuth2Service  # 仮定のサービス
from app.database import SessionLocal
import logging
from typing import Optional

router = APIRouter(
    prefix="/authorize",
    tags=["Authorization"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def authorize_get(request: Request, db: Session = Depends(SessionLocal),
                       response_type: str = Query(...),
                       client_id: str = Query(...),
                       redirect_uri: str = Query(...),
                       scope: str = Query(...),
                       state: str = Query(...),
                       nonce: str = Query(...)):
    # クライアントIDやリダイレクトURIの検証
    if not all([client_id, redirect_uri, state, nonce]):
        raise HTTPException(status_code=400, detail="Missing required parameters")

    client = OAuth2Service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    if redirect_uri not in client.redirect_uri.split(","):
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    # セッションにclient_idを保存
    request.session['client_id'] = client_id

    return templates.TemplateResponse("consent.html", {
        "request": request,
        "client_id": client_id,
        "scope": scope,
        "state": state,
        "nonce": nonce,
        "redirect_uri": redirect_uri,
    })

@router.post("/", response_class=HTMLResponse)
async def authorize_post(
    request: Request,
    db: Session = Depends(SessionLocal),
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(...),
    state: str = Form(...),
    nonce: str = Form(...),
    approve: Optional[str] = Form(None)
):
    # クライアントIDやリダイレクトURIの再検証
    if not all([client_id, redirect_uri, state, nonce]):
        raise HTTPException(status_code=400, detail="Missing required parameters")

    client = OAuth2Service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    if redirect_uri not in client.redirect_uri.split(","):
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    if approve:
        # ユーザーが許可した場合
        authorization_code = OAuth2Service.generate_authorization_code(db, client_id, request.user.id)
        params = {
            "code": authorization_code,
            "state": state
        }
        redirect_query = urlencode(params)
        redirect_url = f"{redirect_uri}?{redirect_query}"
        return RedirectResponse(url=redirect_url)
    else:
        # ユーザーが拒否した場合
        params = {
            "error": "access_denied",
            "state": state
        }
        redirect_query = urlencode(params)
        redirect_url = f"{redirect_uri}?{redirect_query}"
        return RedirectResponse(url=redirect_url)

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    redirect_uri: Optional[str] = Form(None),
    db: Session = Depends(SessionLocal)
):
    user = OAuth2Service.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    request.session['user_id'] = user.id
    if redirect_uri:
        return RedirectResponse(url=redirect_uri)
    return RedirectResponse(url="/")